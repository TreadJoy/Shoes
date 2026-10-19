from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class HeritageCourtComponentMigrationTests(TransactionTestCase):
    migrate_from = ("products", "0013_product_product_price_nonnegative_and_more")
    migrate_to = ("products", "0015_heritage_court_component_taxonomy")

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def _create_legacy_part_references(self, apps):
        PartType = apps.get_model("products", "PartType")
        Part = apps.get_model("products", "Part")
        PartVariant = apps.get_model("products", "PartVariant")
        ProductVariantComponent = apps.get_model(
            "products", "ProductVariantComponent"
        )
        CompatibilityGroup = apps.get_model("products", "CompatibilityGroup")
        Product = apps.get_model("products", "Product")
        ProductVariant = apps.get_model("products", "ProductVariant")
        group = CompatibilityGroup.objects.create(
            code="MIGRATION-TEST-090-STD",
            name="Migration reference test group",
            platform_code="MIGRATION-TEST",
            platform_version=1,
            internal_size_code="S090",
            width_code="STD",
        )
        product = Product.objects.create(
            name="Migration reference test shoe",
            slug="migration-reference-test-shoe",
            price="100.00",
        )
        variant = ProductVariant.objects.create(
            product=product,
            compatibility_group=group,
            sku="MIGRATION-TEST-090-BLK",
            size="9",
            color="Black",
        )
        part_ids = {}
        component_ids = {}
        for code in (
            "TONGUE",
            "LOGO",
            "SOLE",
            "OUTER_SHELL",
            "BACK_PANEL",
            "LACES",
        ):
            part = Part.objects.create(
                part_type=PartType.objects.get(code=code),
                code=f"LEGACY-{code}",
                name=f"Legacy {code}",
            )
            part_ids[code] = part.pk
            part_variant = PartVariant.objects.create(
                part=part,
                compatibility_group=group,
                sku=f"MIGRATION-{code}-090",
            )
            component = ProductVariantComponent.objects.create(
                product_variant=variant,
                part_type=PartType.objects.get(code=code),
                part_variant=part_variant,
            )
            component_ids[code] = component.pk
        return part_ids, component_ids

    def _ensure_historical_part_types(self, apps):
        PartType = apps.get_model("products", "PartType")
        legacy_types = (
            ("TONGUE", "Tongue", "Removable upper component positioned beneath the laces.", 10),
            ("LOGO", "Logo", "Removable decorative or branded logo component.", 20),
            ("SOLE", "Sole", "Removable lower component that interfaces with the ground.", 30),
            ("OUTER_SHELL", "Outer Shell", "Removable exterior body or upper shell component.", 40),
            ("BACK_PANEL", "Back Panel", "Removable rear exterior panel of the shoe.", 50),
            ("LACES", "Laces", "Removable fastening lace set.", 60),
        )
        for code, name, description, display_order in legacy_types:
            PartType.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "display_order": display_order,
                    "is_active": True,
                },
            )

    def test_migration_seeds_seven_types_and_preserves_legacy_references(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([self.migrate_from]).apps
        PartType = old_apps.get_model("products", "PartType")
        Part = old_apps.get_model("products", "Part")

        self._ensure_historical_part_types(old_apps)
        legacy_part_ids, legacy_component_ids = self._create_legacy_part_references(
            old_apps
        )

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        new_apps = executor.loader.project_state([self.migrate_to]).apps
        NewPartType = new_apps.get_model("products", "PartType")
        NewPart = new_apps.get_model("products", "Part")
        NewProductVariantComponent = new_apps.get_model(
            "products", "ProductVariantComponent"
        )

        active_types = list(
            NewPartType.objects.filter(is_active=True)
            .order_by("display_order", "code")
            .values_list(
                "code",
                "name",
                "description",
                "display_order",
                "interchangeability_status",
            )
        )
        self.assertEqual(
            active_types,
            [
                (
                    "FRONT_SHELL",
                    "Front Shell",
                    "Visual group identified as the front shell in the current prototype. Attachment and removal mechanics are unverified.",
                    10,
                    "unverified",
                ),
                (
                    "BOOTIE_AND_SOLE",
                    "Bootie and Sole",
                    "The bootie and sole stay together as one visual group, designated permanent in the current prototype.",
                    20,
                    "permanent",
                ),
                (
                    "TONGUE",
                    "Tongue",
                    "Visual group identified as the tongue in the current prototype. Attachment and removal mechanics are unverified.",
                    30,
                    "unverified",
                ),
                (
                    "LACES",
                    "Laces",
                    "Visual group identified as the laces in the current prototype. Interchangeability is unverified.",
                    40,
                    "unverified",
                ),
                (
                    "BACK_PANEL",
                    "Back Panel",
                    "Visual group identified as the back panel in the current prototype. Attachment and removal mechanics are unverified.",
                    50,
                    "unverified",
                ),
                (
                    "LOGO_HOLDER",
                    "Logo Holder",
                    "Visual group identified as the logo holder in the current prototype. Attachment and removal mechanics are unverified.",
                    60,
                    "unverified",
                ),
                (
                    "BACK_LOOP",
                    "Back Loop",
                    "Visual group identified as the back loop in the current prototype. Its function and interchangeability are unverified.",
                    70,
                    "unverified",
                ),
            ],
        )
        for code in ("OUTER_SHELL", "LOGO", "SOLE"):
            with self.subTest(legacy_code=code):
                self.assertFalse(NewPartType.objects.get(code=code).is_active)
        for code in ("TONGUE", "LACES", "BACK_PANEL"):
            with self.subTest(reused_code=code):
                self.assertTrue(NewPartType.objects.get(code=code).is_active)
        for code, part_id in legacy_part_ids.items():
            with self.subTest(reference_code=code):
                self.assertEqual(
                    NewPart.objects.get(pk=part_id).part_type.code,
                    code,
                )
        for code, component_id in legacy_component_ids.items():
            with self.subTest(component_reference_code=code):
                self.assertEqual(
                    NewProductVariantComponent.objects.get(
                        pk=component_id
                    ).part_type.code,
                    code,
                )

    def test_reverse_restores_legacy_types_and_deactivates_new_types(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        new_apps = executor.loader.project_state([self.migrate_to]).apps
        legacy_part_ids, legacy_component_ids = self._create_legacy_part_references(
            new_apps
        )

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([self.migrate_from]).apps
        OldPartType = old_apps.get_model("products", "PartType")
        OldPart = old_apps.get_model("products", "Part")
        OldProductVariantComponent = old_apps.get_model(
            "products", "ProductVariantComponent"
        )

        for code in (
            "TONGUE",
            "LOGO",
            "SOLE",
            "OUTER_SHELL",
            "BACK_PANEL",
            "LACES",
        ):
            with self.subTest(legacy_code=code):
                self.assertTrue(OldPartType.objects.get(code=code).is_active)
                self.assertEqual(
                    OldPart.objects.get(pk=legacy_part_ids[code]).part_type.code,
                    code,
                )
                self.assertEqual(
                    OldProductVariantComponent.objects.get(
                        pk=legacy_component_ids[code]
                    ).part_type.code,
                    code,
                )

        for code in (
            "FRONT_SHELL",
            "BOOTIE_AND_SOLE",
            "LOGO_HOLDER",
            "BACK_LOOP",
        ):
            with self.subTest(new_code=code):
                self.assertFalse(OldPartType.objects.get(code=code).is_active)
