from datetime import timedelta

from django.contrib import admin
from django.contrib import messages
from django.db import connection, transaction
from django.utils import timezone

from .providers import ResearchEmailProviderError, send_broadcast

from .models import (
    ConsentEvent,
    EmailSuppression,
    MarketingBroadcast,
    ResearchAbuseMetric,
    ResearchOutboundEmail,
    ResendWebhookEvent,
    WaitlistSubscription,
)

BROADCAST_MONTHLY_CAP_LOCK_ID = 2026083002


class ReadOnlyResearchAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(WaitlistSubscription)
class WaitlistSubscriptionAdmin(ReadOnlyResearchAdmin):
    list_display = ("public_id", "status", "source", "requested_at", "confirmed_at", "updated_at")
    list_filter = ("status", "source")
    search_fields = ("=public_id", "=provider_contact_id")
    exclude = ("email", "confirmation_token_digest", "unsubscribe_token_digest")


@admin.register(ConsentEvent)
class ConsentEventAdmin(ReadOnlyResearchAdmin):
    list_display = ("subscription", "kind", "notice_version", "source", "created_at")
    list_filter = ("kind", "notice_version", "source")


@admin.register(EmailSuppression)
class EmailSuppressionAdmin(ReadOnlyResearchAdmin):
    list_display = ("id", "reason", "created_at", "superseded_at")
    exclude = ("destination_digest",)


@admin.register(ResearchOutboundEmail)
class ResearchOutboundEmailAdmin(ReadOnlyResearchAdmin):
    list_display = ("id", "purpose", "status", "attempt_count", "created_at", "sent_at")
    list_filter = ("purpose", "status")
    exclude = ("destination_digest",)


@admin.register(ResendWebhookEvent)
class ResendWebhookEventAdmin(ReadOnlyResearchAdmin):
    list_display = ("svix_id", "event_type", "outcome", "received_at", "processed_at")
    list_filter = ("event_type", "outcome")


@admin.register(MarketingBroadcast)
class MarketingBroadcastAdmin(ReadOnlyResearchAdmin):
    list_display = ("provider_broadcast_id", "status", "approved_by", "approved_at", "sent_at", "recipient_count")
    list_filter = ("status",)
    actions = ("approve_and_send",)
    fields = ("provider_broadcast_id",)

    def has_add_permission(self, request):
        return request.user.has_perm("waitlist.approve_marketingbroadcast")

    def has_approve_permission(self, request):
        return request.user.has_perm("waitlist.approve_marketingbroadcast")

    @admin.action(description="Approve and send selected provider drafts", permissions=("approve",))
    def approve_and_send(self, request, queryset):
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        draft_ids = list(
            queryset.filter(status=MarketingBroadcast.Status.DRAFT).values_list(
                "pk", flat=True
            )
        )
        queued = []
        with transaction.atomic():
            if connection.vendor == "postgresql":
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock(%s)",
                        (BROADCAST_MONTHLY_CAP_LOCK_ID,),
                    )
            existing = MarketingBroadcast.objects.filter(
                status__in=(
                    MarketingBroadcast.Status.QUEUED,
                    MarketingBroadcast.Status.SENT,
                ),
                approved_at__gte=month_start,
                approved_at__lt=next_month,
            ).count()
            drafts = list(
                MarketingBroadcast.objects.select_for_update()
                .filter(pk__in=draft_ids, status=MarketingBroadcast.Status.DRAFT)
                .order_by("pk")
            )
            if existing + len(drafts) > 2:
                self.message_user(
                    request,
                    "This action would exceed two research broadcasts in the current UTC month.",
                    level=messages.ERROR,
                )
                return
            recipient_count = WaitlistSubscription.objects.filter(
                status="active"
            ).count()
            for locked in drafts:
                locked.status = MarketingBroadcast.Status.QUEUED
                locked.approved_by = request.user
                locked.approved_at = now
                locked.recipient_count = recipient_count
                locked.save()
                queued.append(locked)
        for locked in queued:
            try:
                send_broadcast(locked.provider_broadcast_id)
            except ResearchEmailProviderError:
                locked.status = MarketingBroadcast.Status.FAILED
                locked.save(update_fields=("status", "updated_at"))
                self.message_user(request, "A provider draft could not be sent and remains recorded for review.", level=messages.ERROR)
            else:
                locked.status = MarketingBroadcast.Status.SENT
                locked.sent_at = timezone.now()
                locked.save(update_fields=("status", "sent_at", "updated_at"))


@admin.register(ResearchAbuseMetric)
class ResearchAbuseMetricAdmin(ReadOnlyResearchAdmin):
    list_display = ("day", "action", "kind", "count")
    list_filter = ("action", "kind")
