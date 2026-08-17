from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from web.orders.admin import OrderAdminForm
from web.orders.models import (
    InventoryAllocation,
    InventoryAllocationItem,
    Order,
    Payment,
    Shipment,
)
from web.products.models import Product, ProductVariant


class InventoryReviewAdminTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_superuser(
            username="inventory-reviewer",
            email="staff@example.com",
            password="test-password",
        )
        self.client.force_login(self.staff)
        self.order = Order.objects.create(
            full_name="Inventory Review Customer",
            email="review-customer@example.com",
            status=Order.Status.PAID,
            grand_total=Decimal("100.00"),
        )
        self.allocation = InventoryAllocation.objects.create(
            order=self.order,
            status=InventoryAllocation.Status.REVIEW_REQUIRED,
            review_due_at=timezone.now() - timedelta(hours=1),
        )
        Payment.objects.create(
            order=self.order,
            stripe_payment_intent_id="pi_admin_review",
            stripe_checkout_session_id="cs_admin_review",
            amount=Decimal("100.00"),
            currency="usd",
            status=Payment.Status.SUCCEEDED,
        )
        product = Product.objects.create(
            name="Admin Review Shoe",
            slug="admin-review-shoe",
            price=Decimal("100.00"),
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku="TJ-ADMIN-SHORTAGE",
            size="9",
            color="Black",
            stock_quantity=0,
        )
        InventoryAllocationItem.objects.create(
            allocation=self.allocation,
            variant=variant,
            sku=variant.sku,
            required_quantity=1,
            allocated_quantity=0,
            variant_available_before=0,
            variant_available_after=0,
        )

    def test_review_queue_shows_shortage_and_overdue_filter(self):
        changelist_url = reverse(
            "admin:orders_inventoryallocation_changelist"
        )
        response = self.client.get(
            changelist_url,
            {"review_overdue": "yes"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inventory Review Customer")
        self.assertContains(response, "Review Required")
        self.assertContains(response, "TJ-ADMIN-SHORTAGE")
        self.assertContains(response, "pi_admin_review")
        self.assertContains(response, "cs_admin_review")

        change_response = self.client.get(
            reverse(
                "admin:orders_inventoryallocation_change",
                args=[self.allocation.pk],
            )
        )
        self.assertEqual(change_response.status_code, 200)
        self.assertContains(change_response, "TJ-ADMIN-SHORTAGE")

    def test_notification_action_records_staff_user_and_timestamp(self):
        response = self.client.post(
            reverse("admin:orders_inventoryallocation_changelist"),
            {
                "action": "mark_customer_notified",
                "_selected_action": [str(self.allocation.pk)],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.allocation.refresh_from_db()
        self.assertEqual(self.allocation.customer_notified_by, self.staff)
        self.assertIsNotNone(self.allocation.customer_notified_at)

    def test_refunded_allocation_remains_actionable_until_notification(self):
        self.allocation.status = InventoryAllocation.Status.REFUNDED
        self.allocation.refund_initiated_at = timezone.now()
        self.allocation.resolved_at = timezone.now()
        self.allocation.save(
            update_fields=["status", "refund_initiated_at", "resolved_at"]
        )

        queue_response = self.client.get(
            reverse("admin:orders_inventoryallocation_changelist"),
            {"review_overdue": "yes"},
        )
        self.assertContains(queue_response, "Inventory Review Customer")

        self.client.post(
            reverse("admin:orders_inventoryallocation_changelist"),
            {
                "action": "mark_customer_notified",
                "_selected_action": [str(self.allocation.pk)],
            },
        )

        self.allocation.refresh_from_db()
        self.assertEqual(self.allocation.customer_notified_by, self.staff)
        self.assertIsNotNone(self.allocation.customer_notified_at)
        self.assertFalse(self.allocation.is_overdue)

    def test_order_admin_form_blocks_processing_during_review(self):
        form = OrderAdminForm(
            instance=self.order,
            data={
                "full_name": self.order.full_name,
                "email": self.order.email,
                "status": Order.Status.PROCESSING,
                "subtotal": "0.00",
                "shipping_total": "0.00",
                "tax_total": "0.00",
                "discount_total": "0.00",
                "grand_total": "100.00",
                "stripe_checkout_session_id": "",
                "stripe_payment_intent_id": "",
                "stripe_tax_calculation_id": "",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("Resolve the inventory review", form.errors["status"][0])

    def test_order_admin_action_blocks_shipping_during_review(self):
        response = self.client.post(
            reverse("admin:orders_order_changelist"),
            {
                "action": "mark_as_shipped",
                "_selected_action": [str(self.order.pk)],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PAID)
        self.assertContains(response, "inventory review is still open")

    def test_shipment_timestamps_are_blocked_during_review(self):
        with self.assertRaises(ValidationError):
            Shipment.objects.create(
                order=self.order,
                shipped_at=timezone.now(),
            )

        self.assertFalse(Shipment.objects.filter(order=self.order).exists())
