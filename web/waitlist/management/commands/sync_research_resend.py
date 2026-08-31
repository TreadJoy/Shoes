from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from web.waitlist.models import SubscriptionStatus, WaitlistSubscription
from web.waitlist.providers import ResearchEmailProviderError, upsert_contact


class Command(BaseCommand):
    help = "Synchronize confirmed local subscriptions to the configured Resend segment."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        if settings.IS_COMMERCE_MODE:
            raise CommandError("sync_research_resend only runs in research mode.")
        limit = options["limit"]
        if limit < 1 or limit > 1000:
            raise CommandError("--limit must be between 1 and 1000.")
        ids = list(WaitlistSubscription.objects.filter(status=SubscriptionStatus.ACTIVE, provider_contact_id="").order_by("confirmed_at").values_list("pk", flat=True)[:limit])
        synced = failed = 0
        for pk in ids:
            with transaction.atomic():
                subscription = WaitlistSubscription.objects.select_for_update().get(pk=pk)
                if subscription.status != SubscriptionStatus.ACTIVE or not subscription.email:
                    continue
                try:
                    subscription.provider_contact_id = upsert_contact(subscription)[:100]
                except ResearchEmailProviderError:
                    failed += 1
                else:
                    subscription.save(update_fields=("provider_contact_id", "updated_at"))
                    synced += 1
        self.stdout.write(f"processed={len(ids)} synced={synced} failed={failed}")
