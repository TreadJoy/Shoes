"""Application-owned security response middleware."""

from django.conf import settings


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
