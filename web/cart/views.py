from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .services import (
    CartItemNotFound,
    CartMutationError,
    add_variant,
    clear_cart as clear_cart_service,
    get_or_create_cart,
    remove_item,
    update_item,
)


def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, "cart/cart_detail.html", {"cart": cart})


def _redirect_after_error(error, *, fallback="cart:cart_detail"):
    if error.product_slug:
        return redirect("products:product_detail", slug=error.product_slug)
    return redirect(fallback)


@require_POST
def add_to_cart(request):
    variant_id = request.POST.get("variant_id")
    if not variant_id:
        messages.error(request, "Please select a size and color.")
        return redirect("products:product_list")

    cart = get_or_create_cart(request)
    try:
        product_name = add_variant(cart, variant_id)
    except CartMutationError as error:
        messages.error(request, str(error))
        return _redirect_after_error(error)

    messages.success(request, f"{product_name} was added to your cart.")
    return redirect("cart:cart_detail")


@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    try:
        product_name = remove_item(cart, item_id)
    except CartItemNotFound:
        from django.http import Http404

        raise Http404
    except CartMutationError:
        return redirect("cart:cart_detail")

    messages.success(request, f"Removed {product_name} from your cart.")
    return redirect("cart:cart_detail")


@require_POST
def clear_cart(request):
    clear_cart_service(get_or_create_cart(request))
    messages.success(request, "Your cart has been cleared.")
    return redirect("cart:cart_detail")


@require_POST
def update_cart_item(request, item_id):
    try:
        quantity = int(request.POST.get("quantity"))
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("cart:cart_detail")

    cart = get_or_create_cart(request)
    try:
        product_name = update_item(cart, item_id, quantity)
    except CartItemNotFound:
        from django.http import Http404

        raise Http404
    except CartMutationError as error:
        messages.error(request, str(error))
        return redirect("cart:cart_detail")

    if quantity <= 0:
        messages.success(request, f"Removed {product_name} from your cart.")
    else:
        messages.success(request, f"Updated {product_name} quantity.")
    return redirect("cart:cart_detail")
