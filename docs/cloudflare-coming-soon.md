# Cloudflare Coming-Soon Worker

## Purpose and boundary

`treadjoy-coming-soon` is a temporary, public, noindexed holding page for
`https://tread-joy.com/`. It is an asset-only Cloudflare Worker with no
application runtime, forms, cookies, JavaScript, analytics, external assets,
storage bindings, database access, or secrets.

This package is not the Django research deployment and is not evidence that
research or commerce launch gates have passed. Provider permissions, preview
protection, deployment, custom domains, DNS changes, redirects, and public
exposure belong to later separately approved phases.

## Source and resources

- Worker name: `treadjoy-coming-soon`
- Package root: `deploy/cloudflare/coming-soon`
- Static asset directory: `deploy/cloudflare/coming-soon/public`
- Intended canonical URL: `https://tread-joy.com/`
- Intended production branch: `main`
- Intended Workers Builds root: `deploy/cloudflare/coming-soon`
- Build command: `npm test`
- Deploy command: `npx wrangler deploy`
- Build watch path: `deploy/cloudflare/coming-soon/**`

Do not add account IDs, credentials, billing data, provider screenshots,
database bindings, R2 bindings, KV namespaces, Hyperdrive configurations, or
application APIs to this package.

## Local verification

Use Node 24 as pinned in `.node-version`, then run from the package root:

```sh
npm ci
npm test
npx wrangler deploy --dry-run
npx wrangler dev --ip 127.0.0.1 --port 8787
```

With the development server running, verify:

```sh
curl --fail-with-body --silent --show-error --dump-header - http://127.0.0.1:8787/ -o /dev/null
curl --silent --show-error --dump-header - http://127.0.0.1:8787/not-a-page -o /dev/null
```

The first request must return `200`; the unknown path must return the branded
page with `404`. Both responses must include the policy from `public/_headers`,
set no cookie, and load only the local stylesheet. Inspect the page at widths
320, 390, 768, 1440, and 1920 pixels, at 200% zoom, with keyboard navigation
and reduced-motion enabled. Record browser and Lighthouse results at deployment
time; local checks do not substitute for tests against the Cloudflare route.

Before committing, review only the intended paths and run the repository
checks:

```sh
git diff --check
git status --short
git diff -- .gitignore deploy/cloudflare/coming-soon docs/cloudflare-coming-soon.md PROJECT_PLAN.md
rg -n --hidden --glob '!node_modules/**' '(api[_-]?key|secret|token|password|account[_-]?id)' deploy/cloudflare/coming-soon docs/cloudflare-coming-soon.md
```

The final pattern scan is a review aid, not proof that a secret scanner passed.
Run the repository's established full-history secret scan before promotion.

### Phase 1 local evidence — 2026-09-02

- Node `24.19.0` and exactly pinned Wrangler `4.128.0` were used.
- A clean `npm ci` installed 36 packages and reported zero known
  vulnerabilities; all nine built-in Node tests passed.
- `wrangler deploy --dry-run` read exactly five deployable assets, reported no
  bindings, and exited successfully without contacting a Cloudflare account.
- Local HTTP checks returned `200` for `/` and branded `404` for an unknown
  path. Both responses included the configured CSP, noindex, framing,
  referrer, permissions, MIME-sniffing, and cache headers and no `Set-Cookie`.
- Browser checks at 320, 390, 768, 1440, and 1920 CSS pixels found the exact
  approved holding-page text and no horizontal overflow. The 404 recovery link
  was visible, enabled, and in the keyboard tab order. A 720 CSS-pixel reflow
  check represented a 1440-pixel desktop viewport at 200% browser zoom and had
  no horizontal overflow. The in-app browser did not expose a measurable
  native zoom setting, so the exact 200% browser-control check remains a
  deployment-time manual gate.
- Lighthouse 13.4.1 reported Performance 100, Accessibility 100, LCP 0.93
  seconds, CLS 0, and TBT 0 against the local Worker. Its SEO score was
  intentionally reduced by the required noindex directives. It also logged the
  browser's conventional `/favicon.ico` 404; the approved package intentionally
  contains no imagery or favicon.

These measurements are local diagnostics, not evidence of Cloudflare edge
performance, Access protection, redirects, TLS, custom-domain behavior, or a
public deployment.

### Phase 2 provider evidence — 2026-09-02

- Workers Builds is connected only to `TreadJoy/Shoes`; the GitHub organization
  authorization was completed with repository-scoped access.
- Worker `treadjoy-coming-soon` is configured for production branch `main`,
  root `deploy/cloudflare/coming-soon`, build `npm test`, deploy
  `npx wrangler deploy`, non-production version command
  `npx wrangler versions upload`, non-production builds enabled, and watch
  include `deploy/cloudflare/coming-soon/**` (excluding `node_modules/**` and
  `.git/`).
- A Cloudflare-managed Workers Builds token was approved at action time. No
  token value is stored here; build variables and secrets are empty, and no
  runtime bindings, database, KV, R2, Hyperdrive, or application APIs were
  added.
- The `d3997a9` main-branch build succeeded and produced preview version
  `bdf569e2`. The production `workers.dev` URL returned `200` for `/` and
  `404` for an unknown path with the configured security and noindex headers.
  The preview URL redirected to Cloudflare Access (`302`), while production
  remained publicly readable.
- Preview-only Cloudflare Access uses the Cloudflare-account-members allow
  policy with 24-hour sessions. No custom domains, routes, DNS records, HSTS,
  or production `workers.dev` disablement were changed.
- The approved rollback drill temporarily moved 100% traffic from `bdf569e2`
  to `eb66dde5`, then restored `bdf569e2` to 100%. The restored public page and
  preview Access redirect were rechecked afterward.

### Phase 3 provider evidence — 2026-09-03

- After a fresh DNS export and review, the zone contained the original three
  mail/ownership records unchanged. Cloudflare added exactly two proxied Worker
  records for the custom domains: the apex (`@`) and `www`.
- Production custom domains `tread-joy.com` and `www.tread-joy.com` are attached
  to `treadjoy-coming-soon`. The production `workers.dev` URL is disabled;
  versioned preview URLs remain enabled and protected by the existing
  preview-only Cloudflare Access policy.
- Three active 301 redirect rules preserve the original path and query string:
  `http://tread-joy.com/*` to the HTTPS apex, and both HTTP and HTTPS
  `www.tread-joy.com/*` to the equivalent HTTPS apex URL.
- Read-only checks returned one redirect for each noncanonical URL, `200` for
  the canonical root, and a branded `404` for an unknown apex path. The apex
  and `www` HTTPS responses carry the configured security/noindex headers and
  `Strict-Transport-Security: max-age=3600`, with no `includeSubDomains` or
  `preload` directive.
- Cloudflare's dashboard HSTS control does not offer a one-hour duration, so an
  active response-header transform named `TreadJoy staged HSTS edge header`
  applies the exact one-hour value only to the apex and `www` hostnames. The
  same value is also source-controlled in `public/_headers` for the next
  successful Worker deployment.
- Commit `ff76c28` passed the nine built-in Node tests. Its Workers Builds
  attempts stalled before cloning/installing; the initial attempt and one
  retry were canceled after waiting. No Worker content version changed: the
  deployed version remains `bdf569e2` from `d3997a9` while the edge HSTS rule
  supplies the staged header.

### Phase 4 provider evidence — 2026-09-03

- The account has one active member with the `Super Administrator - All
  Privileges` role. The owner profile email is verified. Account two-factor
  authentication is currently inactive; enabling a factor requires the owner
  to complete the credential/OTP flow directly and was not attempted here.
- The account Notifications page has no configured rules. The current
  notification catalog does not expose a Workers Builds build-failure rule,
  and the Worker settings page has no native build-alert destination. The
  newer Workers Builds event-subscription path would require a separately
  approved queue/consumer and alert endpoint, so no notification resources
  were created.
- The inventory remains intentionally small: one static-assets Worker with no
  runtime bindings, variables, secrets, Logpush, Tail Worker, or enabled
  Workers Observability; no Web Analytics property is configured. Hyperdrive
  has no configurations; R2 has no active subscription or bucket; KV, D1, and
  Analytics Engine have no resources; and account API tokens, OAuth clients,
  Access service tokens, and reusable Zero Trust policies are empty.
- The existing preview-only Access application and its
  `Cloudflare Workers Preview URLs` account-member allow policy remain in
  place. They are required for the protected Worker previews and were not
  changed.
- A persistent cloudflared tunnel named `First Tunnel for web Data to DBEAVER`
  remains healthy with one connected replica and no routes. It is an unfinished
  administration path, not part of the public Worker or database architecture.
  Its token and local connector were not rotated or removed; any cleanup,
  rotation, or policy change requires separate owner approval.
- Billing remains on the existing free Worker and Zero Trust plans. No paid
  upgrade, R2 subscription, analytics product, or other billable feature was
  enabled.

### Holding-page responsive refresh — 2026-09-05

- The public holding-page source now uses a white outer canvas, a height-aware
  dynamic-viewport frame, centered copy, slightly looser letter spacing, and
  two CSS-only pixel-tread corner accents in the existing sky, gold, and ink
  palette. The upper-left TreadJoy stamp was removed from the holding page and
  retained on the custom 404.
- All nine Node tests and the Wrangler 4.128.0 deployment dry run passed. The
  dry run read the same five static assets, reported no bindings, and introduced
  no JavaScript, imagery, remote resource, form, cookie, storage, or secret.
- Browser checks passed at 320x568, 390x844, 568x320, 720x450, 800x600,
  1024x768, 1280x720, 1440x900, 1536x864, and 1920x1080 CSS pixels. At every
  size the holding page matched the viewport in both axes, the message center
  matched the frame center, and all copy remained inside the frame. The 720x450
  case provides the documented 200% reflow approximation.
- The custom 404 retained its visible brand and recovery link at 320x568 and
  568x320 without horizontal overflow or decorative overlap. It intentionally
  permits vertical document scrolling at exceptionally short heights so the
  recovery link cannot be clipped.
- Local HTTP checks returned `200` for `/` and branded `404` for an unknown
  path with the configured CSP, HSTS, noindex, permissions, framing, referrer,
  MIME-sniffing, and cache headers. Public Worker deployment and post-deploy
  edge verification remain separate evidence.

## Deployment gate

Do not deploy from an unreviewed local working tree. Phase 2 must connect
Workers Builds to only the approved GitHub repository, protect preview URLs
with Cloudflare Access, run the tests before deploy, validate the preview, and
exercise version rollback. Obtain action-time confirmation immediately before
granting the persistent GitHub integration permission.

Phase 3 must re-export and compare DNS, preserve the existing mail and
verification records, obtain action-time confirmation immediately before
attaching the apex and `www` custom domains, and verify HTTPS before staging
HSTS. The staged one-hour HSTS value is added only after that live check; it
does not include subdomains or preload. The provider evidence above records
the completed cutover and the temporary Workers Builds runner issue.

Phase 4 is an audit-only hygiene step. Preserve the single owner role and
preview Access policy, do not enable paid products, and do not create a
Workers Builds event-subscription consumer until an alert destination and a
separately approved resource design exist. Treat the existing DBeaver tunnel
as a persistent exception and obtain explicit deletion or rotation approval
before changing it.

## Rollback

For a bad preview or content deployment, restore the preceding known-good
Worker version from Cloudflare's deployment history, then confirm its version
identifier, source commit, response status, headers, and rendered page. A Git
revert followed by the normal tested deployment is the durable source rollback.

Public routing rollback is a separate Phase 3 operation: disable the three
redirect rules and staged HSTS transform if required, detach both Worker custom
domains, and restore the reviewed pre-cutover DNS export. Never edit or replace
the authoritative mail or ownership-verification records as part of a web
rollback. Re-enable the production `workers.dev` URL only as an explicit,
reviewed rollback action.

## References

- [Cloudflare static assets configuration](https://developers.cloudflare.com/workers/static-assets/configuration/)
- [Cloudflare static asset headers](https://developers.cloudflare.com/workers/static-assets/headers/)
- [Wrangler commands](https://developers.cloudflare.com/workers/wrangler/commands/)
- [Workers Builds configuration](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/)
