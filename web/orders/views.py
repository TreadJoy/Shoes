from datetime import datetime, timezone as datetime_timezone
from decimal import Decimal
import stripe
import json
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from web.cart.services import get_or_create_cart
from web.products.services import AvailabilityError

from .forms import CheckoutForm
from .models import (
    CheckoutAttempt,
    Order,
    OrderStatusEvent,
    Payment,
    StripeEvent
)
from .services import (
    UnmatchedRefundPaymentError,
    allocate_inventory_for_paid_order,
    commit_attempt_reservations,
    create_checkout_attempt,
    CheckoutReconciliationResult,
    reconcile_retrieved_checkout_session,
    reconcile_paid_order_cart,
    release_attempt_reservations,
    retrieve_checkout_session,
    synchronize_refund,
)
from .transitions import transition_order

logger = logging.getLogger(__name__)


def create_stripe_checkout_session(*, idempotency_key, **params):
    """Create hosted Checkout through an instance-scoped Stripe client."""
    client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)
    return client.v1.checkout.sessions.create(
        params,
        options={"idempotency_key": idempotency_key},
    )


def retrieve_stripe_checkout_session(session_id):
    """Retrieve authoritative Checkout state from Stripe for reconciliation."""
    return retrieve_checkout_session(session_id)

@transaction.atomic
def mark_order_as_paid(
    order,
    *,
    amount_total_cents,
    amount_subtotal_cents=None,
    payment_intent_id="",
    checkout_session_id="",
    currency="usd",
    raw_response=None,
    status_note="Payment succeeded.",
):
    order = Order.objects.select_for_update().get(pk=order.pk)
    logger.info("mark_order_as_paid called for order %s.", order.id)
    logger.info("order status before payment update: %s", order.status)

    payment_already_recorded = Payment.objects.filter(
        order=order,
        status=Payment.Status.SUCCEEDED,
    ).exists()

    if order.status == Order.Status.PAID or payment_already_recorded:
        reconcile_paid_order_cart(order)
        return False

    expected_total_cents = int(order.grand_total * Decimal("100"))
    expected_subtotal_cents = int(order.subtotal * Decimal("100"))
    if (
        amount_total_cents != expected_total_cents
        or (
            amount_subtotal_cents is not None
            and amount_subtotal_cents != expected_subtotal_cents
        )
        or currency.lower() != "usd"
    ):
        raise ValueError("Legacy payment does not match the order quote.")

    if checkout_session_id:
        order.stripe_checkout_session_id = checkout_session_id

    if payment_intent_id:
        order.stripe_payment_intent_id = payment_intent_id
    order.save(
        update_fields=[
            "stripe_checkout_session_id",
            "stripe_payment_intent_id",
            "updated_at",
        ]
    )
    order, _ = transition_order(
        order,
        Order.Status.PAID,
        source=OrderStatusEvent.Source.STRIPE,
        reason="legacy_payment_reconciled",
        external_reference=checkout_session_id or payment_intent_id,
        internal_detail=status_note,
        customer_message="Payment confirmed.",
    )

    Payment.objects.update_or_create(
        order=order,
        defaults={
            "stripe_payment_intent_id": payment_intent_id or None,
            "stripe_checkout_session_id": checkout_session_id or order.stripe_checkout_session_id or None,
            "amount": order.grand_total,
            "currency": currency,
            "status": Payment.Status.SUCCEEDED,
            # Provider payloads are intentionally not persisted. Reconciliation
            # fields above are the durable audit record.
            "raw_response": {},
        },
    )

    allocation = allocate_inventory_for_paid_order(order)
    if order.checkout_attempt_id:
        commit_attempt_reservations(
            order.checkout_attempt,
            review_required=(
                allocation.status != allocation.Status.ALLOCATED
            ),
        )
    reconcile_paid_order_cart(order)

    return True

def checkout(request):
    cart = get_or_create_cart(request)

    if cart.items.count() == 0:
        return redirect("cart:cart_detail")

    form = CheckoutForm(request.POST or None)

    if request.method == "POST":
        if not form.is_valid():
            return render(request, "orders/checkout.html", {
                "cart": cart,
                "form": form,
            })

        try:
            checkout_attempt = create_checkout_attempt(
                cart,
                user=request.user,
                email=form.cleaned_data["email"],
                eligibility_state=form.cleaned_data["state"],
            )
        except (AvailabilityError, ValueError) as error:
            messages.error(request, str(error))
            return redirect("cart:cart_detail")

        success_url = request.build_absolute_uri(
            reverse("orders:checkout_success", args=[checkout_attempt.id])
        )

        cancel_url = request.build_absolute_uri(
            reverse("cart:cart_detail")
        )

        attempt_ids = request.session.get("checkout_attempt_ids", [])
        attempt_id = str(checkout_attempt.id)
        if attempt_id not in attempt_ids:
            attempt_ids.append(attempt_id)
        request.session["checkout_attempt_ids"] = attempt_ids[-20:]
        request.session.modified = True

        try:
            checkout_session = create_stripe_checkout_session(
                mode="payment",
                line_items=build_stripe_line_items(checkout_attempt),
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=checkout_attempt.email,
                client_reference_id=str(checkout_attempt.id),
                expires_at=int(checkout_attempt.expires_at.timestamp()),
                shipping_address_collection={"allowed_countries": ["US"]},
                metadata={
                    "checkout_attempt_id": str(checkout_attempt.id),
                    "expected_amount": str(
                        int(checkout_attempt.grand_total * Decimal("100"))
                    ),
                    "currency": checkout_attempt.currency,
                },
                payment_intent_data={
                    "metadata": {
                        "checkout_attempt_id": str(checkout_attempt.id),
                        "expected_amount": str(
                            int(checkout_attempt.grand_total * Decimal("100"))
                        ),
                        "currency": checkout_attempt.currency,
                    }
                },
                integration_identifier="treadjoy_checkout_xqnvkzpr",
                automatic_tax={
                    "enabled": False,
                },
                idempotency_key=checkout_attempt.idempotency_key,
            )
        except stripe.error.StripeError as error:
            # Network/time-out failures are ambiguous: keep the reservation and
            # idempotency key so the same attempt can be retried safely. Release
            # only when Stripe definitively rejected session creation.
            ambiguous_errors = (
                stripe.error.APIConnectionError,
                stripe.error.APIError,
                stripe.error.RateLimitError,
            )
            if not isinstance(error, ambiguous_errors):
                release_attempt_reservations(checkout_attempt)
            messages.error(
                request,
                "Payment checkout failed. Please try again.",
            )
            return redirect("cart:cart_detail")

        with transaction.atomic():
            checkout_attempt = CheckoutAttempt.objects.select_for_update().get(
                pk=checkout_attempt.pk
            )
            if (
                checkout_attempt.stripe_checkout_session_id
                and checkout_attempt.stripe_checkout_session_id != checkout_session.id
            ):
                release_attempt_reservations(
                    checkout_attempt,
                    status=CheckoutAttempt.Status.REVIEW_REQUIRED,
                )
                messages.error(request, "Payment checkout requires staff review.")
                return redirect("cart:cart_detail")
            checkout_attempt.status = CheckoutAttempt.Status.STRIPE_CREATED
            checkout_attempt.stripe_checkout_session_id = checkout_session.id
            checkout_attempt.save(
                update_fields=["status", "stripe_checkout_session_id", "updated_at"]
            )

        return redirect(checkout_session.url)

    return render(request, "orders/checkout.html", {
        "cart": cart,
        "form": form,
    })


def checkout_success(request, attempt_id):
    attempt = get_object_or_404(CheckoutAttempt, pk=attempt_id)
    session_attempt_ids = request.session.get("checkout_attempt_ids", [])
    user_owns_attempt = (
        request.user.is_authenticated and attempt.user_id == request.user.id
    )
    guest_owns_attempt = (
        attempt.user_id is None and str(attempt.id) in session_attempt_ids
    )
    if not user_owns_attempt and not guest_owns_attempt:
        raise PermissionDenied

    result = None
    if request.GET.get("check") == "1" and attempt.stripe_checkout_session_id:
        try:
            result = handle_checkout_session_completed(
                {"id": attempt.stripe_checkout_session_id}
            )
        except stripe.error.StripeError:
            logger.info(
                "Stripe status check unavailable for checkout attempt %s.",
                attempt.id,
            )
    attempt.refresh_from_db()
    order = (
        Order.objects.select_related("payment")
        .prefetch_related("items__variant")
        .filter(checkout_attempt=attempt)
        .first()
    )
    payment = getattr(order, "payment", None) if order else None
    return render(
        request,
        "orders/order_success.html",
        {
            "attempt": attempt,
            "order": order,
            "is_paid": bool(order and order.status == Order.Status.PAID),
            "is_refunded": bool(order and order.status == Order.Status.REFUNDED),
            "is_review_required": bool(
                order and order.status == Order.Status.REVIEW_REQUIRED
            ),
            "payment": payment,
            "reconciliation_result": result,
        },
    )
def order_success(request, order_id):
    order = get_object_or_404(
        Order.objects
        .select_related("payment")
        .prefetch_related("items__variant"),
        id=order_id,
    )

    checkout_order_ids = request.session.get("checkout_order_ids", [])

    user_owns_order = (
        request.user.is_authenticated and
        order.user_id == request.user.id
    )

    guest_session_owns_order = (
        order.user_id is None and
        order.id in checkout_order_ids
    )

    if not user_owns_order and not guest_session_owns_order:
        raise PermissionDenied

    if (
        request.GET.get("check") == "1"
        and order.stripe_checkout_session_id
        and order.status == Order.Status.PENDING_PAYMENT
    ):
        try:
            handle_checkout_session_completed(
                {"id": order.stripe_checkout_session_id}
            )
        except stripe.error.StripeError:
            logger.info("Stripe status check unavailable for order %s.", order.id)
        order.refresh_from_db()

    payment = getattr(order, "payment", None)
    is_paid = (
        payment is not None
        and payment.status == Payment.Status.SUCCEEDED
    )
    is_refunded = order.status == Order.Status.REFUNDED

    return render(
        request,
        "orders/order_success.html",
        {
            "order": order,
            "is_paid": is_paid,
            "is_refunded": is_refunded,
            "payment": payment,
        },
    )


@login_required
def order_list(request):
    orders = request.user.orders.prefetch_related("items").order_by("-created_at")

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders,
        },
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
            "shipments",
            "status_events",
        ),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
        },
    )


def build_stripe_line_items(attempt):
    line_items = []

    for item in attempt.quote_lines.all():
        product_data = {
            "name": item.product_name,
            "metadata": {
                "sku": item.sku,
                "size": item.size,
                "color": item.color,
                "fulfillment_type": item.fulfillment_type,
            },
        }
        if item.fulfillment_type == Order.FulfillmentType.PREORDER:
            product_data["description"] = (
                "Preorder — estimated to ship "
                f"{item.estimated_tender_start:%b %d}–"
                f"{item.estimated_tender_end:%b %d, %Y}. "
                "Delivery time begins after the package is handed to the carrier."
            )
            product_data["metadata"]["preorder_batch"] = (
                item.preorder_batch_code
            )

        line_items.append({
            "price_data": {
                "currency": attempt.currency,
                "product_data": product_data,
                "unit_amount": int(item.unit_price * 100),
            },
            "quantity": item.quantity,
        })
    return line_items

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    logger.info("Stripe webhook received.")
    logger.debug("Stripe signature present: %s", bool(sig_header))
    logger.debug("Stripe webhook secret configured: %s", bool(endpoint_secret))

    try:
        stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret,
        )
    except ValueError as error:
        logger.warning("Invalid Stripe webhook payload: %s", error)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as error:
        logger.warning("Invalid Stripe webhook signature: %s", error)
        return HttpResponse(status=400)

    event_data = json.loads(payload.decode("utf-8"))

    stripe_event_id = event_data["id"]
    event_type = event_data["type"]

    logger.info(
        "Stripe webhook event received: %s %s",
        event_type,
        stripe_event_id,
    )

    with transaction.atomic():
        event_object = event_data.get("data", {}).get("object") or {}
        event_created = event_data.get("created")
        provider_created_at = (
            datetime.fromtimestamp(event_created, tz=datetime_timezone.utc)
            if event_created
            else None
        )
        amount_cents = (
            event_object.get("amount_total")
            or event_object.get("amount_received")
            or event_object.get("amount")
        )
        stripe_event, created = StripeEvent.objects.get_or_create(
            stripe_event_id=stripe_event_id,
            defaults={
                "event_type": event_type,
                "provider_created_at": provider_created_at,
                "api_version": event_data.get("api_version") or "",
                "amount": (
                    Decimal(amount_cents) / Decimal("100")
                    if amount_cents is not None
                    else None
                ),
                "currency": event_object.get("currency") or "",
            },
        )

        if not created and stripe_event.processed:
            logger.info(
                "Stripe webhook event already processed: %s",
                stripe_event_id,
            )
            return HttpResponse(status=200)

        if event_type == "checkout.session.completed":
            session = event_data["data"]["object"]
            reconciliation = handle_checkout_session_completed(session)
            stripe_event.error_code = reconciliation.reason if reconciliation else ""

        elif event_type == "checkout.session.async_payment_succeeded":
            session = event_data["data"]["object"]
            reconciliation = handle_checkout_session_completed(session)
            stripe_event.error_code = reconciliation.reason if reconciliation else ""

        elif event_type in {
            "checkout.session.expired",
            "checkout.session.async_payment_failed",
        }:
            handle_checkout_session_expired(event_data["data"]["object"])

        elif event_type in [
            "refund.created",
            "refund.updated",
            "refund.failed",
        ]:
            refund = event_data["data"]["object"]

            try:
                synchronize_refund(refund, event_type=event_type)
            except UnmatchedRefundPaymentError as error:
                logger.error("Unable to match Stripe refund: %s", error)
                stripe_event.processing_attempts += 1
                stripe_event.error_code = "unmatched_refund_payment"
                stripe_event.save(
                    update_fields=["processing_attempts", "error_code"]
                )
                return HttpResponse(status=500)

        stripe_event.processing_attempts += 1
        stripe_event.processed = True
        stripe_event.processed_at = timezone.now()
        stripe_event.save(
            update_fields=[
                "processing_attempts",
                "processed",
                "processed_at",
                "error_code",
            ]
        )

    return HttpResponse(status=200)

def get_order_id_from_metadata(stripe_object):
    metadata = stripe_object.get("metadata") or {}
    order_id = metadata.get("order_id")

    if not order_id:
        return None

    return int(order_id)


def handle_checkout_session_completed(session):
    session = retrieve_stripe_checkout_session(session.get("id", ""))
    session = session.to_dict_recursive() if hasattr(session, "to_dict_recursive") else session
    result = reconcile_retrieved_checkout_session(session)
    if result.state != "legacy":
        return result

    # Compatibility for historical pending orders created before CheckoutAttempt.
    order_id = get_order_id_from_metadata(session)
    order = Order.objects.filter(pk=order_id).first() if order_id else None
    payment_intent_id = session.get("payment_intent") or ""
    if isinstance(payment_intent_id, dict):
        payment_intent_id = payment_intent_id.get("id", "")
    expected_cents = int(order.grand_total * Decimal("100")) if order else None
    if (
        order is not None
        and order.status == Order.Status.PENDING_PAYMENT
        and session.get("payment_status") == "paid"
        and session.get("amount_total") == expected_cents
        and (session.get("currency") or "").lower() == "usd"
        and payment_intent_id
    ):
        mark_order_as_paid(
            order,
            amount_total_cents=expected_cents,
            amount_subtotal_cents=int(order.subtotal * Decimal("100")),
            payment_intent_id=payment_intent_id,
            checkout_session_id=session.get("id", "") or "",
            currency="usd",
            status_note="Legacy Stripe Checkout Session reconciled as paid.",
        )
        return CheckoutReconciliationResult(state="paid", order=order)
    return result


def handle_checkout_session_expired(session):
    session_id = session.get("id", "")
    attempt = (
        CheckoutAttempt.objects.select_for_update()
        .filter(stripe_checkout_session_id=session_id)
        .first()
    )
    if attempt is not None and not Order.objects.filter(
        checkout_attempt=attempt
    ).exists():
        release_attempt_reservations(
            attempt,
            status=CheckoutAttempt.Status.EXPIRED,
        )
