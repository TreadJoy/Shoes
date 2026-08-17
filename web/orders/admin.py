from django import forms
from django.contrib import admin
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import (
    InventoryAllocation,
    InventoryAllocationItem,
    Order,
    OrderItem,
    OrderStatusEvent,
    Payment,
    Refund,
    Shipment,
    ShippingAddress,
    StripeEvent
)


FULFILLMENT_BLOCKING_STATUSES = [
    InventoryAllocation.Status.REVIEW_REQUIRED,
    InventoryAllocation.Status.REFUND_PENDING,
]
REVIEW_TRACKED_STATUSES = [
    *FULFILLMENT_BLOCKING_STATUSES,
    InventoryAllocation.Status.REFUNDED,
]


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def clean_status(self):
        status = self.cleaned_data["status"]

        if not self.instance.pk:
            return status

        fulfillment_statuses = [
            Order.Status.PROCESSING,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
        ]
        allocation_is_blocked = InventoryAllocation.objects.filter(
            order=self.instance,
            status__in=FULFILLMENT_BLOCKING_STATUSES,
        ).exists()

        if allocation_is_blocked and status in fulfillment_statuses:
            raise forms.ValidationError(
                "Resolve the inventory review before fulfilling this order."
            )

        return status

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
    form = OrderAdminForm
    list_display = (
        "id",
        "email",
        "full_name",
        "status",
        "inventory_status_display",
        "inventory_review_due_at",
        "subtotal",
        "shipping_total",
        "tax_total",
        "discount_total",
        "grand_total",
        "created_at",
    )
    list_filter = (
        "status",
        "inventory_allocation__status",
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
        blocked_count = 0

        for order in queryset:
            previous_status = order.status

            if (
                new_status in [
                    Order.Status.PROCESSING,
                    Order.Status.SHIPPED,
                    Order.Status.DELIVERED,
                ]
                and InventoryAllocation.objects.filter(
                    order=order,
                    status__in=FULFILLMENT_BLOCKING_STATUSES,
                ).exists()
            ):
                blocked_count += 1
                continue

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

        if blocked_count:
            self.message_user(
                request,
                (
                    f"{blocked_count} order(s) skipped because inventory "
                    "review is still open."
                ),
                level=messages.WARNING,
            )

    @admin.display(description="Inventory status")
    def inventory_status_display(self, obj):
        try:
            return obj.inventory_allocation.get_status_display()
        except InventoryAllocation.DoesNotExist:
            return "Not attempted"

    @admin.display(description="Inventory review due")
    def inventory_review_due_at(self, obj):
        try:
            return obj.inventory_allocation.review_due_at
        except InventoryAllocation.DoesNotExist:
            return None

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


class InventoryAllocationItemInline(admin.TabularInline):
    model = InventoryAllocationItem
    extra = 0
    can_delete = False
    fields = (
        "variant",
        "sku",
        "required_quantity",
        "allocated_quantity",
        "stock_before",
        "stock_after",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


class InventoryReviewOverdueFilter(admin.SimpleListFilter):
    title = "review deadline"
    parameter_name = "review_overdue"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Overdue"),
            ("no", "Not overdue"),
        ]

    def queryset(self, request, queryset):
        incomplete_action = (
            Q(refund_initiated_at__isnull=True)
            | Q(customer_notified_at__isnull=True)
        )
        overdue = (
            Q(status__in=REVIEW_TRACKED_STATUSES)
            & Q(review_due_at__lt=timezone.now())
            & incomplete_action
        )

        if self.value() == "yes":
            return queryset.filter(overdue)

        if self.value() == "no":
            return queryset.exclude(overdue)

        return queryset


@admin.register(InventoryAllocation)
class InventoryAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "customer_display",
        "status",
        "shortage_details",
        "review_due_at",
        "overdue_display",
        "stripe_payment_intent_id",
        "stripe_checkout_session_id",
        "refund_initiated_at",
        "customer_notified_at",
        "customer_notified_by",
        "resolved_at",
    )
    list_filter = (
        "status",
        InventoryReviewOverdueFilter,
        "review_due_at",
    )
    search_fields = (
        "order__id",
        "order__email",
        "items__sku",
    )
    list_select_related = (
        "order",
        "customer_notified_by",
    )
    readonly_fields = (
        "order",
        "status",
        "review_due_at",
        "refund_initiated_at",
        "customer_notified_at",
        "customer_notified_by",
        "resolved_at",
        "created_at",
        "updated_at",
    )
    actions = ("mark_customer_notified",)
    inlines = (InventoryAllocationItemInline,)

    @admin.display(description="Overdue", boolean=True)
    def overdue_display(self, obj):
        return obj.is_overdue

    @admin.display(description="Customer")
    def customer_display(self, obj):
        return f"{obj.order.full_name} ({obj.order.email})"

    @admin.display(description="Shortage details")
    def shortage_details(self, obj):
        return "; ".join(
            (
                f"{item.sku}: {item.allocated_quantity}/"
                f"{item.required_quantity} allocated "
                f"(stock {item.stock_before} to {item.stock_after})"
            )
            for item in obj.items.all()
        )

    @admin.display(description="Stripe PaymentIntent")
    def stripe_payment_intent_id(self, obj):
        try:
            return obj.order.payment.stripe_payment_intent_id or "-"
        except Payment.DoesNotExist:
            return obj.order.stripe_payment_intent_id or "-"

    @admin.display(description="Stripe Checkout Session")
    def stripe_checkout_session_id(self, obj):
        try:
            return obj.order.payment.stripe_checkout_session_id or "-"
        except Payment.DoesNotExist:
            return obj.order.stripe_checkout_session_id or "-"

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related("order", "order__payment", "customer_notified_by")
            .prefetch_related("items")
        )

    @admin.action(description="Mark selected customers as notified")
    def mark_customer_notified(self, request, queryset):
        updated_count = 0

        for allocation in queryset.filter(
            status__in=REVIEW_TRACKED_STATUSES,
            customer_notified_at__isnull=True,
        ):
            allocation.customer_notified_at = timezone.now()
            allocation.customer_notified_by = request.user
            allocation.save(
                update_fields=[
                    "customer_notified_at",
                    "customer_notified_by",
                    "updated_at",
                ]
            )
            updated_count += 1

        self.message_user(
            request,
            f"Customer notification recorded for {updated_count} order(s).",
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        "stripe_refund_id",
        "payment",
        "amount",
        "currency",
        "status",
        "stripe_created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "currency",
        "stripe_created_at",
    )
    search_fields = (
        "stripe_refund_id",
        "stripe_payment_intent_id",
        "payment__order__id",
        "payment__order__email",
    )
    list_select_related = ("payment", "payment__order")
    readonly_fields = (
        "payment",
        "stripe_refund_id",
        "stripe_payment_intent_id",
        "amount",
        "currency",
        "status",
        "reason",
        "failure_reason",
        "stripe_created_at",
        "raw_response",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
