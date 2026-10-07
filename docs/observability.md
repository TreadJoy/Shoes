# A1.3 / A2.3 Plan 3 — Health and Observability

**Prepared:** 2026-09-02
**Status:** Repository implementation complete; provider and staging evidence
pending.

## Endpoints

| Endpoint | Success | Dependency failure | Body and headers |
|---|---:|---:|---|
| `GET /health/live/` | `200` | Not applicable | `{"status":"ok"}`; `Cache-Control: no-store` |
| `GET /health/ready/` | `200` | `503` | `{"status":"ok"}` or `{"status":"unavailable"}`; `Cache-Control: no-store` |

Both responses are intentionally generic. They do not expose versions,
provider names, database details, exception text, configuration, or PII. The
readiness probe performs a minimal `SELECT 1` against Django's authoritative
database connection. A failed probe emits the deduplicable
`database_unavailable` alert event and returns only the generic `503` body.

## Correlation and redaction

`treadjoy.observability.RequestCorrelationMiddleware` runs before application
middleware. It accepts only a UUID-shaped `X-Request-ID`; invalid or missing
values are replaced with a new UUID. The response returns the normalized ID in
the same header. A context variable makes the ID available to application log
records during the request.

The stdout handler emits an allow-listed JSON record with timestamp, level,
logger, event, request ID, method/path/status/duration, and alert fields. It
never serializes arbitrary `LogRecord` attributes. Before serialization it
redacts:

- authorization, password, secret, token, API-key, access-key, and refresh-token
  assignments;
- Stripe, Resend, and similar provider key prefixes;
- email addresses; and
- opaque waitlist confirmation/unsubscribe path tokens.

Application code must still avoid logging request bodies, query strings,
headers, full addresses, session IDs, provider payloads, or customer data. The
filter is a safety boundary, not permission to log sensitive values.

## Provider-neutral monitoring integration

The application writes structured events to stdout so the selected managed
origin can ingest them without a vendor SDK. `emit_alert()` validates a short
alert name and severity and emits an `event=alert` record with a stable
deduplication key. The selected provider's log/metric monitor must route these
events to the owner after staging configuration; no external network call is
made by local or CI tests.

## Alert definitions

| Alert | Severity | Initial signal | Owner action |
|---|---|---|---|
| `health_readiness_503` / `database_unavailable` | Critical | Any readiness failure, deduplicated for 5 minutes | Check origin/database status, stop unsafe writes, follow database-outage runbook |
| `http_5xx_rate` | Critical | 5xx responses ≥5% of requests for 5 minutes or ≥10 in 5 minutes, whichever is lower | Inspect the correlated release/error events and consider rollback |
| `storage_unavailable` | Critical | Two consecutive storage probes fail or a public-media request returns 5xx for 5 minutes | Stop media writes, verify R2/edge configuration, follow storage runbook |
| `payment_reconciliation_mismatch` | Critical | A provider event or retrieved session does not match the server-side amount, currency, ownership, or payment state | Keep the order unpaid/reviewable, preserve the provider event ID, and follow the payment-reconciliation runbook |
| `reservation_expiry_backlog` | High | Expired reservations remain open past the scheduled cleanup window or the cleanup job fails twice | Pause new checkout promotion if availability is uncertain, run the idempotent cleanup once, and reconcile inventory |
| `inventory_exception` | Critical | A reservation, payment, release, or fulfillment transition cannot produce the expected inventory allocation change | Stop automatic retries that could double-adjust stock, preserve the transition identifiers, and escalate for human review |
| `email_delivery_failure` | High | Any provider failure/bounce/complaint event without a successful retry within 15 minutes | Pause delivery, inspect bounded provider state, follow email runbook |
| `scheduler_missed_or_failed` | High | A required scheduled job has no success event in its expected window or fails twice | Run the job once under the runbook and investigate provider scheduling |
| `provider_event_backlog` | High | Signed provider events remain unprocessed for 15 minutes | Preserve event IDs, replay idempotently, and escalate to the owner |
| `redaction_regression` | Critical | Synthetic canary detects a secret/token/email in a captured record | Stop public traffic, preserve only sanitized evidence, rotate affected secrets |

Thresholds are initial operational defaults for the private POC. They must be
tested with synthetic data and owner-approved in staging before public traffic;
they are not evidence that a monitoring provider is currently configured.

## Verification evidence

- Health endpoint tests cover generic success, dependency failure, `503`,
  no-store headers, and absence of dependency details.
- Correlation tests cover valid propagation, invalid-ID replacement, and
  request-completion records.
- Redaction tests cover provider secrets, token-like assignments, email
  addresses, and waitlist path tokens.
- Alert tests emit a synthetic warning and verify the structured alert fields.
- Provider alert routing, synthetic delivery, escalation, and dashboard access
  remain staging tasks for the selected origin.
