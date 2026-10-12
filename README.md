# TreadJoy

TreadJoy is a Django 5.2 application for a modular shoe concept and supporting research/commerce workflows. It is an active development codebase focused on product, policy, and operational validation rather than a finished public storefront.

The repository intentionally keeps the public-facing description high level. It documents the system architecture, development workflow, and release gates without exposing internal infrastructure, operational secrets, or live environment details.

## Project goals

- Explore a modular footwear system built around compatible, interchangeable components.
- Support a research-first product preview before any commerce launch.
- Keep customer-facing, payment, inventory, and fulfillment logic conservative and auditable.
- Maintain a clear separation between research-only features and commerce capabilities.
- Treat product, policy, and operational decisions as explicit requirements rather than assumptions.

## Source of truth

When evidence conflicts, use this order:

1. Reproduced behavior
2. Current source code
3. Schema and migrations
4. Automated tests
5. Current configuration
6. Repository documentation
7. Assumptions

Important repository references:

- `AGENTS.md` defines the approved product, commerce, security, and working policies.
- `PROJECT_PLAN.md` is the living project assessment and roadmap.
- `MISTAKES.md` records failed attempts and verification limitations.
- `docs/` contains detailed product, privacy, deployment, CI, and review guidance.

## Architecture

- Django templates provide the UI; there is no public SPA or general-purpose API.
- PostgreSQL is the authoritative transactional database.
- `web/products` owns catalog, variants, compatibility data, availability, and preorder logic.
- `web/cart` and `web/orders` are commerce-only components.
- `web/survey` stores anonymous research engagement, while `web/waitlist` owns consented delivery and suppression workflows.
- Stripe-hosted Checkout is the payment boundary; raw card data is never collected or stored.
- Research mode and commerce mode are intentionally distinct and must not be mixed.

`TREADJOY_MODE` is required and must be set to `commerce` or `research`.
`TREADJOY_ENVIRONMENT` is required and must be set to `local`, `ci`, `staging`, or `production`.

## Deployment modes

TreadJoy runs in two deployment modes, built from the same codebase:

- `research`: public research preview, no commerce routes or Stripe initialization.
- `commerce`: commerce functionality with cart, checkout, orders, and payment workflows.

The project is designed to fail closed if configuration is missing or invalid.

## Local development

TreadJoy targets CPython 3.12.

Create a dedicated virtual environment and install the reviewed development dependencies:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.txt
```

If no local `.env` exists, create one from `.env.example` and replace placeholders locally. Do not commit `.env`.

The repository supports both local SQLite-safe preview usage and a configured PostgreSQL profile.

SQLite preview (safe local-only convenience):

```sh
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=research \
  SECRET_KEY=django-insecure-local-preview-only \
  TREADJOY_RUNSERVER_DEFAULTS=1 \
  STRIPE_SECRET_KEY= STRIPE_WEBHOOK_SECRET= \
  .venv/bin/python manage.py migrate
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=research \
  SECRET_KEY=django-insecure-local-preview-only \
  TREADJOY_RUNSERVER_DEFAULTS=1 \
  STRIPE_SECRET_KEY= STRIPE_WEBHOOK_SECRET= \
  .venv/bin/python manage.py runserver
```

Configured PostgreSQL profile:

```sh
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=commerce \
  .venv/bin/python manage.py migrate
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=commerce \
  .venv/bin/python manage.py runserver
```

Research mode with Stripe explicitly neutralized:

```sh
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=research \
  STRIPE_SECRET_KEY= STRIPE_WEBHOOK_SECRET= \
  .venv/bin/python manage.py runserver
```

## Verification

Before handing off a change, run the relevant checks for the affected deployment mode:

```sh
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=commerce \
  .venv/bin/python manage.py check
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=commerce \
  .venv/bin/python manage.py makemigrations --check --dry-run
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=research \
  STRIPE_SECRET_KEY= STRIPE_WEBHOOK_SECRET= \
  .venv/bin/python manage.py check
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=research \
  TREADJOY_RUNSERVER_DEFAULTS=1 STRIPE_SECRET_KEY= STRIPE_WEBHOOK_SECRET= \
  .venv/bin/python manage.py test web.core web.products web.survey web.waitlist
.venv/bin/python -m compileall -q treadjoy web
.venv/bin/python -m pip check
```

The full CI path uses PostgreSQL-backed validation for both modes and verifies critical research/commerce boundaries.

## Security and privacy

This project treats security and privacy as launch gates, not cleanup tasks.

Important rules:

- Do not commit secrets, credentials, `.env` files, or production payloads.
- Keep local development and production configuration separate.
- Do not collect or store raw card data.
- Enforce server-side authorization and validation for all mutations.
- Keep research data restricted to the approved research scope.
- Treat customer, order, address, and provider payload data as sensitive.

See the documentation in `docs/` for the detailed operating policy, privacy posture, and release verification expectations.

## Change discipline

Work one approved implementation phase at a time. Preserve working behavior unless a verified issue requires change. Add or update tests for business logic and permission/security-sensitive behavior, and keep migrations and deployment documentation aligned with the code.

## Notes

This repository is intended for development and review under controlled conditions. It is not a finished public storefront, and it should not be treated as production-ready infrastructure until the relevant operational, security, and payment gates are complete.
