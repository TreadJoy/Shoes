from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from scipy.stats import variation

from .models import Cart, CartItem
from web.products.models import Product, ProductVariant




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

    if variant.stock_quantity < 1:
        messages.error(
            request,
            "That size and color is currently out of stock.",
        )
        return redirect(
            "products:product_detail",
            slug=variant.product.slug,
        )

    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            "quantity": 1,
        },
    )

    if not created:
        new_quantity = cart_item.quantity + 1

        if new_quantity > variant.stock_quantity:
            messages.error(
                request,
                "You cannot add more than the available inventory.",
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
        elif quantity > item.variant.stock_quantity:
            messages.error(
                request,
                f"Only {item.variant.stock_quantity} of "
                        f"{item.variant.product.name} - {item.variant.color}, "
                        f"Size {item.variant.size} available."
            )

        else:
            item.quantity = quantity
            item.save()
            messages.success(request, f"Updated {item.variant.product.name} quantity.")

    return redirect("cart:cart_detail")