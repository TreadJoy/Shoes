from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.views.decorators.http import require_POST

from .models import Cart, CartItem
from web.products.models import ProductVariant
from web.products.services import PREORDER, variant_availability




def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart

    if not request.session.session_key:
        request.session.create()

    cart, created = Cart.objects.get_or_create(
        session_key=request.session.session_key,
        user=None,
    )
    return cart


def cart_detail(request):
    cart = get_or_create_cart(request)

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
    })

@require_POST
def add_to_cart(request):
    if request.method != "POST":
        return redirect("products:product_list")

    variant_id = request.POST.get("variant_id")

    if not variant_id:
        messages.error(request, "Please select a size and color.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    variant = get_object_or_404(
        ProductVariant.objects.select_related("product"),
        id=variant_id,
        is_active=True,
    )

    availability = variant_availability(variant)

    if not availability.is_available:
        messages.error(
            request,
            (
                "That preorder option is not currently available."
                if availability.fulfillment_type == PREORDER
                else "That size and color is currently out of stock."
            ),
        )
        return redirect(
            "products:product_detail",
            slug=variant.product.slug,
        )

    cart = get_or_create_cart(request)

    if availability.fulfillment_type == PREORDER:
        incompatible_item_exists = cart.items.exclude(
            preorder_batch=availability.preorder_batch,
        ).exists()
        if incompatible_item_exists:
            messages.error(
                request,
                "Your cart can contain items from only one preorder batch.",
            )
            return redirect("cart:cart_detail")
    elif cart.items.filter(preorder_batch__isnull=False).exists():
        messages.error(
            request,
            "Stocked products and preorders cannot be purchased together.",
        )
        return redirect("cart:cart_detail")

    existing_item = cart.items.filter(variant=variant).first()
    new_quantity = existing_item.quantity + 1 if existing_item else 1
    other_cart_quantity = (
        cart.items.exclude(variant=variant).aggregate(total=Sum("quantity"))[
            "total"
        ]
        or 0
    )
    if (
        availability.fulfillment_type == PREORDER
        and other_cart_quantity + new_quantity
        > availability.preorder_batch.remaining_quantity
    ):
        messages.error(
            request,
            "The selected preorder quantities exceed the remaining batch "
            "availability.",
        )
        return redirect("cart:cart_detail")

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            "quantity": 1,
            "preorder_batch": availability.preorder_batch,
        },
    )

    if not created:
        if new_quantity > availability.available_quantity:
            messages.error(
                request,
                (
                    "That preorder quantity is no longer available."
                    if availability.fulfillment_type == PREORDER
                    else "You cannot add more than the available inventory."
                ),
            )
            return redirect("cart:cart_detail")

        cart_item.quantity = new_quantity
        cart_item.save(update_fields=["quantity"])

    messages.success(
        request,
        f"{variant.product.name} was added to your cart.",
    )

    return redirect("cart:cart_detail")


@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    product_name = item.variant.product.name
    item.delete()

    messages.success(request, f"Removed {product_name} from your cart.")

    return redirect("cart:cart_detail")

@require_POST
def clear_cart(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()

    messages.success(request, "Your cart has been cleared.")

    return redirect("cart:cart_detail")

@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if request.method == "POST":
        quantity = request.POST.get("quantity")

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid quantity.")
            return redirect("cart:cart_detail")

        if quantity <= 0:
            product_name = item.variant.product.name
            item.delete()
            messages.success(request, f"Removed {product_name} from your cart.")
            return redirect("cart:cart_detail")

        availability = variant_availability(item.variant)
        batch_is_current = (
            item.preorder_batch_id
            == (
                availability.preorder_batch.id
                if availability.preorder_batch is not None
                else None
            )
        )
        preorder_cart_total = (
            cart.items.exclude(pk=item.pk).aggregate(total=Sum("quantity"))[
                "total"
            ]
            or 0
        ) + quantity

        if not batch_is_current:
            messages.error(
                request,
                "This cart item is no longer current. Remove it and select "
                "the current offer.",
            )
        elif quantity > availability.available_quantity:
            messages.error(
                request,
                (
                    f"The selected preorder quantity for "
                    f"{item.variant.product.name} is no longer available."
                    if availability.fulfillment_type == PREORDER
                    else (
                        f"Only {availability.available_quantity} of "
                        f"{item.variant.product.name} - {item.variant.color}, "
                        f"Size {item.variant.size} available."
                    )
                )
            )
        elif (
            availability.fulfillment_type == PREORDER
            and preorder_cart_total
            > availability.preorder_batch.remaining_quantity
        ):
            messages.error(
                request,
                "The selected preorder quantities exceed the remaining batch "
                "availability.",
            )
        else:
            item.quantity = quantity
            item.save()
            messages.success(request, f"Updated {item.variant.product.name} quantity.")

    return redirect("cart:cart_detail")
