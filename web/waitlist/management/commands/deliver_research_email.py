from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from web.waitlist.models import ResearchOutboundEmail
from web.waitlist.providers import ResearchEmailProviderError, send_confirmation


class Command(BaseCommand):
    help = "Deliver bounded research email outbox records."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        if settings.IS_COMMERCE_MODE:
            raise CommandError("deliver_research_email only runs in research mode.")
        limit = options["limit"]
        if limit < 1 or limit > 1000:
            raise CommandError("--limit must be between 1 and 1000.")
        ids = list(
            ResearchOutboundEmail.objects.filter(
                status__in=(ResearchOutboundEmail.Status.PENDING, ResearchOutboundEmail.Status.FAILED),
            )
            .filter(Q(next_attempt_at__isnull=True) | Q(next_attempt_at__lte=timezone.now()))
            .order_by("created_at")
            .values_list("pk", flat=True)[:limit]
        )
        delivered = failed = canceled = 0
        for pk in ids:
            with transaction.atomic():
                # ``subscription`` is nullable because retention may redact it.  On
                # PostgreSQL, locking a queryset that includes that nullable
                # ``select_related`` join fails with ``FOR UPDATE cannot be
                # applied to the nullable side of an outer join``.  Lock only
                # the outbox row; the joined subscription data is still loaded
                # for the decision below.
                outbound = (
                    ResearchOutboundEmail.objects.select_for_update(of=("self",))
                    .select_related("subscription")
                    .get(pk=pk)
                )
                outbound.attempt_count += 1
                if not outbound.subscription or not outbound.subscription.email:
                    outbound.status = ResearchOutboundEmail.Status.CANCELED
                    outbound.error_code = "recipient_unavailable"
                    outbound.save()
                    canceled += 1
                    continue
                try:
                    provider_id = send_confirmation(outbound)
                except ResearchEmailProviderError as exc:
                    outbound.status = ResearchOutboundEmail.Status.FAILED
                    outbound.error_code = str(exc)[:80]
                    outbound.next_attempt_at = timezone.now() + timedelta(minutes=min(60, 2 ** min(outbound.attempt_count, 6)))
                    failed += 1
                else:
                    outbound.status = ResearchOutboundEmail.Status.SENT
                    outbound.provider_message_id = provider_id[:100]
                    outbound.error_code = ""
                    outbound.next_attempt_at = None
                    outbound.sent_at = timezone.now()
                    delivered += 1
                outbound.save()
        self.stdout.write(f"processed={len(ids)} sent={delivered} failed={failed} canceled={canceled}")
