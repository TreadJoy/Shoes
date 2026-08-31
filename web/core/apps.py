from django.core.exceptions import ImproperlyConfigured
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web.core"

    def ready(self):
        from django.db.models.signals import post_migrate

        from .research_boundary import runtime_boundary_violations

        violations = runtime_boundary_violations()
        if violations:
            raise ImproperlyConfigured(
                "Research capability boundary violation: "
                + "; ".join(violations)
                + "."
            )

        from . import checks  # noqa: F401

        from web.waitlist.roles import configure_research_roles

        post_migrate.connect(
            configure_research_roles,
            dispatch_uid="treadjoy.configure_research_roles",
            weak=False,
        )
