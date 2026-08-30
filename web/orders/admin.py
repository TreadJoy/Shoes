from django.contrib import admin
from django.db.models import Q
from django.utils import timezone

from .models import (
    CheckoutAttempt,
    CheckoutQuoteComponent,
    CheckoutQuoteLine,
    InventoryAllocation,
    InventoryAllocationItem,
    InventoryReservation,
    Order,
    OrderItem,
    OrderItemComponentSnapshot,
    OrderStatusEvent,
    Payment,
    Refund,
    Shipment,
    ShippingAddress,
    StripeEvent
)
from .transitions import OrderTransitionError, transition_order


FULFILLMENT_BLOCKING_STATUSES = [
    InventoryAllocation.Status.REVIEW_REQUIRED,
    InventoryAllocation.Status.REFUND_PENDING,
]
REVIEW_TRACKED_STATUSES = [
    *FULFILLMENT_BLOCKING_STATUSES,
    InventoryAllocation.Status.REFUNDED,
]

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
    can_delete = False

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "variant",
        "product_name",
        "sku",
        "fulfillment_type",
        "preorder_batch_code",
        "estimated_tender_start",
        "estimated_tender_end",
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
        "fulfillment_type",
        "preorder_batch_code",
        "estimated_tender_start",
        "estimated_tender_end",
        "size",
        "color",
        "unit_price",
        "quantity",
        "line_total",
    )

    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(OrderStatusEvent)
class OrderStatusEventAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "from_status",
        "to_status",
        "source",
        "reason",
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
        "source",
        "reason",
        "external_reference",
        "internal_detail",
        "customer_message",
    )

    readonly_fields = (
        "order",
        "actor",
        "from_status",
        "to_status",
        "source",
        "reason",
        "external_reference",
        "internal_detail",
        "customer_message",
        "note",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderStatusEventInline(admin.TabularInline):
    model = OrderStatusEvent
    extra = 0
    readonly_fields = (
        "actor",
        "from_status",
        "to_status",
        "source",
        "reason",
        "external_reference",
        "internal_detail",
        "customer_message",
        "created_at",
    )
    fields = (
        "actor",
        "from_status",
        "to_status",
        "source",
        "reason",
        "external_reference",
        "internal_detail",
        "customer_message",
        "created_at",
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "full_name",
        "status",
        "fulfillment_type",
        "preorder_batch",
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
        "fulfillment_type",
        "preorder_batch",
        "inventory_allocation__status",
        "created_at",
    )
    search_fields = (
        "id",
        "email",
        "full_name",
    )
    readonly_fields = [field.name for field in Order._meta.fields]
    actions = ("mark_as_processing",)
    inlines = [
        OrderItemInline,
        OrderStatusEventInline,
        ShipmentInline,
    ]
    @admin.action(description="Mark selected paid orders as processing")
    def mark_as_processing(self, request, queryset):
        updated_count = 0
        blocked_count = 0
        for order in queryset:
            try:
                _, changed = transition_order(
                    order,
                    Order.Status.PROCESSING,
                    source=OrderStatusEvent.Source.ADMIN,
                    reason="staff_started_processing",
                    actor=request.user,
                    internal_detail="Staff began fulfillment processing.",
                    customer_message="Your order is being prepared for shipment.",
                )
            except OrderTransitionError:
                blocked_count += 1
                continue
            updated_count += int(changed)

        self.message_user(
            request,
            f"{updated_count} order(s) updated.",
        )

        if blocked_count:
            self.message_user(
                request,
                f"{blocked_count} order(s) skipped because the transition is not allowed.",
                level="warning",
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

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

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
    readonly_fields = [field.name for field in OrderItem._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderItemComponentSnapshot)
class OrderItemComponentSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "order_item",
        "part_type_code",
        "part_code",
        "part_variant_sku",
        "quantity",
        "created_at",
    )
    list_select_related = ("order_item", "order_item__order")
    search_fields = (
        "order_item__order__id",
        "part_type_code",
        "part_code",
        "part_variant_sku",
    )
    readonly_fields = (
        "order_item",
        "part_type_code",
        "part_id_snapshot",
        "part_code",
        "part_variant_id_snapshot",
        "part_variant_sku",
        "quantity",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
    readonly_fields = [field.name for field in ShippingAddress._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

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

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    exclude = ("raw_response",)
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
    readonly_fields = [field.name for field in Payment._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CheckoutAttempt)
class CheckoutAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "email",
        "grand_total",
        "stripe_checkout_session_id",
        "expires_at",
        "created_at",
    )
    list_filter = ("status", "currency", "created_at")
    search_fields = ("id", "email", "stripe_checkout_session_id", "idempotency_key")
    readonly_fields = [field.name for field in CheckoutAttempt._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CheckoutQuoteLine)
class CheckoutQuoteLineAdmin(admin.ModelAdmin):
    list_display = (
        "attempt",
        "sku",
        "quantity",
        "unit_price",
        "line_total",
        "fulfillment_type",
    )
    list_select_related = ("attempt", "variant", "preorder_batch")
    search_fields = ("attempt__id", "sku", "product_name")
    readonly_fields = [field.name for field in CheckoutQuoteLine._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CheckoutQuoteComponent)
class CheckoutQuoteComponentAdmin(admin.ModelAdmin):
    list_display = (
        "quote_line",
        "part_type_code",
        "part_variant_sku",
        "quantity",
    )
    list_select_related = ("quote_line__attempt",)
    search_fields = (
        "quote_line__attempt__id",
        "part_type_code",
        "part_variant_sku",
    )
    readonly_fields = [field.name for field in CheckoutQuoteComponent._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(InventoryReservation)
class InventoryReservationAdmin(admin.ModelAdmin):
    list_display = (
        "attempt",
        "variant",
        "quantity",
        "status",
        "expires_at",
        "committed_at",
        "released_at",
    )
    list_filter = ("status", "expires_at")
    list_select_related = ("attempt", "variant", "preorder_batch")
    search_fields = ("attempt__id", "variant__sku")
    readonly_fields = [field.name for field in InventoryReservation._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    exclude = ("raw_event",)
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

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class InventoryAllocationItemInline(admin.TabularInline):
    model = InventoryAllocationItem
    extra = 0
    can_delete = False
    fields = (
        "variant",
        "fulfillment_type",
        "preorder_batch",
        "sku",
        "required_quantity",
        "allocated_quantity",
        "variant_available_before",
        "variant_available_after",
        "batch_available_before",
        "batch_available_after",
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
    readonly_fields = [field.name for field in InventoryAllocation._meta.fields]
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
                f"(SKU availability {item.variant_available_before} to "
                f"{item.variant_available_after})"
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
    exclude = ("raw_response",)
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
