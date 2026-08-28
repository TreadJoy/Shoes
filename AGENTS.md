# AGENTS.md

## 1. Product mission and current status

Shoes is the Django 5.2 application for **TreadJoy**, a public ecommerce business for modular shoes and accessories. The finished system will handle real customer accounts, personal information, inventory, orders, payments, shipping, returns, and operational history. Treat every production-facing change as work on a real commercial system, not a class project, portfolio demo, or disposable prototype.

TreadJoy is pre-launch and still validating demand, positioning, and operations. It nevertheless has approved provisional launch policies recorded in this file. Those policies are authoritative until the project owner changes them; do not describe them as absent or silently replace them with generic ecommerce defaults.

Production quality means the system is:

- correct and auditable for money, inventory, orders, customers, and staff actions;
- secure by default and conservative with personal data;
- reliable under retries, duplicate events, concurrency, and partial failure;
- accessible to WCAG 2.2 Level AA, responsive, performant, SEO-friendly, and trustworthy;
- maintainable by a small team using conventional Django patterns;
- operationally supportable through documented deployment, monitoring, backup, recovery, and incident procedures; and
- designed to learn from real customer behavior without manufacturing claims or prematurely building enterprise complexity.

The backend is intended to become the business's single source of truth. Judge architecture by whether it supports faster, more accurate, and auditable business decisions—not merely whether it resembles a generic ecommerce stack.

### Source-of-truth order

When sources disagree, investigate and use this order:

1. Reproduced running behavior.
2. Current source code.
3. Database schema and migrations.
4. Automated tests.
5. Current configuration.
6. Repository documentation, `PROJECT_PLAN.md`, `MISTAKES.md`.
7. This file.
8. Assumptions.

Document discrepancies instead of choosing whichever source is convenient. A model, template, route, or test file proves only that code exists; it does not prove the feature is complete or production-ready.

## 2. Collaboration and approval protocol

Work as a senior backend architect, product-minded technical co-founder, and—when relevant—senior product designer/frontend engineer.

- Teach while delivering: state what is changing, why, the tradeoffs, and exactly how to verify it.
- Work one explicitly agreed implementation step at a time. Complete and hand off that step, then wait for the project owner to say `next` before starting another roadmap task.
- Inspect the existing implementation before proposing or generating files. Prefer a focused extension over a parallel implementation.
- Ask before encoding or changing business policy, including pricing, discounts, inventory thresholds, shipping, fulfillment, cancellations, returns, refunds, order transitions, customer segments, retention, consent, staff permissions, or legal promises.
- Customer-facing behavior/design, cross-cutting schema or infrastructure work, and security/PII changes require explicit approval before editing unless the concrete change was already approved in the current task.
- Make technical recommendations that do not depend on business policy, explain material tradeoffs and opportunity cost, and prefer the smallest reversible solution.
- Give direct, respectful criticism when an idea is insecure, internally inconsistent, operationally expensive, difficult to validate, or unsupported by evidence. Do not invent objections merely for balance.
- Separate known facts, owner decisions, working hypotheses, recommendations, and unresolved questions.
- For consequential recommendations, use current primary or authoritative evidence, identify uncertainty, include the strongest reasonable counterargument, and state when another choice would be better.
- Never invent market data, legal conclusions, security guarantees, customer behavior, partnerships, impact claims, or competitor facts.

Maintain a learning loop where evidence is weak: define the hypothesis, choose a low-cost test, name the measurable signal and decision threshold, record the result, and update the product thesis or rule.

## 3. Approved product and launch decisions

These are approved decisions, not suggestions:

- Maintain one codebase and release commit for two independently configured deployments.
- Launch the public **research deployment first**. Launch commerce only after its security, legal, payment, inventory, fulfillment, and operational gates pass.
- Research mode cannot accept orders. It must not register checkout/order-taking routes, initialize Stripe, possess Stripe credentials, or create commerce records.
- Commerce and research deployments use separate PostgreSQL databases. The commerce database is authoritative for customers, inventory, orders, payments, and fulfillment; the research database contains only data required for research features.
- Use Cloudflare for DNS, TLS edge termination, proxy/CDN, WAF controls, and R2-backed public media. Run Django and PostgreSQL on managed origin infrastructure for launch. Cloudflare Containers are a future option, not the launch default.
- The owner confirmed on 2026-08-26 that `tread-joy.com` was purchased through Cloudflare as TreadJoy's intended base domain. Registration does not establish an active hostname, DNS records, TLS, origin, R2 custom domain, or email service; assign those separately in the deployment tasks. Do not store Cloudflare account, registrant, billing, credential, renewal, or screenshot data in the repository.
- Launch products are fixed, preconfigured shoe variants. Do not build a customer component configurator or sell standalone components at launch without a new approved scope.
- TreadJoy modularity means selecting interchangeable standardized components—not engraving, one-off fabrication, or customer-specific manufacturing. If configurable standard components are introduced later, do not classify the resulting product as final sale merely because the customer selected them.
- Finished `ProductVariant` stock and preorder allocations are the launch inventory authority. Component/BOM records describe compatibility and composition; they do not independently limit sellable stock until a later approved inventory design.
- Guest checkout remains available and customer accounts are optional. Guest carts, order access, and later account association must be secure and auditable.
- Entering hosted Stripe Checkout creates a **30-minute finished-SKU reservation**. Reservation creation must be atomic; expiration/cancellation releases it idempotently; confirmed payment commits it. A cart alone does not reserve inventory.
- Preorders collect full payment when ordered.
- Continue using Stripe-hosted Checkout. TreadJoy must never collect or store raw payment-card data.

`PROJECT_PLAN.md` distinguishes these approved targets from current implementation. Never present a planned invariant as already implemented.
`MISTAKES.md` is a auditable historical log that is to be updated by the working agent which maintains what actions have been attempted and failed

### Customer thesis

Treat this as a pre-validation beachhead hypothesis, not established customer truth:

- Primarily men aged 20–30 in Midwestern urban areas, initially represented by Detroit, Milwaukee, Chicago, Cleveland, and Pittsburgh.
- Median-to-above-median income for their age group; possible interests include art, LEGO, DIY, and fashion.
- Uses fashion for self-expression and owns several enjoyed pairs of shoes without necessarily identifying as a sneakerhead.
- Seeks casual streetwear sneakers for social occasions, nights out, dates, and travel.
- Expected core-shoe price position is approximately $90–$120.
- The differentiated promise is credible participation in local culture through real relationships with creators, events, independent shops, nonprofits, and third places—not generic city-themed marketing.
- Initial acquisition and validation should focus on local partners and communities rather than broad national advertising.

Do not turn inferred tastes, income, identity, or community affiliation into profile fields. Collect personal data only for an approved operational purpose.

### Fulfillment policy

The approved launch operating model is:

- Support stocked products and clearly identified preorders. The first run is expected to use preorders to reduce unsold-inventory risk.
- The project owner packs orders and tenders packages after receiving goods from the manufacturer.
- Ship only to addresses in the contiguous United States at launch.
- Customers pay for available shipping service levels and receive carrier tracking.
- Tender paid stocked-product orders by the end of the next business day; do not promise next-calendar-day shipment.
- Display a manufacturer-supported preorder shipping window before payment.
- Describe selected shipping speed as estimated carrier transit time beginning after carrier tender, not purchase time.
- If a preorder cannot ship in its stated window, notify the customer before the window expires and offer a recorded choice: accept the revised date or cancel for a full refund.
- Do not mix stocked and preorder products in one launch cart. Split fulfillment requires a later approved design.
- Cap preorder sales by the approved production allocation; supply is not unlimited.
- Send fulfillment failures and unusual problems to human review rather than making substitutions or automatic resolutions.
- Record exceptions, delays, consent, cancellation, refund, shipment, and tracking actions in order history.

The stocked-order cutoff, business-day holiday calendar, exact preorder date representation, supported carriers, shipping-rate source, and behavior when a customer does not respond to a delay remain unresolved. Obtain decisions before implementing them.

### Cancellation, return, and exchange policy

The approved launch policy is:

- Allow cancellation of stocked orders for a full refund, including outbound shipping, until carrier tender.
- Allow cancellation of preorders for a full refund until carrier tender, including after production begins. After tender, use the return policy.
- Accept eligible return requests within 30 calendar days after confirmed delivery.
- Require items to be unworn outdoors, undamaged, and accompanied by original packaging; indoor fit testing is allowed.
- Offer one free size exchange per order within the contiguous United States, subject to inventory. TreadJoy pays return and replacement shipping. If no suitable replacement exists, offer a refund.
- For preference returns, the customer pays return shipping and original outbound shipping is nonrefundable.
- For defective, damaged, or incorrect items, TreadJoy pays return and replacement shipping and offers replacement or a full refund.
- Issue approved refunds to the original payment method after inspection. Approve the refund or explain the decision within five business days of receiving the return.
- Do not charge restocking fees or make automatic substitutions.
- Require human review for cancellations, returns, exchanges, inspections, and refunds at launch; record every decision and state change.
- Inspect returned modular configurations at component level. Return only complete, safe, undamaged, resellable components to inventory; quarantine the rest.

Do not create final-sale categories or policy exceptions without explicit approval and clear pre-purchase disclosure.

## 4. Actual technical architecture

- **Backend:** Django 5.2 project in `Shoes/` with domain apps under `web/`.
- **Rendering:** server-rendered Django templates. There is no public API or SPA architecture.
- **Frontend:** semantic HTML, centralized CSS/design tokens, and small vanilla JavaScript enhancements.
- **Database:** PostgreSQL is the authoritative transactional store. Correctness relies on transactions and row locking in high-risk workflows.
- **Authentication:** Django authentication plus django-allauth account flows. Google/social authentication is removed for now; username login and optional email verification remain, with production hardening still required before commerce launch.
- **Catalog:** `Product`, finished `ProductVariant` (expanded selling/compare-at price fields), compatibility groups, parts, part variants, and product BOM/component relationships. Active catalog pricing is read from variants with a one-release legacy fallback during migration.
- **Cart:** database-backed carts identified by exactly one authenticated user or nonblank guest session. Principal constraints, transactional mutations, and sign-in merge with availability notices are implemented in `web/cart/services.py`.
- **Checkout/payments:** hosted Stripe Checkout with signed webhooks, server-side attempts and immutable quote/BOM facts, one-active-attempt-per-cart idempotency, 30-minute finished-SKU/preorder reservations, Stripe-collected shipping addresses, and bounded provider audit fields. One retrieved-Session reconciler creates paid/review orders only after exact server-side verification. PostgreSQL/provider/operations acceptance remains a commerce launch gate.
- **Orders:** durable orders are created only for reconciled paid payments or financially meaningful review exceptions. They retain line/preorder/BOM snapshots, payment/refund records, status events, shipments, and transactional inventory allocation; the broader Phase 5 historical-address/state-machine hardening is still pending.
- **Email:** console backend in development; no production transactional provider is configured.
- **Static/media:** local development uses project static files and local media. Public-environment settings use manifest static storage and an R2-backed public-media configuration, but no live R2 bucket, custom domain, CDN path, or origin static service has been provisioned or verified.
- **Operations:** PostgreSQL application CI, dependency auditing, full-history secret scanning, and a fail-closed production-settings contract are implemented. No production deployment definition, health/readiness endpoints, monitoring, backup automation, restore drill, or rollback runbook exists yet.
- **Optional systems:** no required Redis, Celery, search service, or generalized CMS. Add them only in response to measured need.

### Deployment modes

`TREADJOY_MODE` must be explicitly set to `commerce` or `research`; invalid or missing production configuration must fail closed.

For developer convenience only, a bare `python manage.py runserver` invocation
supplies local defaults and uses SQLite when no database variables are explicitly
provided. Migrations, tests, CI, and every public deployment still require the
explicit configuration described above.

- Commerce registers `cart` and `orders`, requires valid Stripe configuration, and uses the commerce database.
- Research excludes commerce apps/routes and rejects Stripe credentials. Shared presentation must not provide a crafted-request path around this boundary.
- Build both modes from the same tested release commit. Do not create long-lived commerce/research branches.

### Repository map

- `Shoes/settings.py`: environment-driven Django and deployment-mode configuration.
- `Shoes/urls.py`: mode-aware root routing.
- `web/core/`: homepage and general content pages.
- `web/products/`: products, variants, compatibility/BOM data, availability, and preorder batches.
- `web/cart/`: authenticated and guest carts plus cart context.
- `web/orders/`: checkout, Stripe webhooks, payments/refunds, order history, shipment, and inventory allocation.
- `web/accounts/`: account-related views/forms layered around django-allauth.
- `web/survey/` and `web/waitlist/`: anonymous survey responses and normalized, source-controlled waitlist relationship flows.
- `templates/`: shared and app-namespaced Django templates; shared chrome belongs in `templates/base.html` and `templates/partials/`.
- `static/`: CSS, JavaScript, and committed public assets.
- `media/`: local development uploads. Do not commit customer uploads or unapproved development imagery.
- `.github/workflows/`: separate PostgreSQL application CI, dependency-audit, and full-history secret-scanning workflows.
- `PROJECT_PLAN.md`: evidence-based current-state assessment and dependency-ordered implementation roadmap.

The former root-level `web/views.py`, `web/models.py`, `web/tests.py`, comment-only `web/admin.py`, and unused root `web/apps.py` legacy scaffolds were removed in Phase 1. Active behavior belongs to the domain apps above; confirm references and both deployment modes before removing any future legacy path.

## 5. Engineering and backend standards

- Follow Django conventions and keep changes in the app that owns the domain behavior.
- Preserve existing URL namespaces unless a planned migration explicitly changes them.
- Keep views thin: parse the request, enforce authentication/authorization, call domain services/forms, and render or redirect.
- Put reusable validation in forms, models, or domain services according to responsibility. Never rely on browser validation for a security or business invariant.
- Keep business rules out of templates, JavaScript, scattered signals, and ad hoc admin actions.
- Put nontrivial workflows in explicit service/domain functions with documented inputs, outputs, invariants, transactions, and tests.
- Do not duplicate money, inventory, availability, state-transition, or permission logic. One authoritative implementation must serve views, webhooks, admin, and future jobs.
- Use transactions for multi-record state changes. Lock authoritative rows before inventory, reservation, payment, refund, or state-transition decisions that can race.
- Design retryable operations to be idempotent. Persist provider/request identifiers with appropriate uniqueness constraints.
- Handle expected failures with actionable user/staff messages and durable operational state. Do not convert financially meaningful failures into logs alone.
- Use `select_related`/`prefetch_related` deliberately and avoid hidden N+1 queries in catalog, order, and admin pages.
- Do not introduce new frameworks, services, or packages without a concrete requirement, maintenance/security review, alternatives, and owner approval where required.
- Preserve server-side rendering and progressive enhancement. Do not introduce React, Vue, a SPA, or a general API without an approved requirement.

## 6. Database and domain standards

The schema should communicate the business directly through names, relationships, constraints, and comments—not require reverse-engineering application code.

- PostgreSQL is authoritative. Caches, search indexes, analytics, queues, Stripe, and Cloudflare are derived or external systems, never the only record of business state.
- Use descriptive model/field/constraint/index names and explicit related names. Add database comments where a business distinction would otherwise be ambiguous.
- Enforce stable invariants with `CheckConstraint`, `UniqueConstraint`, foreign keys, and non-null fields. Keep request-dependent or evolving policy in services.
- Index actual query and operational access paths; do not add speculative indexes without query evidence.
- Use `Decimal` for application money and fixed-precision database fields. Convert to integer minor units only at provider boundaries. Never use binary floats for money.
- Prices and totals are server-authoritative. Recalculate from active variants and approved adjustments; never trust browser/session totals or overwrite expected order amounts with provider payload values without reconciliation.
- Preserve historical truth. Order lines, customer/shipping details, prices, tax, shipping, discounts, currency, fulfillment promises, and policy-relevant facts must be snapshotted where later catalog/account edits would change their meaning.
- Do not cascade-delete completed financial or fulfillment history through customer/catalog deletion. Use appropriate protection, anonymization, retention, or snapshot behavior after policy approval.
- Treat important transitions as explicit state machines. Record actor, source, prior/new state, reason, timestamps, and external identifiers in append-only history where appropriate.
- Create and commit migrations for model changes. Do not edit an already-applied migration merely to improve it; add a corrective migration.
- Review migration locking, backfill, reversibility, and rollback for production data. Separate deploy-safe schema expansion from destructive cleanup when needed.
- Use least-privilege database roles. Production runtime roles should not own the database; migrations and backup/restore use separately controlled privileges.

## 7. Ecommerce invariants

### Products and inventory

- A sellable launch SKU is an active finished `ProductVariant` with an authoritative price and availability state.
- Size and color options must map to real variants; do not accept arbitrary client-provided variant attributes.
- Sold-out products remain discoverable but cannot be purchased. Preorders must be visibly and semantically distinct from stocked products.
- Component compatibility/BOM data cannot reduce or increase launch availability until component-level inventory authority is explicitly approved.
- Inventory changes require reasoned, auditable adjustments. Never silently repair stock by editing counts without history.
- Use atomic reservations and row locks to prevent overselling. Reservation expiry, payment confirmation, replay, and release must remain idempotent.

### Carts

- A cart belongs to exactly one authenticated customer or one guest session. Prevent unowned, multiply owned, or duplicate guest carts.
- Scope every cart lookup/mutation to the current principal. Mutations are POST-only and CSRF-protected.
- Validate active variant, fulfillment compatibility, quantity, and current availability on add/update and again at Checkout creation.
- Logging in or signing up must merge or associate carts according to an explicitly tested rule without exposing another session's data.
- Cart prices are display values, not permanent financial authority. Reprice during Checkout using current approved prices and clearly surface material changes.

### Checkout and payments

- Hosted Stripe Checkout is the payment boundary. Do not store card numbers, CVC, magnetic-stripe data, or equivalent sensitive authentication data.
- Create Checkout from a server-side order/quote snapshot and an atomic 30-minute SKU reservation. Use an idempotency key so retries cannot create duplicate orders, sessions, or reservations.
- Store and reconcile the expected amount, currency, order/session ownership, payment intent, and payment status. A signed event is authentic transport; it is not proof that its business fields match the order.
- Mark an order paid and commit inventory only from an eligible confirmed-payment state. Do not infer payment solely from a success redirect or a generic session-completed signal.
- Keep webhook signature verification, event uniqueness, transactional processing, replay safety, failure diagnostics, and alerting.
- Handle success, asynchronous success/failure, expiration, cancellation, refund, dispute/chargeback, duplicates, out-of-order delivery, and partial internal failure where applicable.
- Never log secrets or full sensitive provider payloads. Retain only data needed for reconciliation, audit, support, and an approved retention period.
- Do not enable automated tax collection until registrations/nexus treatment and product tax codes are confirmed with an appropriate advisor. Test-mode success is not legal or tax approval.

### Orders, fulfillment, and administration

- Orders are historical commercial records. Catalog/account changes must not rewrite what the customer bought, paid, was promised, or supplied at checkout.
- Centralize legal order transitions; use the same service from customer flows, webhooks, admin actions, and future jobs.
- Financial/provider identifiers and append-only history must be read-only in ordinary admin forms. Disable destructive deletion of material commerce records.
- Staff actions require explicit permissions, safe scopes, actor/reason audit, confirmation for destructive/financial actions, and useful exception queues.
- Customer and guest order views must enforce ownership using an authenticated relationship or short-lived/safely revocable signed access mechanism.
- Fulfillment, tracking, cancellations, returns, exchanges, inspections, and refunds must follow the approved policy and remain traceable.
- Send customer receipts and lifecycle messages only after authoritative state changes. Email delivery failure must not roll back a successfully recorded payment/order; it must create a retryable operational exception.

## 8. Security, privacy, and dependency standards

Security is a launch gate, not a cleanup phase.

### Secrets and configuration

- Never commit or print `.env`, Django secrets, Stripe keys/webhook secrets, OAuth credentials, database passwords, access tokens, customer data, or production payloads.
- Keep production, staging, and local credentials separate. Use the hosting platform's secrets store and least-privilege/restricted provider keys where available.
- If evidence suggests exposure, stop feature work, do not reproduce the value, notify the owner, rotate/revoke, review logs/history, and document containment.
- Production configuration must fail closed: `DEBUG=False`, explicit hosts/origins, secure cookies, HTTPS redirect, HSTS after validation, trusted proxy headers only from the managed Cloudflare/origin path, safe referrer policy, CSP, and non-console email.
- Never weaken CSRF, XSS escaping, clickjacking, session, or webhook-signature controls to make a flow easier.

### Authentication and authorization

- Enforce authorization server-side on every object and mutation. Authentication alone does not prove ownership or staff authority.
- Protect account creation, login, password reset, waitlist, survey, and sensitive actions against enumeration, brute force, and abuse using application and Cloudflare controls appropriate to measured risk.
- Define and test email verification, account recovery, session invalidation, admin MFA/access, and staff permission policy before commerce launch.
- Do not expose whether another person's account/order exists through status, message, timing, or identifier behavior when it can be avoided.

### PII, uploads, and logging

- Classify collected data, state its purpose, minimize it, restrict access, define retention/deletion, and include it in backup/restore and incident planning.
- Never collect demographic or behavioral fields merely because they might be useful later.
- Treat addresses, emails, survey responses, order data, IP/user-agent data, and provider payloads as sensitive according to context.
- Redact secrets, session identifiers, tokens, full addresses, and unnecessary payload fields from logs and monitoring.
- Validate uploads by type, size, and content; generate safe names; keep originals away from executable/static paths; strip unnecessary metadata where appropriate; and serve through controlled storage.
- Customer-facing imagery and copy require ownership/licensing/consent and factual approval. Do not ship test/customer-like photos or hidden EXIF metadata.

### Dependencies

- Keep runtime and development dependencies intentional, minimal, pinned/locked, and reproducible.
- Before adding/upgrading, review maintenance, license, transitive risk, release compatibility, operational cost, and whether the standard library/Django already meets the need.
- Run automated vulnerability and secret scanning in CI. Triage findings; do not blindly suppress or perform unsafe upgrades.

## 9. Frontend, brand, accessibility, and performance contract

Material changes require owner approval. Preserve the existing Django-template system, semantic HTML, CSS tokens, and minimal vanilla JavaScript.

### Brand foundation

- The homepage is a brand/storytelling surface, not a product-card catalog. It should communicate the product difference, people/community, and a clear path to shopping or relationship-building.
- Direction: bright, energetic, playful, sporty, street-art influenced, editorial, and youthful without feeling childish, chaotic, or untrustworthy for a $90–$120 purchase.
- Use bright color as an accent against calmer neutral surfaces; favor bold crops, expressive transitions, asymmetry, controlled overlap, and occasional near-black contrast sections over a generic card grid. Campaigns may add approved tokenized accents without redefining global semantic colors or reusable commerce UI.
- Core tokens: sky blue `#4CCBF0`, gold `#EDDC4F`, near-black around `#191919`, warm stone around `#E9E1D5`, and cool muted surface around `#DCE5E7`. Do not scatter one-off colors or use pure white as the default page background.
- Typography: Fredoka for expressive display/headlines and DM Sans for body/interface text. Do not add paid fonts or extra global families without approval.
- Use Title Case as the default for headlines/navigation, mixed weights for hierarchy, and deliberately readable line lengths. Purposeful outlines, rotation, layering, or oversized display type are allowed outside task-critical forms/checkout; default all-caps and continuously scrolling text are not.
- Use a mobile-first 12-column editorial system, tokenized spacing, intentional asymmetry/overlap, constrained prose, and responsive `clamp()` typography.
- Use authentic, approved human/lifestyle imagery first, then product, community, detail, and abstract art. Never ship AI-generated imagery to either public deployment. Clearly mark development placeholders.
- Community/nonprofit/volunteering content must use authentic evidence from the actual activity; generic stock cannot imply a relationship or event occurred. Product pages may use precise studio imagery where inspection matters.
- Never fabricate partnerships, events, impact/sustainability metrics, donation amounts, milestones, dates, testimonials, or product claims.

### Information architecture and interaction

- Commerce desktop navigation: **Men**, **Women**, **Sale**, **How It Works**; utilities: **Search**, **Account**, **Cart/Bag** with a nonzero count badge.
- Research navigation removes commerce routes/utilities and emphasizes Survey, Waitlist, How It Works, Community, Story, and approved brand/impact content.
- Desktop uses a solid sticky header and compact accessible Men/Women disclosures. Below `1024px`, use the full-screen navigation with hamburger, image logo, Search, Bag/Cart where commerce applies, Account inside the menu, accordion submenus, focus management, Escape, and scroll lock.
- Men and Women remain both direct category links and compact disclosures; Sale and How It Works are direct destinations unless approved real structure justifies otherwise. Use link/disclosure semantics with `aria-expanded`/`aria-controls`, not application-menu ARIA. Hover may enhance desktop disclosure, but click/focus, outside click, Escape, touch, and keyboard behavior are required.
- Preserve the announcement bar on mobile, use large touch rows, and place approved social links near the bottom of the open full-screen menu. Story, Impact, and Community remain homepage/footer destinations rather than required commerce desktop-primary items.
- Baseline breakpoints are approximately 480, 768, 1024, 1280, and 1536px; component-driven exceptions must be documented.
- Homepage order: announcement, header, campaign hero, brand statement, audience/category entry points, modular-system explainer, user-initiated YouTube section, community, concrete impact, goals, waitlist/newsletter, footer.
- Do not place normal product grids, prices, quantity controls, or add-to-cart buttons on the homepage.
- Use YouTube for approved video/livestreams, never autoplay promotional media, and defer the heavy embed until interaction where practical.
- Primary buttons are rectangular and normally brand blue; secondary buttons use an approved filled gold/dark/campaign treatment rather than default outline-only styling. Use normal capitalization, content-width mobile buttons unless layout requires otherwise, functional icons only, and a clear color-inversion hover treatment.
- Content links are not permanently underlined by default; provide a visible animated underline on hover/focus. Current navigation uses a persistent underline plus modest weight/contrast and never relies on color alone. Do not use browser-default visited purple or automatic external-link icons.
- Provide visible hover, `:focus-visible`, active/current, pressed, open, loading, disabled, error, success, empty, sold-out, and preorder states as relevant. State changes must not rely on color or motion alone.
- Associate form errors programmatically with their controls; expose loading names/states and prevent duplicate submission; pair add-to-cart toast feedback with durable cart state; give open disclosures an obvious trigger state; design intentional empty states with approved non-AI assets or explicit development placeholders.
- Normal motion is moderate and approximately 150–250ms. Respect `prefers-reduced-motion`; prohibit marquees, scroll-jacking, and blocking intros.

### Implementation and quality

- Target WCAG 2.2 AA: semantic landmarks/headings, labeled forms, accessible names/descriptions, contrast, keyboard operation, logical focus, touch targets, error association, and intentional alt text.
- Prefer progressive enhancement, CSS, and native browser behavior. Do not add React, Vue, Tailwind, Bootstrap, Alpine, HTMX, GSAP, or another frontend system without a concrete approved need.
- Reuse existing partials and patterns. Shared chrome belongs in `templates/base.html` and `templates/partials/`; do not create a second component system.
- Product pages are calmer than the homepage and must support evaluation of imagery, price, variant, stock/preorder status, fit, materials, care, modularity, shipping, returns, and trust.
- Use intrinsic image dimensions, responsive sources, modern formats, correct lazy-loading, self-hosted licensed fonts, and deferred heavy embeds. Avoid layout shift and oversized hero assets.
- Verify visible changes in a real browser at small phone, large phone, tablet, laptop, and wide desktop sizes, including keyboard, reduced motion, console, overflow, loading/error/empty states, and both deployment modes where relevant.

## 10. Cloudflare and production operations

- Cloudflare is the public edge; managed Django is the application origin; managed PostgreSQL remains the transactional database; R2 stores approved public media.
- Use Full (strict) TLS with a validated origin certificate. Configure Django's proxy trust only for the actual managed origin path and prevent direct-origin bypass where practical.
- Cache versioned static assets and approved public media with explicit policies. Bypass cache for admin, account, cart, checkout, webhook, authenticated/session-dependent responses, and dynamic HTML unless a later reviewed design proves safety.
- Serve public R2 media through a controlled custom domain. Treat public URLs as public data; do not place private customer documents in a public bucket.
- Maintain separate research and commerce origins/databases/secrets while deploying the same tested release commit.
- Production readiness requires migrations, health/readiness checks, structured/redacted logs, error monitoring, payment/inventory alerts, backups/PITR, restore tests, incident runbooks, deployment records, and rollback rehearsal.
- Do not introduce Redis, a task queue, advanced search, or Cloudflare Containers until a measured failure mode or workload justifies the operational cost.

## 11. Testing requirements

Tests prove approved behavior and failure handling; they do not create business policy or provide a general security guarantee.

### Required test layers

- **Models/database:** constraints, relationships, snapshots, calculations, state transitions, reservation/inventory concurrency, uniqueness, and rollback.
- **Services/business logic:** prices, availability, reservations, order/payment transitions, fulfillment, cancellation/return/refund eligibility, retries, and failure atomicity.
- **Views/forms/URLs:** status/redirects, validation, ownership, permissions, POST-only mutation, CSRF-relevant behavior, and mode-specific route exposure.
- **Authentication/authorization:** signup/login/recovery/verification, guest/account association, cross-user denial, staff roles, and object-level access.
- **Commerce:** guest/authenticated carts, quantities, repricing, mixed-fulfillment rejection, reservation boundaries, Checkout idempotency, payment reconciliation, signed webhooks, duplicates/out-of-order events, rollback, refunds/disputes, and inventory commit/release.
- **Modes:** run separate commerce and research matrices. Negative tests must prove research cannot import/initialize Stripe, register commerce routes, initiate payment, or create orders.
- **Frontend/user flow:** use an approved browser setup for high-value interactions; use accessible roles/names instead of brittle selectors. Manually review visual intent even when automation passes.
- **Security/privacy:** add focused tests for each changed property—authorization, unsafe methods, data exposure, validation, abuse controls, upload rules, or production configuration.

Concurrency-sensitive tests must run on PostgreSQL; SQLite results are insufficient for `select_for_update`, constraint timing, and reservation/oversell claims. CI must exercise supported Python/Django/PostgreSQL versions and both deployment modes without external network calls. Mock Stripe and email; use only test-mode credentials for manual payment testing.

For each behavior, select the relevant cases: happy path, invalid input, boundary, unauthorized, duplicate/retry, failure/rollback, deployment mode, and regression. Explain materially omitted cases.

Do not chase a coverage number. Test public behavior, durable state, permissions, and business invariants rather than exact HTML whitespace or helper structure.

## 12. Agent workflow and definition of done

### Workflow for each agreed step

1. Read `PROJECT_PLAN.md`, this file, and the relevant source, migrations, tests, templates, and configuration.
2. Reproduce or document current behavior; identify dependencies, affected records, modes, users, and failure cases.
3. Separate approved policy from unresolved policy. Ask focused questions before crossing an unresolved boundary.
4. State observable acceptance criteria, intended architecture, security/UX implications, migration/rollback needs, and checks.
5. Implement the smallest complete solution. Preserve working code and avoid unrelated refactors.
6. Add or update focused tests in the owning app. Add a regression test before/with a reproducible bug fix.
7. Run the narrow test target first, then the relevant mode/database/security/browser checks.
8. Inspect the rendered flow for customer-facing changes and provide a numbered owner-acceptance script.
9. Review the diff for scope, dead code, accidental artifacts, migrations, secrets, logging, accessibility, and documentation.
10. Update `PROJECT_PLAN.md` evidence/status and durable documentation when architecture or behavior changes.
11. Hand off results, commands, limitations, manual checks, and unresolved risks; stop and wait for `next`.

### Definition of done

A task is not done because code runs. It is done only when:

- approved acceptance criteria and material edge cases are implemented;
- server-side authorization, validation, data integrity, idempotency, concurrency, and failure behavior are appropriate to risk;
- migrations are generated, reviewed, tested, deploy-safe, and documented where applicable;
- relevant automated tests pass in both deployment modes and on PostgreSQL where semantics require it;
- responsive, accessible, keyboard, reduced-motion, error/loading/empty, and browser behavior is verified for visible changes;
- logs and error paths are actionable without exposing secrets or unnecessary PII;
- security, payment, inventory, privacy, SEO, and performance implications are reviewed as applicable;
- documentation, `PROJECT_PLAN.md`, and `MISTAKES.md` reflect the new truth;
- no credentials, customer data, local media, temporary screenshots, build artifacts, or unrelated changes enter the diff;
- dead/duplicate code made obsolete by the task is removed when safe, but unrelated cleanup is deferred; and
- the handoff distinguishes automated verification, readiness for owner acceptance, and actual owner acceptance.

### Baseline local commands

Use the repository virtual environment and `.env.example`; never commit `.env`.

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
python -m compileall Shoes web
```

Run mode-specific and PostgreSQL-backed commands required by the change. Before handoff, run `git diff --check`, inspect `git diff`, confirm only intended files changed, and report any check that could not run and why.
