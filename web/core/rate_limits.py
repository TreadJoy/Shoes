"""Small session-scoped research throttles with no cross-session identifiers."""

from datetime import timedelta

from django.db.models import F
from django.utils import timezone
from django.shortcuts import render


def throttled_response(request, retry_after: int):
    response = render(request, "429.html", {"retry_after": retry_after}, status=429)
    response["Retry-After"] = str(retry_after)
    return response


def consume_session_limit(request, *, key: str, limit: int, window: timedelta) -> int | None:
    now = timezone.now()
    cutoff = (now - window).timestamp()
    timestamps = [value for value in request.session.get(key, []) if value >= cutoff]
    if len(timestamps) >= limit:
        retry_after = max(1, int(timestamps[0] + window.total_seconds() - now.timestamp()) + 1)
        request.session[key] = timestamps
        return retry_after
    timestamps.append(now.timestamp())
    request.session[key] = timestamps
    request.session.modified = True
    return None


def completed_within(request, *, key: str, window: timedelta) -> int | None:
    completed = request.session.get(key)
    if not completed:
        return None
    remaining = completed + window.total_seconds() - timezone.now().timestamp()
    return max(1, int(remaining) + 1) if remaining > 0 else None


def record_abuse_metric(*, action: str, kind: str) -> None:
    from web.waitlist.models import ResearchAbuseMetric

    metric, created = ResearchAbuseMetric.objects.get_or_create(
        day=timezone.now().date(), action=action[:32], kind=kind[:32], defaults={"count": 1}
    )
    if not created:
        ResearchAbuseMetric.objects.filter(pk=metric.pk).update(count=F("count") + 1)
