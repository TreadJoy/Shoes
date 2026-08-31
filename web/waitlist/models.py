"""Consent, suppression, and bounded delivery records for research email."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class SubscriptionStatus(models.TextChoices):
    LEGACY_QUARANTINED = "legacy_quarantined", "Legacy quarantined"
    PENDING = "pending", "Pending confirmation"
    ACTIVE = "active", "Active"
    UNSUBSCRIBED = "unsubscribed", "Unsubscribed"
    SUPPRESSED = "suppressed", "Suppressed"
    EXPIRED = "expired", "Expired"


class SubscriptionSource(models.TextChoices):
    HOMEPAGE = "homepage", "Homepage"
    WAITLIST_PAGE = "waitlist_page", "Waitlist page"
    UNKNOWN = "unknown", "Unknown"


class WaitlistSubscription(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(null=True, blank=True)
    status = models.CharField(max_length=24, choices=SubscriptionStatus.choices, default=SubscriptionStatus.PENDING, db_index=True)
    source = models.CharField(max_length=20, choices=SubscriptionSource.choices, default=SubscriptionSource.UNKNOWN)
    notice_version = models.CharField(max_length=50, blank=True)
    confirmation_token_digest = models.CharField(max_length=64, blank=True)
    confirmation_expires_at = models.DateTimeField(null=True, blank=True)
    unsubscribe_token_digest = models.CharField(max_length=64, blank=True)
    requested_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    last_affirmative_interaction_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    provider_contact_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), condition=Q(email__isnull=False), name="waitlist_subscription_email_ci_unique"),
            models.UniqueConstraint(fields=("confirmation_token_digest",), condition=~Q(confirmation_token_digest=""), name="waitlist_confirmation_digest_unique"),
            models.UniqueConstraint(fields=("unsubscribe_token_digest",), condition=~Q(unsubscribe_token_digest=""), name="waitlist_unsubscribe_digest_unique"),
            models.UniqueConstraint(fields=("provider_contact_id",), condition=~Q(provider_contact_id=""), name="waitlist_provider_contact_unique"),
            models.CheckConstraint(
                condition=(
                    Q(status__in=(SubscriptionStatus.LEGACY_QUARANTINED, SubscriptionStatus.EXPIRED))
                    | Q(status=SubscriptionStatus.PENDING, email__isnull=False, confirmation_token_digest__gt="", confirmation_expires_at__isnull=False)
                    | Q(status=SubscriptionStatus.ACTIVE, email__isnull=False, confirmed_at__isnull=False, unsubscribe_token_digest__gt="")
                    | Q(status__in=(SubscriptionStatus.UNSUBSCRIBED, SubscriptionStatus.SUPPRESSED), email__isnull=True)
                ),
                name="waitlist_subscription_state_consistent",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        if self.source not in SubscriptionSource.values:
            self.source = SubscriptionSource.UNKNOWN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Subscription {self.public_id} ({self.get_status_display()})"


class ConsentEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Consent events are append-only.")

    def delete(self):
        raise ValidationError("Consent events are append-only.")


class ConsentEvent(models.Model):
    class Kind(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        UNSUBSCRIBED = "unsubscribed", "Unsubscribed"
        SUPPRESSED = "suppressed", "Suppressed"
        RESUBSCRIBED = "resubscribed", "Resubscribed"
        EXPIRED = "expired", "Expired"

    subscription = models.ForeignKey(WaitlistSubscription, on_delete=models.PROTECT, related_name="consent_events")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    notice_version = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=20, choices=SubscriptionSource.choices, default=SubscriptionSource.UNKNOWN)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ConsentEventQuerySet.as_manager()

    class Meta:
        ordering = ("created_at", "pk")

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Consent events are append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Consent events are append-only.")


class EmailSuppression(models.Model):
    destination_digest = models.CharField(max_length=64, unique=True)
    reason = models.CharField(max_length=32)
    provider_contact_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    superseded_at = models.DateTimeField(null=True, blank=True)


class ResearchOutboundEmail(models.Model):
    class Purpose(models.TextChoices):
        CONFIRMATION = "confirmation", "Confirmation"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        DELAYED = "delayed", "Delayed"
        FAILED = "failed", "Failed"
        BOUNCED = "bounced", "Bounced"
        COMPLAINED = "complained", "Complained"
        SUPPRESSED = "suppressed", "Suppressed"
        CANCELED = "canceled", "Canceled"

    subscription = models.ForeignKey(WaitlistSubscription, null=True, blank=True, on_delete=models.SET_NULL, related_name="outbound_emails")
    destination_digest = models.CharField(max_length=64)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    template_version = models.CharField(max_length=50)
    idempotency_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    provider_message_id = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    attempt_count = models.PositiveSmallIntegerField(default=0)
    error_code = models.CharField(max_length=80, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    last_provider_event_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("provider_message_id",),
                condition=~Q(provider_message_id=""),
                name="research_outbound_provider_message_unique",
            )
        ]


class ResendWebhookEvent(models.Model):
    svix_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=50)
    provider_created_at = models.DateTimeField(null=True, blank=True)
    outcome = models.CharField(max_length=32, blank=True)
    error_code = models.CharField(max_length=80, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)


class MarketingBroadcast(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    provider_broadcast_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="approved_research_broadcasts")
    approved_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    recipient_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [("approve_marketingbroadcast", "Can approve a research broadcast")]


class ResearchAbuseMetric(models.Model):
    day = models.DateField()
    action = models.CharField(max_length=32)
    kind = models.CharField(max_length=32)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("day", "action", "kind"), name="research_abuse_metric_unique")]
