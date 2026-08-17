from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from web.cart.models import Cart, CartItem
from web.products.models import Product, ProductVariant


class CartFlowTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Cart Shoe",
            slug="cart-shoe",
            price=Decimal("90.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TJ-CART-090-BLK",
            size="9",
            color="Black",
            stock_quantity=3,
        )

    def add_item(self, client=None):
        client = client or self.client
        return client.post(
            reverse("cart:add_to_cart"),
            {"variant_id": self.variant.pk},
        )

    def test_guest_can_add_increment_update_remove_and_clear_items(self):
        self.add_item()
        self.add_item()
        item = CartItem.objects.get()
        self.assertEqual(item.quantity, 2)

        response = self.client.post(
            reverse("cart:update_cart_item", args=[item.pk]),
            {"quantity": 3},
        )
        self.assertRedirects(response, reverse("cart:cart_detail"))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

        response = self.client.post(
            reverse("cart:remove_from_cart", args=[item.pk])
        )
        self.assertRedirects(response, reverse("cart:cart_detail"))
        self.assertFalse(CartItem.objects.exists())

        self.add_item()
        response = self.client.post(reverse("cart:clear_cart"))
        self.assertRedirects(response, reverse("cart:cart_detail"))
        self.assertFalse(CartItem.objects.exists())

    def test_cart_rejects_missing_unavailable_and_excess_quantity(self):
        response = self.client.post(
            reverse("cart:add_to_cart"),
            {},
            follow=True,
        )
        self.assertContains(response, "Please select a size and color.")
        self.assertFalse(CartItem.objects.exists())

        self.variant.stock_quantity = 0
        self.variant.save(update_fields=["stock_quantity"])
        response = self.add_item()
        self.assertRedirects(
            response,
            reverse("products:product_detail", args=[self.product.slug]),
        )
        self.assertFalse(CartItem.objects.exists())

        self.variant.stock_quantity = 1
        self.variant.save(update_fields=["stock_quantity"])
        self.add_item()
        response = self.add_item()
        self.assertRedirects(response, reverse("cart:cart_detail"))
        self.assertEqual(CartItem.objects.get().quantity, 1)

    def test_cart_item_mutation_is_scoped_to_current_cart(self):
        self.add_item()
        item = CartItem.objects.get()
        other_client = Client()
        other_client.get(reverse("cart:cart_detail"))

        update = other_client.post(
            reverse("cart:update_cart_item", args=[item.pk]),
            {"quantity": 2},
        )
        remove = other_client.post(
            reverse("cart:remove_from_cart", args=[item.pk])
        )

        self.assertEqual(update.status_code, 404)
        self.assertEqual(remove.status_code, 404)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_zero_quantity_removes_item(self):
        self.add_item()
        item = CartItem.objects.get()

        response = self.client.post(
            reverse("cart:update_cart_item", args=[item.pk]),
            {"quantity": 0},
        )

        self.assertRedirects(response, reverse("cart:cart_detail"))
        self.assertFalse(CartItem.objects.exists())

    def test_cart_item_string_uses_variant_product(self):
        self.add_item()

        self.assertEqual(str(CartItem.objects.get()), "1 x Cart Shoe")

