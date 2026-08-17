import json
from decimal import Decimal
from unittest.mock import patch

import stripe
from django.test import TestCase
from django.urls import reverse

from web.orders.models import (
    InventoryAllocation,
    Order,
    OrderItem,
    OrderStatusEvent,
    Payment,
    StripeEvent,
)
from web.products.models import Product, ProductVariant


class StripePaymentWebhookTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="TreadJoy Test Shoe",
            slug="treadjoy-test-shoe",
            price=Decimal("50.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TJ-TEST-090-BLK",
            size="9",
            color="Black",
            stock_quantity=10,
        )
        self.order = Order.objects.create(
            full_name="Test Customer",
            email="customer@example.com",
            status=Order.Status.PENDING_PAYMENT,
            subtotal=Decimal("100.00"),
            grand_total=Decimal("100.00"),
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            variant=self.variant,
            product_name=self.product.name,
            sku=self.variant.sku,
            unit_price=Decimal("50.00"),
            quantity=2,
            size=self.variant.size,
            color=self.variant.color,
            line_total=Decimal("100.00"),
        )

    def checkout_completed_event(self, event_id="evt_checkout_completed"):
        return {
            "id": event_id,
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_completed",
                    "payment_intent": "pi_test_completed",
                    "amount_subtotal": 10000,
                    "amount_total": 12000,
                    "currency": "usd",
                    "metadata": {
                        "order_id": str(self.order.id),
                    },
                },
            },
        }

    def payment_intent_succeeded_event(self):
        return {
            "id": "evt_payment_intent_succeeded",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_completed",
                    "amount_received": 12000,
                    "currency": "usd",
                    "metadata": {
                        "order_id": str(self.order.id),
                    },
                },
            },
        }

    def post_signed_event(self, event):
        payload = json.dumps(event)

        with patch(
            "web.orders.views.stripe.Webhook.construct_event",
            return_value=event,
        ) as construct_event:
            response = self.client.post(
                reverse("orders:stripe_webhook"),
                data=payload,
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        construct_event.assert_called_once()
        return response

    def test_checkout_completed_records_payment_and_reduces_inventory(self):
        response = self.post_signed_event(self.checkout_completed_event())

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.variant.refresh_from_db()
        payment = Payment.objects.get(order=self.order)
        status_event = OrderStatusEvent.objects.get(order=self.order)
        stripe_event = StripeEvent.objects.get(
            stripe_event_id="evt_checkout_completed"
        )

        self.assertEqual(self.order.status, Order.Status.PAID)
        self.assertEqual(self.order.subtotal, Decimal("100.00"))
        self.assertEqual(self.order.grand_total, Decimal("120.00"))
        self.assertEqual(
            self.order.stripe_checkout_session_id,
            "cs_test_completed",
        )
        self.assertEqual(
            self.order.stripe_payment_intent_id,
            "pi_test_completed",
        )
        self.assertEqual(payment.status, Payment.Status.SUCCEEDED)
        self.assertEqual(payment.amount, Decimal("120.00"))
        self.assertEqual(payment.currency, "usd")
        self.assertEqual(status_event.from_status, Order.Status.PENDING_PAYMENT)
        self.assertEqual(status_event.to_status, Order.Status.PAID)
        self.assertEqual(self.variant.stock_quantity, 8)
        allocation = InventoryAllocation.objects.get(order=self.order)
        allocation_item = allocation.items.get()
        self.assertEqual(
            allocation.status,
            InventoryAllocation.Status.ALLOCATED,
        )
        self.assertEqual(allocation_item.required_quantity, 2)
        self.assertEqual(allocation_item.allocated_quantity, 2)
        self.assertEqual(allocation_item.variant_available_before, 10)
        self.assertEqual(allocation_item.variant_available_after, 8)
        self.assertTrue(stripe_event.processed)
        self.assertIsNotNone(stripe_event.processed_at)

    def test_duplicate_event_is_processed_only_once(self):
        event = self.checkout_completed_event()

        first_response = self.post_signed_event(event)
        second_response = self.post_signed_event(event)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 8)
        self.assertEqual(Payment.objects.filter(order=self.order).count(), 1)
        self.assertEqual(
            OrderStatusEvent.objects.filter(order=self.order).count(),
            1,
        )
        self.assertEqual(
            StripeEvent.objects.filter(
                stripe_event_id="evt_checkout_completed"
            ).count(),
            1,
        )

    def test_related_success_events_do_not_reduce_inventory_twice(self):
        checkout_response = self.post_signed_event(
            self.checkout_completed_event()
        )

        self.order.refresh_from_db()
        self.order.status = Order.Status.PROCESSING
        self.order.save(update_fields=["status", "updated_at"])

        payment_intent_response = self.post_signed_event(
            self.payment_intent_succeeded_event()
        )

        self.assertEqual(checkout_response.status_code, 200)
        self.assertEqual(payment_intent_response.status_code, 200)

        self.variant.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PROCESSING)
        self.assertEqual(self.variant.stock_quantity, 8)
        self.assertEqual(Payment.objects.filter(order=self.order).count(), 1)
        self.assertEqual(
            OrderStatusEvent.objects.filter(order=self.order).count(),
            1,
        )
        self.assertEqual(StripeEvent.objects.filter(processed=True).count(), 2)
        self.assertEqual(
            InventoryAllocation.objects.filter(order=self.order).count(),
            1,
        )

    def test_insufficient_inventory_records_paid_order_for_staff_review(self):
        self.variant.stock_quantity = 1
        self.variant.save(update_fields=["stock_quantity"])

        response = self.post_signed_event(self.checkout_completed_event())

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.variant.refresh_from_db()
        payment = Payment.objects.get(order=self.order)
        allocation = InventoryAllocation.objects.get(order=self.order)
        allocation_item = allocation.items.get()
        stripe_event = StripeEvent.objects.get(
            stripe_event_id="evt_checkout_completed"
        )

        self.assertEqual(self.order.status, Order.Status.PAID)
        self.assertEqual(payment.status, Payment.Status.SUCCEEDED)
        self.assertEqual(self.variant.stock_quantity, 1)
        self.assertEqual(
            allocation.status,
            InventoryAllocation.Status.REVIEW_REQUIRED,
        )
        self.assertIsNotNone(allocation.review_due_at)
        self.assertEqual(allocation_item.required_quantity, 2)
        self.assertEqual(allocation_item.allocated_quantity, 0)
        self.assertEqual(allocation_item.variant_available_before, 1)
        self.assertEqual(allocation_item.variant_available_after, 1)
        self.assertTrue(stripe_event.processed)

    def test_missing_order_metadata_does_not_change_business_records(self):
        event = self.checkout_completed_event(event_id="evt_missing_metadata")
        event["data"]["object"]["metadata"] = {}

        response = self.post_signed_event(event)

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.variant.refresh_from_db()
        stripe_event = StripeEvent.objects.get(
            stripe_event_id="evt_missing_metadata"
        )

        self.assertEqual(self.order.status, Order.Status.PENDING_PAYMENT)
        self.assertEqual(self.variant.stock_quantity, 10)
        self.assertFalse(Payment.objects.exists())
        self.assertFalse(OrderStatusEvent.objects.exists())
        self.assertTrue(stripe_event.processed)

    def test_invalid_signature_is_rejected_before_event_processing(self):
        event = self.checkout_completed_event(event_id="evt_bad_signature")

        with patch(
            "web.orders.views.stripe.Webhook.construct_event",
            side_effect=stripe.error.SignatureVerificationError(
                "Invalid signature",
                "test-signature",
            ),
        ):
            response = self.client.post(
                reverse("orders:stripe_webhook"),
                data=json.dumps(event),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StripeEvent.objects.exists())
        self.assertFalse(Payment.objects.exists())
