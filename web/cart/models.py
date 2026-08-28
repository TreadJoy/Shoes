from django.conf import settings
from django.db import models
from web.products.models import ProductVariant


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="cart",
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, session_key__isnull=True)
                    | (
                        models.Q(user__isnull=True)
                        & models.Q(session_key__isnull=False)
                        & ~models.Q(session_key="")
                    )
                ),
                name="cart_exactly_one_principal",
            ),
            models.UniqueConstraint(
                fields=["session_key"],
                condition=(
                    models.Q(user__isnull=True)
                    & models.Q(session_key__isnull=False)
                    & ~models.Q(session_key="")
                ),
                name="unique_guest_cart_session",
            ),
        ]

    def total_price(self):
        return sum(
            item.subtotal()
            for item in self.items.select_related(
                "variant",
                "variant__product",
            )
        )

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest Cart {self.session_key}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="cart_items",
    )
    preorder_batch = models.ForeignKey(
        "products.PreorderBatch",
        on_delete=models.PROTECT,
        related_name="cart_items",
        blank=True,
        null=True,
    )
    quantity = models.PositiveIntegerField(
        default=1
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "variant"],
                name="unique_cart_variant",
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gte=1),
                name="cartitem_quantity_at_least_one",
            ),
        ]

    def unit_price(self):
        return self.variant.current_price()

    def line_total(self):
        return self.unit_price() * self.quantity

    def subtotal(self):
        return self.line_total()

    def __str__(self):
        return f"{self.quantity} x {self.variant.product.name}"
