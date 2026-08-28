from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class AccountFlowTests(TestCase):
    password = "CorrectHorseBattery9!"

    def test_allauth_signup_login_logout_and_protected_profile(self):
        profile = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(
            profile,
            f"{reverse('account_login')}?next={reverse('accounts:profile')}",
        )

        signup = self.client.post(
            reverse("account_signup"),
            {
                "username": "newcustomer",
                "email": "newcustomer@example.com",
                "password1": self.password,
                "password2": self.password,
                "terms": "on",
            },
        )
        self.assertRedirects(signup, reverse("core:home"))
        self.assertTrue(
            get_user_model().objects.filter(username="newcustomer").exists()
        )
        self.assertEqual(
            self.client.get(reverse("accounts:profile")).status_code,
            200,
        )

        logout = self.client.post(reverse("account_logout"))
        self.assertRedirects(logout, reverse("core:home"))

        login = self.client.post(
            reverse("account_login"),
            {"login": "newcustomer", "password": self.password},
        )
        self.assertRedirects(login, reverse("core:home"))

    def test_legacy_signup_url_redirects_to_working_allauth_signup(self):
        response = self.client.get(reverse("accounts:signup"))

        self.assertRedirects(response, reverse("account_signup"))

    def test_password_reset_entry_accepts_known_email(self):
        get_user_model().objects.create_user(
            username="reset-user",
            email="reset@example.com",
            password=self.password,
        )

        response = self.client.post(
            reverse("account_reset_password"),
            {"email": "reset@example.com"},
        )

        self.assertEqual(response.status_code, 302)

    def test_admin_login_is_guarded_by_allauth_before_django_admin(self):
        response = self.client.get("/admin/login/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response["Location"].startswith(reverse("account_login"))
        )
