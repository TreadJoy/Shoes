from unittest import skipIf

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse


@skipIf(settings.IS_COMMERCE_MODE, "Research-only content contract")
class ResearchContentAndMetadataTests(TestCase):
    def test_private_local_pages_are_not_indexable(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(
            response, 'name="robots" content="noindex, nofollow, noarchive"'
        )
        self.assertContains(response, "Private TreadJoy development preview")
        self.assertNotContains(response, 'rel="canonical"')
        self.assertNotContains(response, 'property="og:url"')

    def test_public_metadata_uses_fixed_origin_and_excludes_session_routes(self):
        with override_settings(
            IS_PUBLIC_ENVIRONMENT=True,
            TREADJOY_PRIVATE_POC=False,
            TREADJOY_ORIGIN_SHARED_SECRET="public-origin-secret",
        ):
            response = self.client.get(
                reverse("core:home"),
                HTTP_X_TREADJOY_ORIGIN="public-origin-secret",
            )
            self.assertContains(
                response,
                '<link rel="canonical" href="https://research.tread-joy.com/">',
            )
            self.assertContains(response, 'property="og:url"')
            self.assertContains(response, 'name="twitter:card" content="summary"')
            self.assertContains(response, 'name="robots" content="index, follow"')

            waitlist = self.client.get(
                reverse("waitlist:join_waitlist"),
                HTTP_X_TREADJOY_ORIGIN="public-origin-secret",
            )
            self.assertContains(
                waitlist,
                'name="robots" content="noindex, nofollow, noarchive"',
            )
            self.assertNotContains(waitlist, 'rel="canonical"')
            self.assertNotContains(waitlist, 'property="og:url"')

    def test_private_poc_keeps_public_routes_noindex(self):
        with override_settings(
            IS_PUBLIC_ENVIRONMENT=True,
            TREADJOY_PRIVATE_POC=True,
            TREADJOY_ORIGIN_SHARED_SECRET="public-origin-secret",
        ):
            response = self.client.get(
                reverse("core:about"),
                HTTP_X_TREADJOY_ORIGIN="public-origin-secret",
            )

        self.assertContains(response, 'rel="canonical"')
        self.assertContains(
            response, 'name="robots" content="noindex, nofollow, noarchive"'
        )

    def test_robots_txt_is_private_by_default_and_uncached(self):
        response = self.client.get(reverse("core:robots"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(response.content.decode(), "User-agent: *\nDisallow: /\n")

    def test_public_robots_excludes_sensitive_paths(self):
        with override_settings(
            IS_PUBLIC_ENVIRONMENT=True,
            TREADJOY_PRIVATE_POC=False,
            TREADJOY_ORIGIN_SHARED_SECRET="public-origin-secret",
        ):
            response = self.client.get(
                reverse("core:robots"),
                HTTP_X_TREADJOY_ORIGIN="public-origin-secret",
            )

        self.assertContains(response, "Disallow: /admin/")
        self.assertContains(response, "Disallow: /waitlist/")
        self.assertNotContains(response, "Disallow: /\n")

    def test_policy_placeholders_and_contact_page_are_explicit(self):
        for route_name, title in (
            ("core:privacy", "Research Privacy Placeholder"),
            ("core:terms", "Terms Placeholder"),
            ("core:accessibility", "Accessibility Placeholder"),
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, title)
                self.assertContains(response, "contact@tread-joy.com")

        response = self.client.get(reverse("core:contact"))
        self.assertContains(response, "mailto:contact@tread-joy.com")
        self.assertNotContains(response, "ethan@tread-joy.com")

    def test_research_supporting_pages_use_editorial_shell_and_public_contact(self):
        for route_name in (
            "core:about",
            "core:contact",
            "waitlist:join_waitlist",
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertContains(response, "research-editorial-page")
                self.assertContains(response, "research-page-mark")

        for route_name, pending_copy in (
            ("core:privacy", "Not yet effective"),
            ("core:terms", "Not yet effective"),
            ("core:accessibility", "Working draft"),
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertContains(response, "research-policy-page")
                self.assertContains(response, pending_copy)
                self.assertContains(response, "contact@tread-joy.com")

    def test_social_destinations_use_configured_links_without_fake_targets(self):
        response = self.client.get(reverse("core:home"))

        for profile_url in (
            "https://www.instagram.com/treadjoy/",
            "https://x.com/TreadJoy",
            "https://www.youtube.com/@TreadJoy",
            "https://www.tiktok.com/@realtreadjoy",
        ):
            with self.subTest(profile_url=profile_url):
                self.assertContains(response, f'href="{profile_url}"', count=2)
        self.assertNotContains(response, 'href="#"')
