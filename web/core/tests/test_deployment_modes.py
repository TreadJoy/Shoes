import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase


DJANGO_SETUP_PROBE = r"""
import sys

import django

django.setup()

from django.apps import apps
from django.conf import settings
from django.urls import NoReverseMatch, Resolver404, resolve, reverse


assert settings.ACCOUNT_LOGIN_METHODS == {"username"}
assert settings.ACCOUNT_EMAIL_VERIFICATION == "optional"


if settings.TREADJOY_MODE == "commerce":
    assert settings.IS_COMMERCE_MODE
    assert apps.is_installed("web.cart")
    assert apps.is_installed("web.orders")
    assert apps.get_model("orders", "Order") is not None
    assert reverse("cart:cart_detail") == "/cart/"
    assert reverse("cart:update_cart_item", args=[1]) == "/cart/update/1/"
    assert reverse("orders:order_list") == "/orders/"
    assert reverse("orders:checkout") == "/orders/checkout/"
    assert reverse("orders:stripe_webhook") == "/orders/stripe/webhook/"
    assert resolve("/orders/history/").url_name is None

    for removed_route_name, args in (
        ("cart:add_to_cart_item", [1]),
        ("orders:order_history", []),
    ):
        try:
            reverse(removed_route_name, args=args)
        except NoReverseMatch:
            pass
        else:
            raise AssertionError(f"{removed_route_name} remains reversible.")
    assert settings.STRIPE_SECRET_KEY == "sk_test_mode_boundary"
    assert settings.STRIPE_WEBHOOK_SECRET == "whsec_mode_boundary"

    import stripe

    assert stripe.api_key is None
else:
    assert settings.TREADJOY_MODE == "research"
    assert not settings.IS_COMMERCE_MODE
    assert not apps.is_installed("web.cart")
    assert not apps.is_installed("web.orders")

    try:
        apps.get_model("orders", "Order")
    except LookupError:
        pass
    else:
        raise AssertionError("The Order model is registered in research mode.")

    for route_name in (
        "cart:cart_detail",
        "orders:order_list",
        "orders:checkout",
        "orders:stripe_webhook",
    ):
        try:
            reverse(route_name)
        except NoReverseMatch:
            pass
        else:
            raise AssertionError(f"{route_name} is available in research mode.")

    try:
        reverse("cart:update_cart_item", args=[1])
    except NoReverseMatch:
        pass
    else:
        raise AssertionError("cart:update_cart_item is available in research mode.")

    for route_path in (
        "/cart/",
        "/cart/update/1/",
        "/orders/",
        "/orders/history/",
        "/orders/1/",
        "/orders/checkout/",
        "/orders/stripe/webhook/",
    ):
        try:
            resolve(route_path)
        except Resolver404:
            pass
        else:
            raise AssertionError(f"{route_path} resolves in research mode.")

    assert not hasattr(settings, "STRIPE_SECRET_KEY")
    assert not hasattr(settings, "STRIPE_WEBHOOK_SECRET")
    assert "allauth.socialaccount" not in settings.INSTALLED_APPS
    assert "allauth.socialaccount.providers.google" not in settings.INSTALLED_APPS
    assert "web.cart.models" not in sys.modules
    assert "web.orders.models" not in sys.modules
    assert "stripe" not in sys.modules
    assert reverse("products:product_list") == "/products/"
    assert reverse("survey:survey_welcome") == "/survey/"
    assert reverse("waitlist:join_waitlist") == "/waitlist/join/"

    from django.contrib.auth.models import AnonymousUser
    from django.contrib.messages.storage.fallback import FallbackStorage
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.template.loader import render_to_string
    from django.test import RequestFactory

    request = RequestFactory().get("/")
    SessionMiddleware(lambda request: None).process_request(request)
    request.user = AnonymousUser()
    request._messages = FallbackStorage(request)

    home_html = render_to_string("home.html", request=request)
    assert 'href="/cart/' not in home_html
    assert 'href="/orders/' not in home_html

    survey_html = render_to_string("survey/survey_welcome.html", request=request)
    waitlist_html = render_to_string(
        "waitlist/join_waitlist.html",
        {"signup_count": 0},
        request=request,
    )
    assert "Start Survey" in survey_html
    assert "Join the TreadJoy Waitlist" in waitlist_html
    assert 'href="/cart/' not in survey_html + waitlist_html
    assert 'href="/orders/' not in survey_html + waitlist_html

    class ResearchUser:
        is_authenticated = True
        username = "research-user"
        email = "research@example.com"

    request.user = ResearchUser()
    profile_html = render_to_string("account/profile.html", request=request)
    assert "/orders/" not in profile_html
    assert "View Order History" not in profile_html

    class EmptyVariants:
        def count(self):
            return 0

        def all(self):
            return []

    class ResearchProduct:
        id = 1
        name = "Research Product"
        image = None
        price = "100.00"
        sale_price = None
        description = "Research-only product page."
        variants = EmptyVariants()

        def get_audience_display(self):
            return "All"

        def get_category_display(self):
            return "Shoes"

    product_html = render_to_string(
        "products/product_detail.html",
        {"product": ResearchProduct()},
        request=request,
    )
    assert "/cart/add/" not in product_html
    assert "Add to Cart" not in product_html
"""


class DeploymentModeProcessTests(SimpleTestCase):
    project_root = Path(__file__).resolve().parents[3]

    def test_bare_runserver_uses_safe_local_defaults(self):
        environment = os.environ.copy()
        for name in (
            "TREADJOY_ENVIRONMENT",
            "TREADJOY_MODE",
            "SECRET_KEY",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWORD",
            "DB_HOST",
            "DB_PORT",
            "TREADJOY_RUNSERVER_DEFAULTS",
        ):
            environment[name] = ""
        environment["STRIPE_SECRET_KEY"] = ""
        environment["STRIPE_WEBHOOK_SECRET"] = ""
        environment["PYTHONPATH"] = str(self.project_root)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import os, sys; os.environ['DJANGO_SETTINGS_MODULE'] = 'Shoes.settings'; "
                "sys.argv = ['manage.py', 'runserver']; "
                "from manage import _configure_runserver_defaults; "
                "_configure_runserver_defaults(); import django; django.setup(); "
                "from django.conf import settings; "
                "assert settings.TREADJOY_ENVIRONMENT == 'local'; "
                "assert settings.TREADJOY_MODE == 'research'; "
                "assert settings.DATABASES['default']['ENGINE'] == "
                "'django.db.backends.sqlite3'",
            ],
            # Run outside the repository so an ignored developer .env file
            # cannot affect this genuinely unconfigured startup check.
            cwd="/tmp",
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def environment_for(self, mode):
        environment = os.environ.copy()
        for name in list(environment):
            if name.startswith("STRIPE_"):
                environment.pop(name)
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "Shoes.settings",
                "TREADJOY_ENVIRONMENT": "local",
                "TREADJOY_MODE": mode,
                "TREADJOY_INGRESS": "direct",
                "SECRET_KEY": "mode-boundary-test-secret-key",
                "DJANGO_DEBUG": "True",
                "ALLOWED_HOSTS": "localhost,testserver",
                "DB_NAME": "mode_boundary_test",
                "DB_USER": "mode_boundary_test",
                "DB_PASSWORD": "mode_boundary_test",
                "DB_HOST": "127.0.0.1",
                "DB_PORT": "5432",
                "STRIPE_SECRET_KEY": "",
                "STRIPE_WEBHOOK_SECRET": "",
            }
        )
        return environment

    def run_setup(self, environment, script=DJANGO_SETUP_PROBE):
        return subprocess.run(
            [sys.executable, "-c", script],
            cwd=self.project_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def assert_process_succeeded(self, result):
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_commerce_mode_registers_order_taking_capabilities(self):
        environment = self.environment_for("commerce")
        environment.update(
            {
                "STRIPE_SECRET_KEY": "sk_test_mode_boundary",
                "STRIPE_WEBHOOK_SECRET": "whsec_mode_boundary",
            }
        )

        self.assert_process_succeeded(self.run_setup(environment))

    def test_research_mode_excludes_order_taking_capabilities(self):
        environment = self.environment_for("research")

        self.assert_process_succeeded(self.run_setup(environment))

    def test_missing_or_invalid_mode_fails_during_startup(self):
        for mode in ("", "staging"):
            with self.subTest(mode=mode or "missing"):
                environment = self.environment_for(mode)

                result = self.run_setup(
                    environment,
                    "import django; django.setup()",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "Invalid configuration for TREADJOY_MODE",
                    result.stderr,
                )

    def test_commerce_mode_requires_every_stripe_setting(self):
        stripe_settings = {
            "STRIPE_SECRET_KEY": "sk_test_mode_boundary",
            "STRIPE_WEBHOOK_SECRET": "whsec_mode_boundary",
        }

        for missing_name in stripe_settings:
            with self.subTest(missing_name=missing_name):
                environment = self.environment_for("commerce")
                environment.update(stripe_settings)
                environment[missing_name] = ""

                result = self.run_setup(
                    environment,
                    "import django; django.setup()",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    f"Invalid configuration for {missing_name}: "
                    "a non-empty value is required",
                    result.stderr,
                )

    def test_research_mode_rejects_stripe_credentials(self):
        environment = self.environment_for("research")
        environment["STRIPE_SECRET_KEY"] = "sk_test_must_not_be_loaded"

        result = self.run_setup(environment, "import django; django.setup()")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Stripe configuration must not be present when "
            "TREADJOY_MODE='research': STRIPE_SECRET_KEY",
            result.stderr,
        )


class CISettingsProcessTests(SimpleTestCase):
    project_root = Path(__file__).resolve().parents[3]

    def environment(self):
        environment = os.environ.copy()
        for name in list(environment):
            if name.startswith("STRIPE_"):
                environment.pop(name)
        environment.update(
            {
                "DJANGO_SETTINGS_MODULE": "Shoes.ci_settings",
                "TREADJOY_CI": "true",
                "TREADJOY_ENVIRONMENT": "ci",
                "TREADJOY_MODE": "research",
                "TREADJOY_INGRESS": "direct",
                "SECRET_KEY": "ci-settings-process-test-secret-key",
                "DJANGO_DEBUG": "True",
                "ALLOWED_HOSTS": "localhost,testserver",
                "DB_NAME": "treadjoy_ci",
                "DB_USER": "treadjoy_ci",
                "DB_PASSWORD": "ci-settings-process-test-password",
                "DB_HOST": "127.0.0.1",
                "DB_PORT": "5432",
                "CI_DB_TEST_NAME": "treadjoy_ci_test",
                "CI_STATIC_ROOT": "/tmp/treadjoy-ci-settings-static",
                "STRIPE_SECRET_KEY": "",
                "STRIPE_WEBHOOK_SECRET": "",
            }
        )
        return environment

    def run_setup(self, environment, script="import django; django.setup()"):
        return subprocess.run(
            [sys.executable, "-c", script],
            cwd=self.project_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def assert_failed_with(self, environment, message):
        result = self.run_setup(environment)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)

    def test_valid_ci_settings_define_isolated_test_services(self):
        result = self.run_setup(
            self.environment(),
            """
import django
django.setup()
from django.conf import settings
assert settings.DATABASES["default"]["TEST"]["NAME"] == "treadjoy_ci_test"
assert str(settings.STATIC_ROOT) == "/tmp/treadjoy-ci-settings-static"
assert settings.EMAIL_BACKEND == "django.core.mail.backends.locmem.EmailBackend"
""",
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_ci_settings_require_explicit_guard(self):
        environment = self.environment()
        environment["TREADJOY_CI"] = ""

        self.assert_failed_with(
            environment,
            "Shoes.ci_settings requires TREADJOY_CI=true",
        )

    def test_ci_settings_require_the_ci_environment(self):
        environment = self.environment()
        environment["TREADJOY_ENVIRONMENT"] = "local"

        self.assert_failed_with(
            environment,
            "Shoes.ci_settings requires TREADJOY_ENVIRONMENT=ci",
        )

    def test_ci_settings_require_a_distinct_test_database(self):
        environment = self.environment()
        environment["CI_DB_TEST_NAME"] = environment["DB_NAME"]

        self.assert_failed_with(
            environment,
            "CI_DB_TEST_NAME must differ from DB_NAME",
        )

    def test_ci_settings_require_an_absolute_static_root(self):
        environment = self.environment()
        environment["CI_STATIC_ROOT"] = "relative/staticfiles"

        self.assert_failed_with(
            environment,
            "CI_STATIC_ROOT must be an absolute path",
        )
