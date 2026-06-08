from django.db import models


class Product(models.Model):

    objects = None

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

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default="unisex")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="shoes")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def current_price(self):
        return self.sale_price if self.sale_price else self.price

    def __str__(self):
        return self.name