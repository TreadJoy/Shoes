from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

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
    component_bom_issues,
    validate_heritage_court_bom,
)


class HeritageCourtComponentStandardTests(TestCase):
    def setUp(self):
        self.part_counter = 0
        for order, (code, name, description, status) in enumerate(
            HERITAGE_COURT_COMPONENTS,
            start=1,
        ):
            PartType.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "display_order": order * 10,
                    "interchangeability_status": status,
                    "is_active": True,
                },
            )
        PartType.objects.update_or_create(
            code="OUTER_SHELL",
            defaults={
                "name": "Outer Shell",
                "description": "Legacy outer shell lookup row.",
                "display_order": 40,
                "interchangeability_status": PartType.InterchangeabilityStatus.UNVERIFIED,
                "is_active": False,
            },
        )
        self.group = CompatibilityGroup.objects.create(
            code="HC-TEST-090-STD",
            name="Heritage Court test size 9",
            platform_code="HC-TEST",
            platform_version=1,
            internal_size_code="S090",
            width_code="STD",
        )
        self.product = Product.objects.create(
            name="Heritage Court test",
            slug="heritage-court-test",
            price=Decimal("100.00"),
            component_standard=Product.ComponentStandard.HERITAGE_COURT_V1,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            compatibility_group=self.group,
            sku="HC-TEST-090-BLK",
            size="9",
            color="Black",
            stock_quantity=4,
            is_active=False,
        )

    def _assign(self, code):
        self.part_counter += 1
        part_type = PartType.objects.get(code=code)
        part = Part.objects.create(
            part_type=part_type,
            code=f"TEST-{code}-{self.part_counter}",
            name=f"Test {part_type.name}",
        )
        part_variant = PartVariant.objects.create(
            part=part,
            compatibility_group=self.group,
            sku=f"TEST-{code}-{self.part_counter}-090",
        )
        return ProductVariantComponent.objects.create(
            product_variant=self.variant,
            part_type=part_type,
            part_variant=part_variant,
        )

    def _complete_bom(self):
        return [self._assign(code) for code in HERITAGE_COURT_COMPONENT_CODES]

    def test_complete_bom_is_valid_and_canonical(self):
        self._complete_bom()

        validate_heritage_court_bom(self.variant)
        self.assertEqual(component_bom_issues(self.variant), {})
        self.assertEqual(
            list(
                self.variant.components.order_by("part_type__display_order")
                .values_list("part_type__code", flat=True)
            ),
            list(HERITAGE_COURT_COMPONENT_CODES),
        )

    def test_canonical_part_types_cannot_be_deleted(self):
        part_type = PartType.objects.get(code="LACES")

        with self.assertRaises(ValidationError):
            part_type.delete()
        with self.assertRaises(ValidationError):
            PartType.objects.filter(pk=part_type.pk).delete()

        self.assertTrue(PartType.objects.filter(pk=part_type.pk).exists())

    def test_each_missing_slot_is_reported_and_blocks_activation(self):
        for missing_code in HERITAGE_COURT_COMPONENT_CODES:
            with self.subTest(missing_code=missing_code):
                self.variant.components.all().delete()
                for code in HERITAGE_COURT_COMPONENT_CODES:
                    if code != missing_code:
                        self._assign(code)

                issues = component_bom_issues(self.variant)
                self.assertIn(missing_code, " ".join(issues.get("is_active", [])))
                self.variant.is_active = True
                with self.assertRaises(ValidationError) as raised:
                    self.variant.save()
                self.assertIn("is_active", raised.exception.message_dict)
                self.variant.is_active = False

    def test_applying_the_standard_cannot_leave_an_active_variant_incomplete(self):
        product = Product.objects.create(
            name="Existing active shoe",
            slug="existing-active-shoe",
            price=Decimal("80.00"),
        )
        ProductVariant.objects.create(
            product=product,
            sku="EXISTING-ACTIVE-090-BLK",
            size="9",
            color="Black",
            is_active=True,
        )

        product.component_standard = Product.ComponentStandard.HERITAGE_COURT_V1
        with self.assertRaises(ValidationError) as raised:
            product.save()

        self.assertIn("component_standard", raised.exception.message_dict)
        product.refresh_from_db()
        self.assertEqual(product.component_standard, "")

    def test_reassigning_an_active_variant_to_heritage_court_requires_a_ready_bom(self):
        generic_product = Product.objects.create(
            name="Existing active shoe",
            slug="existing-active-shoe-reassignment",
            price=Decimal("80.00"),
        )
        variant = ProductVariant.objects.create(
            product=generic_product,
            sku="EXISTING-ACTIVE-090-REASSIGN",
            size="9",
            color="Black",
            is_active=True,
        )

        variant.product = self.product
        with self.assertRaises(ValidationError) as raised:
            variant.save()

        self.assertIn("is_active", raised.exception.message_dict)
        variant.refresh_from_db()
        self.assertEqual(variant.product_id, generic_product.pk)

    def test_legacy_or_unexpected_component_type_is_rejected(self):
        outer_shell = PartType.objects.get(code="OUTER_SHELL")
        part = Part.objects.create(
            part_type=outer_shell,
            code="TEST-LEGACY-OUTER",
            name="Legacy outer shell",
        )
        part_variant = PartVariant.objects.create(
            part=part,
            compatibility_group=self.group,
            sku="TEST-LEGACY-OUTER-090",
        )

        component = ProductVariantComponent(
            product_variant=self.variant,
            part_type=outer_shell,
            part_variant=part_variant,
        )
        with self.assertRaises(ValidationError) as raised:
            component.full_clean()
        self.assertIn("part_type", raised.exception.message_dict)

        unexpected_type = PartType.objects.create(
            code="UNEXPECTED_TEST", name="Unexpected test type"
        )
        unexpected_part = Part.objects.create(
            part_type=unexpected_type,
            code="TEST-UNEXPECTED",
            name="Unexpected test part",
        )
        unexpected_variant = PartVariant.objects.create(
            part=unexpected_part,
            compatibility_group=self.group,
            sku="TEST-UNEXPECTED-090",
        )
        unexpected_component = ProductVariantComponent(
            product_variant=self.variant,
            part_type=unexpected_type,
            part_variant=unexpected_variant,
        )
        with self.assertRaises(ValidationError) as raised:
            unexpected_component.full_clean()
        self.assertIn("part_type", raised.exception.message_dict)

    def test_existing_component_type_and_compatibility_validation_remains(self):
        tongue = PartType.objects.get(code="TONGUE")
        laces = PartType.objects.get(code="LACES")
        part = Part.objects.create(
            part_type=tongue,
            code="TEST-MISMATCHED-TONGUE",
            name="Mismatched tongue",
        )
        part_variant = PartVariant.objects.create(
            part=part,
            compatibility_group=self.group,
            sku="TEST-MISMATCHED-TONGUE-090",
        )
        wrong_type = ProductVariantComponent(
            product_variant=self.variant,
            part_type=laces,
            part_variant=part_variant,
        )
        with self.assertRaises(ValidationError) as raised:
            wrong_type.full_clean()
        self.assertIn("part_variant", raised.exception.message_dict)

        other_group = CompatibilityGroup.objects.create(
            code="HC-TEST-090-WIDE",
            name="Heritage Court test size 9 wide",
            platform_code="HC-TEST",
            platform_version=1,
            internal_size_code="S090",
            width_code="WIDE",
        )
        incompatible_variant = PartVariant.objects.create(
            part=part,
            compatibility_group=other_group,
            sku="TEST-MISMATCHED-TONGUE-WIDE",
        )
        wrong_group = ProductVariantComponent(
            product_variant=self.variant,
            part_type=tongue,
            part_variant=incompatible_variant,
        )
        with self.assertRaises(ValidationError) as raised:
            wrong_group.full_clean()
        self.assertIn("part_variant", raised.exception.message_dict)

    def test_inactive_related_rows_make_bom_unready(self):
        self._complete_bom()
        assignment = self.variant.components.select_related(
            "part_type",
            "part_variant__part",
            "part_variant__compatibility_group",
        ).first()
        related_rows = (
            assignment.part_type,
            assignment.part_variant.part,
            assignment.part_variant,
            assignment.part_variant.compatibility_group,
        )
        for related_row in related_rows:
            with self.subTest(model=type(related_row).__name__):
                related_row.is_active = False
                related_row.save(update_fields=["is_active"])

                self.assertTrue(component_bom_issues(self.variant))
                with self.assertRaises(ValidationError):
                    validate_heritage_court_bom(self.variant)

                related_row.is_active = True
                related_row.save(update_fields=["is_active"])

    def test_required_component_cannot_be_removed_while_variant_is_active(self):
        self._complete_bom()
        self.variant.is_active = True
        self.variant.save()

        component = self.variant.components.first()
        another_variant = ProductVariant.objects.create(
            product=self.product,
            compatibility_group=self.group,
            sku="HC-TEST-090-RED",
            size="9",
            color="Red",
            is_active=False,
        )
        component.product_variant = another_variant
        with self.assertRaises(ValidationError):
            component.save()
        component.refresh_from_db()
        self.assertEqual(component.product_variant_id, self.variant.pk)

        with self.assertRaises(ValidationError):
            component.delete()
        self.assertEqual(self.variant.components.count(), 7)
        with self.assertRaises(ValidationError):
            self.variant.components.all().delete()
        self.assertEqual(self.variant.components.count(), 7)

    def test_non_heritage_products_keep_existing_unconstrained_behavior(self):
        generic_product = Product.objects.create(
            name="Generic Shoe",
            slug="generic-shoe",
            price=Decimal("80.00"),
        )
        generic_variant = ProductVariant.objects.create(
            product=generic_product,
            sku="GENERIC-090-BLK",
            size="9",
            color="Black",
            is_active=True,
        )
        self.assertTrue(generic_variant.is_active)
        self.assertEqual(generic_product.component_standard, "")
