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
from django.test import TestCase, override_settings
from PIL import Image

from web.products.models import Product


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

            with override_settings(DEBUG=True, MEDIA_ROOT=media_root):
                response = self.client.get("/")

        self.assertContains(response, 'src="/media/development/treadjoy-ai-logo.png"')

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

    def run_command(self):
        output = io.StringIO()
        try:
            call_command("check_release_content", stderr=output)
        except CommandError:
            return output.getvalue()
        return output.getvalue()

    def test_current_development_content_blocks_release(self):
        output = io.StringIO()

        with self.assertRaises(CommandError):
            call_command("check_release_content", stderr=output)

        self.assertIn("blocked-content-surface:homepage-development-media", output.getvalue())

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

    def test_removed_public_images_are_not_in_the_repository_tree(self):
        repository_root = Path(settings.BASE_DIR)
        public_images_root = repository_root / "static" / "images"
        product_media_root = repository_root / "media" / "products"

        self.assertFalse(
            public_images_root.exists() and any(public_images_root.iterdir())
        )
        self.assertFalse(
            product_media_root.exists() and any(product_media_root.glob("*.JPG"))
        )
