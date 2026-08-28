# TreadJoy Homepage Acceptance Scripts

Historical evidence snapshot: browser evidence was captured on 2026-08-18;
the operational script version was last updated at base commit
`a046d47d1b8b639c7fe34def214f803a28d01616` on 2026-08-27. Re-run every script
against the current release candidate before owner acceptance.

These scripts are for final owner acceptance. On 2026-08-18, agent-controlled
Chrome preflight passed the five target widths in both modes, the interactive
navigation checks, research waitlist submissions, and commerce-route isolation.
That evidence does not replace owner judgment of composition, motion preference,
final media, or launch suitability.

## Agent Chrome Preflight Record

- Environment: Chrome extension runtime on macOS, 2026-08-18.
- Viewports: 360×800, 430×932, 768×1024, 1280×800, and 1536×960.
- Modes: isolated commerce on port 8000 and isolated research on port 8001.
- Passed: no horizontal overflow or console errors; correct mode hierarchy and
  utility isolation; desktop disclosures/search; mobile menu/accordion/body
  lock/focus containment/Escape; inline waitlist validation, valid signup,
  normalized duplicate, and source attribution; full research survey
  completion; commerce-only research routes not found; working commerce
  Men/Women/Sale/How It Works/Bag destinations.
- Unconfigured video passed the no-iframe placeholder check. A test-only
  configured video also passed the user-initiated, one-iframe,
  `youtube-nocookie.com`, responsive 16:9, and accessible-title checks. The
  actual approved final video still requires owner review in steps 9 and 10.
- Reduced-motion browser emulation and the subjective final visual review remain
  pending owner checks.

## Safe Local Setup

Use separate commerce and research environments and databases. Never point the
research process at the commerce database merely to simplify testing.

Before starting each server, verify the active mode without exposing secrets:

```bash
TREADJOY_ENVIRONMENT=local TREADJOY_INGRESS=direct .venv/bin/python manage.py shell -c "from django.conf import settings; print(settings.TREADJOY_MODE, settings.DATABASES['default']['NAME'], hasattr(settings, 'STRIPE_SECRET_KEY'))"
```

Expected commerce output: `commerce`, the commerce database name, and `True`.

Expected research output: `research`, a different research database name, and
`False`. Stop immediately if research prints the commerce database name or
`True` for Stripe configuration.

With the correct environment active, start commerce on port 8000 or research
on port 8001:

```bash
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

```bash
.venv/bin/python manage.py runserver 127.0.0.1:8001
```

Inspect each mode at 360×800, 430×932, 768×1024, 1280×800, and 1536×960.

## Commerce Acceptance

Purpose: confirm that the homepage communicates the intended brand hierarchy,
routes visitors into a usable storefront, and contains no research conversion.

Setup: start the isolated commerce deployment on port 8000, use a guest browser
session, and keep developer tools available for the video and responsive checks.

1. Start commerce mode, open `/`, and confirm the deployment before interacting.
   - Expected: the mode probe reports `commerce`, Stripe test configuration is
     present, the homepage returns normally, and no real payment is initiated.
   - Failure signs: the research database/mode is active, Stripe production data
     is present, the page errors, or the browser redirects directly to checkout.

2. Verify the hero hierarchy.
   - Expected: a drops/events announcement, sticky solid header, campaign hero,
     and `Shop Men →` / `Shop Women →` hero actions.
   - Failure signs: transparent-over-media navigation, research-first copy, a
     waitlist action, or a missing announcement bar.

3. Verify Men navigation from the hero, editorial gateway, desktop disclosure,
   and mobile accordion.
   - Expected: every primary Men link reaches `/products/?audience=men`; the
     compact disclosure exposes usable Shoes and Accessories links; hover,
     focus, click, outside click, and Escape produce coherent open/close states.
   - Failure signs: a destination is unreachable, `aria-expanded` disagrees with
     visibility, the first link is sacrificed to toggle the menu, or focus is
     trapped in a closed disclosure.

4. Repeat the preceding navigation checks for Women.
   - Expected: primary links reach `/products/?audience=women`, and the compact
     desktop/mobile category disclosures behave like Men.
   - Failure signs: Men filters remain active, the destination errors, or the
     disclosure is unavailable to keyboard or touch users.

5. Activate Sale from desktop and mobile navigation.
   - Expected: `/products/?sale=1` loads with a `Sale` heading and no server
     error; Sale remains a direct destination rather than an empty dropdown.
   - Failure signs: dead link, unrelated catalog state, checkout initiation, or
     a disclosure with no real sale structure.

6. Activate How It Works from navigation and the homepage modular section.
   - Expected: `/how-it-works/` loads, and the homepage shows Tongue, Logo, Sole,
     Outer Shell, Back Panel, and Laces in domain display order.
   - Failure signs: missing/duplicated parts, unsupported compatibility claims,
     a broken destination, or a product-grid presentation.

7. Verify video behavior.
   - Expected with no configuration: an honest development placeholder and no
     iframe. With an approved valid configuration: one button before play, no
     eager player request, then one titled responsive 16:9 iframe sourced only
     from `www.youtube-nocookie.com` after activation.
   - Failure signs: autoplay, eager/duplicate iframe, another host, missing
     title, overflow, or playback before deliberate user action.

8. Review the lifestyle, community, impact, and roadmap sections in order.
   - Expected: the brand story remains scannable; every unapproved image, claim,
     relationship, statistic, date, and milestone is clearly a placeholder.
   - Failure signs: invented evidence, generic stock/AI imagery presented as
     final, broken heading order, or unsupported environmental/social claims.

9. Search the rendered homepage, header, mobile navigation, and footer for
   `waitlist`.
   - Expected: no waitlist text, link, form, or conversion panel appears.
   - Failure signs: any waitlist reference, hidden waitlist form, or form posting
     to `/`.

10. Judge the survey hierarchy.
    - Expected: Survey is available only as a subordinate discovery link; Men,
      Women, shopping, and brand storytelling dominate commerce mode.
    - Failure signs: survey copy replaces a commerce CTA, appears in the hero,
      or competes with the final shopping conversion.

11. Test the full-screen navigation and page at 360×800, 430×932, 768×1024,
    1280×800, and 1536×960.
    - Expected: large touch rows, working Men/Women accordions, Account inside
      the menu, explicit close button, Escape support, focus containment, body
      scroll lock, no horizontal page scroll, readable controlled overlaps, and
      a non-clickable social-links placeholder. The six-part grid changes from
      one to two to three columns without cramped copy.
    - Failure signs: background scroll, focus escaping behind the overlay, fake
      `#` social links, clipped headings, stretched buttons, or placeholders
      escaping their sections.

12. Verify commerce remains usable from the homepage.
    - Expected: Search opens and focuses its labeled field; Bag reaches `/cart/`
      and renders `Your Cart`; category and Sale destinations load without a
      server error; the cart-count badge appears when count is greater than zero.
    - Failure signs: disabled commerce utilities, a research redirect, missing
      cart route, broken query filtering, or an incorrect count state.

13. Enable the operating system/browser reduced-motion preference and repeat
    disclosure, menu, hover, video, and button checks using keyboard only.
    - Expected: content and interactions remain usable; decorative transitions
      are effectively removed; focus remains visible and logical.
    - Failure signs: hidden content, required animation, lost focus, inaccessible
      open/close state, or a continually spinning control without a readable
      loading label.

## Research Acceptance

Purpose: confirm that research mode prioritizes learning and relationship
building, persists valid test responses, and cannot expose order-taking
capability even through crafted navigation.

Setup: start the isolated research deployment on port 8001 with a separate
database, blank Stripe environment variables, and a unique test email address.

1. Start research mode, open `/`, and confirm the deployment.
   - Expected: the mode probe reports `research`, the database differs from
     commerce, Stripe settings are absent, and the homepage returns normally.
   - Failure signs: the commerce database is active, any Stripe setting exists,
     startup accepts a Stripe credential, or the page exposes a payment route.

2. Verify Join the Waitlist is prominent.
   - Expected: research announcement, `Join the Waitlist →` as the primary hero
     action near the top and a clearly labeled inline form below the brand story.
   - Failure signs: waitlist is footer-only, Shop language replaces it, or the
     hero action opens an unrelated page.

3. Verify Take the Survey is prominent.
   - Expected: it is the secondary hero action, appears in the announcement and
     closing context, and reaches the survey welcome flow.
   - Failure signs: dead link, commerce wording, or survey content is missing
     from the research hierarchy.

4. Test waitlist submission with the unique test email.
   - Action: first submit a malformed email, then a valid mixed-case email, then
     the same email again with different capitalization.
   - Expected: malformed input stays inline with an associated field error and
     `aria-invalid=true`; valid input shows `Joining…`, prevents a second click,
     redirects to `/#home-waitlist`, and shows success; the duplicate reports
     already-on-list and leaves exactly one normalized row.
   - Failure signs: server error, lost first name, duplicate row, missing CSRF,
     generic unassociated error, overwritten attribution, or commerce redirect.

   Verify the stored source in a research-environment shell:

   ```bash
   .venv/bin/python manage.py shell -c "from web.waitlist.models import WaitlistSignup; print(WaitlistSignup.objects.order_by('-created_at').values('email', 'source').first())"
   ```

   - Expected: the normalized test email appears once and `source` is `homepage`.
   - Failure signs: blank source or `waitlist_page` for an email first created on
     the homepage.

5. Complete the survey using clearly marked test answers.
   - Action: start at `/survey/`, answer all five questions, and submit the final
     step once.
   - Expected: each valid step advances in order, the final step reaches the
     Thank You page, and exactly one `SurveyResponse` contains the submitted
     values for the current guest session.
   - Failure signs: skipped prerequisite steps, lost answers, duplicate response,
     server error, or any purchase language/control in the flow.

6. Verify purchasing is not exposed across the homepage, mobile menu, footer,
   survey, waitlist, product preview, and account surfaces.
   - Expected: no Bag/Cart, Orders, Checkout, Add to Cart, price-led purchase CTA,
     or Stripe-facing control appears; Men/Women gateways say `Explore`.
   - Failure signs: any purchase action, `Shop` hero language, order history, or
     a control capable of creating a commerce record.

7. Attempt each commerce-only path directly in the address bar:
   `/cart/`, `/orders/checkout/`, and `/orders/stripe/webhook/`.
   - Expected: each returns a Django not-found response.
   - Failure signs: redirect, cart rendering, checkout view, webhook response,
     or any route resolution.

8. Confirm the preceding direct attempts fail closed in authoritative state.
   - Expected: the orders/cart apps and models are not registered, Stripe is not
     imported or configured, and no order/payment/cart row can be created.
   - Failure signs: an Order model is available, Stripe initializes, a commerce
     URL reverses, or a crafted request changes commerce state.

9. Verify brand and storytelling content remains intact.
   - Expected: brand statement, Men/Women preview gateways, six modular parts,
     lifestyle, video, community, impact, goals, and footer appear in the same
     coherent order as commerce without implying availability.
   - Failure signs: missing story sections, a product grid, invented claims,
     unsupported dates, or purchase-oriented copy.

10. Test the research page and full-screen navigation at 360×800, 430×932,
    768×1024, 1280×800, and 1536×960.
    - Expected: no overflow; Survey/Waitlist/How It Works/Story hierarchy;
      touch-friendly rows; focus containment; body lock; Escape and explicit
      close; honest social/media placeholders.
    - Failure signs: cart/order utilities, inaccessible menu state, focus escape,
      clipped content, unreadable overlap, or fabricated links.

11. Repeat video, placeholder, keyboard-only, and reduced-motion checks from
    Commerce Acceptance steps 7, 8, and 13.
    - Expected: research mode preserves the same accessible branded behavior
      while never introducing a commerce capability.
    - Failure signs: eager autoplay, unlabeled control, required animation,
      final-looking unsupported content, or any purchase route/control.

## Cleanup and Reset

1. Delete only the waitlist and survey rows created with the clearly identified
   owner-test email/answers from the isolated research database; do not run this
   against commerce or production data.
2. Stop the research server and remove its isolated temporary database if one
   was created solely for acceptance.
3. Clear the guest browser session or use a fresh private window before a repeat
   survey run so session-draft state cannot affect the result.
4. Remove test-only YouTube environment values and restore the intended blank or
   approved configuration.
5. Do not delete commerce cart/order data unless it was created deliberately in
   the isolated test database and the exact rows are known.

## Acceptance Record

Record the browser/version, operating system, date, mode, viewport, pass/fail,
and screenshot reference for each owner run. Do not mark the homepage accepted
until every failure is resolved or explicitly approved as a documented
exception.
