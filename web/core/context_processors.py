from pathlib import Path

from django.conf import settings


_METADATA_EXCLUDED_PREFIXES = (
    "/admin/",
    "/accounts/",
    "/cart/",
    "/health/",
    "/orders/",
    "/survey/",
    "/waitlist/",
)


def _metadata(request):
    """Return safe, deployment-owned discovery metadata for the shared shell."""
    path = "/" + request.path.lstrip("/")
    excluded = path == "/robots.txt" or path.startswith(_METADATA_EXCLUDED_PREFIXES)
    route_is_indexable = request.method == "GET" and not excluded

    # Never derive a canonical URL from Host. The origin is a reviewed setting
    # for the selected deployment mode, so a crafted Host header cannot poison
    # canonical, Open Graph, or X metadata.
    canonical_url = ""
    if settings.IS_PUBLIC_ENVIRONMENT and route_is_indexable:
        canonical_url = f"{settings.TREADJOY_CANONICAL_ORIGIN}{path}"

    noindex = (
        not settings.IS_PUBLIC_ENVIRONMENT
        or settings.TREADJOY_PRIVATE_POC
        or not route_is_indexable
    )
    if settings.IS_COMMERCE_MODE:
        meta_title = "TreadJoy"
        meta_description = "TreadJoy storefront."
    else:
        meta_title = "TreadJoy research preview"
        meta_description = (
            "Private TreadJoy development preview for internal testing. "
            "No public product claims or offers are made here."
        )

    return {
        "canonical_url": canonical_url,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "robots_directive": (
            "noindex, nofollow, noarchive" if noindex else "index, follow"
        ),
        "private_poc": settings.TREADJOY_PRIVATE_POC,
        "contact_email": settings.TREADJOY_CONTACT_EMAIL,
        "social_platforms": ("X", "YouTube", "Instagram", "TikTok"),
    }


def deployment_mode(request):
    development_logo_path = (
        Path(settings.MEDIA_ROOT) / "development" / "treadjoy-ai-logo.png"
    )

    context = {
        "is_commerce_mode": settings.IS_COMMERCE_MODE,
        "development_logo_url": (
            f"{settings.MEDIA_URL}development/treadjoy-ai-logo.png"
            if settings.IS_COMMERCE_MODE
            and settings.DEBUG
            and development_logo_path.is_file()
            else ""
        ),
        "research_preview_notice": (
            not settings.IS_COMMERCE_MODE
            and (not settings.IS_PUBLIC_ENVIRONMENT or settings.TREADJOY_PRIVATE_POC)
        ),
    }
    context.update(_metadata(request))
    return context
