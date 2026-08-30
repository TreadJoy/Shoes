"""Verify the active research process and database capability boundary."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from web.core.research_boundary import (
    database_boundary_violations,
    runtime_boundary_violations,
    url_boundary_violations,
)


class Command(BaseCommand):
    help = "Verify that research mode exposes no commerce runtime or database state."

    def handle(self, *args, **options):
        if settings.IS_COMMERCE_MODE or settings.TREADJOY_MODE != "research":
            raise CommandError(
                "check_research_boundary must run with TREADJOY_MODE='research'."
            )

        violations = runtime_boundary_violations()
        violations.extend(url_boundary_violations())
        try:
            violations.extend(database_boundary_violations())
        except DatabaseError as error:
            raise CommandError(
                "Research boundary database inspection failed."
            ) from error

        if violations:
            formatted = "\n".join(f"- {violation}" for violation in violations)
            raise CommandError(f"Research capability boundary failed:\n{formatted}")

        self.stdout.write(
            self.style.SUCCESS(
                "Research capability boundary verified: no commerce apps, routes, "
                "imports, settings, tables, migrations, or content types."
            )
        )
