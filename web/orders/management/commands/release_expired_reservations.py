from django.core.management.base import BaseCommand

from web.orders.services import release_expired_reservations


class Command(BaseCommand):
    help = "Release checkout inventory reservations whose 30-minute window expired."

    def handle(self, *args, **options):
        released = release_expired_reservations()
        self.stdout.write(
            self.style.SUCCESS(f"Released {released} expired reservation(s).")
        )
