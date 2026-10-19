# TreadJoy Product Language

## Current Heritage Court prototype taxonomy — 2026-10-14

The approved product-domain map describes one shoe prototype as seven visual
component groups. These are grouping labels, not verified removable modules,
attachment mechanisms, manufacturable parts, selectable options, or inventory
units. The same ordered identifiers are used in ADR 0003 and the
`heritage_court_v1` product standard.

1. **Front Shell** (`FRONT_SHELL`) — Visual group identified as the front shell
   in the current prototype. Attachment/removal is unverified.
2. **Bootie and Sole** (`BOOTIE_AND_SOLE`) — The bootie and sole stay together
   as one group; designated permanent in the current prototype.
3. **Tongue** (`TONGUE`) — Visual group identified as the tongue. Attachment/
   removal is unverified.
4. **Laces** (`LACES`) — Visual group identified as the laces;
   interchangeability is unverified.
5. **Back Panel** (`BACK_PANEL`) — Visual group identified as the back panel.
   Attachment/removal is unverified.
6. **Logo Holder** (`LOGO_HOLDER`) — Visual group identified as the logo
   holder. Attachment/removal is unverified.
7. **Back Loop** (`BACK_LOOP`) — Visual group identified as the back loop;
   its function and interchangeability are unverified.

`permanent` and `unverified` are evidence states, not customer promises. The
product standard requires one active assignment per canonical slot before a
variant can be activated or purchased. It does not constrain component
quantities or change finished-SKU inventory authority.

## Historical CAD terminology

The following terms are retained because they identify particular engineering
CAD revisions and QA records. They are not synonyms for the current seven
product-domain groups. Preserve their source files and revision-specific
evidence; do not use them to imply the current prototype has verified
interchangeability.

**Integrated Upper Overlay**: The connected outer-shell assembly described in
the historical CAD track, spanning the dark forefoot surround, lower strip,
connectors, eyestay bands, and side overlay, including mounted eyelets and
overlay stitching. This revision-specific assembly is not the current
`FRONT_SHELL` validation result.

**Permanent Chassis**: The structural base named in the historical CAD track;
the warm-stone vamp and quarter belong to that design description.

**Permanent Core Assembly**: The historical engineering union of sole,
carrier, bootie, structural chassis, and fit-critical reinforcement. It is not
the same thing as the current visual `BOOTIE_AND_SOLE` product slot, and the
historical CAD decision does not validate a production build.

**Module**: In historical engineering records, a named assembly intended to be
interchangeable as a unit. The term alone does not prove a working attachment
or approved removal method. For current product copy, use **visual component
group** unless interchangeability is separately verified and approved.

**Art Badge**: A historical identity assembly carrying the fixed TreadJoy mark,
with coordinated artwork, backing, or finish variants. The current taxonomy
uses the visual name **Logo Holder** and does not imply separate logo sales.

**Art Kit**: A historical coordinated set of surface patterns, colors, and
finishes applied to the same shoe geometry. It is not a production color
standard or available option.

**Visual Master**: A reviewed digital shoe used to produce concept imagery,
distinct from engineered dimensions and physical performance. It is not a
manufacturing master or validated physical prototype.

**Studio Lineup**: A presentation of coordinated or mixed styles that
communicates a concept without asserting an assembly sequence or removal path.
