from decimal import Decimal
from unittest import skipIf

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from web.products.models import Product, ProductVariant
from web.survey.models import SurveyResponse
from web.waitlist.models import ResearchOutboundEmail, WaitlistSubscription


@skipIf(settings.IS_COMMERCE_MODE, "Research-only launch rehearsal")
class ResearchLaunchRehearsalTests(TestCase):
    """Exercise the private research POC's synthetic launch smoke path."""

    def setUp(self):
        product = Product.objects.create(
            name="Synthetic Research Shoe",
            slug="synthetic-research-shoe",
            description="Synthetic fixture; never a public claim.",
            price=Decimal("100.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="SYNTHETIC-RESEARCH-090-BLK",
            size="9",
            color="Black",
            stock_quantity=2,
        )

    def test_smoke_surfaces_and_private_poc_state(self):
        smoke_routes = (
            reverse("core:home"),
            reverse("products:product_list"),
            reverse("products:product_detail", args=[self.variant.product.slug]),
            reverse("waitlist:join_waitlist"),
            reverse("survey:survey_welcome"),
            reverse("core:privacy"),
            reverse("core:terms"),
            reverse("core:accessibility"),
            reverse("core:contact"),
        )

        for route in smoke_routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                body = response.content.decode(response.charset or "utf-8")
                self.assertNotIn("add to cart", body.casefold())
                self.assertNotIn("checkout", body.casefold())

        not_found = self.client.get("/synthetic-rehearsal-not-found/")
        self.assertEqual(not_found.status_code, 404)

        waitlist_response = self.client.post(
            reverse("waitlist:join_waitlist"),
            {"email": "research-smoke@example.invalid", "consent": "on"},
        )
        self.assertEqual(waitlist_response.status_code, 302)
        self.assertEqual(WaitlistSubscription.objects.count(), 1)
        self.assertEqual(ResearchOutboundEmail.objects.count(), 1)

        survey_steps = (
            (1, "style_preference", "athletic"),
            (2, "comfort_importance", "very_important"),
            (3, "price_range", "100_150"),
            (4, "favorite_brand", "Synthetic Brand"),
            (5, "additional_feedback", "Synthetic rehearsal feedback."),
        )
        for number, field_name, value in survey_steps:
            response = self.client.post(
                reverse("survey:survey_question", args=[number]),
                {field_name: value},
            )
            self.assertIn(response.status_code, (302, 303))
        self.assertEqual(SurveyResponse.objects.count(), 1)

    def test_waitlist_throttle_is_a_rehearsed_429_state(self):
        for index in range(5):
            response = self.client.post(
                reverse("waitlist:join_waitlist"),
                {
                    "email": f"research-throttle-{index}@example.invalid",
                    "consent": "on",
                },
            )
            self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse("waitlist:join_waitlist"),
            {"email": "research-throttle-blocked@example.invalid", "consent": "on"},
        )
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response)
        self.assertContains(
            response, "Please Wait Before Trying Again", status_code=429
        )
