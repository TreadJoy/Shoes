# Heritage Court V3 — Implementation Status

**2026-10-13:** owner approved AP-01 appearance prototype first. The coupon
checklist below is deferred. Active work: extract Trial 08, repair the five
physical modules, add disposable registration, validate and prepare P2S
plates. Physical printing and AP-01 owner acceptance precede engineering.

Baseline: [approved plan](plan.md). Updated 2026-10-12.
The historical coupon Stage 1 below is deferred. An unchecked physical gate is
not satisfied by mesh validation. Engineering waits for AP-01 owner acceptance.

## Active AP-01 Work — 2026-10-14

- [x] Preserve Trial 08 and verify its exact SHA-256; extract right master in mm.
- [x] Create a separate source-derived five-module mesh pipeline and review 3MF.
- [x] Omit laces, stitching and sub-limit raised decoration.
- [x] Trial disposable alignment pins, sockets and shallow collar floor.
- [x] Independently inspect saved STL topology, volume, bounds and interference.
- [x] Preserve one independent file/body per module and matching named 3MF objects.
- [x] Test Trial 13 digital removal paths continuously: badge, heel, overlay, tongue.
- [x] Screen all 14 eyelets for retained ring material and clear bores.
- [ ] Resolve all thin regions and surface/edge defects; candidate is not released.
- [x] Add subtle per-module viewing colors and inspect colored saved-model reviews.
- [x] Trial bounded core fairing and rerun independent-body/removal/eyelet checks;
  retain unresolved wall minima and visual defects as release blockers.
- [ ] Certify protected exterior deviations and document intentional repairs.
- [x] Trial 24: rebuild badge face and seat, reinforce selected rear skin,
  regularize export slivers, and repeat saved-file/removal/eyelet checks.
- [x] Trial 25: reinforce the diagnosed rear edge; target chord 3.088 mm and
  81-line local directional grid minimum 2.714 mm; removal paths remain clear.
- [x] Diagnose six medial-quarter thin skins against M09 occupancy; inward-only
  backing conflicts at all six samples. Audit medial-quarter-001; no mesh edit.
- [x] Trial 27 removes the six diagnosed medial skin remnants; independent
  removable meshes, colors and core bounds preserved. Trial 26 rejected.
- [x] Test source-guided trim restoration (Trials 28–30); reject raised-band
  appearance despite Trial 30 local wall pass. Trial 27 was retained then.
- [x] Trial 32 blends the medial trim along its length and lower wall, fills
  the two prior short-edge locations, and preserves five separate modules;
  all four continuous removal sweeps and 344 sampled pair-poses pass.
- [x] Trial 33: test and reject a 0.2 mm cap rise; expand the trim-end screen
  on both candidates. Trial 32 retained, with 65 thin sampled chords now recorded.
- [x] Reject Trial 34 rectangular strip replacement: old cap removed, but
  thin/notched joins remain; removable meshes unchanged from Trial 32.
- [x] Build isolated rounded-section study: 139 section checks and 5,680
  face-centroid normals pass ≥1.6 mm. Trial 32 untouched.
- [ ] Match study end loops to the shoe, resolve 10.758 mm³ M09 overlap, and
  validate the actual joined region to ≥1.6 mm without another rectangular cut,
  other local walls and
  collar/panel-boundary defects; audit C01's earlier topology change before printing.
- [ ] Complete hidden labels, clearance and insertion-path review.
- [ ] Validate orientations and native P2S slices; record durations and mass.
- [ ] Seal library print package, then obtain physical review and owner acceptance.

Current evidence is under private `cad/ap01/revisions/`; failed trials remain
archived. No AP-01 slice or physical print is approved by these checkmarks.

## Stage 1 — Rev A Calibration

- [x] Preserve existing exact coupon geometry and prior artifacts.
- [x] Prepare P2S 0.4 mm / Textured PEI / PLA Basic slice and support review.
- [x] Provide nominal measurements and 12-trial Run 001 worksheet.
- [x] Verify and package immutable portable library handoff (25 entries,
  internal hashes, source-byte comparison, ZIP CRC, selected slice identity).
- [ ] Staff confirms actual hardware, spool, preview, and permitted duration.
- [ ] Print and test each family C45 → C35 → C25 → C15; record actual dimensions,
  clean cycles, damage, support scars, play, and both detent returns.
- [ ] Select independently; repeat selected candidates on second print.
- [ ] If no candidate passes, prepare revised 0.10 mm ladder around transition.
- [ ] Record disposition, update contract/report/checksums, owner accepts Stage 1.

Verification: package SHA-256/ZIP integrity; physical criteria in plan Stage 1.
Files: private cad/calibration, cad/releases, contract and validation report.
No physical pass is currently recorded. No printer has been started.

## Subsequent Gated Slices

| Stage | Dependency | Acceptance evidence | Status |
| --- | --- | --- | --- |
| 2 Last registration | Stage 1 acceptance + next | Reviewed last, rights, checksum, datums, deviations | Not started |
| 3 C01 core | Reviewed last + next | Valid solids, sections, clearances, structural review | Not started |
| 4 M09 | C01, measured interfaces + next | Local rigs, 14-eyelet shell, reviewed numerical limits/tests | Not started |
| 5a M04 | M09 handoff + next | Interface record, pull/snag/impact/pressure/loop results | Not started |
| 5b M05 | Previous handoff + next | Interface record, unlacing/migration/pressure/wear results | Not started |
| 5c M06 | Previous handoff + next | Interface record, seating/snag/abrasion/small-part results | Not started |
| 5d M07 | Previous handoff + next | Lace access, abrasion and chassis load path review | Not started |
| 6 Integration | All slices accepted + next | Seams, interference, paths, release-failure checks | Not started |
| 7 Process prototypes | Integrated review + next | Intended-material joint tests, bench results, wear gate | Not started |
| 8 Release | Previous acceptance + next | All specified exports, records, manifest, build verification | Not started |

Break subsequent stages into focused implementation tasks when their gates
pass and inputs are available; do not invent last dimensions or force targets.
