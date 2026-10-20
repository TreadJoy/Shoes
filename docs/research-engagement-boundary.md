# Research Engagement Boundary

This is the A2.2 application and operations contract. It does not activate a
public deployment, approve legal copy, verify provider domains, place secrets,
or deploy Cloudflare rules; those remain approval/A2.3 gates.

## Public identity and consent

- Research has no customer signup, login, password-reset, email-management,
  profile, or allauth route. Django admin login is staff-only.
- Waitlist forms collect email only and require the unchecked approved
  two-product-update-messages-per-UTC-month statement.
- All eligible/ineligible/known/unknown outcomes use one neutral response.
- Confirmation and unsubscribe GETs are read-only; CSRF-protected POSTs own
  state changes. Confirmation expires in 72 hours.
- Tokens are opaque 256-bit HMAC values; only SHA-256 digests are stored.
- Existing waitlist rows migrate to `legacy_quarantined` and are never
  contacted or synchronized without a fresh request and confirmation.
- Suppression evidence is HMAC-keyed and preserved when a new local double
  opt-in supersedes it. Provider-side reactivation cannot restore consent.

## Staff capabilities

- `Research analyst`: view and formula-safe CSV export of anonymous survey
  responses only.
- `Relationship manager`: view bounded consent/suppression/delivery state and
  record only an already-drafted provider broadcast ID, then approve it.
- Broadcast approval is limited to two queued/sent records per UTC month and
  stores actor, provider draft ID, timestamps, status, and aggregate recipients
  without message bodies.
- Superuser is break-glass; assigning groups and verifying least privilege is
  a release task.

The active V3 survey records product-research answers, including an age band
and gender response; gender includes a "Prefer not to say" option. These fields
remain on the anonymous survey response and are not copied to a customer
profile or linked to waitlist identity. The public privacy notice must describe
this collection before V3 is activated publicly.

## Provider and secrets

Resend 2.42.0 is hash-locked. Ordinary web delivery uses the send key; webhook
verification uses the signing secret; contact/segment synchronization and
broadcast work require the management key in a separately scoped job. If the
origin cannot scope job secrets separately, marketing activation is blocked.

Public research requires:

- `RESEARCH_PRIVACY_NOTICE_VERSION` (not a draft identifier),
  `RESEARCH_PRIVACY_NOTICE_BODY`, and a matching
  `RESEARCH_PRIVACY_NOTICE_SHA256`; approved notice text is supplied only after
  adviser/technical approval and is not authored by the implementation;
- `RESEARCH_IDENTITY_HMAC_KEY`;
- `RESEARCH_RESEND_SEND_API_KEY`, `RESEARCH_RESEND_WEBHOOK_SECRET`, and
  `RESEARCH_RESEND_SEGMENT_ID`;
- distinct `RESEARCH_EMAIL_TRANSACTIONAL_FROM` and
  `RESEARCH_EMAIL_MARKETING_FROM` addresses on separate `tread-joy.com`
  subdomains;
- monitored `RESEARCH_EMAIL_REPLY_TO=hello@tread-joy.com`; and
- effective `RESEARCH_RETENTION_POLICY_VERSION`.

The owner-scoped private development POC is narrower than public research: it
uses `ethan@tread-joy.com` as the temporary operational, reply, and error-mail
destination, assigns only the owner, and does not enable consumer
marketing/broadcast mail. The distinct public sender subdomains and monitored
`hello@tread-joy.com` reply mailbox remain mandatory before public activation;
this temporary exception does not change that contract.

CI/local use the deterministic fake adapter and make no Resend call.
Confirmation URLs use the first configured `ALLOWED_HOSTS` entry as the public
host. A2.3 must place the approved research hostname first and verify the exact
rendered link in a controlled inbox before activation.
The identity HMAC key is a long-lived suppression lookup key. Store and back it
up as a deployment secret; do not rotate it until a reviewed dual-key migration
can preserve lookup of existing suppression digests.

## Abuse and edge rules

The application permits five waitlist POSTs per session/hour, three
confirmation records per normalized-address digest/24 hours, 60 survey-step
POSTs per session/hour, and one completion per session/24 hours. Limits return
an accessible 429 plus `Retry-After`. Honeypots persist no submitted identity
or free text and increment an aggregate daily signal only.

A2.3 must stage exact-endpoint Cloudflare rules in log mode before enforcement:

- managed challenge above 10 waitlist POSTs/IP/10 minutes for
  `/waitlist/join/` and `/waitlist/join/homepage/` only;
- managed challenge above 60 survey POSTs/IP/10 minutes for
  `/survey/question/*/` only.

Turnstile remains absent. It may be proposed for only the affected form after
either endpoint records more than 100 edge/application throttle events per day
for two consecutive days or honeypots exceed 5% of attempts over seven days,
with false-positive review and recorded evidence.

## Commands and release order

```sh
python manage.py deliver_research_email --limit 100
python manage.py sync_research_resend --limit 100
python manage.py enforce_research_retention
python manage.py enforce_research_retention --apply --policy-version VERSION
python manage.py check_research_engagement
```

Retention is dry-run by default. Destructive application requires both
`--apply` and the matching effective configuration version, then operates in
bounded transactions and reports counts only. A version containing `draft`
cannot authorize deletion. The five-year evidence clock starts at the terminal
withdrawal event; suppression uses its later supersession timestamp when one
exists.

Confirmation and unsubscribe paths contain usable opaque tokens. A1.3 must
redact those path segments in edge, origin, application, error, and monitoring
logs before public traffic; the current development server does not provide
that production control. A2.2 remains incomplete until
A1.3/A1.4, A2.1 CI, staff assignment, provider review, scheduler, monitored
reply mailbox, and staging Resend/Cloudflare evidence are recorded.
