"""Fail closed when known development content could reach a public release."""

import json
import hashlib
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.http import HttpRequest
from PIL import Image, UnidentifiedImageError

from web.core.context_processors import deployment_mode
from web.products.models import Product
from web.products.models import ProductVariant


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
    "approval_status",
)
PUBLIC_ENVIRONMENTS = {"research", "commerce"}
ALLOWED_ENVIRONMENTS = PUBLIC_ENVIRONMENTS | {"local-debug"}
APPROVAL_STATUSES = {"approved", "development-only", "blocked", "pending"}
METADATA_STATUSES = {"clean", "not-applicable", "metadata-present"}
ALT_TEXT_KINDS = {"meaningful", "decorative", "not-public"}
EMBEDDED_METADATA_KEYS = {"exif", "xmp", "xml", "iptc", "comment"}
PROFILE_CHOICES = ("public", "private-poc")
PRIVATE_POC_ALLOWED_BLOCKED_SURFACES = {
    "homepage-development-media",
    "pending-social-links",
    "research-privacy-placeholder",
    "terms-placeholder",
    "accessibility-placeholder",
}


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


def hash_stream(stream):
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(64 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def has_embedded_metadata(stream):
    """Return whether an image contains release-blocking embedded metadata."""
    try:
        stream.seek(0)
        with Image.open(stream) as image:
            if image.getexif():
                return True
            return bool(EMBEDDED_METADATA_KEYS & set(image.info))
    except (UnidentifiedImageError, OSError):
        return False
    finally:
        stream.seek(0)


def validate_asset(asset, errors):
    asset_id = asset.get("id", "unknown-asset")
    for field in REQUIRED_ASSET_FIELDS:
        if field not in asset:
            errors.append(f"inventory-asset-missing-field:{asset_id}:{field}")

    path = asset.get("path")
    if not isinstance(path, str) or not path or Path(path).is_absolute():
        errors.append(f"inventory-asset-invalid-path:{asset_id}")

    checksum = asset.get("sha256")
    if not isinstance(checksum, str) or len(checksum) != 64 or any(
        character not in "0123456789abcdef" for character in checksum
    ):
        errors.append(f"inventory-asset-invalid-checksum:{asset_id}")

    environments = asset.get("allowed_environments")
    if (
        not isinstance(environments, list)
        or not environments
        or not set(environments).issubset(ALLOWED_ENVIRONMENTS)
    ):
        errors.append(f"inventory-asset-invalid-environments:{asset_id}")

    approval_status = asset.get("approval_status")
    if approval_status not in APPROVAL_STATUSES:
        errors.append(f"inventory-asset-invalid-approval-status:{asset_id}")

    public_release = asset.get("public_release")
    if not isinstance(public_release, bool):
        errors.append(f"inventory-asset-invalid-public-release:{asset_id}")
    elif public_release and approval_status != "approved":
        errors.append(f"inventory-asset-unapproved-public-release:{asset_id}")

    metadata_review = asset.get("metadata_review")
    if (
        not isinstance(metadata_review, dict)
        or metadata_review.get("status") not in METADATA_STATUSES
        or not isinstance(metadata_review.get("notes"), str)
    ):
        errors.append(f"inventory-asset-invalid-metadata-review:{asset_id}")

    alt_text_decision = asset.get("alt_text_decision")
    if (
        not isinstance(alt_text_decision, dict)
        or alt_text_decision.get("kind") not in ALT_TEXT_KINDS
        or not isinstance(alt_text_decision.get("text"), str)
    ):
        errors.append(f"inventory-asset-invalid-alt-text-decision:{asset_id}")


def public_asset_errors(asset, path, environment):
    errors = []
    if asset.get("approval_status") != "approved" or not asset.get(
        "public_release", False
    ):
        errors.append(f"nonpublic-asset:{path}")
    if environment not in asset.get("allowed_environments", []):
        errors.append(f"asset-not-allowed-in-environment:{path}:{environment}")
    if asset.get("source_type") == "ai-generated":
        errors.append(f"ai-generated-public-asset:{path}")
    metadata_review = asset.get("metadata_review", {})
    if metadata_review.get("status") not in {"clean", "not-applicable"}:
        errors.append(f"metadata-review-blocked:{path}")
    return errors


def verify_asset_file(asset, path, stream, errors):
    if hash_stream(stream) != asset.get("sha256"):
        errors.append(f"checksum-mismatch:{path}")
    if has_embedded_metadata(stream):
        errors.append(f"embedded-metadata:{path}")


class Command(BaseCommand):
    help = "Fail when development-only content or unapproved public assets remain."

    def add_arguments(self, parser):
        parser.add_argument(
            "--profile",
            choices=PROFILE_CHOICES,
            default="public",
            help=(
                "Release content contract to enforce. The default public profile "
                "is fail-closed; private-poc is staging-only."
            ),
        )

    @staticmethod
    def private_poc_configuration_errors():
        errors = []
        if settings.TREADJOY_ENVIRONMENT != "staging":
            errors.append("private-poc-requires-staging")
        if settings.TREADJOY_MODE != "research":
            errors.append("private-poc-requires-research-mode")
        if not settings.TREADJOY_PRIVATE_POC:
            errors.append("private-poc-requires-TREADJOY_PRIVATE_POC=true")

        request = HttpRequest()
        request.method = "GET"
        request.path = "/"
        metadata = deployment_mode(request)
        if metadata.get("robots_directive") != "noindex, nofollow, noarchive":
            errors.append("private-poc-requires-noindex")

        if Product.objects.filter(is_active=True).exists():
            errors.append("private-poc-active-catalog-present")
        if ProductVariant.objects.filter(
            is_active=True,
            product__is_active=True,
        ).exists():
            errors.append("private-poc-active-catalog-variant-present")
        return errors

    def handle(self, *args, **options):
        profile = options["profile"]
        inventory = load_inventory()
        errors = []
        assets = inventory.get("assets", [])
        assets_by_path = {}

        if profile == "private-poc":
            errors.extend(self.private_poc_configuration_errors())

        for asset in assets:
            validate_asset(asset, errors)
            path = asset.get("path")
            if path:
                if path in assets_by_path:
                    errors.append(f"inventory-duplicate-path:{path}")
                assets_by_path[path] = asset

        for path in sorted(static_image_paths()):
            asset = assets_by_path.get(path)
            if asset is None:
                errors.append(f"unlisted-static-asset:{path}")
                continue

            if profile == "private-poc":
                errors.append(f"private-poc-media-present:{path}")
                continue

            errors.extend(public_asset_errors(asset, path, settings.TREADJOY_MODE))
            try:
                with (Path(settings.BASE_DIR) / path).open("rb") as asset_file:
                    verify_asset_file(asset, path, asset_file, errors)
            except OSError:
                errors.append(f"static-asset-unreadable:{path}")

        for surface in inventory.get("content_surfaces", []):
            surface_id = surface.get("id", "unknown-content-surface")
            if profile == "private-poc":
                if surface_id not in PRIVATE_POC_ALLOWED_BLOCKED_SURFACES:
                    errors.append(f"private-poc-unknown-content-surface:{surface_id}")
                elif surface.get("public_release", False):
                    errors.append(
                        f"private-poc-content-surface-not-blocked:{surface_id}"
                    )
            elif not surface.get("public_release", False):
                errors.append(f"blocked-content-surface:{surface_id}")

        if profile == "private-poc":
            for asset in assets:
                if asset.get("public_release", False):
                    errors.append(
                        f"private-poc-public-asset:{asset.get('path', 'unknown-asset')}"
                    )

        blocked_slugs = set(inventory.get("blocked_catalog_slugs", []))
        for product in Product.objects.filter(is_active=True).only(
            "slug",
            "image",
        ):
            if profile == "private-poc":
                if product.image:
                    errors.append(f"private-poc-product-media-present:{product.slug}")
                continue
            if product.slug in blocked_slugs:
                errors.append(f"active-development-product:{product.slug}")
            if product.image:
                image_path = f"media/{product.image.name}"
                asset = assets_by_path.get(image_path)
                if asset is None:
                    errors.append(f"unapproved-product-image:{product.slug}")
                    continue

                errors.extend(
                    public_asset_errors(asset, image_path, settings.TREADJOY_MODE)
                )
                try:
                    with product.image.open("rb") as image_file:
                        verify_asset_file(asset, image_path, image_file, errors)
                except OSError:
                    errors.append(f"product-image-unreadable:{product.slug}")

        if errors:
            for error in sorted(set(errors)):
                self.stderr.write(error)
            raise CommandError(f"{len(set(errors))} release-content blocker(s) found.")

        self.stdout.write(
            self.style.SUCCESS(f"release-content-check: passed (profile={profile})")
        )
