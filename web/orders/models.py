
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from web.products.models import Product, ProductVariant


class ShippingAddress(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="shipping_addresses",
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="United States")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.state}"


class Order(models.Model):
    class FulfillmentType(models.TextChoices):
        STOCKED = "stocked", "Stocked"
        PREORDER = "preorder", "Preorder"

    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending Payment"
        REVIEW_REQUIRED = "review_required", "Review Required"
        PAID = "paid", "Paid"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELED = "canceled", "Canceled"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="orders",
    )
    full_name = models.CharField(max_length=100)
    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="orders",
    )
    source_cart = models.ForeignKey(
        "cart.Cart",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="checkout_orders",
    )
    checkout_attempt = models.OneToOneField(
        "CheckoutAttempt",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="order",
    )
    cart_reconciled_at = models.DateTimeField(blank=True, null=True)
    email = models.EmailField(
        blank=True
    )
    currency = models.CharField(max_length=3, default="usd")
    shipping_full_name = models.CharField(max_length=100, blank=True)
    shipping_email = models.EmailField(blank=True)
    shipping_address_line_1 = models.CharField(max_length=255, blank=True)
    shipping_address_line_2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
        db_index=True,
    )
    fulfillment_type = models.CharField(
        max_length=20,
        choices=FulfillmentType.choices,
        default=FulfillmentType.STOCKED,
        db_index=True,
    )
    preorder_batch = models.ForeignKey(
        "products.PreorderBatch",
        on_delete=models.PROTECT,
        related_name="orders",
        blank=True,
        null=True,
    )
    estimated_tender_start = models.DateField(blank=True, null=True)
    estimated_tender_end = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    shipping_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    tax_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    discount_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        blank=True
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True
    )
    stripe_tax_calculation_id = models.CharField(
        max_length=255,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        fulfillment_type="stocked",
                        preorder_batch__isnull=True,
                        estimated_tender_start__isnull=True,
                        estimated_tender_end__isnull=True,
                    )
                    | models.Q(
                        fulfillment_type="preorder",
                        preorder_batch__isnull=False,
                        estimated_tender_start__isnull=False,
                        estimated_tender_end__isnull=False,
                    )
                ),
                name="order_fulfillment_snapshot_consistent",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(subtotal__gte=0)
                    & models.Q(shipping_total__gte=0)
                    & models.Q(tax_total__gte=0)
                    & models.Q(discount_total__gte=0)
                    & models.Q(grand_total__gte=0)
                ),
                name="order_totals_nonnegative",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        discount_total__lte=(
                            models.F("subtotal")
                            + models.F("shipping_total")
                            + models.F("tax_total")
                        )
                    )
                ),
                name="order_discount_within_pretax_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    grand_total=(
                        models.F("subtotal")
                        + models.F("shipping_total")
                        + models.F("tax_total")
                        - models.F("discount_total")
                    )
                ),
                name="order_grand_total_matches_components",
            ),
        ]

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

class Shipment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="shipments",
    )

    carrier = models.CharField(
        max_length=20,
        blank=True,
    )

    tracking_number = models.CharField(
        max_length=50,
        blank=True,
    )

    tracking_url = models.URLField(
        blank=True,
    )

    estimated_delivery = models.DateField(
        null=True,
        blank=True,
    )

    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        super().clean()

        if not self.order_id:
            return

        previous_shipped_at = None
        previous_delivered_at = None

        if not self._state.adding:
            previous = Shipment.objects.only(
                "shipped_at",
                "delivered_at",
            ).get(pk=self.pk)
            previous_shipped_at = previous.shipped_at
            previous_delivered_at = previous.delivered_at

        shipped_at_added, delivered_at_added = self._timestamp_transitions(
            previous_shipped_at,
            previous_delivered_at,
        )

        if shipped_at_added or delivered_at_added:
            order = Order.objects.only("status").get(pk=self.order_id)
            self._validate_timestamp_transitions(
                order.status,
                shipped_at_added,
                delivered_at_added,
            )
            self._validate_inventory_allocation(
                order,
                shipped_at_added,
                delivered_at_added,
            )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            previous_shipped_at = None
            previous_delivered_at = None

            if not self._state.adding:
                previous = (
                    Shipment.objects.select_for_update()
                    .only("shipped_at", "delivered_at")
                    .get(pk=self.pk)
                )
                previous_shipped_at = previous.shipped_at
                previous_delivered_at = previous.delivered_at

            shipped_at_added, delivered_at_added = self._timestamp_transitions(
                previous_shipped_at,
                previous_delivered_at,
                update_fields=kwargs.get("update_fields"),
            )

            order = None
            if shipped_at_added or delivered_at_added:
                order = Order.objects.select_for_update().get(pk=self.order_id)
                self._validate_timestamp_transitions(
                    order.status,
                    shipped_at_added,
                    delivered_at_added,
                )
                self._validate_inventory_allocation(
                    order,
                    shipped_at_added,
                    delivered_at_added,
                )

            super().save(*args, **kwargs)

            if shipped_at_added:
                self.mark_order_shipped(order=order)

            if delivered_at_added:
                self.mark_order_delivered(order=order)

    def _timestamp_transitions(
        self,
        previous_shipped_at,
        previous_delivered_at,
        update_fields=None,
    ):
        fields_being_saved = None
        if update_fields is not None:
            fields_being_saved = set(update_fields)

        shipped_at_is_saved = (
            fields_being_saved is None or "shipped_at" in fields_being_saved
        )
        delivered_at_is_saved = (
            fields_being_saved is None or "delivered_at" in fields_being_saved
        )

        shipped_at_added = (
            shipped_at_is_saved
            and self.shipped_at is not None
            and previous_shipped_at is None
        )
        delivered_at_added = (
            delivered_at_is_saved
            and self.delivered_at is not None
            and previous_delivered_at is None
        )

        return shipped_at_added, delivered_at_added

    @staticmethod
    def _validate_timestamp_transitions(
        order_status,
        shipped_at_added,
        delivered_at_added,
    ):
        errors = {}
        effective_status = order_status

        if shipped_at_added:
            if effective_status in [
                Order.Status.PAID,
                Order.Status.PROCESSING,
            ]:
                effective_status = Order.Status.SHIPPED
            elif effective_status not in [
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ]:
                errors["shipped_at"] = (
                    "Only paid or processing orders can be marked shipped."
                )

        if delivered_at_added:
            if effective_status == Order.Status.SHIPPED:
                effective_status = Order.Status.DELIVERED
            elif effective_status != Order.Status.DELIVERED:
                errors["delivered_at"] = (
                    "An order must be shipped before it can be marked delivered."
                )

        if errors:
            raise ValidationError(errors)

    @staticmethod
    def _validate_inventory_allocation(
        order,
        shipped_at_added,
        delivered_at_added,
    ):
        if not (shipped_at_added or delivered_at_added):
            return

        allocation_is_blocked = InventoryAllocation.objects.filter(
            order=order,
            status__in=[
                InventoryAllocation.Status.REVIEW_REQUIRED,
                InventoryAllocation.Status.REFUND_PENDING,
            ],
        ).exists()

        if not allocation_is_blocked:
            return

        errors = {}

        if shipped_at_added:
            errors["shipped_at"] = (
                "This order cannot ship while inventory review is open."
            )

        if delivered_at_added:
            errors["delivered_at"] = (
                "This order cannot be delivered while inventory review is open."
            )

        raise ValidationError(errors)

    def mark_order_shipped(self, order=None):
        order = order or self.order
        if order.status == Order.Status.DELIVERED:
            return
        from .transitions import transition_order

        transition_order(
            order,
            Order.Status.SHIPPED,
            source=OrderStatusEvent.Source.SHIPMENT,
            reason="carrier_tender_recorded",
            external_reference=f"shipment:{self.pk}",
            internal_detail=f"Shipment #{self.pk} received its shipped timestamp.",
            customer_message="Your order has shipped.",
        )

    def mark_order_delivered(self, order=None):
        order = order or self.order
        from .transitions import transition_order

        transition_order(
            order,
            Order.Status.DELIVERED,
            source=OrderStatusEvent.Source.SHIPMENT,
            reason="carrier_delivery_recorded",
            external_reference=f"shipment:{self.pk}",
            internal_detail=f"Shipment #{self.pk} received its delivered timestamp.",
            customer_message="Your order was delivered.",
        )

    def __str__(self):
        return f"Shipment for Order #{self.order_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="order_items",
        blank=True,
        null=True,
    )
    fulfillment_type = models.CharField(
        max_length=20,
        choices=Order.FulfillmentType.choices,
        default=Order.FulfillmentType.STOCKED,
    )
    preorder_batch = models.ForeignKey(
        "products.PreorderBatch",
        on_delete=models.PROTECT,
        related_name="order_items",
        blank=True,
        null=True,
    )
    preorder_batch_code = models.CharField(max_length=50, blank=True)
    estimated_tender_start = models.DateField(blank=True, null=True)
    estimated_tender_end = models.DateField(blank=True, null=True)

    product_name = models.CharField(
        max_length=255,
    )

    sku = models.CharField(
        max_length=50,
        blank=True,
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    size = models.CharField(
        max_length=20,
        blank=True,
    )

    color = models.CharField(
        max_length=50,
        blank=True,
    )

    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        fulfillment_type=Order.FulfillmentType.STOCKED,
                        preorder_batch__isnull=True,
                        preorder_batch_code="",
                        estimated_tender_start__isnull=True,
                        estimated_tender_end__isnull=True,
                    )
                    | models.Q(
                        fulfillment_type=Order.FulfillmentType.PREORDER,
                        preorder_batch__isnull=False,
                        estimated_tender_start__isnull=False,
                        estimated_tender_end__isnull=False,
                    )
                ),
                name="order_item_fulfillment_snapshot_consistent",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(unit_price__gte=0)
                    & models.Q(line_total__gte=0)
                    & models.Q(quantity__gte=1)
                ),
                name="order_item_amounts_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    line_total=models.F("unit_price") * models.F("quantity")
                ),
                name="order_item_line_total_matches_quantity",
            ),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"


class OrderItemComponentSnapshot(models.Model):
    """Immutable BOM facts copied when an order line is created."""

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="component_snapshots",
    )
    part_type_code = models.CharField(max_length=30)
    part_id_snapshot = models.PositiveBigIntegerField()
    part_code = models.CharField(max_length=50)
    part_variant_id_snapshot = models.PositiveBigIntegerField()
    part_variant_sku = models.CharField(max_length=50)
    quantity = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["part_type_code", "part_variant_sku"]
        constraints = [
            models.UniqueConstraint(
                fields=["order_item", "part_type_code"],
                name="unique_order_item_component_snapshot_slot",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="order_item_component_snapshot_quantity_positive",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Order component snapshots are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Order component snapshots are immutable.")

    def __str__(self):
        return f"{self.order_item_id}: {self.part_type_code} / {self.part_variant_sku}"


class CheckoutAttempt(models.Model):
    """Short-lived server-side quote and payment attempt."""

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        STRIPE_CREATED = "stripe_created", "Stripe Checkout Created"
        PAID = "paid", "Paid"
        EXPIRED = "expired", "Expired"
        FAILED = "failed", "Failed"
        REVIEW_REQUIRED = "review_required", "Review Required"

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    cart = models.ForeignKey(
        "cart.Cart",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="checkout_attempts",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="checkout_attempts",
    )
    email = models.EmailField(blank=True)
    eligibility_state = models.CharField(max_length=2, blank=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True,
    )
    currency = models.CharField(max_length=3, default="usd")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    idempotency_key = models.CharField(max_length=64, unique=True)
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    review_reason = models.CharField(max_length=255, blank=True)
    reconciled_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart"],
                condition=(
                    models.Q(cart__isnull=False)
                    & models.Q(status__in=["created", "stripe_created"])
                ),
                name="unique_active_checkout_attempt_per_cart",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(subtotal__gte=0)
                    & models.Q(shipping_total__gte=0)
                    & models.Q(tax_total__gte=0)
                    & models.Q(discount_total__gte=0)
                    & models.Q(grand_total__gte=0)
                ),
                name="checkout_attempt_totals_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    discount_total__lte=(
                        models.F("subtotal")
                        + models.F("shipping_total")
                        + models.F("tax_total")
                    )
                ),
                name="checkout_attempt_discount_within_pretax_total",
            ),
        ]


class CheckoutQuoteLine(models.Model):
    attempt = models.ForeignKey(
        CheckoutAttempt,
        on_delete=models.CASCADE,
        related_name="quote_lines",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="checkout_quote_lines",
    )
    preorder_batch = models.ForeignKey(
        "products.PreorderBatch",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="checkout_quote_lines",
    )
    fulfillment_type = models.CharField(max_length=20, choices=Order.FulfillmentType.choices)
    sku = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=100, blank=True)
    preorder_batch_code = models.CharField(max_length=50, blank=True)
    estimated_tender_start = models.DateField(blank=True, null=True)
    estimated_tender_end = models.DateField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "variant", "preorder_batch"],
                name="unique_checkout_quote_variant_batch",
                nulls_distinct=False,
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(unit_price__gte=0)
                    & models.Q(line_total__gte=0)
                    & models.Q(quantity__gte=1)
                ),
                name="checkout_quote_line_amounts_nonnegative",
            ),
        ]


class CheckoutQuoteComponent(models.Model):
    """Immutable BOM fact captured when the server creates a quote."""

    quote_line = models.ForeignKey(
        CheckoutQuoteLine,
        on_delete=models.CASCADE,
        related_name="component_snapshots",
    )
    part_type_code = models.CharField(max_length=50)
    part_id_snapshot = models.PositiveBigIntegerField()
    part_code = models.CharField(max_length=50)
    part_variant_id_snapshot = models.PositiveBigIntegerField()
    part_variant_sku = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["quote_line", "part_type_code"],
                name="unique_checkout_quote_component_slot",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="checkout_quote_component_quantity_positive",
            ),
        ]


class InventoryReservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMMITTED = "committed", "Committed"
        RELEASED = "released", "Released"
        REVIEW_REQUIRED = "review_required", "Review Required"

    attempt = models.ForeignKey(
        CheckoutAttempt,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="inventory_reservations",
    )
    preorder_batch = models.ForeignKey(
        "products.PreorderBatch",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="inventory_reservations",
    )
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    released_at = models.DateTimeField(blank=True, null=True)
    committed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "variant", "preorder_batch"],
                name="unique_inventory_reservation_variant_batch",
                nulls_distinct=False,
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="inventory_reservation_quantity_positive",
            ),
        ]

class InventoryAllocation(models.Model):
    class Status(models.TextChoices):
        ALLOCATED = "allocated", "Allocated"
        REVIEW_REQUIRED = "review_required", "Review Required"
        REFUND_PENDING = "refund_pending", "Refund Pending"
        REFUNDED = "refunded", "Refunded"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="inventory_allocation",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        db_index=True,
    )
    review_due_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
    )
    refund_initiated_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    customer_notified_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    customer_notified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["review_due_at", "created_at"]

    @property
    def blocks_fulfillment(self):
        return self.status in [
            self.Status.REVIEW_REQUIRED,
            self.Status.REFUND_PENDING,
        ]

    @property
    def is_overdue(self):
        if (
            self.status == self.Status.ALLOCATED
            or self.review_due_at is None
        ):
            return False

        staff_action_incomplete = (
            self.refund_initiated_at is None
            or self.customer_notified_at is None
        )
        return staff_action_incomplete and timezone.now() > self.review_due_at

    def __str__(self):
        return f"Inventory allocation for Order #{self.order_id}: {self.status}"


class InventoryAllocationItem(models.Model):
    allocation = models.ForeignKey(
        InventoryAllocation,
        on_delete=models.CASCADE,
        related_name="items",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="inventory_allocation_items",
    )
    fulfillment_type = models.CharField(
        max_length=20,
        choices=Order.FulfillmentType.choices,
        default=Order.FulfillmentType.STOCKED,
    )
    preorder_batch = models.ForeignKey(
        "products.PreorderBatch",
        on_delete=models.PROTECT,
        related_name="inventory_allocation_items",
        blank=True,
        null=True,
    )
    sku = models.CharField(max_length=50)
    required_quantity = models.PositiveIntegerField()
    allocated_quantity = models.PositiveIntegerField(default=0)
    variant_available_before = models.PositiveIntegerField()
    variant_available_after = models.PositiveIntegerField()
    batch_available_before = models.PositiveIntegerField(blank=True, null=True)
    batch_available_after = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["variant_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["allocation", "variant"],
                name="unique_allocation_variant",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    allocated_quantity__lte=models.F("required_quantity")
                ),
                name="allocation_quantity_not_over_required",
            ),
        ]

    def __str__(self):
        return f"{self.sku}: {self.allocated_quantity}/{self.required_quantity}"


class Payment(models.Model):
    class Status(models.TextChoices):
        REQUIRES_PAYMENT_METHOD = (
            "requires_payment_method",
            "Requires Payment Method",
        )
        REQUIRES_CONFIRMATION = (
            "requires_confirmation",
            "Requires Confirmation",
        )
        REQUIRES_ACTION = (
            "requires_action",
            "Requires Action",
        )
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        CANCELED = "canceled", "Canceled"
        FAILED = "failed", "Failed"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PROCESSING,
        db_index=True,
    )
    raw_response = models.JSONField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order #{self.order_id} - {self.status}"


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REQUIRES_ACTION = "requires_action", "Requires Action"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELED = "canceled", "Canceled"

    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name="refunds",
    )
    stripe_refund_id = models.CharField(
        max_length=255,
        unique=True,
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        db_index=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    currency = models.CharField(max_length=10)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        db_index=True,
    )
    reason = models.CharField(max_length=100, blank=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    stripe_created_at = models.DateTimeField()
    raw_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-stripe_created_at"]

    def __str__(self):
        return f"Refund {self.stripe_refund_id}: {self.status}"

class StripeEvent(models.Model):
    stripe_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255)
    provider_created_at = models.DateTimeField(blank=True, null=True)
    api_version = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True)
    processing_attempts = models.PositiveSmallIntegerField(default=0)
    error_code = models.CharField(max_length=100, blank=True)
    processed = models.BooleanField(default=False)
    # Retained temporarily for expand/contract migration compatibility. New
    # events must use the bounded audit fields above instead of raw payloads.
    raw_event = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Stripe Event {self.event_type} - {self.stripe_event_id}"

class AppendOnlyStatusEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Order status history is append-only.")

    def delete(self):
        raise ValidationError("Order status history is append-only.")


class OrderStatusEvent(models.Model):
    class Source(models.TextChoices):
        SYSTEM = "system", "System"
        STRIPE = "stripe", "Stripe"
        SHIPMENT = "shipment", "Shipment"
        REFUND = "refund", "Refund"
        ADMIN = "admin", "Admin"
        MIGRATION = "migration", "Migration"
        LEGACY = "legacy", "Legacy"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="status_events"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="order_status_events",
    )

    from_status = models.CharField(
        max_length=30,
        blank=True,
    )

    to_status = models.CharField(
        max_length=30,
    )

    note = models.TextField(
        blank=True,
    )

    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.SYSTEM,
    )

    reason = models.CharField(max_length=100)

    external_reference = models.CharField(max_length=255, blank=True)

    internal_detail = models.TextField(blank=True)

    customer_message = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    objects = AppendOnlyStatusEventQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Order status history is append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Order status history is append-only.")

    def __str__(self):
        return (
            f"Order #{self.order_id}: "
            f"{self.from_status or 'new'} -> {self.to_status}"
        )
