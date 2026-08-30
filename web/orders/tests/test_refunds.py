import json
from datetime import datetime, timedelta, timezone as datetime_timezone
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from web.orders.models import (
    InventoryAllocation,
    Order,
    OrderStatusEvent,
    Payment,
    Refund,
    StripeEvent,
)


class StripeRefundWebhookTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            full_name="Refund Test Customer",
            email="customer@example.com",
            status=Order.Status.PAID,
            subtotal=Decimal("100.00"),
            grand_total=Decimal("100.00"),
        )
        self.payment = Payment.objects.create(
            order=self.order,
            stripe_payment_intent_id="pi_refund_test",
            amount=Decimal("100.00"),
            currency="usd",
            status=Payment.Status.SUCCEEDED,
        )
        self.allocation = InventoryAllocation.objects.create(
            order=self.order,
            status=InventoryAllocation.Status.REVIEW_REQUIRED,
            review_due_at=timezone.now(),
        )

    def refund_event(
        self,
        *,
        event_id,
        event_type="refund.updated",
        refund_id="re_test",
        amount=10000,
        status=Refund.Status.PENDING,
        payment_intent_id="pi_refund_test",
    ):
        return {
            "id": event_id,
            "type": event_type,
            "data": {
                "object": {
                    "id": refund_id,
                    "payment_intent": payment_intent_id,
                    "amount": amount,
                    "currency": "usd",
                    "status": status,
                    "reason": "requested_by_customer",
                    "failure_reason": (
                        "declined" if status == Refund.Status.FAILED else None
                    ),
                    "created": 1786900000,
                },
            },
        }

    def post_signed_event(self, event):
        payload = json.dumps(event)

        with patch(
            "web.orders.views.stripe.Webhook.construct_event",
            return_value=event,
        ):
            return self.client.post(
                reverse("orders:stripe_webhook"),
                data=payload,
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

    def test_pending_full_refund_moves_allocation_to_refund_pending(self):
        response = self.post_signed_event(
            self.refund_event(event_id="evt_refund_pending")
        )

        self.assertEqual(response.status_code, 200)
        self.allocation.refresh_from_db()
        self.order.refresh_from_db()
        refund = Refund.objects.get(stripe_refund_id="re_test")
        self.assertEqual(refund.status, Refund.Status.PENDING)
        self.assertEqual(refund.amount, Decimal("100.00"))
        self.assertEqual(
            refund.stripe_created_at,
            datetime.fromtimestamp(1786900000, tz=datetime_timezone.utc),
        )
        self.assertEqual(
            self.allocation.status,
            InventoryAllocation.Status.REFUND_PENDING,
        )
        self.assertIsNotNone(self.allocation.refund_initiated_at)
        self.assertEqual(self.order.status, Order.Status.PAID)

    def test_requires_action_full_refund_is_still_pending(self):
        response = self.post_signed_event(
            self.refund_event(
                event_id="evt_refund_requires_action",
                status=Refund.Status.REQUIRES_ACTION,
            )
        )

        self.assertEqual(response.status_code, 200)
        self.allocation.refresh_from_db()
        self.assertEqual(
            self.allocation.status,
            InventoryAllocation.Status.REFUND_PENDING,
        )

    def test_multiple_partial_refunds_require_cumulative_success(self):
        first_response = self.post_signed_event(
            self.refund_event(
                event_id="evt_partial_one",
                refund_id="re_partial_one",
                amount=4000,
                status=Refund.Status.SUCCEEDED,
            )
        )
        self.allocation.refresh_from_db()
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(
            self.allocation.status,
            InventoryAllocation.Status.REVIEW_REQUIRED,
        )

        pending_response = self.post_signed_event(
            self.refund_event(
                event_id="evt_partial_two_pending",
                refund_id="re_partial_two",
                amount=6000,
            )
        )
        self.allocation.refresh_from_db()
        self.assertEqual(pending_response.status_code, 200)
        self.assertEqual(
            self.allocation.status,
            InventoryAllocation.Status.REFUND_PENDING,
        )

        succeeded_response = self.post_signed_event(
            self.refund_event(
                event_id="evt_partial_two_succeeded",
                refund_id="re_partial_two",
                amount=6000,
                status=Refund.Status.SUCCEEDED,
            )
        )

        self.assertEqual(succeeded_response.status_code, 200)
        self.allocation.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(
            self.allocation.status,
            InventoryAllocation.Status.REFUNDED,
        )
        self.assertIsNotNone(self.allocation.resolved_at)
        self.assertTrue(self.allocation.is_overdue)
        self.assertEqual(self.order.status, Order.Status.REFUNDED)
        self.assertTrue(
            OrderStatusEvent.objects.filter(
                order=self.order,
                to_status=Order.Status.REFUNDED,
            ).exists()
        )

    def test_late_created_event_does_not_regress_updated_success(self):
        updated = self.refund_event(
            event_id="evt_refund_updated_first",
            status=Refund.Status.SUCCEEDED,
        )
        created = self.refund_event(
            event_id="evt_refund_created_late",
            event_type="refund.created",
            status=Refund.Status.PENDING,
        )

        self.assertEqual(self.post_signed_event(updated).status_code, 200)
        self.assertEqual(self.post_signed_event(created).status_code, 200)

        refund = Refund.objects.get(stripe_refund_id="re_test")
        self.allocation.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(refund.status, Refund.Status.SUCCEEDED)
        self.assertEqual(
            self.allocation.status,
            InventoryAllocation.Status.REFUNDED,
        )
        self.assertEqual(self.order.status, Order.Status.REFUNDED)

    def test_duplicate_refund_event_is_idempotent(self):
        event = self.refund_event(
            event_id="evt_refund_duplicate",
            status=Refund.Status.SUCCEEDED,
        )

        self.assertEqual(self.post_signed_event(event).status_code, 200)
        self.assertEqual(self.post_signed_event(event).status_code, 200)

        self.assertEqual(Refund.objects.count(), 1)
        self.assertEqual(StripeEvent.objects.count(), 1)
        self.assertEqual(
            OrderStatusEvent.objects.filter(
                order=self.order,
                to_status=Order.Status.REFUNDED,
            ).count(),
            1,
        )

    def test_full_refund_updates_normal_allocated_order_without_releasing_stock(self):
        self.allocation.status = InventoryAllocation.Status.ALLOCATED
        self.allocation.save(update_fields=["status"])

        response = self.post_signed_event(
            self.refund_event(
                event_id="evt_normal_full_refund",
                status=Refund.Status.SUCCEEDED,
            )
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.allocation.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.REFUNDED)
        self.assertEqual(
            self.allocation.status,
            InventoryAllocation.Status.ALLOCATED,
        )

    def test_terminal_refund_and_order_do_not_regress_on_late_failure(self):
        succeeded = self.refund_event(
            event_id="evt_refund_succeeded_first",
            status=Refund.Status.SUCCEEDED,
        )
        failed = self.refund_event(
            event_id="evt_refund_failed_late",
            event_type="refund.failed",
            status=Refund.Status.FAILED,
        )

        self.assertEqual(self.post_signed_event(succeeded).status_code, 200)
        self.assertEqual(self.post_signed_event(failed).status_code, 200)

        refund = Refund.objects.get(stripe_refund_id="re_test")
        self.order.refresh_from_db()
        self.assertEqual(refund.status, Refund.Status.SUCCEEDED)
        self.assertEqual(self.order.status, Order.Status.REFUNDED)

    def test_failed_or_canceled_refund_reopens_review_with_new_deadline(self):
        for terminal_status in [Refund.Status.FAILED, Refund.Status.CANCELED]:
            with self.subTest(status=terminal_status):
                self.allocation.review_due_at = timezone.now() - timedelta(days=1)
                self.allocation.save(update_fields=["review_due_at"])
                pending_event = self.refund_event(
                    event_id=f"evt_{terminal_status}_pending",
                    refund_id=f"re_{terminal_status}",
                )
                self.assertEqual(
                    self.post_signed_event(pending_event).status_code,
                    200,
                )
                self.allocation.refresh_from_db()
                original_deadline = self.allocation.review_due_at
                self.allocation.customer_notified_at = timezone.now()
                self.allocation.save(update_fields=["customer_notified_at"])

                terminal_event = self.refund_event(
                    event_id=f"evt_{terminal_status}_terminal",
                    event_type=(
                        "refund.failed"
                        if terminal_status == Refund.Status.FAILED
                        else "refund.updated"
                    ),
                    refund_id=f"re_{terminal_status}",
                    status=terminal_status,
                )
                self.assertEqual(
                    self.post_signed_event(terminal_event).status_code,
                    200,
                )

                self.allocation.refresh_from_db()
                self.order.refresh_from_db()
                self.assertEqual(
                    self.allocation.status,
                    InventoryAllocation.Status.REVIEW_REQUIRED,
                )
                self.assertIsNone(self.allocation.refund_initiated_at)
                self.assertIsNone(self.allocation.customer_notified_at)
                self.assertIsNone(self.allocation.customer_notified_by)
                self.assertGreater(self.allocation.review_due_at, original_deadline)
                self.assertEqual(self.order.status, Order.Status.PAID)

                self.allocation.status = InventoryAllocation.Status.REVIEW_REQUIRED
                self.allocation.save(update_fields=["status"])

    def test_unmatched_payment_intent_returns_retryable_error(self):
        event = self.refund_event(
            event_id="evt_unmatched_refund",
            payment_intent_id="pi_missing",
        )

        response = self.post_signed_event(event)

        self.assertEqual(response.status_code, 500)
        stripe_event = StripeEvent.objects.get(
            stripe_event_id="evt_unmatched_refund"
        )
        self.assertFalse(stripe_event.processed)
        self.assertFalse(Refund.objects.exists())
