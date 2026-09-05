"""Fail-closed Cloudflare Access application-token verification."""

from __future__ import annotations

import hmac
from functools import lru_cache
from typing import Any

import jwt
from django.conf import settings
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError, PyJWTError


_MAX_TOKEN_LENGTH = 16_384
_CLOCK_SKEW_SECONDS = 30


class AccessTokenInvalid(Exception):
    """The presented token is absent, malformed, or not authorized."""


class AccessKeyServiceUnavailable(Exception):
    """Cloudflare's signing keys could not be retrieved safely."""


@lru_cache(maxsize=4)
def _jwks_client(team_domain: str) -> PyJWKClient:
    """Reuse Cloudflare's signing-key cache while permitting key rotation."""
    return PyJWKClient(
        f"{team_domain}/cdn-cgi/access/certs",
        cache_jwk_set=True,
        lifespan=300,
        cache_keys=True,
        max_cached_keys=16,
        timeout=5,
    )


def verify_access_token(token: str) -> dict[str, Any]:
    """Verify signature, application audience, issuer, lifetime, and owner."""
    if not token or len(token) > _MAX_TOKEN_LENGTH:
        raise AccessTokenInvalid

    try:
        signing_key = _jwks_client(
            settings.CLOUDFLARE_ACCESS_TEAM_DOMAIN
        ).get_signing_key_from_jwt(token)
    except PyJWKClientConnectionError as exc:
        raise AccessKeyServiceUnavailable from exc
    except PyJWTError as exc:
        raise AccessTokenInvalid from exc

    try:
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.CLOUDFLARE_ACCESS_AUD,
            issuer=settings.CLOUDFLARE_ACCESS_TEAM_DOMAIN,
            leeway=_CLOCK_SKEW_SECONDS,
            options={"require": ["aud", "exp", "iat", "iss", "sub"]},
        )
    except PyJWTError as exc:
        raise AccessTokenInvalid from exc

    email = claims.get("email")
    token_type = claims.get("type")
    if not isinstance(email, str) or not hmac.compare_digest(
        email.casefold(), settings.CLOUDFLARE_ACCESS_ALLOWED_EMAIL.casefold()
    ):
        raise AccessTokenInvalid
    if token_type != "app":
        raise AccessTokenInvalid

    return claims
