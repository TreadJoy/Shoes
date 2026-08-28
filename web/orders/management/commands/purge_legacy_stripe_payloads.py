from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from web.orders.models import Payment, Refund, StripeEvent


class Command(BaseCommand):
    help = (
        "Purge legacy raw Stripe payloads after bounded audit fields have been "
        "verified and a restorable backup has been confirmed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm-backup",
            action="store_true",
            help="Confirm that a current restorable backup has been verified.",
        )

    def handle(self, *args, **options):
        counts = {
            "events": StripeEvent.objects.exclude(raw_event__isnull=True).count(),
            "payments": Payment.objects.exclude(raw_response__isnull=True)
            .exclude(raw_response={})
            .count(),
            "refunds": Refund.objects.exclude(raw_response={}).count(),
        }
        self.stdout.write(
            "Legacy payload rows: "
            f"events={counts['events']}, payments={counts['payments']}, "
            f"refunds={counts['refunds']}."
        )
        if not options["confirm_backup"]:
            raise CommandError(
                "No data changed. Verify a restorable backup, validate the "
                "bounded audit backfill, then rerun with --confirm-backup."
            )

        with transaction.atomic():
            StripeEvent.objects.exclude(raw_event__isnull=True).update(raw_event=None)
            Payment.objects.exclude(raw_response__isnull=True).exclude(
                raw_response={}
            ).update(raw_response={})
            Refund.objects.exclude(raw_response={}).update(raw_response={})
        self.stdout.write(self.style.SUCCESS("Legacy Stripe payloads purged."))
