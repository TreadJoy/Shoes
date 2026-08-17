from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from threading import Barrier

from django.db import close_old_connections, connections
from django.test import TestCase, TransactionTestCase

from web.orders.models import InventoryAllocation, Order, OrderItem, Payment
from web.orders.services import (
    allocate_inventory_for_paid_order,
    synchronize_refund,
)
from web.products.models import (
    PreorderBatch,
    PreorderVariantAllocation,
    Product,
    ProductVariant,
)


class PreorderAllocationDataMixin:
    def create_preorder_setup(self, *, total_capacity=5, sku_capacity=5):
        product = Product.objects.create(
            name=f"Preorder Allocation Shoe {Product.objects.count()}",
            slug=f"preorder-allocation-shoe-{Product.objects.count()}",
            price=Decimal("100.00"),
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku=f"TJ-PREALLOC-{Product.objects.count():03d}",
            size="9",
            color="Black",
            stock_quantity=20,
        )
        batch = PreorderBatch.objects.create(
            code=f"PREALLOC-{PreorderBatch.objects.count()}",
            product=product,
            estimated_tender_start=date(2026, 10, 12),
            estimated_tender_end=date(2026, 10, 23),
            total_capacity=total_capacity,
        )
        sku_allocation = PreorderVariantAllocation.objects.create(
            batch=batch,
            variant=variant,
            capacity=sku_capacity,
        )
        if total_capacity > sku_capacity:
            supporting_variant = ProductVariant.objects.create(
                product=product,
                sku=f"TJ-PREALLOC-SUPPORT-{Product.objects.count():03d}",
                size="10",
                color="Black",
            )
            PreorderVariantAllocation.objects.create(
                batch=batch,
                variant=supporting_variant,
                capacity=total_capacity - sku_capacity,
            )
        batch.status = PreorderBatch.Status.OPEN
        batch.save()
        return product, variant, batch, sku_allocation

    def create_preorder_order(self, product, variant, batch, quantity):
        order = Order.objects.create(
            full_name="Preorder Allocation Customer",
            email="customer@example.com",
            status=Order.Status.PAID,
            fulfillment_type=Order.FulfillmentType.PREORDER,
            preorder_batch=batch,
            estimated_tender_start=batch.estimated_tender_start,
            estimated_tender_end=batch.estimated_tender_end,
            grand_total=product.price * quantity,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            variant=variant,
            fulfillment_type=Order.FulfillmentType.PREORDER,
            preorder_batch=batch,
            preorder_batch_code=batch.code,
            estimated_tender_start=batch.estimated_tender_start,
            estimated_tender_end=batch.estimated_tender_end,
            product_name=product.name,
            sku=variant.sku,
            unit_price=product.price,
            quantity=quantity,
            size=variant.size,
            color=variant.color,
            line_total=product.price * quantity,
        )
        return order


class PreorderPaidAllocationTests(PreorderAllocationDataMixin, TestCase):
    def test_confirmed_payment_commits_batch_and_sku_capacity_once(self):
        product, variant, batch, sku_allocation = self.create_preorder_setup()
        order = self.create_preorder_order(product, variant, batch, quantity=2)

        first = allocate_inventory_for_paid_order(order)
        second = allocate_inventory_for_paid_order(order)

        batch.refresh_from_db()
        sku_allocation.refresh_from_db()
        variant.refresh_from_db()
        audit = first.items.get()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.status, InventoryAllocation.Status.ALLOCATED)
        self.assertEqual(batch.committed_quantity, 2)
        self.assertEqual(sku_allocation.committed_quantity, 2)
        self.assertEqual(variant.stock_quantity, 20)
        self.assertEqual(audit.fulfillment_type, Order.FulfillmentType.PREORDER)
        self.assertEqual(audit.batch_available_before, 5)
        self.assertEqual(audit.batch_available_after, 3)
        self.assertEqual(audit.variant_available_before, 5)
        self.assertEqual(audit.variant_available_after, 3)

    def test_sku_shortfall_commits_nothing_and_opens_review(self):
        product, variant, batch, sku_allocation = self.create_preorder_setup(
            total_capacity=5,
            sku_capacity=1,
        )
        order = self.create_preorder_order(product, variant, batch, quantity=2)

        allocation = allocate_inventory_for_paid_order(order)

        batch.refresh_from_db()
        sku_allocation.refresh_from_db()
        audit = allocation.items.get()
        self.assertEqual(
            allocation.status,
            InventoryAllocation.Status.REVIEW_REQUIRED,
        )
        self.assertEqual(batch.committed_quantity, 0)
        self.assertEqual(sku_allocation.committed_quantity, 0)
        self.assertEqual(audit.allocated_quantity, 0)
        self.assertEqual(audit.variant_available_before, 1)
        self.assertEqual(audit.variant_available_after, 1)
        self.assertEqual(audit.batch_available_before, 5)
        self.assertEqual(audit.batch_available_after, 5)

    def test_generic_refund_does_not_release_preorder_capacity(self):
        product, variant, batch, sku_allocation = self.create_preorder_setup()
        order = self.create_preorder_order(product, variant, batch, quantity=1)
        allocate_inventory_for_paid_order(order)
        Payment.objects.create(
            order=order,
            stripe_payment_intent_id="pi_generic_preorder_refund",
            amount=Decimal("100.00"),
            currency="usd",
            status=Payment.Status.SUCCEEDED,
        )

        synchronize_refund({
            "id": "re_generic_preorder",
            "payment_intent": "pi_generic_preorder_refund",
            "amount": 10000,
            "currency": "usd",
            "status": "succeeded",
            "created": 1786900000,
        })

        batch.refresh_from_db()
        sku_allocation.refresh_from_db()
        self.assertEqual(batch.committed_quantity, 1)
        self.assertEqual(sku_allocation.committed_quantity, 1)


class ConcurrentPreorderAllocationTests(
    PreorderAllocationDataMixin,
    TransactionTestCase,
):
    def allocate(self, order_id, barrier):
        close_old_connections()
        try:
            order = Order.objects.get(pk=order_id)
            barrier.wait(timeout=5)
            return allocate_inventory_for_paid_order(order).status
        finally:
            connections.close_all()

    def test_competing_payments_cannot_exceed_preorder_capacity(self):
        product, variant, batch, sku_allocation = self.create_preorder_setup(
            total_capacity=1,
            sku_capacity=1,
        )
        orders = [
            self.create_preorder_order(product, variant, batch, quantity=1)
            for _ in range(2)
        ]
        barrier = Barrier(2)

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    lambda order: self.allocate(order.pk, barrier),
                    orders,
                )
            )

        batch.refresh_from_db()
        sku_allocation.refresh_from_db()
        self.assertCountEqual(
            results,
            [
                InventoryAllocation.Status.ALLOCATED,
                InventoryAllocation.Status.REVIEW_REQUIRED,
            ],
        )
        self.assertEqual(batch.committed_quantity, 1)
        self.assertEqual(sku_allocation.committed_quantity, 1)
