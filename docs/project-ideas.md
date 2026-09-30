# TreadJoy Project Ideas

This is a living backlog for ideas and work the project owner wants to pursue.
Update the status, notes, and ordering as work progresses. This document is a
planning list, not evidence that an item is complete or approved for release.

The detailed entries below are organized as parent ideas. Each entry records
the current owner decisions, the work still required, unresolved questions,
and the next checkpoint. Checkboxes describe planning progress only; move an
item to **Completed work** only after the intended scope has been completed and
verified with dated evidence.

## Status legend

- **Not started** — idea captured; no meaningful work completed.
- **In progress** — active work is underway.
- **Blocked** — progress depends on a decision, person, resource, or external event.
- **Complete** — the intended scope is finished and verified.

## Backlog

| Status | Idea | Notes / next checkpoint |
| --- | --- | --- |
| Not started | Rework the website color scheme | Capture the specific problems with the current palette, define approved token changes, and verify contrast, responsive presentation, and both deployment modes before release. |
| Not started | Create and review website legal, accessibility, and policy materials | Research permitted guidance, draft terms of sale, terms of use, privacy, accessibility, and necessary legal notes, then obtain appropriate review and approval before publishing. Do not copy another site’s text or treat drafts as active policy. |
| Not started | Make frontend edits to improve UX/UI | Capture the specific friction or evidence first, then record the intended change and how it will be validated. |
| Not started | Add social links and establish social presence | Decide which approved social destinations belong on the website, verify ownership and URLs, and add them consistently without placeholder or invented accounts. |
| Not started | Rewrite the language on each page | Audit page copy, clarify the brand and product story, improve voice and readability, and verify factual, legal, and mode-specific claims before publishing. |
| Not started | Create a new logo with an artist | Identify the artist, agree on scope/usage rights, and collect approved final assets. |
| Not started | Take brand and product photos | Plan the shot list, subjects, location, styling, usage rights, and required product details. |
| Not started | Build financial tracking for current and known future expenses | Start with recurring expenses and renewal details, then record known fixed future expenses. Do not estimate unknown costs such as manufacturing; update them when reliable figures become available. |
| Not started | Plan footwear/industrial-design outreach | Prepare a paid engagement beginning with feasibility critique and design refinement. Defer CAD engineering and manufacturing outreach until the design direction is approved. |
| Not started | Create the shoe CAD-file workflow | After design approval, produce a parametric 3D model, then prototype-ready files, then the full manufacturing package. |
| Not started | Create a 3D-printable model of the shoe | Develop a printable representation after the design and parametric model are sufficiently stable. Define whether it is for visual review, fit/form study, or another approved prototype purpose before production use. |
| In progress | Add Blender-rendering snapshots to the research homepage | Finish the current rendering touch-ups, export approved snapshots, label them as development concepts, and place them on the research homepage without presenting them as final product imagery. |
| Not started | Create bold modular art-palette concepts for the homepage | Show the product vision and modularity through static, non-purchasable examples. The modules should share a coherent theme together and remain visually intentional when reused on another shoe. |
| Blocked | Update product logic to match the current modular shoe | The current backend part definitions are no longer authoritative. Do not change product taxonomy, BOM, compatibility, or customer-facing logic until the owner provides the current part map and rules. |

## Subscriptions and services

| Status | Service | Notes / next checkpoint |
| --- | --- | --- |
| Not started | GitHub Enterprise | Confirm the required plan, seats, and billing owner before subscribing. |
| Not started | Cloudflare | Confirm the required domain, DNS, security, and media services and keep account credentials outside the repository. |
| Not started | Render | Confirm the required hosting services, environment, database, and billing plan. |
| Not started | Set up professional business email addresses | Decide which addresses are needed—such as hello or sales—who should receive them, and which email provider will host them. |
| Not started | Codex | Confirm the appropriate plan and account/billing owner for ongoing project work. |

## Completed work

Move finished items here with the completion date, a short result, and links to
any relevant evidence or assets. Keep the original idea wording recognizable
so the backlog remains useful as a history of the project.

## New ideas

Add future ideas here before deciding whether they belong in the active backlog.

## Detailed idea tracking

### 1. Build financial tracking for current and known future expenses

**Status:** Not started

**Purpose:** Give the project owner a reliable view of what the business is
already paying and what fixed expenses are known to arrive next, without
inventing uncertain costs.

**Decisions captured:**

- Begin with current recurring expenses such as monthly subscriptions.
- Record the amount, billing cadence, renewal date, service, status, and any
  relevant owner or account note.
- Add known future expenses only when there is a concrete amount and a known
  payment date, trigger, or obligation.
- Leave unknown costs unresolved rather than estimating them. Manufacturing
  costs are explicitly deferred until reliable information is available.

**Steps:**

- [ ] Inventory the current recurring expenses and source evidence for each.
- [ ] Record renewal dates, billing cadence, amount, currency, and active or
  canceled status.
- [ ] Identify known future expenses with a fixed amount and payment timing.
- [ ] Define how updates, renewals, cancellations, and newly learned costs
  will be recorded.
- [ ] Decide whether the first implementation is a documented register,
  backend data model, staff view, or a staged combination of these.
- [ ] Add tests and verification for totals, dates, duplicate entries, and
  historical changes once implementation scope is approved.

**Current progress:** The scope and non-speculation rule are defined. No
expense register or financial-tracking backend has been implemented as part of
this idea.

**Next checkpoint:** Collect the current subscription list and confirm the
minimum fields and first viewing workflow.

**Open questions:**

- Which source should be authoritative for each expense: receipt, provider
  account, contract, or owner-entered record?
- Who may view or edit financial records?
- What reporting period or summary is needed first?

### 2. Plan footwear/industrial-design outreach

**Status:** Not started

**Purpose:** Find the right specialist to evaluate and refine the shoe design
before engineering files or supplier conversations create avoidable rework.

**Decisions captured:**

- The first specialist is a footwear or industrial designer.
- The initial engagement should be paid.
- The first phase should cover feasibility critique and design refinement.
- Production-ready files are deferred until the design direction is approved.
- CAD engineering comes after design refinement; manufacturing outreach comes
  after the CAD and product definition are sufficiently reliable.

**Outreach plan:**

- [ ] Assemble a concise design brief describing the product vision, bold art
  direction, modularity, current Blender work, and known constraints.
- [ ] Clearly state what the engagement is and is not: paid feasibility and
  refinement first; no assumption of production-ready files in phase one.
- [ ] Identify qualified footwear/industrial-design candidates and review
  relevant footwear, modular-product, form, materials, and production work.
- [ ] Ask candidates for their process, availability, proposed deliverables,
  revision approach, timeline, fee, ownership/usage terms, and handoff plan.
- [ ] Compare proposals against the design brief and choose a first engagement.
- [ ] Record the approved design direction and the handoff requirements for
  CAD engineering.

**Current progress:** The engagement sequence and first-phase goal are
defined. No candidate, proposal, or engagement has been recorded here yet.

**Next checkpoint:** Finish the design brief and identify the information that
can be shared with prospective designers.

### 3. Create the shoe CAD-file workflow

**Status:** Not started

**Dependency:** The design direction must be approved before production-oriented
CAD work begins.

**Purpose:** Turn the approved shoe design into increasingly precise digital
files while keeping early changes manageable.

**Decisions captured:**

- First deliverable: a parametric 3D model for continued iteration.
- Second deliverable: prototype-ready files.
- Final deliverable: the full manufacturing package, including the engineering
  information required for supplier handoff.

**Steps:**

- [ ] Receive and record the approved design direction and current modular
  product definition.
- [ ] Select the CAD workflow and responsible CAD engineer.
- [ ] Create and review the parametric 3D model.
- [ ] Define the prototype objective and export prototype-ready files.
- [ ] Test the prototype and record required design or engineering changes.
- [ ] Define tolerances, interfaces, materials, and supplier handoff details
  only after the product definition is stable.
- [ ] Assemble and verify the full manufacturing package.

**Current progress:** The deliverable sequence is defined. No CAD workflow,
engineer, or production file has been approved or recorded here.

**Next checkpoint:** Complete the design engagement and confirm the product
definition that CAD must represent.

### 4. Add Blender-rendering snapshots to the research homepage

**Status:** In progress

**Purpose:** Use the nearly finished Blender work to help research visitors
understand the product direction without confusing development concepts with
final products or purchase availability.

**Decisions captured:**

- The Blender rendering project is largely complete, with final details still
  being touched up.
- The largest remaining asset task is exporting and selecting snapshots.
- Snapshots must be documented and presented as development concepts.
- The research homepage must not imply that the images are final product
  imagery or purchasable products.

**Steps:**

- [x] Establish that the rendering work is in final touch-up rather than a new
  modeling project.
- [ ] Finish the remaining Blender details.
- [ ] Export approved snapshots at web-appropriate sizes and formats.
- [ ] Record asset provenance, approval status, and development-concept
  labeling.
- [ ] Add the snapshot section to the research homepage.
- [ ] Confirm responsive presentation, accessible text alternatives, and clear
  separation from commerce/product availability language.
- [ ] Run the research homepage acceptance checks and record evidence.

**Current progress:** The owner reports that the Blender renderings are being
finalized. The snapshots and homepage integration are not yet recorded as
complete in this repository.

**Next checkpoint:** Export the final snapshots and agree on the accompanying
development-concept copy.

### 5. Create a 3D-printable model of the shoe

**Status:** Not started

**Dependency:** The design direction and parametric CAD model must be stable
enough to produce a useful printable representation.

**Purpose:** Create a physical 3D-printable representation of the shoe for an
approved product-development purpose, such as visual review or fit/form study.

**Decisions captured:**

- This is a separate idea from the full CAD-file and manufacturing-package
  workflow.
- The printable model should be based on the approved shoe design rather than
  an outdated backend part definition.
- A printable model must not be treated as production-ready, wearable, or
  manufacturing-valid unless those purposes are separately approved and
  verified.

**Steps:**

- [ ] Confirm the purpose of the first print: visual review, fit/form study,
  modular-interface review, or another owner-approved purpose.
- [ ] Confirm whether the model should represent the complete shoe, separate
  modules, or both.
- [ ] Prepare the printable geometry from the approved parametric CAD model.
- [ ] Check mesh closure, scale, orientation, wall thickness, clearances, and
  relevant modular interfaces for the chosen print purpose.
- [ ] Export the selected printable file format and record its source revision.
- [ ] Produce and inspect the print, recording issues and required design
  changes.
- [ ] Keep the printable asset clearly labeled as a development prototype and
  separate from customer-facing catalog assets.

**Current progress:** The need for a 3D-printable shoe model is now captured.
No purpose, geometry, file, or print has been approved or recorded here.

**Next checkpoint:** Confirm what the first physical print is meant to answer
before preparing the printable model.

### 6. Create bold modular art-palette concepts for the homepage

**Status:** Not started

**Purpose:** Communicate the visual ambition and modularity of the product
through bold concept examples, not through a product-selection or sales flow.

**Decisions captured:**

- The examples are for sharing the product vision.
- Modularity should be visible because it is central to the brand.
- The examples are ideas only and are not purchasable now or in the future.
- The art should be bold.
- Modules used together on one shoe should share a coherent theme.
- The same modules should also look intentional when placed on another shoe.

**Steps:**

- [x] Define the examples as permanent, non-purchasable concept references.
- [ ] Define the visual themes and module combinations to illustrate.
- [ ] Create or approve the art-palette and shoe-example assets.
- [ ] Write copy that explains the vision without promising production,
  inventory, or future availability.
- [ ] Add the examples to the research homepage as static editorial content.
- [ ] Verify that no configurator, add-to-cart path, price, or availability
  claim is introduced.
- [ ] Review the examples at required responsive widths and record evidence.

**Current progress:** The purpose, visual direction, and permanent
non-purchasable status are defined. No final palette or homepage asset has been
approved here.

**Next checkpoint:** Choose the first set of themes and identify which Blender
snapshots or new artwork will illustrate them.

### 7. Update product logic to match the current modular shoe

**Status:** Blocked

**Purpose:** Bring the backend, templates, and related product logic into
alignment with the shoe that is actually being designed.

**Decisions captured:**

- TreadJoy sells fixed, preconfigured shoes built from coordinated
  interchangeable modules.
- Conceptual modular combinations explain the brand vision but are not
  customer-configurable, standalone, or purchasable products.
- The pieces currently described in the backend do not represent the current
  modularity of the shoe.
- The current part taxonomy and compatibility rules must not be guessed.

**Steps:**

- [x] Record that the existing backend modular definitions are no longer
  authoritative.
- [x] Record the high-level product boundary: fixed preconfigured shoes, no
  customer configurator, and no standalone module sales.
- [ ] Owner provides the current part map, including names, fixed elements,
  interchangeable elements, and compatibility rules.
- [ ] Reconcile the product taxonomy, BOM, compatibility relationships,
  availability behavior, and historical snapshots against that map.
- [ ] Update the owning models, migrations, services, templates, tests, and
  documentation together.
- [ ] Verify both research and commerce behavior and ensure concept art does
  not become an unintended sellable catalog path.
- [ ] Record the final product definition as the new implementation source of
  truth.

**Current progress:** The mismatch and the high-level product boundary are
known. Detailed implementation is intentionally blocked because the current
part definitions and compatibility rules have not yet been supplied.

**Next checkpoint:** Provide the authoritative current modular-part map before
any product-logic change is designed or implemented.

### 8. Add social links and establish social presence

**Status:** Not started

**Purpose:** Give visitors reliable paths to TreadJoy’s approved social
destinations and establish the minimum ownership and content context needed to
keep those links trustworthy.

**Decisions captured:**

- Social links should be added only for accounts and destinations that have
  been approved and verified.
- The website must not publish placeholder, invented, or unowned social URLs.
- Social links should be reviewed wherever shared navigation or footer content
  exposes them.

**Steps:**

- [ ] Decide which social platforms and profiles TreadJoy will use.
- [ ] Confirm account ownership, public handles, destination URLs, and launch
  readiness for each profile.
- [ ] Decide the approved placement and accessible link labels in the header,
  footer, research homepage, and mobile navigation where applicable.
- [ ] Add the links through the shared template path rather than duplicating
  URLs across pages.
- [ ] Verify destinations, new-tab behavior if used, keyboard access, and both
  research and commerce mode presentations.
- [ ] Record the approved social destinations in the release-content inventory.

**Current progress:** The need for social links and an associated social
presence is captured. No approved destinations or handles have been recorded
here.

**Next checkpoint:** Decide which social profiles exist and which are ready to
be linked publicly.

### 9. Create and review website legal, accessibility, and policy materials

**Status:** Not started

**Purpose:** Prepare the website materials needed to make customer-facing
promises, data practices, accessibility expectations, and commerce terms clear
and reviewable before publication.

**Decisions captured:**

- The scope includes terms of sale, terms of use, privacy policy,
  accessibility information, and other necessary website legal notes.
- Public guidance and comparable materials may be researched for structure and
  requirements where permitted, but another site’s wording must not be copied.
- Drafts are not active policy; publication requires the appropriate owner or
  qualified review and approval.

**Steps:**

- [ ] Inventory the pages, forms, data flows, commerce promises, and
  accessibility information that require coverage.
- [ ] Identify authoritative guidance and review sources for the relevant
  topics, preserving citations and avoiding copied text.
- [ ] Draft terms of sale, terms of use, privacy policy, accessibility
  statement, and any required supporting notices.
- [ ] Reconcile the drafts with the actual research/commerce mode boundary,
  checkout behavior, shipping/returns policy, data collection, cookies,
  email practices, and accessibility implementation.
- [ ] Obtain the required owner and qualified legal/privacy review before
  publishing or presenting the documents as final.
- [ ] Add approved documents to the correct navigation and footer locations.
- [ ] Record versions, effective dates, approval evidence, and future review
  triggers.

**Current progress:** The document categories and need for review are
captured. No new legal or accessibility policy text is approved by this idea.

**Next checkpoint:** Inventory the current customer-facing promises and data
practices that the documents must accurately describe.

### 10. Rework the website color scheme

**Status:** Not started

**Purpose:** Improve the website’s color direction while preserving a coherent,
accessible system across brand, research, and commerce experiences.

**Decisions captured:**

- The current color scheme is not meeting the owner’s expectations.
- The work should address the color system rather than apply isolated one-off
  color changes.
- Changes require review against the existing design tokens, accessibility
  contrast, responsive states, and both deployment modes.

**Steps:**

- [ ] Record which current surfaces, accents, states, or combinations are not
  working and why.
- [ ] Define candidate palette changes using the centralized design tokens.
- [ ] Check text, controls, focus indicators, alerts, disabled states, and
  imagery overlays for sufficient contrast and semantic clarity.
- [ ] Review the candidate scheme across research and commerce pages and key
  mobile and desktop widths.
- [ ] Obtain owner approval for the revised direction before changing shared
  tokens.
- [ ] Update affected templates and styles, then run visual and accessibility
  verification.

**Current progress:** The owner’s dissatisfaction with the current color scheme
is captured. No replacement palette has been selected or implemented.

**Next checkpoint:** Identify the specific color problems and the surfaces that
need review first.

### 11. Rewrite the language on each page

**Status:** Not started

**Purpose:** Make the website copy clearer, more compelling, and more aligned
with TreadJoy’s actual product, research purpose, and approved policies.

**Decisions captured:**

- The copy should be reviewed page by page rather than changed only on the
  homepage.
- Improved language must remain accurate about the product, modularity,
  research status, availability, community claims, and customer promises.
- Legal, policy, and accessibility language must remain consistent with the
  separately reviewed materials in the legal-content idea.

**Steps:**

- [ ] Inventory all public page copy, shared navigation/footer text, forms,
  error messages, product previews, and transactional screens.
- [ ] Mark copy that is unclear, generic, outdated, unsupported, or inconsistent
  with the current product definition.
- [ ] Establish the intended voice and terminology for research and commerce
  modes.
- [ ] Rewrite pages in a reviewable sequence and preserve factual source notes
  for claims that require approval.
- [ ] Review headings, labels, calls to action, alternative text, validation
  messages, and mobile navigation language for clarity and accessibility.
- [ ] Obtain owner approval for brand/product claims and coordinate legal review
  where copy creates a promise or policy statement.
- [ ] Run both-mode content checks and record the pages reviewed.

**Current progress:** The need for a site-wide language pass is captured. No
page-wide rewrite has been marked complete.

**Next checkpoint:** Create the page inventory and agree on the desired voice
before rewriting individual pages.

### 12. Set up professional business email addresses

**Status:** Not started

**Purpose:** Provide trustworthy business contact addresses for the website and
route messages to accountable recipients without exposing personal addresses
or creating unmonitored channels.

**Decisions captured:**

- Candidate addresses include role-based addresses such as `hello` and `sales`,
  but the final list is not yet approved.
- Each address needs an owner, destination, response expectation, and provider
  configuration.
- Email credentials and provider secrets must remain outside the repository.

**Steps:**

- [ ] Decide which role-based addresses are needed for launch and which are
  aliases versus separate mailboxes.
- [ ] Assign an accountable recipient and backup for each address.
- [ ] Select the email provider and confirm domain, DNS, authentication,
  forwarding, retention, and abuse controls.
- [ ] Configure the addresses and test sending, receiving, forwarding, and
  failure handling.
- [ ] Update website contact links and forms only after delivery is verified.
- [ ] Document ownership and operating procedures without storing credentials
  in the repository.

**Current progress:** The need for professional website email addresses is
captured. No address list, provider, or routing configuration is approved here.

**Next checkpoint:** Decide the initial role-based address list and who will
monitor each inbox or alias.

### 13. Review and clean project files

**Status:** Not started

**Purpose:** Establish a trustworthy, maintainable file set by reviewing stale,
duplicate, generated, misplaced, unreferenced, or sensitive material before
future product and website work builds on it.

**Decisions captured:**

- The review should cover the repository and relevant project assets, not just
  one directory.
- Cleaning must be evidence-based and must preserve needed history, active
  behavior, user-owned work, and approved assets.
- No broad deletion should occur until targets are identified, references are
  checked, and the owner approves any material removal.

**Steps:**

- [ ] Inventory tracked files, ignored files relevant to development, generated
  outputs, media, templates, static assets, scripts, and documentation.
- [ ] Identify stale, duplicate, obsolete, unreferenced, test/customer-like,
  secret-bearing, or incorrectly located files.
- [ ] Check code, templates, settings, tests, deployment manifests, and docs for
  references before proposing changes.
- [ ] Classify each proposed action as keep, rename, archive, replace, or
  remove, with a reason and risk note.
- [ ] Obtain approval for material removals and preserve recoverability where
  practical.
- [ ] Apply the approved cleanup with focused diffs, then run relevant tests,
  checks, static collection, and release-content validation.
- [ ] Record what was cleaned, what was intentionally retained, and any
  remaining follow-up work.

**Current progress:** The need for a file review and cleanup pass is captured.
No cleanup operation has been performed under this idea.

**Next checkpoint:** Produce an inventory and candidate list without deleting
anything.

## Cross-idea sequencing

The current dependency order is:

1. Capture current and known financial expenses without estimating unknowns.
2. Prepare and conduct the paid footwear/industrial-design outreach.
3. Approve the design direction.
4. Create the parametric CAD model, then prototype files, then the manufacturing
   package.
5. Create and inspect the approved 3D-printable model when its purpose and
   geometry are ready.
6. Finalize Blender snapshots and add them to the research homepage as
   development concepts.
7. Create and publish static bold art-palette concepts that explain the
   modular vision.
8. Update product logic only after the owner supplies the current modular-part
   map and compatibility rules.

These ideas may progress in parallel where their inputs are independent, but a
completed design, CAD, or homepage concept does not by itself authorize a
customer configurator, standalone component sales, or a change to the
authoritative commerce catalog.
