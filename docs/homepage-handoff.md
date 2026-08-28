# TreadJoy Homepage Stage Handoff

Historical snapshot: evidence captured on 2026-08-18 at commit
`6a8c2b10ea9df7409f9aa16064cd737256975599`. Re-run the acceptance checks
against the current release candidate; this document is not current launch
approval.

Status: implementation and agent-controlled Chrome preflight complete; owner
acceptance and Figma reconciliation pending.

This document tracks the 20 deliverables required by the approved homepage
prompt. It is deliberately explicit about missing evidence and must not be read
as acceptance of the wider storefront.

## 1. Files Changed

Configuration and documentation:

- `.env.example`
- `Shoes/settings.py`
- `docs/homepage-acceptance.md`
- `docs/homepage-handoff.md`
- `docs/homepage-implementation-decisions.md`

Templates and shared chrome:

- `templates/base.html`
- `templates/home.html`
- `templates/partials/header.html`
- `templates/partials/footer.html`
- `templates/waitlist/join_waitlist.html`

Styles and interactions:

- `static/css/home.css`
- `static/css/style.css`
- `static/js/home.js`
- `static/js/navigation.js`

Backend and tests:

- `web/core/views.py`
- `web/core/youtube.py`
- `web/core/tests/test_homepage.py`
- `web/core/tests/test_youtube.py`
- `web/products/tests/test_catalog.py`
- `web/cart/tests/test_cart.py`
- `web/cart/tests/test_preorders.py`
- `web/orders/tests/test_inventory.py`
- `web/orders/tests/test_preorder_allocation.py`
- `web/waitlist/forms.py`
- `web/waitlist/services.py`
- `web/waitlist/views.py`
- `web/waitlist/tests.py`

## 2. Homepage Architecture Implemented

One shared Django template renders announcement/header chrome followed by:

1. Campaign hero.
2. Concise brand statement.
3. Men/Women editorial gateways.
4. Six authoritative modular component types.
5. Lifestyle editorial band.
6. Deferred YouTube video/livestream area.
7. Community section.
8. Positive-impact section.
9. Brand roadmap.
10. Mode-specific closing conversion.
11. Shared footer.

No product-price grid, product card, quantity control, or add-to-cart control is
rendered on the homepage.

## 3. Design Decisions

- The approved Fredoka/DM Sans, blue/gold, warm stone, muted cool surface, and
  soft near-black token system remains authoritative.
- Bright color is concentrated in gateways and conversion moments rather than
  saturating every section.
- Composition uses irregular radii, controlled overlap, asymmetric editorial
  grids, large responsive display type, and one dark community contrast band.
- Mobile retains side-by-side Men/Women gateways but uses one-column modular
  items until 480px; text-heavy editorial regions are not forced into cramped
  columns.
- Tablet hero type is capped to preserve a balanced three-line headline at the
  768px breakpoint.
- No scroll-entry reveal or parallax was added without browser evidence.
- All missing media and unapproved claims remain explicit development
  placeholders.

Detailed rationale is recorded in `homepage-implementation-decisions.md`.

## 4. Backend and Supporting Architecture

- `GET /` renders the homepage in both modes.
- Research `POST /` validates the inline waitlist form, creates idempotently,
  records `source="homepage"`, and uses post/redirect/get.
- Commerce `POST /` returns `405 Method Not Allowed` and cannot create a signup.
- The shared waitlist service is also used by `/waitlist/join/`, where new
  records use `source="waitlist_page"`.
- The modular explainer reads the first six active domain `PartType` records.
- Optional YouTube configuration accepts only a syntactically valid ID or a
  supported HTTPS YouTube URL and emits only a `youtube-nocookie.com` embed URL.
- Blank/invalid YouTube input renders a static placeholder with no iframe.
- Both waitlist forms use Django's inline validation instead of the browser's
  inconsistent native email-validation bubble.
- No migration or marketing-content model was added.

## 5. Commerce-Mode Behavior

- Primary navigation is Men, Women, Sale, and How It Works.
- Search, Account, and Bag utilities remain available.
- Hero and closing actions prioritize Men/Women shopping.
- Waitlist content and footer navigation are absent.
- Survey remains subordinate in shared/footer discovery.

## 6. Research-Mode Behavior

- Header emphasizes Survey, Waitlist, How It Works, and Story.
- Hero prioritizes Join the Waitlist and Take the Survey.
- Men/Women links use `Explore` preview language.
- Inline waitlist form and contextual survey repetition replace the shopping
  conversion.
- Cart, orders, checkout, Stripe configuration, and purchase controls remain
  fail-closed.

## 7. Automated Tests Added or Modified

- Commerce homepage content and waitlist absence.
- Research homepage hierarchy and preview language.
- Commerce `POST /` rejection.
- Valid, invalid, normalized, and duplicate research submissions.
- Homepage/waitlist source attribution.
- Six authoritative modular types.
- Homepage-only static asset loading.
- Deferred valid-video control and invalid-video fallback.
- YouTube ID/URL allowlist and privacy-enhanced embed construction.
- Existing waitlist-page behavior through the shared service.
- Real deployment-process mode assertions rather than impossible mixed
  URL-configuration overrides.
- Mode-aware catalog expectations and research-preview assertions.
- Commerce-only cart test-module discovery in commerce mode, with the fail-closed
  boundary covered separately in research.
- PostgreSQL-only execution markers on row-locking concurrency tests; all other
  commerce tests still run against the isolated SQLite verifier.

## 8. Commands Run

Representative commands:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test web.core.tests.test_deployment_modes
.venv/bin/python manage.py test web.core.tests.test_youtube
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python -m compileall -q Shoes web
git diff --check
```

Isolated SQLite settings were used for database-writing tests because the local
PostgreSQL role cannot create a test database. Separate environment overrides
started the test process in real commerce and research modes.

## 9. Command Results

- Focused homepage/waitlist coverage passed in both modes: 14 tests in commerce
  and 14 tests in research, including mode-specific skips.
- Both real-mode Django system checks passed.
- Five deployment-boundary subprocess tests passed.
- Three YouTube parser/security tests passed.
- Migration drift: no changes detected. The command warned that sandboxed
  PostgreSQL history inspection was unavailable.
- Python compilation and diff whitespace checks passed.
- `static/js/home.js` and `static/js/navigation.js` passed native
  JavaScriptCore syntax parsing.
- Static contrast calculations corrected muted-on-blue text and dark-surface
  focus rings to meet the relevant WCAG thresholds.
- The broad commerce SQLite run passed all 123 discovered tests with eight
  intentional opposite-mode/PostgreSQL-only skips.
- The broad research SQLite run passed all 61 discovered tests with eight
  intentional commerce-only skips.

## 10. Browser and Viewports Tested

Agent-controlled Chrome inspected commerce and research at 360×800, 430×932,
768×1024, 1280×800, and 1536×960 on 2026-08-18.

- Both modes matched viewport width with no horizontal overflow and produced no
  console error or warning.
- Commerce contained no waitlist content at any width. Desktop disclosures and
  search, working Men/Women/Sale/How It Works/Bag destinations, mobile
  navigation/accordion, body scroll lock, focus containment, outside-click
  dismissal, and Escape closure behaved as intended.
- Research contained no cart/order utilities. Inline and standalone malformed
  emails rendered associated errors and `aria-invalid`; valid and normalized
  duplicate submissions preserved a single `source="homepage"` record.
- The full five-step research survey reached its thank-you page and persisted
  exactly one response containing the supplied test values.
- Direct research requests for `/cart/`, `/orders/checkout/`, and
  `/orders/stripe/webhook/` rendered Django not-found pages.
- The unconfigured video rendered the honest placeholder with zero iframes.
- A test-only configured video rendered zero iframes before activation and one
  titled, responsive 16:9 `youtube-nocookie.com` iframe after activation.
- The 768px hero headline was refined after inspection and rechecked in both
  modes.

## 11. Browser Checks Not Completed

- A true browser/operating-system reduced-motion preference was not available
  through the connected Chrome control surface; the matching source-level media
  query remains implemented and requires owner confirmation.
- No approved final YouTube video, poster, or title exists, so final content and
  real playback quality could not be judged even though the configured component
  behavior passed with test data.
- Final asset crops, intrinsic dimensions, responsive source selection, loading
  behavior, and final alt text cannot be checked until approved media exists.
- The owner still needs to make the subjective brand/composition judgment and
  may perform exhaustive focus traversal through every page link.
- Figma comparison was impossible because the connected Starter workspace had
  exhausted its MCP quota.

## 12. Commerce Manual Acceptance Procedure

The numbered procedure, expected outcomes, and failure signs are in
`homepage-acceptance.md` under **Commerce Acceptance**.

## 13. Research Manual Acceptance Procedure

The numbered procedure, expected outcomes, direct-commerce-path attempts, and
failure signs are in `homepage-acceptance.md` under **Research Acceptance**.

## 14. Placeholder Imagery and Assets

- Hero campaign media, including a deliberate mobile focal point.
- Men editorial/lifestyle media.
- Women editorial/lifestyle media.
- Modular-shoe explanatory imagery or approved diagrams.
- Lifestyle band photography.
- Video poster, final YouTube ID/URL, and final accessible title.
- Authentic community/activity photography.
- Approved community, impact, and roadmap evidence/content.
- Approved social URLs.
- Optional compact-dropdown campaign media.
- Final intentional alt text, intrinsic dimensions, responsive source sets,
  formats, usage rights, and asset provenance for every supplied image.

## 15. Missing Final Content

- Approved hero, Men, Women, lifestyle, community, modular-system, impact, and
  roadmap media.
- Final YouTube video or livestream ID/URL, poster, and accessible title.
- Approved community relationships, events, collaborators, impact evidence,
  roadmap milestones, and any dates or quantitative claims.
- Approved social profile URLs and any optional dropdown campaign content.
- Final media rights/provenance records and intentional meaningful/decorative
  alt-text decisions.

## 16. Known Limitations

- Current image logo is retained by owner choice and remains a known
  premium-positioning limitation.
- Placeholders prevent final crop, loading, and alt-text verification.
- No PostgreSQL test database could be created by the configured role.
- The two row-locking concurrency classes were therefore skipped locally; they
  remain enabled automatically for PostgreSQL test runs.
- Reduced-motion emulation, final-media validation, and owner acceptance remain
  outstanding.
- Figma MCP quota access remains unavailable.

## 17. Intentional Deviations From `AGENTS.md`

- Figma-before-code was temporarily waived by explicit owner approval because
  the connected Starter workspace had exhausted its MCP quota. Browser control
  later became available and the implemented modes were preflighted in Chrome.
- Social links are honest non-interactive placeholders until real URLs are
  approved, rather than fabricated links.
- Responsive `<picture>` assets, intrinsic media dimensions, eager hero
  loading, and final alt text cannot be implemented until approved media exists.

No framework, styling library, animation dependency, AI-generated customer
imagery, invented claim, payment relaxation, or long-lived mode branch was
introduced.

## 18. Intentional Deviations From Figma

No comparison is possible. The Figma file was created, but MCP quota exhaustion
prevented inspection or composition. Implementation decisions are recorded so
the file can later be reconciled accurately.

## 19. Figma Work Completed

No frames, components, variables, or styles were changed. The intended file was
preserved at:

<https://www.figma.com/design/VPcb3JwUkrp3Yrd85tPjYp>

The connected account and file were identified, but the Starter-plan MCP quota
prevented inspection or writes. The owner's temporary gate override allowed the
code implementation and Chrome verification to continue.

## 20. Figma Work Still Requiring Synchronization

Figma does not yet accurately represent the verified homepage. Required work:

- Archive, Foundations, Components, Commerce, and Research pages.
- Announcement/header/footer and all homepage section components.
- Commerce and Research frames at 390px, 768px, and 1440px.
- Tokens, variants, states, and implemented responsive behavior.
- Implemented-page captures and explicit documentation of approved departures.
- Clear labels for abandoned explorations without deleting unrelated prior work.

Chrome preflight has passed, but final acceptance still requires owner review;
Figma reconciliation remains a deferred final design-record task when access
returns.
