# Security-Incident and Privacy-Breach Annex

**Policy:** `TJ-PRIV-001` `0.1-draft`
**Status:** Proposed; responders, contact routes, targets, insurer/provider
terms, and legal notification rules require approval and secure off-repository
configuration

## Principles

- Protect people and stop ongoing loss first while preserving evidence.
- Operational severity prioritizes response; it does not decide whether an
  event is legally reportable.
- Counsel determines notification duties from the entity, jurisdictions,
  affected data/people, facts, and applicable law.
- Do not destroy evidence, wipe systems, rotate away the only evidence, or
  communicate speculative facts without incident-command direction.
- Do not place secrets, raw payloads, full addresses, session keys, exports, or
  private evidence in ordinary logs, tickets, Git, or general chat.
- Research and commerce containment remains separated unless the facts prove a
  shared control is affected.

## Proposed severity and activation targets

| Severity | Criteria | Proposed activation target | Authority |
|---|---|---|---|
| `SEV-1` | Active or material compromise; leaked production secret; unauthorized privileged access; payment/auth/session compromise; significant or ongoing personal-data exposure; loss of authoritative commerce integrity | Immediately; incident commander target within 30 minutes | Incident commander; notify owner, technical responder, and privacy/legal contact immediately |
| `SEV-2` | Confirmed limited personal-data exposure; contained privileged-access failure; provider incident affecting TreadJoy data; material control failure without evidence of ongoing access | Within 4 hours | Incident commander and affected domain owner; privacy/legal review same day |
| `SEV-3` | Suspected or contained event with no confirmed disclosure; isolated policy breach; unsuccessful abuse with evidence needed; recoverable integrity/availability issue | Within 1 business day | Security/incident owner and affected domain owner |
| `SEV-4` | Near miss, low-risk control weakness, or process deviation with no exposure/integrity impact | Within 5 business days | Technical/data steward; escalate if facts change |

Any responder may raise severity. Only the incident commander with documented
reason may lower it. New evidence restarts the assessment.

## Secure contact register

Keep names, phone numbers, private emails, account IDs, policy numbers, and
provider emergency routes in the approved secrets/operations system—not this
repository. The register must name roles for:

- incident commander and backup;
- technical/forensic responder;
- project owner/business decision maker;
- privacy/legal reviewer and backup;
- communications authority;
- finance/Stripe, fulfillment, research, email, Cloudflare, origin/database,
  monitoring, insurer, and law-enforcement liaison as applicable.

Test the route at least quarterly without sending customer data.

## Incident ledger

Create a restricted `OPS-INCIDENT-001` record containing:

- opaque incident ID, detected time/source, severity history, and commander;
- affected modes, systems, providers, data-class IDs, and estimated counts;
- confirmed facts, hypotheses explicitly labeled, and decision timestamps;
- containment, evidence, access, credential, recovery, and validation actions;
- provider case IDs and evidence references, not copied secret/payload values;
- legal/notification decision owner, jurisdictions reviewed, conclusion, and
  message approvals without privileged reasoning;
- affected-person support and communications status;
- root cause, corrective owners/dates, closure, and review date.

Maintain a separate evidence manifest with hashes, sources, collection actor,
time, access history, and secure location. Do not repeatedly copy evidence.

## Response workflow

### 1. Detect, declare, and protect the channel

1. Record the initial report and assign an incident ID.
2. Choose severity from known facts and activate the contact route.
3. Move coordination to the approved restricted channel.
4. Warn responders not to paste secrets/payloads or notify outside parties.
5. Begin a timestamped decision and evidence log.

### 2. Contain without destroying evidence

- Revoke or narrow affected access; isolate compromised services, accounts,
  routes, buckets, deployments, or database roles.
- Preserve logs and snapshots approved by the incident commander before any
  destructive remediation. Do not create an unbounded permanent backup.
- Stop exposed public downloads and purge unsafe caches while retaining the
  minimum evidence needed to prove what occurred.
- Disable optional integrations/analytics and commerce checkout when safe
  operation or reconciliation cannot be proven.
- For payment/inventory integrity risk, stop order-taking before attempting
  silent repair; preserve provider and PostgreSQL facts for reconciliation.

### 3. Credential exposure procedure

1. Identify credential class, environment, privileges, last rotation, and all
   consumers without printing the value.
2. Create a replacement through the provider's approved secret interface.
3. Deploy the replacement, verify a synthetic or safe staging operation, and
   monitor authentication failures.
4. Revoke the old credential as soon as overlap is no longer needed.
5. Invalidate derived sessions/tokens/signatures where applicable.
6. Review provider/database/audit access from the earliest plausible exposure.
7. Record actor, dates, systems, validation, and remaining risk; never record
   the old or new secret.

If source history may contain the secret, stop normal feature work, preserve
the repository, notify the owner, rotate first, then perform approved history
and log review. Do not reproduce the value in `MISTAKES.md` or an issue.

### 4. Determine scope and impact

Answer with evidence and confidence level:

- What happened, when did it begin/end, and is access still possible?
- Which mode, release, database, provider account, credential, or staff role?
- Which `data_class_id` values and how many subjects/records?
- Was data viewed, acquired, changed, deleted, made public, or merely exposed?
- Were encryption, authentication, least privilege, and mode separation intact?
- Can money, inventory, orders, identity, or communications still be trusted?
- Which logs/backups/providers could confirm or contradict the hypothesis?
- Could containment or notification itself increase harm?

Review provider access and subprocessors. Verify fixes rather than accepting a
provider assurance without evidence.

### 5. Legal and communications decision

Escalate promptly to qualified counsel. Counsel determines affected
jurisdictions, notification recipients/timing/content, preservation, law
enforcement, regulator, insurer, contractual, and provider duties.

The communications authority maintains one approved fact set. Messages must be
plain, accurate, useful, and updated as facts change. They must not conceal a
material fact, speculate, expose another person, compromise the investigation,
or claim legal/security guarantees.

### 6. Eradicate, recover, and validate

- Remove the root cause and all persistence paths; patch/configure/rebuild from
  a trusted immutable release as appropriate.
- Restore only into an isolated environment. Reapply deletion/anonymization
  tombstones and later business state before service.
- Reconcile PostgreSQL, Stripe, inventory, orders, refunds, email, and provider
  state where affected. Never overwrite expected amounts with provider values.
- Validate authorization, secret rotation, mode separation, health, logging,
  alerting, backups, and critical user flows with synthetic data.
- Obtain incident-command approval before restoring traffic or checkout.

### 7. Support, close, and learn

Track notifications and support without turning the incident ledger into a
copy of customer correspondence. Complete root-cause analysis and corrective
actions with owners, deadlines, verification, and rollback.

Closure requires containment, scope, legal/communications decision, recovery,
monitoring, evidence manifest, customer/provider actions, and overdue-action
review. Revisit at 7 and 30 days for `SEV-1/2`, or the approved interval.

Anonymized lessons may update controls and `MISTAKES.md` when an attempted
engineering action failed; never include affected personal data or secrets.

## Incident-specific stop conditions

- Suspected Stripe/payment mismatch: stop fulfillment and, when systemic, stop
  checkout; use retrieved provider state and bounded reconciliation records.
- Inventory integrity uncertainty: stop affected SKU/preorder sales and require
  human review; do not edit counts without audit history.
- Research boundary failure: take the research surface or affected route out of
  service until commerce code, credentials, routes, and records are proven
  unreachable.
- Public R2/private-data exposure: block access and cache, preserve bounded
  evidence, enumerate objects and access, rotate credentials, and review every
  cached/custom-domain path.
- Backup compromise: isolate backup credentials/storage, preserve evidence,
  verify recovery copies, and do not destroy the only known-good restore point
  without incident-command and legal approval.

## Current limitation

On 2026-08-30 the repository did not contain the structured logging,
correlation, redaction, health/readiness, monitoring, alert routes, or incident
runbooks that `PROJECT_PLAN.md` says A1.3 completed. This annex supplies policy
and procedure only. It does not satisfy A1.3 implementation or staging-alert
acceptance.
