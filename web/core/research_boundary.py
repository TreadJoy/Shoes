"""Fail-closed capability checks for the public research deployment."""

from __future__ import annotations

import sys
from collections.abc import Iterable

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver


FORBIDDEN_APP_NAMES = ("web.cart", "web.orders")
FORBIDDEN_APP_LABELS = ("cart", "orders")
FORBIDDEN_CONTEXT_PROCESSORS = (
    "web.cart.context_processors.cart_summary",
)
FORBIDDEN_MODULE_PREFIXES = ("web.cart", "web.orders", "stripe")
FORBIDDEN_SETTING_PREFIXES = ("STRIPE_",)
FORBIDDEN_URL_NAMESPACES = ("cart", "orders")
FORBIDDEN_URL_PREFIXES = ("cart/", "orders/")
FORBIDDEN_TABLE_PREFIXES = ("cart_", "orders_")


def _matching_prefixes(names: Iterable[str], prefixes: Iterable[str]) -> set[str]:
    matches = set()
    for prefix in prefixes:
        if any(name == prefix or name.startswith(f"{prefix}.") for name in names):
            matches.add(prefix)
    return matches


def _configured_context_processors() -> set[str]:
    processors = set()
    for template in settings.TEMPLATES:
        processors.update(template.get("OPTIONS", {}).get("context_processors", ()))
    return processors


def runtime_boundary_violations() -> list[str]:
    """Return safe, value-free descriptions of active research violations."""
    if settings.IS_COMMERCE_MODE:
        return []

    violations = []
    if settings.TREADJOY_MODE != "research":
        violations.append("deployment mode flags disagree")

    installed_apps = {
        app_name for app_name in FORBIDDEN_APP_NAMES if apps.is_installed(app_name)
    }
    if installed_apps:
        violations.append(
            "forbidden apps installed: " + ", ".join(sorted(installed_apps))
        )

    context_processors = (
        _configured_context_processors() & set(FORBIDDEN_CONTEXT_PROCESSORS)
    )
    if context_processors:
        violations.append(
            "forbidden context processors configured: "
            + ", ".join(sorted(context_processors))
        )

    setting_names = {
        name
        for name in dir(settings)
        if any(name.startswith(prefix) for prefix in FORBIDDEN_SETTING_PREFIXES)
    }
    if setting_names:
        violations.append(
            "forbidden settings exposed: " + ", ".join(sorted(setting_names))
        )

    module_prefixes = _matching_prefixes(
        sys.modules,
        FORBIDDEN_MODULE_PREFIXES,
    )
    if module_prefixes:
        violations.append(
            "forbidden modules loaded: " + ", ".join(sorted(module_prefixes))
        )

    return violations


def _walk_urlpatterns(
    patterns,
    *,
    route_prefix: str = "",
    namespace_prefix: tuple[str, ...] = (),
):
    for entry in patterns:
        route = f"{route_prefix}{entry.pattern}"
        if isinstance(entry, URLResolver):
            namespace = namespace_prefix
            if entry.namespace:
                namespace = (*namespace_prefix, entry.namespace)
            yield from _walk_urlpatterns(
                entry.url_patterns,
                route_prefix=route,
                namespace_prefix=namespace,
            )
        elif isinstance(entry, URLPattern):
            yield route, namespace_prefix, entry.callback


def url_boundary_violations() -> list[str]:
    """Inspect only the active root resolver; never import commerce URLconfs."""
    if settings.IS_COMMERCE_MODE:
        return []

    forbidden_namespaces = set()
    forbidden_prefixes = set()
    forbidden_callbacks = set()

    for route, namespaces, callback in _walk_urlpatterns(get_resolver().url_patterns):
        forbidden_namespaces.update(
            namespace
            for namespace in namespaces
            if namespace in FORBIDDEN_URL_NAMESPACES
        )
        forbidden_prefixes.update(
            prefix
            for prefix in FORBIDDEN_URL_PREFIXES
            if route.startswith(prefix)
        )
        callback_module = getattr(callback, "__module__", "")
        forbidden_callbacks.update(
            _matching_prefixes((callback_module,), FORBIDDEN_MODULE_PREFIXES)
        )

    violations = []
    if forbidden_namespaces:
        violations.append(
            "forbidden URL namespaces registered: "
            + ", ".join(sorted(forbidden_namespaces))
        )
    if forbidden_prefixes:
        violations.append(
            "forbidden URL prefixes registered: /"
            + ", /".join(sorted(forbidden_prefixes))
        )
    if forbidden_callbacks:
        violations.append(
            "forbidden URL callbacks registered: "
            + ", ".join(sorted(forbidden_callbacks))
        )

    # Resolving the active URL tree must not import a forbidden module either.
    module_prefixes = _matching_prefixes(sys.modules, FORBIDDEN_MODULE_PREFIXES)
    if module_prefixes:
        violations.append(
            "forbidden modules loaded while resolving URLs: "
            + ", ".join(sorted(module_prefixes))
        )
    return violations


def database_boundary_violations(*, using: str = "default") -> list[str]:
    """Inspect the selected research database without changing it."""
    db_connection = connections[using]
    table_names = set(db_connection.introspection.table_names())

    recorder = MigrationRecorder(db_connection)
    recorder_present = recorder.has_table()
    migration_count = 0
    if recorder_present:
        migration_count = recorder.migration_qs.filter(
            app__in=FORBIDDEN_APP_LABELS
        ).count()

    migration_apps = {
        app_label
        for app_label, _migration_name in MigrationLoader(
            db_connection,
            ignore_no_migrations=True,
        ).graph.nodes
        if app_label in FORBIDDEN_APP_LABELS
    }

    content_type_table = ContentType._meta.db_table
    content_type_table_present = content_type_table in table_names
    content_type_count = 0
    if content_type_table_present:
        content_type_count = ContentType.objects.using(using).filter(
            app_label__in=FORBIDDEN_APP_LABELS
        ).count()

    return database_observation_violations(
        table_names=table_names,
        recorder_present=recorder_present,
        migration_count=migration_count,
        migration_apps=migration_apps,
        content_type_table_present=content_type_table_present,
        content_type_count=content_type_count,
    )


def database_observation_violations(
    *,
    table_names: Iterable[str],
    recorder_present: bool,
    migration_count: int,
    migration_apps: Iterable[str],
    content_type_table_present: bool,
    content_type_count: int,
) -> list[str]:
    """Evaluate already-collected database facts without querying a database."""
    forbidden_tables = {
        table_name
        for table_name in table_names
        if table_name.startswith(FORBIDDEN_TABLE_PREFIXES)
    }

    violations = []
    if forbidden_tables:
        violations.append(
            f"forbidden commerce tables present: {len(forbidden_tables)}"
        )
    if not recorder_present:
        violations.append("migration recorder table is missing")
    elif migration_count:
        violations.append(
            f"forbidden commerce migration records present: {migration_count}"
        )

    migration_apps = set(migration_apps)
    if migration_apps:
        violations.append(
            "forbidden commerce migrations loaded: "
            + ", ".join(sorted(migration_apps))
        )

    if not content_type_table_present:
        violations.append("content type table is missing")
    elif content_type_count:
        violations.append(
            f"forbidden commerce content types present: {content_type_count}"
        )

    return violations
