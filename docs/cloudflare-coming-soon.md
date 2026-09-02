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

## Deployment gate

Do not deploy from an unreviewed local working tree. Phase 2 must connect
Workers Builds to only the approved GitHub repository, protect preview URLs
with Cloudflare Access, run the tests before deploy, validate the preview, and
exercise version rollback. Obtain action-time confirmation immediately before
granting the persistent GitHub integration permission.

Phase 3 must re-export and compare DNS, preserve the existing mail and
verification records, obtain action-time confirmation immediately before
attaching the apex and `www` custom domains, and verify HTTPS before staging
HSTS. HSTS is intentionally absent from this package until that live check.

## Rollback

For a bad preview or content deployment, restore the preceding known-good
Worker version from Cloudflare's deployment history, then confirm its version
identifier, source commit, response status, headers, and rendered page. A Git
revert followed by the normal tested deployment is the durable source rollback.

Public routing rollback is a separate Phase 3 operation: detach both Worker
custom domains and restore the reviewed pre-cutover DNS export. Never edit or
replace the authoritative mail or ownership-verification records as part of a
web rollback.

## References

- [Cloudflare static assets configuration](https://developers.cloudflare.com/workers/static-assets/configuration/)
- [Cloudflare static asset headers](https://developers.cloudflare.com/workers/static-assets/headers/)
- [Wrangler commands](https://developers.cloudflare.com/workers/wrangler/commands/)
- [Workers Builds configuration](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/)
