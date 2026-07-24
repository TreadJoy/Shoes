from django.db import models


class Product(models.Model):

    AUDIENCE_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("kids", "Kids"),
        ("unisex", "Unisex"),
    ]

    CATEGORY_CHOICES = [
        ("shoes", "Shoes"),
        ("socks", "Socks"),
        ("hats", "Hats"),
        ("accessories", "Accessories"),
    ]

    name = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        unique=True
    )
    description = models.TextField(
        blank=True
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    sale_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default="unisex"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="shoes"
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True
    )
    is_featured = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def current_price(self):
        if self.sale_price is not None:
            return self.sale_price

        return self.price

    def total_stock(self):
        result = self.variants.filter(
            is_active=True,
        ).aggregate(
            total=models.Sum("stock_quantity")
        )
        return result["total"] or 0

    def is_in_stock(self):
        return self.total_stock() > 0

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
    )
    size = models.CharField(
        max_length=20,
    )
    color = models.CharField(
        max_length=50,
    )
    stock_quantity = models.PositiveIntegerField(
        default=0
    )
    price_override = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "size", "color"],
                name="unique_product_size_color",
            ),
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name="variant_stock_nonnegative",
            ),
            models.CheckConstraint(
                check=(
                        models.Q(price_override__gte=0)
                        | models.Q(price_override__isnull=True)
                ),
                name="variant_price_override_nonnegative",
            ),
        ]
        ordering = ["product", "color", "size"]

    def current_price(self):
        if self.price_override is not None:
            return self.price_override

        return self.product.current_price()

    def __str__(self):
        return (
            f"{self.product.name} -"
            f"{self.color}, Size {self.size}"
        )