"""Settings used only by TreadJoy's isolated CI verification jobs."""

from pathlib import Path

from decouple import config
from django.core.exceptions import ImproperlyConfigured

if not config("TREADJOY_CI", default=False, cast=bool):
    raise ImproperlyConfigured(
        "treadjoy.ci_settings requires TREADJOY_CI=true."
    )

if config("TREADJOY_ENVIRONMENT", default="").strip() != "ci":
    raise ImproperlyConfigured(
        "treadjoy.ci_settings requires TREADJOY_ENVIRONMENT=ci."
    )

from .settings import *  # noqa: F403, E402

CI_DB_TEST_NAME = config("CI_DB_TEST_NAME", default="").strip()
if not CI_DB_TEST_NAME:
    raise ImproperlyConfigured(
        "CI_DB_TEST_NAME is required when using treadjoy.ci_settings."
    )

if CI_DB_TEST_NAME == DATABASES["default"]["NAME"]:  # noqa: F405
    raise ImproperlyConfigured(
        "CI_DB_TEST_NAME must differ from DB_NAME."
    )

CI_STATIC_ROOT = Path(config("CI_STATIC_ROOT", default="").strip())
if not CI_STATIC_ROOT.is_absolute():
    raise ImproperlyConfigured(
        "CI_STATIC_ROOT must be an absolute path when using treadjoy.ci_settings."
    )

DATABASES["default"].setdefault("TEST", {})["NAME"] = CI_DB_TEST_NAME  # noqa: F405
STATIC_ROOT = CI_STATIC_ROOT
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
