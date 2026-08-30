import re
import sys
from datetime import date, timedelta
from decimal import Decimal
from html.parser import HTMLParser
from io import StringIO
from types import SimpleNamespace
from unittest import skipIf
from unittest.mock import patch
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.checks import Error
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import DatabaseError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from web.core.checks import check_research_capability_boundary
from web.core.research_boundary import (
    database_observation_violations,
    runtime_boundary_violations,
    url_boundary_violations,
)
from web.products.models import (
    PreorderBatch,
    PreorderVariantAllocation,
    Product,
    ProductVariant,
)


class ResearchBoundaryEvaluationTests(SimpleTestCase):
    @skipIf(settings.IS_COMMERCE_MODE, "Research runtime contract")
    def test_current_runtime_has_no_violation(self):
        self.assertEqual(runtime_boundary_violations(), [])
        self.assertEqual(url_boundary_violations(), [])

    @skipIf(settings.IS_COMMERCE_MODE, "Research runtime contract")
    def test_runtime_detects_installed_app_context_setting_and_import(self):
        templates = [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "OPTIONS": {
                    "context_processors": [
                        "web.cart.context_processors.cart_summary",
                    ]
                },
            }
        ]
        with (
            patch(
                "web.core.research_boundary.apps.is_installed",
                side_effect=lambda name: name == "web.orders",
            ),
            patch.dict(sys.modules, {"stripe": object()}),
            override_settings(
                TEMPLATES=templates,
                STRIPE_SECRET_KEY="",
            ),
        ):
            violations = runtime_boundary_violations()

        self.assertTrue(any("web.orders" in item for item in violations))
        self.assertTrue(any("context processors" in item for item in violations))
        self.assertTrue(any("STRIPE_SECRET_KEY" in item for item in violations))
        self.assertTrue(any("stripe" in item for item in violations))

    @skipIf(settings.IS_COMMERCE_MODE, "Research runtime contract")
    def test_url_evaluation_detects_namespace_prefix_callback_and_import(self):
        def commerce_callback(request):
            raise AssertionError("The callback must never execute.")

        commerce_callback.__module__ = "web.orders.views"
        observed_routes = [
            ("orders/checkout/", ("orders",), commerce_callback),
        ]
        with (
            patch(
                "web.core.research_boundary.get_resolver",
                return_value=SimpleNamespace(url_patterns=()),
            ),
            patch(
                "web.core.research_boundary._walk_urlpatterns",
                return_value=observed_routes,
            ),
            patch.dict(sys.modules, {"web.orders": object()}),
        ):
            violations = url_boundary_violations()

        self.assertTrue(any("namespaces" in item for item in violations))
        self.assertTrue(any("prefixes" in item for item in violations))
        self.assertTrue(any("callbacks" in item for item in violations))
        self.assertTrue(any("resolving URLs" in item for item in violations))

    def test_database_evaluation_reports_every_forbidden_category(self):
        violations = database_observation_violations(
            table_names={"django_migrations", "orders_order", "cart_cart"},
            recorder_present=True,
            migration_count=2,
            migration_apps={"cart", "orders"},
            content_type_table_present=True,
            content_type_count=3,
        )

        self.assertEqual(
            violations,
            [
                "forbidden commerce tables present: 2",
                "forbidden commerce migration records present: 2",
                "forbidden commerce migrations loaded: cart, orders",
                "forbidden commerce content types present: 3",
            ],
        )

    @skipIf(settings.IS_COMMERCE_MODE, "Research deployment check")
    def test_deployment_check_uses_distinct_runtime_and_route_errors(self):
        with (
            patch(
                "web.core.checks.runtime_boundary_violations",
                return_value=["forbidden runtime"],
            ),
            patch(
                "web.core.checks.url_boundary_violations",
                return_value=["forbidden route"],
            ),
        ):
            errors = check_research_capability_boundary(None)

        self.assertEqual([error.id for error in errors], ["treadjoy.E010", "treadjoy.E011"])
        self.assertTrue(all(isinstance(error, Error) for error in errors))

    @override_settings(TREADJOY_MODE="commerce", IS_COMMERCE_MODE=True)
    def test_command_refuses_to_claim_success_in_commerce_mode(self):
        with self.assertRaisesMessage(
            CommandError,
            "must run with TREADJOY_MODE='research'",
        ):
            call_command("check_research_boundary")


@skipIf(settings.IS_COMMERCE_MODE, "Research database boundary")
class ResearchBoundaryCommandTests(TestCase):
    def test_command_accepts_the_clean_installed_research_database(self):
        output = StringIO()

        call_command("check_research_boundary", stdout=output)

        self.assertIn("Research capability boundary verified", output.getvalue())

    def test_command_fails_closed_on_database_violation(self):
        with patch(
            "web.core.management.commands.check_research_boundary."
            "database_boundary_violations",
            return_value=["forbidden commerce tables present: 1"],
        ):
            with self.assertRaisesMessage(
                CommandError,
                "forbidden commerce tables present: 1",
            ):
                call_command("check_research_boundary")

    def test_command_redacts_database_exception_detail(self):
        marker = "do-not-print-research-database-detail"
        with patch(
            "web.core.management.commands.check_research_boundary."
            "database_boundary_violations",
            side_effect=DatabaseError(marker),
        ):
            with self.assertRaises(CommandError) as raised:
                call_command("check_research_boundary")

        self.assertEqual(
            str(raised.exception),
            "Research boundary database inspection failed.",
        )
        self.assertNotIn(marker, str(raised.exception))


class _ReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "action", "formaction"} and value:
                self.references.append(value)


@skipIf(settings.IS_COMMERCE_MODE, "Research rendered surfaces")
class ResearchRenderedSurfaceTests(TestCase):
    def setUp(self):
        self.stocked_product = Product.objects.create(
            name="Research Stocked Preview",
            slug="research-stocked-preview",
            description="Synthetic research boundary fixture.",
            price=Decimal("100.00"),
        )
        ProductVariant.objects.create(
            product=self.stocked_product,
            sku="A21-STOCKED-090-BLK",
            size="9",
            color="Black",
            stock_quantity=4,
        )

        self.preorder_product = Product.objects.create(
            name="Research Preorder Preview",
            slug="research-preorder-preview",
            description="Synthetic research boundary fixture.",
            price=Decimal("110.00"),
        )
        preorder_variant = ProductVariant.objects.create(
            product=self.preorder_product,
            sku="A21-PREORDER-100-BLU",
            size="10",
            color="Blue",
            stock_quantity=0,
        )
        batch = PreorderBatch.objects.create(
            code="A21-RESEARCH-PREVIEW",
            product=self.preorder_product,
            estimated_tender_start=date.today() + timedelta(days=30),
            estimated_tender_end=date.today() + timedelta(days=45),
            total_capacity=5,
        )
        PreorderVariantAllocation.objects.create(
            batch=batch,
            variant=preorder_variant,
            capacity=5,
        )
        batch.status = PreorderBatch.Status.OPEN
        batch.save()

        self.user = get_user_model().objects.create_user(
            username="a21-research-user",
            email="a21-research@example.invalid",
            password="synthetic-test-password",
        )

    def assert_research_only_html(self, response):
        self.assertEqual(response.status_code, 200)
        html = response.content.decode(response.charset or "utf-8")
        parser = _ReferenceParser()
        parser.feed(html)
        for reference in parser.references:
            path = urlsplit(reference).path
            self.assertFalse(
                path.startswith(("/cart/", "/orders/")),
                reference,
            )
        self.assertIsNone(
            re.search(r"\b(add to cart|checkout|buy now)\b", html, re.IGNORECASE)
        )

    def test_public_and_authenticated_surfaces_emit_no_commerce_capability(self):
        anonymous_urls = (
            reverse("core:home"),
            reverse("core:about"),
            reverse("core:how_it_works"),
            reverse("core:contact"),
            reverse("products:product_list"),
            reverse("products:product_detail", args=[self.stocked_product.slug]),
            reverse("products:product_detail", args=[self.preorder_product.slug]),
            reverse("survey:survey_welcome"),
            reverse("waitlist:join_waitlist"),
            reverse("account_login"),
            reverse("account_signup"),
            reverse("account_reset_password"),
        )
        responses = [self.client.get(url) for url in anonymous_urls]

        self.client.force_login(self.user)
        responses.append(self.client.get(reverse("accounts:profile")))

        for response in responses:
            self.assert_research_only_html(response)

        for product in (self.stocked_product, self.preorder_product):
            response = self.client.get(
                reverse("products:product_detail", args=[product.slug])
            )
            self.assertContains(response, "Purchasing is unavailable")
            self.assertContains(response, "Research Preview")

        self.assertFalse(
            any(
                name == prefix or name.startswith(f"{prefix}.")
                for name in sys.modules
                for prefix in ("web.cart", "web.orders", "stripe")
            )
        )
