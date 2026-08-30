# Research Capability Boundary

The public research deployment is an allowlisted Django capability profile.
It shares one reviewed source commit and dependency lock with commerce, but it
must not be able to create a cart, reservation, order, payment, refund,
shipment, or other commerce record or initialize a Stripe client.

This document describes application behavior. It does not provision or prove
the separate managed database, hostname, secrets store, origin, or media
resources required by A2.3.

## Allowed capabilities

Research mode installs Django administration/authentication/session support,
django-allauth account flows, and these TreadJoy applications:

- `web.core` for public brand, story, contact, and how-it-works pages;
- `web.products` for read-only public catalog and product previews;
- `web.survey` for anonymous completed survey responses;
- `web.waitlist` for normalized research signups; and
- `web.accounts` for the approved optional account flows.

Its public URL surface may include `/`, `/about/`, `/how-it-works/`,
`/contact/`, `/products/`, `/survey/`, `/waitlist/`, and `/accounts/`.
`/admin/` remains available for separately permissioned research operations.
Research catalog and preorder records are presentation/testing copies only;
they are never the commerce source of truth.

The research database may contain only the shared Django/allauth records and
data needed by the allowed applications above. It must have separate
credentials and storage from commerce and must never be initialized from,
restored from, or pointed at the commerce database.

## Prohibited capabilities

Research mode must not expose or load:

- the `web.cart` or `web.orders` applications, models, administration,
  context processor, management commands, URL namespaces, callbacks, or
  migrations;
- any `/cart/` or `/orders/` route, including Checkout success and Stripe
  webhook routes;
- any `cart_*` or `orders_*` table, migration record, or content type;
- any nonempty `STRIPE_*` configuration value; or
- the `stripe`, `web.cart`, or `web.orders` Python modules during application
  startup, URL resolution, template rendering, or crafted requests.

The Stripe distribution remains installed in the shared hash-locked runtime.
That installation is not a research capability: clean-process tests make any
attempt to import it fail, and the runtime guard rejects it if it was loaded.
Staging and production research manifests must omit `STRIPE_*` names entirely.
Empty overrides are allowed only for documented local commands that must
neutralize a developer's commerce `.env`.

## Enforcement and release verification

Settings reject nonempty Stripe configuration immediately after selecting
research mode and reject even empty `STRIPE_*` process variables in staging or
production. Django application initialization then rejects commerce apps,
settings, context processors, or loaded modules. The deployment system check
loads and inspects the active root URL resolver. It never imports a commerce
URLconf merely to inspect it.

After applying research migrations, run:

```sh
python manage.py check --deploy --fail-level WARNING
python manage.py check_research_boundary
```

`check_research_boundary` is read-only and refuses to report success in
commerce mode. It exits nonzero if the runtime, active URL tree, migration
graph, database tables, migration history, or content types contain a commerce
capability. Its output contains only setting/module names and aggregate counts,
never configuration values or database contents.

The required research PostgreSQL job runs the command against a newly migrated
database before the installed research test suites. A passing local SQLite
run is useful for development but is not launch acceptance. Before a public
research release, retain the PostgreSQL CI result and rerun the command in the
exact production-like research environment.
