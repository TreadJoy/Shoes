# TreadJoy

TreadJoy is a pre-launch Django 5.2 application for modular shoes and
accessories. It is a real-commerce codebase under active hardening, not a
production-ready storefront. The public research deployment launches first;
commerce remains disabled until its payment, inventory, fulfillment, legal,
security, and operational gates pass.

The owner confirmed on 2026-08-26 that `tread-joy.com` was purchased through
Cloudflare as the intended base domain. Registration is not an active-site
claim: this repository has not provisioned a public hostname, DNS/TLS path,
managed origin, R2 bucket/custom domain, PostgreSQL service, or email service.
`hello@tread-joy.com` and `noreply@tread-joy.com` are reserved future addresses,
not active or monitored mailboxes.

## Source of Truth

Use evidence in this order: reproduced behavior, current source, schema and
migrations, automated tests, configuration, repository documentation, then
assumptions. In particular:

- `AGENTS.md` contains the approved product, commerce, security, and working
  policies.
- `PROJECT_PLAN.md` is the living current-state assessment and launch roadmap.
- `MISTAKES.md` is the append-only record of failed attempts and verification
  limitations.
- `docs/production-configuration.md`, `docs/ci.md`, and
  `docs/dependencies.md` are the detailed operating references.

Do not treat a roadmap target or configured provider backend as implemented
live infrastructure.

## Architecture and Deployment Modes

- Django templates provide the UI; there is no SPA or public API.
- PostgreSQL is the authoritative transactional database.
- `web/products` owns catalog, variants, compatibility/BOM, availability, and
  preorder batches.
- `web/cart` and `web/orders` are installed only in commerce mode.
- `web/survey` stores anonymous responses (with session drafts only during completion), and
  `web/waitlist` stores a normalized email plus optional first name and controlled source.
- Commerce cart mutations are server-side transactional operations. Each cart has one
  principal, and signing in merges the guest cart with availability-cap notices.
- Stripe-hosted Checkout is the payment boundary; TreadJoy must never collect
  or store raw card data. Checkout attempts quote current variants and create
  expiring server-side reservation records before redirecting to Stripe.
- Public settings use manifest static files and configure R2-backed public
  media. These settings have automated coverage, but no live resources have
  been provisioned.

`TREADJOY_MODE` is required and must be `commerce` or `research`.
`TREADJOY_ENVIRONMENT` is required and must be `local`, `ci`, `staging`, or
`production`. Research excludes commerce apps/routes and rejects every
nonempty `STRIPE_*` variable. Research and commerce must use separate
PostgreSQL databases.

## Local Setup

TreadJoy targets CPython 3.12. Create a dedicated virtual environment and
install the reviewed development lock:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.txt
```

If no local `.env` exists, create one from `.env.example`, replace placeholders
locally, and never commit it. Use a local PostgreSQL database and a role with
only the privileges needed by the application. Do not point research at the
commerce database for convenience.

The bare `.venv/bin/python manage.py runserver` convenience supplies only
missing local defaults. With no configured mode or database profile, it uses
the safe research deployment and local SQLite; an explicitly configured mode
is preserved. A database profile—including one supplied by `.env`—uses
PostgreSQL and fails closed if the profile is incomplete. The command never
applies migrations automatically.

To initialize the isolated SQLite preview without changing `.env`, run the
explicit migration once, then start the same profile:

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

For the configured PostgreSQL profile, apply migrations explicitly before
starting the server.

Apply migrations and start a selected local mode:

```sh
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=commerce \
  .venv/bin/python manage.py migrate
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=commerce \
  .venv/bin/python manage.py runserver
```

For research, use its separate database configuration and neutralize any
Stripe values inherited from a commerce `.env`:

```sh
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=research \
  STRIPE_SECRET_KEY= STRIPE_WEBHOOK_SECRET= \
  .venv/bin/python manage.py runserver
```

Commerce deployments should run the idempotent reservation cleanup command
from the managed-origin scheduler:

```sh
.venv/bin/python manage.py release_expired_reservations
```

Legacy Stripe payload contraction is deliberately backup-gated. First verify
the bounded audit backfill and a restorable backup; without the confirmation
flag the command reports aggregate row counts and changes nothing:

```sh
.venv/bin/python manage.py purge_legacy_stripe_payloads
.venv/bin/python manage.py purge_legacy_stripe_payloads --confirm-backup
```

## Verification

Run mode checks and migration-drift detection before handing off a change:

```sh
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=commerce \
  .venv/bin/python manage.py check
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=commerce \
  .venv/bin/python manage.py makemigrations --check --dry-run
env TREADJOY_ENVIRONMENT=local TREADJOY_MODE=research \
  STRIPE_SECRET_KEY= STRIPE_WEBHOOK_SECRET= \
  .venv/bin/python manage.py check
.venv/bin/python -m compileall -q Shoes web
.venv/bin/python -m pip check
```

The required GitHub checks run commerce and research against PostgreSQL,
collect static files, audit both dependency locks, and scan complete Git
history for secrets. Local SQLite-only success does not prove row-locking or
concurrency behavior. Reproduce the PostgreSQL jobs using the restricted-role
procedure in `docs/ci.md`; do not grant the runtime role `CREATEDB` merely to
make Django's default test runner convenient.

Before any public release, run `manage.py check_release_content` in the exact
deployment-mode environment. A nonzero result is a release blocker; see
`docs/release-content-checklist.md`.

## Commerce Stripe Webhook

The commerce deployment's signed webhook endpoint is:

`/orders/stripe/webhook/`

The current implementation handles:

- `checkout.session.completed`
- `checkout.session.async_payment_succeeded`
- `checkout.session.expired`
- `checkout.session.async_payment_failed`
- `payment_intent.succeeded` (audit only; it does not mutate orders)
- `refund.created`
- `refund.updated`
- `refund.failed`

Checkout creates an immutable server-side quote and 30-minute reservation,
then creates hosted Checkout after the database commit using a stable
idempotency key. Webhooks and the bounded manual success-page check both
retrieve the authoritative Session and call the same reconciler. Durable
orders and full addresses are created only for paid or financially meaningful
review records; mismatches never overwrite the expected quote or commit
inventory. Research does not register this route and must not possess Stripe
credentials. Production webhook subscription, scheduler, restricted-key,
alerting/replay, PostgreSQL race, and backup/payload-purge acceptance are still
deployment gates.

When current paid-order allocation reports insufficient inventory, use the
Django admin allocation queue for human review. Initiate a full refund in
Stripe Dashboard, notify the customer outside the application, and record that
notification with the queue action by its displayed deadline. Refund webhooks
update the local audit record.

## Preorder Batch Operations

Preorder capacity is managed in **Products → Preorder batches** in Django
admin. Only superusers can create or change a batch.

1. Create the batch in `draft` with its customer-facing carrier-tender window
   and total production capacity.
2. Add an allocation for every active product variant. Combined SKU capacity
   must cover the batch total.
3. Save, then reopen the batch and change it to `open` with a reason. An open
   batch makes that product preorder-only.
4. Use `paused` to stop new checkouts without discarding existing carts. Reopen
   it to resume sales, or use terminal `closed` when the offer is over.

Every status and capacity change is audited. Capacity cannot be reduced below
confirmed commitments, and the promised shipping window becomes read-only
after the first confirmed payment. Stripe refunds do not restore preorder
capacity; that release belongs to the future typed pre-tender cancellation
workflow.

## Change Discipline

Work one explicitly approved implementation phase at a time. Preserve working
behavior unless a verified correctness, security, privacy, historical-truth,
or measured-performance problem requires change. Use expand/backfill/verify/
contract migrations for destructive cleanup, update the living Markdown with
each phase, and wait for owner `next` approval before starting another roadmap
task.
