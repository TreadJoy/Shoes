from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from web.cart.views import get_or_create_cart
from .models import Order, OrderItem, ShippingAddress
from django.contrib import messages
from django.db import transaction

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
            messages.error(request, "Please fill out all required shipping fields.")
            return render(request, "orders/checkout.html", {
                "cart": cart,
            })

        for item in cart.items.all():
            product = item.product

            if item.quantity > product.stock_quantity:
                messages.error(
                    request,
                    f"Only {product.stock_quantity} of {product.name} available."
                )
                return redirect("cart:cart_detail")

        with transaction.atomic():
            shipping_address = ShippingAddress.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=request.POST.get("full_name"),
                email=request.POST.get("email"),
                address_line_1=request.POST.get("address_line_1"),
                address_line_2=request.POST.get("address_line_2", ""),
                city=request.POST.get("city"),
                state=request.POST.get("state"),
                postal_code=request.POST.get("postal_code"),
            )

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                shipping_address=shipping_address,
                email=shipping_address.email,
                status="pending",
                total=cart.total_price(),
            )

            for item in cart.items.all():
                product = item.product

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.current_price(),
                    quantity=item.quantity,
                    size=item.size,
                    color=item.color,
                )

                product.stock_quantity -= item.quantity
                product.save()

            cart.items.all().delete()

        messages.success(request, f"Order #{order.id} was placed successfully!")

        return redirect("orders:order_success", order_id=order.id)

    return render(request, "orders/checkout.html", {
        "cart": cart,
    })

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, "orders/order_success.html", {
        "order": order,
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