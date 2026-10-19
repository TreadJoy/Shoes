---
version: alpha
name: "TreadJoy"
description: "An energetic editorial shoe brand with quiet, trustworthy product and research workflows."
colors:
  primary: "#4CCBF0"
  secondary: "#EDDC4F"
  background: "#E7EEF0"
  surface: "#DCE5E7"
  text: "#191919"
  muted-text: "#475457"
  border: "#889598"
  focus: "#006B82"
  success: "#175C35"
  warning: "#6B5000"
  danger: "#842133"
typography:
  display:
    fontFamily: "Fredoka, Arial Rounded MT Bold, sans-serif"
  sans:
    fontFamily: "DM Sans, Arial, sans-serif"
rounded:
  DEFAULT: "0.75rem"
  sm: "0.5rem"
  md: "0.75rem"
  lg: "1.25rem"
  xl: "1.5rem"
spacing:
  unit: "0.25rem"
  section-gap: "4rem"
  page-max: "80rem"
components:
  button:
    minHeight: "2.75rem"
  input:
    minHeight: "2.75rem"
  card:
    borderWidth: "1px"
---

# TreadJoy Design System

## Overview

### Creative North Star

TreadJoy should feel like a well-edited independent streetwear magazine translated into a trustworthy shoe storefront: expressive campaign composition around the task, calm and familiar controls inside it.

### Product context and register

- **Audience and primary job:** Pre-launch visitors explore modular shoes, provide anonymous research feedback, or affirmatively subscribe to bounded updates; commerce customers later shop and manage orders.
- **Target markets and evidence:** Initial US research focuses on Midwestern urban communities as a working hypothesis documented in `AGENTS.md`.
- **Locale and language policy:** English (`en-us`) is the active UI locale. Customer-facing legal copy requires its named approval owner.
- **Usage scene:** Mobile-first public browsing and short forms; staff use standard Django admin for low-frequency audited work.
- **Register:** Hybrid. Public storytelling is expressive; forms, consent, privacy, account, checkout, and admin surfaces prioritize familiarity and clarity.
- **Memorable signature:** Sky-blue and gold accents, Fredoka display type, and controlled editorial asymmetry.
- **Restraint:** Consent, identity, payment, destructive, permissioned, and error states avoid decorative motion or ambiguous language.
- **Anti-references:** Generic white SaaS dashboards, chaotic graffiti pastiche, dark-pattern signup prompts, and card grids on the homepage.
- **Token ownership/runtime mapping:** `static/css/style.css` is canonical runtime token source; this file mirrors those values. `static/css/home.css` may compose them but must not redefine them.

## Colors

The shared page background is a cool muted neutral; research mode overrides it with warm near-white `#F5F4F0`. Near-black carries primary text and high-trust contrast. Sky blue and gold are expressive accents, not semantic success/error colors. Functional success, warning, danger, information, focus, and disabled colors remain separate in `static/css/style.css`. The product currently supports one light theme; forced-colors behavior remains platform-owned.

## Typography

Fredoka is reserved for display hierarchy and DM Sans for prose and controls. Headings default to Title Case; interface copy uses sentence case. Body measure is capped near 42rem, and task copy favors concrete verbs over slogans.

## Layout

Public pages use a mobile-first editorial system with a maximum 80rem content area, responsive gutters, and established 480/768/1024/1280/1536px review points. Forms keep natural document scrolling and a readable single-column measure. Layout changes must preserve focus visibility, reachable controls, and stable error/help space.

## Elevation & Depth

Tonal surfaces and borders establish hierarchy. Small and medium shadows are reserved for deliberate floating/editorial media surfaces; task forms and admin records stay primarily flat and bordered.

## Shapes

Controls use the 0.75rem family, compact elements may use 0.5rem, and editorial containers may reach 1.5rem. Pill shapes are accents, not the default for inputs or buttons.

## Components

### Foundational visual states

All controls provide default, hover, focus-visible, active, disabled, busy, and error states where applicable. Focus uses the dedicated high-contrast focus color. Status never relies on color alone.

### Buttons and actions

Primary and secondary buttons share a 2.75rem minimum height and explicit verbs. Dangerous or irreversible work remains separated in standard Django admin/commands and requires a distinct confirmation or gated command contract.

### Navigation and data display

Research navigation omits customer accounts and commerce controls. Commerce retains its established category/account/bag model. Staff tables use Django admin ownership and server-side permissions.

### Forms and overlays

Product forms use `novalidate`, visible labels, inline errors, a form-level summary when needed, preserved non-sensitive input, and a clear privacy path. Consent checkboxes are unchecked and visually paired with their full statement. Textareas do not resize and must provide an adequate starting height.
Choice fields keep native Django form ownership. Compact questions use ordinary
radio cards; the Heritage Court visual-direction question adds approved imagery,
visible names, and short descriptions while retaining native radio inputs and a
fieldset/legend relationship. Images supplement rather than replace the text.

### Iconography

Existing inline SVG uses simple two-pixel strokes. Icon-only controls require visible focus and an accessible name; consequential actions retain text labels.

### Motion

Transitions communicate hover, disclosure, or state change in roughly 180–220ms.
Reduced-motion rules target the components that actually transition or animate;
they preserve immediate checked, focus, disclosure, error, and busy feedback.

### Content and data visualization

Voice is direct, optimistic, and evidence-aware. Research success messages do not reveal whether an email exists. No visualization is used when plain text or a table communicates the fact more safely.

## Do's and Don'ts

- **Do:** Keep brand expression around a form while making the form itself conventional and quiet.
- **Do:** Reuse the semantic tokens and shared controls in `static/css/style.css`.
- **Don't:** turn consent into preselection, implied agreement, or eligibility disclosure.
- **Don't:** use expressive campaign color as the only indicator of error, permission, or destructive severity.
