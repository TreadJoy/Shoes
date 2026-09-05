"""Application-owned security and origin-boundary middleware."""

import hmac
import logging

from django.conf import settings
from django.http import HttpResponse

from .cloudflare_access import (
    AccessKeyServiceUnavailable,
    AccessTokenInvalid,
    verify_access_token,
)


_ORIGIN_HEALTH_PATHS = frozenset({"/health/live/", "/health/ready/"})
_security_logger = logging.getLogger("Shoes.security")


class CloudflareOriginLockMiddleware:
    """Require both the edge secret and a valid private-POC Access token.

    Render's provider health checker reaches the service directly, so the
    generic health endpoints remain exempt. They disclose no configuration or
    dependency details and are separately rate-limited at the edge.
    """

    header_name = "X-TreadJoy-Origin"

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _error_response(body: str, status: int) -> HttpResponse:
        response = HttpResponse(body, status=status)
        response.headers["Cache-Control"] = "no-store"
        return response

    def __call__(self, request):
        if settings.IS_PUBLIC_ENVIRONMENT and request.path not in _ORIGIN_HEALTH_PATHS:
            expected = getattr(settings, "TREADJOY_ORIGIN_SHARED_SECRET", "")
            presented = request.headers.get(self.header_name, "")
            if not expected or not hmac.compare_digest(presented, expected):
                _security_logger.warning(
                    "cloudflare origin request denied",
                    extra={
                        "event": "cloudflare.origin_denied",
                        "origin_header_present": bool(presented),
                        "origin_header_length": len(presented),
                        "origin_secret_configured": bool(expected),
                    },
                )
                return self._error_response("Forbidden", 403)

            if getattr(settings, "CLOUDFLARE_ACCESS_REQUIRED", False):
                token = request.headers.get("Cf-Access-Jwt-Assertion", "")
                try:
                    verify_access_token(token)
                except AccessTokenInvalid:
                    _security_logger.warning(
                        "cloudflare access token denied",
                        extra={"event": "cloudflare.access_token_denied"},
                    )
                    return self._error_response("Forbidden", 403)
                except AccessKeyServiceUnavailable:
                    _security_logger.error(
                        "cloudflare access signing keys unavailable",
                        extra={"event": "cloudflare.access_keys_unavailable"},
                    )
                    return self._error_response("Service Unavailable", 503)
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
