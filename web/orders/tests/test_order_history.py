from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.test import TestCase

from web.orders.models import (
    Order,
    OrderItem,
    OrderStatusEvent,
    ShippingAddress,
)
from web.orders.transitions import OrderTransitionError, transition_order
from web.products.models import Product


class OrderTransitionTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="order-operator",
            password="test-password",
            is_staff=True,
        )
        self.order = Order.objects.create(
            full_name="History Customer",
            email="history@example.com",
            status=Order.Status.PAID,
        )

    def test_staff_processing_transition_is_audited_and_idempotent(self):
        order, changed = transition_order(
            self.order,
            Order.Status.PROCESSING,
            source=OrderStatusEvent.Source.ADMIN,
            reason="staff_started_processing",
            actor=self.staff,
            internal_detail="Internal fulfillment detail.",
            customer_message="Your order is being prepared for shipment.",
        )
        _, repeated = transition_order(
            order,
            Order.Status.PROCESSING,
            source=OrderStatusEvent.Source.ADMIN,
            reason="staff_started_processing",
            actor=self.staff,
        )

        event = OrderStatusEvent.objects.get(order=order)
        self.assertTrue(changed)
        self.assertFalse(repeated)
        self.assertEqual(event.actor, self.staff)
        self.assertEqual(event.source, OrderStatusEvent.Source.ADMIN)
        self.assertEqual(OrderStatusEvent.objects.count(), 1)

    def test_direct_or_wrong_source_fulfillment_transitions_are_rejected(self):
        with self.assertRaises(OrderTransitionError):
            transition_order(
                self.order,
                Order.Status.DELIVERED,
                source=OrderStatusEvent.Source.ADMIN,
                reason="invalid_direct_delivery",
                actor=self.staff,
            )
        with self.assertRaises(OrderTransitionError):
            transition_order(
                self.order,
                Order.Status.SHIPPED,
                source=OrderStatusEvent.Source.ADMIN,
                reason="invalid_manual_shipping",
                actor=self.staff,
            )

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PAID)
        self.assertFalse(OrderStatusEvent.objects.exists())

    def test_refunded_status_is_terminal(self):
        order, _ = transition_order(
            self.order,
            Order.Status.REFUNDED,
            source=OrderStatusEvent.Source.REFUND,
            reason="full_refund_confirmed",
        )

        with self.assertRaises(OrderTransitionError):
            transition_order(
                order,
                Order.Status.PAID,
                source=OrderStatusEvent.Source.STRIPE,
                reason="invalid_reopen",
            )

    def test_status_history_cannot_be_changed_or_deleted(self):
        event = OrderStatusEvent.objects.create(
            order=self.order,
            from_status="",
            to_status=Order.Status.PAID,
            source=OrderStatusEvent.Source.SYSTEM,
            reason="test_event",
        )
        event.internal_detail = "Changed"

        with self.assertRaises(ValidationError):
            event.save()
        with self.assertRaises(ValidationError):
            event.delete()
        with self.assertRaises(ValidationError):
            OrderStatusEvent.objects.filter(pk=event.pk).update(
                reason="changed"
            )
        with self.assertRaises(ValidationError):
            OrderStatusEvent.objects.filter(pk=event.pk).delete()

    def test_customer_history_hides_actor_and_internal_detail(self):
        OrderStatusEvent.objects.create(
            order=self.order,
            actor=self.staff,
            from_status=Order.Status.PAID,
            to_status=Order.Status.PROCESSING,
            source=OrderStatusEvent.Source.ADMIN,
            reason="staff_started_processing",
            internal_detail="Private warehouse note and staff-only detail.",
            customer_message="Your order is being prepared.",
        )

        rendered = render_to_string(
            "orders/order_detail.html", {"order": self.order}
        )

        self.assertContainsText(rendered, "Your order is being prepared.")
        self.assertNotIn("Private warehouse note", rendered)
        self.assertNotIn(self.staff.username, rendered)

    def test_staff_account_deletion_preserves_status_history(self):
        event = OrderStatusEvent.objects.create(
            order=self.order,
            actor=self.staff,
            from_status=Order.Status.PAID,
            to_status=Order.Status.PROCESSING,
            source=OrderStatusEvent.Source.ADMIN,
            reason="staff_started_processing",
        )

        self.staff.delete()
        event.refresh_from_db()

        self.assertIsNone(event.actor_id)
        self.assertEqual(event.reason, "staff_started_processing")

    def assertContainsText(self, rendered, text):
        self.assertIn(text, rendered)


class OrderHistoricalSnapshotTests(TestCase):
    def test_account_deletion_preserves_order_shipping_snapshot(self):
        user = get_user_model().objects.create_user(username="snapshot-owner")
        address = ShippingAddress.objects.create(
            user=user,
            full_name="Snapshot Owner",
            email="snapshot@example.com",
            address_line_1="123 Test Street",
            city="Chicago",
            state="IL",
            postal_code="60601",
        )
        order = Order.objects.create(
            user=user,
            shipping_address=address,
            full_name=address.full_name,
            email=address.email,
            shipping_full_name=address.full_name,
            shipping_email=address.email,
            shipping_address_line_1=address.address_line_1,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_postal_code=address.postal_code,
            shipping_country=address.country,
        )

        user.delete()
        order.refresh_from_db()

        self.assertIsNone(order.user_id)
        self.assertIsNone(order.shipping_address_id)
        self.assertEqual(order.shipping_address_line_1, "123 Test Street")
        self.assertEqual(order.shipping_email, "snapshot@example.com")

    def test_database_rejects_inconsistent_order_total(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.create(
                full_name="Invalid Total",
                subtotal=Decimal("10.00"),
                grand_total=Decimal("11.00"),
            )

    def test_database_rejects_inconsistent_line_total(self):
        order = Order.objects.create(full_name="Invalid Line")
        product = Product.objects.create(
            name="Formula Shoe",
            slug="formula-shoe",
            price=Decimal("10.00"),
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=Decimal("10.00"),
                quantity=2,
                line_total=Decimal("19.00"),
            )
