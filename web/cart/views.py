from django.shortcuts import render, redirect, get_object_or_404
from web.products.models import Product
from .models import Cart, CartItem
from django.contrib import messages

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


def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id, is_active=True)

        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": 1},
        )

        if created:
            if product.stock_quantity <= 0:
                cart_item.delete()
                messages.error(request, f"{product.name} is currently out of stock.")
                return redirect("products:product_detail", slug=product.slug)

            messages.success(request, f"Added {product.name} to your cart.")
        else:
            if cart_item.quantity >= product.stock_quantity:
                messages.error(
                    request,
                    f"Only {product.stock_quantity} of {product.name} available."
                )
                return redirect("cart:cart_detail")

            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Updated {product.name} quantity in your cart.")

    return redirect("cart:cart_detail")

def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    product_name = item.product.name
    item.delete()

    messages.success(request, f"Removed {product_name} from your cart.")

    return redirect("cart:cart_detail")


def clear_cart(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()

    messages.success(request, "Your cart has been cleared.")

    return redirect("cart:cart_detail")

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
            product_name = item.product.name
            item.delete()
            messages.success(request, f"Removed {product_name} from your cart.")
        elif quantity > item.product.stock_quantity:
            messages.error(
                request,
                f"Only {item.product.stock_quantity} of {item.product.name} available."
            )
        else:
            item.quantity = quantity
            item.save()
            messages.success(request, f"Updated {item.product.name} quantity.")

    return redirect("cart:cart_detail")