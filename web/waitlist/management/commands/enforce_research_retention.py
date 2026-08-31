from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from web.survey.models import SurveyResponse
from web.waitlist.models import ConsentEvent, EmailSuppression, ResearchOutboundEmail, SubscriptionStatus, WaitlistSubscription


class Command(BaseCommand):
    help = "Report or enforce the approved research retention policy in bounded batches."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--policy-version", default="")
        parser.add_argument("--batch-size", type=int, default=500)

    def handle(self, *args, **options):
        if settings.IS_COMMERCE_MODE:
            raise CommandError("enforce_research_retention only runs in research mode.")
        now = timezone.now()
        cutoffs = {
            "pending_identity": now - timedelta(days=7),
            "survey": now - timedelta(days=730),
            "inactive_active": now - timedelta(days=730),
            "evidence": now - timedelta(days=1825),
            "delivery": now - timedelta(days=730),
        }
        terminal_statuses = (
            SubscriptionStatus.UNSUBSCRIBED,
            SubscriptionStatus.SUPPRESSED,
            SubscriptionStatus.EXPIRED,
        )
        terminal_event_kinds = (
            ConsentEvent.Kind.UNSUBSCRIBED,
            ConsentEvent.Kind.SUPPRESSED,
            ConsentEvent.Kind.EXPIRED,
        )
        evidence_subscription_ids = WaitlistSubscription.objects.filter(
            status__in=terminal_statuses,
        ).annotate(
            terminal_at=Max(
                "consent_events__created_at",
                filter=Q(consent_events__kind__in=terminal_event_kinds),
            )
        ).filter(
            terminal_at__lt=cutoffs["evidence"],
        ).values_list("pk", flat=True)
        suppression_evidence = EmailSuppression.objects.annotate(
            retention_started_at=Coalesce("superseded_at", "created_at")
        ).filter(retention_started_at__lt=cutoffs["evidence"])
        consent_evidence = ConsentEvent.objects.filter(
            subscription_id__in=evidence_subscription_ids
        )
        counts = {
            "pending_identity": WaitlistSubscription.objects.filter(status=SubscriptionStatus.PENDING, requested_at__lt=cutoffs["pending_identity"]).count(),
            "survey": SurveyResponse.objects.filter(created_at__lt=cutoffs["survey"]).count(),
            "inactive_active": WaitlistSubscription.objects.filter(status=SubscriptionStatus.ACTIVE, last_affirmative_interaction_at__lt=cutoffs["inactive_active"]).count(),
            "consent_evidence": consent_evidence.count(),
            "suppression_evidence": suppression_evidence.count(),
            "delivery": ResearchOutboundEmail.objects.filter(created_at__lt=cutoffs["delivery"]).count(),
        }
        self.stdout.write(" ".join(f"{key}={value}" for key, value in counts.items()))
        if not options["apply"]:
            self.stdout.write("dry_run=true")
            return
        configured = settings.RESEARCH_RETENTION_POLICY_VERSION
        if (
            not configured
            or "draft" in configured.casefold()
            or options["policy_version"] != configured
        ):
            raise CommandError("Destructive retention requires a matching effective RESEARCH_RETENTION_POLICY_VERSION.")
        if options["batch_size"] < 1 or options["batch_size"] > 5000:
            raise CommandError("--batch-size must be between 1 and 5000.")
        batch_size = options["batch_size"]

        for status, cutoff_key in ((SubscriptionStatus.PENDING, "pending_identity"), (SubscriptionStatus.ACTIVE, "inactive_active")):
            date_field = "requested_at" if status == SubscriptionStatus.PENDING else "last_affirmative_interaction_at"
            while True:
                with transaction.atomic():
                    filters = {"status": status, f"{date_field}__lt": cutoffs[cutoff_key]}
                    records = list(WaitlistSubscription.objects.select_for_update().filter(**filters)[:batch_size])
                    for subscription in records:
                        ResearchOutboundEmail.objects.filter(subscription=subscription, status__in=("pending", "failed")).update(status="canceled", error_code="retention_expired")
                        subscription.email = None
                        subscription.status = SubscriptionStatus.EXPIRED
                        subscription.confirmation_token_digest = ""
                        subscription.unsubscribe_token_digest = ""
                        subscription.save()
                        ConsentEvent.objects.create(subscription=subscription, kind=ConsentEvent.Kind.EXPIRED, notice_version=subscription.notice_version, source=subscription.source)
                if len(records) < batch_size:
                    break

        for model, queryset in (
            (SurveyResponse, SurveyResponse.objects.filter(created_at__lt=cutoffs["survey"])),
            (ConsentEvent, consent_evidence),
            (EmailSuppression, suppression_evidence),
            (ResearchOutboundEmail, ResearchOutboundEmail.objects.filter(created_at__lt=cutoffs["delivery"])),
        ):
            while True:
                ids = list(queryset.values_list("pk", flat=True)[:batch_size])
                if not ids:
                    break
                with transaction.atomic():
                    model.objects.filter(pk__in=ids)._raw_delete(model.objects.db)
        self.stdout.write("applied=true")
