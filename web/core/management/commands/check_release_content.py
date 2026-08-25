"""Fail closed when known development content could reach a public release."""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from web.products.models import Product


INVENTORY_PATH = "docs/release-content-inventory.json"
REQUIRED_ASSET_FIELDS = (
    "id",
    "path",
    "source_type",
    "rights_status",
    "allowed_environments",
    "public_release",
    "sha256",
    "metadata_review",
    "alt_text_decision",
)


def load_inventory():
    inventory_path = Path(settings.BASE_DIR) / INVENTORY_PATH
    try:
        return json.loads(inventory_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise CommandError(f"content-inventory-missing:{INVENTORY_PATH}") from error
    except json.JSONDecodeError as error:
        raise CommandError(f"content-inventory-invalid:{INVENTORY_PATH}") from error


def static_image_paths():
    images_root = Path(settings.BASE_DIR) / "static" / "images"
    if not images_root.exists():
        return set()
    return {
        path.relative_to(Path(settings.BASE_DIR)).as_posix()
        for path in images_root.rglob("*")
        if path.is_file()
    }


class Command(BaseCommand):
    help = "Fail when development-only content or unapproved public assets remain."

    def handle(self, *args, **options):
        inventory = load_inventory()
        errors = []
        assets = inventory.get("assets", [])
        assets_by_path = {}

        for asset in assets:
            asset_id = asset.get("id", "unknown-asset")
            for field in REQUIRED_ASSET_FIELDS:
                if field not in asset:
                    errors.append(f"inventory-asset-missing-field:{asset_id}:{field}")
            path = asset.get("path")
            if path:
                assets_by_path[path] = asset

        for path in sorted(static_image_paths()):
            asset = assets_by_path.get(path)
            if asset is None:
                errors.append(f"unlisted-static-asset:{path}")
            elif not asset.get("public_release", False):
                errors.append(f"nonpublic-static-asset:{path}")
            elif asset.get("source_type") == "ai-generated":
                errors.append(f"ai-generated-public-asset:{path}")

        for surface in inventory.get("content_surfaces", []):
            if not surface.get("public_release", False):
                surface_id = surface.get("id", "unknown-content-surface")
                errors.append(f"blocked-content-surface:{surface_id}")

        blocked_slugs = set(inventory.get("blocked_catalog_slugs", []))
        for product in Product.objects.filter(is_active=True).only(
            "slug",
            "image",
        ):
            if product.slug in blocked_slugs:
                errors.append(f"active-development-product:{product.slug}")
            if product.image:
                image_path = f"media/{product.image.name}"
                asset = assets_by_path.get(image_path)
                if asset is None or not asset.get("public_release", False):
                    errors.append(f"unapproved-product-image:{product.slug}")

        if errors:
            for error in sorted(set(errors)):
                self.stderr.write(error)
            raise CommandError(f"{len(set(errors))} release-content blocker(s) found.")

        self.stdout.write(self.style.SUCCESS("release-content-check: passed"))
