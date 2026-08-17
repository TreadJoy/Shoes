from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from web.products.models import Product, ProductVariant


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Everyday Shoe",
            slug="everyday-shoe",
            description="An active catalog product.",
            price=Decimal("100.00"),
            sale_price=Decimal("85.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TJ-EVERYDAY-090-BLK",
            size="9",
            color="Black",
            stock_quantity=3,
            price_override=Decimal("80.00"),
        )
        self.inactive_product = Product.objects.create(
            name="Hidden Shoe",
            slug="hidden-shoe",
            price=Decimal("75.00"),
            is_active=False,
        )

    def test_list_only_shows_active_products_and_current_product_price(self):
        response = self.client.get(reverse("products:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, "$85.00")
        self.assertNotContains(response, self.inactive_product.name)

    def test_detail_uses_variant_override_and_exposes_available_option(self):
        response = self.client.get(
            reverse("products:product_detail", args=[self.product.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Black")
        self.assertContains(response, "Size 9")
        self.assertContains(response, "$80.00")
        self.assertContains(response, "Add to Cart")

    def test_inactive_product_detail_is_not_public(self):
        response = self.client.get(
            reverse("products:product_detail", args=[self.inactive_product.slug])
        )

        self.assertEqual(response.status_code, 404)

    def test_inactive_and_sold_out_variants_are_not_selectable(self):
        self.variant.stock_quantity = 0
        self.variant.save(update_fields=["stock_quantity"])
        ProductVariant.objects.create(
            product=self.product,
            sku="TJ-EVERYDAY-100-BLU",
            size="10",
            color="Blue",
            stock_quantity=4,
            is_active=False,
        )

        response = self.client.get(
            reverse("products:product_detail", args=[self.product.slug])
        )

        self.assertContains(response, "Out of Stock")
        self.assertNotContains(response, "Add to Cart")
