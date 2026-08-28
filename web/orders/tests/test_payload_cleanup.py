from datetime import datetime, timezone
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from web.orders.models import Order, Payment, Refund, StripeEvent


class LegacyStripePayloadCleanupTests(TestCase):
    def setUp(self):
        order = Order.objects.create(
            full_name="Payload Audit",
            email="audit@example.com",
            grand_total=Decimal("10.00"),
        )
        self.payment = Payment.objects.create(
            order=order,
            stripe_payment_intent_id="pi_payload_cleanup",
            amount=Decimal("10.00"),
            currency="usd",
            status=Payment.Status.SUCCEEDED,
            raw_response={"legacy": "payment"},
        )
        self.refund = Refund.objects.create(
            payment=self.payment,
            stripe_refund_id="re_payload_cleanup",
            stripe_payment_intent_id="pi_payload_cleanup",
            amount=Decimal("5.00"),
            currency="usd",
            status=Refund.Status.SUCCEEDED,
            stripe_created_at=datetime.now(timezone.utc),
            raw_response={"legacy": "refund"},
        )
        self.event = StripeEvent.objects.create(
            stripe_event_id="evt_payload_cleanup",
            event_type="checkout.session.completed",
            raw_event={"legacy": "event"},
        )

    def test_cleanup_requires_explicit_backup_confirmation(self):
        with self.assertRaises(CommandError):
            call_command("purge_legacy_stripe_payloads", stdout=StringIO())

        self.event.refresh_from_db()
        self.payment.refresh_from_db()
        self.refund.refresh_from_db()
        self.assertEqual(self.event.raw_event, {"legacy": "event"})
        self.assertEqual(self.payment.raw_response, {"legacy": "payment"})
        self.assertEqual(self.refund.raw_response, {"legacy": "refund"})

    def test_confirmed_cleanup_removes_only_raw_payload_fields(self):
        call_command(
            "purge_legacy_stripe_payloads",
            confirm_backup=True,
            stdout=StringIO(),
        )

        self.event.refresh_from_db()
        self.payment.refresh_from_db()
        self.refund.refresh_from_db()
        self.assertIsNone(self.event.raw_event)
        self.assertEqual(self.payment.raw_response, {})
        self.assertEqual(self.refund.raw_response, {})
        self.assertEqual(self.payment.stripe_payment_intent_id, "pi_payload_cleanup")
        self.assertEqual(self.refund.stripe_refund_id, "re_payload_cleanup")
