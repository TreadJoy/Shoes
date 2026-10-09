import io
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, TestCase, override_settings
from PIL import Image

from web.core.context_processors import deployment_mode
from web.products.models import Product, ProductVariant


class DevelopmentLogoRenderingTests(TestCase):
    def test_non_debug_header_uses_the_text_wordmark(self):
        with override_settings(DEBUG=False):
            response = self.client.get("/")

        self.assertContains(response, 'class="brand-wordmark"')
        self.assertNotContains(response, "treadjoy-ai-logo.png")

    def test_debug_header_uses_local_logo_only_when_it_exists(self):
        with TemporaryDirectory() as temporary_media_root:
            media_root = Path(temporary_media_root)
            logo_path = media_root / "development" / "treadjoy-ai-logo.png"
            logo_path.parent.mkdir()
            logo_path.write_bytes(b"development-only-logo")

            with override_settings(DEBUG=True, IS_COMMERCE_MODE=True, MEDIA_ROOT=media_root):
                context = deployment_mode(RequestFactory().get("/"))

        self.assertEqual(context["development_logo_url"], "/media/development/treadjoy-ai-logo.png")

    def test_debug_research_header_never_uses_local_development_logo(self):
        with TemporaryDirectory() as temporary_media_root:
            media_root = Path(temporary_media_root)
            logo_path = media_root / "development" / "treadjoy-ai-logo.png"
            logo_path.parent.mkdir()
            logo_path.write_bytes(b"development-only-logo")

            with override_settings(DEBUG=True, IS_COMMERCE_MODE=False, MEDIA_ROOT=media_root):
                context = deployment_mode(RequestFactory().get("/"))

        self.assertEqual(context["development_logo_url"], "")

    def test_debug_header_falls_back_to_wordmark_without_local_logo(self):
        with TemporaryDirectory() as temporary_media_root:
            with override_settings(DEBUG=True, MEDIA_ROOT=Path(temporary_media_root)):
                response = self.client.get("/")

        self.assertContains(response, 'class="brand-wordmark"')
        self.assertNotContains(response, "treadjoy-ai-logo.png")


class ReleaseContentCommandTests(TestCase):
    def image_bytes(self, *, with_exif=False):
        output = io.BytesIO()
        image = Image.new("RGB", (1, 1), color="blue")
        save_kwargs = {"format": "JPEG"}
        if with_exif:
            exif = Image.Exif()
            exif[270] = "development metadata"
            save_kwargs["exif"] = exif
        image.save(output, **save_kwargs)
        return output.getvalue()

    def inventory_asset(self, path, content, **overrides):
        asset = {
            "id": "approved-asset",
            "path": path,
            "source_type": "licensed-photograph",
            "rights_status": "Licensed for approved TreadJoy public use.",
            "allowed_environments": ["commerce", "research"],
            "public_release": True,
            "approval_status": "approved",
            "sha256": hashlib.sha256(content).hexdigest(),
            "metadata_review": {
                "status": "clean",
                "notes": "Reviewed before release.",
            },
            "alt_text_decision": {
                "kind": "meaningful",
                "text": "Approved product image.",
            },
        }
        asset.update(overrides)
        return asset

    def write_inventory(self, base_dir, assets=(), content_surfaces=()):
        docs = base_dir / "docs"
        docs.mkdir()
        (docs / "release-content-inventory.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "assets": list(assets),
                    "content_surfaces": list(content_surfaces),
                    "blocked_catalog_slugs": ["treadjoy-test-shoe"],
                }
            ),
            encoding="utf-8",
        )

    def run_command(self, *arguments):
        output = io.StringIO()
        try:
            call_command("check_release_content", *arguments, stderr=output)
        except CommandError:
            return output.getvalue()
        return output.getvalue()

    def test_current_development_content_blocks_release(self):
        output = io.StringIO()

        with self.assertRaises(CommandError):
            call_command("check_release_content", stderr=output)

        self.assertIn("blocked-content-surface:homepage-development-media", output.getvalue())

    def test_private_poc_profile_accepts_known_placeholder_surfaces(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            self.write_inventory(
                base_dir,
                content_surfaces=[
                    {"id": surface_id, "public_release": False}
                    for surface_id in (
                        "homepage-development-media",
                        "pending-social-links",
                        "research-privacy-placeholder",
                        "terms-placeholder",
                        "accessibility-placeholder",
                    )
                ],
            )
            with override_settings(
                BASE_DIR=base_dir,
                TREADJOY_ENVIRONMENT="staging",
                TREADJOY_MODE="research",
                IS_PUBLIC_ENVIRONMENT=True,
                TREADJOY_PRIVATE_POC=True,
            ):
                output = io.StringIO()
                call_command(
                    "check_release_content",
                    "--profile",
                    "private-poc",
                    stdout=output,
                    stderr=output,
                )

        self.assertIn("release-content-check: passed (profile=private-poc)", output.getvalue())

    def test_private_poc_profile_requires_staging_research_private_and_noindex(self):
        cases = (
            ({"TREADJOY_ENVIRONMENT": "local"}, "private-poc-requires-staging"),
            ({"TREADJOY_ENVIRONMENT": "production"}, "private-poc-requires-staging"),
            ({"TREADJOY_MODE": "commerce"}, "private-poc-requires-research-mode"),
            ({"TREADJOY_PRIVATE_POC": False}, "private-poc-requires-TREADJOY_PRIVATE_POC=true"),
            ({"TREADJOY_PRIVATE_POC": False, "IS_PUBLIC_ENVIRONMENT": True}, "private-poc-requires-noindex"),
        )
        for settings_override, expected in cases:
            with self.subTest(expected=expected):
                values = {
                    "TREADJOY_ENVIRONMENT": "staging",
                    "TREADJOY_MODE": "research",
                    "IS_PUBLIC_ENVIRONMENT": True,
                    "TREADJOY_PRIVATE_POC": True,
                }
                values.update(settings_override)
                with override_settings(**values):
                    output = self.run_command("--profile", "private-poc")
                self.assertIn(expected, output)

    def test_private_poc_profile_rejects_unknown_content_surface(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            self.write_inventory(
                base_dir,
                content_surfaces=[
                    {
                        "id": "unapproved-placeholder",
                        "public_release": False,
                    }
                ],
            )
            with override_settings(
                BASE_DIR=base_dir,
                TREADJOY_ENVIRONMENT="staging",
                TREADJOY_MODE="research",
                IS_PUBLIC_ENVIRONMENT=True,
                TREADJOY_PRIVATE_POC=True,
            ):
                output = self.run_command("--profile", "private-poc")

        self.assertIn("private-poc-unknown-content-surface:unapproved-placeholder", output)

    def test_private_poc_profile_rejects_active_catalog_records(self):
        product = Product.objects.create(
            name="Private POC Fixture",
            slug="private-poc-fixture",
            price=Decimal("100.00"),
            is_active=True,
        )
        ProductVariant.objects.create(
            product=product,
            sku="PRIVATE-POC-FIXTURE-090-BLK",
            size="9",
            color="Black",
            stock_quantity=1,
            is_active=True,
        )

        with override_settings(
            TREADJOY_ENVIRONMENT="staging",
            TREADJOY_MODE="research",
            IS_PUBLIC_ENVIRONMENT=True,
            TREADJOY_PRIVATE_POC=True,
        ):
            output = self.run_command("--profile", "private-poc")

        self.assertIn("private-poc-active-catalog-present", output)
        self.assertIn("private-poc-active-catalog-variant-present", output)

    def test_private_poc_profile_rejects_media_even_if_inventory_approved(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            image_path = base_dir / "static" / "images" / "approved.jpg"
            image_path.parent.mkdir(parents=True)
            content = self.image_bytes()
            image_path.write_bytes(content)
            self.write_inventory(
                base_dir,
                [self.inventory_asset("static/images/approved.jpg", content)],
            )
            with override_settings(
                BASE_DIR=base_dir,
                TREADJOY_ENVIRONMENT="staging",
                TREADJOY_MODE="research",
                IS_PUBLIC_ENVIRONMENT=True,
                TREADJOY_PRIVATE_POC=True,
            ):
                output = self.run_command("--profile", "private-poc")

        self.assertIn("private-poc-media-present:static/images/approved.jpg", output)

    def test_private_poc_profile_cannot_be_selected_for_commerce(self):
        with override_settings(
            TREADJOY_ENVIRONMENT="staging",
            TREADJOY_MODE="commerce",
            IS_COMMERCE_MODE=True,
            IS_PUBLIC_ENVIRONMENT=True,
            TREADJOY_PRIVATE_POC=False,
        ):
            output = self.run_command("--profile", "private-poc")

        self.assertIn("private-poc-requires-research-mode", output)
        self.assertIn("private-poc-requires-TREADJOY_PRIVATE_POC=true", output)

    def test_private_poc_profile_cannot_be_selected_for_production(self):
        with override_settings(
            TREADJOY_ENVIRONMENT="production",
            TREADJOY_MODE="research",
            IS_COMMERCE_MODE=False,
            IS_PUBLIC_ENVIRONMENT=True,
            TREADJOY_PRIVATE_POC=True,
        ):
            output = self.run_command("--profile", "private-poc")

        self.assertIn("private-poc-requires-staging", output)

    def test_active_known_test_product_blocks_release(self):
        Product.objects.create(
            name="Development Product",
            slug="treadjoy-test-shoe",
            price=Decimal("100.00"),
            is_active=True,
        )
        output = io.StringIO()

        with self.assertRaises(CommandError):
            call_command("check_release_content", stderr=output)

        self.assertIn("active-development-product:treadjoy-test-shoe", output.getvalue())

    def test_active_product_image_requires_public_inventory_approval(self):
        Product.objects.create(
            name="Unapproved Image Product",
            slug="unapproved-image-product",
            price=Decimal("100.00"),
            image="products/unapproved-product.jpg",
            is_active=True,
        )
        output = io.StringIO()

        with self.assertRaises(CommandError):
            call_command("check_release_content", stderr=output)

        self.assertIn("unapproved-product-image:unapproved-image-product", output.getvalue())

    def test_unlisted_static_asset_blocks_release(self):
        output = io.StringIO()
        with patch(
            "web.core.management.commands.check_release_content.static_image_paths",
            return_value={"static/images/unlisted.png"},
        ):
            with self.assertRaises(CommandError):
                call_command("check_release_content", stderr=output)

        self.assertIn("unlisted-static-asset:static/images/unlisted.png", output.getvalue())

    def test_approved_static_asset_passes(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            image_path = base_dir / "static" / "images" / "approved.jpg"
            image_path.parent.mkdir(parents=True)
            content = self.image_bytes()
            image_path.write_bytes(content)
            self.write_inventory(
                base_dir,
                [self.inventory_asset("static/images/approved.jpg", content)],
            )

            with override_settings(BASE_DIR=base_dir):
                output = io.StringIO()
                call_command("check_release_content", stderr=output)

        self.assertEqual(output.getvalue(), "")

    def test_development_only_static_asset_blocks_release(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            image_path = base_dir / "static" / "images" / "development.jpg"
            image_path.parent.mkdir(parents=True)
            content = self.image_bytes()
            image_path.write_bytes(content)
            self.write_inventory(
                base_dir,
                [
                    self.inventory_asset(
                        "static/images/development.jpg",
                        content,
                        allowed_environments=["local-debug"],
                        public_release=False,
                        approval_status="development-only",
                    )
                ],
            )

            with override_settings(BASE_DIR=base_dir):
                output = self.run_command()

        self.assertIn("nonpublic-asset:static/images/development.jpg", output)

    def test_ai_generated_public_asset_blocks_release(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            image_path = base_dir / "static" / "images" / "ai.jpg"
            image_path.parent.mkdir(parents=True)
            content = self.image_bytes()
            image_path.write_bytes(content)
            self.write_inventory(
                base_dir,
                [
                    self.inventory_asset(
                        "static/images/ai.jpg",
                        content,
                        source_type="ai-generated",
                    )
                ],
            )

            with override_settings(BASE_DIR=base_dir):
                output = self.run_command()

        self.assertIn("ai-generated-public-asset:static/images/ai.jpg", output)

    def test_metadata_review_and_embedded_metadata_block_release(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            image_path = base_dir / "static" / "images" / "metadata.jpg"
            image_path.parent.mkdir(parents=True)
            content = self.image_bytes(with_exif=True)
            image_path.write_bytes(content)
            self.write_inventory(
                base_dir,
                [
                    self.inventory_asset(
                        "static/images/metadata.jpg",
                        content,
                        metadata_review={
                            "status": "metadata-present",
                            "notes": "EXIF must be stripped before approval.",
                        },
                    )
                ],
            )

            with override_settings(BASE_DIR=base_dir):
                output = self.run_command()

        self.assertIn("metadata-review-blocked:static/images/metadata.jpg", output)
        self.assertIn("embedded-metadata:static/images/metadata.jpg", output)

    def test_checksum_mismatch_blocks_release(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            image_path = base_dir / "static" / "images" / "changed.jpg"
            image_path.parent.mkdir(parents=True)
            content = self.image_bytes()
            image_path.write_bytes(content)
            self.write_inventory(
                base_dir,
                [
                    self.inventory_asset(
                        "static/images/changed.jpg",
                        content,
                        sha256="0" * 64,
                    )
                ],
            )

            with override_settings(BASE_DIR=base_dir):
                output = self.run_command()

        self.assertIn("checksum-mismatch:static/images/changed.jpg", output)

    def test_active_product_image_requires_approved_inventory_asset(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            media_root = base_dir / "media"
            product_path = media_root / "products" / "approved.jpg"
            product_path.parent.mkdir(parents=True)
            content = self.image_bytes()
            product_path.write_bytes(content)
            self.write_inventory(
                base_dir,
                [self.inventory_asset("media/products/approved.jpg", content)],
            )
            Product.objects.create(
                name="Approved Product",
                slug="approved-product",
                price=Decimal("100.00"),
                image="products/approved.jpg",
                is_active=True,
            )

            with override_settings(BASE_DIR=base_dir, MEDIA_ROOT=media_root):
                output = io.StringIO()
                call_command("check_release_content", stderr=output)

        self.assertEqual(output.getvalue(), "")

    def test_database_backed_product_error_does_not_expose_product_name(self):
        Product.objects.create(
            name="Sensitive Product Display Name",
            slug="unapproved-image-product",
            price=Decimal("100.00"),
            image="products/unapproved-product.jpg",
            is_active=True,
        )

        output = self.run_command()

        self.assertIn("unapproved-product-image:unapproved-image-product", output)
        self.assertNotIn("Sensitive Product Display Name", output)

    def test_repository_static_images_are_exactly_the_inventoried_assets(self):
        repository_root = Path(settings.BASE_DIR)
        public_images_root = repository_root / "static" / "images"
        product_media_root = repository_root / "media" / "products"
        inventory = json.loads(
            (repository_root / "docs" / "release-content-inventory.json").read_text(
                encoding="utf-8"
            )
        )
        inventoried_static_paths = {
            asset["path"]
            for asset in inventory["assets"]
            if asset["path"].startswith("static/images/")
        }
        repository_static_paths = {
            path.relative_to(repository_root).as_posix()
            for path in public_images_root.rglob("*")
            if path.is_file()
        }

        self.assertEqual(repository_static_paths, inventoried_static_paths)
        self.assertEqual(len(repository_static_paths), 14)
        self.assertFalse(
            product_media_root.exists() and any(product_media_root.glob("*.JPG"))
        )
