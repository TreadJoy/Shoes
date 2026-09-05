import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from django.http import HttpResponse
from django.middleware.clickjacking import XFrameOptionsMiddleware
from django.middleware.security import SecurityMiddleware
from django.test import RequestFactory, SimpleTestCase, override_settings

from Shoes.middleware import CloudflareOriginLockMiddleware, ContentSecurityPolicyMiddleware


PUBLIC_SETUP_PROBE = r"""
import importlib.abc
import os
import sys


FORBIDDEN_MODULE_PREFIXES = (
    "allauth",
    "web.accounts",
    "web.cart",
    "web.orders",
    "stripe",
)


def is_forbidden_module(name):
    return any(
        name == prefix or name.startswith(f"{prefix}.")
        for prefix in FORBIDDEN_MODULE_PREFIXES
    )


class ResearchImportBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if is_forbidden_module(fullname):
            raise AssertionError(
                f"Public research startup attempted forbidden import: {fullname}"
            )
        return None


if os.environ.get("TREADJOY_MODE") == "research":
    sys.meta_path.insert(0, ResearchImportBlocker())

import django

django.setup()

from django.conf import settings
from django.core.management import call_command

assert settings.IS_PUBLIC_ENVIRONMENT
assert not settings.DEBUG
assert settings.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
if settings.TREADJOY_MODE == "commerce":
    assert settings.EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend"
else:
    assert settings.RESEARCH_EMAIL_PROVIDER == "resend"
assert settings.STORAGES["default"]["BACKEND"] == "storages.backends.s3.S3Storage"
assert settings.STORAGES["staticfiles"]["BACKEND"] == "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
assert settings.MEDIA_URL == "https://media.ci.invalid/media/"
assert "https://media.ci.invalid" in settings.CONTENT_SECURITY_POLICY
assert "upgrade-insecure-requests" in settings.CONTENT_SECURITY_POLICY
call_command("check", "--deploy", "--fail-level", "WARNING")
if settings.TREADJOY_MODE == "research":
    assert not any(is_forbidden_module(name) for name in sys.modules)
"""


class PublicSettingsProcessTests(SimpleTestCase):
    project_root = Path(__file__).resolve().parents[3]

    def environment_for(self, mode="research"):
        environment = os.environ.copy()
        for name in list(environment):
            if name.startswith("STRIPE_") or name in {"DATABASE_URL", "TREADJOY_PRIVATE_POC"}:
                environment.pop(name)
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "Shoes.settings",
                "TREADJOY_ENVIRONMENT": "staging",
                "TREADJOY_MODE": mode,
                "TREADJOY_INGRESS": "cloudflare-locked",
                "TREADJOY_ORIGIN_SHARED_SECRET": "public-origin-lock-secret-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "DJANGO_DEBUG": "false",
                "SECRET_KEY": "public-settings-test-key-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ!",
                "SECRET_KEY_FALLBACKS": "",
                "ALLOWED_HOSTS": "ci.invalid",
                "CSRF_TRUSTED_ORIGINS": "https://ci.invalid",
                "DB_NAME": "treadjoy_public_check",
                "DB_USER": "treadjoy_public_check",
                "DB_PASSWORD": "public-database-password-not-a-secret",
                "DB_HOST": "database.ci.invalid",
                "DB_PORT": "5432",
                "DB_SSLMODE": "require",
                "STATIC_ROOT": "/tmp/treadjoy-public-settings-static",
                "R2_ACCOUNT_ID": "publiccheckaccount",
                "R2_BUCKET_NAME": "treadjoy-public-check",
                "R2_ACCESS_KEY_ID": "public-r2-access-key-not-a-secret",
                "R2_SECRET_ACCESS_KEY": "public-r2-secret-not-a-secret",
                "R2_MEDIA_CUSTOM_DOMAIN": "media.ci.invalid",
                "EMAIL_HOST": "smtp.ci.invalid",
                "EMAIL_PORT": "587",
                "EMAIL_HOST_USER": "public-check-user",
                "EMAIL_HOST_PASSWORD": "public-email-password-not-a-secret",
                "DEFAULT_FROM_EMAIL": "noreply@ci.invalid",
                "SERVER_EMAIL": "errors@ci.invalid",
                "SECURE_HSTS_SECONDS": "3600",
                "SECURE_HSTS_INCLUDE_SUBDOMAINS": "false",
                "SECURE_HSTS_PRELOAD": "false",
            }
        )
        if mode == "commerce":
            environment.update(
                {
                    "STRIPE_SECRET_KEY": "sk_test_public_settings_boundary",
                    "STRIPE_WEBHOOK_SECRET": "whsec_public_settings_boundary",
                }
            )
        else:
            environment.update(
                {
                    "RESEARCH_PRIVACY_NOTICE_VERSION": "ci-approved-notice-v1",
                    "RESEARCH_PRIVACY_NOTICE_BODY": "Synthetic CI research privacy notice.",
                    "RESEARCH_PRIVACY_NOTICE_SHA256": "7f9862d185c863a44aecce5c100391d98888738d7d47a1b802dff54b8ea1f205",
                    "RESEARCH_IDENTITY_HMAC_KEY": "ci-research-hmac-key-not-a-secret-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                    "RESEARCH_RESEND_SEND_API_KEY": "re_ci_send_key_not_a_secret",
                    "RESEARCH_RESEND_WEBHOOK_SECRET": "whsec_ci_resend_not_a_secret",
                    "RESEARCH_RESEND_SEGMENT_ID": "ci-research-segment",
                    "RESEARCH_EMAIL_TRANSACTIONAL_FROM": "TreadJoy Research <confirm@confirm.tread-joy.com>",
                    "RESEARCH_EMAIL_MARKETING_FROM": "TreadJoy <updates@updates.tread-joy.com>",
                    "RESEARCH_EMAIL_REPLY_TO": "hello@tread-joy.com",
                    "RESEARCH_RETENTION_POLICY_VERSION": "ci-retention-v1",
                }
            )
        existing_pythonpath = environment.get("PYTHONPATH", "")
        environment["PYTHONPATH"] = os.pathsep.join(
            item
            for item in (str(self.project_root), existing_pythonpath)
            if item
        )
        return environment

    def run_setup(self, environment, script=PUBLIC_SETUP_PROBE):
        with TemporaryDirectory() as temporary_directory:
            isolated_config_script = (
                "import os\n"
                "import decouple\n"
                "decouple.config = decouple.AutoConfig(search_path=os.getcwd())\n"
            )
            return subprocess.run(
                [sys.executable, "-c", isolated_config_script + script],
                cwd=temporary_directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

    def assert_setup_succeeds(self, environment):
        result = self.run_setup(environment)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def assert_setup_fails(self, environment, message):
        result = self.run_setup(environment, "import django; django.setup()")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)

    def test_valid_staging_profiles_pass_deploy_checks(self):
        for mode in ("commerce", "research"):
            with self.subTest(mode=mode):
                self.assert_setup_succeeds(self.environment_for(mode))

    def test_public_profiles_fail_closed_for_required_services(self):
        required_names = (
            "ALLOWED_HOSTS",
            "CSRF_TRUSTED_ORIGINS",
            "TREADJOY_ORIGIN_SHARED_SECRET",
            "DB_SSLMODE",
            "STATIC_ROOT",
            "R2_SECRET_ACCESS_KEY",
            "EMAIL_HOST_PASSWORD",
            "SECURE_HSTS_SECONDS",
        )
        for name in required_names:
            with self.subTest(name=name):
                environment = self.environment_for()
                environment[name] = ""
                self.assert_setup_fails(environment, name)

        for name in (
            "RESEARCH_PRIVACY_NOTICE_VERSION",
            "RESEARCH_PRIVACY_NOTICE_BODY",
            "RESEARCH_PRIVACY_NOTICE_SHA256",
            "RESEARCH_IDENTITY_HMAC_KEY",
            "RESEARCH_RESEND_SEND_API_KEY",
            "RESEARCH_RESEND_WEBHOOK_SECRET",
            "RESEARCH_RESEND_SEGMENT_ID",
            "RESEARCH_EMAIL_TRANSACTIONAL_FROM",
            "RESEARCH_EMAIL_MARKETING_FROM",
            "RESEARCH_EMAIL_REPLY_TO",
            "RESEARCH_RETENTION_POLICY_VERSION",
        ):
            with self.subTest(mode="research", name=name):
                environment = self.environment_for("research")
                environment[name] = ""
                self.assert_setup_fails(environment, name)

    def test_public_research_rejects_unapproved_or_inconsistent_email_contract(self):
        cases = (
            (
                "RESEARCH_IDENTITY_HMAC_KEY",
                "too-short",
                "generated production-strength secret",
            ),
            (
                "RESEARCH_PRIVACY_NOTICE_SHA256",
                "0" * 64,
                "must match the approved notice body",
            ),
            (
                "RESEARCH_PRIVACY_NOTICE_VERSION",
                "research-notice-draft",
                "must identify an approved notice",
            ),
            (
                "RESEARCH_RETENTION_POLICY_VERSION",
                "draft-retention-v1",
                "must identify an effective policy",
            ),
            (
                "RESEARCH_EMAIL_REPLY_TO",
                "unmonitored@tread-joy.com",
                "monitored hello@tread-joy.com mailbox",
            ),
            (
                "RESEARCH_EMAIL_MARKETING_FROM",
                "TreadJoy <updates@confirm.tread-joy.com>",
                "two distinct verified",
            ),
        )
        for name, value, message in cases:
            with self.subTest(name=name):
                environment = self.environment_for("research")
                environment[name] = value
                self.assert_setup_fails(environment, message)

    def test_private_research_poc_accepts_owner_mailbox_and_draft_policy(self):
        environment = self.environment_for("research")
        environment.update(
            {
                "TREADJOY_PRIVATE_POC": "true",
                "RESEARCH_PRIVACY_NOTICE_VERSION": "0.1-draft",
                "RESEARCH_RETENTION_POLICY_VERSION": "0.1-draft",
                "RESEARCH_EMAIL_TRANSACTIONAL_FROM": "TreadJoy Research <ethan@tread-joy.com>",
                "RESEARCH_EMAIL_MARKETING_FROM": "TreadJoy <ethan@tread-joy.com>",
                "RESEARCH_EMAIL_REPLY_TO": "ethan@tread-joy.com",
            }
        )
        environment.pop("RESEARCH_RESEND_SEGMENT_ID", None)
        result = self.run_setup(
            environment,
            """
import django
django.setup()
from django.conf import settings
assert settings.TREADJOY_PRIVATE_POC is True
assert settings.RESEARCH_EMAIL_REPLY_TO == "ethan@tread-joy.com"
""",
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_render_database_url_supplies_postgresql_connection_values(self):
        environment = self.environment_for("research")
        for name in ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_SSLMODE"):
            environment.pop(name, None)
        environment["DATABASE_URL"] = (
            "postgresql://url-user:url-pass@database.ci.invalid:5432/url-db"
        )
        result = self.run_setup(
            environment,
            """
import django
django.setup()
from django.conf import settings
database = settings.DATABASES["default"]
assert database["NAME"] == "url-db"
assert database["USER"] == "url-user"
assert database["PASSWORD"] == "url-pass"
assert database["HOST"] == "database.ci.invalid"
assert database["PORT"] == 5432
assert database["OPTIONS"] == {"sslmode": "require"}
""",
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_render_internal_database_url_defaults_postgresql_port(self):
        environment = self.environment_for("research")
        for name in ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_SSLMODE"):
            environment.pop(name, None)
        environment["DATABASE_URL"] = "postgresql://url-user:url-pass@database.ci.invalid/url-db"
        result = self.run_setup(
            environment,
            """
import django
django.setup()
from django.conf import settings
assert settings.DATABASES["default"]["PORT"] == 5432
""",
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_public_profiles_reject_relaxed_or_inconsistent_security_values(self):
        cases = (
            ("DJANGO_DEBUG", "true", "DJANGO_DEBUG must be false"),
            ("TREADJOY_INGRESS", "direct", "TREADJOY_INGRESS must be cloudflare-locked"),
            ("ALLOWED_HOSTS", "*", "ALLOWED_HOSTS"),
            ("CSRF_TRUSTED_ORIGINS", "http://ci.invalid", "CSRF_TRUSTED_ORIGINS"),
            ("SECURE_HSTS_PRELOAD", "true", "SECURE_HSTS_PRELOAD requires"),
        )
        for name, value, message in cases:
            with self.subTest(name=name):
                environment = self.environment_for()
                environment[name] = value
                self.assert_setup_fails(environment, message)

    def test_research_rejects_stripe_configuration_before_other_services(self):
        for setting_name in (
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET",
            "STRIPE_FUTURE_TOKEN",
        ):
            with self.subTest(setting_name=setting_name):
                marker = f"do-not-print-{setting_name.casefold()}"
                environment = self.environment_for("research")
                environment[setting_name] = marker
                environment["EMAIL_HOST"] = ""

                result = self.run_setup(environment, "import django; django.setup()")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(setting_name, result.stderr)
                self.assertNotIn("EMAIL_HOST", result.stderr)
                self.assertNotIn(marker, result.stdout)
                self.assertNotIn(marker, result.stderr)

    def test_public_research_requires_stripe_variable_names_to_be_absent(self):
        for setting_name in ("STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"):
            with self.subTest(setting_name=setting_name):
                environment = self.environment_for("research")
                environment[setting_name] = ""

                self.assert_setup_fails(environment, setting_name)

    def test_configuration_errors_do_not_expose_secret_values(self):
        marker = "do-not-print-this-public-r2-secret-marker"
        environment = self.environment_for()
        environment["R2_SECRET_ACCESS_KEY"] = marker
        environment["EMAIL_HOST"] = ""
        result = self.run_setup(environment, "import django; django.setup()")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(marker, result.stdout)
        self.assertNotIn(marker, result.stderr)


class SecurityHeaderTests(SimpleTestCase):
    def response_for(self, **headers):
        request = RequestFactory().get("/", **headers)
        application = SecurityMiddleware(
            ContentSecurityPolicyMiddleware(
                XFrameOptionsMiddleware(lambda request: HttpResponse("ok"))
            )
        )
        return application(request)

    @override_settings(
        IS_PUBLIC_ENVIRONMENT=True,
        TREADJOY_ORIGIN_SHARED_SECRET="origin-secret",
    )
    def test_public_origin_requires_cloudflare_header_except_health(self):
        blocked = CloudflareOriginLockMiddleware(lambda request: HttpResponse("ok"))(
            RequestFactory().get("/")
        )
        self.assertEqual(blocked.status_code, 403)

        allowed = CloudflareOriginLockMiddleware(lambda request: HttpResponse("ok"))(
            RequestFactory().get("/", HTTP_X_TREADJOY_ORIGIN="origin-secret")
        )
        self.assertEqual(allowed.status_code, 200)

        health = CloudflareOriginLockMiddleware(lambda request: HttpResponse("ok"))(
            RequestFactory().get("/health/live/")
        )
        self.assertEqual(health.status_code, 200)

    def test_csp_is_enforced_without_unsafe_inline_scripts(self):
        response = self.response_for()

        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["Referrer-Policy"], "same-origin")
        self.assertEqual(response.headers["Cross-Origin-Opener-Policy"], "same-origin")
        self.assertIn("script-src 'self'", response.headers["Content-Security-Policy"])
        self.assertNotIn("script-src 'self' 'unsafe-inline'", response.headers["Content-Security-Policy"])
        self.assertIn("frame-src https://www.youtube-nocookie.com", response.headers["Content-Security-Policy"])

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_PROXY_SSL_HEADER=None,
    )
    def test_direct_ingress_does_not_trust_a_spoofed_forwarded_protocol(self):
        response = self.response_for(HTTP_X_FORWARDED_PROTO="https")

        self.assertEqual(response.status_code, 301)
        self.assertTrue(response["Location"].startswith("https://"))

    @override_settings(
        SECURE_SSL_REDIRECT=True,
        SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
        SECURE_HSTS_SECONDS=3600,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
        CSRF_COOKIE_HTTPONLY=True,
    )
    def test_trusted_proxy_requests_receive_https_headers(self):
        response = self.response_for(HTTP_X_FORWARDED_PROTO="https")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Strict-Transport-Security"], "max-age=3600")
