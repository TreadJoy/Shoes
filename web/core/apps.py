from django.core.exceptions import ImproperlyConfigured
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web.core"

    def ready(self):
        from .research_boundary import runtime_boundary_violations

        violations = runtime_boundary_violations()
        if violations:
            raise ImproperlyConfigured(
                "Research capability boundary violation: "
                + "; ".join(violations)
                + "."
            )

        from . import checks  # noqa: F401
