
from django.conf import settings
from django.db import models
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
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending Payment"
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
    email = models.EmailField(
        blank=True
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
        db_index=True,
    )
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

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        previous_shipped_at = None
        previous_delivered_at = None

        if not is_new:
            previous = Shipment.objects.only(
                "shipped_at",
                "delivered_at",
            ).get(pk=self.pk)

            previous_shipped_at = previous.shipped_at
            previous_delivered_at = previous.delivered_at

            super().save(*args, **kwargs)

            if self.shipped_at and not previous_shipped_at:
                self.mark_order_shipped()

            if self.delivered_at and not previous_delivered_at:
                self.mark_order_delivered()

    def mark_order_shipped(self):
        order = self.order

        if order.status in [
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
            Order.Status.CANCELED,
        ]:
            return

        previous_status = order.status

        order.status = Order.Status.SHIPPED
        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        OrderStatusEvent.objects.create(
            order=order,
            from_status=previous_status,
            to_status=Order.Status.SHIPPED,
            note=f"Order marked shipped from shipment #{self.id}.",
        )

    def mark_order_delivered(self):
        order = self.order

        if order.status in [
            Order.Status.DELIVERED,
            Order.Status.CANCELED,
        ]:
            return

        previous_status = order.status

        order.status = Order.Status.DELIVERED
        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        OrderStatusEvent.objects.create(
            order=order,
            from_status=previous_status,
            to_status=Order.Status.DELIVERED,
            note=f"Order marked delivered from shipment #{self.id}.",
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

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    def calculate_line_total(self):
        return self.unit_price * self.quantity


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
        return f"Payment for Order #{self.id} - {self.status}"

class StripeEvent(models.Model):
    stripe_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255)
    processed = models.BooleanField(default=False)
    raw_event = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Stripe Event {self.event_type} - {self.stripe_id}"

class OrderStatusEvent(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_events"
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

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Order #{self.order_id}: "
            f"{self.from_status or 'new'} -> {self.to_status}"
        )