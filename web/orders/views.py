from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from web.cart.views import get_or_create_cart
from .models import Order, OrderItem, ShippingAddress
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied

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

        try:
            with transaction.atomic():
                locked_items = []
                order_total = Decimal("0.00")

                for cart_item in cart.items.select_related("product"):
                    product = Product.objects.select_for_update().get(
                        pk=cart_item.product_id
                    )

                    if not product.is_active:
                        raise ValueError(f"{product.name} is currently unavailable.")

                    if cart_item.quantity > product.stock_quantity:
                        raise ValueError(
                            f"Only {product.stock_quantity} of " 
                            f"{product.name} available."
                        )

                    price = product.current_price()
                    order_total += price * cart_item.quantity

                    locked_items.append((cart_item, product, price))

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
                    status="pending",
                    total=order_total,
                )

                for cart_item, product, price in locked_items:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=price,
                        quantity=cart_item.quantity,
                        size=cart_item.size,
                        color=cart_item.color,
                    )

                    product.stock_quantity -= cart_item.quantity
                    product.save(update_fields=["stock_quantity"])

                cart.items.all().delete()

        except ValueError as error:
            messages.error(request, str(error))
            return redirect("cart:cart_detail")

        request.session["completed_order_id"] = order.id

        messages.success(request, f"Order #{order.id} was placed successfully!")

        return redirect("orders:order_success", order_id=order.id)

    return render(request, "orders/checkout.html", {
        "cart": cart,
    })

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user.is_authenticated:
        if order.user_id != request.user.id:
            raise PermissionDenied

    else:
        completed_order_id = request.session.get("completed_order_id")

        if completed_order_id != order_id:
            raise PermissionDenied

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