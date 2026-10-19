from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from web.products.admin import (
    PartTypeAdmin,
    ProductVariantComponentAdmin,
    ProductVariantComponentInline,
)
from web.products.models import (
    CompatibilityGroup,
    Part,
    PartType,
    PartVariant,
    Product,
    ProductVariant,
    ProductVariantComponent,
)
from web.products.services import (
    HERITAGE_COURT_COMPONENTS,
    HERITAGE_COURT_COMPONENT_CODES,
)


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

    def test_active_heritage_component_removal_has_a_field_specific_admin_error(self):
        part_types = {}
        for order, (code, name, description, status) in enumerate(
            HERITAGE_COURT_COMPONENTS,
            start=1,
        ):
            part_types[code], _ = PartType.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "display_order": order * 10,
                    "interchangeability_status": status,
                    "is_active": True,
                },
            )
        product = Product.objects.create(
            name="Heritage Court admin test",
            slug="heritage-court-admin-test",
            price=Decimal("100.00"),
            component_standard=Product.ComponentStandard.HERITAGE_COURT_V1,
        )
        variant = ProductVariant.objects.create(
            product=product,
            compatibility_group=self.compatibility_group,
            sku="HC-ADMIN-090-BLK",
            size="9",
            color="Black",
            is_active=False,
        )
        for index, code in enumerate(HERITAGE_COURT_COMPONENT_CODES):
            part = Part.objects.create(
                part_type=part_types[code],
                code=f"HC-ADMIN-{code}",
                name=f"Admin {code}",
            )
            part_variant = PartVariant.objects.create(
                part=part,
                compatibility_group=self.compatibility_group,
                sku=f"HC-ADMIN-{code}-090",
            )
            ProductVariantComponent.objects.create(
                product_variant=variant,
                part_type=part_types[code],
                part_variant=part_variant,
            )
        variant.is_active = True
        variant.save()

        inline = ProductVariantComponentInline(ProductVariant, admin.site)
        request = RequestFactory().get("/admin/")
        request.user = self.admin_user
        formset_class = inline.get_formset(
            request,
            variant,
        )
        unbound_formset = formset_class(instance=variant)
        prefix = unbound_formset.prefix
        data = {
            f"{prefix}-TOTAL_FORMS": str(unbound_formset.total_form_count()),
            f"{prefix}-INITIAL_FORMS": str(unbound_formset.initial_form_count()),
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1000",
        }
        for index, form in enumerate(unbound_formset.forms):
            row = f"{prefix}-{index}"
            component = form.instance
            data.update(
                {
                    f"{row}-id": str(component.pk),
                    f"{row}-product_variant": str(variant.pk),
                    f"{row}-part_type": str(component.part_type_id),
                    f"{row}-part_variant": str(component.part_variant_id),
                    f"{row}-quantity": str(component.quantity),
                }
            )
        data[f"{prefix}-0-DELETE"] = "on"

        bound_formset = formset_class(data, instance=variant)

        self.assertFalse(bound_formset.is_valid())
        self.assertIn("part_type", bound_formset.forms[0].errors)
        self.assertIn(
            "cannot be removed while the variant is active",
            str(bound_formset.forms[0].errors["part_type"]),
        )
        self.assertEqual(variant.components.count(), 7)

    def test_bulk_admin_delete_surfaces_protected_part_type_error(self):
        part_types = {}
        for order, (code, name, description, status) in enumerate(
            HERITAGE_COURT_COMPONENTS,
            start=1,
        ):
            part_types[code], _ = PartType.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "display_order": order * 10,
                    "interchangeability_status": status,
                    "is_active": True,
                },
            )
        product = Product.objects.create(
            name="Protected admin shoe",
            slug="protected-admin-shoe",
            price=Decimal("100.00"),
            component_standard=Product.ComponentStandard.HERITAGE_COURT_V1,
        )
        variant = ProductVariant.objects.create(
            product=product,
            compatibility_group=self.compatibility_group,
            sku="HC-ADMIN-090-DELETE",
            size="9",
            color="Black",
            is_active=False,
        )
        components = {}
        for code in HERITAGE_COURT_COMPONENT_CODES:
            part = Part.objects.create(
                part_type=part_types[code],
                code=f"HC-ADMIN-DELETE-{code}",
                name=f"Admin delete test {code}",
            )
            part_variant = PartVariant.objects.create(
                part=part,
                compatibility_group=self.compatibility_group,
                sku=f"HC-ADMIN-DELETE-{code}-090",
            )
            components[code] = ProductVariantComponent.objects.create(
                product_variant=variant,
                part_type=part_types[code],
                part_variant=part_variant,
            )
        variant.is_active = True
        variant.save()
        component = components["LACES"]

        request = RequestFactory().post(
            "/admin/delete-selected/",
            data={"post": "yes"},
        )
        request.user = self.admin_user
        request.session = {}
        request._messages = FallbackStorage(request)
        model_admin = ProductVariantComponentAdmin(
            ProductVariantComponent,
            admin.site,
        )
        model_admin.delete_selected_components(
            request,
            ProductVariantComponent.objects.filter(pk=component.pk),
        )

        self.assertTrue(ProductVariantComponent.objects.filter(pk=component.pk).exists())
        self.assertTrue(
            any(
                message.level_tag == "error"
                and "Part type:" in message.message
                and "cannot be removed while the variant is active"
                in message.message
                for message in get_messages(request)
            )
        )

    def test_canonical_part_type_delete_is_confirmed_and_reported_in_admin(self):
        part_type, _ = PartType.objects.update_or_create(
            code="FRONT_SHELL",
            defaults={
                "name": "Front Shell",
                "description": "Canonical prototype component.",
                "display_order": 10,
                "interchangeability_status": "unverified",
                "is_active": True,
            },
        )
        request = RequestFactory().post(
            "/admin/delete-selected/",
            data={"post": "yes"},
        )
        request.user = self.admin_user
        request.session = {}
        request._messages = FallbackStorage(request)
        model_admin = PartTypeAdmin(PartType, admin.site)

        model_admin.delete_selected_part_types(
            request,
            PartType.objects.filter(pk=part_type.pk),
        )

        self.assertTrue(PartType.objects.filter(pk=part_type.pk).exists())
        self.assertTrue(
            any(
                message.level_tag == "error"
                and "Part type:" in message.message
                and "cannot be deleted" in message.message
                for message in get_messages(request)
            )
        )
