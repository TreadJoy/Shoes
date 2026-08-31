from unittest import skipIf, skipUnless

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from web.products.models import PartType
from web.waitlist.models import ResearchOutboundEmail, WaitlistSubscription


class HomepageModeTests(TestCase):
    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce-mode homepage test")
    def test_commerce_home_prioritizes_categories_without_waitlist(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shop Men →")
        self.assertContains(response, "Shop Women →")
        self.assertContains(response, "How Compatibility Works →")
        self.assertContains(response, 'href="/products/?audience=men"')
        self.assertContains(response, 'href="/products/?audience=women"')
        self.assertContains(response, 'href="/how-it-works/"')
        self.assertNotContains(response, "Waitlist")
        self.assertNotContains(response, "waitlist")
        self.assertNotContains(response, "Help Shape What Comes Next")
        self.assertNotContains(response, "Add to Cart")
        self.assertNotContains(response, "data-product-card")
        self.assertNotIn("waitlist_form", response.context)
        self.assertContains(response, 'static/css/home.css')
        self.assertContains(response, 'static/js/home.js')

    @skipIf(settings.IS_COMMERCE_MODE, "Research-mode homepage test")
    def test_research_home_prioritizes_waitlist_survey_and_preview_links(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Join the Waitlist")
        self.assertContains(response, "Take the Survey →")
        self.assertContains(response, "Explore Men →")
        self.assertContains(response, "Explore Women →")
        self.assertContains(response, 'href="/products/?audience=men"')
        self.assertContains(response, 'href="/products/?audience=women"')
        self.assertContains(response, 'href="/how-it-works/"')
        self.assertContains(response, 'action="/waitlist/join/homepage/"')
        self.assertContains(response, "novalidate")
        self.assertNotContains(response, "Shop Men →")
        self.assertNotContains(response, "Shop Women →")
        self.assertNotContains(response, "Add to Cart")
        self.assertNotContains(response, 'href="/cart/')
        self.assertNotContains(response, 'href="/orders/')
        self.assertIn("waitlist_form", response.context)

    @skipUnless(settings.IS_COMMERCE_MODE, "Commerce-mode homepage test")
    def test_commerce_post_to_home_is_rejected(self):
        response = self.client.post(
            reverse("core:home"),
            {"first_name": "Jo", "email": "jo@example.com"},
        )

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.headers["Allow"], "GET")
        self.assertFalse(WaitlistSubscription.objects.exists())

    @skipIf(settings.IS_COMMERCE_MODE, "Research-mode homepage test")
    def test_research_home_join_endpoint_creates_pending_email_only_request(self):
        response = self.client.post(
            reverse("waitlist:join_homepage"),
            {"email": "Jo@Example.COM", "consent": "on"},
        )

        self.assertRedirects(
            response,
            f"{reverse('core:home')}#home-waitlist",
            fetch_redirect_response=False,
        )
        signup = WaitlistSubscription.objects.get()
        self.assertEqual(signup.email, "jo@example.com")
        self.assertEqual(signup.source, "homepage")
        self.assertEqual(signup.status, "pending")
        self.assertEqual(ResearchOutboundEmail.objects.count(), 1)

    @skipIf(settings.IS_COMMERCE_MODE, "Research-mode homepage test")
    def test_research_home_duplicate_is_idempotent(self):
        first = self.client.post(
            reverse("waitlist:join_homepage"),
            {"email": "jo@example.com", "consent": "on"},
        )
        second = self.client.post(
            reverse("waitlist:join_homepage"),
            {"email": "JO@EXAMPLE.COM", "consent": "on"},
            follow=True,
        )

        self.assertEqual(first.status_code, 302)
        self.assertContains(second, "Check your email if your address is eligible")
        self.assertEqual(WaitlistSubscription.objects.count(), 1)
        signup = WaitlistSubscription.objects.get()
        self.assertEqual(signup.source, "homepage")

    @skipIf(settings.IS_COMMERCE_MODE, "Research-mode homepage test")
    def test_research_home_rejects_post_and_join_page_renders_field_errors(self):
        response = self.client.post(
            reverse("core:home"),
            {"email": "jo@example..com", "consent": "on"},
        )
        self.assertEqual(response.status_code, 405)
        response = self.client.post(reverse("waitlist:join_waitlist"), {"email": "jo@example..com", "consent": "on"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")
        self.assertFalse(WaitlistSubscription.objects.exists())

    def test_home_uses_the_six_authoritative_modular_part_types(self):
        response = self.client.get(reverse("core:home"))

        displayed_names = [
            part_type.name
            for part_type in response.context["modular_part_types"]
        ]
        expected_names = list(
            PartType.objects.filter(is_active=True)
            .values_list("name", flat=True)[:6]
        )
        self.assertEqual(displayed_names, expected_names)
        self.assertEqual(len(displayed_names), 6)

    @override_settings(
        HOMEPAGE_YOUTUBE_VIDEO_ID="https://www.youtube.com/live/dQw4w9WgXcQ",
        HOMEPAGE_YOUTUBE_TITLE="TreadJoy live session",
    )
    def test_valid_video_configuration_renders_deferred_play_control(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "data-video-play")
        self.assertContains(
            response,
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
        )
        self.assertContains(response, "TreadJoy live session")
        self.assertNotContains(response, "<iframe")

    @override_settings(
        HOMEPAGE_YOUTUBE_VIDEO_ID="https://example.com/not-youtube",
        HOMEPAGE_YOUTUBE_TITLE="Untrusted video",
    )
    def test_invalid_video_configuration_renders_static_placeholder(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "YouTube Development Placeholder")
        self.assertNotContains(response, "data-video-play")
        self.assertNotContains(response, "youtube-nocookie.com")
        self.assertNotContains(response, "<iframe")

    def test_home_assets_are_not_loaded_by_other_pages(self):
        response = self.client.get(reverse("core:about"))

        self.assertNotContains(response, "static/css/home.css")
        self.assertNotContains(response, "static/js/home.js")
