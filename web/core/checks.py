"""Deployment checks for the settings contract that Django cannot infer."""

from django.conf import settings
from django.core.checks import Error, Tags, register

from .research_boundary import runtime_boundary_violations, url_boundary_violations


@register(Tags.security, deploy=True)
def check_public_settings_contract(app_configs, **kwargs):
    """Keep intentional HSTS rollout exceptions narrow and auditable."""
    if not settings.IS_PUBLIC_ENVIRONMENT:
        return []

    errors = []
    if settings.DEBUG:
        errors.append(Error("Public TreadJoy settings must disable DEBUG.", id="treadjoy.E001"))
    if settings.SECURE_PROXY_SSL_HEADER != ("HTTP_X_FORWARDED_PROTO", "https"):
        errors.append(
            Error("Public TreadJoy settings must trust only the Cloudflare HTTPS header.", id="treadjoy.E002")
        )
    if not all((settings.SECURE_SSL_REDIRECT, settings.SESSION_COOKIE_SECURE, settings.CSRF_COOKIE_SECURE)):
        errors.append(
            Error("Public TreadJoy settings must redirect HTTPS and secure cookies.", id="treadjoy.E003")
        )
    if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
        errors.append(Error("Public TreadJoy settings must use SMTP email.", id="treadjoy.E004"))
    if settings.STORAGES["default"]["BACKEND"] != "storages.backends.s3.S3Storage":
        errors.append(Error("Public TreadJoy media must use the R2 S3 backend.", id="treadjoy.E005"))
    if (
        settings.STORAGES["staticfiles"]["BACKEND"]
        != "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
    ):
        errors.append(Error("Public TreadJoy static files must use a manifest backend.", id="treadjoy.E006"))
    if "Shoes.middleware.ContentSecurityPolicyMiddleware" not in settings.MIDDLEWARE:
        errors.append(Error("The TreadJoy CSP middleware must be enabled.", id="treadjoy.E007"))
    if "script-src 'self'" not in settings.CONTENT_SECURITY_POLICY:
        errors.append(Error("The TreadJoy CSP must restrict scripts to self.", id="treadjoy.E008"))

    expected_silenced = set()
    if not settings.SECURE_HSTS_INCLUDE_SUBDOMAINS:
        expected_silenced.add("security.W005")
    if not settings.SECURE_HSTS_PRELOAD:
        expected_silenced.add("security.W021")
    actual_silenced = set(getattr(settings, "SILENCED_SYSTEM_CHECKS", ()))
    if actual_silenced != expected_silenced:
        errors.append(
            Error(
                "Only the HSTS rollout advisories justified by the configured "
                "HSTS stage may be silenced.",
                id="treadjoy.E009",
            )
        )
    return errors


@register(Tags.security, deploy=True)
def check_research_capability_boundary(app_configs, **kwargs):
    """Reject commerce runtime or URL capabilities in research mode."""
    if settings.IS_COMMERCE_MODE:
        return []

    runtime_violations = runtime_boundary_violations()
    route_violations = url_boundary_violations()
    errors = []
    if runtime_violations:
        errors.append(
            Error(
                "; ".join(runtime_violations),
                hint="Remove commerce configuration and imports from research startup.",
                id="treadjoy.E010",
            )
        )
    if route_violations:
        errors.append(
            Error(
                "; ".join(route_violations),
                hint="Keep cart and order URLconfs conditional on commerce mode.",
                id="treadjoy.E011",
            )
        )
    return errors
