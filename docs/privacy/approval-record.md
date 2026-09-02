# A1.4 Approval and Decision Record

**Policy:** `TJ-PRIV-001`
**Draft version:** `0.1-draft`
**Evidence date:** 2026-08-30
**A1.4 status:** Open — project-owner acceptance recorded; adviser, technical,
and operational validation outstanding

## Required approvals

No signature or approval is inferred from a code change, pull request, merge,
or instruction to prepare this package.

| Role | Required scope | Status | Reviewer / date | Repository evidence allowed |
|---|---|---|---|---|
| Project owner | Business purposes, access roles, all retention/disposal choices, operating targets, final policy | Accepted for draft review; not yet effective | Project owner — explicit user acceptance, 2026-08-30, `0.1-draft`; no exceptions recorded | Name/role, date, version, accepted exceptions |
| Technical/data steward | Inventory and system-field completeness | Pending | Not recorded | Role, date, commands/checks, known gaps |
| Qualified privacy/legal reviewer | Entity/jurisdictions, notices/consent, request duties, marketing, breach notification, legal holds, public-rights evidence | Pending | Not recorded | Role/firm if approved, scope, date, conclusion; no privileged advice |
| Qualified accounting/tax reviewer | Order/payment/refund/tax evidence triggers and periods | Pending | Not recorded | Role/firm if approved, scope, date, conclusion; no confidential records |
| Incident/operations owner | Severity, response targets, contacts, evidence and communications workflow | Pending | Not recorded | Role, date, version |

## Facts that must be confirmed before approval

- Legal entity name and formation/operating jurisdiction.
- Principal operating location and approved public research reach.
- Contiguous-US commerce reach and any launch geofencing or sales restrictions.
- Tax registrations, filing obligations, chargeback/insurance/warranty needs,
  and the adviser-approved record periods they create.
- Employees, contractors, vendors, and advisers who will access each mode.
- Selected origin, PostgreSQL, Cloudflare/R2, email, monitoring, and later
  commerce providers plus their contractual deletion/backup behavior.
- Approved privacy-request and incident contact channels stored outside Git.

## Owner-accepted draft decisions pending adviser review

The project owner accepted the following draft defaults on 2026-08-30:

- 14-day sessions with daily expired-session purge.
- 24-month waitlist inactivity and anonymous-survey periods.
- 5-year consent/suppression evidence after withdrawal.
- 30-day abandoned carts, 90-day unpaid checkout attempts, and 7-year
  transaction/financial evidence proposals.
- 30/90-day general/security log periods, 5-year incident evidence, and a
  maximum 35-day rolling backup/PITR window.
- Short-lived secure exports and the proposed role/access boundaries.

These values remain non-operative until the required scoped privacy/legal and
accounting/tax reviews are recorded, technical completeness is attested, and a
later policy version receives an effective date.

## Scoped private POC exception

On 2026-08-31, the project owner authorized a private, development-team-only
proof of concept for testing and learning. Legal, accounting, tax, and
commerce/consumer-outreach holds are deferred for this scope only. This
exception does not make `0.1-draft` effective, waive technical privacy or
security controls, authorize consumer traffic, or approve public claims. The
deferred reviews and holds remain required before a public research release or
commerce activity.

## Dependency discrepancies

### A1.2

Production settings are implemented in the repository, but owner acceptance
and live origin/provider validation remain pending. A1.4 may be reviewed, but
final approval must cite the accepted A1.2 configuration version.

### A1.3

`PROJECT_PLAN.md` labels A1.3 complete while its own current-state text says
logging is basic and health, monitoring, correlation, redaction, alerting, and
runbooks are absent. Repository inspection on 2026-08-30 found application
logger calls but no `LOGGING` configuration, health/readiness routes,
correlation middleware, redaction filter, monitoring integration, or A1.3
operations runbooks.

This is a source-of-truth discrepancy. A1.4 does not claim those controls and
does not reimplement them. The project owner reopened A1.3 on 2026-08-31;
implementation and staging-alert evidence are still required before incident
monitoring or redaction acceptance.

## Launch blockers remaining after this draft

- All remaining approvals and attestations in the table above.
- Public privacy/terms/contact content and in-context collection notices.
- Consent versioning, marketing separation, unsubscribe, and suppression.
- Enforced staff-role matrix and removal of broad admin/search exposure.
- Retention/anonymization services and scheduled session cleanup.
- Provider selection, contract review, least-privilege grants, and deletion
  verification.
- Live backup/PITR expiry and isolated restore/tombstone drill.
- A1.3 logging, redaction, monitoring, alert, and incident-channel evidence.
- Tabletop participation and acceptance by the assigned operational roles.

## Downstream handoff by data-class ID

| Roadmap area | Required handoff |
|---|---|
| A2.2 / A3.3 | `REL-WAITLIST-001`, `REL-CONSENT-001`, `REL-SUPPRESSION-001`, `ID-ACCOUNT-001`, `ID-EMAIL-TOKEN-001` |
| A2.3 / A9 | `OPS-EDGE-LOG-001`, `OPS-SESSION-001`, `OPS-BACKUP-001`, `OPS-EXPORT-001`, provider-register activation gates |
| A3.2 / A3.4 | All `COM-*` identity/history classes plus `OPS-STAFF-AUDIT-001`; anonymization and role enforcement |
| A5–A6 | `COM-TAX-001`, `COM-SHIPMENT-001`, `COM-RETURN-001` |
| A7 | `OPS-EMAIL-001`, `REL-CONSENT-001`, `REL-SUPPRESSION-001` |
| A8 | Public policy pages and `OPS-ANALYTICS-001` consent/GPC design |
| A1.3 follow-up | `OPS-APP-LOG-001`, `OPS-INCIDENT-001`, redaction inventory, monitoring/provider alerts |

## Change log

| Version | Date | Status | Change |
|---|---|---|---|
| `0.1-draft` | 2026-08-30 | Owner accepted; adviser/technical/operational review pending | Initial repository-grounded policy package and engineering proposals; owner accepted the draft without recorded exceptions |
| `0.1-draft` | 2026-08-31 | Owner-scoped private POC exception; public approval gates unchanged | Internal development-team-only POC authorized; legal/accounting/consumer holds deferred only for this scope |
