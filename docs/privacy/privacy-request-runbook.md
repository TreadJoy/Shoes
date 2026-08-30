# Privacy-Request Runbook

**Policy:** `TJ-PRIV-001` `0.1-draft`
**Status:** Proposed procedure; contact channel, deadlines, and authority require
owner and privacy/legal approval before public use

## Purpose and safety rules

Use this runbook for access, correction, deletion/anonymization, marketing
withdrawal, portability, and related privacy requests. It does not create a
legal right or exception; qualified counsel determines applicable obligations
and deadlines.

- Never ask for a password, session cookie/key, email token, API key, full card
  number, CVC, or unrelated identity information.
- Avoid government identification. Collect it only when counsel documents why
  a lower-risk method cannot verify a legally required request.
- Do not confirm that an account, order, waitlist entry, or email exists before
  verification.
- Never send an export to a newly supplied destination without separately
  verifying that destination.
- Do not put request contents, identity evidence, exports, or private contact
  details in Git, ordinary logs, public storage, or general chat.
- A request cannot erase a suppression entry, legal hold, another person's
  data, or protected commercial history merely by asking for “all deletion.”

## Proposed operating targets

These are internal review proposals, not public or statutory promises:

| Milestone | Proposed target |
|---|---|
| Acknowledge without confirming record existence | 5 business days |
| Assign owner, applicable deadline, and verification method | 3 business days after intake |
| Complete ordinary verified request | 30 calendar days after verification, or earlier when applicable law requires |
| Escalate provider delay, legal hold, dispute, or high-risk export | Same business day it is identified |
| Delete temporary export | Immediately after confirmed receipt when safe, otherwise automatically within 7 days |

Counsel must replace these targets if an applicable rule is shorter or requires
a particular extension/appeal notice.

## Minimal request ledger

Create one restricted record with:

- opaque request ID;
- request type and intake date/channel;
- claimed relationship category, without recording unnecessary narrative;
- data-class IDs and mode(s) believed in scope;
- verification method, status, and date—not the secret or identity evidence;
- applicable deadline and counsel escalation flag;
- systems/providers checked and date;
- decision category and bounded rationale code;
- approved actions, executor, reviewer, and completion timestamps;
- export ID/expiry/receipt when applicable;
- deletion/anonymization tombstone ID;
- legal-hold or appeal reference; and
- closure and next-action dates.

Until a dedicated ledger exists, use an approved restricted operational system.
Do not improvise with repository issues or ordinary email folders.

## Workflow

### 1. Receive and contain

1. Assign the opaque request ID and privacy-request owner.
2. Preserve the original message in the approved restricted channel.
3. Do not click untrusted links or open unapproved attachments.
4. Send the neutral acknowledgement without confirming record existence.
5. Identify possible urgency: active account compromise, exposed data, legal
   process, imminent deadline, or complaint. Route a suspected incident to the
   security annex without closing the request.

### 2. Classify scope

Select all that apply:

- waitlist/marketing only: `REL-WAITLIST-001`, `REL-CONSENT-001`,
  `REL-SUPPRESSION-001`, `OPS-EMAIL-001`;
- anonymous research survey: `RS-SURVEY-001` and possibly a live
  `RS-SURVEY-DRAFT-001` session;
- account without commerce: `ID-ACCOUNT-001`, `ID-EMAIL-TOKEN-001`, sessions;
- authenticated customer: account plus cart, checkout, orders, and providers;
- guest purchaser: checkout email/order facts without assuming that access to
  an email inbox alone proves order ownership;
- staff, creator, or media subject: staff audit or public-rights evidence;
- incident/complaint/hold: restricted escalation path.

Determine which deployment database owns each class. Never copy raw records
between databases to make the search easier.

### 3. Verify proportionately

Use the least additional data that provides adequate assurance:

| Relationship | Preferred verification | Prohibited shortcut |
|---|---|---|
| Signed-in account | Recent reauthentication plus existing verified email when needed | Trusting username or visible profile alone |
| Waitlist/marketing | Single-use challenge to the already stored address | Revealing whether the address is enrolled before challenge succeeds |
| Guest paid order | Single-use challenge to checkout email plus bounded order facts or future approved guest-access mechanism | Accepting an order ID, provider ID, tracking number, or session key alone |
| Anonymous survey | Explain that completed responses deliberately have no identity link | Searching free text for guessed identity and claiming a match |
| Staff/creator/media subject | Existing approved organizational or contract channel | Accepting a new social-media account or forwarded document without review |

Record only verification success/failure, method category, and date. Revoke or
expire the challenge after use.

### 4. Search authoritative systems

Use approved read-only queries or services. Search only after verification and
only within the request's scope.

1. Correct mode-specific PostgreSQL database: account/allauth, sessions,
   waitlist/survey, or commerce models mapped in `data-register.csv`.
2. Selected email provider: delivery, suppression, and approved consent facts.
3. Stripe for a verified commerce request: bounded customer-facing transaction
   facts; do not download raw payloads as a convenience.
4. Active Cloudflare, monitoring, carrier, tax, return-evidence, support, and
   analytics providers only when their register row shows they are active and
   the subject can be located under approved identifiers.
5. Backups are handled by aging and tombstone replay, not an ad hoc scan or
   rewrite of immutable recovery media.

Record systems checked, queries/services used, date, and count. Do not copy
unnecessary values into the ledger.

### 5. Review and decide

- **Access/export:** identify customer-supplied data and customer-facing facts;
  remove other persons, secrets, security/fraud reasoning, internal notes,
  privileged material, staff-private information, and unnecessary provider
  identifiers.
- **Correction:** correct mutable identity/preferences at the authoritative
  source. Do not rewrite immutable transaction history; append a correction
  event when the approved domain design requires it.
- **Deletion/anonymization:** apply the register action. Preserve bounded
  commercial facts, suppression, and holds; never cascade-delete material
  order/payment/fulfillment history.
- **Withdrawal/opt-out:** stop future optional processing, create or update the
  minimal suppression record, and separate marketing from operational email.
- **Restriction/refusal/extension:** require a bounded rationale category and
  privacy/legal review when law, fraud/security, another person's rights,
  active transaction, dispute, or hold affects the outcome.

The privacy-request owner proposes the decision. Finance/tax, incident,
fulfillment, or research owners review their data classes. Counsel reviews
rights, exceptions, notices, holds, appeals, and uncertain scope.

### 6. Execute safely

1. Produce a dry-run list of data-class IDs, systems, row/object counts, and
   actions without outputting personal values.
2. Obtain the required approval and, for commerce history or bulk/provider
   action, a second-person review.
3. Execute idempotently in authoritative systems first, then providers.
4. Create the minimal tombstone covering the maximum backup window.
5. Invalidate relevant sessions/tokens when identity or security is affected.
6. Re-run the scoped search and record counts/results.
7. Do not run `purge_legacy_stripe_payloads` as part of an individual request;
   it is a separate backup-gated migration cleanup.

### 7. Export and deliver

1. Build from an allowlist keyed by data-class ID.
2. Escape spreadsheet-formula prefixes if CSV is approved.
3. Use a strong encrypted archive or authenticated, expiring delivery path in
   a nonpublic store. Public R2 is forbidden.
4. Verify the exact recipient immediately before transmission. Typing or
   uploading personal data to a destination is itself a disclosure.
5. Record checksum, size, expiry, transmission time, and receipt status without
   storing the decryption secret beside the export.
6. Delete the export at receipt or within 7 days and verify deletion.

### 8. Communicate and close

The response states what was located, corrected, exported, deleted,
anonymized, suppressed, retained, or not locatable; the bounded reason for any
retention; provider work still pending; and how backup aging works. It must not
claim immediate erasure from immutable backups or reveal security internals.

Close only after verification, actions, provider responses, tombstone, export
deletion, reviewer approval, and required appeal/escalation information are
recorded.

## Scenario-specific rules

### Waitlist deletion and unsubscribe

Verify the existing address, stop active marketing, remove `REL-WAITLIST-001`
identity, and retain only approved `REL-SUPPRESSION-001` evidence. Do not send a
promotional confirmation.

### Anonymous completed survey

Because current completed responses store no user or session identifier,
explain that the response cannot be reliably found by identity. Do not search
free text for a name or delete a guessed row. A live draft can be abandoned by
clearing the verified current session.

### Account with no commerce record

Disable access, expire sessions/tokens, apply the closure grace if approved,
delete/anonymize identity, and preserve only security/suppression facts allowed
by the register.

### Guest or account order

Verify strongly, separate direct identity from transaction facts, check all
refund/return/dispute/tax/hold triggers, and use the future A3.2 anonymization
service. Until that service and retention values are approved, do not manually
edit or cascade-delete commerce rows.

### Backup restore after deletion

Keep restored systems isolated. Replay deletion/anonymization tombstones and
all later state changes, run scoped verification, obtain recovery approval, and
only then serve traffic.
