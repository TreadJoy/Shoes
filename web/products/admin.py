from django.contrib import admin
from .models import (
    CompatibilityGroup,
    Part,
    PartType,
    PartVariant,
    Product,
    ProductVariant,
    ProductVariantComponent,
)

class ProductVariantComponentInline(admin.TabularInline):
    model = ProductVariantComponent
    extra = 0
    fields = (
        "part_type",
        "part_variant",
        "quantity",
    )
    autocomplete_fields = (
        "part_type",
        "part_variant",
    )
@admin.register(PartType)
class PartTypeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "display_order",
        "is_active",
        "updated_at",
    )
    list_editable = (
        "display_order",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
        "description",
    )
    ordering = (
        "display_order",
        "code",
    )


class PartVariantInline(admin.TabularInline):
    model = PartVariant
    extra = 0
    fields = (
        "sku",
        "compatibility_group",
        "stock_quantity",
        "is_active",
    )
    autocomplete_fields = (
        "compatibility_group",
    )


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "part_type",
        "color_name",
        "material",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "part_type",
        "is_active",
        "color_name",
    )
    search_fields = (
        "code",
        "name",
        "description",
        "material",
    )
    list_select_related = (
        "part_type",
    )
    autocomplete_fields = (
        "part_type",
    )
    inlines = [
        PartVariantInline,
    ]


@admin.register(PartVariant)
class PartVariantAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "part",
        "part_type_display",
        "compatibility_group",
        "stock_quantity",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "part__part_type",
        "compatibility_group",
        "is_active",
    )
    search_fields = (
        "sku",
        "part__code",
        "part__name",
        "compatibility_group__code",
    )
    list_select_related = (
        "part",
        "part__part_type",
        "compatibility_group",
    )
    autocomplete_fields = (
        "part",
        "compatibility_group",
    )

    @admin.display(
        description="Part type",
        ordering="part__part_type__name",
    )
    def part_type_display(self, obj):
        return obj.part.part_type.name

class ProductVariantInLine(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "sku",
        "size",
        "compatibility_group",
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

@admin.register(CompatibilityGroup)
class CompatibilityGroupAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "platform_code",
        "platform_version",
        "internal_size_code",
        "width_code",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "platform_code",
        "platform_version",
        "width_code",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
        "internal_size_code",
        "description",
    )
    ordering = (
        "platform_code",
        "platform_version",
        "internal_size_code",
        "width_code",
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "product",
        "size",
        "compatibility_group",
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
        "compatibility_group",
    )
    search_fields = (
        "sku",
        "product__name",
        "size",
        "color",
        "compatibility_group__code",
    )
    list_select_related = (
        "product",
        "compatibility_group",
    )
    inlines = [
        ProductVariantComponentInline,
    ]

@admin.register(ProductVariantComponent)
class ProductVariantComponentAdmin(admin.ModelAdmin):
    list_display = (
        "product_variant",
        "part_type",
        "part_variant",
        "quantity",
        "updated_at",
    )
    list_filter = (
        "part_type",
        "product_variant__compatibility_group",
    )
    search_fields = (
        "product_variant__sku",
        "product_variant__product__name",
        "part_variant__sku",
        "part_variant__part__code",
    )
    list_select_related = (
        "product_variant",
        "product_variant__product",
        "product_variant__compatibility_group",
        "part_type",
        "part_variant",
        "part_variant__part",
        "part_variant__compatibility_group",
    )
    autocomplete_fields = (
        "product_variant",
        "part_type",
        "part_variant",
    )
