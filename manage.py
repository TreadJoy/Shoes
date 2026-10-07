#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from decouple import config


_DATABASE_SETTING_NAMES = (
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
)


def _configure_runserver_defaults():
    """Make a bare local runserver useful without weakening deployment checks."""
    if len(sys.argv) < 2 or sys.argv[1] != "runserver":
        return

    if not config("TREADJOY_ENVIRONMENT", default="").strip():
        os.environ["TREADJOY_ENVIRONMENT"] = "local"
    # Research is the safe default only when no mode is configured in the
    # environment or the local .env file. It cannot initialize Stripe or create
    # orders.
    if not config("TREADJOY_MODE", default="").strip():
        os.environ["TREADJOY_MODE"] = "research"
        os.environ["STRIPE_SECRET_KEY"] = ""
        os.environ["STRIPE_WEBHOOK_SECRET"] = ""
    if not config("SECRET_KEY", default="").strip():
        os.environ["SECRET_KEY"] = "django-insecure-local-runserver-only-change-me"
    # ``config`` preserves process-environment precedence while also reading
    # the ignored local .env file. If any database setting is present, let the
    # normal PostgreSQL configuration validate the complete profile instead
    # of silently replacing it with SQLite.
    if not any(config(name, default="").strip() for name in _DATABASE_SETTING_NAMES):
        os.environ["TREADJOY_RUNSERVER_DEFAULTS"] = "1"


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treadjoy.settings")
    _configure_runserver_defaults()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Confirm it is installed and available on "
            "PYTHONPATH, and that the project virtual environment is active."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
