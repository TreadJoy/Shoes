# UX Contract

## Product context

- Audience: public research participants, future commerce customers, and narrowly permissioned staff.
- Primary jobs: explore products, submit anonymous research, confirm or withdraw email consent, and administer/export only authorized records.
- Target market: contiguous-US launch; initial research hypothesis in `AGENTS.md`.
- Active locale: English (`en-us`).
- Timezone/calendar policy: operational subscription limits and audit timestamps use UTC.
- Accessibility target: WCAG 2.2 AA.

## Business-context sources

| Domain / scope | Authoritative source | Source type | Reviewed date |
|---|---|---|---|
| Permission model | `AGENTS.md`; A2.2 in `PROJECT_PLAN.md` | Product/permission policy | 2026-08-30 |
| Data lifecycle | `docs/privacy/data-register.csv` | Data register | 2026-08-30 |
| Deletion / retention | `docs/privacy/operating-policy.md`; A2.2 | Draft privacy policy / approved implementation step | 2026-08-30 |
| Commerce boundary | `docs/research-capability-boundary.md` | Capability contract | 2026-08-30 |
| Legal copy | `docs/privacy/approval-record.md` | Approval record | 2026-08-30 |
| Market / content conventions | `AGENTS.md`; `docs/homepage-implementation-decisions.md` | Product/brand contract | 2026-08-30 |

## Visual contract

- Project `DESIGN.md`: `DESIGN.md`.
- Token ownership: existing runtime canonical.
- Runtime source: `static/css/style.css`; homepage composition in `static/css/home.css`.
- Token drift gate: design lint, strict project audit, tests, and narrow/desktop browser inspection.
- Supported themes: light; system forced-colors behavior preserved.

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Form | Django Forms + shared CSS | server validation | research / commerce | tests + browser |
| Select/Listbox | native select | Django choices | native only | keyboard + browser |
| Toast | Django messages + inline status | server response | info/success/error | rendered tests |
| CRUD | Django admin + management commands | model permissions/effective policy version | read-only export; dry-run/apply retention | permission + command tests |

## Component behavior

| Component | Default | Hover | Focus | Active | Disabled | Busy | Error |
|---|---|---|---|---|---|---|---|
| Button | semantic intent | token contrast | 3px focus ring | 1px shift | muted/noninteractive | stable label/indicator | persistent inline/page status |
| Input | labeled/bordered | unchanged | focus border/ring | n/a | muted | duplicate submit blocked server-side | inline + summary |
| Textarea | six rows, no resize | unchanged | focus border/ring | n/a | muted | n/a | inline + 1,000-character guidance |
| Admin table | Django admin | Django admin | Django admin | n/a | action hidden by permission | server response | admin message |

## Dataset navigation

- Admin tables: Django admin pagination/filtering; no public counts.
- Survey export selection means selected rows only and records exact exported row count/checksum.
- Empty/error/loading treatment: standard admin ownership; public forms use persistent inline recovery.
- No waitlist export exists.

## Flow ledger

| Operation | Trigger | Pending | Success destination | Success feedback | Failure recovery | Focus outcome | Source ref |
|---|---|---|---|---|---|---|---|
| Waitlist request | POST dedicated source route | queued outbox | source page | neutral eligibility message | inline validation or 429 | first invalid field; status on success | A2.2 |
| Confirm | CSRF POST from read-only GET page | transaction | result page | confirmed/active | expired/invalid with new-request path | result heading | A2.2 |
| Unsubscribe | CSRF POST from read-only GET page | transaction | result page | inactive confirmation | invalid link message | result heading | A2.2 |
| Survey complete | final step POST | transaction | thank-you | anonymous completion | inline error or 429 | first invalid field or thank-you heading | A2.2 |
| Survey export | permissioned admin action | server generation | CSV download | audit row | admin error/no file | changelist | A2.2 |
| Broadcast | permissioned admin action | provider call after local queue | changelist | aggregate status | durable failed ledger | admin message | A2.2 |
| Retention | CLI `--apply` + matching version | bounded transactions | CLI | counts only | abort/nonzero | terminal | A2.2 / privacy policy |

## Navigation and responsive behavior

- Every public route sets a descriptive document title.
- Research `/accounts/*`, cart, and order paths are capability-boundary 404s; forbidden staff actions use Django admin 403 behavior.
- Research mobile/desktop navigation omits customer identity and commerce controls.
- Forms remain single-column and document-scrolling at narrow widths.

## Overlays and feedback

- No custom dialogs are introduced in A2.2.
- Inline validation is persistent; throttling uses an accessible 429 page and `Retry-After`.
- Consent/provider failures never expose address existence, secrets, tokens, or raw provider detail.

## Async and resilience

- Mutations are pessimistic and transactional.
- Confirmation and webhook handling are idempotent; email delivery uses a durable retryable outbox.
- Provider delivery never rolls back consent-request persistence.
- Provider event ordering cannot weaken terminal bounce/complaint/suppression states.

## Validation

- Django Forms/models/services own validation and state transitions.
- Validate on submit, then render inline errors with `novalidate`.
- Preserve non-sensitive form values; never echo secret settings, token digests, raw webhook bodies, or email existence.

## Permission and clipboard

- Irrelevant public identity/commerce features are absent in research; direct forbidden paths return 404 by capability policy.
- Staff direct access uses Django admin authorization and 403 behavior.
- Research analysts receive only survey view/export; relationship managers receive bounded waitlist view/broadcast approval permissions.
- No clipboard feature is introduced.

## Verification

- Static: Django checks, migration drift, strict premium UI audit, dependency/license audit.
- Browser: 390px and desktop waitlist, confirmation, unsubscribe, survey, privacy, validation, success, and 429 states; keyboard and reduced-motion checks.
- Database: fresh PostgreSQL research migrations/boundary/engagement suite and full commerce PostgreSQL suite.
- Legal/staging: adviser-effective notice and retention versions plus Resend/Cloudflare evidence remain release gates.
