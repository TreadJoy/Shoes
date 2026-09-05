import time
from types import SimpleNamespace
from unittest.mock import Mock, patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings
from jwt.exceptions import PyJWKClientConnectionError

from Shoes.cloudflare_access import (
    AccessKeyServiceUnavailable,
    AccessTokenInvalid,
    verify_access_token,
)
from Shoes.middleware import CloudflareOriginLockMiddleware


TEAM_DOMAIN = "https://unit-test.cloudflareaccess.com"
AUDIENCE = "unit_test_access_audience_0123456789"
OWNER_EMAIL = "owner@example.com"


@override_settings(
    CLOUDFLARE_ACCESS_TEAM_DOMAIN=TEAM_DOMAIN,
    CLOUDFLARE_ACCESS_AUD=AUDIENCE,
    CLOUDFLARE_ACCESS_ALLOWED_EMAIL=OWNER_EMAIL,
)
class CloudflareAccessTokenTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.public_key = cls.private_key.public_key()

    def token(self, **overrides):
        now = int(time.time())
        claims = {
            "aud": [AUDIENCE],
            "email": OWNER_EMAIL,
            "exp": now + 300,
            "iat": now,
            "iss": TEAM_DOMAIN,
            "sub": "owner-subject",
            "type": "app",
        }
        claims.update(overrides)
        return jwt.encode(
            claims,
            self.private_key,
            algorithm="RS256",
            headers={"kid": "unit-test-key"},
        )

    def client_for(self, key=None):
        client = Mock()
        client.get_signing_key_from_jwt.return_value = SimpleNamespace(
            key=key or self.public_key
        )
        return client

    @patch("Shoes.cloudflare_access._jwks_client")
    def test_valid_application_token_is_accepted(self, jwks_client):
        jwks_client.return_value = self.client_for()

        claims = verify_access_token(self.token())

        self.assertEqual(claims["email"], OWNER_EMAIL)
        jwks_client.assert_called_once_with(TEAM_DOMAIN)

    @patch("Shoes.cloudflare_access._jwks_client")
    def test_invalid_claims_or_signature_are_rejected(self, jwks_client):
        other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cases = (
            self.token(aud=["another-application"]),
            self.token(iss="https://another.cloudflareaccess.com"),
            self.token(email="someone-else@example.com"),
            self.token(type="org"),
            self.token(exp=int(time.time()) - 120),
            jwt.encode(
                {
                    "aud": [AUDIENCE],
                    "email": OWNER_EMAIL,
                    "exp": int(time.time()) + 300,
                    "iat": int(time.time()),
                    "iss": TEAM_DOMAIN,
                    "sub": "owner-subject",
                    "type": "app",
                },
                other_key,
                algorithm="RS256",
                headers={"kid": "unit-test-key"},
            ),
        )
        jwks_client.return_value = self.client_for()

        for token in cases:
            with self.subTest(token=token[:20]):
                with self.assertRaises(AccessTokenInvalid):
                    verify_access_token(token)

    @patch("Shoes.cloudflare_access._jwks_client")
    def test_signing_key_outage_fails_closed_without_claiming_bad_identity(
        self, jwks_client
    ):
        client = Mock()
        client.get_signing_key_from_jwt.side_effect = PyJWKClientConnectionError(
            "synthetic outage"
        )
        jwks_client.return_value = client

        with self.assertRaises(AccessKeyServiceUnavailable):
            verify_access_token(self.token())


@override_settings(
    IS_PUBLIC_ENVIRONMENT=True,
    CLOUDFLARE_ACCESS_REQUIRED=True,
    TREADJOY_ORIGIN_SHARED_SECRET="origin-secret",
)
class CloudflareAccessMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.middleware = CloudflareOriginLockMiddleware(
            lambda request: HttpResponse("ok")
        )
        self.factory = RequestFactory()

    def request(self, *, token="signed-token", path="/"):
        return self.factory.get(
            path,
            HTTP_X_TREADJOY_ORIGIN="origin-secret",
            HTTP_CF_ACCESS_JWT_ASSERTION=token,
        )

    @patch("Shoes.middleware.verify_access_token")
    def test_requires_both_origin_secret_and_access_token(self, verify_token):
        def reject_missing_token(token):
            if not token:
                raise AccessTokenInvalid
            return {}

        verify_token.side_effect = reject_missing_token
        missing_origin = self.middleware(
            self.factory.get("/", HTTP_CF_ACCESS_JWT_ASSERTION="signed-token")
        )
        missing_token = self.middleware(
            self.factory.get("/", HTTP_X_TREADJOY_ORIGIN="origin-secret")
        )

        self.assertEqual(missing_origin.status_code, 403)
        self.assertEqual(missing_token.status_code, 403)
        self.assertEqual(missing_origin.headers["Cache-Control"], "no-store")
        self.assertEqual(missing_token.headers["Cache-Control"], "no-store")
        verify_token.assert_called_once_with("")

    @patch("Shoes.middleware.verify_access_token")
    def test_valid_access_token_reaches_django(self, verify_token):
        verify_token.return_value = {"email": OWNER_EMAIL}

        response = self.middleware(self.request())

        self.assertEqual(response.status_code, 200)

    @patch("Shoes.middleware.verify_access_token")
    def test_invalid_token_is_forbidden(self, verify_token):
        verify_token.side_effect = AccessTokenInvalid

        response = self.middleware(self.request())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    @patch("Shoes.middleware.verify_access_token")
    def test_key_service_outage_is_unavailable(self, verify_token):
        verify_token.side_effect = AccessKeyServiceUnavailable

        response = self.middleware(self.request())

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    @patch("Shoes.middleware.verify_access_token")
    def test_generic_health_paths_remain_directly_available(self, verify_token):
        response = self.middleware(self.factory.get("/health/ready/"))

        self.assertEqual(response.status_code, 200)
        verify_token.assert_not_called()
