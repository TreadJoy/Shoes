from django.conf import settings


def deployment_mode(request):
    return {
        "is_commerce_mode": settings.IS_COMMERCE_MODE,
    }
