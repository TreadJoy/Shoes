# TreadJoy Production Roadmap

- Last repository audit: 2026-08-30
- Audited base commit: 0e8a0dd1487e9f7a15b75af91c9dfc74a221510c
- Document purpose: living assessment, decision record, and dependency-ordered path from the current repository to research launch and then commerce launch.

## How to use this plan

- Complete one approved task at a time and update its status and evidence before selecting another.
- Status values are **Not started**, **In progress**, **Blocked**, **Ready for owner acceptance**, **Complete**, and **Deferred**.
- Priorities are **P0 — launch blocker**, **P1 — required for production**, **P2 — important improvement**, and **P3 — post-launch enhancement**.
- A dependency is satisfied only when its task is Complete, not merely merged or partially tested.
- The task descriptions record intended work, not current capability. Do not present roadmap text as implemented behavior.
- If implementation evidence contradicts this audit, update the assessment and affected task before coding against the new finding.
- Business, legal, tax, retention, staff-permission, and customer-promise decisions require project-owner approval. A task may gather evidence and present a recommendation, but it must not silently encode policy.

## Repository assessment

### Current architecture

TreadJoy is a Django 5.2 and PostgreSQL application rendered with Django templates, centralized CSS, and small vanilla JavaScript enhancements. It uses django-allauth account flows without Google/social authentication for now, Stripe-hosted Checkout and signed webhooks, database-backed authenticated/guest carts, order snapshots, shipment records, and Django admin. Public-environment settings configure manifest static files and R2-backed public media, but no live origin, bucket, custom domain, or CDN path has been provisioned. There is no SPA, public API, background queue, cache service, search service, or generalized CMS.

The codebase supports two fail-closed modes selected by TREADJOY_MODE:

- **Commerce** registers cart and order applications/routes and requires Stripe configuration.
- **Research** excludes commerce applications/routes, rejects Stripe credentials, and emphasizes survey/waitlist/customer-learning flows.

The approved deployment architecture is one tested release commit deployed to separate research and commerce origins and PostgreSQL databases. Cloudflare provides DNS, edge TLS, proxy/CDN, WAF controls, and R2 media; managed infrastructure runs Django and PostgreSQL.

### Major strengths

- Mode-aware settings and routes fail closed, and automated negative tests exercise research-mode isolation.
- Hash-locked runtime/development dependencies, PostgreSQL CI for both modes, dependency auditing, and full-history secret scanning are implemented and documented.
- Public-environment settings validate hosts, origins, proxy ingress, PostgreSQL TLS, SMTP, R2 media, static collection, CSP, secure cookies, and staged HSTS before startup.
- Preorder batches have capacity/allocation invariants, explicit state transitions, append-only events, and strong tests.
- Order items snapshot product, SKU, size, color, price, fulfillment type, and preorder promises.
- Stripe webhooks verify signatures, persist unique event IDs, and process inside database transactions.
- Paid-order inventory allocation uses row locks, is idempotent, and records shortage/refund-review exceptions.
- Shipment records drive fulfillment state and guard against shipping an inventory-review order.
- The automated suite covers meaningful catalog, preorder, cart, checkout, webhook, inventory, order, shipment, and deployment-mode behavior.
- The current homepage/navigation shell is distinctive, responsive, and substantially aligned with the approved visual direction.

### Major problems and production risks

- Checkout now creates a server-side attempt, immutable quote/BOM facts, a unique idempotency key, and atomic 30-minute finished-SKU reservations without creating an abandoned order or address. The remaining launch risk is operational verification of the PostgreSQL races and the managed expiry schedule.
- One retrieved-Session reconciler now verifies payment state, test/live mode, Checkout ownership, expected amount/currency metadata, actual amount/currency, PaymentIntent, reservation age, and the Stripe-collected address before creating a paid or review-required order. Dispute/chargeback operations and production alerting remain launch work.
- Catalog pricing now has variant selling/compare-at fields with a compatibility fallback, and catalog availability reads use a bounded prefetch path; full price-field contraction and some order money formula constraints remain open.
- Orders now retain immutable currency and shipping/contact snapshots, so account/address deletion does not remove historical delivery facts. The legacy `ShippingAddress` relationship remains for one compatibility release and must not be contracted until deployed backfill completeness and rollback reads are verified.
- Order, line, payment/refund, provider, allocation, and status-history fields are read-only in ordinary admin workflows; material record deletion and direct shipped/delivered/canceled actions are disabled. Shipment timestamps, the refund reconciler, and a guarded processing action use one row-locking transition service.
- Authentication still needs production hardening: email verification is optional and effective login is username-based; terms/privacy acceptance is not durably recorded, and stronger verification/MFA policy remains a separate launch decision.
- There is no application rate limiting, brute-force/abuse control, production email provider, data-retention schedule, consent versioning, unsubscribe/suppression system, or complete staff-permission model.
- Shipping and tax totals are hardcoded to zero. Contiguous-US validation, carriers, service levels, rate source, tax registrations, product tax codes, and customer disclosures are not implemented.
- Cancellation, return, exchange, inspection, and customer-initiated refund workflows do not yet represent the approved policy.
- New Stripe event/payment/refund writes retain bounded audit fields instead of raw payloads. Legacy raw fields remain temporarily for expand/backfill/verify/backup/contract safety; production retention approval, alerting, and controlled replay tooling remain open.
- The reviewed dependency inputs and hash-locked runtime/development manifests are reproducible; Phase 1 removed the Google/social extra and refreshed both locks and the license inventory.
- GitHub runs separate commerce/research PostgreSQL jobs, a dependency audit, and full-history secret scanning. There is still no deployment pipeline or deployment-status check.
- Production configuration includes `STATIC_ROOT`, manifest static storage, and an R2 media backend contract. No live hosting, DNS/TLS path, R2 resource, health/readiness endpoint, monitoring, analytics, backup/PITR procedure, restore drill, migration release process, or rollback runbook has been provisioned or verified.
- The catalog has been quarantined to its safe empty state, while homepage and
  social sections remain explicitly labeled development placeholders that block
  release until approved factual replacements exist.
- Product detail lacks production imagery, size/fit, materials, care, compatibility explanation, shipping/returns context, and other purchase-confidence content.
- SEO support is limited: sitemap, robots policy, canonicals, structured data, social metadata, production error pages, and measurement are absent.

### Missing or intentionally deferred functionality

Launch work still includes shipping rates/tax decisions, verified transactional email, secure durable guest-order access, operational cancellation/returns/exchanges/disputes, production catalog/assets, legal disclosures, accessibility/performance validation, Cloudflare/origin infrastructure, monitoring, backups, and launch rehearsal. Phase 4 reservation and Phase 5 order-history/state-machine application code are implemented but still require PostgreSQL CI/deployment acceptance.

Customer configurators, standalone component sales, reviews, advanced promotions, advanced search, Redis, a task queue, and Cloudflare Containers are deliberately deferred until evidence shows that they solve a real launch or post-launch problem.

### Repository and documentation discrepancies

- The prior AGENTS.md called the project a proof of concept with no established policies but later declared detailed fulfillment and return policies approved. The rewritten manual treats them as approved provisional launch policy.
- The login UI and effective django-allauth settings now both use username login; email verification remains optional by policy.
- A product description describes a test shoe being used while the server is in production; test content is not valid production catalog data.
- The former root-level `web/views.py`, `web/models.py`, and `web/tests.py` scaffolds were removed in A0.2, but older documentation continued to describe them as present.
- The comment-only root `web/admin.py` and unused `web/apps.py` were removed in Phase 1; active features live in domain apps.
- Before the 2026-08-28 cleanup phase, README.md documented selected Stripe/preorder operations but was not a complete developer entry point.

### Verified evidence and limitations

- The worktree was clean at the 2026-08-28 audit start at base commit `a046d47`; no repository file was changed during the inspection or aggregate database preflight.
- Commerce and research Django checks pass. The 2026-08-28 Phase 0 rerun passed 161 isolated commerce tests with 9 skips and 87 installed-app research tests with 6 skips.
- GitHub-hosted PostgreSQL CI is the locking/concurrency authority. Its latest recorded acceptance evidence at commit `91d9f4f` passed 152 commerce tests, both explicit row-lock race classes, and 78 research tests. The local PostgreSQL role still cannot create a Django test database.
- `makemigrations --check --dry-run`, Python compilation, and `pip check` pass. The configured local database was unavailable inside the default sandbox but allowed aggregate-only reads through the approved local process boundary.
- A targeted catalog probe with five products and three variants each rendered successfully in 18 queries; 15 were repeated preorder-batch lookups. This is the cleanup program's performance baseline, not an accepted budget.
- Phase 0 collected 134 static files in a disposable directory, found no known vulnerabilities in either hash-locked dependency manifest, and found no leaks across all 48 reachable Git commits or the changed-document credential-pattern scan.
- Phase 1 removed the verified dead/authentication paths without schema changes. On 2026-08-28 both deployment-mode checks passed; the isolated SQLite suites passed 160 commerce tests (9 skipped) and 86 research tests (6 skipped); both refreshed locks installed with hashes and passed `pip check` and `pip-audit`; disposable `collectstatic` copied 134 files; and full-history Gitleaks again found no leaks. The release-content command could not reach the sandboxed local PostgreSQL instance in this environment, so its previously recorded two expected content blockers remain authoritative.
- The commerce release-content command still fails on exactly the two documented homepage-media and pending-social-link blockers. That is an expected public-release stop, not a Phase 0 regression.
- Browser evidence recorded in the older homepage documents remains historical. Phase 6 added a current manual viewport baseline for the required commerce/research and mobile/desktop matrix, but no current Core Web Vitals, network waterfall, Lighthouse accessibility result, or automated visual-regression service exists yet.
- No secret or customer values were printed. Aggregate preflight counts only are recorded below; the repository's prior contained-exposure history still makes rotation and incident discipline mandatory.

### Refactor and cleanup preflight (2026-08-28)

The local development database contained no case-insensitive waitlist duplicate groups, linked survey users/session keys, social accounts/apps/tokens, nonzero component-stock rows, duplicate nonblank order Checkout Session or PaymentIntent groups, orphaned shipping addresses, or orders missing a shipping address. It contained two pending-payment orders, two Stripe event rows with raw payloads, and one payment row with a raw payload. Later cleanup must preserve and reconcile those financial records before any contraction; these counts do not establish the state of staging, production, or a future commerce database.

## Approved decision log

| Decision | Approved direction | Consequence |
|---|---|---|
| Release sequence | Public research deployment before commerce | Shared security/infrastructure work and research launch precede payment launch |
| Codebase | One tested release commit, no long-lived mode branches | Mode differences stay in fail-closed configuration and routing |
| Hosting | Cloudflare edge plus managed Django/PostgreSQL origin | Do not target Cloudflare Containers for launch |
| Domain ownership | Owner confirmed on 2026-08-26 that `tread-joy.com` was purchased through Cloudflare as TreadJoy's intended base domain | Hostname allocation and DNS, TLS, origin, R2, and email configuration remain incomplete |
| Databases | Separate research and commerce PostgreSQL databases | Research data cannot become the commerce source of truth |
| Launch product | Fixed, preconfigured shoe variants | No launch configurator or standalone component sales |
| Inventory authority | Finished ProductVariant stock and preorder allocation | BOM/component records are compatibility/reference data at launch |
| Accounts | Guest checkout plus optional accounts | Secure guest order access and safe cart/order association are launch requirements |
| Reservation | 30 minutes after hosted Checkout creation | Reserve atomically, release on expiry/cancel, commit on confirmed payment |
| Preorder payment | Full payment when ordered | Payment, delay notification, and cancellation/refund behavior must support preorders |
| Payment boundary | Stripe-hosted Checkout | Never collect or store raw card data |
| Shipping | Contiguous United States, paid available service levels | Address validation and rate/service source must be approved before launch |
| Social authentication cleanup | Remove Google authentication for now | Use django-allauth account flows without the Google provider until a complete public flow is approved |
| Survey identity | Anonymous responses | Remove user and raw session links without adding replacement tracking identifiers |
| Waitlist data | Email plus optional first name | Normalize email, constrain source attribution, and retain no additional profile data |
| Cart merge | Combine with an explicit availability notice | Keep distinct items, combine identical SKU/batch quantities, and disclose every cap or removal |
| Checkout address | Stripe collects the full address | Retain only a transient state eligibility check before redirect and snapshot the retrieved address only for paid/review records |

### Authoritative implementation references

Re-check current versions when the related task begins; these links guide design but do not replace repository evidence or owner policy:

- [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Stripe: manage limited inventory with Checkout](https://docs.stripe.com/payments/checkout/managing-limited-inventory)
- [Stripe Checkout Session object and payment status](https://docs.stripe.com/api/checkout/sessions/object)
- [Cloudflare R2 public buckets and custom domains](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [Cloudflare Origin CA and Full strict TLS](https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/)
- [Cloudflare Containers FAQ](https://developers.cloudflare.com/containers/faq/) — revisit after launch only if measured demand justifies the additional compute/autoscaling design.

## Planning summary

### Recommended development order

1. Clean repository inputs and make dependencies/tests reproducible.
2. Establish shared production configuration, PostgreSQL CI, security, logging, and data-governance foundations.
3. Harden and launch research mode on the intended Cloudflare/managed-origin architecture.
4. Correct commerce schema, identity, cart ownership, and staff authorization.
5. Implement atomic 30-minute inventory reservations.
6. Correct shipping, tax, Checkout idempotency, payment reconciliation, and webhook lifecycle.
7. Implement auditable order operations, fulfillment, returns/refunds, and customer communications.
8. Finish licensed product/brand content and the customer journey.
9. Verify accessibility, SEO, privacy, and performance.
10. Provision commerce infrastructure, rehearse failure/rollback, complete independent audits, and launch.

### Approved refactor and cleanup sequence

The 2026-08-28 cleanup review adds a gated implementation stream without replacing the dependency-ordered launch roadmap. Complete and verify one phase, update this document and the operating manual, then wait for owner `next` approval:

0. Restore documentation and evidence accuracy. **Complete on 2026-08-28.**
1. Remove proven dead paths and the approved Google/custom-auth surface. **Complete on 2026-08-28.**
2. Minimize survey/waitlist data and enforce cart ownership/mutation rules. **Complete on 2026-08-28.**
3. Consolidate variant pricing, availability, preorder administration, and historical BOM snapshots. **Complete on 2026-08-28.**
4. Add Checkout attempts, 30-minute reservations, and authoritative Stripe reconciliation. **Complete on 2026-08-28; PostgreSQL/deployment acceptance remains a launch gate.**
5. Protect order/address history and centralize staff-visible state transitions. **Complete on 2026-08-30; PostgreSQL/deployment acceptance and compatibility-field contraction remain gated.**
6. Remove only visually verified template/static duplication and complete the documentation audit. **Complete on 2026-08-30; production-like performance/accessibility acceptance remains a launch gate.**

Phase 0 changed Markdown only. It corrected current-state claims, recorded the aggregate-only data preflight, expanded the developer entry point, preserved the append-only failure history, and labeled dated homepage evidence as historical. Both modes, migration drift, compilation, static collection, dependency health/audits, release-content blockers, isolated suites, and secret scans were rechecked before handoff.

Phase 1 removed verified dead scaffolding/helpers/templates, the custom activation implementation, unsafe referrer fallback, unused session/form values, and Google/social authentication configuration. It preserved the allauth username-login and optional-verification policy, routed Django admin login through allauth's secure admin wrapper, refreshed the hash-locked runtime/development dependencies and license inventory, and aligned login copy and deployment tests. Full validation evidence is recorded below and in `MISTAKES.md`; no database schema or historical commerce data was changed.

Phase 2 made completed survey responses anonymous and added an unlink migration while retaining compatibility columns for a later contract migration. It normalized and deduplicated waitlist records, constrained source attribution, and enforced case-insensitive email uniqueness. Cart rows now require exactly one authenticated or guest principal, guest sessions are unique, cart mutations are transactional and availability-aware, broad context-processor suppression is removed, and allauth sign-in merges the guest cart atomically with explicit reduction/removal notices. Aggregate preflight found no rows requiring deduplication or identifier unlinking in the local database. The isolated SQLite commerce suite passed 161 tests (9 skipped), and the installed-app research suite passed 86 tests (6 skipped); PostgreSQL locking/concurrency coverage remains a CI requirement. No survey identifiers or raw provider payloads were printed.

Phase 3 added variant selling and compare-at price fields with the approved precedence backfill and a one-release legacy dual-read fallback, moved catalog display values to active-variant price ranges, and reduced the measured five-product/three-variant catalog path from 18 queries to 3 (under the eight-query budget). It added nonnegative product/order amount constraints and a discount bound while deferring formula constraints that current legacy totals cannot satisfy without rewriting history. Finished-SKU availability continues through the existing authoritative service, with prefetched live preorder batches and allocations. Component stock was removed from staff edit/list workflows but its legacy column remains pending owner review outside the zero-row local preflight; it remains non-authoritative. Order item BOM composition is copied into immutable component snapshot rows, including a migration backfill and admin read view. The isolated SQLite commerce suite passed 163 tests (9 skipped), and the installed-app research suite passed 87 tests (6 skipped). PostgreSQL locking and migration verification remain CI requirements.

Phase 4 completed the Checkout lifecycle on 2026-08-28. Checkout now commits an attempt, immutable quote/BOM snapshots, one active-attempt-per-cart constraint, a stable Stripe idempotency key, and 30-minute finished-SKU/preorder reservations before the provider call; no durable order or full address is created for an abandoned attempt. Ambiguous Stripe failures retry the same key, definite creation failures release inventory, hosted Checkout collects the U.S. address, and success pages perform only a bounded manual status check. One retrieved-Session reconciler is shared by webhooks and the success return and requires paid state plus exact environment, mode, attempt/Session ownership, amount, currency, PaymentIntent, metadata, reservation age, and contiguous-state agreement. It creates paid orders exactly once, copies address/price/preorder/BOM snapshots, and commits inventory once; paid mismatches and late payments create durable `REVIEW_REQUIRED` order/payment records without fulfillment or inventory commitment. Session expiry/async failure and the scheduler command release idempotently; PaymentIntent events no longer mutate orders independently. New provider records use bounded audit fields, migration `0020` backfills those fields, and the backup-gated purge command supports later payload contraction without deleting data during deployment. SQLite passes 178 commerce tests with 10 skips (including the new PostgreSQL last-unit reservation race) and research passes 88 tests with 6 skips. PostgreSQL CI, scheduler provisioning, webhook subscription/configuration, restricted-key rollout, alerting, and backup-verified legacy payload purge remain deployment/launch acceptance, not missing Phase 4 application code.

Phase 5 completed the order-history and staff-safety application work on 2026-08-30. Orders now snapshot three-letter currency plus the Stripe-collected shipping/contact fields independently of account and address rows. Migrations `0022`–`0024` expand the schema, preserve and classify legacy status detail, backfill address/currency facts, normalize legacy financial components while preserving each recorded grand total, and only then add order/line formula constraints. The address foreign key and legacy status `note` remain compatibility fields for one observed release; no destructive contraction occurs in this phase. One row-locking transition service now enforces the approved forward fulfillment graph and full-refund terminal state across Stripe reconciliation, legacy reconciliation, shipments, refunds, and the staff processing action. Shipment timestamps alone drive shipped/delivered, partial refunds do not rewrite fulfillment, and failed or late refund events cannot reopen a confirmed refunded order. Status history records actor, source, reason, external reference, internal detail, and separately approved customer-safe text; customer templates render only the latter. Material commerce records are read-only/nondeletable in ordinary admin screens, and the unsafe bulk shipped/delivered/canceled actions are removed. Local SQLite passes 194 commerce tests with 10 PostgreSQL-only skips and 93 installed-app research tests with 6 skips. PostgreSQL applied all migrations and passed 35 focused Phase 5 and inventory/preorder/Checkout concurrency tests. A reused-test-database full run passed 193 of 194; the sole failure was an unrelated data-migration seed previously flushed from the preserved test database, and the least-privilege role correctly could not recreate it. Clean PostgreSQL CI, one-release compatibility observation, backup verification, and later address/note contraction remain deployment gates.

Phase 6 completed the evidence-gated presentation cleanup on 2026-08-30. No template or JavaScript module was removed because the semantic scan and browser matrix showed that each remaining path is active; all five committed static source files have current template references, and no committed public image was available for safe deletion. Authenticated footer logout now uses allauth's CSRF-protected POST flow. Removing only proven obsolete or fully superseded CSS reduced `style.css` from 54,234 to 44,801 bytes (9,433 bytes, 17.4%) without adding a dependency or changing the design system; combined source CSS is 64,637 bytes and JavaScript is 9,903 bytes. A disposable synthetic fixture was used to inspect the required commerce/research surfaces at desktop and `390x844`; commerce-only routes remained absent from research. The catalog stayed at 3 queries for the five-product/three-variant fixture. Local one-shot response timings were 2.7–43.6 ms across five representative routes, but these are diagnostics rather than production or Core Web Vitals evidence. Both-mode checks and migration drift passed; SQLite passed 195 commerce tests with 10 skips and 94 installed-app research tests with 6 skips; `collectstatic` copied 134 files; both dependency locks had no known vulnerabilities; full-history secret scanning found no leaks; and release validation stopped only on the two expected development-media and pending-social-link blockers. Clean PostgreSQL CI, production-like performance traces, automated accessibility review, approved release imagery/social destinations, and the wider operational gates remain required before launch.

### Critical path

**P0 dependency/CI baseline → production security/configuration → research deployment → commerce data integrity/identity → reservations → shipping/tax decisions → Checkout/payment correctness → order operations → commerce infrastructure → pre-launch audit/rehearsal → launch**

P1 storefront, email, accessibility, SEO, performance, monitoring, and admin-usability work must also complete before the relevant public launch even where it can proceed in parallel after its dependencies.

### Highest-risk areas

1. A customer can pay without an inventory reservation, causing oversell/refund harm.
2. Provider totals/status can replace or advance authoritative order state without complete reconciliation.
3. Order/admin mutability can damage financial and operational history.
4. Identity, guest ownership, PII retention, and production secrets/proxy configuration are incomplete.
5. Shipping, tax, legal disclosure, email, returns, and fulfillment operations are not ready to support real customers.
6. Test data, placeholders, or imagery without documented rights could reach a public deployment.

### Major decisions still requiring owner or specialist approval

- Managed Django/PostgreSQL origin vendor, region, service tier, connection-pooling limits, and recovery objectives.
- Production email provider, mailbox activation, SPF/DKIM/DMARC, and retry/escalation policy. `hello@tread-joy.com` and `noreply@tread-joy.com` are reserved future addresses, not active or monitored addresses.
- Supported carriers, shipping service levels, live/contract/table rate source, order cutoff, holiday calendar, and unresponsive preorder-delay behavior.
- Tax registrations/nexus treatment and product tax codes, confirmed with a qualified advisor before enabling collection.
- Terms, privacy, cookie/analytics, shipping, return, warranty, accessibility, and contact disclosures reviewed for the actual business.
- PII/provider-payload/log retention, account deletion/anonymization, backup retention, and customer data-request procedures.
- Staff roles and which users may alter catalog, inventory, fulfillment, refunds, customer data, deployment, and secrets.
- Incident severity, notification/escalation contacts, recovery-time objective, recovery-point objective, and launch rollback authority.

## Phase 0 — Audit, repository hygiene, and dependency baseline

### A0.1 — Remove unsafe launch data and establish asset provenance

- **Priority / status:** P0 — Complete.
- **Objective:** Ensure no test/customer-like data, unapproved image, hidden metadata, or development claim can enter a public release.
- **Why it matters:** Publishing identifiable or unlicensed media creates privacy, trust, and legal risk; test catalog content makes a real store appear fraudulent or unfinished.
- **Current state:** The tracked test imagery and public test catalog have been quarantined, and the public catalog renders its safe empty state. Homepage and social placeholders remain intentionally documented release blockers pending approved factual content.
- **Required work:** Inventory all committed/database-referenced assets and public copy; record owner/license/consent and permitted use; remove the tracked test image and launch-path test records; strip unnecessary EXIF from approved assets; create safe deterministic development fixtures/placeholders that cannot be mistaken for production content; add a pre-release content checklist.
- **Dependencies:** None.
- **Affected areas:** media, static/images, product records/fixtures, templates, seed/setup documentation, Git history review.
- **Security considerations:** Do not print or redistribute personal metadata; confirm whether history cleanup is necessary before any destructive rewrite; keep development data out of production backups and analytics.
- **Testing requirements:** Search tracked files and templates for removed names/paths; load both modes with a clean database; verify missing assets fail safely; inspect rendered catalog/homepage and media metadata.
- **Acceptance criteria:** No unapproved/test/customer-like asset or test product is tracked or publicly rendered; every production asset has recorded provenance; placeholders are unmistakably nonproduction; owner approves the release content inventory.
- **Implementation evidence (2026-08-25):** Migrations quarantine the known product and both variants, remove stale cart lines, preserve three protected order records including the paid payment, and never restore unsafe content on rollback. The release-content command now validates inventory fields, unique paths, checksums, approval/environment state, metadata, AI provenance, and database-backed product images; it fails only on the intentionally documented homepage/social blockers. A disposable PostgreSQL 17 cluster passed 94 focused commerce tests (2 skipped) and 31 focused research tests (3 skipped), and browser smoke checks confirmed the empty catalog, retired-product 404, empty cart, and desktop/mobile text wordmark. Local history was rewritten and pruned; `origin/main` was force-updated with an exact lease, a fresh clone resolves to the rewritten commit, and retired raw-path/blob URLs return 404. The owner approved the release-content inventory and accepted the remote-containment verification on 2026-08-25.

### A0.2 — Remove confirmed dead and duplicate implementation paths

- **Priority / status:** P0 — Complete.
- **Objective:** Leave one discoverable implementation for every active route and business workflow.
- **Why it matters:** Stale checkout/auth/cart code invites security fixes and features to be applied to the wrong path and may be accidentally reconnected later.
- **Current state:** Confirmed unrouted root-level scaffolding has been removed. Cart mutations and customer order presentation now have one canonical route name and owning view, with the former order-history URL retained only as a login-protected compatibility redirect.
- **Required work:** Use repository-wide reference, URL-resolution, import, and template scans; delete only confirmed unreachable modules/aliases; consolidate duplicate URL names/views while preserving intended public URLs or adding explicit redirects; remove stale imports and documentation; do not rewrite migrations.
- **Dependencies:** A0.1 can run independently.
- **Affected areas:** web/views.py, web/models.py, web/tests.py, web/cart/urls.py, web/orders URLs/views/templates/tests, README references.
- **Security considerations:** Confirm no webhook, account recovery, admin, or crafted direct URL depends on a path before removal; avoid re-exposing legacy Stripe handling through compatibility redirects.
- **Testing requirements:** URL reverse/resolve tests, both mode suites, direct-request negative tests, compile/import checks, and repository searches proving no remaining references.
- **Acceptance criteria:** Active behavior has one owning module and one canonical route name; legacy code is removed or explicitly documented with a removal blocker; both modes pass their route and regression tests.
- **Implementation evidence (2026-08-25):** Removed the unrouted root `web` views/models/tests scaffolding, including its hardcoded localhost Stripe flow; removed the duplicate cart update alias while preserving `/cart/update/<id>/`; consolidated customer orders under `orders:order_list` and `orders:order_detail`; and retained `/orders/history/` as an unnamed, login-protected 302 redirect. Canonical route/reverse, redirect, ownership, relation-prefetch, cart mutation, and research negative-capability tests pass. A disposable PostgreSQL 17 cluster passed 79 focused commerce tests and 73 installed-app research tests (5 skipped); both Django mode checks, compile checks, and `makemigrations --check --dry-run` passed. The owner accepted the route and template consolidation on 2026-08-25.

### A0.3 — Create minimal reproducible dependency manifests

- **Priority / status:** P0 — Complete.
- **Objective:** Replace the unrelated frozen environment with reviewed runtime and development dependency inputs and reproducible locks.
- **Why it matters:** Unused packages expand attack surface, slow builds, obscure licenses, and make security upgrades harder.
- **Current state:** Reviewed runtime and standalone development inputs now
  produce hash-locked requirements files from public PyPI only. CPython 3.12
  is recorded as the supported minor; the existing development virtual
  environment was not replaced.
- **Required work:** Derive direct dependencies from imports/settings; choose and document a supported Python minor compatible with the managed origin; create requirements.in for runtime inputs and requirements-dev.in for test/security tooling; use pip-tools to generate pinned requirements.txt and requirements-dev.txt; document upgrade/lock commands and license/vulnerability review; remove packages only after checks prove they are unused.
- **Dependencies:** A0.2, so stale imports do not preserve dead dependencies.
- **Affected areas:** requirements files, runtime documentation, CI setup, deployment build configuration.
- **Security considerations:** Verify hashes or trusted index policy, package provenance, licenses, known vulnerabilities, and separate runtime from development-only tools; never embed private index credentials.
- **Testing requirements:** Build a fresh virtual environment, install each lock independently, run pip check, compile, Django checks, both mode suites, admin/static collection smoke checks, and dependency audit.
- **Acceptance criteria:** Fresh installs are deterministic; every direct package has a documented use; unrelated packages are gone; runtime image excludes development tools; CI can reproduce the environment.
- **Implementation evidence (2026-08-26):** Added `.python-version`, seven
  reviewed runtime inputs, and four development-only inputs; generated ordered
  hash locks with pip-tools 7.6.1 and verified byte-identical regeneration
  under a temporary CPython 3.12.14 build. Separate clean 3.12.14 runtime and
  development environments installed with `--require-hashes`, passed `pip
  check` and compile checks, and showed the runtime contains no pip-tools,
  pip-audit, pip-licenses, or pre-commit. `pip-audit --require-hashes` reports
  no known vulnerabilities for either lock. The auditable license inventory
  covers every installed distribution, reports no unknown/custom license, and
  flags `psycopg`/`psycopg-binary` as LGPL-3.0-only for owner review. A
  disposable PostgreSQL 17 cluster migrated both modes from zero; Django
  checks and `makemigrations --check --dry-run` passed, along with 147
  commerce tests (6 skipped), 73 research tests (5 skipped), admin
  autodiscovery, and isolated static collection. Research remained free of
  commerce routes/models and Stripe initialization; commerce used synthetic
  settings without external calls. The runtime lock uses `--no-allow-unsafe`.
  The standalone development lock is the documented pip-tools 7.6.1 exception:
  it uses `--allow-unsafe` solely to pin and hash its required `pip` and
  `setuptools`, since omitting setuptools makes a clean hash-enforced install
  fail. No CI workflow was added. The owner approved the direct dependency
  purposes, license inventory/audit results, and this narrowly scoped
  development-lock exception on 2026-08-26.

## Phase 1 — Shared CI, configuration, and security foundation

### A1.1 — Add PostgreSQL CI for both deployment modes

- **Priority / status:** P0 — Complete (2026-08-26).
- **Objective:** Make every release prove Django and database behavior against PostgreSQL in commerce and research modes.
- **Why it matters:** SQLite skips the locking semantics used to prevent duplicate allocation and future overselling.
- **Current state:** GitHub requires separate commerce and research PostgreSQL
  jobs, a dependency audit, and a full-history Gitleaks scan on `main` with
  strict branch freshness.
- **Required work:** Add GitHub Actions with a pinned PostgreSQL service and least-privilege test credentials; run mode-specific Django checks/tests, migrations-from-zero, makemigrations --check, compile, static collection, dependency audit, secret scan, and production-configuration checks; cache only package downloads, not database state; make required checks branch-protection ready.
- **Dependencies:** A0.3.
- **Affected areas:** .github/workflows, test settings/environment helpers, requirements-dev, repository documentation.
- **Security considerations:** Use synthetic CI secrets, restricted permissions, pinned action revisions, no fork access to sensitive values, and no external Stripe/email network calls.
- **Testing requirements:** Exercise row locks, uniqueness, transaction rollback, research negative capability tests, and a deliberately failing check to prove the workflow blocks a merge.
- **Acceptance criteria:** One commit produces green, separately visible commerce/research PostgreSQL jobs; concurrency tests execute rather than skip; required checks and troubleshooting instructions are documented.
- **Implementation evidence (2026-08-26):** PR
  [#1](https://github.com/TreadJoy/Shoes/pull/1) added explicit commerce and
  research jobs against isolated digest-pinned PostgreSQL 17.11 services,
  restricted application roles, guarded CI settings, blank-database migration
  and drift checks, warning-fatal deployment checks, isolated static
  collection, hash-enforced dependency auditing, and a shared PostgreSQL
  uniqueness/atomic-rollback contract test. GitHub-hosted
  [Application CI #5](https://github.com/TreadJoy/Shoes/actions/runs/33005044655)
  passed 152 commerce tests (6 skipped), both explicit row-lock race classes,
  and 78 research tests (5 skipped); both modes passed the explicit database
  contract. [Secret Scan #33](https://github.com/TreadJoy/Shoes/actions/runs/33005044653)
  passed with the official Gitleaks 8.30.1 image pinned to its Linux/AMD64
  digest and needed no license or secret. The private repository moved into the
  TreadJoy Enterprise organization so protection could be enforced. With no
  prior branch rule to preserve, `main` now requires the four documented checks
  and strict freshness. Commit `7676e4c` deliberately failed the required
  commerce job in [Application CI #3](https://github.com/TreadJoy/Shoes/actions/runs/33004202293);
  GitHub disabled merging while research and the dependency audit remained
  green. The probe was removed without merging, and commit `91d9f4f` restored
  all four checks to green.

### A1.2 — Harden and validate production settings

- **Priority / status:** P0 — Implemented; owner acceptance pending (2026-08-27).
- **Objective:** Make unsafe or incomplete production configuration fail before serving traffic.
- **Why it matters:** Current non-DEBUG settings are incomplete for a Cloudflare proxy, production origins, CSP, storage, email, and security invariants.
- **Current state:** The repository implements explicit local/CI/staging/production profiles, Cloudflare-locked ingress validation, exact hosts/origins, PostgreSQL TLS policy, SMTP/R2/static requirements, CSP, secure cookies, and staged HSTS checks. Owner acceptance and live provider/origin validation remain pending; repository configuration is not deployed infrastructure.
- **Required work:** Keep the current settings architecture incremental; add typed environment parsing and mode-aware validation; require explicit ALLOWED_HOSTS/CSRF origins/database/email/storage values; configure secure cookies, SSL redirect, HSTS rollout, referrer/frame/content-type controls, CSP, proxy SSL header only for the locked origin path, trusted origins, production static/media storage, and a startup check that research rejects all Stripe configuration.
- **Dependencies:** A0.3 and A1.1.
- **Affected areas:** Shoes/settings.py or a narrowly split settings package, .env.example, deployment checks, tests.
- **Security considerations:** Prevent direct-origin/proxy spoofing, DEBUG leakage, wildcard hosts/origins, insecure cookies, accidental console email, and secrets in error messages; document key rotation.
- **Testing requirements:** Matrix tests for valid/invalid commerce and research environments, Django check --deploy, header/cookie integration tests, direct-origin simulation, and no-secret error assertions.
- **Acceptance criteria:** Each environment either starts with the complete approved security contract or exits with a redacted actionable error; CI proves both success and fail-closed cases.
- **Implementation evidence (2026-08-27):** Added strict local/CI/staging/production settings axes, redacted typed configuration parsing, Cloudflare-locked proxy trust, host/origin/SMTP/database/R2 validation, manifest static storage, public R2 media URLs, CSP middleware, externalized base startup JavaScript, key-rotation support, and custom deployment checks. Added 18 focused settings, mode-boundary, and security-header tests. A clean CPython 3.12 development-lock install passed `pip check`; a public-like research profile passed `check --deploy` with only the two intentional HSTS rollout advisories and collected 134 manifest static files; the runtime lock audit reported no known vulnerabilities. This is repository-only evidence: no live DNS, Cloudflare, R2, database, SMTP, origin, or public deployment was configured.

### A1.3 — Establish logging, health, monitoring, and incident foundations

- **Priority / status:** P0 — Complete (2026-08-28).
- **Objective:** Make service health and business-critical failures visible without exposing sensitive data.
- **Why it matters:** Payment, reservation, inventory, email, and deployment failures cannot rely on console logs or customer reports.
- **Current state:** Application logging is basic; there are no health/readiness endpoints, error monitor, alert routes, correlation IDs, runbooks, or provider-event failure dashboard.
- **Required work:** Define structured log fields and redaction filters; add liveness and dependency-aware readiness endpoints with no sensitive detail; choose error monitoring and alert channels; correlate request/order/provider event identifiers; define alerts for payment reconciliation, reservation expiry backlog, inventory exception, email failure, database/storage outage, and elevated 5xx; write incident triage and credential-exposure runbooks.
- **Dependencies:** A1.2. Provider-specific alerts can be completed with their later integrations.
- **Affected areas:** Django logging/middleware, health URLs/views, monitoring configuration, operations documentation.
- **Security considerations:** Health endpoints must not reveal versions/configuration; logs exclude secrets, tokens, session IDs, full addresses, and unnecessary payloads; monitoring access follows least privilege.
- **Testing requirements:** Redaction tests, health dependency-failure tests, correlation propagation tests, synthetic error/alert delivery in staging, and runbook tabletop.
- **Acceptance criteria:** Operators can distinguish alive, ready, and degraded states; a staged failure creates a redacted searchable event and reaches the approved responder; runbooks name owner, severity, and next action.

### A1.4 — Approve privacy, retention, and security operating policy

- **Priority / status:** P0 — Not started.
- **Objective:** Define which data TreadJoy collects, why, who can access it, how long it remains, and how incidents/deletion requests are handled.
- **Why it matters:** Schema, logs, backups, analytics, support tools, and provider payloads cannot be designed safely without retention and authority decisions.
- **Current state:** Orders, addresses, survey responses, waitlist emails, sessions, and raw Stripe payloads are stored without a complete approved retention/deletion matrix or data-subject request process.
- **Required work:** Inventory fields and processors by mode; classify purpose/sensitivity; propose minimum retention for accounts, consent, abandoned checkout, orders/tax evidence, surveys, waitlist, logs, backups, and provider payloads; define anonymization versus deletion; map staff/provider access; document incident severity/contacts and privacy request verification; obtain owner and qualified legal/accounting review where required.
- **Dependencies:** A1.2; may proceed in parallel with A1.3.
- **Affected areas:** Data models, settings, logs, backups, analytics, email, privacy/legal documentation, staff procedures.
- **Security considerations:** Minimize collection, avoid speculative demographic fields, prevent deletion from destroying required commercial records, and avoid claiming legal compliance from engineering review alone.
- **Testing requirements:** Policy-to-schema traceability review, sample export/deletion/anonymization tabletop, backup-retention check, access-control review, and redaction test inventory.
- **Acceptance criteria:** An approved matrix names purpose, authority, access, retention, deletion/anonymization, backup behavior, and owner for every sensitive data class; dependent tasks reference it.

## Phase 2 — Research deployment production readiness

### A2.1 — Prove the research-mode capability boundary

- **Priority / status:** P0 — Not started.
- **Objective:** Make it technically impossible for the research deployment to initiate payment or create commerce records.
- **Why it matters:** Research is intentionally public before commerce and must fail closed even under crafted requests or configuration mistakes.
- **Current state:** Mode-aware installed apps/routes and subprocess tests are a strong base; shared product preview routes remain intentional; complete production-environment and dependency-import assertions are not yet in CI.
- **Required work:** Add route/app/import/configuration assertions; test all known commerce URL patterns and crafted POSTs; verify templates/context never emit purchase controls or commerce endpoints; ensure research migrations/database lack commerce tables where intended; make Stripe packages/configuration unreachable at startup; document allowed research capabilities.
- **Dependencies:** A1.1 and A1.2.
- **Affected areas:** Shoes/settings.py, Shoes/urls.py, base/navigation/product templates, deployment-mode tests, release checklist.
- **Security considerations:** Test direct URLs rather than navigation only; reject credentials rather than ignore them; avoid sharing sessions, databases, caches, secrets, or media containing commerce/customer data.
- **Testing requirements:** PostgreSQL research suite, URL enumeration, crafted order/payment requests, template link scan, import instrumentation, and production-like startup with/without forbidden Stripe variables.
- **Acceptance criteria:** CI proves no registered/importable order-taking path, Stripe initialization, order creation, or commerce credential in research mode; allowed product previews remain read-only and documented.

### A2.2 — Make research identity, consent, email, and abuse controls production-ready

- **Priority / status:** P0 — Not started.
- **Objective:** Collect survey/waitlist/account data transparently and resiliently without exposing or spamming participants.
- **Why it matters:** Research mode still handles personal data and public forms; weak consent and anti-abuse controls can harm reputation before commerce launches.
- **Current state:** Waitlist email is case-insensitively normalized/unique with controlled source values, and completed surveys are anonymous (session drafts remain transient). Signup count is public, consent/version/unsubscribe/suppression are absent, email uses console backend, and public forms have no complete rate/bot controls.
- **Required work:** Decide whether public signup count remains; add privacy notice/consent version/timestamps and marketing preference separation; configure verified transactional/marketing sender behavior and suppression/unsubscribe; add application throttling plus scoped Cloudflare rate/WAF or Turnstile only where evidence supports it; define survey/waitlist retention and staff export/access; add accessible success/error states.
- **Dependencies:** A1.3, A1.4, and an approved email provider decision.
- **Affected areas:** waitlist, survey, accounts/allauth, forms/templates, email configuration, Cloudflare rules, admin/export tooling.
- **Security considerations:** Prevent enumeration, injection, automated submissions, consent spoofing, formula injection in exports, and cross-mode data sharing; do not treat marketing consent as required for operational email.
- **Testing requirements:** Duplicate/normalization, consent version, unsubscribe/suppression, rate-boundary, crafted input, export-safety, accessibility, email mock, and both mode tests.
- **Acceptance criteria:** Every collected field has notice/purpose/retention; consent and suppression are durable; abuse is bounded without blocking ordinary use; verified email flows work in staging; staff access is permissioned.

### A2.3 — Provision, rehearse, and launch the research deployment

- **Priority / status:** P0 — Not started.
- **Objective:** Deploy research mode through Cloudflare to a managed Django/PostgreSQL origin with repeatable release and recovery.
- **Why it matters:** The research site is the first public validation surface and the production architecture rehearsal for commerce.
- **Current state:** `tread-joy.com` has been purchased through Cloudflare as the intended base domain, but no research hostname allocation, DNS, TLS, managed origin, R2, managed database, deployment definition, backups, observability, or rollback process is configured.
- **Required work:** Select an approved research hostname plus managed origin/vendor/region; provision a separate research database and least-privilege roles; configure Cloudflare DNS, Full strict TLS, WAF/rate rules, origin lock-down, static/media caching, and an R2 custom domain; configure secrets, email, logs, health checks, migrations, backups/PITR, restore and rollback; publish approved research privacy/terms/accessibility/contact content and basic canonical/robots/social metadata; complete keyboard, WCAG 2.2 AA, responsive, and performance launch checks; deploy one immutable release artifact and run launch/rollback rehearsals.
- **Dependencies:** A0.1–A0.3, A1.1–A1.4, A2.1, and A2.2.
- **Affected areas:** Hosting/IaC or deployment config, Cloudflare, R2/storage, database, CI/CD, settings, operations docs.
- **Security considerations:** Separate research secrets/database from commerce; no Stripe credentials; restrict origin/admin; protect deploy credentials; cache only public safe responses; treat R2 custom-domain objects as public.
- **Testing requirements:** Clean deploy, migrations, smoke/user-flow/accessibility checks, header/TLS/cache validation, backup and point-in-time/restore drill, origin-bypass attempt, monitoring alert, rollback to prior artifact, and research negative commerce tests in production-like staging.
- **Acceptance criteria:** Research runs from a recorded commit with green required checks, approved domain/TLS/content/legal notices, WCAG 2.2 AA launch evidence, acceptable measured performance, separate data/services, tested restore/rollback, active monitoring, and owner launch acceptance; it cannot take an order.

## Phase 3 — Commerce data integrity and identity

### A3.1 — Strengthen catalog, money, and cart database invariants

- **Priority / status:** P0 — Partially implemented in cleanup Phase 3; remaining catalog/order work open (2026-08-28).
- **Objective:** Move stable commerce truths from application convention into understandable PostgreSQL constraints.
- **Why it matters:** Invalid prices, ambiguous carts, or inconsistent totals can create financial loss and records that admin/database tools cannot safely interpret.
- **Current state:** Variant selling/compare-at prices, product price checks, order nonnegative/discount bounds, and cart principal constraints are implemented. Order arithmetic formulas remain deferred because legacy totals are not consistently decomposed; normalized currency and broader catalog/order invariants remain open.
- **Required work:** Retain PostgreSQL coverage for the implemented constraints; establish a verified legacy-total backfill before adding formula checks; define normalized currency representation; add indexes for real catalog/cart/order access paths; use staged migrations for remaining constraints.
- **Dependencies:** A0.1, A0.2, A1.1, and approved handling for any invalid development data.
- **Affected areas:** products, cart, orders models/migrations/services/admin, schema documentation.
- **Security considerations:** Never trust client values during cleanup; avoid logging invalid PII; review migration locks and rollback; do not invent discount policy while constraining arithmetic.
- **Testing requirements:** PostgreSQL constraint and concurrent-cart tests, migration forward/backward or safe-rollback tests, invalid-data fixtures, server-price tests, and both mode migration checks.
- **Acceptance criteria:** PostgreSQL rejects every documented impossible stable state; existing valid behavior passes; constraints and relationships are understandable in a database tool; migration/recovery instructions are recorded.

### A3.2 — Preserve historical customer, order, and payment records

- **Priority / status:** P0 — Partially implemented in cleanup Phase 3; address/history work remains (2026-08-28).
- **Objective:** Prevent account, address, catalog, or admin changes from erasing what occurred in a commercial transaction.
- **Why it matters:** Support, refunds, taxes, disputes, and audits depend on stable historical facts.
- **Current state:** OrderItem snapshots product facts and immutable BOM component snapshots are now recorded/backfilled. ShippingAddress still belongs to a user with cascade behavior and order/admin relationships can lose or mutate important history; deletion/retention policy is incomplete.
- **Required work:** Apply the approved retention matrix; snapshot checkout name/email/full address/country and shipping/tax/service promises on the order; protect or anonymize user/catalog relations without cascading commercial history; add immutable identifiers/timestamps and database protections; define abandoned-order cleanup separately from paid records.
- **Dependencies:** A1.4 and A3.1.
- **Affected areas:** accounts, orders, addresses, payments/refunds, admin, migrations, privacy/export/deletion services.
- **Security considerations:** Balance historical obligations with minimization; restrict address/payment access; ensure anonymization cannot break reconciliation; do not treat backups as immediately mutable.
- **Testing requirements:** Account/catalog deletion and anonymization tests, snapshot immutability, admin permission tests, retention-boundary tests, migrations, and historical order rendering after source changes.
- **Acceptance criteria:** Paid/refunded/fulfilled history remains intelligible and internally consistent after permitted account/catalog lifecycle actions; PII is retained or anonymized only under the approved policy.

### A3.3 — Correct authentication, cart merge, and guest order access

- **Priority / status:** P0 — Partially implemented in cleanup Phases 1–2; guest order access and policy records remain open (2026-08-28).
- **Objective:** Provide coherent optional accounts and secure continuity from guest browsing through payment and later support.
- **Why it matters:** Identity confusion can expose another customer's cart/order or strand a purchaser without access.
- **Current state:** Allauth effective login and UI are username-based, email verification is optional, and guest-cart merge now combines/caps items with visible notices across the session-rotation boundary. Signed guest-order access, order claiming, and durable terms/privacy acceptance remain open.
- **Required work:** Retain the approved username-login/optional-verification policy and exercise it through staging email flows; preserve and extend deterministic cart-merge/session-rotation coverage; issue expiring/revocable signed guest-order links to the checkout email; allow safe authenticated claiming after re-verification; record legal notice versions without coupling operational email to marketing consent.
- **Dependencies:** A1.2, A1.4, A2.2 where shared, A3.1, and owner approval of identity/claim expiration policy.
- **Affected areas:** accounts/allauth settings/templates/adapters, cart services, orders access, email, consent records, sessions.
- **Security considerations:** Prevent enumeration, link leakage/replay, session fixation, cross-user merge, social-account confusion, and unauthorized claim; hash/store tokens safely and redact them from logs.
- **Testing requirements:** Signup/login/recovery/verification, explicit absence of unapproved social providers, guest/auth cart cases, concurrent merge, link expiry/revocation/replay, cross-user order denial, claim conflict, session rotation, and accessibility.
- **Acceptance criteria:** UI and effective auth behavior match; every cart/order is accessible only by its legitimate guest/account principal; merge/claim rules are documented and idempotent; recovery and verification work through the production email path.

### A3.4 — Establish staff roles and safe commerce administration

- **Priority / status:** P0 — Not started.
- **Objective:** Limit staff capabilities by operational responsibility before real customer and payment data exists.
- **Why it matters:** Default broad Django admin access allows accidental or malicious financial, inventory, and privacy damage.
- **Current state:** Preorder admin has stronger superuser/audit behavior, but order/payment fields and destructive actions remain broadly editable; no approved staff-role matrix or admin access perimeter exists.
- **Required work:** Approve roles for catalog, inventory, fulfillment, support/returns, finance/refunds, customer data, and deployment; implement groups/object-action checks; make financial/provider/history fields read-only; disable destructive deletion; require confirmation and actor/reason for sensitive actions; protect admin through MFA and a reviewed Cloudflare Access/origin approach without replacing Django authorization.
- **Dependencies:** A1.3, A1.4, A3.2, and owner-approved role matrix.
- **Affected areas:** Django admin, auth/groups/permissions, order/product/preorder services, audit records, Cloudflare/admin operations.
- **Security considerations:** Least privilege, separation of duties for refunds/deployment where practical, session security, break-glass access, audit immutability, and no PII in list pages unnecessarily.
- **Testing requirements:** Permission matrix tests for each action/role, read-only/deletion tests, audit actor/reason tests, direct POST bypass attempts, MFA/access staging test, and admin usability review.
- **Acceptance criteria:** Every sensitive admin action has an approved role, server-side enforcement, confirmation where needed, and durable audit; ordinary staff cannot edit/delete financial history or bypass domain transitions.

## Phase 4 — Cart and 30-minute inventory reservation

### A4.1 — Add an auditable reservation model and state contract

- **Priority / status:** P0 — Not started.
- **Objective:** Represent temporary claims on finished SKU/preorder capacity independently from cart display and final allocation.
- **Why it matters:** A precise durable model is required to prevent oversell and reconcile abandoned/expired Checkout Sessions.
- **Current state:** `CheckoutAttempt`, immutable quote/BOM facts, and finished-SKU/preorder `InventoryReservation` rows represent active, committed, released, and review-required claims. Opaque attempt UUIDs, expiry timestamps, one-active-attempt-per-cart uniqueness, nonnegative constraints, and read-only admin inspection are implemented.
- **Required work:** Design a reservation aggregate tied to cart/order, ProductVariant or preorder allocation, Stripe Checkout Session when created, quantity, created/expires timestamps, state, idempotency key, release/commit reason, and audit events; define active uniqueness/indexes and allowed state transitions; make 30 minutes the approved TTL; document availability as on-hand/allocation minus active reservations and committed sales.
- **Dependencies:** A3.1–A3.3.
- **Affected areas:** products/preorders, cart, orders, new migrations/services/admin read views.
- **Security considerations:** Use opaque identifiers externally; do not expose other carts/orders; preserve event history; ensure cleanup cannot release another session's reservation.
- **Testing requirements:** Model constraints, expiry boundaries with controlled time, duplicate idempotency keys, stocked/preorder cases, invalid transitions, migrations, admin immutability, and query/index review.
- **Acceptance criteria:** Schema and service contract unambiguously distinguish active, committed, expired, canceled, and failed reservations; PostgreSQL prevents invalid stable states; database tools reveal ownership and history.

### A4.2 — Implement atomic reserve, release, and payment commit services

- **Priority / status:** P0 — Ready for owner acceptance; PostgreSQL CI evidence required.
- **Objective:** Guarantee that concurrent customers cannot reserve or commit more finished inventory than exists.
- **Why it matters:** This is the core overselling control and must remain correct under retries and process failure.
- **Current state:** Checkout locks the cart and authoritative finished SKU/preorder rows, reprices and validates fulfillment, subtracts nonexpired active reservations, and creates a 30-minute reservation atomically. Reconciliation commits its own reservation and allocation once; definite failure/expiry releases it, while late/shortfall payment becomes review-required without an inventory commitment. A PostgreSQL last-unit race test is present but skipped by SQLite.
- **Required work:** Centralize availability calculation; lock SKU/preorder allocation and relevant active reservations; atomically create/refresh the caller's reservation; reject shortages before Stripe Session creation; release idempotently on cancellation/expiry/failure; commit exactly once after reconciled payment; adapt paid allocation to consume the matching reservation instead of decrementing independently; retain a manual exception only for impossible/reconciliation failures.
- **Dependencies:** A4.1.
- **Affected areas:** products availability/preorder services, orders allocation/payment services, cart/checkout, admin exception views.
- **Security considerations:** Scope every operation to expected order/session/idempotency identity; validate quantities/prices again inside the transaction; avoid denial through unlimited reservations.
- **Testing requirements:** PostgreSQL TransactionTestCase concurrency for last-unit and preorder capacity, duplicate/reordered release/commit, process rollback, expired reservation race with payment, mixed fulfillment rejection, and unauthorized reservation access.
- **Acceptance criteria:** Concurrent tests prove accepted active reservations plus committed units never exceed authority; all operations are idempotent and auditable; payment consumes only its own valid reservation.

### A4.3 — Reconcile expiration and abandoned reservations operationally

- **Priority / status:** P0 — In progress (application complete; operations pending).
- **Objective:** Release inventory promptly when Checkout expires and detect any reservation/provider state drift.
- **Why it matters:** Webhooks can be delayed or missed; relying on a single delivery can strand scarce inventory.
- **Current state:** Signed Session expiry/async-failure events and an idempotent `release_expired_reservations` command release nonpaid claims; paid/review orders cannot be swept, and read-only admin inspection is available. The managed scheduler, backlog/drift alert, and production runbook are not provisioned.
- **Required work:** Add a safe idempotent expiry service and periodic reconciliation mechanism appropriate to the managed origin; release locally expired nonpaid reservations under documented safeguards; accept provider state as an explicit future input rather than embedding API calls in the core transition; record failures and alert on backlog/drift; provide staff read-only inspection and controlled retry. A5.3 will set the Stripe Session expiry, and A5.4 will wire provider expiry/failure events and bounded stale-session lookup into this service.
- **Dependencies:** A1.3 and A4.2.
- **Affected areas:** orders webhooks/services, reservation model, scheduling mechanism, monitoring, admin/operations runbook.
- **Security considerations:** Authenticate provider events, restrict retry tools, rate-limit provider API calls, redact payloads/tokens, and prevent a sweep from releasing a paid reservation.
- **Testing requirements:** Controlled-time expiry, missing/duplicate/out-of-order webhook, delayed payment at boundary, provider API timeout/rate limit, sweep reentrancy, backlog alert, and staff permission tests.
- **Acceptance criteria:** Expired/canceled inventory returns automatically and exactly once; paid reservations cannot be swept; drift is visible and retryable; no stale active reservation exceeds the documented grace/reconciliation bound without an alert.

## Phase 5 — Shipping, tax, Checkout, and payments

### A5.1 — Implement launch shipping services and address eligibility

- **Priority / status:** P0 — Ready for owner acceptance; provider/PostgreSQL acceptance pending.
- **Objective:** Quote, charge, snapshot, and fulfill approved contiguous-US shipping services consistently.
- **Why it matters:** Zero-dollar placeholder shipping and unrestricted addresses create direct financial loss and broken customer promises.
- **Current state:** Checkout collects a US-style address and stores zero shipping total; country defaults to the United States but Alaska, Hawaii, territories, PO boxes, carriers, rates, and service levels are not authoritatively handled.
- **Required work:** Obtain owner decisions for carrier(s), service levels, rate source, PO/APO/FPO policy, cutoff, holiday calendar, and fallback when rate lookup fails; validate/normalize country/state/postal eligibility server-side; quote only approved services; snapshot service, carrier, charge, quoted transit estimate, tender promise, and rate-source version on the order; keep shipping charge in server-calculated totals sent to Stripe; disclose preorder versus transit timing.
- **Dependencies:** A1.3, A3.1–A3.2, A4.2, and approved shipping decisions.
- **Affected areas:** checkout form/service/templates, order/address schema, totals, Stripe line items, shipment/admin, email, operations documentation.
- **Security considerations:** Treat addresses as PII; do not leak them to unnecessary rate/log systems; authenticate carrier APIs, constrain outbound calls/timeouts, and do not accept client-selected prices or hidden service IDs.
- **Testing requirements:** Contiguous state/postal boundaries, disallowed destinations, normalization, rate timeout/fallback, service tampering, money snapshots, preorder wording, carrier mocks, and responsive/accessibility form review.
- **Acceptance criteria:** Every accepted address and service is launch-eligible; customer-visible and charged shipping match the immutable order snapshot; failures stop before payment with actionable guidance; operations can purchase/tender the promised service.

### A5.2 — Establish tax and legal collection gates

- **Priority / status:** P0 — Not started.
- **Objective:** Collect tax only where the business is registered/required and preserve evidence of the calculation.
- **Why it matters:** Enabling automated tax without registration or correct product treatment can silently collect zero or collect/remit incorrectly; engineering cannot decide nexus.
- **Current state:** tax_total is always zero and Stripe automatic_tax is disabled; registrations, nexus analysis, product tax codes, shipping taxability, reporting, and customer disclosures are unresolved.
- **Required work:** Obtain qualified tax/legal advice and owner approval; document registered jurisdictions and review cadence; assign approved Stripe/product tax codes; choose Stripe Tax or another approved calculation source; calculate against normalized address and shipping; reconcile calculation to Checkout; snapshot tax amount, jurisdiction summary, source/version, and exemption evidence if later applicable; define reporting/refund effects without storing unnecessary tax-provider PII.
- **Dependencies:** A1.4, A3.1–A3.2, A5.1, and written advisor/owner decisions.
- **Affected areas:** product tax metadata, checkout totals, orders/refunds, Stripe configuration, reporting, legal/customer documentation.
- **Security considerations:** Minimize provider data, protect tax identifiers/reports, restrict configuration changes, and never represent test calculations as professional advice or registration proof.
- **Testing requirements:** Registered/unregistered destination mocks, shipping taxability, rounding, refunds, provider timeout, tampering, snapshot/reconciliation, and test-versus-live configuration separation.
- **Acceptance criteria:** Collection cannot be enabled without recorded registration/configuration approval; charged tax reconciles to the order and is auditable/refundable; zero-tax behavior is intentional and explainable for every launch destination.

### A5.3 — Make Checkout creation atomic and idempotent

- **Priority / status:** P0 — Not started.
- **Objective:** Ensure one customer intent creates at most one order, reservation, and active Stripe Checkout Session.
- **Why it matters:** Current order-before-Stripe behavior can leave orphan records and duplicate customer charges/holds under retries.
- **Current state:** A valid POST atomically creates/reuses one active attempt per locked cart, snapshots the authoritative quote/BOM, and reserves inventory before the network call. Stripe Checkout is created after commit through an instance-scoped client with a stable idempotency key; ambiguous network/API/rate-limit failures reuse the attempt/key, definite rejection releases it, and no abandoned order/address is created.
- **Required work:** Introduce a server-generated checkout intent/idempotency key scoped to the cart/principal and material quote version; validate/reprice cart and create order snapshot/reservation transactionally; call Stripe with the same idempotency key; persist the resulting Session through a retry-safe state machine; on provider failure retain a diagnosable retryable attempt without duplicating the order/reservation; expire superseded attempts; avoid holding database locks during network calls.
- **Dependencies:** A3.2–A3.3, A4.2–A4.3, A5.1, and A5.2.
- **Affected areas:** checkout views/forms/services, order/payment-attempt schema, reservations, Stripe client, session state, customer error UX.
- **Security considerations:** Bind intent to principal/cart/quote, rotate or invalidate after material cart change, prevent request replay and parameter substitution, and never expose provider secrets in retry errors.
- **Testing requirements:** Double POST, refresh/back, provider timeout before/after response, database failure, changed cart/price, expired intent, concurrent same-cart attempts, guest/auth cases, and exactly-one order/session/reservation assertions.
- **Acceptance criteria:** Repeating the same intent returns or resumes the same safe Checkout result; no retry creates duplicate authoritative records or holds inventory indefinitely; failures are customer-safe, diagnosable, and recoverable.

### A5.4 — Reconcile Stripe payments and complete webhook lifecycle

- **Priority / status:** P0 — In progress (core reconciliation complete; dispute/operations pending).
- **Objective:** Advance money/order/inventory state only after a signed Stripe event matches the expected order and an eligible payment state.
- **Why it matters:** Authentic webhook transport does not guarantee correct amount, currency, metadata, Session ownership, or payment completion.
- **Current state:** New Checkout events retrieve the authoritative Session and use one idempotent reconciler shared with the success return. It verifies paid state, mode/livemode, attempt/Session ownership, amount, currency, PaymentIntent, metadata, reservation age, and Stripe-collected address; expected totals are never overwritten. Valid payment creates the order/address/payment/snapshots and commits inventory once; mismatches create a durable review record without fulfillment. Explicit Stripe clients, dynamic payment methods, async success/failure, expiry, duplicate/out-of-order protection, bounded audit fields, and raw-payload migration tooling are implemented. Dispute/chargeback handling, production alerts/replay, webhook/provider configuration, and backup-verified payload purge remain open.
- **Required work:** Upgrade the Stripe SDK/API version through reviewed changelogs and contract tests; use an explicit Stripe client and restricted key; omit hardcoded payment methods if approved dynamic methods are safe; retrieve/verify bounded provider objects when needed; reconcile order ID, Checkout Session, PaymentIntent, amount, currency, metadata, livemode, expected status, and reservation before transition; never overwrite expected totals to make a mismatch pass; handle checkout completed/expired, async success/failure, payment success/failure, refund updates/failures, disputes/chargebacks, duplicates, and out-of-order events; persist attempt count, processing result/error code, and safe replay controls; alert on mismatch/failure.
- **Dependencies:** A1.3, A4.3, A5.3, and Stripe Dashboard/test configuration.
- **Affected areas:** orders/views.py, payment/webhook services/models/admin, Stripe settings/client, reservations, monitoring, tests/runbooks.
- **Security considerations:** Verify signatures against raw body, separate test/live endpoints and keys, minimize/redact payload retention, restrict replay/refund tools, use strong Stripe account MFA, and never store card data.
- **Testing requirements:** Official Stripe fixture/mocked contracts for every subscribed event; amount/currency/metadata/status/livemode mismatch; duplicate/out-of-order/retry; signature failures; partial transaction rollback; expiry-payment race; reservation commit/release; dispute/refund; SDK upgrade regression; live-mode isolation.
- **Acceptance criteria:** Only a fully reconciled eligible payment commits inventory and marks an order paid; mismatches preserve expected order amounts and create an alert/exception; every event is idempotent, traceable, safely replayable, and covered by tests.

## Phase 6 — Orders, fulfillment, returns, and administration

### A6.1 — Centralize the order lifecycle and immutable audit history

- **Priority / status:** P0 — Not started.
- **Objective:** Make one domain service the authority for allowed order transitions and their evidence.
- **Why it matters:** Views, webhooks, shipment records, and admin actions can otherwise disagree or skip required side effects and customer promises.
- **Current state:** OrderStatusEvent exists and shipment logic has useful safeguards, but status changes are scattered and admin actions can jump states or directly edit fields.
- **Required work:** Approve a state/transition table for pending payment, paid, inventory review, fulfillment, tendered/shipped, delivered, canceled, return/refund states, and preorder delay consent; centralize preconditions and side effects; record actor/source/reason/from/to/timestamps/provider IDs; make history append-only and relevant fields admin read-only; distinguish payment, fulfillment, return, and refund sub-state rather than overloading one status where needed.
- **Dependencies:** A3.2, A3.4, and A5.4.
- **Affected areas:** orders models/services/admin/views, shipments, reservations, refunds, customer order pages, email events.
- **Security considerations:** Enforce permission and ownership at service boundary; require confirmation for irreversible actions; prevent forged actor/reason; preserve history against deletion/editing.
- **Testing requirements:** Transition table success/invalid cases, role permissions, duplicate transition, rollback, webhook/admin parity, history immutability, customer visibility, and migration tests.
- **Acceptance criteria:** Every state change uses the same tested service; impossible jumps are rejected; required history/side effects occur exactly once; admin cannot bypass the lifecycle.

### A6.2 — Complete fulfillment, shipment, tracking, and preorder-delay operations

- **Priority / status:** P0 — Not started.
- **Objective:** Give staff a reliable workflow from paid inventory through carrier tender, tracking, delivery, and preorder exception handling.
- **Why it matters:** Payment success is not business success unless orders are shipped within the disclosed promise and exceptions are acted on.
- **Current state:** Shipment records and inventory-review blocking exist; carrier/service rules, next-business-day deadline calculation, tracking validation, delay consent, and customer notification are incomplete.
- **Required work:** Implement approved cutoff/holiday calculation; create fulfillment queues by stocked/preorder deadline; validate carrier/service/tracking and tender timestamp; integrate tracking status manually or through an approved provider only if justified; represent preorder estimated window, delay notice, revised date, customer consent/cancellation, and escalation; prevent shipment during inventory/payment/return holds; record packing/tender exceptions.
- **Dependencies:** A5.1, A6.1, and owner decisions listed under fulfillment policy.
- **Affected areas:** shipments/orders/preorders services/models/admin, dashboards, emails, customer history, monitoring.
- **Security considerations:** Do not expose full addresses/tracking unnecessarily; authenticate carrier callbacks/APIs; restrict fulfillment actions; prevent formula injection in exports/labels.
- **Testing requirements:** Business-day boundaries/holidays/time zones, preorder window/delay paths, invalid tracking, duplicate tender/delivery, blocked order, permission, customer messaging, and full lifecycle manual rehearsal.
- **Acceptance criteria:** Staff can identify what must ship and why, record tender/tracking once, handle approved delays, and leave a complete customer-visible/internal audit without bypassing holds.

### A6.3 — Implement cancellations, returns, exchanges, inspections, and refunds

- **Priority / status:** P0 — Not started.
- **Objective:** Represent and enforce the approved post-purchase policy with human review and Stripe reconciliation.
- **Why it matters:** Real customers need a predictable remedy, while the business needs to avoid duplicate refunds, unsafe restocking, and undocumented exceptions.
- **Current state:** Refund webhook synchronization and manual review concepts exist, but no customer request, eligibility, exchange, inspection, return shipment, component disposition, or in-app refund initiation workflow implements the approved policy.
- **Required work:** Model request type/reason/items/deadlines/shipping responsibility/evidence/review/inspection/disposition/exchange/refund links; calculate eligibility from immutable order/delivery/tender facts; require staff review and actor/reason; initiate Stripe refunds idempotently with expected amount reconciliation; track failure and customer communication; restock only approved complete/safe/resellable units/components; quarantine others; implement one-free-size-exchange limit and unavailable-replacement refund path.
- **Dependencies:** A1.4, A5.4, A6.1–A6.2, and approved operational forms/instructions.
- **Affected areas:** orders/refunds/new return domain, products/inventory, admin, customer account/guest access, email, reporting.
- **Security considerations:** Verify order ownership, protect uploaded evidence, restrict refund amounts/actions, prevent duplicate/excess refunds, retain dispute/audit evidence, and avoid exposing internal fraud notes.
- **Testing requirements:** Every approved eligibility boundary, stocked/preorder cancellation before/after tender, 30-day delivery boundary, preference/defect/incorrect paths, exchange limit/stock race, inspection dispositions, duplicate refund/webhook, partial failure, permissions, and manual Stripe test-mode rehearsal.
- **Acceptance criteria:** Approved requests can be submitted, reviewed, fulfilled/refunded, communicated, and audited; disallowed requests receive accurate explanations; inventory and payment totals remain reconciled under retry/failure.

### A6.4 — Add reliable transactional customer communications

- **Priority / status:** P0 — Not started.
- **Objective:** Deliver verified, accessible, retryable messages for account and order lifecycle events.
- **Why it matters:** Customers need receipts, shipping information, delay choices, return/refund status, and secure guest access; console email is not production service.
- **Current state:** The console backend is configured. `hello@tread-joy.com` and `noreply@tread-joy.com` are reserved future addresses, while the legacy `@treadjoy.com` contact-page and sender-default references are stale launch blockers. There are no production templates/provider, active mailboxes, delivery event records, retry/escalation workflow, or complete lifecycle messages.
- **Required work:** Select and configure an email provider; activate the intended `hello@tread-joy.com` support and `noreply@tread-joy.com` sender addresses; configure SPF, DKIM, DMARC, bounce/complaint handling and suppression; then replace the legacy `@treadjoy.com` code references. Create branded plain-text/HTML templates for verification/recovery, receipt, payment exception, shipment, preorder delay/consent, cancellation, return/exchange, refund, and guest access; enqueue/send after committed domain state using a reliable outbox/retry design appropriate to the managed origin; record delivery status without storing full content unnecessarily.
- **Dependencies:** A1.3–A1.4, A3.3, A6.1–A6.3, and provider/brand approval.
- **Affected areas:** settings, email/outbox models/services, templates, account/order workflows, monitoring, DNS.
- **Security considerations:** Signed links expire/revoke; templates escape user data; avoid sensitive content in subject/previews; separate transactional from marketing consent; process bounces/complaints safely.
- **Testing requirements:** Provider mocks, post-commit send, retry/idempotency, bounce/suppression, inaccessible token, template escaping, plain-text parity, screen-reader/content review, staging deliverability across major mailbox providers.
- **Acceptance criteria:** Each authoritative lifecycle event produces at most one appropriate message attempt with observable retry/failure state; domain authentication passes; critical email failure alerts staff without corrupting the order.

## Phase 7 — Catalog, storefront, and conversion readiness

### A7.1 — Build a complete, trustworthy production catalog

- **Priority / status:** P1 — Not started.
- **Objective:** Replace test records with approved sellable variants and enough structured information for a customer to evaluate the product.
- **Why it matters:** A polished shell cannot convert or reduce returns if product facts, imagery, fit, and availability are incomplete.
- **Current state:** A0.1 quarantined the known test catalog and customer-like image, so the public catalog currently renders its safe empty state. Approved production products, imagery, fit, care, and other merchandising facts remain absent, and the product/variant schema still lacks several launch facts.
- **Required work:** Define minimum launch product data for SKU/name/slug/audience/category/prices/status, ordered variant values, size/fit guide, materials/care, included modular components/compatibility explanation, weight/dimensions where operationally needed, preorder/stock promise, approved claims, and multi-angle responsive media with alt text/provenance; add validation/admin completeness checks; normalize catalog values; expose customer-friendly availability without raw counts.
- **Dependencies:** A0.1, A3.1, A4.2, A5.1–A5.2, and approved product facts/assets.
- **Affected areas:** products models/admin/forms/services/templates, media/R2, structured data, fixtures/import tools.
- **Security considerations:** Validate uploads, strip metadata, preserve licensing/consent, prevent stored XSS in rich copy, and restrict price/inventory publication actions.
- **Testing requirements:** Required-field/normalization, price/availability/preorder, media validation/alt, admin permissions/completeness, responsive images, empty/sold-out states, and clean-database catalog smoke tests.
- **Acceptance criteria:** Every published SKU has approved accurate content/assets, valid price/tax/shipping metadata, clear availability/fit/modularity information, and no development/test language or raw stock exposure.

### A7.2 — Complete the cart-to-post-purchase customer journey

- **Priority / status:** P1 — Not started.
- **Objective:** Make product selection, cart, Checkout handoff, confirmation, account/guest history, and support paths cohesive and accessible.
- **Why it matters:** High-risk backend correctness must be understandable to customers or it will still cause abandonment, duplicate attempts, and support burden.
- **Current state:** Catalog/product/cart/checkout/order templates exist and are visually coherent, but variant detail, pricing-change feedback, reservation timing, shipping/tax summary, hosted-payment wording, durable guest access, error recovery, and post-purchase content are incomplete.
- **Required work:** Add explicit variant/size selection and unavailable states; show server-repriced totals, reservation/expiry expectations, stocked/preorder distinction, shipping/tax/return links, loading/double-submit protection, safe Stripe redirect language, pending/success/failure/expired recovery, durable order confirmation/history, guest access, and accessible cart/order empty/error states; ensure no commerce UI appears in research mode.
- **Dependencies:** A3.3, A4.3, A5.1–A5.4, A6.1, A6.4, and A7.1.
- **Affected areas:** product/cart/checkout/order/account templates, forms, vanilla JavaScript, messages/toasts, navigation.
- **Security considerations:** Never expose another order or trust client state; avoid leaking signed links/referrers; keep mutations CSRF-protected/idempotent; prevent duplicate submit during slow provider calls.
- **Testing requirements:** Full guest/account stocked/preorder paths, repricing/stock race, invalid address, payment failure/expiry/back navigation, order ownership, research negative UI, keyboard/screen-reader, reduced motion, and five viewport classes.
- **Acceptance criteria:** A customer can understand and complete or safely recover from every launch journey; displayed totals/status match authoritative state; all sensitive pages enforce ownership and are excluded from unsafe caching.

### A7.3 — Finish approved brand, trust, legal, and support content

- **Priority / status:** P1 — Not started.
- **Objective:** Replace development placeholders with verified brand storytelling and complete trust/support destinations.
- **Why it matters:** Fabricated or missing claims undermine credibility, while absent policies leave customers unable to make an informed purchase.
- **Current state:** The homepage implements the intended section architecture but uses labeled placeholders; legal, shipping, return, privacy, terms, accessibility, warranty/support, community/impact evidence, and complete footer destinations are missing.
- **Required work:** Obtain approved logo/photography/video/posters/copy and source records; publish only real community/impact/goal claims or explicitly label future goals; create reviewed policy/support pages consistent with approved operations; complete mode-specific navigation/footer/contact; keep homepage commerce CTAs directed to catalog/how-it-works rather than inline selling; preserve campaign flexibility outside commerce records.
- **Dependencies:** A0.1, A1.4, A2.3 for research content, A5.1–A5.2, A6.3, A7.1, and legal/brand approval.
- **Affected areas:** core templates/content, base/navigation/footer, static/R2 media, legal/support URLs, SEO metadata.
- **Security considerations:** No AI-generated public imagery, fabricated partner/impact claims, unlicensed marks/media, hidden metadata, unsafe embeds, or contact forms without abuse controls.
- **Testing requirements:** Link/content-claim inventory, both mode navigation, responsive/keyboard review, contrast/alt text, YouTube consent/performance behavior, legal-policy consistency against implemented workflows, and owner visual/content acceptance.
- **Acceptance criteria:** No development placeholder or unsupported claim remains on a public release; every footer/policy/support link resolves to approved content; both modes communicate their intended action clearly and truthfully.

## Phase 8 — Accessibility, SEO, privacy, and performance

### A8.1 — Complete WCAG 2.2 AA audit and remediation

- **Priority / status:** P1 — Not started.
- **Objective:** Make all public and essential staff/customer workflows perceivable, operable, understandable, and robust.
- **Why it matters:** Accessibility is a customer requirement, legal risk area, and quality signal; visual polish alone does not prove it.
- **Current state:** Semantic navigation, skip link, focus behavior, responsive layouts, and reduced-motion intent are a good base; no complete automated/manual audit or documented exceptions exist.
- **Required work:** Add an approved automated accessibility smoke tool to CI for representative pages/states; manually audit keyboard/focus, headings/landmarks, accessible names, errors, dialogs/disclosures, dynamic announcements, contrast, zoom/reflow, touch targets, media, tables/admin-critical workflows, and both modes; remediate defects in shared patterns first; document any owner-approved exception with impact and mitigation.
- **Dependencies:** A2.3 for production-like research review and A7.1–A7.3 for final public content; commerce flows also require A7.2.
- **Affected areas:** templates, CSS, JavaScript, forms, email content, test tooling/CI, accessibility statement.
- **Security considerations:** Automated scanners run only against approved nonproduction data; accessibility changes must not weaken validation, focus security dialogs incorrectly, or expose hidden sensitive content.
- **Testing requirements:** Automated role/state scans, keyboard-only scripts, screen-reader spot checks, 200%/400% zoom, reduced motion, contrast, small-phone reflow, error/success/loading states, and owner acceptance.
- **Acceptance criteria:** No known WCAG 2.2 AA blocker remains in launch journeys; CI covers representative regressions; manual evidence and any explicit exceptions are recorded.

### A8.2 — Implement technical SEO and truthful structured metadata

- **Priority / status:** P1 — Not started.
- **Objective:** Make approved public content discoverable without indexing private, duplicate, test, or mode-inappropriate pages.
- **Why it matters:** Search visibility and trustworthy previews support validation/conversion, while incorrect indexing can expose customer or placeholder content.
- **Current state:** Templates provide basic title/language/viewport but lack full meta descriptions, canonicals, social cards, sitemap, robots policy, structured data, and production 404/500 content.
- **Required work:** Define indexable URL policy per mode; add canonical and robots directives, sitemap and robots.txt, Product/Offer/Breadcrumb/Organization structured data only from authoritative fields, Open Graph/Twitter metadata with approved images, semantic heading/link cleanup, clean pagination/query handling, favicon/manifest as appropriate, and branded accessible 404/500 pages; register webmaster tools after the applicable public hostname and production DNS/TLS are active.
- **Dependencies:** A7.1–A7.3 and activated production hostnames from A2.3/A9.1.
- **Affected areas:** base/product/catalog/core templates, context processors, sitemap/robots/error views, URLs, settings, static media.
- **Security considerations:** Never index account/cart/checkout/order/admin/search-private URLs or expose raw stock/PII; avoid structured claims not supported by current price/availability.
- **Testing requirements:** Crawl both modes, validate status/canonical/robots/sitemap/schema, test query variants and error pages, verify no private URLs, and use search-engine schema tools in staging/public-safe pages.
- **Acceptance criteria:** Each indexable page has one correct canonical and truthful metadata; private/transactional pages are excluded; sitemaps/robots/schema validate for both deployments.

### A8.3 — Establish and meet performance budgets

- **Priority / status:** P1 — Not started.
- **Objective:** Measure and control Core Web Vitals, asset weight, query cost, and cache behavior on representative devices.
- **Why it matters:** The audit found large source images and external fonts but could not collect a DevTools trace; unmeasured visual richness can damage conversion.
- **Current state:** Phase 6 reduced combined source CSS to roughly 64.6 KB and JavaScript to roughly 9.9 KB, retained only referenced modules, established a manual two-mode/two-viewport visual matrix, and kept the five-product/three-variant catalog at 3 queries. Fonts still load from Google; no approved Core Web Vitals budgets, production network/cache measurements, or automated browser-regression trace exists.
- **Required work:** Capture baseline Lighthouse/DevTools traces for key pages/modes; define owner-visible budgets for LCP, CLS, INP, server response, page/asset weight, and key query counts; generate responsive AVIF/WebP with intrinsic sizes; optimize logo/hero/posters; self-host licensed Fredoka/DM Sans subsets; defer YouTube; use hashed immutable static assets and controlled R2 variants; profile queries and add only justified caching/indexes; configure Cloudflare to bypass dynamic/session pages.
- **Dependencies:** A7.1–A7.3, A8.1, and production-like Cloudflare/R2 environments.
- **Affected areas:** static/media build, templates/CSS/JS/fonts, storage/CDN headers, Django queries, CI performance checks.
- **Security considerations:** Do not public-cache personalized HTML or signed URLs; preserve image quality and strip metadata; ensure optimization tooling/dependencies are reviewed.
- **Testing requirements:** Repeatable mobile/desktop traces, throttled network/CPU, cache HIT/MISS/bypass validation, layout-shift inspection, query-count tests, image quality/alt checks, and reduced-motion behavior.
- **Acceptance criteria:** Recorded baseline and budgets exist; launch pages meet approved thresholds in production-like tests; dynamic/private responses demonstrably bypass shared cache; regressions fail or alert in CI.

### A8.4 — Add consent-aware analytics and a learning dashboard

- **Priority / status:** P1 — Not started.
- **Objective:** Measure the validation and commerce funnel with the minimum data needed for decisions.
- **Why it matters:** TreadJoy needs evidence about demand and conversion, but indiscriminate tracking conflicts with privacy and can create noise rather than learning.
- **Current state:** No approved analytics service, event taxonomy, consent behavior, attribution policy, dashboard, or data-quality checks exist.
- **Required work:** Define research and commerce hypotheses, funnel events, properties, success signals, and decision thresholds; select a privacy-appropriate analytics approach; implement consent and Do Not Track/GPC behavior under approved policy; use opaque internal IDs and avoid PII in event properties; validate server/client event deduplication; create a small dashboard for survey/waitlist, catalog-to-checkout, payment failure, reservation expiry, fulfillment, and returns.
- **Dependencies:** A1.4, A2.2, A7.2–A7.3, and legal/owner approval.
- **Affected areas:** templates/JS, optional server event service, consent UI, CSP/Cloudflare, analytics configuration, dashboards/documentation.
- **Security considerations:** No email/address/free-text/token/provider payload in analytics; restrict access/export/retention; honor consent before nonessential scripts; do not let analytics become order truth.
- **Testing requirements:** Consent granted/denied/revoked, script blocking, event schema/deduplication, PII scanner, mode separation, ad-block failure tolerance, and dashboard reconciliation to synthetic orders.
- **Acceptance criteria:** Each event supports a named decision; no prohibited data is sent; consent behavior is demonstrable; analytics failure cannot block commerce; dashboard definitions are documented.

## Phase 9 — Commerce infrastructure and operations

### A9.1 — Provision isolated commerce origin, PostgreSQL, R2, and secrets

- **Priority / status:** P0 — Not started.
- **Objective:** Create production commerce infrastructure isolated from research and aligned with the tested release contract.
- **Why it matters:** Real payments and PII require stronger separation, capacity, secrets, recovery, and origin controls than a development server.
- **Current state:** `tread-joy.com` has been purchased through Cloudflare as the intended base domain, but no commerce hostname allocation, hosting resources, database roles, object storage, secrets store, capacity plan, or infrastructure definition is configured.
- **Required work:** Select an approved commerce hostname, managed Django service, and PostgreSQL region/tier; create runtime/migration/backup roles and pooling limits; configure separate commerce R2/media namespace, secrets, email, Stripe live placeholders, Cloudflare DNS and Full strict TLS, origin lock-down, WAF/rate rules, admin perimeter, and health checks; deploy immutable artifacts from CI; document resource ownership/cost and scaling signals.
- **Dependencies:** A1.1–A1.4, research lessons from A2.3, and commerce settings/storage behavior from prior phases.
- **Affected areas:** Hosting/IaC or deployment config, Cloudflare/R2, PostgreSQL, secrets, CI/CD, Django settings, operations docs.
- **Security considerations:** No shared research database/secrets; least privilege and MFA; prevent origin bypass; restrict production console/database access; public R2 contains public media only; rotate bootstrap credentials.
- **Testing requirements:** Clean staging clone, connection limits/failure, TLS/headers/cache, origin bypass, admin access, secret rotation, R2 upload/render, health/monitoring, and mode/database isolation.
- **Acceptance criteria:** Commerce infrastructure is reproducible, isolated, monitored, cost-documented, and runs the same green commit as research without enabling live order acceptance.

### A9.2 — Make deployment, migrations, backups, restore, and rollback repeatable

- **Priority / status:** P0 — Not started.
- **Objective:** Release schema/code safely and recover the service or data within approved objectives.
- **Why it matters:** A deployment is not production-ready if the team cannot detect failure, restore data, or roll back without improvisation.
- **Current state:** There is no release pipeline, migration preflight, backup/PITR policy, restore drill, release record, rollback mechanism, or approved RTO/RPO.
- **Required work:** Approve RTO/RPO/retention; build staged CI/CD promotion with artifact/commit identity and manual commerce gate; run predeploy checks and deploy-safe migrations before traffic switch; separate irreversible cleanup; back up PostgreSQL and required R2/configuration; automate integrity checks; restore to isolated environment; document rollback for code, schema, secrets, Cloudflare, and provider configuration; maintain a release checklist/change log.
- **Dependencies:** A9.1 and migration discipline from A3–A6.
- **Affected areas:** CI/CD, hosting, PostgreSQL, R2, Cloudflare, migrations, operations/runbooks.
- **Security considerations:** Encrypt and access-control backups; test restores without exposing production data broadly; protect deploy approvals; never log secrets; account for key loss/rotation and compromised release rollback.
- **Testing requirements:** Zero-to-current migration, representative production-size timing, failed migration, app rollback across compatible schema, full database restore/PITR, R2 recovery, secret rotation, and release-cancel rehearsal.
- **Acceptance criteria:** A non-author can follow the runbook to deploy and roll back; restore meets approved RTO/RPO in an isolated drill; each release records artifact, migrations, approver, checks, and outcome.

### A9.3 — Complete production observability, WAF, and operational runbooks

- **Priority / status:** P0 — Not started.
- **Objective:** Detect, triage, and safely respond to technical and commerce failures from edge to database.
- **Why it matters:** Generic uptime does not reveal lost webhooks, stuck reservations, payment mismatches, or delayed orders.
- **Current state:** A1.3 establishes shared foundations; commerce-specific SLOs, dashboards, synthetic checks, WAF tuning, on-call ownership, and business runbooks remain incomplete.
- **Required work:** Define availability and critical-flow SLOs; add synthetic research and commerce checks that stop before real payment; dashboard request/error/latency/database/storage plus checkout/payment/reservation/inventory/email/fulfillment metrics; configure Cloudflare managed WAF and scoped rate rules with tested exceptions for Stripe webhooks; write runbooks for payment mismatch, webhook backlog, oversell, data leak, credential exposure, database/storage outage, email outage, bad deploy, carrier failure, and customer-impact communication.
- **Dependencies:** A1.3, A4.3, A5.4, A6.2–A6.4, and A9.1.
- **Affected areas:** Monitoring/alerts, Cloudflare, Django instrumentation, provider dashboards, operations documentation.
- **Security considerations:** Alert destinations and dashboards contain minimized data; webhook WAF exceptions are narrow; runbooks define evidence preservation and access revocation; synthetic checks use dedicated safe accounts/data.
- **Testing requirements:** Inject representative failures in staging, verify alert routing/dedup/escalation, WAF false-positive/negative tests, webhook delivery through edge, dashboard reconciliation, and tabletop each P0 runbook.
- **Acceptance criteria:** Each P0 failure has a measurable signal, accountable responder, tested runbook, and customer/business mitigation; false alerts and blind spots found in rehearsal are resolved.

## Phase 10 — Pre-launch audit and commerce launch

### A10.1 — Run the complete security, commerce, accessibility, and recovery audit

- **Priority / status:** P0 — Not started.
- **Objective:** Independently challenge every launch-critical invariant in a production-like environment.
- **Why it matters:** Component tests cannot prove the integrated business survives concurrency, retries, hostile input, provider failure, or operator mistakes.
- **Current state:** Required CI runs commerce and research against PostgreSQL and explicitly exercises the existing allocation row-lock races. Production infrastructure, integrated provider workflows, browser/accessibility/performance coverage, backup restoration, rollback rehearsal, and independent review do not yet exist.
- **Required work:** Freeze a release candidate; run all PostgreSQL mode/unit/integration/browser/accessibility/performance suites; perform dependency/secret/configuration review and targeted threat-model penetration tests; rehearse last-unit reservation, payment success/failure/async/expiry/refund/dispute, webhook replay/out-of-order, cart merge/guest access, fulfillment, returns, email failure, backup restore, bad migration/deploy rollback, origin bypass, and research direct-request attacks; commission appropriate external security review before live card acceptance.
- **Dependencies:** All P0 implementation tasks through A9.3 and P1 launch-experience tasks A7–A8.
- **Affected areas:** Entire application, providers, infrastructure, staff workflows, documentation, launch candidate.
- **Security considerations:** Use staging/test Stripe and synthetic PII; authorize testing scope; preserve findings privately; never run destructive/security tests against unrelated systems or public customer data.
- **Testing requirements:** The task is the integrated test program; record command/tool/version/environment, expected result, evidence, owner, severity, remediation, retest, and accepted residual risk for every finding.
- **Acceptance criteria:** No unresolved P0/P1 security, payment, inventory, privacy, accessibility, recovery, or operational finding remains; external/internal reviewers and owner sign the dated release evidence.

### A10.2 — Complete business, legal, content, and operational launch sign-off

- **Priority / status:** P0 — Not started.
- **Objective:** Confirm the business can truthfully deliver every public promise and support every launch workflow.
- **Why it matters:** Technically correct payment processing is unsafe if product, manufacturing, shipping, tax, policies, staffing, or support are not ready.
- **Current state:** Manufacturing/fulfillment details, carriers/rates, tax registration, legal review, production content/assets, support contacts, and incident authority require final evidence.
- **Required work:** Verify sellable quantities/preorder allocation and manufacturer dates; approve prices/margins/shipping/tax; inventory packaging/labels/return process; confirm legal/policy/product-claim review; verify asset rights and accessibility; train staff on order/refund/data/incident runbooks; configure support ownership/hours; verify live Stripe/email/domain/provider accounts and keys without transacting; prepare customer communication and launch/rollback decision checklist.
- **Dependencies:** A10.1 plus owner/specialist approvals named in the decision section.
- **Affected areas:** Business operations, product/admin data, providers, legal/support pages, staff access/runbooks, launch checklist.
- **Security considerations:** Verify live access/MFA/least privilege and secrets rotation; avoid placing legal/tax documents or personal supplier/customer data in public repository; define launch-stop authority.
- **Testing requirements:** Staff tabletop and complete test-order lifecycle, content/policy cross-check, inventory count reconciliation, support response exercise, live-configuration dry run, and owner acceptance of every launch gate.
- **Acceptance criteria:** A dated launch checklist names evidence and accountable approver for product, inventory, payments, shipping, tax, legal, content, accessibility, privacy, support, security, recovery, and rollback; every gate is approved.

### A10.3 — Launch commerce with bounded exposure and hypercare

- **Priority / status:** P0 — Not started.
- **Objective:** Enable real ordering deliberately, monitor first transactions closely, and retain a fast stop/rollback path.
- **Why it matters:** Early real traffic will expose assumptions that staging cannot; a controlled launch limits customer and financial harm.
- **Current state:** Commerce is not production-ready or publicly accepting approved real orders.
- **Required work:** Deploy the signed release from the same tested line as research; verify migrations/health/edge/cache/provider webhooks; enable live Stripe only after final approval; use a bounded initial inventory/preorder allocation and explicit launch window; place a real low-risk owner-authorized purchase/refund only if operationally/legal approved; monitor dashboards, reconciliation, email, fulfillment queue, and support; hold launch review checkpoints and execute stop/rollback criteria immediately if breached.
- **Dependencies:** A10.1 and A10.2 Complete.
- **Affected areas:** Production commerce deployment, Cloudflare, Stripe, database, catalog/inventory, email, monitoring, staff operations.
- **Security considerations:** Never use real customer/card data for engineering tests; verify live/test isolation; restrict launch switches; monitor fraud/abuse and credential access; preserve incident evidence.
- **Testing requirements:** Final smoke before traffic, webhook/provider health, first authorized transaction lifecycle, reservation/inventory/payment reconciliation, receipt/support/fulfillment verification, and rollback readiness check.
- **Acceptance criteria:** Real orders are enabled only within approved bounds; first transactions reconcile end to end; no stop criterion is active; owner records launch acceptance and hypercare handoff.

## Phase 11 — Post-launch monitoring and evidence-led improvement

### A11.1 — Operate a weekly learning and reliability review

- **Priority / status:** P1 — Not started.
- **Objective:** Convert customer, operational, reliability, and financial signals into explicit product and engineering decisions.
- **Why it matters:** The business is validating its thesis; shipping more features without examining outcomes wastes time and hides operational risk.
- **Current state:** No production data or review cadence exists.
- **Required work:** Review research response quality, waitlist conversion, catalog-to-cart-to-Checkout funnel, payment/expiry/mismatch rates, support contacts, fulfillment timeliness, returns/exchanges/reasons, inventory exceptions, accessibility/performance regressions, uptime/errors, fraud/abuse, margin and shipping variance; compare each hypothesis to its threshold; log decisions, owners, follow-up task, and policy/AGENTS.md changes.
- **Dependencies:** A8.4, A9.3, and A10.3.
- **Affected areas:** Analytics/monitoring, operations, product thesis, PROJECT_PLAN.md, AGENTS.md, backlog.
- **Security considerations:** Use aggregated/minimized data; restrict sensitive drill-down; do not infer or store protected/cultural traits; avoid treating analytics as authoritative order data.
- **Testing requirements:** Reconcile sample metrics to PostgreSQL/provider records, validate dashboard definitions, audit access/retention, and periodically test alert/runbook readiness.
- **Acceptance criteria:** A recurring review produces an evidence record and explicit continue/change/stop decisions; reliability/customer harms get owners and deadlines; roadmap statuses reflect actual evidence.

### A11.2 — Add deferred capabilities only after a measured trigger

- **Priority / status:** P2/P3 — Deferred.
- **Objective:** Prevent speculative infrastructure and feature complexity while preserving clear reconsideration paths.
- **Why it matters:** A pre-launch/small-volume business gains more from learning and operational correctness than from enterprise tooling or an oversized feature surface.
- **Current state:** Configurators, standalone component commerce, reviews, advanced promotions/search, Redis, task queues, generalized CMS, and Cloudflare Containers are not required for launch.
- **Required work:** For each proposal, document the observed problem, baseline metric, customer/business value, simpler alternatives, security/privacy/operational cost, success threshold, rollback, and owner decision; run the smallest reversible test; only then create a scoped implementation task with dependencies and acceptance criteria.
- **Dependencies:** A11.1 evidence and explicit owner approval for the specific capability.
- **Affected areas:** Determined per proposal; update architecture and operations documentation before adoption.
- **Security considerations:** New services expand data processors, credentials, attack surface, retention, and incident scope; complete threat/vendor review before data transfer.
- **Testing requirements:** Capability-specific functional/failure/security/performance tests plus proof that the measured trigger improves without regressing launch invariants.
- **Acceptance criteria:** No deferred capability begins from preference alone; every adopted system has a recorded trigger, owner, measurable outcome, operational plan, and removal/rollback path.

## Launch gates at a glance

Research launch requires A0.1–A0.3, A1.1–A1.4, and A2.1–A2.3. A2.2–A2.3 contain its minimum privacy, legal-content, accessibility, metadata, and measured-performance gates; later A7–A8 work completes and re-audits the shared commerce experience.

Commerce launch requires every P0 task through A10.3 plus the P1 customer-facing, accessibility, SEO, performance, email, monitoring, and admin work necessary for the actual release. A P1 label does not permit launch with a broken required customer journey.

The following are unconditional stop-ship conditions:

- Research mode can reach commerce code, credentials, routes, or records.
- A customer can be charged without amount/currency/status/session reconciliation.
- Finished SKU/preorder capacity can oversell under concurrent reservation/payment.
- Order/payment/history records can be silently edited or destructively deleted.
- Guest/account ownership permits cross-customer cart or order access.
- Production secrets, proxy/TLS, email, storage, backup, monitoring, or rollback are incomplete.
- Shipping/tax/legal/product promises are not approved and operationally deliverable.
- Test data, development placeholders, unlicensed/customer-like imagery, fabricated claims, or AI-generated public imagery remain.
- A known P0/P1 security, accessibility, payment, inventory, privacy, recovery, or fulfillment defect is unresolved.
