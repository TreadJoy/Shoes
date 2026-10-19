# TreadJoy Heritage Court V3 Engineering CAD Plan

**2026-10-13 owner supersession:** AP-01 full-scale appearance prototyping now
precedes physical coupon calibration and last-based engineering. The active
implementation contract is `design/active/treadjoy-heritage-court-v3/cad/ap01/PLAN.md`.
The historical sequence below is retained as engineering background; it must
not block AP-01 or imply coupon calibration is the current first task.

Owner-approved implementation baseline, 2026-10-12. Task status lives in
[todo.md](todo.md). Each stage ends with owner handoff and waits for `next`.
Current stage: **1 — physical calibration pending**. Digital preparation is
not a physical, structural, fit, wear, or production approval.

## Summary and Authority

Produce a right US men's 9 engineering-development package derived from
Trial 08 Blender visual authority. Correct faceting, connector dents, eyelet
notches, stitching irregularities, and stiff lace geometry while preserving
the approved silhouette and modular ownership.

Maintain parametric Python/build123d as geometry authority. FCStd documents
provide native review files; STEP provides exact exchange solids; STL/3MF
provide process-specific prototype outputs. Imported FCStd solids are not a
claim of a native parametric feature tree.

Visual source: `design/active/treadjoy-heritage-court-v3/qa/r16-final-polish-trial-08/treadjoy-heritage-court-v3-pair-r16-final-polish.blend`.
SHA-256: `94f6de5b13295fd2d4c866e36044b8040f654f9d7fadab6dcecf5cb6ba1fc4e9`.
Trial 08 is visual authority, not manufacturing geometry.

## Product and Interface Contract

- Permanent core `TJ-HC3-C01`: sole, carrier, structural bootie/chassis,
  reinforcement, heel counter, toe structure, and fit-critical surfaces.
- Interchangeable `M09`: connected Integrated Upper Overlay, all 14 mounted
  eyelets and overlay stitching.
- Interchangeable `M04`: Back Panel and Heel, pull loop and related stitching.
- Interchangeable `M05`: Tongue and fixed label/mark.
- Interchangeable `M06`: Art Badge with fixed Junction Tile silhouette.
- Interchangeable `M07`: Laces.
- Retire M08 as interchangeable; sole is an internal permanent-core BOM item.
- Swaps are tool-free, off-foot, unloaded. Remove laces before M09 or M05.
  Concealed, guarded releases require deliberate action. Wrong order and
  partial engagement must be detectable or physically blocked.
- Millimeters; +Y toe, -Y heel, +Z up, +X lateral. Origin: heel-seat center
  projected onto carrier bottom.
- No Django/catalog changes or standalone-component launch expansion.

## Implementation Sequence

### 1. Complete Rev A Physical Calibration

Print `TJ-HC3-M09-CPN-A01` at Milwaukee Public Library from the prepared P2S
sliced 3MF. Baseline: 0.4 mm nozzle, Textured PEI, PLA Basic, 0.20 mm layers,
four walls, five top/bottom layers, 25% gyroid, 5 mm brim, build-plate-only
supports. Confirm actual library configuration before printing.

Test C45, C35, C25, then C15 independently for toe, eyelet, and quarter.
A candidate must assemble/release by hand for 10 cycles without shaving,
whitening, cracking, permanent deformation, or incomplete return of either
quarter detent. Choose the smallest nonbinding clearance with least observed
play for each interface. Repeat selected candidates on a second print.
If no lane passes, create a second ladder in 0.10 mm steps around the nearest
bind/loose transition. Record printer, plate, nozzle, filament, measured
dimensions, support scars, cycles, play, and failure modes in Run 001.

### 2. Acquire and Register the Size-9 Last

Obtain an engineer/manufacturer-reviewed right US men's 9 last with explicit
units, revision, provenance/use rights, toe allowance, sock allowance,
heel-seat definition, and grading reference. Preserve the original; register
its checksum and heel, ball, toe, centerline, ground, and collar datums.
Compare Blender envelope to last and document every deviation. Do not freeze
fit-critical surfaces, stack height, drop, carrier, or interior volume before
this gate passes.

### 3. Reconstruct the Permanent Core

Build cupsole/outsole, JOY ORBIT tread intent, carrier, warm-stone vamp and
quarters, collar, heel counter, toe structure, footbed allowance, and lace-load
reinforcement around the approved last. Preserve broad rounded forefoot,
sole proportions, lower side-panel curve, collar opening, and pull-loop
placement. Build closed solids with explicit thicknesses, fillets, draft
assumptions, flex zones, and manufacturing datums. Keep the primary forefoot
flex line free of rigid continuous attachment features. Release requires
exact-solid validation, sections, last-clearance review, and engineer/
manufacturer approval of structural assumptions.

### 4. Engineer M09 First

Reconstruct one removable connected shell with 14 eyelets. Architecture:
toe/lower-perimeter sliding capture, eyelet-aligned load-transfer keys into
permanent reinforcement, two concealed opposed rear releases. Incorporate
physically selected clearances, insertion stops, tactile/visible complete
engagement, drainage/debris relief, wrong-side/wrong-size prevention.
Use clean shared boundaries and controlled curvature, not mesh ripples or
notches. Produce localized load-path rigs before shell integration. Obtain
numerical retention, lace-load, release-force, and cycle targets from the
footwear engineer/manufacturer before claiming structural pass.

### 5. Engineer M04–M07 as Independent Slices

- M04: replaceable heel panel, permanent heel support in C01. Test pull, snag,
  impact, pressure, and pull-loop anchoring.
- M05: removable padded tongue retained by permanent throat/gusset. Require
  unlacing; test migration, pressure, hook wear, and lace contact.
- M06: fixed-shape badge, keyed blind slide/backer and guarded compliant
  retention. Test rattle, snag, impact, wrong seating, abrasion, small-part behavior.
- M07: conventional removable laces, abrasion-safe eyelets, permanent chassis
  load reinforcement. Validate unthreading/rethreading after M09 integration.

Each module needs a separate interface record: mating IDs, assembly vector,
release travel, engagement indication, tolerance stack, materials, wear
surfaces, contamination paths, fixture, limits, failure modes, disposition.
Handoff each independent slice before proceeding.

### 6. Integrate the Complete Shoe

Assemble C01 with all five modules; compare every visual seam to Blender.
Check interference and approved removal paths. Verify one depressed/failed
release cannot detach M09, ordinary standing compression cannot release it,
and structural foot retention remains in C01. Left presentation geometry
follows accepted right-size-9 engineering assembly; mirror appearance where
appropriate while retaining side-specific IDs and interface handedness.
Exploded technical views must use validated assembly/removal vectors.

### 7. Prototype and Manufacturing Progression

PLA FDM is dimensional screening only. Repeat chosen joints in intended
prototype material families before integration: PA12/SLS or MJF rigid
carriers, appropriate TPU/soft-good flexible parts. Bench-test fit, retention,
release, contamination, wear, abrasion, flex, pressure, and repeated swapping.
Integrated prototypes remain engineering samples until an engineer-approved
wear protocol exists. Coupon results do not establish comfort, durability,
traction, safety, or production readiness.

### 8. Release the Engineering Package

Deliver maintained parametric source/build instructions; native FCStd review
assembly; exact STEP assembly and separate C01/module/part STEP; watertight
STL and unsliced 3MF for approved prototype processes; schema-v3 module/
interface registry; BOM; material candidates; tolerances; datum map; removal
sequence; engineering drawings; validation reports; physical-test records;
SHA-256 manifest. Use revisioned immutable directories. Never overwrite prior
CAD, Blender, slice, or test evidence.

## Verification and Acceptance

- Every exported solid: valid, positive volume, correct scale/name, checksum.
- Meshes: watertight, exact-solid envelope within declared tessellation tolerance.
- Assembly: intended clearances, unintended intersections, incomplete engagement,
  wrong module/side, release travel, unlacing dependencies, all removal paths.
- DfAM: wall/feature thickness, holes, bridges, overhangs, support contact,
  orientation, build envelope, process-specific tolerances.
- Visual: approved silhouette, rounded panel curve, badge, collar, pull loop,
  sole proportions, JOY ORBIT identity; record intentional engineering deviations.
- Physical: distinguish dimensional fit from retention, load, fatigue, comfort,
  and wear performance.
- Each stage updates contract, validation report, checksums, PROJECT_PLAN.md,
  and MISTAKES.md, then stops for owner acceptance.

## Assumptions and Gates

Right US men's 9 only until last/grading approval. Two hours is a planning
target, not a published MPL limit. Production materials, numerical load
limits, stack height, drop, target weight, grading rules require footwear
engineer/manufacturer input before freeze. Final deliverable is an auditable
engineering-development package, not wearable/production approval.
