from django.test import TestCase
from django.urls import reverse

from web.waitlist.models import WaitlistSignup


class WaitlistFlowTests(TestCase):
    def test_valid_signup_is_normalized_and_duplicate_is_not_created(self):
        first = self.client.post(
            reverse("waitlist:join_waitlist"),
            {"first_name": "  Jo  ", "email": "Jo@Example.COM"},
            follow=True,
        )
        second = self.client.post(
            reverse("waitlist:join_waitlist"),
            {"first_name": "Different", "email": "jo@example.com"},
            follow=True,
        )

        self.assertContains(first, "joined the waitlist successfully")
        self.assertContains(second, "already on the waitlist")
        self.assertEqual(WaitlistSignup.objects.count(), 1)
        signup = WaitlistSignup.objects.get()
        self.assertEqual(signup.email, "jo@example.com")
        self.assertEqual(signup.first_name, "Jo")

    def test_server_rejects_malformed_email_that_bypasses_browser_validation(self):
        response = self.client.post(
            reverse("waitlist:join_waitlist"),
            {"first_name": "Jo", "email": "jo@example..com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")
        self.assertFalse(WaitlistSignup.objects.exists())

    def test_server_rejects_overlong_name_without_database_error(self):
        response = self.client.post(
            reverse("waitlist:join_waitlist"),
            {"first_name": "x" * 101, "email": "long@example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "at most 100 characters")
        self.assertFalse(WaitlistSignup.objects.exists())

