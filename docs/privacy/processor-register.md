# Processor and External-Service Register

**Policy:** `TJ-PRIV-001` `0.1-draft`
**Status:** Inventory and activation gates; no listed candidate is approved merely
by appearing here

TreadJoy is the proposed business/controller for its customer and research
data. This register covers external services that receive data or direct
browser connections. Framework packages running inside TreadJoy's origin are
dependencies, not independent processors, but their storage effects are listed
in the data register.

## Current repository connections

| Service | Status | Modes | Data / purpose | Current evidence | Required decision or remediation |
|---|---|---|---|---|---|
| Stripe | Commerce code present; live service not validated | Commerce only | Email, line/amount/currency facts, hosted shipping collection, provider/payment identifiers, refunds, verified webhooks | Commerce settings require keys; research rejects every `STRIPE_*` value; hosted Checkout/reconciliation code exists | Review Stripe agreement/DPA, account roles/MFA, retention/export/deletion, subprocessors, incident notices, live/test separation, and restricted keys before commerce activation |
| Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`) | Current direct browser connection | Both | Browser network metadata to retrieve DM Sans and Fredoka CSS/font files | Shared base template preconnects and loads stylesheet from Google | Before research launch, either approve/disclose this connection or lawfully self-host reviewed font files and remove the external CSP/preconnect paths |
| YouTube privacy-enhanced embed | Optional; inactive without configured approved video | Both | Browser network metadata and playback activity after a deliberate activation | Server emits only `youtube-nocookie.com`; current local page renders a placeholder | Keep user-initiated; approve video, notice, consent/cookie behavior, retention, and Google/YouTube terms before activation |

## Required launch infrastructure not yet selected or validated

| Service class | Intended modes | Proposed data / purpose | Mandatory pre-activation evidence |
|---|---|---|---|
| Cloudflare edge | Separate configuration for both | IP/user agent/request metadata, WAF events, DNS/TLS/proxy delivery | Account owner/MFA and roles; DPA/terms/subprocessors/region; log fields and 30/90-day retention; access and deletion; incident route; origin lock-down; no cache of private responses |
| Cloudflare R2 | Separate namespace/credentials per mode | Approved public media only | Public custom domain; no `r2.dev`; bucket/credential separation; object deletion/versioning behavior; access log policy; confirmation that private rights evidence, exports, and uploads are excluded |
| Managed Django origin | Separate deployment configuration | Request processing, application logs, runtime secrets, temporary files | Vendor/region; DPA; staff/support access; log retention; secret store; image/runtime lifecycle; incident notice; export/exit deletion; origin access controls |
| Managed PostgreSQL | Separate databases and roles | Authoritative research or commerce records, PITR/backups | Region/DPA; runtime/migration/backup roles; encryption; maximum 35-day backup/PITR; restore isolation; deletion/tombstone behavior; support access; incident notice; exit export/deletion |
| SMTP/email delivery | Mode-scoped credentials and streams | Recipients, provider message IDs, delivery/bounce/complaint/suppression events | Sender verification; DPA/terms/subprocessors/region; content/log retention; suppression/export/deletion; webhook authentication; support access; incident notice; SPF/DKIM/DMARC |
| Error monitoring/alerting | Both, separate environments | Redacted errors, correlation IDs, bounded entity/provider identifiers | Selected fields and scrub rules; no sessions/tokens/address/email/raw payload; 30/90-day retention; roles/MFA; alert contacts; test event; deletion/export; DPA/subprocessors/incident notice |

## Deferred services

| Service class | Status | Gate before any data transfer |
|---|---|---|
| Analytics | Not approved or implemented | A8.2 event taxonomy, consent/GPC behavior, no-PII property allowlist, separate mode properties, 13-month-or-shorter raw retention, DPA/roles/deletion, owner/legal approval |
| Tax calculation/reporting | Not selected | Adviser-approved registrations and tax policy, exact fields, tax codes, DPA/roles, retention, reconciliation, provider failure behavior |
| Carriers/rate providers | Not selected | Owner shipping decisions, address minimization, API authentication, retention/deletion, tracking disclosure, incident route |
| Returns evidence storage | Not selected | Approved evidence types/size/metadata handling, private storage and signed access, malware/content validation, retention/deletion, provider review |
| Support/ticketing | Not selected | Need demonstrated; purpose/field allowlist, no payment-card data, access roles, retention, export/deletion, DPA/subprocessors |
| Forensics/incident provider | Not selected | Incident-specific owner/legal approval, confidentiality, evidence scope, secure transfer, chain of custody, deletion/return |

## Systems prohibited from production-data use

- Git repositories and issue bodies.
- GitHub Actions logs, artifacts, and CI databases.
- Developer screenshots, recordings, local fixtures, or browser history.
- Public R2/media paths, static assets, or CDN caches.
- General chat, personal email, consumer file sharing, and unapproved AI tools.

## Activation checklist

For every provider, the accountable owner records outside sensitive contract
material:

1. Business purpose and stable data-class IDs.
2. Exact fields, modes, subjects, transfer direction, and source/recipient.
3. Account owner, MFA, least-privilege roles, API key scope, and break-glass path.
4. Contract/DPA status, region, subprocessors, government-request handling, and
   incident-notification terms, reviewed by qualified counsel where required.
5. Active retention, backups, deletion request process, support-access logs,
   export/portability, and contract termination deletion.
6. Security headers/CSP, DNS/webhooks, credential rotation, logging/redaction,
   health/failure behavior, and a staging test using synthetic data.
7. Removal plan, owner, cost, review date, and evidence location.

Failure or uncertainty in any required item keeps the provider inactive.
