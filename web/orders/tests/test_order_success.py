from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from web.orders.models import InventoryAllocation, Order, Payment


class OrderSuccessStatusTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            full_name="Success Page Customer",
            email="customer@example.com",
            status=Order.Status.PAID,
            subtotal=Decimal("100.00"),
            grand_total=Decimal("100.00"),
        )
        Payment.objects.create(
            order=self.order,
            stripe_payment_intent_id="pi_success_page",
            amount=Decimal("100.00"),
            currency="usd",
            status=Payment.Status.SUCCEEDED,
        )
        self.allocation = InventoryAllocation.objects.create(
            order=self.order,
            status=InventoryAllocation.Status.REVIEW_REQUIRED,
        )
        session = self.client.session
        session["checkout_order_ids"] = [self.order.pk]
        session.save()

    def test_inventory_review_keeps_generic_paid_confirmation(self):
        response = self.client.get(
            reverse("orders:order_success", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thank you for your order!")
        self.assertNotContains(response, "inventory review")
        self.assertNotContains(response, "payment processing")

    def test_refunded_order_shows_accurate_confirmation(self):
        self.order.status = Order.Status.REFUNDED
        self.order.save(update_fields=["status", "updated_at"])
        self.allocation.status = InventoryAllocation.Status.REFUNDED
        self.allocation.save(update_fields=["status", "updated_at"])

        response = self.client.get(
            reverse("orders:order_success", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your order has been refunded")
        self.assertNotContains(response, "payment processing")
        self.assertNotContains(response, 'http-equiv="refresh"')
