---
status: accepted
date: 2026-09-28
---

# Treat The Connected Upper Overlay As One Module

The current Heritage Court visual model joins the former forefoot, eyestay, and quarter overlays into one continuous dark shell. On 2026-09-28 the owner approved one **Integrated Upper Overlay**, `TJ-HC3-M09` (`OUTER_SHELL / INTEGRATED_OVERLAY`), including its 14 mounted eyelets and overlay stitching per shoe, instead of preserving three independently removable identities that the geometry no longer supports. The warm-stone vamp and quarter remain permanent chassis surfaces; laces remain M07.

## Consequences

- M01–M03 retire with `replaced_by: TJ-HC3-M09`; M04 Back Panel and Heel, M05 Tongue, M06 Art Badge, M07 Laces, and M08 Sole retain their IDs, producing six active module concepts.
- The module registry moves to schema v2 with explicit active and retired records and actual visual-object ownership. M09 attachment design, removal vector, and dependencies remain `TBC_ENGINEER`; null values mean unresolved, not dependency-free.
- The existing six Django `PartType` categories already represent this contract. This decision requires no schema migration, edits to applied migrations, catalog seeding, or change to finished-SKU inventory authority.
- Current specifications, generators, and validators adopt the new contract. Hash-bound V2 and R1–R15 evidence stays unchanged and is identified as superseded through living indexes.
- Rendering shows whole-overlay swaps and studio lineups. Splitting its pattern into fictional independently removable regions or animating an unengineered removal path would misrepresent the design.
