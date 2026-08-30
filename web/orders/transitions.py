"""Authoritative, audited order-status transitions.

All callers use this module so legal transitions, row locking, inventory-review
guards, and append-only history cannot drift between Stripe, shipments, refunds,
and staff workflows.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import InventoryAllocation, Order, OrderStatusEvent


class OrderTransitionError(ValidationError):
    pass


ALLOWED_TRANSITIONS = {
    Order.Status.PENDING_PAYMENT: {Order.Status.PAID},
    Order.Status.PAID: {
        Order.Status.PROCESSING,
        Order.Status.SHIPPED,
        Order.Status.REVIEW_REQUIRED,
        Order.Status.REFUNDED,
    },
    Order.Status.PROCESSING: {
        Order.Status.SHIPPED,
        Order.Status.REFUNDED,
    },
    Order.Status.SHIPPED: {
        Order.Status.DELIVERED,
        Order.Status.REFUNDED,
    },
    Order.Status.DELIVERED: {Order.Status.REFUNDED},
    Order.Status.CANCELED: {Order.Status.REFUNDED},
    Order.Status.REVIEW_REQUIRED: {Order.Status.REFUNDED},
    Order.Status.REFUNDED: set(),
}

SOURCE_REQUIREMENTS = {
    Order.Status.PAID: {OrderStatusEvent.Source.STRIPE},
    Order.Status.PROCESSING: {OrderStatusEvent.Source.ADMIN},
    Order.Status.SHIPPED: {OrderStatusEvent.Source.SHIPMENT},
    Order.Status.DELIVERED: {OrderStatusEvent.Source.SHIPMENT},
    Order.Status.REFUNDED: {OrderStatusEvent.Source.REFUND},
    Order.Status.REVIEW_REQUIRED: {
        OrderStatusEvent.Source.STRIPE,
        OrderStatusEvent.Source.SYSTEM,
    },
}

FULFILLMENT_STATUSES = {
    Order.Status.PROCESSING,
    Order.Status.SHIPPED,
    Order.Status.DELIVERED,
}


def record_initial_status(
    order,
    *,
    source,
    reason,
    actor=None,
    external_reference="",
    internal_detail="",
    customer_message="",
):
    """Record the immutable creation state for a newly persisted order."""
    if not reason:
        raise OrderTransitionError("Order status history requires a reason.")
    return OrderStatusEvent.objects.create(
        order=order,
        actor=actor,
        from_status="",
        to_status=order.status,
        source=source,
        reason=reason,
        external_reference=external_reference,
        internal_detail=internal_detail,
        customer_message=customer_message,
        # One-release compatibility field. Customer views never render it.
        note=internal_detail,
    )


@transaction.atomic
def transition_order(
    order,
    to_status,
    *,
    source,
    reason,
    actor=None,
    external_reference="",
    internal_detail="",
    customer_message="",
):
    """Lock and transition an order, returning ``(locked_order, changed)``."""
    locked_order = Order.objects.select_for_update().get(pk=order.pk)
    from_status = locked_order.status

    if not reason:
        raise OrderTransitionError("Order status history requires a reason.")

    if from_status == to_status:
        return locked_order, False

    if to_status not in ALLOWED_TRANSITIONS.get(from_status, set()):
        raise OrderTransitionError(
            f"Order cannot transition from {from_status} to {to_status}."
        )

    required_sources = SOURCE_REQUIREMENTS.get(to_status)
    if required_sources is not None and source not in required_sources:
        raise OrderTransitionError(
            f"The {to_status} transition cannot be recorded by {source}."
        )

    if source == OrderStatusEvent.Source.ADMIN:
        if actor is None or not actor.is_authenticated or not actor.is_staff:
            raise OrderTransitionError(
                "Admin order transitions require an authenticated staff actor."
            )

    if to_status in FULFILLMENT_STATUSES:
        allocation_is_blocked = InventoryAllocation.objects.filter(
            order=locked_order,
            status__in={
                InventoryAllocation.Status.REVIEW_REQUIRED,
                InventoryAllocation.Status.REFUND_PENDING,
            },
        ).exists()
        if allocation_is_blocked:
            raise OrderTransitionError(
                "Resolve the inventory review before fulfilling this order."
            )

    locked_order.status = to_status
    locked_order.save(update_fields=["status", "updated_at"])
    OrderStatusEvent.objects.create(
        order=locked_order,
        actor=actor,
        from_status=from_status,
        to_status=to_status,
        source=source,
        reason=reason,
        external_reference=external_reference,
        internal_detail=internal_detail,
        customer_message=customer_message,
        # One-release compatibility field. Customer views never render it.
        note=internal_detail,
    )
    return locked_order, True
