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
| How It Works | `/how-it-works/` | `/how-it-works/` | Guest |
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

For How It Works in both modes, confirm the Night Grid exploded-study image
loads responsively, retains its descriptive alternative text and figure
caption, and does not obscure or crowd the hero copy at mobile widths.

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

## Heritage Court Gallery Addendum

For the owner-authorized Heritage Court render-study gallery, add these checks
to both homepage-mode captures:

- Capture at `390x844`, `768x1024`, and a desktop viewport at or above
  `1280px`. Confirm the one-column, two-column, and 12-column editorial
  compositions respectively, with no horizontal overflow or clipped caption.
- Confirm exactly six visible figures and labels: Night Grid, Relief Contour,
  Evergreen Route, Relief / Noir, Forest / Noir, and Relief Joyfront.
- Confirm each crop remains 16:9, preserves both shoes, and loads the expected
  960px or 1600px source without layout shift.
- Inspect Relief Contour for lost tonal detail, Evergreen Route for texture
  moire, both Noir crossovers for accidental color clashes, and Relief Joyfront
  for mascot readability at mobile width.
- Verify the render-only disclaimer remains visible as text and that commerce
  links to the compatibility explanation while research links to the survey.
- Verify keyboard focus reaches only the section link—not the noninteractive
  figures—and that its focus indication remains visible on the near-black
  surface.
- The release-content command must report no error for any Heritage Court
  derivative. Existing unrelated blocked surfaces remain launch blockers until
  separately approved and resolved.

## Slot 00 Exploded Hero Addendum

For the owner-authorized Night Grid exploded hero in both homepage modes:

- Capture at `390x844`, `768x1024`, and `1440x900`. Confirm the full 16:9 image
  is visible, the figure stays inside its grid column, and no horizontal
  overflow or layout shift occurs.
- Confirm the embedded title and seven label plates remain distinct at tablet
  and desktop widths. At phone width, confirm the adjacent caption visibly
  repeats all seven names even when the embedded callouts are too small to read.
- Confirm slot marker `00`, the visual-separation qualification, and the
  unverified-interface/removal-mechanics notice remain visible.
- Confirm the browser selects only an inventoried 960px or 1600px WebP and the
  hero is eager/high-priority while the six lower gallery images remain lazy.
- Confirm meaningful alternative text names the visual as an exploded concept,
  not a verified removal or assembly diagram.
