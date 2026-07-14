from decimal import Decimal
import stripe
import json

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
    ShippingAddress,
    Payment,
    StripeEvent
)

stripe.api_key = settings.STRIPE_SECRET_KEY

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
                        "product",
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
                            f"{cart_item.product.name} does not have a valid size/color option."
                        )

                    variant = cart_item.variant

                    if not variant.is_active:
                        raise ValueError(
                            f"{cart_item.product.name} — {variant.color}, Size {variant.size} is no longer available."
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
                    line_total=order_line_total,
                    shipping_total=Decimal("0.00"),
                    tax_total=Decimal("0.00"),
                    discount_total=Decimal("0.00"),
                    grand_total=order_line_total,
                )

                for cart_item in cart_items:
                    unit_price = cart_item.unit_price()
                    line_total = cart_item.line_total()
                    variant = cart_item.variant

                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        variant=variant,
                        product_name=cart_item.product.name,
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
                    "allowed_countries": ["US", "CA"],
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
        Order.objects.select_related("payment").prefetch_related("items"),
        id=order_id,
    )

    if request.user.is_authenticated:
        if order.user_id != request.user.id:
            raise PermissionDenied
    else:
        completed_order_id = request.session.get("completed_order_id")

        if completed_order_id != order_id:
            raise PermissionDenied

    is_paid = order.status == Order.Status.PAID
    payment = getattr(order, "payment", None)

    if is_paid:
        remove_paid_order_items_from_cart(request, order)

    return render(request, "orders/order_success.html", {
        "order": order,
        "is_paid": is_paid,
        "payment": payment,
    })

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

    for item in order.items.all():
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item.product.name,
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

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret,
        )
    except ValueError as error:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as error:
        return HttpResponse(status=400)

    event_data = json.loads(payload.decode("utf-8"))

    stripe_event_id = event["id"]
    event_type = event["type"]

    with transaction.atomic():
        stripe_event, created = StripeEvent.objects.get_or_create(
            stripe_event_id=stripe_event_id,
            defaults={
                "event_type": event_type,
                "raw_event": event_data,
            },
        )

        if not created and stripe_event.processed:
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
    order_id = get_order_id_from_metadata(session)

    if order_id is None:
        print("No order_id found on checkout session metadata.")
        return

    order = (
        Order.objects
        .select_for_update()
        .prefetch_related("items__variant")
        .get(id=order_id)
    )

    if order.status == Order.Status.PAID:
        return

    amount_total = session.get("amount_total") or 0
    amount_subtotal = session.get("amount_subtotal") or 0
    payment_intent_id = session.get("payment_intent", "")
    checkout_session_id = session.get("id", "")

    order.status = Order.Status.PAID
    order.subtotal = Decimal(amount_subtotal) / Decimal("100")
    order.grand_total = Decimal(amount_total) / Decimal("100")
    order.stripe_checkout_session_id = checkout_session_id
    order.stripe_payment_intent_id = payment_intent_id or ""

    order.save(
        update_fields=[
            "status",
            "subtotal",
            "grand_total",
            "stripe_checkout_session_id",
            "stripe_payment_intent_id",
            "updated_at",
        ]
    )

    Payment.objects.update_or_create(
        order=order,
        defaults={
            "stripe_payment_intent_id": payment_intent_id or None,
            "stripe_checkout_session_id": checkout_session_id or None,
            "amount": order.grand_total,
            "currency": session.get("currency", "usd"),
            "status": Payment.Status.SUCCEEDED,
            "raw_response": session,
        },
    )
    reduce_inventory_for_order(order)

def handle_payment_intent_succeeded(payment_intent):
    order_id = get_order_id_from_metadata(payment_intent)

    if order_id is None:
        print("No order_id found on payment intent metadata.")
        return

    order = (
        Order.objects
        .select_for_update()
        .prefetch_related("items__variant")
        .get(id=order_id)
    )

    if order.status == Order.Status.PAID:
        return

    amount_received = payment_intent.get("amount_received") or 0
    payment_intent_id = payment_intent.get("id", "")

    order.status = Order.Status.PAID
    order.grand_total = Decimal(amount_received) / Decimal("100")
    order.stripe_payment_intent_id = payment_intent_id

    order.save(
        update_fields=[
            "status",
            "grand_total",
            "stripe_payment_intent_id",
            "updated_at",
        ]
    )

    Payment.objects.update_or_create(
        order=order,
        defaults={
            "stripe_payment_intent_id": payment_intent_id or None,
            "stripe_checkout_session_id": order.stripe_checkout_session_id or None,
            "amount": order.grand_total,
            "currency": payment_intent.get("currency", "usd"),
            "status": Payment.Status.SUCCEEDED,
            "raw_response": payment_intent,
        },
    )

    reduce_inventory_for_order(order)

def remove_paid_order_items_from_cart(request, order):
    cart = get_or_create_cart(request)

    for order_item in order.items.select_related("variant"):
        if order_item.variant is None:
            continue

        cart_item = CartItem.objects.filter(
            cart=cart,
            variant=order_item.variant,
        ).first()

        if cart_item is None:
            continue

        if cart_item.quantity <= order_item.quantity:
            cart_item.delete()
        else:
            cart_item.quantity -= order_item.quantity
            cart_item.save(update_fields=["quantity"])

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