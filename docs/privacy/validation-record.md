# A1.4 Validation and Tabletop Record

**Policy:** `TJ-PRIV-001` `0.1-draft`
**Review date:** 2026-08-30
**Reviewer:** Engineering repository review only; no owner, legal, accounting,
provider, or operational approval is represented

## Evidence boundary and checks performed

The review inspected current models, migrations, settings, views, services,
forms, templates, admin registrations, management commands, tests, and roadmap
dependencies in both deployment modes. Django model metadata was enumerated
without reading real rows. Research-mode waitlist, survey, signup, and login
pages were reproduced locally in the in-app Browser without submitting data.

The review did not inspect `.env`, secrets, customer/development rows, provider
accounts, browser cookies/storage, contracts, tax records, backups, or private
reviewer contact details.

Observed repository facts:

- Database-backed sessions use Django's 1,209,600-second (14-day) default,
  persist arbitrary JSON session data, and have no scheduled `clearsessions`.
- Completed surveys are created without user/session linkage; a migration
  cleared legacy identifiers, but the nullable/blank schema fields remain.
- Waitlist stores normalized email, optional first name, controlled source, and
  created time. It has no consent version, unsubscribe, suppression, or
  last-interaction field.
- Account/allauth stores identity, password hash, email verification state, and
  persisted email-confirmation keys.
- Commerce stores address/contact snapshots, provider identifiers, financial
  and fulfillment facts, staff actors, and free-text operational fields.
- New payment paths persist bounded provider facts and empty payload objects;
  legacy JSON columns and the backup-gated purge command remain.
- Shared templates connect browsers to Google Fonts; optional YouTube embeds
  use `youtube-nocookie.com` only after activation.
- The original A1.4 reproduction found no in-context privacy notice,
  consent/version record, retention statement, unsubscribe control, or footer
  privacy link. A2.2 has since added those application controls, but the notice
  and retention policy remain draft and therefore not effective approval.
- No analytics, customer upload, selected production email, selected managed
  origin/database, live R2, monitoring provider, or backup configuration was
  found.

## Policy-to-schema traceability

### A2.2 implementation delta (2026-08-30)

Research now excludes allauth/sites/public accounts while retaining staff
authentication. `WaitlistSubscription`, append-only `ConsentEvent`, HMAC-keyed
`EmailSuppression`, bounded email/webhook records, broadcast approval, and
aggregate abuse metrics replace the old signup-only record. Existing rows are
quarantined and cannot be contacted. Completed survey rows no longer contain
user/session columns; free text is capped, list/search exposure is removed, and
anonymous CSV export is dedicated-permission, formula-safe, and audited. The
data-register rows below were updated to describe that implementation without
changing their draft policy version or implying adviser approval.

### Shared and research models

| Repository record | Sensitive/current fields | Data-class IDs | Coverage result |
|---|---|---|---|
| `auth.User`, groups, permissions | username, password hash, login/join times, email/name, staff flags and authorization | `ID-ACCOUNT-001` | Covered |
| `account.EmailAddress`, `EmailConfirmation` (commerce only) | email, verified/primary, confirmation key and timestamps | `ID-ACCOUNT-001`, `ID-EMAIL-TOKEN-001` | Covered; absent from research |
| `sessions.Session` | session key, serialized auth/flow data, expiry | `OPS-SESSION-001` | Covered |
| `survey.SurveyResponse` | preference choices, favorite brand, free text, created time; cleared legacy linkage | `RS-SURVEY-001` | Covered |
| Survey session draft | five in-progress answers, including free text | `RS-SURVEY-DRAFT-001`, `OPS-SESSION-001` | Covered |
| Waitlist subscription/consent/suppression/outbox records | nullable email, versioned events, HMAC digest, bounded provider IDs/status | `REL-WAITLIST-001`, `REL-CONSENT-001`, `REL-SUPPRESSION-001`, `OPS-EMAIL-001` | Implemented; policy/provider approval remains blocked |
| `admin.LogEntry` | staff actor, object representation, change message, timestamp | `OPS-STAFF-AUDIT-001` | Covered; broad default behavior needs A3.4 review |
| Product/part `FileField` and future public human media | file/object metadata and public depiction | `RIGHTS-MEDIA-001` | Public product media is non-personal unless people/rights evidence is introduced; private rights store missing |
| Preorder event actor/reason | staff identity and free-text reason | `OPS-STAFF-AUDIT-001`, `COM-ORDER-HISTORY-001` | Covered |

### Commerce models

| Repository record | Sensitive/current fields | Data-class IDs | Coverage result |
|---|---|---|---|
| `cart.Cart`, `CartItem` | user or guest session key, product/quantity, timestamps | `COM-CART-001`, `OPS-SESSION-001` | Covered |
| `CheckoutAttempt` | UUID, user/cart/email, eligibility, totals, idempotency/provider IDs, review reason, timestamps | `COM-CHECKOUT-001` | Covered |
| `CheckoutQuoteLine`, `CheckoutQuoteComponent`, `InventoryReservation` | product/BOM/price/quantity/preorder and attempt link | `COM-CHECKOUT-001` | Covered |
| `ShippingAddress` | full name, email, full postal address, user link | `COM-ORDER-IDENTITY-001` | Covered; user cascade conflicts with future anonymization service |
| `Order` | account/cart/attempt links, duplicated contact/address, money, status, preorder promises, Stripe IDs | `COM-ORDER-IDENTITY-001`, `COM-ORDER-HISTORY-001`, `COM-PAYMENT-001` | Covered |
| `OrderItem`, component snapshot | purchased product/SKU/BOM, money, size/color, quantity, promises | `COM-ORDER-HISTORY-001` | Covered |
| `Shipment` | carrier, tracking, delivery, free-text notes | `COM-SHIPMENT-001` | Covered |
| `InventoryAllocation`, items | order, reviewer, quantity and exception/recovery timestamps | `COM-ORDER-HISTORY-001`, `OPS-STAFF-AUDIT-001` | Covered |
| `Payment`, `Refund` | Stripe IDs, money/status/reason/failure, legacy JSON | `COM-PAYMENT-001`, `COM-STRIPE-LEGACY-001` | Covered |
| `StripeEvent` | provider ID/type/time/version/money/error/attempts plus legacy JSON | `COM-PAYMENT-001`, `COM-STRIPE-LEGACY-001` | Covered |
| `OrderStatusEvent` | order, staff actor, state, source/reason/provider reference, internal and customer free text | `COM-ORDER-HISTORY-001`, `OPS-STAFF-AUDIT-001` | Covered |
| Future tax and return records | not implemented | `COM-TAX-001`, `COM-RETURN-001` | Planned-not-active, with activation gates |

### Session keys, logs, and external connections

| Source | Current values | Data-class IDs | Result |
|---|---|---|---|
| Survey views | `survey_draft` | `RS-SURVEY-DRAFT-001`, `OPS-SESSION-001` | Covered |
| Checkout/order views | `checkout_attempt_ids`, `checkout_order_ids` | `OPS-SESSION-001`, `COM-CHECKOUT-001` | Covered |
| Account adapter | `treadjoy_guest_cart_session_key` | `OPS-SESSION-001`, `COM-CART-001` | Covered |
| Application logger calls | order ID, attempt UUID, Stripe event ID, bounded reason/exception text | `OPS-APP-LOG-001`; incident promotion to `OPS-INCIDENT-001` | Covered; redaction and retention not implemented |
| Browser connections | Google Fonts; optional YouTube no-cookie | Processor register, `OPS-EDGE-LOG-001` as provider telemetry category | Covered; approval/remediation pending |
| Planned Cloudflare/R2/origin/PostgreSQL/SMTP/monitoring | not provisioned | Processor register plus relevant `OPS-*` rows | Covered as planned-not-active |

No current sensitive model or known session key was found without a register
mapping. This is an engineering traceability result, not adviser approval of
purpose or retention.

## Admin and access-control review

| Surface | Current exposure | Risk / required follow-up |
|---|---|---|
| Waitlist admin | Bounded status/source/timestamp/provider-reference views; raw email/token/digest fields excluded | Relationship manager group is least-privilege; assignment and staging access review remain release gates |
| Survey admin | Read-only structured filters; no free-text list/search; dedicated audited anonymous CSV action | Research analyst group is least-privilege; assignment and staging access review remain release gates |
| Cart admin | Guest session key in list and search; inline items | Session ownership identifier is restricted; remove from ordinary display/search and enforce support scope |
| Order/address admin | Contact/address searchable; many commerce records read-only | Read-only is helpful but not sufficient; role boundaries, list minimization, MFA/access perimeter, export controls, and direct-POST tests remain A3.4 |
| Payment/refund/Stripe admin | Full provider identifiers searchable/displayed; deletion mostly disabled | Restrict to finance/security roles and consider masked display/approved lookup |
| Order/preorder history | Staff actor and internal/customer free text | Append-only behavior exists in places; enforce bounded reason codes and protect internal detail |
| Django auth/admin | Default model permissions and broad superuser capability | Define approved groups, break-glass, quarterly access review, and staff offboarding before launch |

Result: the policy identifies least-privilege roles, but current enforcement does
not pass the A1.4/A3.4 access acceptance gate.

## Redaction and free-text test inventory

A1.3 implementation must add automated cases proving these values never appear
in ordinary logs, alerts, health responses, CI output, or configuration errors:

- `SECRET_KEY` and fallbacks, database password, Stripe keys/webhook secret,
  R2 key/secret, SMTP password, provider/OAuth/API credentials;
- password hashes, confirmation/reset/guest-access tokens, CSRF token, session
  cookie/key, `treadjoy_guest_cart_session_key`, and checkout/order ID lists;
- full email, name, address lines, city/state/postal combination, tracking URL,
  and uploaded/exported content;
- complete request or webhook bodies and `raw_response`/`raw_event` JSON;
- unbounded provider exceptions or response objects.

Restricted structured logs may use an approved internal request/order/attempt
correlation identifier. Full Stripe event/session/payment/refund identifiers
must be either excluded, hashed/masked, or explicitly approved for the
restricted finance/security log store.

Treat these current free-text sources as possible PII/secrets and test
allowlisting/redaction at their output boundaries:

- survey `additional_feedback` and `favorite_brand`;
- shipment `notes`;
- order-event `note`, `internal_detail`, and `customer_message`;
- preorder event `reason`;
- refund `reason` and `failure_reason`;
- Stripe payload/signature exception text;
- Django admin change messages and object representations.

Health/liveness/readiness responses must reveal no version, exception, host,
database name, bucket, provider ID, or configuration value.

## Engineering tabletop outcomes

These are document walkthroughs against current code and the draft policy. They
do not represent completed operational exercises or owner/adviser acceptance.

| Scenario | Expected policy outcome | Current implementation result | Status / owner |
|---|---|---|---|
| Waitlist unsubscribe and deletion | Verify stored email; remove active waitlist identity; create minimal suppression; age backups | Waitlist can be manually deleted, but no consent, unsubscribe, suppression, request ledger, tombstone, or provider exists | Blocked — A2.2/A7, marketing and privacy-request owners |
| Anonymous survey request | Explain reliable identity lookup is impossible; do not search free text or guess a row; clear verified live draft if present | Completed response has no linkage as intended; no request workflow or retention cleanup exists | Policy path passes; operations pending — A2.2 research owner |
| Account deletion without orders | Reauthenticate; disable; expire sessions/tokens; apply grace; delete/anonymize; retain allowed audit/suppression | Default account deletion and cascades are not an approved anonymization workflow; sessions are not scheduled for purge | Blocked — A3.2/A3.3 |
| Guest paid-order deletion | Strongly verify; preserve commercial facts; anonymize direct identity only through approved service | Immutable snapshots exist, but ShippingAddress/account relationships and retention service are not policy-safe | Blocked — A3.2/A3.3 |
| Refunded/disputed order under hold | Open scoped counsel-approved hold; suspend relevant disposal; preserve audit; continue restrictions | Refund/order history exists; no hold model/process or approved periods | Blocked — A3.2/A6.3 and counsel |
| Expired session and abandoned checkout | Daily session purge; 30-day cart and 90-day unpaid-attempt rules after approval; count-only audit | Django expiry exists, reservation cleanup exists, but no session/cart/attempt retention scheduler | Blocked — A2.3/A4/A9 |
| Legacy Stripe payload disposal | Validate bounded backfill and restorable backup; dry-run; separately approve gated purge | Idempotent gated command/tests exist; no live backup or production-data validation exists | Correctly blocked — A3.2/A9 finance and technical owners |
| Restore after prior deletion | Isolate restore; reapply tombstones/later state; verify; approve return to service | No live backup provider, tombstone ledger, restore automation, or drill | Blocked — A2.3/A9 |
| Session/address/provider-ID incident | Declare severity; contain; preserve redacted evidence; scope by data-class ID; counsel notification decision | Policy annex now exists; contacts, monitoring, redaction, evidence store, and exercised response do not | Blocked — A1.3/A2.3/A9 |

## Backup-retention design review

The draft defines backups as rolling recovery copies with a proposed maximum
35-day window, separate modes, restricted access, no indefinite snapshots, and
tombstone replay before restored service. This satisfies a policy-design
tabletop only.

It does not satisfy operational acceptance because no provider, schedule,
encryption/access evidence, retention/expiry proof, tombstone implementation,
isolated restore, reconciliation, or rollback drill exists. A2.3 must prove the
research deployment; A9 must repeat the proof for commerce.

## Acceptance summary

| A1.4 criterion | Engineering result |
|---|---|
| Sensitive data classes inventoried | Pass for current repository; future rows explicitly marked planned |
| Purpose, authority, access, retention, disposition, backup, owner fields present | Pass as draft proposals; not approved |
| Mode separation documented | Pass as policy/data-flow design; live infrastructure not proven |
| Privacy-request tabletop | Procedures and engineering outcomes recorded; operational exercise pending |
| Incident tabletop | Procedures and engineering outcomes recorded; A1.3 controls and operational exercise pending |
| Access-control review | Completed; enforcement gaps block acceptance |
| Backup-retention check | Design reviewed; live proof blocked |
| Redaction inventory | Completed; automated controls/tests absent |
| Owner/legal/accounting approval | Project-owner acceptance recorded 2026-08-30; privacy/legal, accounting/tax, technical, and operational approvals pending |

Conclusion: the repository now contains a comprehensive reviewable A1.4 draft,
but A1.4 must remain open.
