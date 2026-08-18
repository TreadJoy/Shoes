from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection, connections
from django.test import TestCase, TransactionTestCase

from web.orders.models import (
    InventoryAllocation,
    Order,
    OrderItem,
)
from web.orders.services import allocate_inventory_for_paid_order
from web.products.models import Product, ProductVariant


class InventoryTestDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            name="TreadJoy Inventory Test Shoe",
            slug="treadjoy-inventory-test-shoe",
            price=Decimal("100.00"),
        )

    def create_variant(self, *, sku, size, color, stock_quantity):
        return ProductVariant.objects.create(
            product=self.product,
            sku=sku,
            size=size,
            color=color,
            stock_quantity=stock_quantity,
        )

    def create_order(self):
        return Order.objects.create(
            full_name="Inventory Test Customer",
            email="customer@example.com",
            status=Order.Status.PAID,
        )

    def add_order_item(self, *, order, variant, quantity):
        return OrderItem.objects.create(
            order=order,
            product=self.product,
            variant=variant,
            product_name=self.product.name,
            sku=variant.sku,
            unit_price=self.product.price,
            quantity=quantity,
            size=variant.size,
            color=variant.color,
            line_total=self.product.price * quantity,
        )


class InventoryAllocationTests(InventoryTestDataMixin, TestCase):
    def test_insufficient_variant_rolls_back_all_stock_changes(self):
        available_variant = self.create_variant(
            sku="TJ-INVENTORY-090-BLK",
            size="9",
            color="Black",
            stock_quantity=3,
        )
        unavailable_variant = self.create_variant(
            sku="TJ-INVENTORY-100-BLK",
            size="10",
            color="Black",
            stock_quantity=0,
        )
        order = self.create_order()
        self.add_order_item(
            order=order,
            variant=available_variant,
            quantity=2,
        )
        self.add_order_item(
            order=order,
            variant=unavailable_variant,
            quantity=1,
        )

        allocation = allocate_inventory_for_paid_order(order)

        available_variant.refresh_from_db()
        unavailable_variant.refresh_from_db()
        self.assertEqual(available_variant.stock_quantity, 3)
        self.assertEqual(unavailable_variant.stock_quantity, 0)
        self.assertEqual(
            allocation.status,
            InventoryAllocation.Status.REVIEW_REQUIRED,
        )
        self.assertIsNotNone(allocation.review_due_at)
        audit_items = {
            item.variant_id: item
            for item in allocation.items.all()
        }
        self.assertEqual(
            audit_items[available_variant.id].variant_available_before,
            3,
        )
        self.assertEqual(
            audit_items[available_variant.id].variant_available_after,
            3,
        )
        self.assertEqual(audit_items[available_variant.id].allocated_quantity, 0)
        self.assertEqual(
            audit_items[unavailable_variant.id].variant_available_before,
            0,
        )
        self.assertEqual(
            audit_items[unavailable_variant.id].variant_available_after,
            0,
        )
        self.assertEqual(audit_items[unavailable_variant.id].allocated_quantity, 0)

    def test_multiple_order_lines_for_one_variant_are_combined(self):
        variant = self.create_variant(
            sku="TJ-INVENTORY-090-WHT",
            size="9",
            color="White",
            stock_quantity=5,
        )
        order = self.create_order()
        self.add_order_item(order=order, variant=variant, quantity=2)
        self.add_order_item(order=order, variant=variant, quantity=1)

        allocation = allocate_inventory_for_paid_order(order)

        variant.refresh_from_db()
        self.assertEqual(variant.stock_quantity, 2)
        self.assertEqual(
            allocation.status,
            InventoryAllocation.Status.ALLOCATED,
        )
        audit_item = allocation.items.get()
        self.assertEqual(audit_item.required_quantity, 3)
        self.assertEqual(audit_item.allocated_quantity, 3)
        self.assertEqual(audit_item.variant_available_before, 5)
        self.assertEqual(audit_item.variant_available_after, 2)

    def test_repeated_allocation_is_idempotent(self):
        variant = self.create_variant(
            sku="TJ-INVENTORY-100-WHT",
            size="10",
            color="White",
            stock_quantity=4,
        )
        order = self.create_order()
        self.add_order_item(order=order, variant=variant, quantity=1)

        first = allocate_inventory_for_paid_order(order)
        second = allocate_inventory_for_paid_order(order)

        variant.refresh_from_db()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(variant.stock_quantity, 3)
        self.assertEqual(InventoryAllocation.objects.filter(order=order).count(), 1)


@skipUnless(
    connection.vendor == "postgresql",
    "Requires PostgreSQL row-level locking.",
)
class ConcurrentInventoryAllocationTests(
    InventoryTestDataMixin,
    TransactionTestCase,
):
    def setUp(self):
        self.product = Product.objects.create(
            name="TreadJoy Concurrent Inventory Shoe",
            slug="treadjoy-concurrent-inventory-shoe",
            price=Decimal("100.00"),
        )

    def allocate_order(self, order_id, start_barrier):
        close_old_connections()

        try:
            order = Order.objects.get(pk=order_id)
            start_barrier.wait(timeout=5)
            allocation = allocate_inventory_for_paid_order(order)
            return allocation.status
        finally:
            connections.close_all()

    def test_competing_orders_cannot_consume_the_same_unit(self):
        variant = self.create_variant(
            sku="TJ-CONCURRENT-090-BLK",
            size="9",
            color="Black",
            stock_quantity=1,
        )
        first_order = self.create_order()
        second_order = self.create_order()
        self.add_order_item(
            order=first_order,
            variant=variant,
            quantity=1,
        )
        self.add_order_item(
            order=second_order,
            variant=variant,
            quantity=1,
        )
        start_barrier = Barrier(2)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    self.allocate_order,
                    order.id,
                    start_barrier,
                )
                for order in [first_order, second_order]
            ]
            results = [future.result(timeout=10) for future in futures]

        variant.refresh_from_db()
        self.assertCountEqual(
            results,
            [
                InventoryAllocation.Status.ALLOCATED,
                InventoryAllocation.Status.REVIEW_REQUIRED,
            ],
        )
        self.assertEqual(variant.stock_quantity, 0)
