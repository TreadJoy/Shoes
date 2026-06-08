from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "email",
        "status",
        "total",
        "total_items",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "id",
        "user__username",
        "email",
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product_name",
        "price",
        "quantity",
        "size",
        "color",
        "subtotal",
    )
    search_fields = (
        "product_name",
        "order__email",
    )


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "city",
        "state",
        "postal_code",
        "country",
        "created_at",
    )
    search_fields = (
        "full_name",
        "email",
        "city",
        "state",
        "postal_code",
    )