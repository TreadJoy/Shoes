from datetime import datetime, time, timedelta, timezone as datetime_timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

import holidays
from django.db import transaction
from django.db.models import Min, Sum
from django.utils import timezone

from web.products.models import ProductVariant

from .models import (
    InventoryAllocation,
    InventoryAllocationItem,
    Order,
    OrderStatusEvent,
    Payment,
    Refund,
)


BUSINESS_TIME_ZONE = ZoneInfo("America/Chicago")
REVIEW_CUTOFF = time(hour=17)


class UnmatchedRefundPaymentError(Exception):
    pass


def next_inventory_review_deadline(detected_at=None):
    detected_at = detected_at or timezone.now()
    local_detected_at = timezone.localtime(
        detected_at,
        BUSINESS_TIME_ZONE,
    )
    candidate = local_detected_at.date() + timedelta(days=1)
    us_holidays = holidays.US(
        years=range(candidate.year, candidate.year + 2),
        observed=True,
    )

    while candidate.weekday() >= 5 or candidate in us_holidays:
        candidate += timedelta(days=1)

    local_deadline = datetime.combine(
        candidate,
        REVIEW_CUTOFF,
        tzinfo=BUSINESS_TIME_ZONE,
    )
    return local_deadline.astimezone(datetime_timezone.utc)


@transaction.atomic
def allocate_inventory_for_paid_order(order):
    order = Order.objects.select_for_update().get(pk=order.pk)
    existing_allocation = InventoryAllocation.objects.filter(
        order=order,
    ).first()

    if existing_allocation is not None:
        return existing_allocation

    requirements = list(
        order.items
        .exclude(variant_id__isnull=True)
        .values("variant_id")
        .annotate(
            required_quantity=Sum("quantity"),
            sku=Min("sku"),
        )
        .order_by("variant_id")
    )
    variant_ids = [
        requirement["variant_id"]
        for requirement in requirements
    ]
    variants = {
        variant.id: variant
        for variant in (
            ProductVariant.objects
            .select_for_update()
            .filter(id__in=variant_ids)
            .order_by("id")
        )
    }

    if len(variants) != len(variant_ids):
        raise ValueError(
            "An order item references an unavailable product variant."
        )

    has_shortfall = any(
        variants[requirement["variant_id"]].stock_quantity
        < requirement["required_quantity"]
        for requirement in requirements
    )
    allocation = InventoryAllocation.objects.create(
        order=order,
        status=(
            InventoryAllocation.Status.REVIEW_REQUIRED
            if has_shortfall
            else InventoryAllocation.Status.ALLOCATED
        ),
        review_due_at=(
            next_inventory_review_deadline()
            if has_shortfall
            else None
        ),
    )
    allocation_items = []

    for requirement in requirements:
        variant = variants[requirement["variant_id"]]
        required_quantity = requirement["required_quantity"]
        stock_before = variant.stock_quantity
        allocated_quantity = 0 if has_shortfall else required_quantity
        stock_after = stock_before - allocated_quantity

        allocation_items.append(
            InventoryAllocationItem(
                allocation=allocation,
                variant=variant,
                sku=requirement["sku"] or variant.sku,
                required_quantity=required_quantity,
                allocated_quantity=allocated_quantity,
                stock_before=stock_before,
                stock_after=stock_after,
            )
        )

        if not has_shortfall:
            variant.stock_quantity = stock_after
            variant.save(update_fields=["stock_quantity"])

    InventoryAllocationItem.objects.bulk_create(allocation_items)
    return allocation


def _stripe_object_id(value):
    if isinstance(value, dict):
        return value.get("id", "")
    return value or ""


def _stripe_created_at(refund_data):
    created_timestamp = refund_data.get("created")

    if created_timestamp is None:
        return timezone.now()

    return datetime.fromtimestamp(
        created_timestamp,
        tz=datetime_timezone.utc,
    )


def _change_order_status(order, new_status, note):
    if order.status == new_status:
        return

    previous_status = order.status
    order.status = new_status
    order.save(update_fields=["status", "updated_at"])
    OrderStatusEvent.objects.create(
        order=order,
        from_status=previous_status,
        to_status=new_status,
        note=note,
    )


@transaction.atomic
def synchronize_refund(refund_data, event_type=None):
    payment_intent_id = _stripe_object_id(
        refund_data.get("payment_intent")
    )

    try:
        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .get(stripe_payment_intent_id=payment_intent_id)
        )
    except Payment.DoesNotExist as error:
        raise UnmatchedRefundPaymentError(
            f"No payment found for PaymentIntent {payment_intent_id}."
        ) from error

    refund_defaults = {
        "payment": payment,
        "stripe_payment_intent_id": payment_intent_id,
        "amount": Decimal(refund_data.get("amount") or 0)
        / Decimal("100"),
        "currency": refund_data.get("currency", "usd"),
        "status": refund_data.get("status") or Refund.Status.PENDING,
        "reason": refund_data.get("reason") or "",
        "failure_reason": refund_data.get("failure_reason") or "",
        "stripe_created_at": _stripe_created_at(refund_data),
        "raw_response": refund_data,
    }
    refund = (
        Refund.objects.select_for_update()
        .filter(stripe_refund_id=refund_data["id"])
        .first()
    )

    # Stripe can deliver events out of order. A late refund.created snapshot must
    # not regress state already established by refund.updated/refund.failed.
    if refund is None:
        refund = Refund.objects.create(
            stripe_refund_id=refund_data["id"],
            **refund_defaults,
        )
    elif event_type != "refund.created":
        for field, value in refund_defaults.items():
            setattr(refund, field, value)
        refund.save(update_fields=[*refund_defaults, "updated_at"])
    allocation = (
        InventoryAllocation.objects.select_for_update()
        .filter(order=payment.order)
        .first()
    )

    if allocation is None or allocation.status == InventoryAllocation.Status.ALLOCATED:
        return refund

    active_statuses = [
        Refund.Status.PENDING,
        Refund.Status.REQUIRES_ACTION,
        Refund.Status.SUCCEEDED,
    ]
    active_refunds = payment.refunds.filter(status__in=active_statuses)
    active_total = active_refunds.aggregate(total=Sum("amount"))["total"]
    succeeded_total = payment.refunds.filter(
        status=Refund.Status.SUCCEEDED,
    ).aggregate(total=Sum("amount"))["total"]
    active_total = active_total or Decimal("0.00")
    succeeded_total = succeeded_total or Decimal("0.00")
    full_refund_succeeded = succeeded_total >= payment.amount
    full_refund_initiated = active_total >= payment.amount
    incoming_refund_failed = refund.status in [
        Refund.Status.FAILED,
        Refund.Status.CANCELED,
    ]

    if full_refund_succeeded:
        initiated_at = active_refunds.aggregate(
            initiated_at=Min("stripe_created_at")
        )["initiated_at"]
        allocation.status = InventoryAllocation.Status.REFUNDED
        allocation.refund_initiated_at = initiated_at
        allocation.resolved_at = timezone.now()
        allocation.save(
            update_fields=[
                "status",
                "refund_initiated_at",
                "resolved_at",
                "updated_at",
            ]
        )
        _change_order_status(
            payment.order,
            Order.Status.REFUNDED,
            "Full Stripe refund succeeded for an inventory shortfall.",
        )
        return refund

    if full_refund_initiated and not incoming_refund_failed:
        initiated_at = active_refunds.aggregate(
            initiated_at=Min("stripe_created_at")
        )["initiated_at"]
        allocation.status = InventoryAllocation.Status.REFUND_PENDING
        allocation.refund_initiated_at = initiated_at
        allocation.resolved_at = None
        allocation.save(
            update_fields=[
                "status",
                "refund_initiated_at",
                "resolved_at",
                "updated_at",
            ]
        )

        if payment.order.status == Order.Status.REFUNDED:
            _change_order_status(
                payment.order,
                Order.Status.PAID,
                "Stripe refund is no longer confirmed as succeeded.",
            )

        return refund

    refund_workflow_reopened = (
        incoming_refund_failed
        or allocation.status in [
            InventoryAllocation.Status.REFUND_PENDING,
            InventoryAllocation.Status.REFUNDED,
        ]
    )
    allocation.status = InventoryAllocation.Status.REVIEW_REQUIRED
    allocation.refund_initiated_at = None
    allocation.resolved_at = None

    update_fields = [
        "status",
        "refund_initiated_at",
        "resolved_at",
        "updated_at",
    ]

    if refund_workflow_reopened:
        allocation.review_due_at = next_inventory_review_deadline()
        allocation.customer_notified_at = None
        allocation.customer_notified_by = None
        update_fields.extend([
            "review_due_at",
            "customer_notified_at",
            "customer_notified_by",
        ])

    allocation.save(update_fields=update_fields)

    if payment.order.status == Order.Status.REFUNDED:
        _change_order_status(
            payment.order,
            Order.Status.PAID,
            "Stripe refund failed or was canceled; inventory review reopened.",
        )

    return refund
