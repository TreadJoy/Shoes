from django.contrib import admin
from .models import Product, ProductVariant

class ProductVariantInLine(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "sku",
        "size",
        "color",
        "stock_quantity",
        "price_override",
        "is_active",
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "audience",
        "price",
        "sale_price",
        "total_stock_display",
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
        "slug",
    )
    prepopulated_fields = {
        "slug": ("name",)
    }
    inlines = [ProductVariantInLine]

    @admin.display(description="Total Variant Stock")
    def total_stock_display(self, obj):
        return obj.total_stock()

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "product",
        "size",
        "color",
        "stock_quantity",
        "price_override",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "is_active",
        "color",
        "product",
    )
    search_fields = (
        "sku",
        "product__name",
        "size",
        "color",
    )
    list_select_related = ("product",)