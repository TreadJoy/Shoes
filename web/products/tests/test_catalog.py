from decimal import Decimal
from unittest import skipIf, skipUnless
from unittest.mock import patch

from django.conf import settings
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
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
            audience="men",
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
        self.womens_product = Product.objects.create(
            name="City Shoe",
            slug="city-shoe",
            description="A lightweight city option.",
            price=Decimal("95.00"),
            audience="women",
        )

    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce product pricing")
    def test_list_only_shows_active_products_and_current_product_price(self):
        response = self.client.get(reverse("products:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, "$80.00")
        self.assertNotContains(response, self.inactive_product.name)

    def test_catalog_query_count_is_bounded_as_variants_increase(self):
        for product_number in range(4):
            product = Product.objects.create(
                name=f"Query Budget Shoe {product_number}",
                slug=f"query-budget-shoe-{product_number}",
                price=Decimal("100.00"),
            )
            for variant_number in range(3):
                ProductVariant.objects.create(
                    product=product,
                    sku=f"TJ-QUERY-{product_number}-{variant_number}",
                    size=str(variant_number + 7),
                    color="Black",
                    stock_quantity=3,
                )

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse("products:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(queries), 8)

    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce product-detail behavior")
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

    def test_list_filters_by_audience(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"audience": "women"},
        )

        self.assertContains(response, self.womens_product.name)
        self.assertNotContains(response, self.product.name)

    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce sale merchandising")
    def test_list_filters_sale_products(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"sale": "1"},
        )

        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.womens_product.name)

    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce product availability")
    def test_list_labels_products_without_available_variants_as_sold_out(self):
        response = self.client.get(reverse("products:product_list"))

        self.assertContains(response, "product-badge product-badge-sold-out")
        self.assertContains(response, "Sold Out")

    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce sale merchandising")
    def test_list_labels_sale_products(self):
        response = self.client.get(reverse("products:product_list"))

        self.assertContains(response, "product-badge product-badge-sale")

    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce variant search")
    def test_list_searches_product_and_variant_details(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Black"},
        )

        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.womens_product.name)

    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce variant selection")
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

    @skipIf(settings.IS_COMMERCE_MODE, "Research product-preview behavior")
    def test_research_detail_hides_purchase_controls_and_invites_feedback(self):
        response = self.client.get(
            reverse("products:product_detail", args=[self.product.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Research Preview")
        self.assertContains(response, "Explore the product direction")
        self.assertContains(response, "Take the Survey")
        self.assertNotContains(response, "Add to Cart")
        self.assertNotContains(response, "Black")
        self.assertNotContains(response, "Size 9")
        self.assertNotContains(response, "Sold Out")
        self.assertNotContains(response, "Preorder")
        self.assertNotContains(response, "$")

    @skipIf(settings.IS_COMMERCE_MODE, "Research product-preview behavior")
    def test_research_list_uses_preview_language_without_sale_urgency(self):
        response = self.client.get(reverse("products:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product Preview")
        self.assertContains(response, "View Product Preview")
        self.assertNotContains(response, "product-badge product-badge-sale")
        self.assertNotContains(response, "Add to Cart")
        self.assertNotContains(response, "$")
        self.assertNotContains(response, "Sold Out")
        self.assertNotContains(response, "Preorder")
        self.assertNotContains(response, "available")

    @skipIf(settings.IS_COMMERCE_MODE, "Research product-preview behavior")
    def test_research_product_pages_do_not_evaluate_commerce_availability(self):
        with patch(
            "web.products.views.variant_availability",
            side_effect=AssertionError("research pages must not inspect availability"),
        ), patch(
            "web.products.views._price_summary",
            side_effect=AssertionError("research pages must not inspect prices"),
        ):
            list_response = self.client.get(reverse("products:product_list"))
            detail_response = self.client.get(
                reverse("products:product_detail", args=[self.product.slug])
            )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, self.product.description)
        self.assertNotContains(detail_response, "80.00")
        self.assertNotContains(detail_response, "100.00")
        self.assertTrue(
            {"price", "sale_price"}.issubset(
                detail_response.context["product"].get_deferred_fields()
            )
        )

    @skipIf(settings.IS_COMMERCE_MODE, "Research product-preview behavior")
    def test_research_ignores_commerce_sale_filter(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"sale": "1"},
        )

        self.assertContains(response, self.product.name)
        self.assertContains(response, self.womens_product.name)

    @skipIf(settings.IS_COMMERCE_MODE, "Research empty-catalog behavior")
    def test_research_empty_catalog_invites_survey_without_product_claims(self):
        Product.objects.all().delete()

        response = self.client.get(reverse("products:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product previews are being prepared.")
        self.assertContains(response, "Tell us what belongs here")
        self.assertContains(response, 'href="/survey/"')
        self.assertNotContains(response, "No Matches Yet")
        self.assertNotContains(response, "Add to Cart")
        self.assertNotContains(response, "$80.00")
