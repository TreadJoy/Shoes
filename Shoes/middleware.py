"""Application-owned security and origin-boundary middleware."""

import hmac

from django.conf import settings
from django.http import HttpResponse


_ORIGIN_HEALTH_PATHS = frozenset({"/health/live/", "/health/ready/"})


class CloudflareOriginLockMiddleware:
    """Reject direct-origin requests that did not cross the Cloudflare edge.

    Render's provider health checker reaches the service directly, so the
    generic health endpoints remain exempt. They disclose no configuration or
    dependency details and are separately rate-limited at the edge.
    """

    header_name = "X-TreadJoy-Origin"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.IS_PUBLIC_ENVIRONMENT and request.path not in _ORIGIN_HEALTH_PATHS:
            expected = getattr(settings, "TREADJOY_ORIGIN_SHARED_SECRET", "")
            presented = request.headers.get(self.header_name, "")
            if not expected or not hmac.compare_digest(presented, expected):
                return HttpResponse("Forbidden", status=403)
        return self.get_response(request)


class ContentSecurityPolicyMiddleware:
    """Attach TreadJoy's reviewed CSP without overriding a more specific view."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault(
            "Content-Security-Policy",
            settings.CONTENT_SECURITY_POLICY,
        )
        return response
