"""Safe liveness and dependency-aware readiness endpoints."""

from __future__ import annotations

from django.db import connections
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from treadjoy.observability import emit_alert


def _response(status: str, status_code: int) -> JsonResponse:
    response = JsonResponse({"status": status}, status=status_code)
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@require_GET
def live(request):
    """Report that the Django process can accept a request."""

    return _response("ok", 200)


def _database_is_ready() -> bool:
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        # Do not log the provider exception: it can contain hostnames,
        # credentials, SQL, or other details unsuitable for an edge endpoint.
        return False
    return True


@require_GET
def ready(request):
    """Report whether the application can reach its authoritative database."""

    if not _database_is_ready():
        emit_alert(
            "database_unavailable",
            "critical",
            "Readiness dependency check failed.",
            dedupe_key="research-default-database",
        )
        return _response("unavailable", 503)
    return _response("ok", 200)
