from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from web.orders.models import Order, OrderStatusEvent, Shipment


class ShipmentLifecycleTests(TestCase):
    def create_order(self, status=Order.Status.PAID):
        return Order.objects.create(
            full_name="Test Customer",
            email="customer@example.com",
            status=status,
        )

    def test_tracking_shipment_can_be_created_before_carrier_tender(self):
        order = self.create_order()

        shipment = Shipment.objects.create(
            order=order,
            carrier="UPS",
            tracking_number="1Z999TEST",
        )

        shipment.refresh_from_db()
        order.refresh_from_db()
        self.assertIsNotNone(shipment.pk)
        self.assertIsNone(shipment.estimated_delivery)
        self.assertIsNone(shipment.shipped_at)
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertFalse(OrderStatusEvent.objects.filter(order=order).exists())

    def test_first_shipped_timestamp_transitions_order_once(self):
        order = self.create_order()
        shipment = Shipment.objects.create(
            order=order,
            shipped_at=timezone.now(),
        )

        order.refresh_from_db()
        event = OrderStatusEvent.objects.get(order=order)
        self.assertEqual(order.status, Order.Status.SHIPPED)
        self.assertEqual(event.from_status, Order.Status.PAID)
        self.assertEqual(event.to_status, Order.Status.SHIPPED)
        self.assertEqual(event.source, OrderStatusEvent.Source.SHIPMENT)
        self.assertEqual(event.reason, "carrier_tender_recorded")
        self.assertIn(f"Shipment #{shipment.pk}", event.internal_detail)

        shipment.notes = "Tracking confirmed."
        shipment.save()

        self.assertEqual(OrderStatusEvent.objects.filter(order=order).count(), 1)

    def test_delivered_timestamp_requires_and_follows_shipped_status(self):
        order = self.create_order(status=Order.Status.PROCESSING)
        shipment = Shipment.objects.create(order=order)

        shipment.shipped_at = timezone.now()
        shipment.save(update_fields=["shipped_at", "updated_at"])
        shipment.delivered_at = timezone.now()
        shipment.save(update_fields=["delivered_at", "updated_at"])

        order.refresh_from_db()
        events = list(
            OrderStatusEvent.objects.filter(order=order).order_by("id")
        )
        self.assertEqual(order.status, Order.Status.DELIVERED)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].from_status, Order.Status.PROCESSING)
        self.assertEqual(events[0].to_status, Order.Status.SHIPPED)
        self.assertEqual(events[1].from_status, Order.Status.SHIPPED)
        self.assertEqual(events[1].to_status, Order.Status.DELIVERED)

        shipment.save()

        self.assertEqual(OrderStatusEvent.objects.filter(order=order).count(), 2)

    def test_shipped_and_delivered_timestamps_can_be_recorded_together(self):
        order = self.create_order()
        timestamp = timezone.now()

        Shipment.objects.create(
            order=order,
            shipped_at=timestamp,
            delivered_at=timestamp,
        )

        order.refresh_from_db()
        events = list(
            OrderStatusEvent.objects.filter(order=order).order_by("id")
        )
        self.assertEqual(order.status, Order.Status.DELIVERED)
        self.assertEqual(
            [event.to_status for event in events],
            [Order.Status.SHIPPED, Order.Status.DELIVERED],
        )

    def test_unfulfillable_orders_cannot_be_marked_shipped(self):
        invalid_statuses = [
            Order.Status.PENDING_PAYMENT,
            Order.Status.CANCELED,
            Order.Status.REFUNDED,
        ]

        for status in invalid_statuses:
            with self.subTest(status=status):
                order = self.create_order(status=status)

                with self.assertRaises(ValidationError):
                    Shipment.objects.create(
                        order=order,
                        shipped_at=timezone.now(),
                    )

                self.assertFalse(Shipment.objects.filter(order=order).exists())
                self.assertFalse(
                    OrderStatusEvent.objects.filter(order=order).exists()
                )

    def test_order_cannot_be_marked_delivered_before_shipped(self):
        order = self.create_order()

        with self.assertRaises(ValidationError):
            Shipment.objects.create(
                order=order,
                delivered_at=timezone.now(),
            )

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertFalse(Shipment.objects.filter(order=order).exists())
        self.assertFalse(OrderStatusEvent.objects.filter(order=order).exists())

    def test_timestamp_not_in_update_fields_does_not_change_order_status(self):
        order = self.create_order()
        shipment = Shipment.objects.create(order=order)
        shipment.shipped_at = timezone.now()
        shipment.notes = "Label created only."

        shipment.save(update_fields=["notes", "updated_at"])

        shipment.refresh_from_db()
        order.refresh_from_db()
        self.assertIsNone(shipment.shipped_at)
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertFalse(OrderStatusEvent.objects.filter(order=order).exists())

    def test_shipment_and_order_transition_roll_back_if_history_write_fails(self):
        order = self.create_order()

        with patch(
            "web.orders.models.OrderStatusEvent.objects.create",
            side_effect=RuntimeError("history write failed"),
        ):
            with self.assertRaises(RuntimeError):
                Shipment.objects.create(
                    order=order,
                    shipped_at=timezone.now(),
                )

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertFalse(Shipment.objects.filter(order=order).exists())
        self.assertFalse(OrderStatusEvent.objects.filter(order=order).exists())
