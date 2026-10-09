# TreadJoy Homepage Implementation Decisions

Historical snapshot: decisions and implementation state recorded on 2026-08-18
at commit `6a8c2b10ea9df7409f9aa16064cd737256975599`. Current code and approved
policy take precedence where they differ.

Last updated: 2026-08-18

Figma workspace: <https://www.figma.com/design/VPcb3JwUkrp3Yrd85tPjYp>

## Current Source of Truth

The implementation is based on `AGENTS.md`, the approved homepage plan, the
existing TreadJoy design tokens, and the product-domain taxonomy. Chrome was
used to inspect the current Li-Ning homepage as structural inspiration and to
verify the local TreadJoy implementation in both deployment modes. No Li-Ning
visual asset or copy was reproduced. Figma MCP remained quota-limited, so the
Figma file has not yet been synchronized.

## Composition

- One shared Django template serves commerce and research modes.
- Section order is hero, brand statement, Men/Women gateways, six-part modular
  explainer, lifestyle band, deferred video, community, impact, roadmap, and a
  mode-specific closing conversion.
- Commerce prioritizes Men/Women shopping and contains no waitlist content.
- Research prioritizes an inline waitlist form and survey while retaining
  non-purchase Men/Women preview links.
- The six component names and descriptions come from the authoritative active
  `PartType` records rather than duplicated marketing copy.

## Responsive Direction

- Mobile remains the first priority and retains two compact category gateways
  side by side rather than mechanically stacking them.
- The modular list changes from one column to two at 480px and three at 1024px.
- At 768px, hero and editorial sections adopt the shared 12-column logic.
- Lifestyle copy intentionally overlaps its media surface on mobile and desktop.
- Desktop navigation continues to collapse below 1024px.
- Tablet hero type is capped between 768px and 1023px so the heading retains a
  deliberate three-line composition rather than fragmenting into short lines.
- Wide-screen spacing expands at 1280px while readable copy widths remain
  constrained.

## Media and Accessibility

- Every missing asset is a visibly labeled development placeholder.
- Placeholder artwork is ordinary visible content, not a fake image role with
  invented alternative text.
- Template comments and `data-final-alt-required="true"` identify media slots
  that require approved imagery and intentional alt text before launch.
- No partner, event, impact, sustainability, testimonial, or roadmap claim has
  been invented.
- Unknown social URLs appear as non-interactive pending labels; no `#` links or
  fabricated account URLs are used.

## Video

- `HOMEPAGE_YOUTUBE_VIDEO_ID` accepts an 11-character ID or supported HTTPS
  YouTube URL. Invalid or blank values render the development placeholder.
- Valid input is reduced to a strict video ID server-side.
- The client receives only a `youtube-nocookie.com` embed URL.
- No iframe is rendered or requested until the visitor activates the play
  control.
- A configured title is used as the accessible player title; the neutral
  fallback is `TreadJoy video`.

## Motion and Interaction

- No scroll-entry reveal or parallax effect is included in the first pass. The
  restrained interaction layer keeps focus on hierarchy while avoiding an
  unneeded performance and accessibility cost.
- Hover and press feedback uses the shared 180–220ms transition tokens.
- The inline waitlist form exposes a disabled, busy, labeled loading state.
- Both waitlist entry points disable native browser validation so Django's
  field-level validation, error association, retained values, and
  `aria-invalid` state are presented consistently.
- Motion is disabled under `prefers-reduced-motion`; the loading label remains
  sufficient without a spinning animation.
- Desktop dropdowns may open through hover/focus and remain explicitly
  toggleable by click, including closing on a second click.

## Deferred Reconciliation

When Figma MCP access returns:

1. Create or reconcile Archive, Foundations, Components, Commerce, and Research
   pages in the existing file.
2. Mirror the implemented tokens, section geometry, states, and responsive
   behavior at 390px, 768px, and 1440px.
3. Capture both implemented modes and compare them with the component frames.
4. Record approved divergences and archive abandoned explorations without
   deleting unrelated prior work.
5. Replace development placeholders only after approved assets, usage rights,
   social URLs, claims, video details, and final alt text are supplied.

## Verification Status

- The focused homepage and waitlist suite passed in both real deployment modes:
  14 tests in commerce and 14 tests in research, with the intentionally
  opposite-mode assertions skipped in each process.
- Both deployment-mode system checks, migration drift detection, Python
  compilation, and diff whitespace validation passed.
- Chrome verification passed at 360×800, 430×932, 768×1024, 1280×800, and
  1536×960 in both modes with no horizontal overflow or console errors.
- Commerce Chrome checks covered waitlist absence, desktop disclosures, search,
  working Men/Women/Sale/How It Works/Bag destinations, mobile navigation, body
  scroll locking, focus containment, Escape behavior, and the unconfigured
  video's zero-iframe placeholder state.
- Research Chrome checks covered commerce-utility absence, mobile navigation,
  inline validation and `aria-invalid`, valid and case-insensitive duplicate
  signup behavior, source preservation, standalone waitlist validation, a full
  five-step survey submission, and not-found responses for cart, checkout, and
  Stripe webhook routes.
- A test-only configured video was checked in Chrome: no iframe existed before
  activation; one responsive 16:9 `youtube-nocookie.com` iframe with the
  configured accessible title replaced the play control after activation.
- The broad commerce SQLite run passed all 123 discovered tests with eight
  intentional skips for opposite-mode expectations and PostgreSQL-only
  row-locking concurrency cases.
- The broad research SQLite run passed all 61 discovered tests with eight
  intentional skips for commerce-only modules/expectations. Research-specific
  catalog-preview assertions replace the skipped purchase-state assertions.
- Static token contrast checks caught and corrected muted text on brand blue and
  dark-surface focus-ring treatment; final computed pairs meet the applicable
  4.5:1 text or 3:1 focus-indicator thresholds.
- PostgreSQL-backed test creation remains unavailable because the configured
  database role lacks `CREATE DATABASE`; the two concurrency classes stay live
  and will execute automatically when the test database vendor is PostgreSQL.
- Reduced-motion browser emulation, the actual final YouTube content, and final
  media crops remain owner acceptance items. Source-level reduced-motion and
  deferred-player behavior are implemented and covered where automatable.
- Figma MCP access remained quota-limited and no reconciliation is claimed.

## Heritage Court Render Studies — 2026-10-09

### Approved Scope and Provenance

- The owner requested six final Heritage Court render directions and their
  implementation on the website: Night Grid, Relief Contour, Evergreen Route,
  Relief / Noir, Forest / Noir, and Relief Joyfront.
- The source is the TreadJoy-owned Heritage Court Blender model with original
  procedural materials. Relief Joyfront adds the original procedural Joy Step
  mascot to a sky-blue permanent vamp; it does not replace the fixed TreadJoy
  badge.
- Private 3840x2160 16-bit PNG masters remain under the ignored design tree.
  The public static files are new 1600x900 and 960x540 WebP derivatives. They
  contain no EXIF, XMP, XML, IPTC, or comment metadata and are individually
  hashed in `docs/release-content-inventory.json`.

### Homepage Treatment

- One shared semantic partial renders in both deployment modes. This keeps the
  imagery, alt text, source sets, and render-only qualification identical while
  allowing the heading and destination link to remain mode-appropriate.
- The section is a near-black editorial contact sheet, not a generic product
  card grid. Its asymmetric 12-column composition uses the established sky,
  gold, background, typography, and spacing tokens without adding a new global
  visual system.
- All six figures have meaningful alt text, explicit intrinsic dimensions,
  responsive 960/1600 source sets, asynchronous decoding, and lazy loading.
  Figures are noninteractive; the sole section action is an ordinary text link.
- Copy calls the images visual studies and explicitly states that they do not
  prove production attachment mechanics, manufacturing readiness, or current
  availability. No price, inventory, engineering, or sale claim was added.
- Commerce links to the existing compatibility explanation. Research links to
  the existing survey so the gallery supports the current learning loop.

### Release Boundary

- The new assets pass the release-content command's per-asset checks in both
  modes. The command still fails closed on the existing
  `homepage-development-media` and `pending-social-links` surfaces; this gallery
  does not make the complete homepage or either deployment release-ready.

### Verification

- Native and 25-percent visual reviews passed for all six master renders; Night
  Grid is grid-free, Relief Contour remains legible, and Joy Step stays readable
  on both shoes without replacing the fixed TreadJoy badge.
- Browser verification passed at 390x844, 768x1024, and 1440x900. The gallery
  uses one, two, and asymmetric 12-column arrangements respectively, has no
  horizontal overflow, and retains a visible keyboard focus indicator.
- The complete local `web.core` suite passed all 112 tests in commerce and all
  112 in research, with 23 and 4 intentional mode/vendor skips respectively.
- Django checks in both modes, migration-drift detection, Python compilation,
  diff whitespace validation, image/inventory equality, and the strict frontend
  audit pass. PostgreSQL-backed CI/staging validation remains a launch gate.
