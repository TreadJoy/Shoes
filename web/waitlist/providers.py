"""Narrow Resend adapter. Provider packages are imported only inside job calls."""

from django.conf import settings
from django.urls import reverse

from .services import confirmation_token


class ResearchEmailProviderError(RuntimeError):
    pass


def _base_url() -> str:
    if settings.IS_PUBLIC_ENVIRONMENT:
        return f"https://{settings.ALLOWED_HOSTS[0]}"
    return "http://localhost:8000"


def send_confirmation(outbound) -> str:
    subscription = outbound.subscription
    if not subscription or not subscription.email:
        raise ResearchEmailProviderError("recipient_unavailable")
    url = _base_url() + reverse(
        "waitlist:confirm", args=[confirmation_token(subscription)]
    )
    text = (
        "Confirm your TreadJoy research updates subscription.\n\n"
        f"Open this page, then choose Confirm subscription: {url}\n\n"
        "The link expires after 72 hours. If you did not request this, ignore this message."
    )
    html = (
        "<h1>Confirm Your TreadJoy Updates</h1>"
        "<p>Open the confirmation page, then choose <strong>Confirm subscription</strong>.</p>"
        f'<p><a href="{url}">Review and confirm</a></p>'
        "<p>This link expires after 72 hours. If you did not request this, ignore this message.</p>"
    )
    if settings.RESEARCH_EMAIL_PROVIDER == "fake":
        return f"fake-{outbound.idempotency_key}"
    try:
        import resend

        resend.api_key = settings.RESEARCH_RESEND_SEND_API_KEY
        result = resend.Emails.send(
            {
                "from": settings.RESEARCH_EMAIL_TRANSACTIONAL_FROM,
                "to": [subscription.email],
                "reply_to": settings.RESEARCH_EMAIL_REPLY_TO,
                "subject": "Confirm your TreadJoy updates",
                "text": text,
                "html": html,
                "headers": {"X-Entity-Ref-ID": str(outbound.idempotency_key)},
            },
            {"idempotency_key": str(outbound.idempotency_key)},
        )
        return result["id"]
    except Exception as exc:
        raise ResearchEmailProviderError(type(exc).__name__) from exc


def verify_webhook(raw_body: bytes, headers: dict[str, str]) -> dict:
    try:
        import resend

        return resend.Webhooks.verify(
            {
                "payload": raw_body.decode("utf-8"),
                "headers": {
                    "id": headers["svix-id"],
                    "timestamp": headers["svix-timestamp"],
                    "signature": headers["svix-signature"],
                },
                "webhook_secret": settings.RESEARCH_RESEND_WEBHOOK_SECRET,
            }
        )
    except Exception as exc:
        raise ResearchEmailProviderError("invalid_webhook_signature") from exc


def upsert_contact(subscription) -> str:
    if settings.RESEARCH_EMAIL_PROVIDER == "fake":
        return subscription.provider_contact_id or f"fake-contact-{subscription.public_id}"
    if not settings.RESEARCH_RESEND_MANAGEMENT_API_KEY:
        raise ResearchEmailProviderError("management_key_unavailable")
    try:
        import resend

        resend.api_key = settings.RESEARCH_RESEND_MANAGEMENT_API_KEY
        result = resend.Contacts.create(
            {"email": subscription.email, "unsubscribed": False}
        )
        contact_id = result["id"]
        resend.ContactSegments.add(
            {"contact_id": contact_id, "segment_id": settings.RESEARCH_RESEND_SEGMENT_ID}
        )
        return contact_id
    except Exception as exc:
        raise ResearchEmailProviderError(type(exc).__name__) from exc


def send_broadcast(provider_broadcast_id: str) -> None:
    if settings.RESEARCH_EMAIL_PROVIDER == "fake":
        return
    if not settings.RESEARCH_RESEND_MANAGEMENT_API_KEY:
        raise ResearchEmailProviderError("management_key_unavailable")
    try:
        import resend

        resend.api_key = settings.RESEARCH_RESEND_MANAGEMENT_API_KEY
        resend.Broadcasts.send({"broadcast_id": provider_broadcast_id})
    except Exception as exc:
        raise ResearchEmailProviderError(type(exc).__name__) from exc
