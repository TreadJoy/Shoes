from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "audience",
        "price",
        "sale_price",
        "stock_quantity",
        "is_active",
        "is_featured",
    )
    list_filter = (
        "category",
        "audience",
        "is_active",
        "is_featured",
    )
    search_fields = (
        "name",
        "description",
    )
    prepopulated_fields = {
        "slug": ("name",)
    }