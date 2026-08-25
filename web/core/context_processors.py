from pathlib import Path

from django.conf import settings


def deployment_mode(request):
    development_logo_path = (
        Path(settings.MEDIA_ROOT) / "development" / "treadjoy-ai-logo.png"
    )

    return {
        "is_commerce_mode": settings.IS_COMMERCE_MODE,
        "development_logo_url": (
            f"{settings.MEDIA_URL}development/treadjoy-ai-logo.png"
            if settings.DEBUG and development_logo_path.is_file()
            else ""
        ),
    }
