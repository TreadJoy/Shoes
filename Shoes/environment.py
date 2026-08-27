"""Strict, redacted environment parsing for TreadJoy settings."""

from __future__ import annotations

import ipaddress
import re
from pathlib import Path
from urllib.parse import urlsplit

from decouple import config
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import validate_email


_HOSTNAME_RE = re.compile(
    r"(?=.{1,253}\Z)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\Z"
)


def _error(name: str, message: str) -> None:
    """Raise an actionable error without ever including a setting value."""
    raise ImproperlyConfigured(f"Invalid configuration for {name}: {message}.")


def string(name: str, *, default: str | None = None, required: bool = False) -> str:
    value = config(name, default=default)
    value = "" if value is None else str(value).strip()
    if required and not value:
        _error(name, "a non-empty value is required")
    return value


def choice(name: str, choices: set[str], *, default: str | None = None) -> str:
    value = string(name, default=default, required=default is None)
    if value not in choices:
        _error(name, f"must be one of {', '.join(sorted(choices))}")
    return value


def boolean(name: str, *, default: bool | None = None, required: bool = False) -> bool:
    raw_default = None if default is None else ("true" if default else "false")
    value = string(name, default=raw_default, required=required)
    if not value and default is None:
        _error(name, "must be set to true or false")
    normalized = value.casefold()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    _error(name, "must be set to true or false")
    raise AssertionError("unreachable")


def integer(
    name: str,
    *,
    minimum: int,
    maximum: int,
    default: int | None = None,
    required: bool = False,
) -> int:
    raw_default = None if default is None else str(default)
    value = string(name, default=raw_default, required=required)
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        _error(name, "must be an integer")
    if not minimum <= parsed <= maximum:
        _error(name, f"must be between {minimum} and {maximum}")
    return parsed


def csv(name: str, *, default: str | None = None, required: bool = False) -> tuple[str, ...]:
    value = string(name, default=default, required=required)
    if not value:
        return ()
    values = tuple(item.strip() for item in value.split(","))
    if any(not item for item in values):
        _error(name, "must not contain empty entries")
    if len(set(values)) != len(values):
        _error(name, "must not contain duplicates")
    return values


def hostname(name: str, value: str, *, allow_ip_address: bool) -> str:
    value = value.casefold()
    if value == "*" or "://" in value or "/" in value or ":" in value:
        _error(name, "must contain hostnames only")
    try:
        ipaddress.ip_address(value)
    except ValueError:
        if not _HOSTNAME_RE.fullmatch(value):
            _error(name, "contains an invalid hostname")
    else:
        if not allow_ip_address:
            _error(name, "must not contain an IP address")
    return value


def public_hosts(values: tuple[str, ...]) -> tuple[str, ...]:
    if not values:
        _error("ALLOWED_HOSTS", "at least one hostname is required")
    normalized = tuple(
        hostname("ALLOWED_HOSTS", value, allow_ip_address=False) for value in values
    )
    if len(set(normalized)) != len(normalized):
        _error("ALLOWED_HOSTS", "must not contain duplicates")
    return normalized


def https_origins(values: tuple[str, ...], *, allowed_hosts: tuple[str, ...]) -> tuple[str, ...]:
    if not values:
        _error("CSRF_TRUSTED_ORIGINS", "at least one HTTPS origin is required")

    normalized: list[str] = []
    for value in values:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            _error("CSRF_TRUSTED_ORIGINS", "must contain HTTPS origins only")
        host = hostname("CSRF_TRUSTED_ORIGINS", parsed.hostname, allow_ip_address=False)
        if host not in allowed_hosts:
            _error("CSRF_TRUSTED_ORIGINS", "hosts must also appear in ALLOWED_HOSTS")
        normalized.append(f"https://{parsed.netloc.casefold()}")

    if len(set(normalized)) != len(normalized):
        _error("CSRF_TRUSTED_ORIGINS", "must not contain duplicates")
    return tuple(normalized)


def absolute_path(name: str, *, required: bool = True) -> Path | None:
    value = string(name, required=required)
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        _error(name, "must be an absolute path")
    return path


def email_address(name: str, *, required: bool = True, default: str | None = None) -> str:
    value = string(name, required=required, default=default)
    if not value:
        return value
    try:
        validate_email(value)
    except ValidationError:
        _error(name, "must be a valid email address")
    return value


def strong_secret(name: str, *, required: bool = True) -> str:
    value = string(name, required=required)
    if not value:
        return value
    if (
        len(value) < 50
        or len(set(value)) < 5
        or value.startswith("django-insecure-")
        or value.startswith("replace-with-")
    ):
        _error(name, "must be a generated production-strength secret")
    return value
