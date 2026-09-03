# A1.3 Incident Runbooks

**Prepared:** 2026-09-02
**Scope:** Private development-team-only POC. The project owner is the
responder until another operator is assigned.

## Common first actions

1. Record the UTC time, alert name, request ID or dedupe key, and the last known
   green release. Do not copy secrets, tokens, full addresses, email bodies, or
   provider payloads into the incident record.
2. Confirm whether the event is synthetic, an isolated staging failure, or a
   real POC impact. Do not widen access while diagnosing.
3. Preserve sanitized logs and provider event IDs. Keep the POC behind team-only
   access and pause scheduled jobs or writes if state correctness is uncertain.
4. After mitigation, record cause, affected window, verification, and the
   follow-up owner. Rotate credentials if exposure is possible.

## Database outage or readiness failure

**Trigger:** `database_unavailable`, repeated `/health/ready/` `503`, connection
errors, or an elevated database-related 5xx signal.

1. Check `/health/live/` and `/health/ready/` separately. If liveness is `200`
   but readiness is `503`, treat the origin process as alive but unsafe for
   database-dependent work.
2. Check the managed PostgreSQL provider status and connection/TLS state without
   printing the connection string. Do not retry destructive writes blindly.
3. If the provider is healthy, verify the runtime role's least-privilege grant,
   connection limit, and TLS configuration. Do not use the migration or backup
   role for application traffic.
4. If data integrity is uncertain, keep the POC private, stop writes, and
   restore into an isolated database. Validate schema and synthetic flows
   before changing the application connection.
5. Re-run both health checks and a synthetic read/write check. Record measured
   RTO/RPO and escalate if the one-hour/fifteen-minute targets are missed.

## Elevated 5xx or bad release

**Trigger:** `http_5xx_rate`, a failed deployment, or a reproducible error after
promotion.

1. Use the response `X-Request-ID` and sanitized `request.completed` event to
   identify the failing route. Never request the customer to send a tokenized
   confirmation URL or raw provider payload.
2. Compare the current artifact identity with the last green release. If the
   failure began at promotion and the schema is compatible, stop promotion and
   roll back to the previous artifact.
3. If a migration may have changed data, do not roll back code across an
   incompatible schema. Isolate the database, take/verify a backup, and use the
   migration recovery procedure.
4. Verify `/health/live/`, `/health/ready/`, the homepage, and a synthetic
   research flow before lifting private access restrictions.

## Payment reconciliation mismatch

**Trigger:** `payment_reconciliation_mismatch`, a provider event whose amount,
currency, ownership, PaymentIntent, or reservation state does not match the
server-side snapshot, or an order held for payment review.

1. Keep the order unpaid or in its review state. Do not mark it paid from a
   success redirect, an unverified payload, or a manually copied amount.
2. Preserve only the bounded order, Checkout-session, PaymentIntent, and
   provider-event identifiers plus the request ID. Do not copy the provider
   payload, address, email, or payment details into logs or tickets.
3. Check the authoritative reservation and order rows under the normal
   reconciliation procedure. Do not release or commit inventory twice.
4. If the mismatch is caused by the current release, stop promotion and use
   the bad-release rollback procedure only after checking migration
   compatibility. Escalate unresolved financial mismatches to the owner.

## Reservation expiry or inventory exception

**Trigger:** `reservation_expiry_backlog` or `inventory_exception`, including a
failed cleanup job, an expired reservation that remains open, or a transition
whose inventory allocation does not match the authoritative order state.

1. Pause new checkout promotion if availability cannot be proven. Do not edit
   stock counts directly or run the cleanup repeatedly.
2. Capture the bounded reservation, order, variant, transition, and job IDs;
   never record customer contact data or provider payloads.
3. Run the documented idempotent expiry/reconciliation operation once under
   owner supervision after confirming database health and current artifact.
4. Reconcile reservation, allocation, and order state. Send ambiguous cases to
   human review and restore normal promotion only after a synthetic checkout
   check passes.

## Email delivery failure

**Trigger:** `email_delivery_failure`, a failed/bounced/complained provider
event, or a stalled outbox.

1. Pause consumer/broadcast delivery. The POC has no approved consumer
   marketing scope; operational mail temporarily targets the owner's mailbox.
2. Check bounded local delivery state and provider event IDs. Never log the
   mailbox address, message body, token, or API key.
3. Retry only through the idempotent delivery command. Do not manually resend a
   confirmation or unsubscribe message from an untracked client.
4. If credentials or provider payloads may be exposed, revoke/rotate the
   affected key, preserve sanitized timestamps, and continue with the privacy
   incident runbook.
5. Send a synthetic message, verify its event path, and record the delivery
   result before resuming any approved operational email.

## Storage or media failure

**Trigger:** `storage_unavailable`, failed R2 health probe, or unexpected media
5xx responses.

1. Keep media blank for the POC and disable uploads or writes. Do not substitute
   unapproved assets or expose an `r2.dev`/provider development URL.
2. Check Cloudflare/R2 status, bucket binding, custom-domain configuration, and
   least-privilege credentials without printing values.
3. Verify that no private/customer-like object is public. If exposure is
   possible, restrict the custom domain, preserve object IDs only, and rotate
   credentials.
4. Restore only approved public media into the separate research bucket after
   an integrity and metadata review.

## Secret, token, or PII exposure

**Trigger:** `redaction_regression`, an unredacted record, accidental secret
output, or a leaked waitlist token.

1. Stop the affected log export, public route, or deployment. Do not reproduce
   or paste the exposed value into a ticket, shell, or chat.
2. Revoke/rotate the affected secret or invalidate the affected token. Review
   only the minimum sanitized log metadata needed to determine scope.
3. Remove unsafe output from the active log sink and repository history using
   the approved repository procedure; retain a sanitized incident record.
4. Run the redaction test suite and a synthetic canary. Do not restore access
   until a reviewer confirms the output is safe.
5. Escalate to the appropriate privacy/legal process before any consumer or
   public deployment. The private POC exception does not waive this response.

## Scheduler failure

**Trigger:** `scheduler_missed_or_failed`, missing retention/delivery job event,
or duplicate execution.

1. Confirm the expected job, release artifact, and last successful run from
   sanitized metadata. Do not run an unsafe cleanup command repeatedly.
2. Execute the bounded, idempotent job once under owner supervision if the
   database and provider are healthy.
3. Check for duplicate work, lock contention, and provider scheduler status.
4. Record the missed window and whether data remained within the approved
   retention/consent boundary. Escalate if a job can no longer be proven safe.
