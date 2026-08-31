"""Transactional double-opt-in and suppression workflows."""

import base64
import hashlib
import hmac
from datetime import timedelta

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from .models import (
    ConsentEvent,
    EmailSuppression,
    ResearchOutboundEmail,
    SubscriptionSource,
    SubscriptionStatus,
    WaitlistSubscription,
)


CONFIRMATION_LIFETIME = timedelta(hours=72)
PENDING_IDENTITY_LIFETIME = timedelta(days=7)
MAX_CONFIRMATION_SENDS_PER_DAY = 3


def _lock_identity_digest(digest: str) -> None:
    """Serialize same-address requests, including the first insert, on PostgreSQL."""
    if connection.vendor != "postgresql":
        return
    lock_key = int(digest[:16], 16)
    if lock_key >= 2**63:
        lock_key -= 2**64
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", (lock_key,))


def normalize_email(email: str) -> str:
    return email.strip().lower()


def identity_digest(email: str) -> str:
    return hmac.new(
        settings.RESEARCH_IDENTITY_HMAC_KEY.encode(),
        normalize_email(email).encode(),
        hashlib.sha256,
    ).hexdigest()


def _raw_token(subscription: WaitlistSubscription, purpose: str) -> str:
    timestamp = subscription.requested_at if purpose == "confirm" else subscription.confirmed_at
    material = f"{purpose}:{subscription.public_id}:{timestamp.isoformat()}".encode()
    raw = hmac.new(settings.RESEARCH_IDENTITY_HMAC_KEY.encode(), material, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def confirmation_token(subscription: WaitlistSubscription) -> str:
    return _raw_token(subscription, "confirm")


def unsubscribe_token(subscription: WaitlistSubscription) -> str:
    return _raw_token(subscription, "unsubscribe")


@transaction.atomic
def request_subscription(*, email: str, source: str) -> WaitlistSubscription | None:
    """Create or refresh a pending request without disclosing prior state."""
    normalized = normalize_email(email)
    now = timezone.now()
    digest = identity_digest(normalized)
    _lock_identity_digest(digest)
    source = source if source in SubscriptionSource.values else SubscriptionSource.UNKNOWN

    subscription = (
        WaitlistSubscription.objects.select_for_update()
        .filter(email__iexact=normalized)
        .first()
    )
    if subscription and subscription.status == SubscriptionStatus.ACTIVE:
        return subscription

    recent_sends = ResearchOutboundEmail.objects.filter(
        destination_digest=digest,
        purpose=ResearchOutboundEmail.Purpose.CONFIRMATION,
        created_at__gte=now - timedelta(hours=24),
    ).count()
    if recent_sends >= MAX_CONFIRMATION_SENDS_PER_DAY:
        return subscription

    suppression = EmailSuppression.objects.select_for_update().filter(destination_digest=digest).first()
    had_current_suppression = bool(suppression and suppression.superseded_at is None)
    if had_current_suppression:
        suppression.superseded_at = now
        suppression.save(update_fields=("superseded_at",))

    prior_status = subscription.status if subscription else None
    if subscription is None:
        subscription = WaitlistSubscription(email=normalized)
    subscription.email = normalized
    subscription.status = SubscriptionStatus.PENDING
    subscription.source = source
    subscription.notice_version = settings.RESEARCH_PRIVACY_NOTICE_VERSION
    subscription.requested_at = now
    subscription.confirmation_expires_at = now + CONFIRMATION_LIFETIME
    subscription.confirmed_at = None
    subscription.last_affirmative_interaction_at = now
    subscription.unsubscribed_at = None
    subscription.unsubscribe_token_digest = ""
    raw_token = confirmation_token(subscription)
    subscription.confirmation_token_digest = token_digest(raw_token)
    subscription.save()
    event_kind = (
        ConsentEvent.Kind.RESUBSCRIBED
        if had_current_suppression
        or prior_status in {SubscriptionStatus.UNSUBSCRIBED, SubscriptionStatus.SUPPRESSED}
        else ConsentEvent.Kind.REQUESTED
    )
    ConsentEvent.objects.create(
        subscription=subscription,
        kind=event_kind,
        notice_version=subscription.notice_version,
        source=source,
    )
    ResearchOutboundEmail.objects.create(
        subscription=subscription,
        destination_digest=digest,
        purpose=ResearchOutboundEmail.Purpose.CONFIRMATION,
        template_version=subscription.notice_version,
    )
    return subscription


@transaction.atomic
def confirm_subscription(token: str) -> tuple[WaitlistSubscription | None, str]:
    digest = token_digest(token)
    subscription = WaitlistSubscription.objects.select_for_update().filter(confirmation_token_digest=digest).first()
    if subscription is None:
        return None, "invalid"
    if subscription.status == SubscriptionStatus.ACTIVE:
        return subscription, "active"
    now = timezone.now()
    if subscription.status != SubscriptionStatus.PENDING or not subscription.confirmation_expires_at or subscription.confirmation_expires_at < now:
        return subscription, "expired"
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.confirmed_at = now
    subscription.last_affirmative_interaction_at = now
    subscription.confirmation_token_digest = ""
    subscription.confirmation_expires_at = None
    subscription.unsubscribe_token_digest = token_digest(unsubscribe_token(subscription))
    subscription.save()
    ConsentEvent.objects.create(
        subscription=subscription,
        kind=ConsentEvent.Kind.CONFIRMED,
        notice_version=subscription.notice_version,
        source=subscription.source,
    )
    return subscription, "confirmed"


@transaction.atomic
def unsubscribe_subscription(token: str) -> tuple[WaitlistSubscription | None, str]:
    digest = token_digest(token)
    subscription = WaitlistSubscription.objects.select_for_update().filter(unsubscribe_token_digest=digest).first()
    if subscription is None:
        return None, "invalid"
    if subscription.status in {SubscriptionStatus.UNSUBSCRIBED, SubscriptionStatus.SUPPRESSED}:
        return subscription, "inactive"
    now = timezone.now()
    if not subscription.email:
        return subscription, "inactive"
    destination_digest = identity_digest(subscription.email)
    EmailSuppression.objects.update_or_create(
        destination_digest=destination_digest,
        defaults={"reason": "unsubscribe", "provider_contact_id": subscription.provider_contact_id, "superseded_at": None},
    )
    subscription.status = SubscriptionStatus.UNSUBSCRIBED
    subscription.unsubscribed_at = now
    subscription.last_affirmative_interaction_at = now
    subscription.email = None
    subscription.unsubscribe_token_digest = ""
    subscription.save()
    ConsentEvent.objects.create(
        subscription=subscription,
        kind=ConsentEvent.Kind.UNSUBSCRIBED,
        notice_version=subscription.notice_version,
        source=subscription.source,
    )
    return subscription, "unsubscribed"


@transaction.atomic
def suppress_subscription(subscription: WaitlistSubscription, *, reason: str) -> None:
    subscription = WaitlistSubscription.objects.select_for_update().get(pk=subscription.pk)
    if not subscription.email:
        return
    digest = identity_digest(subscription.email)
    EmailSuppression.objects.update_or_create(
        destination_digest=digest,
        defaults={"reason": reason[:32], "provider_contact_id": subscription.provider_contact_id, "superseded_at": None},
    )
    subscription.status = SubscriptionStatus.SUPPRESSED
    subscription.email = None
    subscription.confirmation_token_digest = ""
    subscription.unsubscribe_token_digest = ""
    subscription.save()
    ConsentEvent.objects.create(
        subscription=subscription,
        kind=ConsentEvent.Kind.SUPPRESSED,
        notice_version=subscription.notice_version,
        source=subscription.source,
    )
