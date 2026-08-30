# TreadJoy Privacy, Retention, and Security Operating Policy

**Policy ID:** `TJ-PRIV-001`
**Version:** `0.1-draft`
**Status:** Owner-accepted draft; adviser and technical review pending; not in force
**Applies to:** TreadJoy research and commerce deployments, their operators,
and approved service providers

## 1. Purpose and boundary

This policy defines how TreadJoy proposes to govern personal, security,
commercial, and operational data. It covers collection purpose, minimization,
mode separation, access, provider review, retention, deletion or anonymization,
legal holds, backups, privacy requests, incidents, and review.

This step does not implement deletion jobs, schema changes, public legal pages,
analytics, new collection, provider configuration, or customer promises. Those
changes require their roadmap task, tests, and any additional owner approval.

## 2. Governance and approval authority

The following are accountable roles, not permission groups currently proven in
the application:

| Role | Proposed responsibility | Approval authority |
|---|---|---|
| Project owner | Business purpose, acceptable risk, retention tradeoffs, final policy | Final owner approval |
| Technical/data steward | Register accuracy, system mapping, implementation tickets, evidence | Technical attestation |
| Privacy-request owner | Intake, verification, deadlines, provider coordination, closure | Operational decision within approved policy |
| Incident commander | Containment, evidence, coordination, recovery, decision log | Operational incident authority |
| Qualified privacy/legal reviewer | Applicable jurisdictions, notices, request rights, breach duties, preservation | Scoped legal review |
| Qualified accounting/tax reviewer | Tax, transaction, refund, and financial evidence periods | Scoped accounting/tax review |
| Communications authority | Approved customer, public, partner, and regulator messages | Message release approval |

The repository records role, scope, date, conclusion, and policy version. It
must not contain privileged advice, provider contracts, credentials, private
contact coordinates, or unnecessary personal details about reviewers.

Before approval, the project owner and advisers must confirm the legal entity,
operating location, public reach, contiguous-US commerce boundary, registration
and tax footprint, insurance requirements, and employee/contractor access. The
public nature of the research site must not be confused with an approved
worldwide business or legal scope.

## 3. Processing-justification categories

Each register row must use one or more of these proposed categories. Counsel
must validate the applicable legal characterization; these labels do not claim
a statutory legal basis.

- **Requested service:** provide a survey, waitlist, account, support, or other
  feature the individual deliberately requested.
- **Transaction and fulfillment:** price, reserve, reconcile, fulfill, support,
  cancel, return, exchange, or refund a purchase.
- **Consent or preference:** act on an affirmative marketing or optional-media
  choice and retain evidence of withdrawal or suppression.
- **Security and integrity:** authenticate, prevent abuse, investigate failures,
  reconcile money/inventory, preserve audit history, and respond to incidents.
- **Recordkeeping obligation:** retain evidence required for tax, accounting,
  disputes, legal holds, insurance, or another adviser-confirmed obligation.
- **Public-rights evidence:** prove permission, licensing, and factual support
  for identifiable people or activities depicted publicly.

## 4. Collection and minimization

1. Collect a field only for a recorded, approved purpose and owner.
2. Do not add demographic, inferred-interest, community-affiliation, precise
   location, behavioral-profile, or special-category fields for speculative
   analysis.
3. Do not store raw payment-card data. Stripe-hosted Checkout remains the card
   boundary.
4. Keep unstructured text out of logs and structured records where a bounded
   code will work. Free-text survey, shipment, return, support, admin, and
   incident fields must be treated as capable of containing personal data.
5. Do not copy complete provider payloads when bounded identifiers, status,
   amount, currency, timestamps, and error codes are sufficient.
6. Do not place customer data, provider payloads, exports, production backups,
   or private media in Git, CI artifacts, static files, or public R2 media.
7. Public imagery containing identifiable people requires approved rights and
   consent evidence. Public media must not be used as private document storage.

## 5. Deployment-mode separation

- Research and commerce use separate PostgreSQL databases, secrets, sessions,
  R2 namespaces, provider configuration, backups, exports, and staff grants.
- Research must not initialize Stripe, accept an order, create commerce data,
  or receive commerce credentials.
- Commerce records must not be copied into research for testing, support,
  analytics, demonstrations, or content creation.
- Cross-mode reporting is limited to approved, anonymous aggregates with no
  email, address, session key, internal user ID, provider ID, free text, or
  small cohort that could reasonably re-identify a person.

## 6. Sensitivity and access

Register sensitivity values have these meanings:

- **Restricted:** credentials, password hashes, authentication/session tokens,
  full addresses, provider payloads, incident evidence, exports, and private
  support or fraud information. Need-to-know access only.
- **Confidential:** email, name, account identifiers, order/payment/provider
  identifiers, tracking information, survey free text, consent records, staff
  audit identity, and pseudonymous telemetry.
- **Internal:** non-personal operational facts that could still reveal business
  or security state.
- **Public-approved:** reviewed catalog/content/media explicitly approved for
  public delivery. Public reach is irreversible enough that rights evidence
  must outlive the publication period.

Access must be granted by role and environment, reviewed at least quarterly,
and removed promptly on role change. Provider consoles, database access,
backups, exports, deployment secrets, and break-glass access are separate
grants. Django staff status alone must not be treated as authorization for all
personal or financial data. A3.4 owns enforcement of the approved role matrix.

Break-glass access requires a documented incident or recovery reason, the
least time and scope possible, a second-person review when practical, and an
after-action access review. Secrets and sensitive values never belong in the
access record.

## 7. Retention and lifecycle

`data-register.csv` is authoritative. Each row has an event-based trigger, a
bounded active period, backup treatment, and one final action:

- `delete`: remove the record and derived copies under TreadJoy's control.
- `anonymize`: irreversibly remove identity and linkage while preserving only
  approved non-identifying facts.
- `retain-restricted`: preserve an approved record with narrower access.
- `retain-under-hold`: suspend ordinary disposal for the documented hold scope.

The draft lifecycle categories are ephemeral, short-lived operational,
relationship/consent, commercial/legal, security/audit, backup/archive, and
public-rights evidence. “Indefinite,” “until no longer needed,” and silent
provider defaults are prohibited unless a reviewer documents a specific legal
need and owner acceptance.

Retention automation must be idempotent, previewable, auditable by counts and
stable IDs, safe under concurrency, and tested at the boundary. Cleanup output
must not list the deleted personal values. Destructive cleanup requires a
restorable backup where the policy calls for one, but creating a fresh backup
must not become a way to extend expired data indefinitely.

Expired database sessions require scheduled `clearsessions`; cookie expiry
alone does not purge the database row. The schedule is an A2.3/A9 deployment
responsibility and is not currently implemented.

## 8. Anonymization and commercial history

- Deleting an account must not cascade-delete paid, refunded, tax, fulfillment,
  return, dispute, inventory, or staff-action history.
- Direct identifiers may be blanked, tokenized, or detached only through an
  approved service that preserves referential and financial consistency.
- Provider identifiers needed for reconciliation remain restricted commercial
  evidence for their approved period; they must not be exposed in ordinary
  list pages or exports.
- Anonymous survey responses are treated as confidential while free text may
  contain identifying material. TreadJoy must not promise that a response can
  be located for a person when no identifier was retained.
- Marketing suppression keeps only the minimum approved evidence needed to
  avoid re-contact. Suppression must not be erased merely because the person
  asked to stop marketing.

## 9. Backups, restore, and deletion tombstones

Backups are recovery copies, not archives. The proposed baseline is a maximum
35-day rolling encrypted database-backup/PITR window, subject to the selected
provider's proven capabilities and owner approval. There must be no indefinite
manual snapshots containing personal data.

Ordinary requests do not rewrite immutable backup media. A minimal deletion or
anonymization tombstone must identify the internal operation—not the deleted
personal values—and remain long enough to cover the backup window. After any
restore, operators must isolate the restored environment, reapply all tombstones
and later state changes, validate the result, and only then return it to service.

Backup access is restricted to recovery roles. Restore drills, retention/expiry
evidence, and provider behavior are A2.3/A9 launch gates. Until those pass, this
policy does not claim that backup deletion or recovery works.

## 10. Legal holds

Only the project owner acting with qualified counsel, or a documented delegated
role, may open or close a legal hold. The hold record contains scope, affected
data-class IDs, systems, start date, owner, review date, and release decision;
it does not reproduce evidence content.

A hold suspends disposal only for the narrow affected records. It does not
authorize unrelated collection, broaden staff access, or permit alteration of
append-only history. Normal retention resumes from the approved trigger when
the hold is released, unless counsel records another bounded rule.

## 11. Provider onboarding and removal

No provider may receive TreadJoy personal data before its processor-register
row has an owner and the required security/privacy review. Review must cover
purpose, fields, environments, credentials, least privilege, location,
retention/deletion, backups, incident notice, contract/DPA, subprocessors,
support access, portability, and exit deletion.

Provider removal requires disabling collection, exporting only approved
records, revoking credentials, requesting deletion, recording confirmation,
removing CSP/DNS/webhook/configuration paths, and validating that retries or
queued jobs cannot resume transfer.

Google Fonts is a current browser-side connection and must either be approved
and disclosed or replaced with lawfully self-hosted files before research
launch. YouTube remains optional and user-initiated. Monitoring, analytics,
email, tax, carriers, and hosting choices remain unapproved until selected.

## 12. Requests, incidents, and communications

Operators follow `privacy-request-runbook.md` and
`security-incident-annex.md`. Operational severity does not decide whether a
legal notification is required. Counsel makes that determination from the
facts and applicable jurisdictions. Only the communications authority may
release customer, regulator, partner, or public statements.

No message may promise deletion from immutable backups immediately, claim a
legal right that has not been reviewed, describe TreadJoy as compliant based
only on engineering work, or disclose facts that increase harm or compromise
the investigation.

## 13. Review and change control

Review occurs at least annually and before any new data class, provider,
jurisdiction, public notice, analytics or profiling capability, business model,
material schema change, or material incident. Each change increments the policy
version, updates affected register rows and downstream tests, and records the
approver and effective date.

A material change to collection, purpose, disclosure, retention, or individual
choice requires renewed owner and scoped adviser review before deployment.
