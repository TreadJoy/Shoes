from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "session_key",
        "total_items",
        "total_price",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "session_key",
    )
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "product",
        "quantity",
        "size",
        "color",
        "subtotal",
        "added_at",
    )
    list_filter = (
        "size",
        "color",
        "added_at",
    )
    search_fields = (
        "product__name",
        "cart__user__username",
        "cart__session_key",
    )