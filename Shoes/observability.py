"""Request correlation, safe structured logs, and provider-neutral alerts."""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any


REQUEST_ID_HEADER = "X-Request-ID"
request_id_context: ContextVar[str | None] = ContextVar(
    "treadjoy_request_id", default=None
)

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_SECRET_VALUE_RE = re.compile(
    r"(?i)\b(?P<key>authorization|password|secret|token|api[_-]?key|"
    r"access[_-]?key|refresh[_-]?token)\b\s*[:=]\s*[^\s,;]+"
)
_PROVIDER_SECRET_RE = re.compile(
    r"\b(?:sk|pk|whsec|re)_(?:live|test)?[A-Za-z0-9_\-]+\b", re.IGNORECASE
)
_WAITLIST_TOKEN_PATH_RE = re.compile(
    r"(?P<prefix>/waitlist/(?:confirm|unsubscribe)/)[^/]+(?P<suffix>/?)",
    re.IGNORECASE,
)
_REQUEST_ID_RE = re.compile(r"^[0-9a-fA-F-]{16,64}$")
_ALERT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{1,79}$")


def normalize_request_id(value: str | None) -> str:
    """Accept only UUID request IDs; generate a safe ID for all other input."""

    if value and _REQUEST_ID_RE.fullmatch(value.strip()):
        try:
            return str(uuid.UUID(value.strip()))
        except ValueError:
            pass
    return str(uuid.uuid4())


def redact_path(path: str) -> str:
    """Remove opaque confirmation/unsubscribe tokens from a URL path."""

    return _WAITLIST_TOKEN_PATH_RE.sub(r"\g<prefix>[REDACTED]\g<suffix>", path)


def redact_text(value: Any) -> str:
    """Return text safe for logs and monitoring payloads."""

    text = str(value)
    text = redact_path(text)
    text = _SECRET_VALUE_RE.sub(
        lambda match: f"{match.group('key')}=[REDACTED]", text
    )
    text = _PROVIDER_SECRET_RE.sub("[REDACTED_SECRET]", text)
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    return text


class RequestCorrelationMiddleware:
    """Propagate a validated request ID and emit one safe completion event."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = normalize_request_id(request.headers.get(REQUEST_ID_HEADER))
        request.request_id = request_id
        context_token = request_id_context.set(request_id)
        started = time.perf_counter()
        logger = logging.getLogger("Shoes.request")
        try:
            response = self.get_response(request)
        except Exception:
            logger.error(
                "request failed",
                extra={
                    "event": "request.failed",
                    "request_id": request_id,
                    "request_method": request.method,
                    "request_path": redact_path(request.path),
                    "status_code": 500,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            raise
        else:
            logger.info(
                "request completed",
                extra={
                    "event": "request.completed",
                    "request_id": request_id,
                    "request_method": request.method,
                    "request_path": redact_path(request.path),
                    "status_code": response.status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            response[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            request_id_context.reset(context_token)


class RequestContextFilter(logging.Filter):
    """Add the current request ID without copying request or user data."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not getattr(record, "request_id", None):
            request = getattr(record, "request", None)
            record.request_id = (
                getattr(request, "request_id", None) or request_id_context.get()
            )
        return True


class RedactionFilter(logging.Filter):
    """Redact secrets and direct identifiers before records reach a handler."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(record.getMessage())
        record.args = ()
        if hasattr(record, "request_path"):
            record.request_path = redact_path(redact_text(record.request_path))
        return True


class JsonFormatter(logging.Formatter):
    """Emit a small allow-listed JSON event rather than arbitrary record data."""

    _EXTRA_FIELDS = (
        "event",
        "request_id",
        "request_method",
        "request_path",
        "status_code",
        "duration_ms",
        "alert_name",
        "severity",
        "summary",
        "dedupe_key",
        "synthetic",
        "origin_header_present",
        "origin_header_length",
        "origin_secret_configured",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_text(record.getMessage()),
        }
        for field in self._EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = (
                    redact_path(redact_text(value))
                    if field == "request_path"
                    else redact_text(value)
                    if isinstance(value, str)
                    else value
                )
        if record.exc_info:
            payload["exception_type"] = record.exc_info[0].__name__
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


_ALERT_LEVELS = {
    "info": logging.INFO,
    "warning": logging.WARNING,
    "critical": logging.CRITICAL,
}


def emit_alert(
    alert_name: str,
    severity: str,
    summary: str,
    *,
    dedupe_key: str | None = None,
    synthetic: bool = False,
) -> None:
    """Emit an allow-listed alert event for the configured log monitor."""

    if not _ALERT_NAME_RE.fullmatch(alert_name):
        raise ValueError("alert_name must be a short lowercase identifier")
    if severity not in _ALERT_LEVELS:
        raise ValueError("severity must be info, warning, or critical")
    logging.getLogger("Shoes.alert").log(
        _ALERT_LEVELS[severity],
        "alert emitted",
        extra={
            "event": "alert",
            "alert_name": alert_name,
            "severity": severity,
            "dedupe_key": dedupe_key,
            "synthetic": synthetic,
            "summary": redact_text(summary),
        },
    )
