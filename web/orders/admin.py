from django.contrib import admin

from .models import (
    Order,
    OrderItem,
    OrderStatusEvent,
    Payment,
    Shipment,
    ShippingAddress,
    StripeEvent
)

class ShipmentInline(admin.TabularInline):
    model = Shipment
    extra = 0
    fields = (
        "carrier",
        "tracking_number",
        "tracking_url",
        "estimated_delivery",
        "shipped_at",
        "delivered_at",
        "notes",
    )

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

class OrderStatusEventAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "from_status",
        "to_status",
        "note",
        "created_at",
    )
    list_filter = (
        "to_status",
        "created_at",
    )

    search_fields = (
        "order__id",
        "from_status",
        "to_status",
        "note",
    )

    readonly_fields = (
        "order",
        "from_status",
        "to_status",
        "note",
        "created_at",
    )


class OrderStatusEventInline(admin.TabularInline):
    model = OrderStatusEvent
    extra = 0
    readonly_fields = (
        "from_status",
        "to_status",
        "note",
        "created_at",
    )
    fields = (
        "from_status",
        "to_status",
        "note",
        "created_at",
    )
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "full_name",
        "status",
        "subtotal",
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
    actions = (
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_canceled",
    )
    inlines = [
        OrderItemInline,
        OrderStatusEventInline,
        ShipmentInline,
    ]
    def save_model(self, request, obj, form, change):
        previous_status = None

        if change:
            previous_status = (
                Order.objects
                .only("status")
                .get(pk=obj.pk)
                .status
            )

        super().save_model(request, obj, form, change)

        if(
            change
            and "status" in form.changed_data
            and previous_status != obj.status
        ):
            OrderStatusEvent.objects.create(
                order=obj,
                from_status=previous_status,
                to_status=obj.status,
                note=f"Order status changed manually in admin by {request.user}.",
            )

    def update_status_for_queryset(self, request, queryset, new_status, note):
        updated_count = 0

        for order in queryset:
            previous_status = order.status

            if previous_status == new_status:
                continue

            order.status = new_status
            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            OrderStatusEvent.objects.create(
                order=order,
                from_status=previous_status,
                to_status=new_status,
                note=f"{note} by {request.user}.",
            )

            updated_count += 1

        self.message_user(
            request,
            f"{updated_count} order(s) updated.",
        )

    @admin.action(description="Mark selected orders as shipped.")
    def mark_as_shipped(self, request, queryset):
        self.update_status_for_queryset(
            request=request,
            queryset=queryset,
            new_status=Order.Status.SHIPPED,
            note="Marked as shipped.",
        )
    @admin.action(description="Mark selected orders as delivered.")
    def mark_as_delivered(self, request, queryset):
        self.update_status_for_queryset(
            request=request,
            queryset=queryset,
            new_status=Order.Status.DELIVERED,
            note="Marked as delivered.",
        )
    @admin.action(description="Mark selected orders as canceled.")
    def mark_as_canceled(self, request, queryset):
        self.update_status_for_queryset(
            request=request,
            queryset=queryset,
            new_status=Order.Status.CANCELED,
            note="Marked as canceled.",
        )

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

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "carrier",
        "tracking_number",
        "shipped_at",
        "delivered_at",
        "created_at",
    )

    list_filter = (
        "carrier",
        "shipped_at",
        "delivered_at",
        "created_at",
    )

    search_fields = (
        "order__id",
        "carrier",
        "tracking_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
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
