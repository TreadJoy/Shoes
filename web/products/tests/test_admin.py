from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from web.products.models import CompatibilityGroup, Product, ProductVariant


class ProductAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="product-admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin_user)
        self.compatibility_group = CompatibilityGroup.objects.create(
            code="TJ-CORE-V1-S090-STD",
            name="Core V1 Size 9 Standard",
            platform_code="TJ-CORE",
            platform_version=1,
            internal_size_code="S090",
            width_code="STD",
        )

    def test_product_add_page_includes_variant_compatibility_group(self):
        response = self.client.get(reverse("admin:products_product_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'name="variants-0-compatibility_group"',
        )

    def test_product_and_first_variant_can_be_created_together(self):
        response = self.client.post(
            reverse("admin:products_product_add"),
            data={
                "name": "TreadJoy Test Shoe",
                "slug": "treadjoy-test-shoe",
                "description": "Admin creation regression test.",
                "price": "100.00",
                "sale_price": "",
                "audience": "unisex",
                "category": "shoes",
                "is_active": "on",
                "variants-TOTAL_FORMS": "1",
                "variants-INITIAL_FORMS": "0",
                "variants-MIN_NUM_FORMS": "0",
                "variants-MAX_NUM_FORMS": "1000",
                "variants-0-id": "",
                "variants-0-sku": "TJ-ADMIN-090-BLK",
                "variants-0-size": "9",
                "variants-0-compatibility_group": str(
                    self.compatibility_group.pk
                ),
                "variants-0-color": "Black",
                "variants-0-stock_quantity": "12",
                "variants-0-price_override": "",
                "variants-0-is_active": "on",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(slug="treadjoy-test-shoe")
        variant = ProductVariant.objects.get(product=product)
        self.assertEqual(product.price, Decimal("100.00"))
        self.assertEqual(variant.sku, "TJ-ADMIN-090-BLK")
        self.assertEqual(variant.compatibility_group, self.compatibility_group)
        self.assertEqual(variant.stock_quantity, 12)
