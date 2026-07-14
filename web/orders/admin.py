from django.contrib import admin

from .models import Order, OrderItem, Payment, ShippingAddress, StripeEvent


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "variant",
        "product_name",
        "sku",
        "size",
        "color",
        "unit_price",
        "quantity",
        "line_total",
    )

    fields = (
        "product",
        "variant",
        "product_name",
        "sku",
        "size",
        "color",
        "unit_price",
        "quantity",
        "line_total",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "full_name",
        "status",
        "line_total",
        "shipping_total",
        "tax_total",
        "discount_total",
        "grand_total",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "id",
        "email",
        "full_name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product_name",
        "sku",
        "size",
        "color",
        "unit_price",
        "quantity",
        "line_total",
        "created_at",
    )
    list_filter = (
        "created_at",
        "color",
        "size",
    )
    search_fields = (
        "order__id",
        "product_name",
        "sku",
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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "amount",
        "currency",
        "status",
        "stripe_payment_intent_id",
        "stripe_checkout_session_id",
        "created_at",
    )
    list_filter = (
        "status",
        "currency",
        "created_at",
    )
    search_fields = (
        "order__id",
        "stripe_payment_intent_id",
        "stripe_checkout_session_id",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "raw_response",
    )

@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    list_display = (
        "stripe_event_id",
        "event_type",
        "processed",
        "created_at",
        "processed_at",
    )
    list_filter = (
        "event_type",
        "processed",
        "created_at",
    )
    search_fields = (
        "stripe_event_id",
        "event_type",
    )
    readonly_fields = (
        "stripe_event_id",
        "event_type",
        "processed",
        "raw_event",
        "created_at",
        "processed_at",
    )