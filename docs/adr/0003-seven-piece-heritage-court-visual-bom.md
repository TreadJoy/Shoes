---
status: accepted
date: 2026-10-14
supersedes: 0002-permanent-core-assembly.md (product/catalog taxonomy only)
---

# Model Heritage Court As Seven Visual Component Groups

The Heritage Court prototype's product-domain BOM uses the seven visual groups
shown in the approved Night Grid exploded study, in this order: `FRONT_SHELL`,
`BOOTIE_AND_SOLE`, `TONGUE`, `LACES`, `BACK_PANEL`, `LOGO_HOLDER`, and
`BACK_LOOP`. `BOOTIE_AND_SOLE` is designated permanent in the current
prototype; interchangeability for the other six groups is unverified.

This is a product-catalog grouping decision, not a mechanical design approval.
The taxonomy does not establish attachment interfaces, removal mechanics,
manufacturability, customer configurability, or component-level inventory
authority. Revision-specific CAD and QA records remain historical evidence for
their own engineering revisions and are not rewritten by this decision.

Products opt in through `component_standard="heritage_court_v1"`. A ready
variant has exactly one active part assignment in each canonical slot, with
active related part records and matching compatibility groups. Incomplete
inactive drafts remain possible. The finished `ProductVariant` and its
preorder allocation remain the only launch sellable-stock authority; component
quantities are not interpreted as inventory units.

Legacy `OUTER_SHELL`, `LOGO`, and `SOLE` lookup rows remain in place and are
inactive. Existing `TONGUE`, `LACES`, and `BACK_PANEL` rows are reused without
changing any part, variant, quote, or order references. Historical Checkout
and order component snapshots retain their recorded codes.

## Consequences

- The seven-slot order is shared by the controlled taxonomy, BOM validation,
  admin readiness, and homepage prototype list.
- Cart addition and Checkout reject an invalid opted-in BOM with a generic
  customer-safe not-ready message. Checkout validates before attempt creation
  and again under the finished-SKU lock before quote and reservation writes.
- Non-opted-in products and other product categories retain existing behavior.
- No Heritage Court catalog product, SKU, price, stock, image, material,
  component quantity, or compatibility record is created by this decision.
- This decision supersedes ADR 0002's product/catalog taxonomy only. ADR 0002's
  dated engineering description remains historical and is not evidence that a
  current physical prototype has validated those interfaces or modules.
