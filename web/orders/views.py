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

from web.cart.views import get_or_create_cart
from web.cart.models import CartItem

from .models import (
    Order,
    OrderItem,
    OrderStatusEvent,
    ShippingAddress,
    Payment,
    StripeEvent
)

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

def create_order_status_event(order, from_status, to_status, note=""):

    OrderStatusEvent.objects.create(
        order=order,
        from_status=from_status or "",
        to_status=to_status,
        note=note,
    )

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
    logger.info("mark_order_as_paid called for order %s.", order.id)
    logger.info("order status before payment update: %s", order.status)

    payment_already_recorded = Payment.objects.filter(
        order=order,
        status=Payment.Status.SUCCEEDED,
    ).exists()

    if order.status == Order.Status.PAID or payment_already_recorded:
        return False

    previous_status = order.status

    order.status = Order.Status.PAID
    order.grand_total = Decimal(amount_total_cents or 0) / Decimal("100")

    update_fields = [
        "status",
        "grand_total",
        "updated_at",
    ]

    if amount_subtotal_cents is not None:
        order.subtotal = Decimal(amount_subtotal_cents or 0) / Decimal("100")
        update_fields.append("subtotal")

    if checkout_session_id:
        order.stripe_checkout_session_id = checkout_session_id
        update_fields.append("stripe_checkout_session_id")

    if payment_intent_id:
        order.stripe_payment_intent_id = payment_intent_id
        update_fields.append("stripe_payment_intent_id")

    order.save(update_fields=update_fields)

    create_order_status_event(
        order=order,
        from_status=previous_status,
        to_status=Order.Status.PAID,
        note=status_note,
    )

    Payment.objects.update_or_create(
        order=order,
        defaults={
            "stripe_payment_intent_id": payment_intent_id or None,
            "stripe_checkout_session_id": checkout_session_id or order.stripe_checkout_session_id or None,
            "amount": order.grand_total,
            "currency": currency,
            "status": Payment.Status.SUCCEEDED,
            "raw_response": raw_response or {},
        },
    )

    reduce_inventory_for_order(order)

    return True

def checkout(request):
    cart = get_or_create_cart(request)

    if cart.items.count() == 0:
        return redirect("cart:cart_detail")

    if request.method == "POST":
        required_fields = [
            "full_name",
            "email",
            "address_line_1",
            "city",
            "state",
            "postal_code",
        ]

        missing_fields = [
            field for field in required_fields
            if not request.POST.get(field)
        ]

        if missing_fields:
            messages.error(
                request,
                "Please fill out all required shipping fields.",
            )
            return render(request, "orders/checkout.html", {
                "cart": cart,
            })

        try:
            with transaction.atomic():
                cart_items = list(
                    cart.items.select_related(
                        "variant",
                        "variant__product",
                    )
                )

                if not cart_items:
                    messages.error(request, "Your cart is empty.")
                    return redirect("cart:cart_detail")

                for cart_item in cart_items:
                    if cart_item.variant is None:
                        raise ValueError(
                            "This cart item does not have a valid size/color option."
                        )

                    variant = cart_item.variant

                    if not variant.is_active:
                        raise ValueError(
                            f"{variant.product.name} — {variant.color}, Size {variant.size} is no longer available."
                        )

                    if not variant.product.is_active:
                        raise ValueError(
                            f"{variant.product.name} is currently unavailable."
                        )

                    if cart_item.quantity > variant.stock_quantity:
                        raise ValueError(
                            f"Only {variant.stock_quantity} of "
                            f"{variant.product.name} — {variant.color}, Size {variant.size} available."
                        )

                order_line_total = sum(
                    cart_item.line_total()
                    for cart_item in cart_items
                )

                shipping_address = ShippingAddress.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    full_name=request.POST.get("full_name", "").strip(),
                    email=request.POST.get("email", "").strip(),
                    address_line_1=request.POST.get("address_line_1", "").strip(),
                    address_line_2=request.POST.get("address_line_2", "").strip(),
                    city=request.POST.get("city", "").strip(),
                    state=request.POST.get("state", "").strip(),
                    postal_code=request.POST.get("postal_code", "").strip(),
                )

                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    shipping_address=shipping_address,
                    email=shipping_address.email,
                    full_name=shipping_address.full_name,
                    status=Order.Status.PENDING_PAYMENT,
                    subtotal=order_line_total,
                    shipping_total=Decimal("0.00"),
                    tax_total=Decimal("0.00"),
                    discount_total=Decimal("0.00"),
                    grand_total=order_line_total,
                )
                create_order_status_event(
                    order=order,
                    from_status="",
                    to_status=Order.Status.PENDING_PAYMENT,
                    note="Order created at checkout."
                )

                checkout_order_ids = request.session.get("checkout_order_ids", [])

                if order.id not in checkout_order_ids:
                    checkout_order_ids.append(order.id)

                request.session["checkout_order_ids"] = checkout_order_ids
                request.session.modified = True

                for cart_item in cart_items:
                    unit_price = cart_item.unit_price()
                    line_total = cart_item.line_total()
                    variant = cart_item.variant

                    OrderItem.objects.create(
                        order=order,
                        product=variant.product,
                        variant=variant,
                        product_name=variant.product.name,
                        sku=variant.sku,
                        size=variant.size,
                        color=variant.color,
                        unit_price=unit_price,
                        quantity=cart_item.quantity,
                        line_total=line_total,
                    )

                # Do not reduce inventory here yet.
                # Do not clear the cart here yet.
                # Stripe webhook will handle that after payment succeeds.

        except ValueError as error:
            messages.error(request, str(error))
            return redirect("cart:cart_detail")

        success_url = request.build_absolute_uri(
            reverse("orders:order_success", args=[order.id,])
        )

        cancel_url = request.build_absolute_uri(
            reverse("cart:cart_detail")
        )

        try:
            checkout_session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=build_stripe_line_items(order),
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=order.email,
                metadata={
                    "order_id": str(order.id),
                },
                payment_intent_data={
                    "metadata": {
                        "order_id": str(order.id),
                    }
                },
                automatic_tax={
                    "enabled": False,
                },
                shipping_address_collection={
                    "allowed_countries": ["US"],
                }
            )
        except stripe.error.StripeError as error:

            messages.error(
                request,
                "Payment checkout failed. Please try again.",
            )
            return redirect("cart:cart_detail")

        order.stripe_checkout_session_id = checkout_session.id
        order.save(update_fields=["stripe_checkout_session_id"])

        request.session["completed_order_id"] = order.id

        return redirect(checkout_session.url)

    return render(request, "orders/checkout.html", {
        "cart": cart,
    })
def order_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__variant"),
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

    is_paid = order.status == Order.Status.PAID

    if is_paid:
        remove_paid_order_items_from_cart(request, order)

    return render(
        request,
        "orders/order_success.html",
        {
            "order": order,
            "is_paid": is_paid,
        },
    )

@login_required
def order_history(request):
    orders = request.user.orders.all().order_by("-created_at")

    return render(request, "orders/order_history.html", {
        "orders": orders,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    return render(request, "orders/order_detail.html", {
        "order": order,
    })

def build_stripe_line_items(order):
    line_items = []

    for item in order.items.select_related(
        "variant",
        "variant__product",
    ):
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item.product_name,
                    "metadata": {
                        "sku": item.sku,
                        "size": item.size,
                        "color": item.color,
                    },
                },
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
        event = stripe.Webhook.construct_event(
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
        stripe_event, created = StripeEvent.objects.get_or_create(
            stripe_event_id=stripe_event_id,
            defaults={
                "event_type": event_type,
                "raw_event": event_data,
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
            handle_checkout_session_completed(session)

        elif event_type == "payment_intent.succeeded":
            payment_intent = event_data["data"]["object"]
            handle_payment_intent_succeeded(payment_intent)

        elif event_type == "checkout.session.async_payment_succeeded":
            session = event_data["data"]["object"]
            handle_checkout_session_completed(session)

        stripe_event.processed = True
        stripe_event.processed_at = timezone.now()
        stripe_event.save(
            update_fields=[
                "processed",
                "processed_at",
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
    logger.info("handle_checkout_session_completed called.")
    logger.info("Checkout session metadata: %s", session.get("metadata"))

    order_id = get_order_id_from_metadata(session)

    if order_id is None:
        logger.warning("No order_id found on checkout session metadata.")
        return

    order = (
        Order.objects
        .select_for_update()
        .prefetch_related("items__variant")
        .get(id=order_id)
    )

    mark_order_as_paid(
        order,
        amount_total_cents=session.get("amount_total") or 0,
        amount_subtotal_cents=session.get("amount_subtotal"),
        payment_intent_id=session.get("payment_intent", "") or "",
        checkout_session_id=session.get("id", "") or "",
        currency=session.get("currency", "usd"),
        raw_response=session,
        status_note="Stripe checkout session completed.",
    )


def handle_payment_intent_succeeded(payment_intent):
    logger.info("handle_payment_intent_succeeded called.")
    logger.info("Payment intent metadata: %s", payment_intent.get("metadata"))

    order_id = get_order_id_from_metadata(payment_intent)

    if order_id is None:
        logger.warning("No order_id found on payment intent metadata.")
        return

    order = (
        Order.objects
        .select_for_update()
        .prefetch_related("items__variant")
        .get(id=order_id)
    )

    mark_order_as_paid(
        order,
        amount_total_cents=payment_intent.get("amount_received") or 0,
        payment_intent_id=payment_intent.get("id", "") or "",
        checkout_session_id=order.stripe_checkout_session_id or "",
        currency=payment_intent.get("currency", "usd"),
        raw_response=payment_intent,
        status_note="Stripe payment intent succeeded.",
    )

def remove_paid_order_items_from_cart(request, order):
    cart = get_or_create_cart(request)

    purchased_variant_ids = order.items.exclude(
        variant__isnull=True
    ).values_list(
        "variant_id",
        flat=True
    )

    CartItem.objects.filter(
        cart=cart,
        variant_id__in=purchased_variant_ids,
    ).delete()

def reduce_inventory_for_order(order):
    for item in order.items.select_related("variant"):
        variant = item.variant

        if variant is None:
            continue

        if variant.stock_quantity < item.quantity:
            raise ValueError(
                f"Not enough inventory for {variant.sku}."
            )

        variant.stock_quantity -= item.quantity
        variant.save(update_fields=["stock_quantity"])

@login_required
def order_list(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders,
        },
    )

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order.objects
        .prefetch_related(
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
