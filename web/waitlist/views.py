from datetime import timedelta

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from web.core.rate_limits import consume_session_limit, record_abuse_metric, throttled_response
from web.core.forms import focus_first_error

from .forms import WaitlistSubscriptionForm
from .models import ResearchOutboundEmail, ResendWebhookEvent, WaitlistSubscription
from .providers import ResearchEmailProviderError, verify_webhook
from .services import confirm_subscription, request_subscription, suppress_subscription, unsubscribe_subscription


NEUTRAL_JOIN_MESSAGE = "Check your email if your address is eligible for TreadJoy updates."
ALLOWED_WEBHOOK_EVENTS = {
    "email.sent",
    "email.delivered",
    "email.delivery_delayed",
    "email.failed",
    "email.bounced",
    "email.complained",
    "email.suppressed",
    "contact.updated",
    "contact.deleted",
}
EMAIL_STATUS_MAP = {
    "email.sent": ResearchOutboundEmail.Status.SENT,
    "email.delivered": ResearchOutboundEmail.Status.DELIVERED,
    "email.delivery_delayed": ResearchOutboundEmail.Status.DELAYED,
    "email.failed": ResearchOutboundEmail.Status.FAILED,
    "email.bounced": ResearchOutboundEmail.Status.BOUNCED,
    "email.complained": ResearchOutboundEmail.Status.COMPLAINED,
    "email.suppressed": ResearchOutboundEmail.Status.SUPPRESSED,
}
STATUS_RANK = {
    ResearchOutboundEmail.Status.PENDING: 0,
    ResearchOutboundEmail.Status.SENT: 1,
    ResearchOutboundEmail.Status.DELAYED: 2,
    ResearchOutboundEmail.Status.DELIVERED: 3,
    ResearchOutboundEmail.Status.FAILED: 3,
    ResearchOutboundEmail.Status.BOUNCED: 4,
    ResearchOutboundEmail.Status.COMPLAINED: 4,
    ResearchOutboundEmail.Status.SUPPRESSED: 4,
    ResearchOutboundEmail.Status.CANCELED: 4,
}
TERMINAL_EMAIL_STATUSES = {
    ResearchOutboundEmail.Status.BOUNCED,
    ResearchOutboundEmail.Status.COMPLAINED,
    ResearchOutboundEmail.Status.SUPPRESSED,
    ResearchOutboundEmail.Status.CANCELED,
}


def _handle_join(request, *, source: str, redirect_name: str, fragment: str = ""):
    retry_after = consume_session_limit(
        request, key="research_waitlist_posts", limit=5, window=timedelta(hours=1)
    )
    if retry_after:
        record_abuse_metric(action="waitlist", kind="session_throttle")
        return throttled_response(request, retry_after)
    form = WaitlistSubscriptionForm(request.POST)
    if form.is_valid():
        if form.cleaned_data["company_website"]:
            record_abuse_metric(action="waitlist", kind="honeypot")
        else:
            request_subscription(email=form.cleaned_data["email"], source=source)
        messages.info(request, NEUTRAL_JOIN_MESSAGE)
        destination = redirect_name
        if fragment:
            destination = f"{redirect(redirect_name).url}{fragment}"
            return redirect(destination)
        return redirect(redirect_name)
    focus_first_error(form)
    return form


def join_waitlist(request):
    if request.method == "POST":
        result = _handle_join(request, source="waitlist_page", redirect_name="waitlist:join_waitlist")
        if not isinstance(result, WaitlistSubscriptionForm):
            return result
        form = result
    elif request.method == "GET":
        form = WaitlistSubscriptionForm()
    else:
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(request, "waitlist/join_waitlist.html", {"form": form})


@require_POST
def join_homepage(request):
    result = _handle_join(
        request,
        source="homepage",
        redirect_name="core:home",
        fragment="#home-waitlist",
    )
    if isinstance(result, WaitlistSubscriptionForm):
        return render(request, "waitlist/join_waitlist.html", {"form": result})
    return result


def confirm(request, token):
    if request.method == "POST":
        _, outcome = confirm_subscription(token)
        return render(request, "waitlist/confirm_result.html", {"outcome": outcome})
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(request, "waitlist/confirm.html", {"token": token})


def unsubscribe(request, token):
    if request.method == "POST":
        _, outcome = unsubscribe_subscription(token)
        return render(request, "waitlist/unsubscribe_result.html", {"outcome": outcome})
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(request, "waitlist/unsubscribe.html", {"token": token})


def _event_data(payload):
    data = payload.get("data", {})
    return data if isinstance(data, dict) else {}


def _provider_created_at(payload):
    try:
        return parse_datetime(str(payload.get("created_at", "")))
    except (AttributeError, TypeError, ValueError):
        return None


@csrf_exempt
@require_POST
def resend_webhook(request):
    signature_headers = {
        "svix-id": request.headers.get("svix-id", ""),
        "svix-timestamp": request.headers.get("svix-timestamp", ""),
        "svix-signature": request.headers.get("svix-signature", ""),
    }
    if not all(signature_headers.values()):
        return HttpResponse(status=400)
    try:
        payload = verify_webhook(request.body, signature_headers)
    except ResearchEmailProviderError:
        return HttpResponse(status=400)
    event_type = str(payload.get("type", ""))[:50]
    if event_type not in ALLOWED_WEBHOOK_EVENTS:
        return HttpResponse(status=204)

    try:
        with transaction.atomic():
            event, created = ResendWebhookEvent.objects.get_or_create(
                svix_id=signature_headers["svix-id"][:100],
                defaults={
                    "event_type": event_type,
                    "provider_created_at": _provider_created_at(payload),
                },
            )
            if not created:
                return HttpResponse(status=204)
            data = _event_data(payload)
            if event_type.startswith("email."):
                provider_id = str(data.get("email_id") or data.get("id") or "")[:100]
                outbound = ResearchOutboundEmail.objects.select_for_update().filter(provider_message_id=provider_id).first()
                if outbound:
                    new_status = EMAIL_STATUS_MAP[event_type]
                    event_at = event.provider_created_at
                    is_terminal = new_status in TERMINAL_EMAIL_STATUSES
                    current_is_terminal = outbound.status in TERMINAL_EMAIL_STATUSES
                    is_newer = (
                        event_at is not None
                        and (
                            outbound.last_provider_event_at is None
                            or event_at >= outbound.last_provider_event_at
                        )
                    )
                    should_apply = (
                        (is_terminal and not current_is_terminal)
                        or (is_terminal and current_is_terminal and is_newer)
                        or (not current_is_terminal and is_newer)
                        or (
                            not current_is_terminal
                            and event_at is None
                            and STATUS_RANK[new_status] >= STATUS_RANK[outbound.status]
                        )
                    )
                    if should_apply:
                        outbound.status = new_status
                        if event_at is not None:
                            outbound.last_provider_event_at = event_at
                        outbound.save(
                            update_fields=(
                                "status",
                                "last_provider_event_at",
                                "updated_at",
                            )
                        )
                    if is_terminal and outbound.subscription:
                        suppress_subscription(outbound.subscription, reason=event_type.removeprefix("email."))
            else:
                contact_id = str(data.get("id") or data.get("contact_id") or "")[:100]
                subscription = WaitlistSubscription.objects.select_for_update().filter(provider_contact_id=contact_id).first()
                if subscription and (event_type == "contact.deleted" or data.get("unsubscribed") is True):
                    suppress_subscription(subscription, reason="provider_contact_change")
            event.outcome = "processed"
            event.processed_at = timezone.now()
            event.save(update_fields=("outcome", "processed_at"))
    except IntegrityError:
        return HttpResponse(status=204)
    return HttpResponse(status=204)
