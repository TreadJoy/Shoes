from datetime import datetime, time, timedelta, timezone as datetime_timezone
from dataclasses import dataclass
from decimal import Decimal
import logging
from uuid import uuid4
from zoneinfo import ZoneInfo

import holidays
import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Min, Sum
from django.utils import timezone

from web.cart.models import CartItem
from web.products.models import (
    PreorderBatch,
    PreorderVariantAllocation,
    ProductVariant,
)
from web.products.services import (
    HERITAGE_COURT_V1,
    validate_cart_items_for_checkout,
    validate_heritage_court_bom,
    variant_availability,
)

from .models import (
    CheckoutAttempt,
    CheckoutQuoteComponent,
    CheckoutQuoteLine,
    InventoryAllocation,
    InventoryAllocationItem,
    InventoryReservation,
    Order,
    OrderItem,
    OrderItemComponentSnapshot,
    OrderStatusEvent,
    Payment,
    Refund,
    ShippingAddress,
)
from .transitions import record_initial_status, transition_order


BUSINESS_TIME_ZONE = ZoneInfo("America/Chicago")
REVIEW_CUTOFF = time(hour=17)
logger = logging.getLogger(__name__)


class UnmatchedRefundPaymentError(Exception):
    pass


class ReservationError(ValueError):
    pass


@dataclass(frozen=True)
class CheckoutReconciliationResult:
    state: str
    attempt: CheckoutAttempt | None = None
    order: Order | None = None
    reason: str = ""


RESERVATION_DURATION = timedelta(minutes=30)
ELIGIBLE_SHIPPING_STATES = {
    "AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND",
    "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY",
}


def validate_shipping_eligibility_state(value):
    state = (value or "").strip().upper()
    if state not in ELIGIBLE_SHIPPING_STATES:
        raise ReservationError(
            "Enter a valid contiguous U.S. state or Washington, D.C."
        )
    return state


@transaction.atomic
def create_checkout_attempt(cart, *, user, email, eligibility_state):
    """Lock cart SKUs, quote current prices, and reserve 30 minutes atomically."""
    state = validate_shipping_eligibility_state(eligibility_state)
    locked_cart = cart.__class__.objects.select_for_update().get(pk=cart.pk)
    cart_items = list(
        locked_cart.items.select_related("variant", "variant__product")
        .order_by("variant_id", "id")
    )
    if not cart_items:
        raise ReservationError("Your cart is empty.")

    validate_cart_items_for_checkout(cart_items)
    now = timezone.now()
    user_id = user.pk if getattr(user, "is_authenticated", False) else None
    normalized_email = (email or "").strip().lower()
    existing_attempt = (
        CheckoutAttempt.objects.select_for_update()
        .prefetch_related("quote_lines")
        .filter(
            cart=locked_cart,
            status__in=[
                CheckoutAttempt.Status.CREATED,
                CheckoutAttempt.Status.STRIPE_CREATED,
            ],
            expires_at__gt=now,
        )
        .first()
    )
    if existing_attempt is not None:
        existing_signature = {
            line.variant_id: (
                line.quantity,
                line.unit_price,
                line.fulfillment_type,
                line.preorder_batch_id,
            )
            for line in existing_attempt.quote_lines.all()
        }
        current_signature = {}
        for item in cart_items:
            availability = variant_availability(item.variant)
            current_signature[item.variant_id] = (
                item.quantity,
                item.variant.current_price(),
                availability.fulfillment_type,
                availability.preorder_batch.pk
                if availability.preorder_batch is not None
                else None,
            )
        if (
            existing_attempt.user_id == user_id
            and existing_attempt.email == normalized_email
            and existing_attempt.eligibility_state == state
            and existing_signature == current_signature
        ):
            return existing_attempt
        release_attempt_reservations(existing_attempt)

    # Stripe evaluates its 30-minute minimum at API receipt time. Round up one
    # second so the provider and reservation share a valid effective deadline
    # without extending the reservation on ambiguous retries.
    expires_at = (
        now.replace(microsecond=0) + RESERVATION_DURATION + timedelta(seconds=1)
    )
    attempt = CheckoutAttempt.objects.create(
        cart=locked_cart,
        user_id=user_id,
        email=normalized_email,
        eligibility_state=state,
        currency="usd",
        idempotency_key=f"checkout-{uuid4().hex}",
        expires_at=expires_at,
    )
    subtotal = Decimal("0.00")
    reservations = []
    for item in cart_items:
        variant = ProductVariant.objects.select_for_update().select_related(
            "product"
        ).get(pk=item.variant_id)
        if variant.product.component_standard == HERITAGE_COURT_V1:
            try:
                validate_heritage_court_bom(variant)
            except ValidationError as error:
                raise ReservationError(
                    "This product is not ready for purchase."
                ) from error
        availability = variant_availability(variant)
        active_reserved = InventoryReservation.objects.filter(
            variant=variant,
            preorder_batch=availability.preorder_batch,
            status=InventoryReservation.Status.ACTIVE,
            expires_at__gt=now,
        ).aggregate(total=Sum("quantity"))["total"] or 0
        available = availability.available_quantity - active_reserved
        if item.quantity > available:
            raise ReservationError(
                f"Only {max(available, 0)} of {variant.product.name} — "
                f"{variant.color}, Size {variant.size} is available."
            )
        unit_price = variant.current_price()
        line_total = unit_price * item.quantity
        subtotal += line_total
        preorder_batch = availability.preorder_batch
        quote_line = CheckoutQuoteLine.objects.create(
            attempt=attempt,
            variant=variant,
            preorder_batch=preorder_batch,
            fulfillment_type=availability.fulfillment_type,
            sku=variant.sku,
            product_name=variant.product.name,
            size=variant.size,
            color=variant.color,
            preorder_batch_code=preorder_batch.code if preorder_batch else "",
            estimated_tender_start=(
                preorder_batch.estimated_tender_start if preorder_batch else None
            ),
            estimated_tender_end=(
                preorder_batch.estimated_tender_end if preorder_batch else None
            ),
            unit_price=unit_price,
            quantity=item.quantity,
            line_total=line_total,
        )
        components = variant.components.select_related(
            "part_type", "part_variant__part"
        )
        CheckoutQuoteComponent.objects.bulk_create([
            CheckoutQuoteComponent(
                quote_line=quote_line,
                part_type_code=component.part_type.code,
                part_id_snapshot=component.part_variant.part_id,
                part_code=component.part_variant.part.code,
                part_variant_id_snapshot=component.part_variant_id,
                part_variant_sku=component.part_variant.sku,
                quantity=component.quantity,
            )
            for component in components
        ])
        reservations.append(
            InventoryReservation(
                attempt=attempt,
                variant=variant,
                preorder_batch=availability.preorder_batch,
                quantity=item.quantity,
                expires_at=expires_at,
            )
        )
    InventoryReservation.objects.bulk_create(reservations)
    attempt.subtotal = subtotal
    attempt.grand_total = subtotal
    attempt.save(update_fields=["subtotal", "grand_total", "updated_at"])
    return attempt


@transaction.atomic
def release_expired_reservations(now=None):
    now = now or timezone.now()
    reservations = list(
        InventoryReservation.objects.select_for_update().filter(
            status=InventoryReservation.Status.ACTIVE,
            expires_at__lte=now,
        )
    )
    if not reservations:
        return 0
    released_at = timezone.now()
    InventoryReservation.objects.filter(
        pk__in=[reservation.pk for reservation in reservations]
    ).update(
        status=InventoryReservation.Status.RELEASED,
        released_at=released_at,
        updated_at=released_at,
    )
    attempt_ids = {reservation.attempt_id for reservation in reservations}
    CheckoutAttempt.objects.filter(
        pk__in=attempt_ids,
        status__in=[
            CheckoutAttempt.Status.CREATED,
            CheckoutAttempt.Status.STRIPE_CREATED,
        ],
    ).update(status=CheckoutAttempt.Status.EXPIRED, updated_at=released_at)
    return len(reservations)


@transaction.atomic
def release_attempt_reservations(attempt, *, status=CheckoutAttempt.Status.FAILED):
    locked_attempt = CheckoutAttempt.objects.select_for_update().get(pk=attempt.pk)
    now = timezone.now()
    InventoryReservation.objects.filter(
        attempt=locked_attempt,
        status=InventoryReservation.Status.ACTIVE,
    ).update(
        status=InventoryReservation.Status.RELEASED,
        released_at=now,
        updated_at=now,
    )
    locked_attempt.status = status
    locked_attempt.save(update_fields=["status", "updated_at"])
    return locked_attempt


@transaction.atomic
def commit_attempt_reservations(attempt, *, review_required=False):
    locked_attempt = CheckoutAttempt.objects.select_for_update().get(pk=attempt.pk)
    reservation_status = (
        InventoryReservation.Status.REVIEW_REQUIRED
        if review_required
        else InventoryReservation.Status.COMMITTED
    )
    now = timezone.now()
    InventoryReservation.objects.filter(
        attempt=locked_attempt,
        status=InventoryReservation.Status.ACTIVE,
    ).update(
        status=reservation_status,
        committed_at=None if review_required else now,
        updated_at=now,
    )
    locked_attempt.status = (
        CheckoutAttempt.Status.REVIEW_REQUIRED
        if review_required
        else CheckoutAttempt.Status.PAID
    )
    locked_attempt.save(update_fields=["status", "updated_at"])
    return locked_attempt


def snapshot_order_item_components(order_item):
    """Copy the finished SKU BOM so later catalog edits cannot rewrite history."""
    if order_item.variant_id is None:
        return 0

    components = order_item.variant.components.select_related(
        "part_type",
        "part_variant__part",
    ).all()
    snapshots = [
        OrderItemComponentSnapshot(
            order_item=order_item,
            part_type_code=component.part_type.code,
            part_id_snapshot=component.part_variant.part_id,
            part_code=component.part_variant.part.code,
            part_variant_id_snapshot=component.part_variant_id,
            part_variant_sku=component.part_variant.sku,
            quantity=component.quantity,
        )
        for component in components
    ]
    OrderItemComponentSnapshot.objects.bulk_create(snapshots)
    return len(snapshots)


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
def reconcile_paid_order_cart(order):
    locked_order = Order.objects.select_for_update().get(pk=order.pk)

    if locked_order.cart_reconciled_at is not None:
        return False

    if locked_order.source_cart_id is not None:
        purchased_items = (
            locked_order.items
            .exclude(variant_id__isnull=True)
            .values("variant_id", "preorder_batch_id")
            .annotate(purchased_quantity=Sum("quantity"))
            .order_by("variant_id")
        )

        for purchased_item in purchased_items:
            cart_item = (
                CartItem.objects.select_for_update()
                .filter(
                    cart_id=locked_order.source_cart_id,
                    variant_id=purchased_item["variant_id"],
                    preorder_batch_id=purchased_item["preorder_batch_id"],
                    added_at__lte=locked_order.created_at,
                )
                .first()
            )

            if cart_item is None:
                continue

            purchased_quantity = purchased_item["purchased_quantity"]
            if cart_item.quantity > purchased_quantity:
                cart_item.quantity -= purchased_quantity
                cart_item.save(update_fields=["quantity"])
            else:
                cart_item.delete()

    locked_order.cart_reconciled_at = timezone.now()
    locked_order.save(update_fields=["cart_reconciled_at", "updated_at"])
    order.cart_reconciled_at = locked_order.cart_reconciled_at
    return True


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

    preorder_batch = None
    preorder_allocations = {}
    batch_available_before = None
    batch_available_after = None

    if order.fulfillment_type == Order.FulfillmentType.PREORDER:
        preorder_batch = (
            PreorderBatch.objects.select_for_update()
            .get(pk=order.preorder_batch_id)
        )
        preorder_allocations = {
            item.variant_id: item
            for item in (
                PreorderVariantAllocation.objects.select_for_update()
                .filter(
                    batch=preorder_batch,
                    variant_id__in=variant_ids,
                )
                .order_by("variant_id")
            )
        }
        total_required = sum(
            requirement["required_quantity"]
            for requirement in requirements
        )
        batch_available_before = preorder_batch.remaining_quantity
        has_shortfall = (
            preorder_batch.status != PreorderBatch.Status.OPEN
            or batch_available_before < total_required
            or any(
                requirement["variant_id"] not in preorder_allocations
                or preorder_allocations[
                    requirement["variant_id"]
                ].remaining_quantity < requirement["required_quantity"]
                for requirement in requirements
            )
        )
        batch_available_after = (
            batch_available_before
            if has_shortfall
            else batch_available_before - total_required
        )
    else:
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
        if preorder_batch is not None:
            preorder_allocation = preorder_allocations.get(variant.id)
            variant_available_before = (
                preorder_allocation.remaining_quantity
                if preorder_allocation is not None
                else 0
            )
        else:
            preorder_allocation = None
            variant_available_before = variant.stock_quantity
        allocated_quantity = 0 if has_shortfall else required_quantity
        variant_available_after = (
            variant_available_before - allocated_quantity
        )

        allocation_items.append(
            InventoryAllocationItem(
                allocation=allocation,
                variant=variant,
                fulfillment_type=order.fulfillment_type,
                preorder_batch=preorder_batch,
                sku=requirement["sku"] or variant.sku,
                required_quantity=required_quantity,
                allocated_quantity=allocated_quantity,
                variant_available_before=variant_available_before,
                variant_available_after=variant_available_after,
                batch_available_before=batch_available_before,
                batch_available_after=batch_available_after,
            )
        )

        if not has_shortfall and preorder_batch is not None:
            preorder_allocation.committed_quantity += required_quantity
            preorder_allocation.save(
                update_fields=["committed_quantity", "updated_at"]
            )
        elif not has_shortfall:
            variant.stock_quantity = variant_available_after
            variant.save(update_fields=["stock_quantity"])

    if not has_shortfall and preorder_batch is not None:
        preorder_batch.committed_quantity += sum(
            requirement["required_quantity"]
            for requirement in requirements
        )
        preorder_batch.save(
            update_fields=["committed_quantity", "updated_at"]
        )

    InventoryAllocationItem.objects.bulk_create(allocation_items)
    return allocation


def retrieve_checkout_session(session_id):
    """Retrieve provider state with an instance-scoped Stripe client."""
    client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)
    return client.v1.checkout.sessions.retrieve(session_id)


def _as_plain_stripe_object(value):
    if hasattr(value, "to_dict_recursive"):
        return value.to_dict_recursive()
    return value


def _expected_stripe_livemode():
    key = settings.STRIPE_SECRET_KEY
    return key.startswith(("sk_live_", "rk_live_"))


def _session_shipping(session):
    collected = session.get("collected_information") or {}
    return collected.get("shipping_details") or session.get("shipping_details") or {}


def _validated_shipping_snapshot(session, attempt):
    shipping = _session_shipping(session)
    address = shipping.get("address") or {}
    state = (address.get("state") or "").strip().upper()
    country = (address.get("country") or "").strip().upper()
    required = ("line1", "city", "state", "postal_code", "country")
    if not all(address.get(field) for field in required):
        return None, "shipping_address_missing"
    customer_details = session.get("customer_details") or {}
    values = {
        "full_name": (shipping.get("name") or "").strip(),
        "email": (customer_details.get("email") or attempt.email).strip().lower(),
        "address_line_1": str(address["line1"]).strip(),
        "address_line_2": str(address.get("line2") or "").strip(),
        "city": str(address["city"]).strip(),
        "state": state,
        "postal_code": str(address["postal_code"]).strip(),
        "country": "United States",
    }
    limits = {
        "full_name": 100,
        "email": 254,
        "address_line_1": 255,
        "address_line_2": 255,
        "city": 100,
        "state": 100,
        "postal_code": 20,
        "country": 100,
    }
    if not values["full_name"] or not values["email"]:
        return None, "shipping_contact_missing"
    if any(len(values[field]) > limit for field, limit in limits.items()):
        return None, "shipping_address_too_long"
    if country != "US":
        return None, "shipping_country_ineligible"
    if state not in ELIGIBLE_SHIPPING_STATES:
        return values, "shipping_state_ineligible"
    if state != attempt.eligibility_state:
        return values, "shipping_state_mismatch"
    return values, ""


def _create_order_from_attempt(
    attempt,
    *,
    session,
    payment_intent_id,
    status,
    shipping_values=None,
    status_note,
):
    quote_lines = list(
        attempt.quote_lines.select_related(
            "variant__product", "preorder_batch"
        ).prefetch_related("component_snapshots")
    )
    if not quote_lines:
        raise ReservationError("Checkout attempt has no quote lines.")

    first_line = quote_lines[0]
    preorder_batch = (
        first_line.preorder_batch
        if first_line.fulfillment_type == Order.FulfillmentType.PREORDER
        else None
    )
    address = None
    if shipping_values is not None:
        address = ShippingAddress.objects.create(
            user=attempt.user,
            **shipping_values,
        )
    order = Order.objects.create(
        user=attempt.user,
        source_cart=attempt.cart,
        checkout_attempt=attempt,
        shipping_address=address,
        full_name=(shipping_values or {}).get("full_name", ""),
        email=(shipping_values or {}).get("email", attempt.email),
        currency=attempt.currency.lower(),
        shipping_full_name=(shipping_values or {}).get("full_name", ""),
        shipping_email=(shipping_values or {}).get("email", attempt.email),
        shipping_address_line_1=(shipping_values or {}).get(
            "address_line_1", ""
        ),
        shipping_address_line_2=(shipping_values or {}).get(
            "address_line_2", ""
        ),
        shipping_city=(shipping_values or {}).get("city", ""),
        shipping_state=(shipping_values or {}).get("state", ""),
        shipping_postal_code=(shipping_values or {}).get("postal_code", ""),
        shipping_country=(shipping_values or {}).get("country", ""),
        status=status,
        fulfillment_type=first_line.fulfillment_type,
        preorder_batch=preorder_batch,
        estimated_tender_start=first_line.estimated_tender_start,
        estimated_tender_end=first_line.estimated_tender_end,
        subtotal=attempt.subtotal,
        shipping_total=attempt.shipping_total,
        tax_total=attempt.tax_total,
        discount_total=attempt.discount_total,
        grand_total=attempt.grand_total,
        stripe_checkout_session_id=session.get("id") or "",
        stripe_payment_intent_id=payment_intent_id,
    )
    record_initial_status(
        order,
        source=OrderStatusEvent.Source.STRIPE,
        reason=(
            "checkout_payment_reconciled"
            if status == Order.Status.PAID
            else "checkout_payment_review_required"
        ),
        external_reference=session.get("id") or "",
        internal_detail=status_note,
        customer_message=(
            "Payment confirmed."
            if status == Order.Status.PAID
            else "Your payment requires review before fulfillment."
        ),
    )
    for quote_line in quote_lines:
        order_item = OrderItem.objects.create(
            order=order,
            product=quote_line.variant.product,
            variant=quote_line.variant,
            fulfillment_type=quote_line.fulfillment_type,
            preorder_batch=quote_line.preorder_batch,
            preorder_batch_code=quote_line.preorder_batch_code,
            estimated_tender_start=quote_line.estimated_tender_start,
            estimated_tender_end=quote_line.estimated_tender_end,
            product_name=quote_line.product_name,
            sku=quote_line.sku,
            size=quote_line.size,
            color=quote_line.color,
            unit_price=quote_line.unit_price,
            quantity=quote_line.quantity,
            line_total=quote_line.line_total,
        )
        OrderItemComponentSnapshot.objects.bulk_create([
            OrderItemComponentSnapshot(
                order_item=order_item,
                part_type_code=component.part_type_code,
                part_id_snapshot=component.part_id_snapshot,
                part_code=component.part_code,
                part_variant_id_snapshot=component.part_variant_id_snapshot,
                part_variant_sku=component.part_variant_sku,
                quantity=component.quantity,
            )
            for component in quote_line.component_snapshots.all()
        ])
    Payment.objects.create(
        order=order,
        stripe_payment_intent_id=payment_intent_id or None,
        stripe_checkout_session_id=session.get("id") or None,
        amount=Decimal(session.get("amount_total") or 0) / Decimal("100"),
        currency=(session.get("currency") or attempt.currency).lower(),
        status=Payment.Status.SUCCEEDED,
        raw_response={},
    )
    return order


def _reconciliation_mismatch(
    attempt,
    session,
    payment_intent_id,
    reason,
    *,
    shipping_values=None,
):
    existing_order = Order.objects.filter(checkout_attempt=attempt).first()
    if existing_order is None:
        order = _create_order_from_attempt(
            attempt,
            session=session,
            payment_intent_id=payment_intent_id,
            status=Order.Status.REVIEW_REQUIRED,
            shipping_values=shipping_values,
            status_note=f"Stripe payment requires staff review ({reason}).",
        )
    else:
        order = existing_order
        if order.status == Order.Status.PAID:
            order, _ = transition_order(
                order,
                Order.Status.REVIEW_REQUIRED,
                source=OrderStatusEvent.Source.STRIPE,
                reason="stripe_reconciliation_mismatch",
                external_reference=session.get("id") or "",
                internal_detail=(
                    f"Stripe reconciliation requires staff review ({reason})."
                ),
                customer_message=(
                    "Your payment requires review before fulfillment."
                ),
            )
    release_attempt_reservations(
        attempt,
        status=CheckoutAttempt.Status.REVIEW_REQUIRED,
    )
    CheckoutAttempt.objects.filter(pk=attempt.pk).update(
        stripe_payment_intent_id=payment_intent_id,
        review_reason=reason,
        reconciled_at=timezone.now(),
    )
    attempt.refresh_from_db()
    logger.error(
        "Checkout payment requires review for attempt %s (%s).",
        attempt.id,
        reason,
    )
    return CheckoutReconciliationResult(
        state="review_required", attempt=attempt, order=order, reason=reason
    )


def reconcile_checkout_session(session_id):
    """Retrieve and idempotently reconcile one hosted Checkout Session."""
    session = _as_plain_stripe_object(retrieve_checkout_session(session_id))
    return reconcile_retrieved_checkout_session(session)


@transaction.atomic
def reconcile_retrieved_checkout_session(session):
    """Create a paid/review order only from verified provider state."""
    session = _as_plain_stripe_object(session)
    metadata = session.get("metadata") or {}
    attempt_id = metadata.get("checkout_attempt_id") or session.get(
        "client_reference_id"
    )
    if not attempt_id:
        return CheckoutReconciliationResult(state="legacy", reason="missing_attempt")
    try:
        attempt = CheckoutAttempt.objects.select_for_update().get(pk=attempt_id)
    except (CheckoutAttempt.DoesNotExist, ValueError):
        logger.error("Stripe Checkout Session references an unknown attempt.")
        return CheckoutReconciliationResult(state="unmatched", reason="unknown_attempt")

    payment_status = (session.get("payment_status") or "").lower()
    payment_intent_id = _stripe_object_id(session.get("payment_intent"))
    expected_cents = int(attempt.grand_total * Decimal("100"))
    existing_order = Order.objects.select_for_update().filter(
        checkout_attempt=attempt
    ).first()
    if existing_order is not None:
        if existing_order.status == Order.Status.REVIEW_REQUIRED:
            return CheckoutReconciliationResult(
                state="review_required",
                attempt=attempt,
                order=existing_order,
                reason=attempt.review_reason,
            )
        payment = Payment.objects.filter(order=existing_order).first()
        replay_checks = (
            (payment_status == "paid", "payment_state_regressed"),
            (
                session.get("id") == attempt.stripe_checkout_session_id,
                "checkout_session_mismatch",
            ),
            (
                session.get("client_reference_id") == str(attempt.id),
                "attempt_ownership_mismatch",
            ),
            (session.get("amount_total") == expected_cents, "amount_mismatch"),
            (
                (session.get("currency") or "").lower() == attempt.currency.lower(),
                "currency_mismatch",
            ),
            (
                payment is not None
                and payment_intent_id == (payment.stripe_payment_intent_id or ""),
                "payment_intent_mismatch",
            ),
            (session.get("mode") == "payment", "checkout_mode_mismatch"),
            (
                session.get("livemode") is _expected_stripe_livemode(),
                "stripe_environment_mismatch",
            ),
            (
                metadata.get("expected_amount") == str(expected_cents),
                "expected_amount_metadata_mismatch",
            ),
            (
                (metadata.get("currency") or "").lower()
                == attempt.currency.lower(),
                "currency_metadata_mismatch",
            ),
        )
        for valid, reason in replay_checks:
            if not valid:
                return _reconciliation_mismatch(
                    attempt, session, payment_intent_id, reason
                )
        return CheckoutReconciliationResult(
            state="paid", attempt=attempt, order=existing_order
        )

    if payment_status != "paid":
        return CheckoutReconciliationResult(state="pending", attempt=attempt)
    shipping_values, shipping_error = _validated_shipping_snapshot(session, attempt)
    checks = (
        (
            session.get("id") == attempt.stripe_checkout_session_id,
            "checkout_session_mismatch",
        ),
        (session.get("client_reference_id") == str(attempt.id), "attempt_ownership_mismatch"),
        (session.get("amount_total") == expected_cents, "amount_mismatch"),
        (
            (session.get("currency") or "").lower() == attempt.currency.lower(),
            "currency_mismatch",
        ),
        (bool(payment_intent_id), "payment_intent_missing"),
        (session.get("mode") == "payment", "checkout_mode_mismatch"),
        (
            session.get("livemode") is _expected_stripe_livemode(),
            "stripe_environment_mismatch",
        ),
        (
            metadata.get("expected_amount") == str(expected_cents),
            "expected_amount_metadata_mismatch",
        ),
        (
            (metadata.get("currency") or "").lower() == attempt.currency.lower(),
            "currency_metadata_mismatch",
        ),
        (attempt.expires_at > timezone.now(), "payment_after_reservation_expiry"),
        (
            attempt.status in {
                CheckoutAttempt.Status.CREATED,
                CheckoutAttempt.Status.STRIPE_CREATED,
            },
            "attempt_not_reconcilable",
        ),
    )
    for valid, reason in checks:
        if not valid:
            return _reconciliation_mismatch(
                attempt,
                session,
                payment_intent_id,
                reason,
                shipping_values=shipping_values,
            )

    if shipping_error:
        return _reconciliation_mismatch(
            attempt,
            session,
            payment_intent_id,
            shipping_error,
            shipping_values=shipping_values,
        )

    order = _create_order_from_attempt(
        attempt,
        session=session,
        payment_intent_id=payment_intent_id,
        status=Order.Status.PAID,
        shipping_values=shipping_values,
        status_note="Stripe Checkout Session reconciled as paid.",
    )
    allocation = allocate_inventory_for_paid_order(order)
    if allocation.status != InventoryAllocation.Status.ALLOCATED:
        order, _ = transition_order(
            order,
            Order.Status.REVIEW_REQUIRED,
            source=OrderStatusEvent.Source.SYSTEM,
            reason="inventory_commit_failed",
            external_reference=str(attempt.id),
            internal_detail=(
                "Paid order requires staff review because inventory could not "
                "be committed."
            ),
            customer_message=(
                "Your payment requires review before fulfillment."
            ),
        )
        commit_attempt_reservations(attempt, review_required=True)
        CheckoutAttempt.objects.filter(pk=attempt.pk).update(
            review_reason="inventory_commit_failed",
            stripe_payment_intent_id=payment_intent_id,
            reconciled_at=timezone.now(),
        )
        attempt.refresh_from_db()
        return CheckoutReconciliationResult(
            state="review_required",
            attempt=attempt,
            order=order,
            reason="inventory_commit_failed",
        )

    commit_attempt_reservations(attempt)
    CheckoutAttempt.objects.filter(pk=attempt.pk).update(
        stripe_payment_intent_id=payment_intent_id,
        review_reason="",
        reconciled_at=timezone.now(),
    )
    reconcile_paid_order_cart(order)
    attempt.refresh_from_db()
    return CheckoutReconciliationResult(state="paid", attempt=attempt, order=order)


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
        # Keep provider identifiers and bounded status fields only; do not
        # persist the complete Stripe refund payload.
        "raw_response": {},
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
    elif (
        event_type != "refund.created"
        and refund.status
        not in {Refund.Status.SUCCEEDED, Refund.Status.FAILED, Refund.Status.CANCELED}
    ):
        for field, value in refund_defaults.items():
            setattr(refund, field, value)
        refund.save(update_fields=[*refund_defaults, "updated_at"])
    allocation = (
        InventoryAllocation.objects.select_for_update()
        .filter(order=payment.order)
        .first()
    )

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
        if (
            allocation is not None
            and allocation.status != InventoryAllocation.Status.ALLOCATED
        ):
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
        transition_order(
            payment.order,
            Order.Status.REFUNDED,
            source=OrderStatusEvent.Source.REFUND,
            reason="full_refund_confirmed",
            external_reference=refund.stripe_refund_id,
            internal_detail="Cumulative confirmed Stripe refunds cover the payment.",
            customer_message="Your payment was fully refunded.",
        )
        return refund

    if (
        allocation is not None
        and allocation.status != InventoryAllocation.Status.ALLOCATED
        and full_refund_initiated
        and not incoming_refund_failed
    ):
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

        return refund

    if allocation is None or allocation.status == InventoryAllocation.Status.ALLOCATED:
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

    return refund
