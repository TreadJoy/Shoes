# Visual Regression Review

This document defines the manual visual snapshot matrix for the current
server-rendered TreadJoy interface. It is a review aid, not a replacement for
functional tests, accessibility testing, or a browser performance trace.

## Snapshot policy

- Use the same release commit, deterministic nonproduction fixture, browser,
  viewport, authentication state, and route before comparing images.
- Capture viewport screenshots at a desktop width above `1024px` and at the
  `390x844` small-phone viewport. Record the actual pixel dimensions emitted by
  the browser harness.
- Store snapshots in a disposable local audit directory by default. Do not
  commit screenshots that contain development imagery, customer data, order
  data, provider data, or assets without approved provenance.
- Synthetic commerce records must use unmistakably noncustomer values and a
  disposable local database. Never seed a shared or production database for a
  visual review.
- Inspect the rendered images in addition to checking routes and DOM roles.
  Full-page screenshot stitching can repeat sticky headers or footers in some
  browser harnesses, so viewport captures are the authoritative comparison.

## Required matrix

| Surface | Commerce | Research | Authentication state |
| --- | --- | --- | --- |
| Homepage | `/` | `/` | Guest |
| Catalog | `/products/` | `/products/` | Guest |
| Product detail | `/products/<approved-fixture-slug>/` | Same | Guest |
| Cart | `/cart/` | Route must be absent | Guest and account |
| Authentication | `/accounts/login/` | Same | Guest |
| Checkout return | `/orders/success/<order-id>/` | Route must be absent | Owning account or authorized attempt |
| Order detail | `/orders/<order-id>/` | Route must be absent | Owning account |
| Survey | `/survey/` | `/survey/` | Guest |
| Waitlist | `/waitlist/join/` | `/waitlist/join/` | Guest |

For authenticated screenshots, verify that every visible logout control is a
CSRF-protected POST form. For research screenshots, also run the automated
negative-capability tests that prove cart and order routes, models, context,
and Stripe initialization are absent; a screenshot of a 404 page is not
sufficient boundary evidence.

For both homepage modes, compare primary and secondary calls to action for
consistent shape, sizing, typography, and hover, keyboard-focus, pressed,
disabled, and busy states. Confirm that editorial text links, category entries,
and the video play control retain their distinct link, card, and media-control
treatments.

## Phase 6 baseline

The 2026-08-30 cleanup review captured and inspected all shared surfaces in
both modes at desktop and `390x844`, plus every commerce-only surface. The
binary images remain disposable local evidence because the development logo
and synthetic product placeholders are not approved release assets. The
semantic scan found no obsolete template safe to remove, all five committed
static source files have current template references, and the three small
JavaScript modules remain in use.

The browser environment did not expose the dedicated DevTools performance
trace service, so this review does not claim Lighthouse or Core Web Vitals
evidence. It separately verified the three-query catalog budget, local response
timings, static byte counts, both-mode tests, and rendered layouts. Capture a
real production-like DevTools/Lighthouse baseline under the A8.3 performance
task before launch.
