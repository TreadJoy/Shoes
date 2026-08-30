from decimal import Decimal

from django.db import migrations


ZERO = Decimal("0.00")


def backfill_order_history(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    OrderItem = apps.get_model("orders", "OrderItem")
    OrderStatusEvent = apps.get_model("orders", "OrderStatusEvent")
    Payment = apps.get_model("orders", "Payment")
    CheckoutAttempt = apps.get_model("orders", "CheckoutAttempt")

    payment_currencies = dict(
        Payment.objects.exclude(currency="").values_list("order_id", "currency")
    )
    attempt_currencies = dict(
        CheckoutAttempt.objects.exclude(currency="").values_list("id", "currency")
    )

    for event in OrderStatusEvent.objects.iterator():
        event.source = "legacy"
        event.reason = "legacy_status_event"
        event.internal_detail = event.note
        event.save(update_fields=["source", "reason", "internal_detail"])

    for order in Order.objects.select_related("shipping_address").iterator():
        address = order.shipping_address
        currency = payment_currencies.get(order.id) or attempt_currencies.get(
            order.checkout_attempt_id
        ) or "usd"
        order.currency = currency.lower()[:3]
        order.shipping_full_name = (
            address.full_name if address else order.full_name
        )
        order.shipping_email = address.email if address else order.email
        order.shipping_address_line_1 = address.address_line_1 if address else ""
        order.shipping_address_line_2 = address.address_line_2 if address else ""
        order.shipping_city = address.city if address else ""
        order.shipping_state = address.state if address else ""
        order.shipping_postal_code = address.postal_code if address else ""
        order.shipping_country = address.country if address else ""

        expected_subtotal = (
            order.grand_total
            - order.shipping_total
            - order.tax_total
            + order.discount_total
        )
        formula_repaired = order.subtotal != expected_subtotal
        if formula_repaired:
            if expected_subtotal >= ZERO:
                order.subtotal = expected_subtotal
            else:
                order.subtotal = order.grand_total
                order.shipping_total = ZERO
                order.tax_total = ZERO
                order.discount_total = ZERO

        order.save(
            update_fields=[
                "currency",
                "shipping_full_name",
                "shipping_email",
                "shipping_address_line_1",
                "shipping_address_line_2",
                "shipping_city",
                "shipping_state",
                "shipping_postal_code",
                "shipping_country",
                "subtotal",
                "shipping_total",
                "tax_total",
                "discount_total",
            ]
        )
        if formula_repaired:
            OrderStatusEvent.objects.create(
                order=order,
                from_status=order.status,
                to_status=order.status,
                source="migration",
                reason="financial_formula_backfill",
                internal_detail=(
                    "Legacy total components were normalized while preserving "
                    "the recorded grand total."
                ),
            )

    for item in OrderItem.objects.iterator():
        expected_line_total = item.unit_price * item.quantity
        if item.line_total != expected_line_total:
            item.line_total = expected_line_total
            item.save(update_fields=["line_total"])


class Migration(migrations.Migration):
    dependencies = [("orders", "0022_order_history_expansion")]

    operations = [
        migrations.RunPython(backfill_order_history, migrations.RunPython.noop),
    ]
