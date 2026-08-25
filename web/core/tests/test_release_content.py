import io
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

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
