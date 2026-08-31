# Production Configuration Contract

TreadJoy uses two independent settings axes:

- `TREADJOY_MODE` is `research` or `commerce` and controls application
  capability. Research rejects nonempty Stripe configuration in every
  environment; staging and production reject even empty `STRIPE_*` process
  variables so deployment manifests must omit them entirely.
- `TREADJOY_ENVIRONMENT` is `local`, `ci`, `staging`, or `production` and
  controls deployment hardening. `ci` is available only through
  `Shoes.ci_settings` with `TREADJOY_CI=true`.

Only staging and production are public environments. They fail at Django
startup unless every required configuration variable is set and valid. Errors
identify variable names and requirements but never print values.

## Public environment variables

Set these through the selected managed origin's configuration or secret store,
not a committed `.env` file:

- `TREADJOY_INGRESS=cloudflare-locked`, `DJANGO_DEBUG=false`, a generated
  `SECRET_KEY`, exact non-wildcard `ALLOWED_HOSTS`, and HTTPS-only
  `CSRF_TRUSTED_ORIGINS` whose hosts are listed in `ALLOWED_HOSTS`.
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and
  `DB_SSLMODE`. `verify-ca` and `verify-full` additionally require an absolute
  `DB_SSLROOTCERT` path.
- An absolute `STATIC_ROOT`; `R2_ACCOUNT_ID`, `R2_BUCKET_NAME`,
  `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, and
  `R2_MEDIA_CUSTOM_DOMAIN`.
- Commerce requires `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`,
  `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, and `SERVER_EMAIL` and uses SMTP
  with STARTTLS.
- Research requires the approved notice version/body/matching SHA-256,
  retention version, production-strength identity HMAC key,
  Resend send/webhook/segment configuration, two sender addresses on distinct
  verified `tread-joy.com` subdomains, and monitored
  `RESEARCH_EMAIL_REPLY_TO=hello@tread-joy.com`. The management key belongs
  only in the contact-sync/broadcast job, not the ordinary web process.
- `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, and
  `SECURE_HSTS_PRELOAD`.

The R2 custom domain is the only approved public media read path. Do not enable
or publish an `r2.dev` URL. Use a distinct bucket namespace and credentials for
each deployment, and put only approved public media there.

## Cloudflare ingress contract

`cloudflare-locked` allows Django to trust `X-Forwarded-Proto` and enable HTTPS
redirects, secure cookies, and HSTS. It is an operator assertion, not evidence
that the origin is protected. Before setting it in staging or production,
configure Full (strict) TLS and prove that the origin accepts traffic only from
the approved Cloudflare path, using an origin firewall, Authenticated Origin
Pulls, or the selected managed-origin equivalent. Cloudflare must strip a
client-provided forwarded-protocol header and set the trusted one itself.

The first live HSTS stage is `SECURE_HSTS_SECONDS=3600` with subdomains and
preload disabled. Raise it only after every hostname and asset is HTTPS-safe.
Enable `includeSubDomains` only after the complete domain inventory is safe;
enable preload only with subdomains enabled and at least one year of HSTS.

## Secret rotation

Use the deployment secret store and rotate one credential class at a time:

1. Create a replacement secret or least-privilege provider key.
2. Update the deployment configuration and verify a fresh startup plus the
   relevant non-production smoke check.
3. Revoke the old secret after the overlap or token-validity window.
4. Record the actor, date, affected environment, and verification result in
   the approved operations record without recording the secret itself.

For Django signing-key rotation, deploy the new `SECRET_KEY` with the previous
key in `SECRET_KEY_FALLBACKS`, wait through the longest applicable signed-token
window, then remove the fallback. Do not use fallbacks as permanent key storage.

## CSP and static/media behavior

The application emits an enforced Content Security Policy. Scripts are
self-only; styles allow the existing Google Fonts stylesheet and the minimal
inline styles required by Django admin; images may use self, data URLs, and the
configured R2 custom domain; YouTube is restricted to the privacy-enhanced
embed domain. The base-template startup script is a same-origin static asset so
the policy does not require `unsafe-inline` scripts.

Public static files use Django's manifest storage and are collected into
`STATIC_ROOT`; the managed origin must serve that directory through Cloudflare.
R2 stores media only. If the selected origin cannot serve collected static
files, resolve that during A2.3 before public launch rather than silently
switching this contract.
