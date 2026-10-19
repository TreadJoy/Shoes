from decimal import Decimal
from unittest import SkipTest

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, SimpleTestCase, TestCase
from django.urls import NoReverseMatch, resolve, reverse

if not settings.IS_COMMERCE_MODE:
    raise SkipTest("Cart tests require the commerce deployment mode.")

from web.cart.models import Cart, CartItem
from web.cart.services import CartMutationError, add_variant
from web.cart import views as cart_views
from web.products.models import Product, ProductVariant


class CartRouteTests(SimpleTestCase):
    def test_update_route_has_one_canonical_name_and_view(self):
        self.assertEqual(
            reverse("cart:update_cart_item", args=[17]),
            "/cart/update/17/",
        )
        self.assertIs(
            resolve("/cart/update/17/").func,
            cart_views.update_cart_item,
        )
        with self.assertRaises(NoReverseMatch):
            reverse("cart:add_to_cart_item", args=[17])


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
        self.assertEqual(
            response.redirect_chain[0][0],
            reverse("products:product_list"),
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

    def test_add_to_cart_rejects_an_incomplete_heritage_court_bom(self):
        product = Product.objects.create(
            name="Prototype Shoe",
            slug="prototype-shoe",
            price=Decimal("100.00"),
            component_standard="heritage_court_v1",
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku="TJ-PROTOTYPE-090-BLK",
            size="9",
            color="Black",
            stock_quantity=3,
            is_active=False,
        )
        ProductVariant.objects.filter(pk=variant.pk).update(is_active=True)
        cart = Cart.objects.create(session_key="prototype-incomplete-cart")

        with self.assertRaises(CartMutationError) as raised:
            add_variant(cart, variant.pk)

        self.assertEqual(
            str(raised.exception),
            "This product is not ready for purchase.",
        )
        self.assertEqual(raised.exception.product_slug, product.slug)
        self.assertFalse(CartItem.objects.filter(cart=cart).exists())

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

    def test_login_merges_guest_cart_and_reports_availability_reduction(self):
        self.variant.stock_quantity = 2
        self.variant.save(update_fields=["stock_quantity"])
        user = get_user_model().objects.create_user(
            username="merge-user",
            password="CorrectHorseBattery9!",
        )
        account_cart = Cart.objects.create(user=user)
        CartItem.objects.create(
            cart=account_cart,
            variant=self.variant,
            quantity=2,
        )

        self.add_item()
        response = self.client.post(
            reverse("account_login"),
            {
                "login": "merge-user",
                "password": "CorrectHorseBattery9!",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reduced Cart Shoe to 2")
        self.assertEqual(Cart.objects.filter(user=None).count(), 0)
        merged_item = CartItem.objects.get(cart=account_cart)
        self.assertEqual(merged_item.quantity, 2)
