# Verification Limitations

## 2026-09-15 — R13 marked front trim

- The first R13 footprint was evaluated in side-view Y/Z coordinates without
  restricting it to the shoe's sides. It extended across the toe-box center.
  Restrict the new strip to the side surface beside the lace opening and
  visually inspect the result; a single connected mesh is not shape acceptance.
- Preserve evaluated source lace geometry before replacing trim objects. Do not
  claim a particular dependency caused a displaced lace end without evidence.
- The lower trim is extended behind the cupsole rim to avoid the exposed sampled
  edge retained in R12. This is a visual overlap, not an engineered attachment.

## 2026-09-14 — R12 continuous-trim fusion

- The first voxel fusion left 169 tiny disconnected fragments, two blocked
  terminal eyelet center rays, and unwelded end-cap rings on new stitch dashes.
  Removed only fragment components under 1,000 vertices from the new trim,
  restored the existing eyelet bores, and welded the new stitch end caps.
- The resulting mesh passed the scoped topology and 40 aperture-center checks,
  but its render still read as stacked flaps. Topological connection alone did
  not meet the owner's continuous-panel request. Re-seat the merging side
  surfaces to a common base-shell depth and blend the junctions before review.
- That attempted per-vertex side projection distorted thin eyestay geometry,
  introduced openings/fragments and blocked four aperture rays. Rejected it.
  Rebuild a single sampled surface from the existing trim footprints and base
  shell instead, with explicit thickness and restored eyelet bores. Do not
  report the failed intermediate R12 render as the completed design.
- Reconstructing the whole trim radially created a toe-tip singularity, and
  regularizing that intermediate solid lost visible panel definition. Restricted
  radial reconstruction to the owner's new connecting strips, retained the
  existing saddle/eyestay/toe-wrap shells, and clamped smoothing against the
  measured supporting surface. Recheck terminal bores after solid fusion because
  a bore cut before fusing overlapping shells may not survive the operation.
- A lace-dependency explanation was considered for a render artifact, but direct
  inspection found no object modifier targets in the original R11 file. Do not
  present that hypothesis as an established cause. Hidden originals are retained
  for reference and smooth-normal transfer. A separate unchanged R11 baseline
  render is preserved in the R12 QA folder without replacing the owner's markup.
- R11 and its newly annotated perspective image must remain untouched. This
  continuous trim crosses previous module divisions; it does not establish an
  engineered removable assembly.

## 2026-09-14 — R11 overlay seam projection

- Directly projecting each new overlay vertex onto the outermost existing panel
  copied abrupt seam heights and produced rough/intersecting areas in the first
  perspective render, despite zero boundary edges or degenerate faces.
- Fit a smooth surface with an outward envelope allowance, round the contour
  tips and bevel the perimeter. Recheck rendered appearance and aperture access;
  topology alone does not prove coherent layering or production attachment.
- The attempted micro-bevel generated hundreds of tiny faces; welding/dissolving
  them opened boundaries. Removed that bevel and its cleanup, retaining the
  explicitly rounded contour. The revised 183-mesh check has zero boundary
  edges and degenerate faces. Seated backs fill the space beneath the smooth
  fronts rather than leaving a floating overlay. Thickness remains conceptual.
- Front/rear review revealed excessive stand-off from the full smoothing
  envelope. Reduced the envelope contribution to 22% with a 0.45 mm base
  face offset. These are visual parameters, not manufactured thicknesses.
- That raw-surface blend reintroduced seam artifacts. Replaced it with local
  smooth support bumps around existing seam relief and a 0.45 mm front offset;
  the front remains analytic while avoiding a global lift for one seam peak.
- Final perspective review also identified inherited stitch dashes poking through
  the new contours. Remove whole covered dash components, retaining exposed
  border stitching; do not treat those marks as texture or a successful smooth
  surface merely because topology checks pass.
- Preserve the marked-up R10 lateral image. New geometry belongs only to R11.

## 2026-09-14 — R9 visual finishing checks

- The first R9 side render still showed heel recesses after the control objects
  were removed: the R4 heel already retained the cut geometry. Restore the uncut
  R3 heel and replay the established R5/R7/R8 shape transforms instead.
- The initial pull loop read as a tall narrow strip, and projecting the inherited
  lower stitch row exposed a stray line beneath the badge. Rebuilt the loop as a
  shorter rounded opening and joined the quarter's lower/front stitch border.
- Rebuilt lace crossings initially intersected adjacent entries and the tongue.
  Offset adjacent entries, separate over/under lanes, and use nearest-surface
  support when a vertical ray misses the tongue edge; a fixed fallback height
  created unwanted dips. The corrected construction check reports zero tested
  crossing/tongue and crossing/crossing overlaps.
- Passing those overlap checks did not prove visible eyelet entry: a subsequent
  render showed lace portions buried by the eyestays. Added explicit eyestay
  surface support to the crossing edges. Keep visual inspection separate from
  the narrower automated crossing/tongue test.
- Neighbor-based sole smoothing was insufficient for the stepped front foxing.
  Filter matching perimeter lanes instead, retaining the cross-section structure
  and footprint. Final visible results still require owner review.
- These are private visual revisions, not proof of loop strength, attachment,
  locking logic, or physical fit. R8 and its annotated review images are retained.

## 2026-09-14 — R8 inherited material names

- The first annotation build reached the new tongue label but stopped because
  saved R7 badge materials carry Blender-generated name suffixes. A fixed
  material-name lookup was not a stable reference.
- Resolve the label colors from the existing Blank face and shared backer material
  assignments instead. The failed invocation stopped before saving or rendering
  R8; R7 and the owner's marked-up images were preserved.
- The first side render of the rounded toe-overlay end exposed a dark gap at
  the old butt joint. Extended the quarter's lower front beneath the new rounded
  termination; the throat and badge region stay unchanged. This is a visual
  underlap, not a validated structural seam or physical attachment.

## 2026-09-14 — R7 final-coordinate width verification

- The first size-9 reference-width check found a 78.4 mm modeled heel against
  the 77.7 mm sample benchmark. Measuring the pre-warp longitudinal band missed
  the effect of redistributing the heel/instep/forefoot stations.
- Added a final-coordinate section measurement and corrective heel scale before
  saving. The 0.1 mm check is a numerical model threshold, not a manufacturing
  tolerance or proof of AF1 fit. R6 remains unchanged.
- The final evaluated mesh check also reports one medial-quarter face below the
  1e-12 m² area threshold at the refitted badge pocket. Boundaries/nonmanifold
  edges remain zero. Logged as open mesh cleanup rather than claiming a complete
  geometry pass at this silhouette-review checkpoint.

## 2026-09-13 — R6 badge close-up artifacts

- Wide views concealed diagonal relief shading artifacts. Increasing sampling
  and embedding the raised mark did not remove the creases. Fitted a smooth shared
  presentation surface and supplied analytic cap normals; the diagnostic close-up
  confirmed the diagonal shading creases were removed. This is not contact QA.
- Per-polygon Art colors produced jagged boundaries. Replaced those assignments
  with a continuous procedural wave and circle study; it remains a placeholder.

## 2026-09-13 — R6 vector triangulation API

- Blender 5.2 returned triangle indices rather than vectors from the triangulation
  helper. The first badge build stopped before saving R6, but the chained render
  script continued on R5. Added compatibility handling and use `--python-exit-code 1`
  on subsequent chained invocations so a failed build cannot continue rendering.
- Hash comparison confirmed the saved R5 Blender source was unchanged, but the
  accidentally rerendered perspective PNG differed. Regenerated that view directly
  from the unchanged saved R5 file and refreshed its geometry/render hash record.
  The original PNG bytes were not preserved; the source model and other views were.

## 2026-09-13 — R5 layered toe and curve conversion

- Merely lowering the perforated vamp did not create the intended overlapping
  toe overlay. Expanding the old overlay also left a swallowed seam at the front.
  Replaced that patch boundary with a true inset vamp and a U-shaped overlay
  extending across the toe roof; the insert no longer runs to the toe tip.
- Baking collar and stitch curves exposed disconnected coincident end-cap
  vertices in the mesh check. Added a coincident-vertex weld to the R5 derivative;
  preserved the R4 source and kept geometry validation separate from visual review.

## 2026-09-13 — R4 lace contact checks

- The first construction render concealed lace/tongue and lace/crossing surface
  intersections. Centerline-only height checks missed the width of ribbons on a
  sloping tongue; endpoint interpolation also overrode the intended crossing lanes.
- Revised placement to sample both ribbon edges, apply separate crossing heights,
  and narrow/offset ends at eyelets. A floating bow tail also required draping.
- Direct tongue conformance then pulled some ribbon ends below their eyelets.
  Restored endpoint seating separately from the middle-span fit; a passing
  intersection check alone was not sufficient evidence of correct threading.
- Aperture center rays passed for 14 eyelet and 18 vent openings; this limited
  evidence does not validate physical threading, reinforcement loads, or fit.

## 2026-09-12 — R2 toe junction refinement

- The first right-foot form pass still showed a slight central toe pinch despite
  the shortened tongue and asymmetric footprint. Added continuous-surface
  subdivision before panel thickness and rerendered for inspection.
- Mesh boundary checks alone do not detect this shading/form defect; visual
  inspection remains necessary. No physical fit or interface claim is established.

## 2026-09-12 — Design-master silhouette diagnostics

- Background Blender again exited 139 inside the sandbox; the approved external
  invocation successfully built the separate design-master revision.
- The initial form render lifted the lower toe boundary off the cupsole and
  cropped the top view. Corrected the lower datum and top-camera framing before
  continuing visual review. The first pass was not accepted.
- Recovery comparison covers mesh coordinates, object matrices, parenting and
  render visibility; it does not establish equality of material or UI state.

## 2026-09-12 — Raised toe loft exposed a terminal gap

- Lifting the final forefoot rows exposed an opening at the toe. A planar convex cap did not bridge the evaluated surface edges.
- Removed both adjustments from `refine_v3_finish.py` and regenerated from the preserved construction source. Retained only the badge alignment and curved ribbon bow changes.
- Toe refinement now requires a coherent forefoot/mudguard loft replacement. The rejected toe patch is not a validated closure or a manufacturing-ready feature.

## 2026-09-11 — V3 exploded transform and layer checks

- Initial return-position checks read stale original object matrices after changing view layers. Switched to the active dependency graph's evaluated matrices; start and end return errors are zero.
- The first renders leaked assembled geometry because recursively clearing exclusions also cleared ancestor exclusions. Set the intended top-level collection exclusions directly and verified them after reopening.
- Rebuilt copies use evaluated world-space meshes, retaining source-object references. The final saved file passes module-motion, sole staging, reverse-order, and view-isolation checks. These do not establish physical clearance or manufacturing readiness.

## 2026-09-09 — Joyline fit review after full render pass

- Completed renders revealed exposed inner badge sockets and a rigid tongue/bow.
  Created a separate fit revision instead of replacing the existing source.
- Its first check revealed the tongue Solidify modifier adding thickness above
  the fitted surface and intersecting the laces. Changed padding to extend inward
  and regenerated front/rear checks. Final package acceptance remains pending.
- Impact: private Blender geometry only; original source and renders preserved.

## 2026-09-09 — Local Blender concept launch and first preview corrections

- The sandboxed Blender background process exited with a crash before running
  the approved concept-generation script. The same command ran successfully
  through the approved outside-sandbox execution path.
- The first preview was overexposed at the model's meter scale and revealed
  floating badge details and excessive lace/tongue height. Reduced light power
  and revised surface placement before continuing visual verification.
- Impact: internal development model and preview artifacts only; no deployed
  imagery, application data, or public product claims were changed.
- Additional preview checks caught view-layer exclusions being reset by parent
  toggles and module pivot relocation using stale parent transforms. Applied
  exclusions in two passes, updated transforms before preserving child world
  matrices, and verified the main shell returned to its original world position.
  Low side-view camera rays also began below the floor; moved that orthographic
  camera farther back while preserving its view angle.

## 2026-09-04 — Provider cost review exposed a lowest-tier capability mismatch

- The initial private-preview plan carried forward the owner's lowest-tier
  choice without proving that the free Cloudflare tier could express the exact
  A2.2 waitlist/survey rules or that free Render infrastructure could satisfy
  the recovery and scheduler requirements.
- Resolution: checked current official capability matrices and pricing before
  any provisioning. Cloudflare Free/Pro cannot express the required
  host/method/source-IP 600-second rules, Render Free has no backup/PITR and
  expires after 30 days, and Free web services have no shell/one-off jobs or
  outbound SMTP. Recorded the compatible paid-path estimate and left Plan 8
  stopped pending an owner decision.
- Impact: documentation and gate status only. No provider, credential, DNS,
  R2, email, paid service, or deployment state changed.

## 2026-09-04 — Plan 7 focused test initially inherited unavailable PostgreSQL

- The first documentation-gate verification ran the focused Django test with
  the repository's configured PostgreSQL profile. No local PostgreSQL listener
  was available, so Django failed while creating the test database.
- Resolution: reran the same focused metadata tests with the documented
  disposable SQLite local profile. All eight tests passed; the Cloudflare
  policy validator and whitespace check also passed.
- Impact: local environment failure only; no database, provider, credential,
  or deployment state was changed.

## 2026-09-04 — Plan 6 rehearsal used the wrong local CLI option on its first attempt

- The first rehearsal invocation passed `--python-bin`, but the script's
  supported option is `--python`.
- Resolution: reran with the documented option; the complete local rehearsal
  passed, including the expected public-content blockers and STOP decision.
- Impact: one local command failed before any checks ran; no provider,
  credential, database, deployment, or persistent project state changed.

## 2026-09-04 — Commerce regression setup initially omitted required local Stripe fixtures

- The first disposable commerce-mode test command intentionally supplied no
  Stripe settings and Django failed closed before test discovery, as required
  for commerce configuration.
- Resolution: reran with clearly synthetic, non-provider Stripe fixture values;
  the 22-test commerce homepage/research-boundary subset passed with the
  expected SQLite skips.
- Impact: local configuration failure only; no Stripe request or external
  state was contacted.

## 2026-09-04 — Plan 6 review found the checked-in edge limits drifted from A2.2

- The existing Cloudflare policy described 5/60 requests per minute and a
  blocking action, while the approved A2.2 edge contract is managed challenge
  above 10 waitlist POSTs/IP/10 minutes and above 60 survey POSTs/IP/10
  minutes, staged in log mode first.
- Resolution: corrected the policy, validator, documentation, and regression
  tests; the probe now requires the fixed research/media hostnames and can be
  made to fail when a requested direct-origin check is omitted.
- Impact: repository-only policy and test changes; no Cloudflare, R2, DNS,
  credential, or deployment state changed.

## 2026-09-04 — Supporting-page regression caught accessibility placeholder wording

- The first Plan 5 full research run failed because a new generic test expected
  the privacy page's “Not yet effective” wording on the accessibility page,
  which intentionally says “Working draft.”
- Resolution: kept the existing, more specific accessibility placeholder copy
  and made the regression assertion route-specific. The rerun passed all 171
  installed research tests and the commerce suite passed 277 tests.
- Impact: disposable local test databases only; no provider, credential,
  deployment, or persistent customer state changed.

## 2026-09-04 — Survey upgrade caught stale template assumptions during verification

- The first Plan 4 test pass exposed an error-path lookup using a Django field
  object where a bound field was required for its generated `auto_id`. A
  browser preview also showed the radio-group legend duplicated the visible
  question heading.
- Resolution: derive error IDs from the bound field, keep the native legend
  available to assistive technology with a standard visually-hidden utility,
  and separate free-text prompt copy from its visible answer label. Added
  regression coverage for prompts, radio cards, progress, optional labels,
  Back retention, error linkage, and completion links.
- Impact: disposable local test databases and localhost browser sessions only;
  no provider, credential, deployment, or persistent customer state changed.

## 2026-09-03 — Research-shell verification needed explicit mode and origin fixtures

- The first Plan 3 test invocation used the system interpreter, which lacked
  the locked PostgreSQL driver. The locked virtualenv then correctly refused
  to connect to the unavailable local PostgreSQL service.
- The first focused run also surfaced stale assertions for the retired
  research homepage sections, a private-staging request without its expected
  Cloudflare origin header, and a commerce logo test that tried to reverse
  commerce-only URLs while the test URL configuration was research-only.
- Resolution: used the documented SQLite convenience override for disposable
  tests, updated assertions to the approved six-section research shell, added
  the synthetic origin header, and tested logo selection through the context
  processor. Research and commerce focused suites then passed.
- Impact: disposable test databases and local browser servers only; no
  provider, credential, deployment, or persistent customer state changed.

## 2026-09-04 — Workflow syntax lint helper was unavailable locally

- Attempted to run `actionlint` against the private-preview release workflow.
- Result: the helper is not installed in this workspace, so no actionlint
  result can be claimed.
- Resolution: parsed the workflow with the locked development PyYAML runtime,
  exercised profile-routing assertions, and ran shell/Python compilation and
  whitespace checks. GitHub-hosted workflow execution remains a CI gate.
- Impact: read-only verification only; no workflow, provider, credential, or
  deployment state changed.

## 2026-09-03 — Research baseline review found cross-mode content leakage

- The private-POC content pass had replaced shared About, Contact, and footer
  copy without preserving the commerce variants.
- Result: commerce still functioned, but it rendered research-only preview
  language and the private contact address on shared pages.
- Resolution: made those surfaces mode-specific, restored the existing
  commerce content, and added a two-mode regression test. The complete
  156-test research suite and 262-test commerce suite then passed.
- Impact: repository templates and tests only; no provider, deployment,
  customer, or persistent data was changed.

## 2026-09-03 — Baseline dependency audit needed scoped network access

- The first hash-locked runtime and development audits tried to prepare
  isolated packaging tools behind the restricted network. Retrying with
  dependency resolution disabled confirmed collection but still could not
  reach PyPI's vulnerability service.
- Resolution: reran the read-only audits through the approved dependency-audit
  network boundary; both reported no known vulnerabilities. A separate clean
  temporary Python 3.12 install verified every runtime hash and Gunicorn's MIT
  package metadata because the developer virtualenv did not contain the
  optional license-reporting command.
- Impact: read-only network queries and a disposable `/private/tmp` virtualenv
  only; no project environment, lock, provider, or external state was changed.

## 2026-09-02 — Holding-page dependency fetch needed scoped network access

- Attempted to obtain the disposable npm 11 runner needed to create and verify
  the Phase 1 `package-lock.json` from the default sandbox.
- Result: public npm registry DNS resolution was blocked; no package or
  repository file was changed by the failed fetch.
- Resolution: reran the exact npm-runner download with scoped approved network
  access, generated the lock, completed `npm ci`, and recorded zero known
  vulnerabilities.

## 2026-10-07 — R17 Diagnostic Continuation Path Check

- The first continuation preflight used the old `media/development/` path after
  the project file review had relocated the private design workspace. Reading
  and updating its authorization file failed before Blender was launched; no
  assets changed. Located the current `design/active/` workspace, read its path
  policy, and verified unchanged source/candidate/script hashes. The authorization
  document already contained the relocated pending command, which is the command
  used for the owner's confirmed continuation. Preserve earlier executed-path
  transcripts rather than rewriting historical evidence.
- Trial 03's rendered diagnostics exposed an additional placement-validation gap:
  all 45 left/right object pairs coincide in every new assembled scene. The build
  copied source world transforms without first evaluating the source presentation
  scene. Preserved raw/evaluated geometry and a zero-error return to the candidate's
  own assembled pose do not prove correct source-relative placement. Add explicit
  per-hand source-world-matrix comparisons to the next candidate; do not reinterpret
  the overlap as an intentional single-shoe composition or weaken the geometry gate.
- The two exploded layouts and motion midpoint render successfully but fail visual
  review: components are small, the top background is dark, and the legend is hard
  to read. A studio setup for an assembled shoe does not automatically light a tall
  exploded composition. Improve composition-specific lighting, camera framing and
  flat readable annotations before authorizing a movie batch; preserve diagnostics.
- Impact: no global package, provider, credential, infrastructure, database,
  DNS, or public deployment state changed.

## 2026-09-02 — Wrangler local verification needed isolated writable paths

- Attempted the holding-page dry run with Wrangler's default macOS state path
  and attempted the local server in the default network sandbox.
- Result: the dry run could not create Wrangler's log/configuration directory
  outside the workspace, and the local server could not bind its loopback
  inspector port. Follow-up sandboxed `curl` calls could not cross into the
  approved local-server process boundary.
- Resolution: redirected Wrangler log/configuration/cache state to dedicated
  paths under `/private/tmp`, reran the dry run successfully, and used scoped
  approved loopback access for the local server and two HTTP checks.
- Impact: disposable local logs and browser evidence only; no Cloudflare
  account, Worker, route, DNS, credential, database, or public state changed.

## 2026-09-02 — In-app browser did not expose measurable native zoom

- Attempted to exercise and measure the required 200% browser zoom with the
  in-app browser's keyboard controls after validating the five explicit
  viewport widths.
- Result: repeated zoom shortcuts left the reported viewport, device-pixel
  ratio, and visual scale unchanged, so an exact native 200% result could not
  be claimed from that surface. Its network-idle wait was also unsupported; a
  normal load-state check succeeded instead.
- Resolution: verified a 720 CSS-pixel reflow equivalent to a 1440-pixel
  desktop at 200%, with no horizontal overflow, and retained exact native 200%
  zoom as a deployment-time manual gate in `docs/cloudflare-coming-soon.md`.
- Impact: verification limitation only; no application or external state
  changed.

## 2026-09-02 — Local PostgreSQL was unavailable for the Plan 5 database-backed suite

- Attempted the Plan 5 settings and waitlist test bundle with the repository's
  normal PostgreSQL configuration.
- Result: no local PostgreSQL server was listening on `127.0.0.1:5432`, so
  Django could not create its disposable test database. The failure happened
  before application tests ran.
- Resolution: reran the database-backed waitlist portion with the explicitly
  supported disposable SQLite local profile (30 tests passed, one expected
  skip) and reran the public-settings process suite separately (12 tests
  passed). The repository's CI/Render workflow remains the PostgreSQL evidence
  path.
- Impact: no provider, database, credential, infrastructure, or application
  state changed.

## 2026-09-02 — First Plan 4 adapter probe used zsh's read-only `status` name

- Attempted the repository-only fail-closed Render adapter probe with a shell
  variable named `status`.
- Result: zsh rejected the assignment because `status` is read-only; the
  adapter itself was not reached and no repository or external state changed.
- Resolution: reran the same probe with a task-scoped `rc` variable; the
  adapter correctly exited nonzero when `RENDER_API_KEY` was absent.
- Impact: no provider, credential, infrastructure, deployment, or application
  state changed.

## 2026-09-02 — Repository-wide test discovery mixed deployment modes

- Attempted a repository-wide `manage.py test` run while validating the Plan 3
  observability changes under research mode.
- Result: Django imported commerce-only test modules under the research
  configuration, producing the known mode-isolation and migration failures.
- Resolution: ran the supported installed-app labels separately for research
  and commerce; the focused Plan 3 tests and both mode-specific suites passed.
- Impact: disposable test databases only; no provider, database, credential,
  infrastructure, or application state changed.

## 2026-08-31 — Base-interpreter content check could not initialize PostgreSQL backend

- Attempted a read-only `TREADJOY_MODE=research python manage.py
  check_release_content` rerun after updating the private POC gate.
- Result: the base Anaconda interpreter lacks `psycopg` and `psycopg2`, so
  Django could not initialize its PostgreSQL backend. This is an environment
  limitation, not an application result.
- Impact: no provider, database, credential, infrastructure, or application
  state changed. The prior dependency-locked run remains the valid content
  evidence and still reports the intentional public blockers.
- Resolution: use the project's hash-locked/dependency-complete environment
  for future management-command verification; do not install ad hoc runtime
  packages or reinterpret this failure as a content pass.

## 2026-08-31 — A2.3 Plan 1 prerequisite checks confirmed launch blockers

- Attempted the read-only local research checks for release content and
  research engagement readiness while preparing the A2.3 prerequisite gate.
- Result: `check_release_content` reported the two known blockers
  `homepage-development-media` and `pending-social-links`. The local ignored
  SQLite database also reported three forbidden commerce tables, eleven
  forbidden migration records, three forbidden content types, a draft privacy
  notice, a draft retention policy, and missing staff-role readiness.
- Impact: no provider, credential, infrastructure, DNS, R2, deployment, or
  application source state changed. The local database was not deleted or
  relabeled.
- Resolution: recorded the evidence and explicit stop conditions in
  `docs/a2.3-prerequisite-gate.md`; require a clean research PostgreSQL
  database and effective A1.3/A1.4/A2.2 evidence before provisioning.

## 2026-08-26 — A1.1 branch creation required managed Git approval

- Attempted to create `codex/a1-1-postgresql-ci` with `git switch -c` inside
  the default workspace sandbox.
- Result: Git could not create the nested ref directory beneath `.git/refs`.
- Impact: no source file, branch ref, or application/database state changed.
- Resolution: reran the same scoped branch-creation command after explicit
  managed approval; the implementation branch was created successfully.

## 2026-08-26 — A1.1 staging required managed Git approval

- Attempted to stage the reviewed A1.1 file list and run the cached whitespace
  check.
- Result: the default sandbox could not create `.git/index.lock`, so Git
  stopped before staging any path.
- Impact: no index, source file, commit, or remote state changed.
- Resolution: rerun the same explicit file-list staging command with managed
  Git approval, then repeat the cached diff and status checks before commit.

## 2026-08-26 — A1.1 YAML check used a newer Ruby API signature

- Attempted to parse both workflow files with `YAML.load_file(..., aliases:
  true)`.
- Result: the macOS system Ruby 2.6/Psych version rejected the `aliases`
  keyword before parsing either file.
- Impact: no workflow or repository file changed; the command did not report a
  YAML defect.
- Resolution: reran the parser with Ruby 2.6's positional `YAML.safe_load`
  signature and alias support; both workflow files parsed successfully.

## 2026-08-26 — A1.1 sandboxed dependency audit could not reach PyPI

- Attempted a clean Python 3.12 installation of `requirements-dev.txt` before
  reproducing the new dependency-audit job.
- Result: the default sandbox could not resolve public PyPI, so pip stopped at
  the first package without installing anything into the temporary virtual
  environment.
- Impact: no repository file, existing environment, or database changed.
- Resolution: reran the same hash-enforced installation with approved network
  access and a dedicated temporary pip cache. `pip check` and both runtime and
  development lock audits passed with no known vulnerabilities.

## 2026-08-25 — Local PostgreSQL test database creation

- Attempted the focused A0.1 Django test suite.
- Result: the configured local PostgreSQL role cannot create `test_treadjoy`.
- Impact: the isolated Django test runner could not execute locally.
- Containment: migrations were applied and verified against the local development
  database; rollback-only probes confirmed the cleanup migrations are idempotent
  and preserve protected order history. PostgreSQL CI remains A1.1 work.

## 2026-08-25 — Disposable PostgreSQL verification in the sandbox

- Attempted to start a separate PostgreSQL 17 cluster beneath `/private/tmp`
  for the A0.1 focused migration and release-content suite.
- Result: PostgreSQL could not create its required shared-memory segment
  (`Operation not permitted`) during `initdb`. Retrying with filesystem-backed
  dynamic shared-memory configuration did not reach an initialized cluster.
- Impact: no project database was changed. The sandbox alone cannot host the
  focused PostgreSQL suite.
- Resolution: with approved elevated local-process access, a separate
  temporary PostgreSQL 17 cluster ran the focused commerce suite (94 tests,
  2 skipped) and research suite (31 tests, 3 skipped) successfully. A1.1
  remains the durable CI solution.

## 2026-08-25 — A0.2 research test discovery scope

- Attempted an unlabelled `manage.py test` run in research mode after the A0.2
  route cleanup.
- Result: Django discovered commerce-only cart migration tests even though the
  cart and orders applications are intentionally excluded from research mode;
  those tests could not resolve cart migration nodes. The 76 applicable tests
  completed, while three incorrectly discovered commerce migration tests
  errored during setup.
- Impact: this was a test-selection error, not a research runtime or migration
  failure. The disposable database was destroyed normally.
- Containment: rerun the installed research application suites explicitly and
  retain the deployment-mode subprocess probes that prove commerce imports,
  routes, models, and Stripe remain unavailable.

## 2026-08-25 — A0.2 final check used system Python

- Attempted the final commerce and research Django checks with the unqualified
  `python` executable.
- Result: the system interpreter did not have the project's PostgreSQL driver,
  so Django stopped during application setup before running either check.
- Impact: no database or repository state changed; the earlier disposable
  PostgreSQL suites used the project environment and remained valid.
- Containment: rerun both checks through `.venv/bin/python` and keep that
  interpreter explicit in the final verification commands.

## 2026-08-25 — A0.2 research recheck inherited commerce credentials

- Attempted the final research-mode Django check through the project virtual
  environment without neutralizing Stripe variables loaded for local commerce.
- Result: research mode failed closed during settings initialization, as
  designed, because Stripe credentials were present.
- Impact: no check ran and no state changed; the preceding commerce check
  completed successfully.
- Containment: rerun research verification with the three Stripe variables
  explicitly empty so the process matches a valid research deployment.

## 2026-08-26 — A0.3 standalone development lock omitted setuptools

- Attempted a clean Python 3.12 installation of the generated
  `requirements-dev.txt` with `--require-hashes`.
- Result: pip-tools' `--no-allow-unsafe` output omitted its transitive
  `setuptools` requirement, leaving it unpinned and causing pip to reject the
  development lock under hash-checking mode.
- Impact: the runtime lock installed and passed `pip check`; no project
  database, application code, or existing virtual environment changed.
- Resolution: the standalone development lock now deliberately uses
  `--allow-unsafe` and fully pins/hashes both `pip` and `setuptools`; a second
  clean Python 3.12.14 install passed `pip check`. The runtime lock retains
  `--no-allow-unsafe`.

## 2026-08-26 — A0.3 lock reproducibility comparison used the Git baseline

- Attempted to confirm repeated lock generation with `git diff --exit-code`.
- Result: the command compared the newly generated locks to the pre-A0.3
  tracked freeze, so it reported the intended dependency replacement rather
  than a regeneration difference.
- Impact: the clean runtime and development installations completed; this did
  not indicate a lock nondeterminism or modify the development database.
- Containment: compare checksums immediately before and after a second ordered
  generation run instead of comparing the implementation worktree to `HEAD`.

## 2026-08-26 — A0.3 initial compatible lock failed vulnerability review

- Attempted `pip-audit --require-hashes` against the initial runtime lock.
- Result: 65 known vulnerabilities were reported across Django, Pillow,
  cryptography, and transitive HTTP/parsing packages inherited from the old
  compatible pins. Every report listed a fixed version within the approved
  input ranges.
- Impact: the audit correctly blocked acceptance before application or
  database verification; no suppression was added.
- Containment: regenerate both locks with an explicit compatible upgrade, then
  repeat clean installation, audit, license, and application verification.

## 2026-08-26 — A0.3 static smoke probe omitted Django settings

- Attempted the temporary admin-autodiscovery and static-collection probe with
  a direct Python process.
- Result: the process did not set `DJANGO_SETTINGS_MODULE`, so Django stopped
  before loading either deployment mode.
- Impact: the temporary PostgreSQL cluster shut down cleanly; no static files,
  application records, or development database state changed.
- Containment: rerun both probes with `DJANGO_SETTINGS_MODULE=Shoes.settings`
  and keep the temporary static roots isolated.

## 2026-08-26 — A0.3 Python 3.12.14 PostgreSQL rerun used the macOS account

- Attempted to create fresh disposable PostgreSQL databases and run the final
  Python 3.12.14 mode suite with `DB_USER=ethanschoen`.
- Result: the temporary cluster does not have that role, so database creation
  and subsequent Django connections failed before migrations or tests.
- Impact: the temporary server stopped normally; no application, development,
  or existing disposable database was changed.
- Resolution: reran with the cluster's `postgres` role using new temporary
  databases. Both mode migrations, checks, migration-drift checks, and suites
  passed under CPython 3.12.14; the cluster stopped normally afterward.

## 2026-08-26 — A0.3 direct lock regeneration used an unwritable compiler cache

- Attempted to regenerate both locks in place with the temporary Python 3.12.14
  pip-tools environment.
- Result: pip-tools inherited a cache path beneath the local user library that
  is unavailable to the workspace sandbox, so it stopped before changing either
  lock.
- Impact: the prior lock files and temporary comparison copies remained
  unchanged; no application or database state changed.
- Resolution: set `PIP_TOOLS_CACHE_DIR` to a dedicated temporary directory.
  The subsequent ordered regeneration completed before the final byte-for-byte
  comparison.

## 2026-08-26 — A0.3 sandboxed regeneration could not resolve public PyPI

- Attempted the corrected in-place regeneration with a temporary pip-tools
  cache directory.
- Result: the sandbox could not resolve `pypi.org`, so pip-tools stopped before
  writing either lock.
- Impact: the pre-generation snapshots still match the tracked locks; no
  application or database state changed.
- Resolution: with approved network access, regenerated from public PyPI only
  and then ran a second ordered generation. Both final lock files matched their
  pre-repeat snapshots byte for byte.

## 2026-08-26 — A0.3 final sandboxed audit could not reach the vulnerability service

- Attempted the final `pip-audit --require-hashes` runs after byte-identical
  lock regeneration.
- Result: the sandbox could not resolve the public PyPI vulnerability endpoint,
  so neither audit result was available from that attempt.
- Impact: the locks, application, and databases were not changed.
- Resolution: reran both exact hash-locked manifests with approved network
  access; each reported no known vulnerabilities.

## 2026-08-26 — Cloudflare setup shell did not expose `npx`

- Attempted Cloudflare's published global skills installation command with
  `npx` while setting up the Codex development environment.
- Result: the shell reported `command not found: npx` before downloading or
  installing anything.
- Impact: no global skills, MCP configuration, repository code, or project data
  changed during the failed attempt.
- Containment: use Codex's bundled Node package runner to execute the equivalent
  Cloudflare skills installation, then verify the installed skill paths before
  registering the MCP servers.

### Bundled package-runner retry

- Attempted the equivalent installation through Codex's bundled `pnpm` runner.
- Result: `pnpm` downloaded the `skills` CLI, but the generated launcher could
  not find `node` on the child process `PATH`; the installer itself did not run.
- Impact: only package-manager cache entries were downloaded; no skills, MCP
  configuration, repository code, or project data changed.
- Containment: expose the bundled Node binary directory on `PATH` for the
  package runner, then repeat the same Cloudflare installer arguments.

## 2026-08-26 — Cloudflare OAuth browser handle expired across approval pause

- Attempted to reuse the prior in-app-browser tab handle after the user
  completed the primary Cloudflare OAuth approval.
- Result: the browser session no longer exposed that handle, so the bindings
  authorization page was not opened on the first attempt.
- Impact: no authorization request was submitted and no Cloudflare, MCP,
  repository, or project state changed.
- Containment: reconnect to the in-app browser, open a fresh bindings OAuth tab,
  inspect the page, and preserve it for the required access-grant confirmation.

## 2026-08-26 — Cloudflare OAuth browser assertions did not match the consent flow

- Attempted to combine each MCP server's first approval click with a regular-
  expression callback assertion.
- Result: the browser wrapper rejected that matcher after the clicks advanced
  to Cloudflare's account-level consent pages. A later callback wait timed out
  for the Builds tab, and browser policy correctly blocked reading the local
  callback URLs because they contained OAuth response data.
- Impact: no approval was duplicated. The user-authorized consent flow
  completed, and all three waiting Codex processes reported successful login.
- Containment: treat the CLI login result as the authoritative completion
  signal for local OAuth callbacks and verify final MCP registration through
  `codex mcp list` without inspecting callback URLs.

## 2026-08-26 — A1.1 first GitHub application workflow was invalid

- Attempted the first GitHub Actions run of the new commerce, research, and
  dependency-audit workflow.
- Result: GitHub Actions treats environment-variable names case-insensitively,
  so defining both uppercase and lowercase HTTP proxy names made the workflow
  invalid even though a generic YAML parser accepted the file. No jobs ran.
- Impact: no application command, database service, or provider interaction
  started in that run.
- Resolution: retained the uppercase proxy variables, removed the duplicate
  lowercase spellings, and will require a green GitHub-hosted run before
  accepting A1.1.

## 2026-08-26 — A1.1 first Gitleaks pull-request run lacked metadata permission

- Attempted the first pull-request-triggered Gitleaks v3.0.0 scan with only
  `contents: read` permission.
- Result: the action returned HTTP 403 while listing the pull request's commits
  because the workflow token lacked `pull-requests: read`.
- Impact: checkout completed, but the secret scan did not execute. The action
  did not publish comments or artifacts.
- Resolution: granted read-only pull-request metadata permission while keeping
  repository contents read-only and comments/artifact upload disabled.

## 2026-08-26 — A1.1 Gitleaks action required a license after organization transfer

- Attempted the required Gitleaks v3.0.0 check after transferring the private
  repository from the personal account to the TreadJoy Enterprise organization.
- Result: the action stopped before scanning because its licensing model
  requires a `GITLEAKS_LICENSE` secret for organization-owned repositories.
- Impact: no repository content or provider payload was exposed, but the
  required `Security / Gitleaks` check failed independently of the deliberate
  commerce-job failure used to prove branch protection.
- Resolution: restored the deliberate application failure separately, then
  replaced the licensed wrapper with the approved official Gitleaks CLI image,
  pinned by version and Linux/AMD64 digest. The replacement scans all reachable
  history without a license, provider token, repository secret, comments, or
  uploaded artifacts.

## 2026-08-26 — A1.1 local Gitleaks container reproduction lacked Docker

- Attempted to reproduce the new digest-pinned Gitleaks container command on
  the development workstation before pushing it to GitHub.
- Result: the shell reported `command not found: docker`; the workflow YAML had
  already parsed successfully, but the local container invocation did not run.
- Impact: no image was downloaded and no repository or system state changed.
- Resolution: ran the identical `gitleaks git --redact --no-banner
  --log-opts=--all` scan with the installed Gitleaks 8.30.1 binary; all 45
  commits scanned with no leaks. The exact container command remains subject to
  GitHub-hosted Ubuntu verification.

## 2026-08-26 — A1.1 combined documentation patch used mismatched context

- Attempted one combined patch for the CI documentation and failure log.
- Result: the patch referenced a `MISTAKES.md` heading while matching
  `docs/ci.md`, so validation rejected the complete patch before writing.
- Impact: neither file changed during that attempt.
- Resolution: inspected the current context and applied the two scoped edits
  with file-appropriate anchors.

## 2026-08-26 — A1.1 acceptance-evidence patch used incomplete context

- Attempted to add acceptance evidence to `docs/ci.md` and mark A1.1 complete
  in one patch.
- Result: the documentation hunk omitted part of the surrounding paragraph, so
  patch validation rejected every hunk before writing.
- Impact: no roadmap, documentation, or failure-log content changed during the
  failed attempt.
- Resolution: inspected both exact sections and applied the evidence with the
  full current paragraph boundary as its anchor.

## 2026-08-26 — A1.1 working-directory scan included ignored local secrets

- Attempted `gitleaks dir` to cover the uncommitted acceptance-documentation
  edits before their final commit.
- Result: directory mode also scanned an existing ignored local environment
  file and reported three findings. The command emitted only the finding count;
  no values or paths were printed.
- Impact: no finding was uploaded, logged to a repository file, staged, or
  committed. The ignored local file was not modified or inspected further.
- Resolution: use Gitleaks Git mode for the repository contract, which scans
  every tracked commit and ref. Re-run that full-history scan after committing
  the documentation so the final tracked content is covered without traversing
  ignored developer secrets.

## 2026-08-27 — A1.2 runtime license command assumed a development-only tool

- Attempted to run `pip-licenses` after a clean, hash-enforced runtime-lock
  installation.
- Result: the command was unavailable because `pip-licenses` is intentionally
  a development-only dependency; the runtime installation and its `pip check`
  had already passed.
- Impact: no repository file, database, or production service changed.
- Resolution: use the clean development-lock license report for the five new
  runtime transitive packages and do not add a reporting tool to runtime.

## 2026-08-27 — A1.2 combined license and roadmap patch used stale table context

- Attempted one patch for the license inventory, roadmap status, and failure
  log using an assumed adjacent license-table row.
- Result: patch validation rejected the whole edit before writing because the
  current runtime table did not contain that exact adjacency.
- Impact: no repository file changed during the failed attempt.
- Resolution: inspected the current table and applied the license inventory,
  roadmap, and failure-log edits with exact, scoped anchors.

## 2026-08-27 — Cleanup audit checks initially omitted required settings context

- Attempted the first Django cleanup-audit check without explicitly setting
  `TREADJOY_ENVIRONMENT`, and attempted the first isolated SQLite harness
  without `DJANGO_SETTINGS_MODULE`.
- Result: both processes stopped during settings initialization before running
  an application check or test.
- Impact: no repository, database, provider, or application state changed.
- Resolution: reran with the explicit local environment/mode and with
  `DJANGO_SETTINGS_MODULE=Shoes.settings`; the checks and isolated suites ran.

## 2026-08-27 — Cleanup audit research harness inherited commerce Stripe values

- Attempted the isolated research suite while the local `.env` still supplied
  commerce Stripe variables.
- Result: research settings failed closed before the suite, as designed.
- Impact: no tests, provider calls, database writes, or repository changes
  occurred in that attempt.
- Resolution: explicitly overrode all three known Stripe variables with empty
  process values; the installed-app research suite then passed.

## 2026-08-27 — Cleanup audit local PostgreSQL suite lacked database-creation privilege

- Attempted to run the cleanup baseline through Django's normal PostgreSQL test
  database creation.
- Result: the restricted local role cannot create the test database.
- Impact: no database or repository state changed; the isolated SQLite suites
  do not prove PostgreSQL row-lock behavior.
- Resolution: retained required GitHub PostgreSQL CI and its explicit
  concurrency classes as the durable locking authority; do not grant the local
  runtime role `CREATEDB` to bypass the restriction.

## 2026-08-28 — Phase 0 aggregate preflight was blocked by the default sandbox

- Attempted the read-only cleanup preflight against PostgreSQL on local
  loopback from the default workspace sandbox.
- Result: the sandbox denied the connection before any query reached the
  database.
- Impact: no database or repository state changed and no record value was
  printed.
- Resolution: reran the same aggregate-only ORM command through the approved
  local process boundary. It returned counts only and made no writes.

## 2026-08-28 — Phase 0 README replacement combined incompatible patch operations

- Attempted to replace `README.md` with one patch containing both delete and
  add operations for the same path.
- Result: patch validation rejected the complete operation before writing.
- Impact: `README.md` and every other repository file remained unchanged by
  that attempt.
- Resolution: applied the reviewed replacement as separate delete and add
  patches, then included the file in the documentation validation pass.

## 2026-08-28 — Phase 0 disposable collectstatic harness omitted the settings module

- Attempted isolated static collection after setting a disposable
  `STATIC_ROOT`, but the direct Python harness had not yet defined
  `DJANGO_SETTINGS_MODULE`.
- Result: Django stopped before setup or static collection.
- Impact: no static file, repository path, or application data changed.
- Resolution: reran with `DJANGO_SETTINGS_MODULE=Shoes.settings`; 134 files were
  collected in a disposable directory that was removed on process exit.

## 2026-08-28 — Phase 0 dependency audit assumed the project venv contained dev tools

- Attempted both lock audits through `.venv/bin/pip-audit`.
- Result: the executable was absent because the current project virtual
  environment contains runtime packages rather than the complete development
  lock.
- Impact: no package, lock file, repository file, or environment changed.
- Resolution: used the existing isolated CPython 3.12 audit environments
  created by the dependency/settings work instead of mutating the project
  virtual environment.

## 2026-08-28 — Phase 0 isolated dependency audit was network-blocked

- Attempted runtime and development lock audits from the default sandbox.
- Result: each audit's disposable installer could not upgrade its packaging
  tools because public package metadata was unreachable.
- Impact: no dependency, lock, repository, or application data changed.
- Resolution: reran both exact hash-locked audits through the approved public
  metadata boundary; both reported no known vulnerabilities.

## 2026-08-28 — Phase 1 runtime lock compile used an unwritable cache

- Attempted the first runtime `pip-compile` run with a cache path that was not
  writable by the process.
- Result: compilation stopped before changing the lock file.
- Impact: no dependency, repository, or application state changed.
- Resolution: reran with a disposable writable cache and verified the generated
  runtime lock.

## 2026-08-28 — Phase 1 development lock compile was network-blocked in the sandbox

- Attempted to regenerate `requirements-dev.txt` from the default sandbox.
- Result: PyPI metadata resolution failed with a network name-resolution error
  before the lock file was written.
- Impact: no dependency, repository, or application state changed in that
  attempt.
- Resolution: reran through the approved public metadata boundary, installed
  the resulting hash-locked lock in a disposable CPython 3.12 environment,
  and regenerated the license inventory.

## 2026-08-28 — Phase 1 release-content check could not reach local PostgreSQL

- Attempted the commerce release-content command after the template and auth
  cleanup.
- Result: the default sandbox denied the local PostgreSQL connection before the
  command could inspect catalog rows.
- Impact: no database, provider, repository, or customer state changed.
- Resolution: retained the prior database-backed result (the two known
  homepage-media and pending-social-link blockers) and relied on both-mode
  isolated suites plus disposable static collection for this phase's local
  validation.

## 2026-08-28 — Phase 1 static collection harness needed two corrections

- First attempted to override `STATIC_ROOT` through an environment variable in
  local mode, where settings intentionally do not read that variable; the
  second attempt called the management command before `django.setup()`.
- Result: both harnesses stopped before collecting files.
- Impact: no repository or application state changed.
- Resolution: set `settings.STATIC_ROOT` in a disposable, initialized Django
  process; 134 files were then collected successfully and the temporary
  directory was removed.

## 2026-08-28 — Phase 2 cart-merge test initially used a non-reducing fixture

- Attempted to verify an availability-reduction notice with two account units,
  one guest unit, and three units of stock.
- Result: the merge correctly accepted all three units, so no reduction notice
  was emitted and the assertion failed.
- Impact: no repository or application data persisted beyond the isolated test
  database.
- Resolution: changed the fixture to two units of stock and asserted the
  visible cap and resulting quantity of two.

## 2026-08-28 — Phase 2 broad research discovery included commerce-only migration tests

- Attempted the full unconstrained test discovery command in research mode.
- Result: three existing quarantine migration tests referenced cart migration
  nodes that are intentionally absent when commerce apps are not installed.
- Impact: no repository or application data changed; the mode boundary itself
  remained intact.
- Resolution: reran the research suite using its installed-app labels
  (`web.core`, `web.products`, `web.survey`, `web.waitlist`, and `web.accounts`),
  which passed 86 tests with 6 intentional skips. Commerce runs retain the
  cart/order migration tests.

## 2026-08-28 — Phase 3 formula constraints were stricter than legacy order rows

- Attempted to add database checks requiring `grand_total` to equal the
  decomposed subtotal, shipping, tax, and discount fields and each order-line
  total to equal unit price times quantity.
- Result: existing fixtures and legacy pending/paid records contain a total
  snapshot without a decomposed subtotal, so payment/webhook tests failed at
  the database boundary.
- Impact: no production or persistent customer data changed; the isolated
  migration database was discarded.
- Resolution: retained safe nonnegative and discount bounds, removed the
  formula checks before they could be applied, and recorded a verified
  legacy-total backfill as a prerequisite for a future constraint migration.

## 2026-08-28 — Phase 3 catalog query probe initially reused per-SKU product instances

- Attempted to use prefetched preorder batches while each prefetched variant
  still held a separate `product` instance.
- Result: the probe remained at 18 queries because availability lookups could
  not see the parent product's prefetch cache.
- Impact: no repository or application data changed.
- Resolution: reattached the parent product instance to prefetched variants;
  the five-product/three-variant probe now completes in 3 queries and remains
  constant as variants increase.

## 2026-08-28 — Phase 3 release-content command was run without migrated fixtures

- Attempted to run `check_release_content` against an in-memory SQLite database
  outside the test runner.
- Result: the command correctly stopped because the disposable database had no
  `products_product` table.
- Impact: no repository, provider, or application data changed.
- Resolution: treated the earlier fixture-backed release-content checks as the
  valid local evidence; the standalone invocation was not a product failure.

## 2026-08-28 — Bare runserver initially conflicted with the local .env profile

- The first fallback forced research mode while the ignored local `.env` still
  supplied Stripe values, so settings correctly rejected the mixed profile.
- A second direct run reached Django's migration check but the sandbox denied
  binding a local listening socket.
- Resolution: the fallback now honors a configured `.env` mode, clears Stripe
  only when research is the unconfigured default, and selects SQLite for a bare
  local runserver when no database variables are explicitly supplied. Explicit
  PostgreSQL configuration remains unchanged; socket binding still requires a
  normal local environment outside this sandbox.

## 2026-08-28 — Phase 4 checkout tests exposed legacy assumptions

- The first checkout-attempt integration retained visible tests that expected a
  locally persisted full shipping address and automatic success-page refresh.
- Result: those assertions failed after the Stripe-hosted address and manual
  status-check behavior were introduced.
- Impact: no persistent production data changed; the isolated test database was
  discarded.
- Resolution: updated the tests and flow to defer the address to Stripe and to
  expose a bounded manual status check, while retaining a compatibility path for
  legacy webhook orders during the expand/contract period.

## 2026-08-28 — Phase 4 migration generation initially lacked explicit mode configuration

- Attempted `manage.py makemigrations` without the explicit environment and
  deployment mode required for non-runserver commands.
- Result: settings failed closed on missing `TREADJOY_ENVIRONMENT` before any
  migration was generated.
- Impact: no repository, database, provider, or customer data changed.
- Resolution: reran with the documented local commerce profile. Django
  generated migrations `0020` and `0021`; its migration-history probe could
  not reach sandboxed local PostgreSQL, so migration execution was verified in
  isolated SQLite and remains subject to PostgreSQL CI/deployment acceptance.

## 2026-08-28 — Active-attempt uniqueness was first inserted into the wrong model block

- A context-short model patch initially placed the conditional active-checkout
  uniqueness constraint in `Order.Meta` instead of `CheckoutAttempt.Meta`.
- Result: immediate reference inspection found the misplaced `cart` constraint
  before Django checks, migrations, or tests were run against it.
- Impact: the invalid intermediate edit was never migrated or applied to data.
- Resolution: moved the constraint to `CheckoutAttempt.Meta`, added an
  aggregate-only migration that quarantines older duplicate active attempts,
  and reran migration-drift and application tests successfully.

## 2026-08-28 — Phase 4 completion exposed two more pre-attempt test assumptions

- The first complete commerce run still had a preorder test that expected an
  `Order` before Stripe reconciliation and a deployment probe that expected
  the deprecated process-global `stripe.api_key` assignment.
- Result: one test errored and one subprocess assertion failed; all other tests
  completed against the isolated database.
- Impact: no persistent database or provider state changed.
- Resolution: updated the preorder test to verify the immutable attempt quote,
  then reconcile the retrieved paid Session into an order, and changed the mode
  probe to require no global Stripe key. The complete SQLite commerce suite
  subsequently passed 178 tests with 10 intentional skips.

## 2026-08-29 — Bare runserver selected an empty SQLite database beside a configured .env

- Attempted the documented local `runserver` path while the ignored `.env`
  contained a complete PostgreSQL profile.
- Result: the startup helper checked only process-environment database values,
  selected the zero-byte ignored `db.sqlite3`, reported 76 unapplied migrations,
  and the homepage failed because `products_parttype` did not exist. The exact
  system-Python command also loaded Django 6.0 instead of the locked Django 5.2
  line and failed while importing model constraints.
- Impact: no commerce records changed. The empty SQLite file was the only
  database artifact created, and the configured PostgreSQL database remained
  untouched during diagnosis.
- Resolution: database-profile detection now reads process and `.env` values
  through `python-decouple`, the project virtual environment was rebuilt on
  Python 3.12 from the hash-locked development requirements, the empty SQLite
  artifact was removed, and the migrated PostgreSQL-backed server passed the
  browser smoke matrix.

## 2026-08-29 — Runserver regression probes initially inherited the developer .env

- The first expanded subprocess suite changed its working directory to isolate
  test `.env` files, assuming `python-decouple` began discovery there.
- Result: four probes failed because the imported project module anchored
  discovery to the repository `.env`; the partial-profile probe also used a
  compound `try` statement after a semicolon, which is invalid Python syntax.
- Impact: only the isolated test run failed; no database, provider, or customer
  state changed.
- Resolution: the harness now supplies one temporary-directory `AutoConfig`
  object before importing either `manage.py` or Django settings, and the
  partial-profile script uses valid multiline syntax. All 16 deployment-mode
  process tests then passed.

## 2026-08-29 — Python 3.12 dependency installation was network-blocked in the sandbox

- Attempted the hash-enforced development-lock installation in the replacement
  project virtual environment through the default sandbox.
- Result: package-index name resolution failed before any dependency was
  installed.
- Impact: the previous Python 3.11 virtual environment remained intact in its
  rollback directory, and no repository or application data changed.
- Resolution: reran the exact hash-locked install through the approved network
  boundary. The Python 3.12 environment then passed `pip check` and the focused
  startup/homepage tests.

## 2026-08-29 — The first local PostgreSQL commerce suite reused a stale test schema

- Attempted the complete commerce suite with `--keepdb` against the existing
  dedicated PostgreSQL test database.
- Result: removed `socialaccount_*` tables and leftover fixtures prevented
  Django from flushing the current installed-app graph, producing two failures
  and eight cleanup errors.
- Impact: the authoritative local commerce database was not used or changed by
  the failed suite; contamination was confined to the role-owned `test_`
  database.
- Resolution: verified the exact test-database prefix, ownership, stale tables,
  and absence of other connections, reset only its `public` schema, and reran
  migrations through Django's test runner. The complete PostgreSQL commerce
  suite then passed 183 tests with 6 intentional skips.

## 2026-08-30 — Phase 5 checks initially used incomplete and invalid local profiles

- First attempted `manage.py check` without the explicit environment required
  for non-runserver management commands, then retried with the invalid
  environment name `development` instead of the documented `local` value.
- Result: both commands failed closed while loading settings, before Django
  opened a database or ran a check.
- Impact: no repository, database, provider, or customer data changed.
- Resolution: used the documented `TREADJOY_ENVIRONMENT=local` profile and the
  project virtual-environment interpreter for subsequent verification.

## 2026-08-30 — Phase 5 validation briefly used the system Python interpreter

- Attempted the explicit local-commerce Django check with `python` rather than
  `.venv/bin/python`.
- Result: the system environment lacked the locked PostgreSQL driver and failed
  while Django initialized its database backend.
- Impact: settings initialization stopped before any query or migration; no
  data or repository state changed.
- Resolution: reran through the Python 3.12 project environment. Both-mode
  checks and migration-drift detection then passed, with the known sandboxed
  local-PostgreSQL history warning remaining a CI/deployment gate.

## 2026-08-30 — Broad research test discovery imported commerce-only migration tests

- Attempted `manage.py test web` in research mode after Phase 5.
- Result: Django correctly omitted the commerce apps and their migration graph,
  but broad filesystem discovery imported three cart migration test classes
  whose explicit migration targets cannot exist in research mode. Ninety-six
  other tests completed; the three imported migration tests errored before
  their setup.
- Impact: the isolated research test database was discarded and no persistent
  data changed. The research application check itself passed.
- Resolution: reran the installed research application labels used by CI
  (`web.core`, `web.products`, `web.survey`, `web.waitlist`, and
  `web.accounts`). All 93 tests passed with 6 intentional skips. The commerce
  migration tests remain confined to the commerce job rather than weakening
  the research boundary.

## 2026-08-30 — Preserved PostgreSQL test data lost a data-migration seed

- Attempted the complete commerce suite with `--keepdb` against the existing
  dedicated PostgreSQL test database after applying the Phase 5 migrations.
- Result: 193 of 194 tests passed, including the concurrency classes. One
  unrelated homepage assertion found zero modular part types because an older
  preserved test run had flushed rows originally created by a data migration;
  Django correctly considered that migration applied and did not reseed them.
  The isolated homepage rerun reproduced the stale-data condition.
- A clean no-`--keepdb` retry then failed before testing because the
  least-privilege application role correctly has `NOCREATEDB` and cannot
  recreate the test database itself.
- Impact: only the role-owned `test_treadjoy` database was involved. The
  authoritative development database, provider state, and repository data were
  not changed, and the database role was not granted broader privileges.
- Resolution: ran all 35 focused Phase 5 order/refund/shipment/admin tests plus
  the established finished-SKU, preorder, and Checkout concurrency classes on
  PostgreSQL; all passed. A clean full-suite database bootstrap remains a CI
  acceptance gate rather than weakening role permissions or adding runtime
  reseeding code to hide a test-database artifact.

## 2026-08-30 — Phase 5 disposable static harness omitted `CI_STATIC_ROOT`

- Attempted `collectstatic` with a unique temporary public `STATIC_ROOT` but
  omitted the separate absolute `CI_STATIC_ROOT` required by
  `Shoes.ci_settings`.
- Result: settings failed closed before Django loaded the command or copied a
  file.
- Impact: the temporary directory remained empty; repository and persistent
  application data were unchanged.
- Resolution: supplied both variables with the same disposable directory. The
  rerun copied the expected 134 static files successfully.

## 2026-08-30 — Phase 5 dependency audit was initially network-blocked

- Attempted the read-only locked-runtime `pip-audit` query inside the default
  network sandbox.
- Result: DNS resolution for the public vulnerability index failed; no package
  was installed, upgraded, or removed.
- Impact: dependencies, lock files, and application data were unchanged.
- Resolution: reran the same read-only audit through the approved network
  boundary. It reported no known vulnerabilities.

## 2026-08-30 — Phase 6 test discovery used two invalid scopes before the documented suites

- First attempted a focused test label named `web.products.tests.test_views`,
  which does not exist; 47 other selected tests ran and the command ended with
  one import error. The corrected `test_catalog` selection passed 58 tests with
  7 intentional skips.
- A later bare research-mode `manage.py test` discovered commerce-only cart
  migration tests from the filesystem. The correctly excluded commerce
  migration graph made those three classes error while 97 other tests ran.
- Impact: both attempts used disposable SQLite test databases; no persistent
  record, provider state, or repository file changed.
- Resolution: used the installed research app labels documented in README and
  CI. The final suites passed 195 commerce tests with 10 skips and 94 research
  tests with 6 skips.

## 2026-08-30 — Phase 6 diagnostics initially used unsuitable local defaults

- The first catalog query probe used Django's default `testserver` host and
  correctly received `DisallowedHost`, so its 400 response and zero-query count
  were discarded. The rerun supplied the allowed local host and rendered in 3
  queries.
- Initial local server binding and loopback timing requests were blocked by the
  default sandbox, and `curl` was unavailable. The read-only server and five
  `urllib` requests were rerun through the approved local boundary.
- A first browser pass also retained no-reload CSS state, and full-page image
  stitching repeated sticky/footer regions. Fresh server ports and authoritative
  viewport captures were used for the final review.
- Impact: all data was unmistakably synthetic in an ignored, disposable SQLite
  database; no customer, provider, production, or shared database was accessed.

## 2026-08-30 — Phase 6 dependency audit required the approved network boundary

- The first `pip-audit` run failed inside the default sandbox while its
  temporary environment tried to update pip; no installed or locked dependency
  changed.
- Resolution: reran both hash-locked manifests through the approved read-only
  network boundary. Both reported no known vulnerabilities, and the unchanged
  license inventory was reverified.

## 2026-08-30 — Runserver diagnosis used the misspelled command and system Python

- Attempted the exact `pyhthon manage.py runserver` command; the shell correctly
  reported that `pyhthon` was not found.
- Retried with system `python`; it loaded Django 6.0 instead of the project's
  locked Django 5.2 line and failed because the system environment had neither
  `psycopg` nor `psycopg2`.
- Retried with `.venv/bin/python`; the project dependencies were correct, but the
  ignored local `.env` selected a PostgreSQL commerce profile and no local
  PostgreSQL server was reachable at `127.0.0.1:5432`.
- Impact: settings initialization and migration inspection stopped before any
  commerce query or mutation. The isolated SQLite preview database was the only
  local artifact initialized, and no configured PostgreSQL data was changed.
- Resolution: initialized the documented local research/SQLite preview with
  explicit environment variables and migrations. The project virtual
  environment then passed Django checks and started successfully on
  `127.0.0.1:8000` in a normal terminal; the temporary server was stopped after
  verification.

## 2026-08-30 — A2.1 public-profile probes still read the developer `.env`

- Attempted the focused production-settings suite after making public research
  manifests reject even empty `STRIPE_*` process variables.
- Result: 13 cases failed before their intended assertions because
  `python-decouple` found the ignored project `.env` through its settings-module
  search path. Merely changing the subprocess working directory did not change
  that search behavior.
- Impact: the failures occurred during settings import. No application,
  database, provider, or repository data was changed, and no configured value
  was printed by the test assertions.
- Resolution: run each public-profile probe from a temporary directory and
  explicitly bind `decouple.config` to that directory before importing Django.
  The rerun passed all 20 focused production/deployment-mode cases and now
  proves both an absent public research Stripe manifest and isolated settings
  inputs.

## 2026-08-30 — A2.1 documentation search used unsafe shell quoting

- Attempted an `rg` documentation audit with Markdown backticks inside a
  double-quoted shell argument. The shell interpreted fragments as command
  substitutions and the resulting search output was invalid.
- Impact: the read-only command changed no repository, database, provider, or
  user data and printed no secret value.
- Resolution: reran the audit with a focused, single-quoted expression and
  retained the repository's documented rule against risky shell escaping.

## 2026-08-30 — A2.1 workflow audit used an unavailable Ruby/Psych helper

- Attempted to parse the application CI workflow with `YAML.safe_load_file`,
  which is not available in the installed Ruby/Psych version.
- Impact: parsing stopped immediately; the read-only command changed no file,
  CI configuration, or external state.
- Resolution: used the compatible `YAML.safe_load(File.read(...), aliases:
  true)` interface for the final workflow syntax check.

## 2026-08-30 — A2.2 migration generation exposed stale imports and local provider settings

- A combined delete/add `apply_patch` was rejected before changing a model;
  the edit was reapplied as atomic delete and add operations.
- The first migration-generation probe inherited nonempty Stripe values from
  the ignored developer `.env` and correctly failed the research boundary.
  The next probe reached a stale `WaitlistSignup` admin import and stopped.
- Resolution: neutralized provider values only for the explicit local command,
  updated admin imports first, then generated and manually converted the
  waitlist migration to a data-preserving rename/quarantine migration.
- Impact: both failed commands stopped before database access; no provider,
  persistent data, or secret value was changed or printed.

## 2026-08-30 — A2.2 lock regeneration needed writable caches and approved network

- The first `pip-compile` used the host's non-writable pip-tools cache. The
  retry used `/private/tmp` but DNS was blocked by the default sandbox.
- Resolution: regenerated both hash locks through the approved network
  boundary with task-scoped writable caches, then installed only the locked
  Resend SDK to inspect its exact webhook/contact/segment/broadcast signatures.
- Impact: the failed runs changed no lock or installed package; the successful
  run intentionally updated both reviewed locks and the project virtualenv.

## 2026-08-30 — A2.2 focused tests initially retained A2.1 account/waitlist assumptions

- The first focused suite found expected stale tests importing
  `WaitlistSignup`, asserting removed survey identity columns, and rendering
  allauth profile links in research. It also found a mobile account block that
  still reversed allauth routes.
- Resolution: removed the research account block, expanded the clean-process
  import/route proof, and replaced the old waitlist assertions with double
  opt-in, digest-token, CSRF, throttling, suppression, outbox, and retention
  tests. The rerun passed 58 tests with two PostgreSQL-only skips.
- Impact: disposable SQLite test databases only; no persistent or provider
  data was used.

## 2026-08-30 — A2.2 privacy routing initially broke shared commerce surfaces

- The first commerce regression run found eight failures after `/privacy/` was
  registered only in research mode even though shared survey/order templates
  still reverse that route in commerce.
- Resolution: kept the research notice route shared while preserving the
  research-only effective-content/configuration contract. The affected tests
  and the later 232-test commerce suite passed.
- Impact: disposable test databases only; no public route, provider, or
  persistent deployment was changed.

## 2026-08-30 — A2.2 design tooling was partly unavailable and initially over-scoped

- The first strict premium-UI audit traversed `.venv` and reported dependency
  sources unrelated to the maintained interface. A scoped `premium-ui.json`
  manifest fixed the audit boundary and the strict rerun reported no findings.
- `npx -p @google/design.md designmd lint DESIGN.md` could not run because this
  workspace has no Node/npm runtime. No runtime was installed merely to satisfy
  a documentation lint helper; the design contract and front matter were
  checked with the available local tools instead.
- Impact: read-only validation only; no design-system token or dependency was
  changed by either failed attempt.

## 2026-08-30 — A2.2 unrestricted research test discovery imported excluded apps

- Running bare `manage.py test` in research mode imported test modules for
  `web.accounts`, `web.cart`, and `web.orders`, even though those apps are not
  installed. That predictably caused account-test route errors and made the
  runtime import boundary fail.
- Resolution: retained repository-wide discovery for commerce and used the
  documented explicit installed research labels (`web.core`, `web.products`,
  `web.survey`, `web.waitlist`). That 126-test suite passed with six expected
  SQLite/PostgreSQL skips, and CI uses the same labels.
- Impact: disposable SQLite test databases only. The product boundary was not
  weakened and excluded app code is not imported by the passing research run.

## 2026-08-30 — A2.2 disposable Browser verification needed scoped retries

- The first local server bind was denied by the sandbox and was rerun through
  the approved localhost runserver boundary. Two read-only selectors also used
  stale assumptions: the honeypot is named `company_website`, and the mobile
  navigation button changes from “Open navigation” to “Close navigation.”
- A scripted second-survey loop looked for another “Next Question” button after
  the application had already returned the expected 24-hour 429 response.
  Inspecting the fresh DOM confirmed the throttle instead of repeating the
  action.
- Resolution: corrected the selectors, verified the fresh DOM after each state
  change, reset the Browser viewport, stopped the server, and deleted the exact
  disposable SQLite database and temporary settings file.
- Impact: synthetic `example.test` identities and a temporary database only;
  no Resend call, real personal data, or project database was used.

## 2026-08-30 — A2.2 dependency audit first ran behind blocked network access

- The first hash-locked runtime audit could not prepare its isolated audit
  environment because package-index access was blocked by the default sandbox.
- Resolution: reran the runtime and development lock audits through the
  approved dependency-audit network boundary with a task-scoped cache. Both
  reported no known vulnerabilities.
- Impact: the failed attempt changed no dependency or lock; the successful
  audits were read-only against the already regenerated lock files.

## 2026-08-30 — A2.2 public import probe briefly overreached into Django auth internals

- A strengthened clean-process probe initially blocked every import under
  `django.contrib.sites`. Django's built-in auth admin imports the sites
  shortcut module even when the sites app is not installed, so the valid
  research startup failed before the intended boundary assertions.
- The first direct engagement-command success test also used the deliberately
  draft local notice/blank retention defaults, so the command correctly
  refused to pass. A combined corrective patch then missed context because the
  two target snippets lived in different test files.
- Resolution: kept the installed-app/table/migration/content-type prohibition
  for sites, limited import blocking to allauth/accounts/commerce/Stripe, and
  supplied synthetic effective versions only in the success test. The focused
  and final suites passed.
- Impact: subprocess and disposable test databases only; no boundary was
  relaxed for installed capabilities and no persistent configuration changed.

## 2026-08-31 — Bare runserver diagnosis distinguished environment failures

- `python manage.py runserver` from the project directory loaded the ignored
  local `.env`, which supplies research mode plus Stripe variables. The
  fail-closed research settings rejected those variables before startup.
- The shell's `python` is `/opt/anaconda3/bin/python` with Django 6.0, while
  the project lock uses `.venv` with Django 5.2.17. The system interpreter
  therefore failed later on Django's renamed `CheckConstraint` argument.
- Resolution: the locked `.venv/bin/python manage.py runserver` started on a
  localhost-only port when provider/database overrides were explicitly empty;
  the server was stopped immediately after the smoke test. No application
  database or provider was contacted or changed.

## 2026-08-31 — Google Workspace Gmail activation remained pending after valid DNS propagation

- Cloudflare already contained the sole required root MX record
  (`smtp.google.com`, priority 1) and the Google SPF TXT record. Google Public
  DNS independently returned that MX record with a successful response.
- Two Google Workspace activation checks nevertheless ended with “Unable to
  verify at the moment” after several minutes each.
- Resolution: made no speculative DNS changes and left Workspace on its safe
  retry screen. The remaining dependency is Google's activation-side
  propagation; retry after its documented delay rather than duplicating or
  replacing the valid records.
- Impact: no DNS record was created, deleted, or modified. The only external
  actions were two Workspace verification attempts.

## 2026-09-05 — Access verification checks needed isolated local settings

- The first combined focused Django test command inherited the ignored local
  PostgreSQL configuration and could not reach `127.0.0.1:5432` inside the
  filesystem sandbox. A mocked missing-token test also initially returned the
  mock's default success value instead of exercising the verifier's fail-closed
  branch.
- The first attempt to restore the documented lock-generation flags ran inside
  the sandbox and could not write pip-tools' user cache.
- Resolution: corrected the test mock to reject an empty token, ran the
  database-free suites separately, ran the broader research regression suite
  against a disposable SQLite database with explicit local settings, and
  regenerated both locks through the approved pip-tools boundary using the
  exact documented commands. All resulting tests, lock installs, secret scan,
  and dependency audit passed.
- Impact: disposable local test data and dependency caches only; no provider,
  DNS, Access policy, public route, or live deployment was changed.

## 2026-09-05 — Local GitHub CLI status check was unavailable

- After pushing the Access-verification commit, the attempted read-only
  `gh run list` check failed because GitHub CLI is not installed in this
  workspace.
- Resolution: verified the clean worktree and pushed commit identifier with
  Git itself. CI remains the remote deployment gate; no replacement CLI or
  credentials were installed merely to inspect it.
- Impact: none; the failed command did not reach GitHub or change local or
  provider state.

## 2026-09-05 — Research PostgreSQL CI exposed a nullable-row lock query

- The first current-commit Application CI run passed commerce and dependency
  checks but failed the research PostgreSQL suite in the research email delivery
  command. Reproducing the suite against disposable PostgreSQL logged
  `FOR UPDATE cannot be applied to the nullable side of an outer join` for the
  nullable `ResearchOutboundEmail.subscription` relation.
- Resolution: changed the command to use `select_for_update(of=("self",))`,
  locking only the authoritative outbox row while retaining the joined
  subscription data. The complete 181-test research suite now passes against
  PostgreSQL and the 287-test commerce suite passes against SQLite.
- Impact: only disposable local PostgreSQL/SQLite test data was used; no
  provider, credential, customer, or deployment state changed.

## 2026-09-05 — Local research boundary checks first used the wrong profile

- A boundary probe accidentally used the populated development SQLite database,
  so the research capability check reported the expected commerce tables. A
  clean local PostgreSQL probe then passed the capability boundary, while the
  engagement check correctly refused draft privacy/retention settings and a
  synthetic privacy-notice digest that did not match its body.
- Resolution: reran the checks on a fresh disposable PostgreSQL database with
  the CI-approved synthetic notice and retention values. Boundary, engagement,
  Cloudflare-policy, and whitespace checks passed.
- Impact: no application, provider, credential, or persistent database state
  was changed; only disposable local databases were created.

## 2026-09-05 — Final documentation verification first used the system interpreter

- The first local `manage.py check` invocation used `/opt/anaconda3/bin/python`
  (Django 6.0), while the repository's locked environment is `.venv` with
  Django 5.2.17. Startup therefore failed on the removed `CheckConstraint`
  `check=` argument before any application checks ran.
- Resolution: reran the check, migration-drift check, compilation, and focused
  metadata/research rehearsal tests with `.venv/bin/python` and explicit local
  research settings. All passed; the SQLite run emitted only expected comments
  unsupported warnings.
- A local commit attempt for the documentation corrections was denied because
  this workspace exposes `.git` read-only. The corrections remain as a clean,
  reviewable working-tree diff; no push or remote mutation was attempted.
- Impact: no application, provider, credential, or database state changed.

## 2026-09-05 — Holding-page verification needed the bundled Node boundary

- The first verification command assumed `npm` and `npx` were on the shell
  path; neither executable was available. A stale local Wrangler shim then
  referenced a missing package, and the first downloaded CLI invocation could
  not locate Node. The first sandboxed Wrangler and local `curl` checks also
  could not write Wrangler diagnostics or reach the separately hosted preview.
- Resolution: ran the nine package tests with the bundled pinned Node 24.19.0
  executable, downloaded the repository-pinned Wrangler 4.128.0 package, and
  ran Wrangler and the local HTTP probes through their approved boundaries.
  The tests, deployment dry run, browser matrix, and HTTP header checks passed.
- Impact: only package-manager caches, Wrangler diagnostic logs, and a
  disposable local preview were used. No credential, DNS record, Worker
  binding, public route, or deployed Worker version changed during these
  failed attempts.

## 2026-09-05 — Holding-page package runner was unavailable in the shell

- The existing uncommitted holding-page visual revision could not be run with
  its declared `npm test` command because this workspace shell has neither npm
  nor a Node executable available from the project directory.
- Resolution: preserved the pre-existing revision, used the bundled browser
  runtime for a read-only contract check of its HTML/CSS/security invariants,
  and left the full Node test as a follow-up for a Node 24 environment.
- Impact: no asset, deployment, Cloudflare, credential, or remote state was
  changed by the failed command.

## 2026-09-05 — Rehearsal manifest retained a stale provider-absence reason

- The current research rehearsal still described Render staging resources and
  live evidence as absent, although the owner-approved private Render POC and
  its database are provisioned.
- Resolution: changed the STOP reason to distinguish the existing private POC
  from the still-pending current-release promotion, Cloudflare edge wiring, and
  public evidence. A fresh rehearsal passed all local checks and recorded the
  corrected reason while retaining `launch_decision: STOP`.
- Impact: manifest wording only; no provider, credential, database, DNS, R2,
  or deployment state changed.

## 2026-09-05 — Holding-page tests were rerun through the bundled Node runtime

- The shell still lacks `npm` and a project-local Node executable, so the
  package script could not be invoked directly.
- Resolution: used the bundled `node:test` runner through the Computer Use
  runtime against the same test file. All nine holding-page tests passed;
  Wrangler dry-run remains provider-tooling evidence from the existing local
  record and was not re-run here.
- Impact: read-only test execution only; no Worker, Cloudflare, or asset state
  changed.

## 2026-09-05 — Full-page browser captures were rejected as scaled artifacts

- The first live holding-page and 404 full-page screenshots were visually
  scaled to roughly half the CSS layout even though DOM measurements were
  correct, so they were not suitable as audit evidence.
- Resolution: rejected those files, captured normal viewport screenshots at
  desktop and 390px mobile sizes, inspected each saved image, and retained
  only the accepted captures in `/private/tmp/treadjoy-visual-audit-2026-09-05`.
- Impact: read-only screenshots only; no website or external state changed.

## 2026-09-05 — Holding-page release inherited failing repository checks

- The approved release push bypassed four expected branch checks, and the
  GitHub connector could not read the private commit status. Wrangler also
  could not list account deployments without introducing an API token, the
  first timed browser wait expired, and the first redirect probes omitted
  shell quoting around query strings.
- Resolution: inspected the existing signed-in Cloudflare and GitHub dashboards
  without creating credentials, then reran the quoted public probes. Cloudflare's
  package build succeeded and deployed the reviewed version to 100% traffic.
  GitHub's commerce PostgreSQL and dependency-audit jobs passed; the research
  PostgreSQL job reproduced the already-recorded nullable outer-join lock error,
  and Gitleaks reported the same two full-history findings as the preceding
  commit. No secret values were opened or reproduced.
- Impact: the holding page is deployed and verified, but the inherited research
  CI and full-history secret-scan failures remain unresolved repository risks.
  No API token, binding, DNS rule, account permission, or billing state changed.

## 2026-09-05 — Access origin denial lacked a safe diagnostic category

- The first owner OTP authentication passed Cloudflare Access but received the
  middleware's intentionally generic `403 Forbidden` response. Existing logs
  did not distinguish an origin-secret mismatch from an invalid application
  token, so changing provider policy speculatively would have weakened the
  evidence chain.
- Resolution: added categorical `Shoes.security` events for origin denial,
  Access-token denial, and signing-key unavailability. The events contain no
  email, token, secret, provider identifier, or request data, and the focused
  middleware/settings suite passed.
- The diagnostic commit's first full-history Gitleaks run failed on two
  synthetic Access audience fixtures introduced in `1c4e69e`. Added only the
  two exact historical fingerprints to `.gitleaksignore`; no detection rule or
  path was broadly excluded.
- Impact: the private hostname remained Access-protected and the Render
  subdomain remained disabled. No access policy, origin secret, credential, or
  database permission was weakened.

## 2026-09-05 — Origin-lock value appeared in dashboard inspection output

- While locating the active request-header transform rule, the dashboard's
  accessible row text included the complete origin-lock shared value and the
  inspection result was emitted to the task transcript.
- Containment: stopped the live configuration workflow immediately, did not
  reuse or repeat the value, and requested action-time owner approval to rotate
  it in both Render and Cloudflare before resuming verification.
- Impact: the value must be treated as exposed until both provider settings use
  a newly generated replacement. Access remains enabled, the Render-provided
  subdomain remains disabled, and no database credential was involved.

## 2026-09-05 — Origin-lock rotation did not restore the authenticated path

- After rotating the shared value in both provider dashboards and redeploying
  Render, the authenticated research request still returned `403`.
- Resolution: added an allow-listed diagnostic shape containing only header
  presence, header length, and whether the server-side secret is configured.
  The next live event showed the forwarded header was absent (`length=0`) while
  the secret was configured; no secret value was logged.
- Impact: the remaining fault is Cloudflare-to-origin header delivery or rule
  ordering, not a credential mismatch. Access and the disabled provider
  subdomain remain intact.

## 2026-09-05 — Research Release workflow remains blocked by content gates

- The release workflow for the diagnostic commit stopped before promotion
  because its existing public-like content gate found
  `homepage-development-media` and `pending-social-links`.
- Resolution: treated this as a pre-existing release-policy blocker, while the
  required Application CI and Secret Scan checks passed. No content gate was
  bypassed and no public promotion was attempted.
- Impact: staging verification used the approved manual Render deployment after
  required checks passed; the immutable Research Release workflow remains
  unavailable until those separate content gates are resolved.

## 2026-09-06 — Access-aware Worker completed the origin-header handoff

- The Cloudflare Transform Rule matched the research request but did not deliver
  `X-TreadJoy-Origin` to Render, so an authenticated request continued to fail
  the origin-lock middleware even though the server-side secret was configured.
- Resolution: deployed the source-controlled `treadjoy-research-edge` Worker
  on the research route, added its encrypted runtime secret, rotated the
  origin-lock value across Render, the Transform Rule, and the Worker, and
  redeployed Render. The Worker preserves the Access JWT header and injects
  only the server-side origin header; no value was logged or committed.
- Verification: unauthenticated and forged-header requests still stop at
  Cloudflare Access (`302`), the disabled Render hostname remains `404`, and
  the Worker binding is present as an encrypted secret. The last observed
  origin-denial event predated the final synchronization. An owner-authenticated
  application response remains pending because the available browser sessions
  could not complete the Access login for this check.
- Impact: the private edge is staged with a reversible Worker route and secret;
  R2, WAF/rate rules, monitoring, recovery, and public launch remain blocked by
  their separate approval and evidence gates.

## 2026-09-10 — V2 Blender blockout startup failure

- Blender 5.2.1 background startup exited with code 139 inside the sandbox,
  before the blockout script could complete. Retried the same private-media
  build through the approved unsandboxed Blender command.
- An attempted log patch used a nonexistent heading and changed nothing;
  corrected the patch to use verified surrounding text.
- No V1 files or public assets were overwritten by these attempts.

## 2026-09-11 — V2 automatic surface projection pinched panel edges

- The interface-envelope script assumed an unused gold material survived file
  reload; Blender had discarded it, causing a KeyError before any save. Added
  explicit material creation when missing and reran the private study.

- During the later upper-detail pass, an assumed regular vertex grid failed
  after the toe vertices had been welded (IndexError before saving). Replaced
  numerical row indexing with actual boundary-edge traversal for mudguard
  stitching. Earlier model files remained untouched.

- The contact-refinement trial welded the central vamp but nearest-surface
  projection pinched the terminal toe and quarter join. The first diagnostic
  also flagged 307 intersecting triangle pairs at each quarter/vamp boundary.
- Replaced quarter projection with blended normal offsets and excluded the
  terminal mudguard pole from projection. Preserve the contact audit rather
  than interpreting a render or unsigned overlap count as safe clearance.
- Original blockout, shape-refined source and V1 files remain unchanged.
- Follow-up pole closure and blended normal offsets increased the diagnostic
  overlaps (827 vamp/mudguard and 468/466 quarter/vamp pairs). Removed those
  adjustments from the saved revision; retain only welded/smoothed vamp and
  the initial overlay projection. Toe-tip and quarter joins remain unresolved;
  this pass must not be labeled contact-verified or promoted as final geometry.

## 2026-09-11 — V3 Blender bootstrap sandbox crash and layer leak

- Blender 5.2.1 background startup exited with code 139 inside the restricted
  sandbox before loading the V2 source. The same source-controlled command was
  rerun with approved Blender background execution and completed successfully.
- The first V3 preview exposed exploded badge duplicates in the assembled
  render because the new vendor-visualization child collection inherited
  render visibility. Marked that collection and its duplicate objects hidden
  for ordinary renders, regenerated from the untouched V2 source, and reran
  the reopen checks.
- Impact: no V2 file or public asset was overwritten. The corrected private V3
  file reopens in Blender 5.2.1 LTS and retains explicit concept-only status.

## 2026-09-11 — Initial V3 upper overlays read as floating directional flaps

- The first upper-rebuild render placed the tongue too high over the inherited
  laces and produced pointed saddle and eyestay ends. In lateral view, the
  saddle became an unacceptable directional gesture and the ventilation
  inserts projected above the vamp.
- Rebuilt the saddle as a broad quarter badge frame, tapered the eyestay,
  lowered and narrowed the tongue, recessed the ventilation inserts, reduced
  the badge presentation scale, and added a true lateral camera.
- Impact: the corrected R1 is retained only as a private form checkpoint. Badge
  seating, contact, heel definition, stitching, materials, exploded geometry,
  and every engineer-owned interface remain open rather than being described
  as production-ready.

## 2026-09-11 — Initial V3 contact-detail hardware was oversized

- The first contact-detail render used eyelet rings and lace lift values that
  were structurally present but visually too large and too far above the
  tongue, especially in lateral view.
- Reduced eyelet diameter and wire section, narrowed and thinned the flat lace
  ribbons, lowered the endpoints, and reduced crossing lift before freezing
  the checkpoint.
- Impact: the corrected geometry is retained only as presentation geometry.
  It is not a tension simulation, last/pattern validation, or evidence that
  the lace, eyelet, or tongue system will work in a physical shoe.

## 2026-09-15 — R16 pair rebuild required Blender 5.2 compatibility fixes

- The requested `game-dev` command was unavailable, so no Game Development
  Studio canonical-package receipt was produced. Used the installed Blender
  5.2.1 LTS executable, source-controlled build/validation scripts, hashes, and
  local QA records instead.
- Blender background startup again exited with code 139 in the restricted
  sandbox. Reran the same bounded Blender commands through the approved native
  Blender execution path.
- Early builds stopped before saving because Blender 5.2 removed the expected
  `GeometryNodeResampleCurve.mode`, uses `BLENDER_EEVEE` rather than the assumed
  `BLENDER_EEVEE_NEXT` enum, and did not return a mesh for unrealized seam
  instances. Replaced the incompatible node setting, corrected the engine enum,
  and explicitly realized Geometry Nodes instances before evaluation.
- Impact: these failed attempts did not overwrite the saved R14 source. R16 was
  generated from the byte-identical R14 `.blend1` recovery copy whose SHA-256
  remains `a90815b9793dab3b9a97edbe7d3db92e12edfee2267a9e9d7fc441f79518898c`.

## 2026-09-15 — Initial R16 geometry and proof candidates failed QA

- The first structural candidate produced nonmanifold diagonal-panel edges and
  a validator threshold incorrectly treated valid small faces as degenerates.
  Moved Shrinkwrap ahead of Subdivision, inset cage endpoints, reduced bevels,
  and changed the degeneracy check to a numerical-zero area threshold while
  retaining the measured minimum face area.
- The first proof render was overexposed because lighting values were scaled
  for a room-sized scene rather than a roughly 287 mm shoe. Reduced studio light
  energy, darkened the world, and used controlled AgX exposure.
- A hidden 200 m studio ground object had been copied into each shoe, and copied
  trim modifiers still targeted unposed master surfaces. Excluded studio objects
  from the shoe hierarchy and generated hidden, pose-matched modifier targets.
- Seam Geometry Nodes initially retained unrealized instances with invalid
  multi-meter bounds. Adding `Realize Instances` restored the intended dash
  dimensions. The first stitch placement also floated as much as 22 mm because
  inherited guide paths were not seated to the rebuilt panels; projected every
  editable seam control point onto the evaluated R16 surface and limited the
  presentation offset to 0.16 mm.
- Early flow and diagonal cages collapsed against undersized legacy patches,
  creating visible blue shards. Reseated those cages against the hidden
  continuous R13 reference surface while keeping that reference non-rendering.
- Impact: failed model and proof iterations are preserved under
  `media/development/treadjoy-heritage-court-v3/qa/pair-master-r16/failed-builds/`.
  The accepted R16 candidate passes the scripted structural checks, but remains
  a private digital concept pending owner visual approval; it is not evidence
  of physical fit, wear, traction, manufacturability, or production readiness.

## 2026-09-15 — R16 rerun disproved the previous visual-completion claim

- Reran the existing R16 build, reopen validation, and seven proof renders from
  the unchanged R14 recovery source. Preserved the previous R16 file and QA under
  `qa/r16-before-rerun-20260915/` in the private Heritage Court media directory.
- Structural checks passed again, but direct render review exposed uneven toe
  layers, hidden lace/eyelet passage, a mirrored left tongue mark, overlapping
  side surfaces, residual faceting, protruding tread blocks, and cropped proofs.
- The earlier handoff incorrectly treated structural checks and limited artwork
  tests as sufficient evidence of visual completion. Recorded the failed visual
  gate in `qa/pair-master-r16/visual-review.md`; further R16 correction is required
  before R17. This rerun did not repair those remaining defects.

## 2026-09-16 — R16 R14-style repair trials and stronger visual checks

- The old builder mixed R3 surface proportions with R14 geometry and located
  baked eyelets using stale object origins. Rebuilt guides from R14 seam
  measurements and actual eyelet mesh centers/normals instead.
- Automatic trim extraction/decimation exceeded the trim budget and produced
  nonmanifold results. Radial grid and face-normal trials introduced ragged
  edges, gaps, or large solidify spikes. These candidates were discarded from
  the active model and preserved in named `qa/r16-repair-*-trial/` archives.
  Replaced them with consistently oriented, bounded-thickness editable cages.
- Old flow stitch guides could land about 32 mm away from the rebuilt panels.
  New flow/diagonal guides use their actual cage boundaries. Dash instances
  now align their long axis to the curve tangent, not the default frame axis.
- Early contact checks found lace/tongue penetration, unintended cross-lace
  intersections, and 16 tread vertices outside the sole. Local tongue seating,
  explicit over/under routing and knot-lead adjustment, and narrower front tread
  blocks removed those failures in the checked candidate. Intentional eyelet
  and knot joins are separately excluded and documented, not claimed as a
  physically simulated knot.
- Passing these checks still left a rough toe edge and wrinkled overlays in
  the perspective render. Old voxel seating and direct projection across
  underlying panel discontinuities were reproducing the defects. Removed that
  toe seating and used smooth fitted side surfaces; further proof inspection
  remains required. No structural PASS alone establishes visual completion.
- Added independent reopened geometry budgets and finite-coordinate checks,
  actual eyelet-bore rays, tread containment, tongue artwork handedness, and
  evaluated lace contact checks. Saved camera/light settings now match the
  calibrated preview rather than relying only on the rendering script.
- Native Blender runs now use `--python-exit-code 1`; without it, Python failures
  could print a traceback but leave a misleading successful process exit.
  The Game Development Studio CLI is unavailable; no canonical package receipt
  is claimed. Original R14 sources remain unchanged, and public-release and
  engineering approval gates remain closed.

## 2026-09-17 — R16 surface repair continuation

- The previous continuation stopped when automatic tool approval reported an
  account usage limit. The queued patch had not been built; the last model and
  proofs were safely archived, not a verified final revision.
- Polynomial fitting across separate upper pieces produced floating edges.
  Projecting solely to the inner bootie also failed where the outer panels
  extend above that surface. Direct coordinate probes identified the mismatch;
  side cages now measure the R14 outer trim and preserve their authored Y/Z
  coordinates, with separate edge seating at the vamp and cupsole.
- The resumed candidate passed reopened structural checks and contact checks,
  but the full proof set still exposed forefoot gaps, sole-rim surface overlap,
  and badge faceting. These remained repair items, not owner-approval items.
- Adding two badge subdivision levels after bevel increased visible geometry
  to 963,745 vertices per shoe. The build budget check rejected it before save.
  Reduced the candidate to one subdivision level before bevel; the original
  500k per-shoe and 200k trim limits remain unchanged.

## 2026-09-21 — R16 validation resumed; narrow-panel bevel removed

- One subdivision level on every badge piece still exceeded the budget
  (539,761 vertices). Restricted it to the visible blue face and route artwork;
  the backing and small release accent retain their existing geometry.
- The narrow diagonal overlays produced zero-area bevel wedges. A micron Weld
  trial removed the degenerate faces but introduced nonmanifold edges. Removed
  the redundant bevel on the flow/diagonal cages instead; Subdivision and
  Solidify remain editable. The reopened replacement meshes subsequently had
  zero boundary, nonmanifold, and degenerate results. Retained R14 meshes also
  passed the separate topology audit.
- Projecting lower overlays to the cupsole rim caused a wavy join. Simplified
  their lower boundary above the rim and extended the toe band behind the join
  to cover the exposed inner-upper strip. Failed candidates remain archived.
- Full-view inspection still found a small toe-overlap opening and badge
  shading bands after structural validation passed. Seated the toe-band upper
  edge directly against the R14 vamp and removed sharp-edge/weighted-normal
  treatment from the smoothed badge. These changes require the new proof set;
  earlier receipts do not establish the revised model's visual quality.
- Direct nearest-surface toe projection subsequently created a scalloped overlap
  and was rejected. Restored the smooth toe band, removed the broad vamp inset,
  and confined the adjustment to the raised toe-center area. Sharp-normal
  removal alone did not remove badge banding; added depth-only smoothing that
  leaves the existing badge's Y/Z outline unchanged.

## 2026-09-23 — R16 interrupted badge build and visual-validation failures

- Recovered the interrupted build result: badge deformation plus an additional
  bevel exceeded the 500k budget at 518,486 vertices. No candidate was saved.
  Removing the redundant bevel reduced the next build to 436,255 vertices.
- Depth smoothing collapsed thin badge faces; the separate retained-mesh audit
  exposed degenerate geometry. Normal-based depth deformation then passed mesh
  topology checks but visibly sank part of the plaque into the upper. Neither
  candidate was accepted; both remain in named private QA archives.
- Replaced that deformation with an affine depth reduction, preserving the
  R14 artwork outline and separating the badge tiers outside the upper.
  The proof verifier now requires the retained-mesh audit to pass as well as
  matching hashes, dimensions, source files, and contact validation. Visual
  inspection remains a separate gate; no structural PASS implies completion.
- The affine badge candidate passed all automated checks but its plaque still
  stood visibly off the quarter. Macro inspection also exposed raised eyestay
  edges; these are unresolved repairs, not approved design changes.
- Increased only the toe band's inward shell from 1.2 to 3.0 mm. The next
  seven-proof set covers the former black toe opening but still shows a small
  notch/step. Reopened topology/contact checks and proof provenance pass at
  436,239 vertices per shoe. Recorded remaining defects in the current private
  `qa/pair-master-r16/visual-review.md`; R16 visual acceptance remains open.

## 2026-09-23 — Owner-requested continuous warm-stone upper

- The owner marked the tonal forefoot strips and requested a continuous piece
  from the badge quarter through the eyelets and toe to the sole rim. Archived
  the previous R16 and removed the floating strips and redundant seam paths.
- The first integration helper shadowed the existing `smooth` function with a
  modifier variable, stopping the build before save. Renamed the variable.
- Volume union produced one main shell plus a three-vertex fragment and closed
  four eyelet bores. Removed tiny debris and recut all fourteen bores; the next
  reopened mesh passed single-component, topology, and contact checks.
- Render review still showed old panel ridges. Added localized side-junction
  smoothing while protecting the eyelet neighborhoods and toe perforations.
  The unified surface is editable but no longer consists of separate quad
  panel cages. This tradeoff is documented in the owner guide; archived panel
  sources remain recoverable. No manufacturing or public-release claim is made.
- Final integration checks pass at 94,741 upper vertices and 363,635 per shoe.
  Seven proofs were inspected. The requested floating strips are removed, but
  remeshing softened some toe perforations and a shallow toe ridge remains;
  close-up surface polish and badge seating are still open before final imagery.

## 2026-09-23 — Wrong layer merged; owner correction

- Misread the owner's marked image and merged the warm-stone base instead of
  the darker overlay. The prior entry's description of an "owner-requested
  continuous warm-stone upper" was incorrect. The owner explicitly rejected
  that interpretation: retain warm stone as before and connect only the darker
  gray/suede layer above it. The rejected model and proofs are archived in
  `qa/r16-rejected-warm-stone-integration/`.
- Restored the warm-stone quarter and vamp geometry and added an independent
  hash/transform/material comparison against the pre-merge R16. Combined only
  the nine darker trim parts; the connectivity audit reports one component.
- Boolean eyelet cuts created an empty material slot, initially causing the
  audit to fail when reading its name. Corrected the audit's diagnostic handling
  and normalized the finished overlay to the existing suede material only.
- Full proof inspection found that merely joining the darker meshes retained
  a stacked lower-strip ridge. Seated the connecting strip cages at a common
  clearance over the unchanged base and lowered the bottom edge toward the rim.
  The corrected result passes all current checks at 425,761 vertices per shoe;
  dark overlay is one component and all warm-stone mesh checks match the
  pre-merge model. Remaining border waviness, small toe-side step, and eyestay
  shadow are recorded in the visual review; final close-up approval stays open.

## 2026-09-23 — Separate pictured-version refinement trials

- The saved owner R16 no longer matched the last rendered proof's source hash.
  Paused instead of replacing that file. The owner explicitly chose to refine
  the last pictured version in a new file. Reused its hash-pinned build sources
  and created the separate `pair-r16-smooth-round` variant; the owner's saved
  master and the R14 sources remain protected by hash checks.
- A radial surface-projection trial made the toe-overlay border pull away from
  the warm-stone vamp. An X-only projection then introduced visible dimples by
  using local normals to distinguish the thin shell's inner and outer skins.
  Both trials passed structural checks but failed visual review. Preserved
  their models and proofs in named local QA trial archives, not release media.
- Continued with a shared shell displacement instead of normal-based skin
  classification. Visual acceptance remains separate from topology, contact,
  layer-preservation, and proof-provenance checks.
- Shared displacement alone also retained surface noise. Parameterizing
  thickness between measured inner/outer shell intersections, followed by
  all-axis and localized junction smoothing, produced a smoother surface.
  Extending side projection around the front introduced toe creases; limited
  it to the side joins and removed the trial's extra toe-roof lift. Rounded
  only the shared plan outline. All intermediate candidates remain archived.
- The separate final review candidate passes the reopened checks at 425,665
  vertices per shoe and 120,818 overlay vertices. Its seven proofs were
  inspected. Main dark-panel joins are blended, but fine edge waviness,
  a raised eyelet transition and existing badge stand-off remain documented in
  `qa/r16-smooth-round/visual-review.md`. This is not final visual approval.

## 2026-09-24 — Separate court-toe and shell-seating refinement

- Started from the owner's accepted `pair-r16-smooth-round` file, preserving
  that input, the independently saved owner master, and both R14 files by hash.
  The new work is isolated in `pair-r16-court-finish`; it is not public media.
- The initial build stopped because Blender cannot apply a modifier to shared
  mesh data. Corrected the helper to copy the editable master's mesh before
  applying the modifier and relink both handed instances afterward.
- The first saved trial contained empty stitch curves after a mistaken
  longitudinal cutoff. Independent validation rejected them. Inspection showed
  these were short transverse seams across the now-fused gray layer, so removed
  those two redundant paths and their pair instances entirely. Six useful
  editable perimeter paths remain.
- The next trial passed topology, eyelet, lace, and seam checks, but its side
  proof still showed a pinched toe/quarter transition. Independent lower-edge
  measurements also found up to 1.06 mm of separation from the sole. This is
  another case where mesh connectivity did not establish visual continuity.
  Preserved both trials, proofs, and build scripts in named local QA archives.
- Continued with a shared toe-side surface displacement and a measured lower
  rim translation that moves both skins together. Final visual acceptance is
  separate from the automated geometry and provenance checks.
- Separate analytical toe-roof and shell remaps subsequently exposed the insert
  through the shoulder. A smoothed side carrier did not solve that overlap and
  introduced scalloping. Rejected those visual trials despite passing closed-
  mesh checks. Replaced them with one shared coordinate transform for all
  forefoot materials, preserving their mutual alignment.
- Shared plan reshaping revealed the inherited upturned toe-wrap rim more
  clearly in the side proof. Matched that rim's height to the actual insert.
  Confined the sole-seating displacement to the bottom few millimeters after
  a broader displacement exposed a small patch of the underlying layer.
  Trials 01–05 remain archived with their models, scripts, and available proofs.
- The rim-only lowering trial exposed the cool-gray lining at the front and
  was also rejected (trial 06). Replaced it with a common monotonic crown taper
  applied to all forefoot materials, so lowering the front does not separate
  the shell, insert, and lining. No trial's topology PASS is treated as proof
  that these visual defects were fixed.

## 2026-09-25 — Lower-wall coverage check added

- Final side-view review found a small warm-stone breakthrough above the sole
  even though the lowest gray edge passed contact checks. Those checks proved
  seating at the hem, not coverage of the visible wall above it.
- Narrowed only the inward part of the hem displacement to the bottom 1.3 mm;
  retained the smoother vertical seating adjustment. Added independent sampled
  rays comparing the base, gray shell, and sole. The new candidate reports
  zero visible lower-wall breakthrough samples and no sampled side/toe gaps.
  The preceding candidate and its proofs remain in trial 07 for comparison.
- The new saved candidate passes the reopened geometry/contact checks and
  seven-proof provenance verification at 422,689 vertices per shoe. Inspected
  all seven proofs and documented residual fine border waviness and existing
  badge stand-off in `qa/r16-court-finish/visual-review.md`. Owner visual approval
  remains separate; R17 images and website implementation have not started.

## 2026-09-26 — Detail-refinement trials and macro regressions

- Continued from the hash-pinned `pair-r16-court-finish` pictured source into
  the separate `pair-r16-detail-refine` candidate. The source, independently
  saved owner master, and both R14 files remain protected; no website or public
  media change is part of this step.
- The first trial read stale eyelet world transforms after switching view
  layers. The reopened entry-distance check rejected it. Updated the dependency
  graph before reading coordinates and moved the eyelet origins with their
  geometry and linked pair instances.
- A tiny central ring in the new toe panel combined with beveling to produce
  numerical-zero faces. Replaced it with a proper center fan and cleaned only
  coincident/degenerate microgeometry. Confined the proportion remap to the
  forefoot after a broader map introduced one upper lace self-intersection.
- New toe holes require corresponding lining openings. Added five aperture
  rays per hole through both layers; the original bore-center check did not
  establish clear ventilation geometry beneath the insert.
- Close-up review found an inherited folded/overlapping toe stitch and thin
  throat fins exposed by the collar-end taper. Rebuilt the two toe perimeter
  paths and seated the quarter/gusset ends below the softened collar. Kept the
  geometry/contact checks separate from this visual review.
- A radial correction of the gray toe border passed topology/contact checks
  but created a raised, wavy lip. Rejected it. A subsequent clean toe-surface
  union had eleven nonmanifold edges and a visible shoulder step; it was also
  rejected. Trials 01–05 and their available local proof/QA records are retained
  in numbered `qa/r16-detail-refine-trial-*` folders. They are not approved assets.
- Pair instances can retain an old modifier after replacing a master's mesh.
  Cleared obsolete pair modifiers when replacing geometry and added independent
  evaluated-vertex parity checks for both hands. Shared mesh data alone does
  not prove that the displayed pair matches the editable master.
- The fused clean-toe trial passed closed-mesh/contact checks but an independent
  lower-wall grid found 37 base-breakthrough samples. Added a localized seating
  allowance and an explicit toe opening. A subsequent exact Boolean left one
  numerical-zero face; removed it with a bounded coincident/degenerate cleanup.
  Trials 06–08 retain these intermediate states and available evidence.
- Full-size visual review of trial 08 still found the warm-stone surface
  breaking through the higher front-side transition, beyond the lower-wall
  check's scope. Raw per-triangle seating offsets then created visible
  corrugation (trial 09). A low-frequency field removed that noise, but its
  eyelet-distance mask introduced small scallops (trial 10). These were not
  accepted merely because automated topology/contact checks passed.
- A repeat Boolean against the already-cut toe boundary introduced nonmanifold
  edges and was stopped before saving. The next attempt uses a broad spatial
  fade before the toe opening and pure vertex fairing of the lower sidewall,
  rather than recutting a coincident boundary. The owner's source files remain
  unchanged throughout these trials.
- The final separate review candidate reopens and passes structural, retained-
  topology, contact, sampled coverage, vent and pair-parity checks at 431,051
  evaluated vertices per shoe and 150,393 shell vertices. All ten 16-bit proofs
  were inspected and verified against model hash `15d4a4d7e81e2f0e154a43f023a301c55a2ef740d798759a2525028276d21b80`.
  Fine border waviness, small eyelet-edge puckering, faint badge highlight
  banding and a remaining lower contact-shadow irregularity are recorded in
  `qa/r16-detail-refine/visual-review.md`; they are not marked visually closed.
  Owner approval, R17 assets and website work remain separate gates.

## 2026-09-26 — Owner-markup contour/tread refinement checks

- The owner annotated the previous `r16-detail-refine` perspective and outsole
  PNGs in place. Their old render receipts therefore no longer describe those
  two files. Preserve the annotated bytes as owner references and create all
  new proofs in `qa/r16-contour-tread`; do not overwrite the marked images or
  call their superseded receipts valid.
- Source inspection found that `R16_MASTER__DM_Bootie` in the pictured detail
  model has zero vertices. This corrects the earlier claim above that the
  ventilation test established clear holes through a valid lining: empty
  geometry trivially passed the ray and zero-nonmanifold checks. New checks
  explicitly require nonempty visible meshes before topology and vent tests.
- Initial mask-projection attempts failed before saving because they assumed
  every mesh had vertices. Added a bounds guard and separated the existing
  visible layers from the missing internal liner when freezing the white-marked
  area. No prior model or owner reference image was modified.
- A read-only liner restoration trial first encountered Blender's multi-user
  modifier restriction, then reproduced destructive exact-Boolean behavior:
  the third individual vent cut reduced the prior 44,344-vertex lining to
  three vertices despite closed edge topology. A bounded internal voxel repair
  and reduction allowed all twenty cuts to retain a nonempty lining in the
  next isolated test. The visible gray shell is not voxel-remeshed in this pass.
- The first full contour/tread build was rejected before saving because a
  perimeter strip extended past the outsole's bottom footprint. Sidewall rays
  can hit a flared lip; added downward-footprint checks including strip width.
  These tests are visual-model checks, not proof of traction or manufacturability.
- The first two saved contour candidates passed sampled contact/connectivity
  checks but had visibly folded connector edges; both were rejected and moved
  intact to `qa/r16-contour-tread-trial-01` and `-02`. Replacing raw underlay-ray
  displacements with a continuous field was insufficient by itself. The white
  exclusion projection had also locked hidden back-side vertices and used a
  hard constraint boundary. Added camera-visibility filtering and a spatial
  transition around the protected vertices before the next visual check.
- The visibility correction removed the sharp frozen-region tear. Subsequent
  macro review still found a broad shoulder bump and shallow crease, so trials
  03–04 were retained while the new candidate received bounded underlay-following
  normalization and a localized smoothing pass. No source/owner master was
  replaced and no proof was image-painted to hide a geometry problem.
- The separate contour/tread candidate now reopens with 483,081 vertices/shoe,
  a 150,393-vertex single connected shell, nonempty restored lining, and passing
  structural, closed-topology, contact, mask, pair-parity and sampled coverage/
  ventilation checks. All ten new 16-bit proofs were inspected and their hashes
  bound to model `a1e035c4521aa97a9089f3449ff7beea8412ef91f31a08b7e03594f8890a89dc`.
  Both annotated references and all protected masters match their prior hashes.
- Do not summarize this pass as all historical polish resolved. The shallow
  connector crease, fine gray/stone border waviness, some eyelet-edge puckering,
  faint badge banding and small lower contact-shadow irregularity remain noted
  in `qa/r16-contour-tread/visual-review.md`. The new file is an owner-review
  candidate, not clean-quad production CAD, a traction-tested outsole, owner
  approval, R17 imagery or a public-release asset.

## 2026-09-26 — Localized eyelet-connector taper

- Continued from the owner's pictured contour/tread candidate into a separate
  `pair-r16-tapered-connector` file, limiting changes to the connected gray
  shoulder and its two eyestay stitch paths. All earlier models remain intact.
- The first scope-fingerprint audit assumed every curve material slot contained
  a material and stopped on an intentionally empty slot. Updated the read-only
  fingerprint to preserve/compare null slots; did not modify source materials.
- The first taper passed structural, contact and preservation checks but still
  appeared too block-like at the bend. It is retained with its available proofs
  in `qa/r16-tapered-connector-trial-01`. Increased the lower contour's forward
  taper and the upper contour's return toward the eyestay for a smoother rising
  sweep, keeping the white-marked surface and bore neighborhoods constrained.
- The second taper's stronger upper return pulled a visible notch into the
  eyestay despite passing topology checks. Rejected it and retained the complete
  candidate in `qa/r16-tapered-connector-trial-02`. The next version fixes the
  upper eyelet strip and tapers the lower connector instead; visual review is
  required in addition to manifold/contact checks.
- Subsequent taper trials 03–05 improved the lower width but retained a stepped
  bend; one smoothing trial also disturbed the neighboring gray toe border.
  Each model and its available proofs are preserved in its numbered trial
  directory. Added a distance-based toe-border exclusion and measured the
  desired rising contour on the unchanged quarter surface before rebuilding.
  These are rejected working candidates, not owner-approved revisions.
- Trial 06's stronger taper exposed the stone through the gray connector,
  above the original lower-wall sampling grid. Added a dedicated connector
  coverage check and tighter local surface fitting. Trial 07 removed the
  visible sliver but the new check found one extra 0.264 mm burial sample;
  rejected both, retaining their saved models and proofs. Applied a bounded
  submillimeter seating allowance before the next review. The test must not
  equate closed manifold geometry with correct layer seating.
- Final review candidate completed on 2026-09-27:
  `pair-r16-tapered-connector.blend`, SHA-256
  `29d4d087552d9c12410c5a8f50e745880339ccd240782d8e96dbe8263c2bbb74`.
  All ten final 16-bit saved-model renders were inspected and hash-verified.
  Reopened structural, contact, retained-topology, pair-parity, ventilation,
  source-preservation and scope checks pass; 44 other master objects are exact.
  The dedicated connector grid retains only the same single inherited throat
  burial sample, with no added sample. It is not a zero-contact-issue claim.
  Residual rounded shoulder flare and close-up surface limitations are recorded
  in the new visual review. Owner acceptance remains pending; no R17, website,
  public assets or deployment work began, and no protected source was replaced.

## 2026-09-27 — Black And Red Connector Markup

- The owner annotated the previous taper proof in place. Its PNG hash is now
  `d3dea70b489ee9cafedd955a1d27058ac12e78e217ed750e76401b414105a324`;
  preserve it as an owner reference, not as the original unmarked render. The
  old proof receipt is historical and no longer matches that annotated file.
- Restored the black-marked side band from the prior contour/tread geometry.
  The first red-connector trial instead sharpened its flare and added nine
  sampled layer-burial points; it was rejected and retained intact under
  `qa/r16-straight-connector-trial-01`.
- Direct surface measurements located the flare beside the old white-mask
  exclusion. Carrying that mask forward unchanged conflicted with the owner's
  new red-circle instruction. The new red shoulder is now allowed to change
  in a bounded outer-side region, with retained exclusion vertices, eyelets,
  laces and the complete toe insert still fixed. Do not claim the superseded
  portion of the old white exclusion is unchanged in this refinement.
- Connector trials 02–04 were also rejected and retained in numbered local
  trial directories. Directional reshaping created a crease; local smoothing
  then exposed the underlying layer at sampled points. Pointwise ray-based
  reseating cleared those samples but introduced a visible short ridge in the
  macro proof. Replaced that discontinuous correction with a spatially
  smoothed seating field; topology and coverage tests alone cannot establish
  that a leather surface looks smooth.
- Trials 05–06 tested a smoothed radial seating field and a wider lower blend.
  Trial 05 still added sampled underlay burial; trial 06 cleared those samples
  but moved the visible crease into the lower join. Both are retained, not
  approved. Switched to fitting the connector against a continuous surface
  approximation of the unchanged quarter while carrying the shell's skin depth.
- Trial 07 reduced the crease but worsened the inherited throat burial depth;
  trial 08's radial smoothing improved the visible join but introduced two
  smaller burial samples. Retained both candidates. Tightened the independent
  scope audit to compare burial location and depth, not merely sample count,
  matching the stronger final-evidence check. Added a smooth localized clearance
  allowance at the upper connector before the next verification.
- Final owner-review candidate: `pair-r16-straight-connector.blend`, SHA-256
  `3ca5905f1ab559d23b72770fb28b35e5d2440d8bd3ba90607a034135ce52f845`.
  The two black-marked side bands restore 6,089 prior vertices exactly. The
  red connector is reshaped and fitted on both sides of the linked pair.
  Reopened structural/contact tests, exact scope/restoration checks and all
  ten native 16-bit proof receipts pass. The dedicated connector grid has
  zero burial samples and the lower-wall grid has zero breakthroughs; these
  remain sampled measurements, not exhaustive fit/manufacturing validation.
  All 44 other master objects, retained exclusions, earlier models and owner
  markups are preserved. Fine border waviness and a shallow lower-join shading
  transition remain documented in the new visual review. No R17, website,
  public-release or deployment work was started; owner acceptance is pending.

## 2026-09-27 — Match Connector Neck Width To Its Middle

- The owner clarified that thickness means widening the narrow neck directly
  below the lowest eyelet, not changing the gray material's raised depth.
  Started a separate `pair-r16-uniform-neck` revision from the unchanged
  straight-connector model, retaining its restored side bands and middle.
- First widening trial passed preservation/coverage checks but produced a
  forked outline in the macro render. The curved toe insert's distance mask
  suppressed neck movement more than movement above/below it. Retained the
  rejected file and proofs under `qa/r16-uniform-neck-trial-01`; replaced that
  constraint with a monotonic toe-side anchor and a height-dependent widening.

## 2026-09-28–29 — Integrated Upper Overlay Contract Reconciliation

- Planning capability discovery could not find the `game-dev` CLI. Blender
  application selection through Computer Use also timed out by both app name
  and bundle ID. The owner approved native Blender as the implementation path;
  do not claim a canonical game-dev package or receipt for this work.
- A planning `rg` command used an unmatched shell glob for QA Markdown files
  and stopped before searching. Retried with directory arguments and `rg` glob
  filtering. During implementation, searches also guessed nonexistent checker
  and product-choice paths; switched to the actual filenames from `rg --files`
  and the existing models/migration. No source changes resulted from these errors.
- The first sandboxed background Blender inspection exited with signal 11
  (exit 139) before loading the selected model. The same read-only command ran
  successfully with approved sandbox escalation. It inspected the source and
  exited without saving a Blender file.
- The documentation patch initially combined deletion and addition of README
  in one patch and was rejected for targeting the same path twice. Replaced it
  with an Update File patch. The workbook patch later failed a context match;
  reread the live block and applied the narrower update. Neither failed patch
  changed a file.
- Parallel Stage 1 work was interrupted by the account usage limit. Resumed
  from the saved files on 2026-09-29 after the owner said `continue`; retained
  completed artifact-operation markers and original-output backups instead of
  repeating or overwriting them.
- The inspected R16 source has 45 visual objects per shoe but no current module
  ID tags. Schema v2 records external ownership: M09 owns the connected overlay,
  its 14 eyelets and four overlay seam paths; M04–M08 and seven chassis objects
  account for the rest. Report source metadata as pending, never as already
  embedded. New candidate files must use the metadata helper and strict check.
- The selected source pathname was independently saved after its planning
  hash was recorded. The earlier bytes remain in `.blend1`; the current source
  is `3201af51...`, and the planning backup is `a1b532e5...`. A read-only comparison
  found matching raw geometry, transforms, material nodes/assignments, modifier
  names/types, visibility, and collections; other modifier properties and
  UI/session state were not compared. Both files stayed unchanged during the
  audit. Added source-path/hash validation and three regression tests so a
  renamed or newer same-name source cannot silently reuse a registry receipt.
- Document review exposed ignored DOCX table-grid widths, an orphaned final
  table row, and workbook auto-fit performed before column widths were set.
  Corrected the generator sources and rerendered all seven pages and five
  sheets. Kept the intermediate render as superseded QA, not current output.
- The first exported-artifact preservation check failed because the unrelated
  `docs/project-ideas.md` changed independently on September 29. This task has
  not edited or reverted it. Record its initial and observed hashes instead of
  assuming a shared-workspace file must remain static. The existing MISTAKES
  prefix and migration 0008 still match their preservation checks.

## 2026-09-29 — R16 Final Polish Preflight

- An initial instruction-file search included absent `.agents`/`.codex` folders
  and returned exit 2. Read the repository's actual root `AGENTS.md` and used
  existing directory paths for subsequent inspection. No asset writes occurred.
- The `game-dev` executable remains unavailable. Continue only through the
  already approved native Blender fallback, with exact source/destination
  authorization before the first file-writing Blender run.

## 2026-09-29 — Stage 2 Final Polish Validation Iterations

- The initial source-inspection helper assumed every material slot held a
  material. Two unused slots are null; the inspection now reports those slots
  explicitly. The diagnostic did not save or alter the source.
- The first in-memory polish failed its pre-save checks: curve cap rings were
  duplicated, seven lace/eyelet passages still intersected, three tail contacts
  appeared, and two sampled connector locations penetrated the quarter. No
  candidate was saved. Preserve failed reports under the trial's `attempts/`
  directory rather than presenting them as accepted evidence.
- Welded coincident curve cap rings, corrected lace profile orientation, lifted
  the free tail ends locally, and used a smooth connector clearance field.
  The second pre-save check passed topology, stitch seating, connector width,
  sampled burial, and pair parity, but still failed lace/eyelet contact checks.
  Radial centering alone does not establish a clear approach over the rim.
- A broad in-memory rim-clearance experiment removed hardware intersections
  but introduced lace self-intersections near previously clear upper eyelets.
  Narrow the correction to failing passages and recheck both kinds of contact;
  do not weaken the validator or save a numerically failing candidate.
- The first saved Stage 2 candidate passed the defined numerical checks and
  produced ten native proof images, but visual review rejected it: connector
  edge waviness persisted and lace entries looked excessively pinched. Numeric
  passage, width, and manifold checks are not visual acceptance. Preserve this
  candidate and its build scripts as a rejected checkpoint; do not promote it.
- Plain local smoothing retained the connector's scalloped contour. A
  normal-based surface projection made local folds worse; an experimental
  Boolean edge patch introduced one nonmanifold edge and 28 tiny faces. These
  source-preserving diagnostic experiments were rendered only, not saved as
  Blender candidates. Use measured inner/outer source surfaces for further
  refinement instead of guessed shell offsets.
- A sandboxed process-status command was denied; the escalated inventory was
  too broad and its output truncated. A subsequent narrowed status request was
  rejected when the approval service hit the account usage limit. No bypass
  was attempted. After owner `continue`, the already-authorized render session
  returned all ten completed proof renders normally.

## 2026-09-30 — Stage 2 Second-Trial Lace Diagnostics

- Separate straight-entry lace spans initially intersected two upper eyelets
  and neighboring spans outside the documented join zones. Per-spline BVH
  diagnostics localized the failures; no Blender file was saved by these tests.
- An aperture-plane correction initially lacked a finite influence mask and
  displaced distant points, creating many self-intersections. The diagnostic
  caught this before saving. Bounded the influence and then restricted the
  correction to the two failing upper spans; blanket corrections also disturbed
  otherwise clear lower routes. Numerical passes still require visual review.
- The authorized second-trial build was rejected before saving by the strict
  module checker: the remeshed M09 contained disconnected mesh components.
  Added an explicit component inventory and a fail-closed size bound before
  removing any tiny cutter slivers; substantial detached pieces still reject
  the build. Source and first-trial files remained unchanged.
- The component inventory identified one eight-vertex cutter sliver with a
  sub-micron bounding box. Removing only that isolated artifact restored the
  one-component contract; the second candidate then passed pre-save and reopen
  validation. Its close proofs still show overly sharp lace bends and fine
  connector-edge ripples, so numerical success is not Stage 2 completion.
- A diagnostic lookup initially used the package root for `module-registry.json`;
  the actual registry is under `engineering/`. Corrected the read-only lookup.
- Read-only outsole inspection found 371 nonadjacent tread triangle overlaps
  above local Y=0.118 m, while the sampled inter-object tip rays found no
  near-coincident sole surfaces. This supports investigating tread self-overlap
  for the inherited tip artifact; it does not prove all overlaps are visible or
  authorize redesigning the JOY ORBIT motif.

## 2026-10-01 — Trial 03 Bilateral Fit And Sweep Diagnostics

- The first explicit-frame lace test cleared all eyelets but produced six
  unintended self-intersections near upper approaches. Smoothed the sampled
  centerlines before sweeping; the follow-up in-memory test reported zero
  hardware, tongue, and unintended self contacts without expanding exclusions.
- Exact self-union of the inherited tread initially left 76 zero-area faces.
  Applied bounded 0.0001 mm duplicate/degenerate cleanup; the follow-up mesh
  passed manifold, zero-area, normal-consistency, and positive-volume checks.
  Visible-surface preservation and rendered artifact removal still require
  separate checks before acceptance.
- A combined instruction/source read was truncated. Re-read the omitted
  instruction ranges separately before implementation; do not infer missing
  repository requirements from truncated output.
- The first full trial-03 pass stopped at module validation because replacing
  the lace object with a mesh violated its existing CURVE type contract.
  No candidate was saved. Preserve the curve controls/type and provide the
  explicit sweep through a source-bound geometry helper instead; track evaluated
  changes as well as raw datablock changes. Do not relax the type validator.
- Bilateral width measurements passed, but mirrored inside/outside previews
  exposed a remaining visible step on the inside boundary. Extending the lower
  deformation fade did not remove it. Keep trial 03 unsaved and trace that
  visible transition to actual surface coordinates instead of declaring the
  owner's style-and-fit requirement met from width samples alone.
- The trace-targeted smoothing rounded the inside step but reduced one sampled
  inside/outside width ratio to 0.8966, below the 0.90 visual-review proxy.
  The pre-save gate correctly refused the candidate. Compensate the bounded
  lower-band width and recheck; retain the threshold and the failed report.

## 2026-10-02 — Trial 03 Resume And Visual Gate

- The October 1 native Blender launch was rejected by the approval service's
  account usage limit. No alternative execution path was used to bypass it.
  After the owner's October 2 `continue`, the same authorized invocation was
  accepted. Source and owner-edited review hashes were checked before resuming.
- Attempt 06 passed numerical checks, including bilateral chord ratios of
  0.9340–1.0744, but its inside macro still showed a wavy shoulder. Stopped at
  the interactive pre-save gate without saving a Blender candidate. Numerical
  width agreement alone does not satisfy the continuous-boundary requirement.
- A preservation check found that trial 01's current `.blend` no longer matches
  its old proof hash. The untouched `.blend1` does match it exactly. Recorded
  both hashes and the later save's timestamp in trial 03's source-provenance
  note rather than relabeling old evidence or restoring over the later file.
  An initial lookup for trial 01's nonexistent `evidence-verification.json`
  failed; its `build-record.json`, review, and matching backup establish the
  historical hash. Trial 03 continues to use the verified trial-02 input.
- An optional status search assumed a package `docs/CONTEXT.md` path that does
  not exist. Do not infer that a domain document is missing from an unverified
  path; no contract documentation was changed from this failed lookup.
- Attempt 07's lower-shoulder profile warp removed the conspicuous inside step
  while passing numerical gates, allowing an isolated saved/reopened trial 03.
  All 13 larger proof views nevertheless show remaining fine boundary ripples
  and sharp/crumpled lace approaches. Recorded a visual rejection and proposed
  a separate, as-yet unauthorized fourth correction; numerical success does
  not authorize promotion or Stage 3.

## Trial 04 — Preparation

- A combined instruction read exceeded the tool output limit. Re-read the
  omitted repository instruction ranges before implementation.
- An initial source lookup guessed `build_r16_final_polish_trial02.py`; that
  file does not exist. Used the actual script inventory and inspected the
  shared `build_r16_final_polish.py` and `refine_r16_lace_entries.py` instead.
- Confirmed the new trial-04 directory was absent before creating it; the
  negative existence check is expected and no prior candidate was replaced.
- Trial-04 attempt 01 lowered crossing spans too far and produced 64 detected
  unintended triangle intersections. Strong edge fairing also created a small
  visible medial toe-edge shadow gap. The diagnostic gate prevented a save.
  Restore more vertical separation and bound connector displacement; keep
  collision exclusions and numerical thresholds unchanged.
- Attempt 02 cleared lace collisions and removed the new shadow gap, but one
  bilateral chord ratio reached 1.10256 against the unchanged 1.10 ceiling.
  No candidate was saved. Reduce smoothing displacement to preserve the
  accepted proportions and retain the longitudinal ribbon axis on crossing
  spans while transporting the knot/lead frames separately.
- Attempt 03 passed the unchanged checks and produced a saved/reopened trial 04
  with thirteen verified proofs. The complete visual review still found fine
  boundary waviness and raised/pointed lace approaches. The bounded smoothing
  and frame correction improved the asset but did not meet the full brief.
  Keep the checkpoint unpromoted and obtain owner direction for explicitly
  controlled local contours; do not repeat general smoothing or move into
  materials while describing those findings as resolved.

## 2026-10-03 — Trial 05 Controlled Contours

- The reported terminal invocation preceded creation of the trial-05 builder;
  inspection found neither that script nor its output directory. Supplied the
  authorized builder without claiming the owner's terminal run succeeded.
- A combined source read was truncated; required instruction/source portions
  were read separately. Future inspection should keep outputs bounded.
- Attempt 01 stopped before geometry changes or a model save because the
  rear-edge sampler unnecessarily required the unrelated forward edge to fit
  within its scan range. Retained the rear-edge bracketing check and removed
  only the irrelevant forward-boundary assertion. The failed helper is archived.
- Attempt 02's explicit rear contours passed the unchanged geometry checks,
  but the shortened lace-entry curves intersected upper hardware and a lower
  crossing. No candidate was saved. Retain the seated bore legs, preserve the
  accepted central lane separation, and account for ribbon width above tilted
  rims before attempting another saved checkpoint. A source search also named
  an absent uniform-neck builder; used the actual script inventory instead.
- Attempt 03 stopped without saving because a fixed 2.8 mm entry threshold
  exceeded the shorter incoming bore legs. Bound the threshold by each existing
  leg's own normal-axis extent; retain diagnostic failures and script snapshots.
- Attempt 04 cleared all hardware but created 385 detected lace self-crossings:
  the normal-clearance correction and transition blending were too aggressive.
  No model was saved. Preserve the bottom return span, reduce the normal offset,
  and test bounded reconstruction strengths against the same collision checks;
  failed search strengths remain evidence, not waived validation failures.
- Attempt 05's five global reconstruction strengths all failed lace contact
  checks. No candidate was saved. Replace global blending with explicit span
  attribution: keep source sweep bytes on the knot and any affected crossing
  spans, and validate the remaining local revisions without contact waivers.
- Attempt 06's span attribution isolated self-folds within eight reconstructed
  crossing spans. Retaining those spans exactly produced a numerical pass with
  four improved crossing spans, but it was not saved while testing a narrower
  clearance correction. The prior correction could affect unchanged/below-rim
  controls; restrict it to altered, outward-facing bend points.
- Attempt 07 passed numerically after preserving seven problematic spans, but
  previews exposed new small creases at some entry joins. Stopped without a
  save. Match the actual source tangent at both cubic endpoints and remove
  the post-curve clearance clamp; retain collision-prone source spans instead
  of introducing a new derivative break to force clearance.
- Attempt 08's tangent-matched curves eliminated all detected self-folds, but
  seven upper spans still needed source preservation for hardware clearance.
  The pass was left unsaved to test smooth interior clearance controls on those
  spans, retaining the same endpoint tangents and strict collision gates.
- Attempt 09's smooth interior controls cleared all twelve revised crossing
  spans without any additional source-span rollback. Pre-save/reopen checks
  pass, but the full thirteen-view review still finds fine edge-wall waviness,
  lower-eyelet notches and raised/angular lace approaches. Saved the isolated
  checkpoint as unpromoted, not as completion of the strict visual brief.
- A proof-manifest lookup ran before the renderer had emitted the final index;
  deferred verification until all images completed. The reused comparison
  renderer also emits an inherited trial-03 text label. The trial-05 verifier
  corrects only this new manifest and binds it to the actual candidate hash;
  no earlier manifest or hash-bound evidence is edited.

## 2026-10-03 — Trial 06 Edge-Wall Replacement

- Attempt 01 replaced actual connector edge-wall faces using rounded analytic
  cut volumes and retained all 602,359 protected shell vertex coordinates.
  Width, bilateral match, clearance and lace checks passed, but one nonmanifold
  edge remained after Boolean cleanup. The gate prevented any model save.
  Inspect the edge and permit deletion only for bounded submicron wire debris;
  do not waive nonmanifold validation or change protected geometry.
- Attempt 02 identified the defect as a 0.044 mm edge with four linked faces,
  not loose wire debris; it was not deleted or split to hide the defect. No
  candidate was saved. Adjust the cutter's upper fade to avoid that pinched
  junction and rerun the unchanged manifold/clearance checks.
- Attempt 03 retained the exact same four-face edge despite the cutter change.
  This points to the subsequent global duplicate/degenerate cleanup rather
  than the cut transition; test the raw Boolean result without that cleanup.
  Lowering entry arches also caused ten contacts between bottom spans 12/13;
  preserving the affected spans restored zero contacts without exclusions.
- Attempt 04 removed global duplicate/degenerate cleanup, but the same
  four-face edge remained, along with one zero-area face. This disproved the
  cleanup hypothesis from attempt 03. No candidate was saved. Trace the
  source and each Boolean separately before attempting a bounded repair.
- Per-operation diagnostics traced the four-face edge to the first Boolean,
  which generated an opposite-facing duplicate of a source sliver triangle
  on the other side. Explicitly triangulating three nearby source ngons
  eliminated that defect without moving vertices. Attempt 05 passes the
  unchanged checks after bounded cleanup of one zero-area Boolean artifact.
  No global merge/remesh or nonmanifold-edge splitting was used. The saved
  candidate remains unpromoted pending the full proof review.
- A manifest lookup used the nonexistent `manifest.json`; the actual package
  index is `package-manifest.json`. No file was created at the wrong path.
- Full thirteen-view review, completed 2026-10-04, still rejects forward-edge
  undulation/lowest-eyelet notches, fine rear-edge serration and raised/angular
  lace entries. Rear-wall replacement and local entry cleanup are not a full
  visual solution. Preserve this numerically passing checkpoint as unpromoted;
  do not describe the brief as complete or start a seventh trial without owner
  approval. Thirteen proofs and thirteen archived scripts are hash-verified.

## 2026-10-04 — Trial 07 Forward Wall And Lace Entries

- Attempt 01 stopped before saving: the Boolean result contained a zero-area
  artifact outside the permitted connector edit region. The bounded cleanup
  assertion correctly rejected it. Record exact coordinates and operation
  provenance; do not silently expand the permitted region or relax validation.
- Attempt 02 identified the off-region artifact at the inherited rear cutter
  boundary (y=0.005 m), unrelated to the new forward cut. No model was saved.
  Confine incidental Boolean retessellation by restoring exact source polygons
  outside support, then rerun the same connectivity/winding, manifold and
  clearance gates. This is source restoration, not an expanded edit region.
- Attempt 03 passed topology, protected geometry and collision checks after
  restoring six exact source polygons in place of nine incidental Boolean
  polygons. Its neck/middle ratio was 1.071005, above 1.05, so no model was
  saved. Previews also showed an overly visible washer-like lowest-eyelet
  support; fit that support to the measured shell surface and reduce the
  forward inset instead of changing acceptance limits. Two upper lace spans
  were retained because their reconstructed sweeps clipped hardware.
- The next confirmed native launch did not start because automatic permission
  review timed out. This was a tool timeout, not a geometry result or safety
  determination; retry the same authorized invocation once as permitted.
- Attempt 04 improved the width ratio to 1.036053 and cleared all twelve
  revised lace crossings without source-span rollback. It nevertheless left
  three nonmanifold shell edges, so no model was saved. Trace these edges
  through each cut/union and protected-polygon restoration before repair.
- Read-only operation tracing found a 3.725 nanometre open triangular slit
  introduced by the final medial union. Close only near-coincident vertices
  on that local open boundary; do not split faces or perform a global weld.
  Also test per-span minimum clearance controls so safe entries are not all
  lifted by the same amount merely to clear two upper rings.
- Attempt 05 passed all numerical checks with twelve revised lace spans and
  per-span clearance controls, but pre-save review still found shallow forward
  edge dents. It was deliberately not saved. Pure subtraction cannot fill
  those inherited recesses; test a narrow surface-fitted two-skin union before
  the rounded trim, while retaining all existing preservation and visual gates.
- Attempt 06 blocked the lowest medial eyelet bore and produced visible filler
  lips. It was not saved. Inspection on 2026-10-05 traced the approximately
  3 mm surface-fit residual to samples hitting the aperture interior at
  z=0.064–0.065 m. Exclude the hole region, fit measured outer-skin sections
  locally with a 0.15 mm residual gate, and taper the filler below the opening;
  do not drill through a visibly distorted patch merely to pass the bore test.
- Attempt 07 stopped at the new section-sampling assertion before any Boolean
  or model save. Read-only inspection showed an intact outward-facing source
  sample with normal-x 0.29753, narrowly excluded by the 0.3 sampling heuristic.
  Use outward-facing first hits below the aperture and retain the 0.15 mm
  fit-residual check. This adjusts sample selection, not acceptance checks.
- Attempt 08 reduced local fit residuals to 0.020892 mm lateral and 0.017017 mm
  medial and cleared all fourteen bores, but still failed: three nonmanifold
  edges, neck/middle ratio 1.056116, and bilateral ratios reaching 1.131740.
  The previews show abrupt filler lips. No model was saved. Reject this filler
  method rather than relax the gates or treat its improved fit as visual success.
  Restore the exact attempt-05 helper for a numerically passing, explicitly
  unfinished review checkpoint. This rollback does not resolve the previously
  documented shallow edge dents or grant visual approval.
- Attempt 09 repeated the exact numerically passing attempt-05 helper and saved
  one isolated Trial 07 review checkpoint. Reopen checks, the independent
  782,854-polygon preservation audit and all thirteen proof hashes pass. Full
  visual review still rejects edge dents, lowest-eyelet junction notches and
  peaked/rigid lace approaches. Saving the checkpoint is not completion or
  promotion. All rejected filler attempts remain archived; recommend a shared-
  boundary surface reconstruction instead of another additive-strip iteration.

## 2026-10-05 — Trial 08 Scope Preparation

- A read-only image lookup assumed the original uniform-neck trial had the
  standard `proofs/pair-lateral.png`; that file does not exist there. No file was
  created or modified. The verified Trial 05 and Trial 07 lateral proofs provide
  the needed curve-versus-step comparison instead.
- Direct web image fetches for Nike and adidas failed. The Nike reference was
  inspected in the existing browser; the adidas view was partly obscured by a
  cookie notice. Keep detailed claims tied to inspected imagery and official
  descriptions, and do not imply current stock or measured market popularity.
- The prior Trial 07 side-view review called the stepped panel boundary
  deliberate. The owner now requests its removal, and comparison with Trial 05
  shows that iteration's smooth curve. Trial 06's fixed cutter termination is a
  plausible cause. Treat this as a repair target, not a design feature to preserve
  or an excuse to weaken unrelated protected-geometry checks.
- During the confirmed execution, a read-only check requested `validation.json`
  before the saved-file reopen validation had finished writing it. The check
  returned file-not-found; no data was modified. Wait for the relevant build
  phase before consuming its final report. The later reopened report passed.
- Trial 08 attempt 01 restores the missing continuous side-panel curve and
  passes all unchanged numerical gates, but full thirteen-view inspection still
  rejects macro edge waviness, the small lowest-eyelet notch/scallop, uneven
  stitch visibility and stiff lace drape. The localized cutter fixes the broad
  termination artifact; reusing the forward cut/support construction does not
  complete the shared-boundary outer-skin/bevel cleanup. Preserve this visibly
  improved but unfinished checkpoint without promotion. Do not describe the
  step repair as completion of the owner's broader waviness/realism request.

## 2026-10-05 — Stage 3 Preparation

- Capability recheck still finds no `game-dev` executable on PATH. Retain the
  previously approved native Blender fallback and do not claim canonical CLI
  receipts. Stage 3 scope is owner-authorized; its new exact file-writing
  invocation still requires confirmation before execution under the skill.

## 2026-10-05 — R17 Material Study Execution

- The first studio proof overexposed Night Grid toward gray and the warm-stone
  chassis toward white. Numerical geometry/material checks passed, but did not
  establish the intended palette under lighting. Stop the remaining first-pass
  previews; preserve the saved model and completed images. Use a separate
  render-only exposure study with an explicit diagnostic gate and recorded
  exposure override before producing the remaining review set.
- A sandboxed process-status check was denied. An approved, narrowly filtered
  process lookup identified only this task's Blender process for interruption.
  The interrupted render returned before writing its image, so the original
  builder's subsequent hash read reported file-not-found. No source or saved
  candidate was lost; the first-pass preview set is incomplete, not a pass.
- The sandbox denied binding a localhost-only review server. Request the scoped
  permission needed for that private review surface; do not expose the folder
  on a LAN interface or treat a local inspection page as website publication.
- The owner rejected the Night Grid lattice while liking the rest of the shoe.
  The corrected-exposure batch was interrupted after its two Night Grid proofs;
  the next cancelled render triggered the same missing-image hash error. Source
  and saved candidate remain intact. Prepare a separate grid-free material
  derivative, remove both lattice color and bump, and preserve other finishes.
  The new script must not be described as an executed Blender correction before
  exact invocation confirmation and saved/reopened validation.
- The separate read-only Trial 02 material audit crashed during sandboxed Blender
  startup (exit 139, before reading the model or running the audit). Request a
  scoped native execution for that audit; do not treat a startup crash as material
  preservation evidence or overwrite either saved model. The authorized build
  and render process remains separate.
- The first material fingerprint included Blender's per-load `session_uid` and
  therefore falsely flagged every material. A diagnostic isolated those runtime
  identities rather than shader differences. Exclude only that non-content
  property and rerun the saved-file comparison; retain all node, input, color-ramp,
  link and other material-property comparisons.
- A batch of three native-resolution PNG previews exceeded the tool's 64 MB
  transport limit. No assets were lost; inspect one full-resolution image per
  call. The verifier in the same orchestration had completed independently and
  its saved report was checked before proceeding.
- The browser showed blank mixed-look images despite completed PNGs and valid
  natural dimensions. Reloading and a shorter gallery alone did not fix it.
  Hash-versioned image URLs forced fresh decoding and restored the images;
  record this as a stale browser-image issue, not a failed Blender render.

## 2026-10-06 — Project File Review Phase 1

- The first local commerce check and migration-drift command set explicit
  commerce mode without providing safe local Stripe placeholders. Both commands
  correctly failed closed before running. No repository or database state was
  changed. Rerun the baseline with explicit non-provider placeholder values and
  `TREADJOY_RUNSERVER_DEFAULTS=1` so the local check uses SQLite rather than
  assuming access to configured PostgreSQL.

## 2026-10-06 — Project File Review Phase 2

- An initial read-only one-line Python command intended to summarize text-file
  hygiene embedded escaped newlines incorrectly and stopped with a syntax error.
  It changed nothing. Use the tested repository-hygiene script rather than an
  ad hoc inline command for the authoritative result.
- The first development-lock compilation inherited a pip-tools cache path under
  the user Library, which is not writable in the project sandbox, and stopped
  before dependency resolution. Rerun with a task-specific cache under `/tmp`;
  do not broaden filesystem permissions merely to use the default cache.
- The first local Ruff pre-commit hook used an unqualified `python` command.
  Pre-commit's system-language hook resolved that command to the host Anaconda
  interpreter rather than the repository virtual environment, so Ruff was not
  found. Point the local hook at `.venv/bin/python`; CI continues to invoke the
  runner's hash-locked Python environment directly.
- The first local `pip-audit` run could not bootstrap its isolated audit
  environment while network access was restricted. It changed no project files.
  Rerun the same hash-locked requirements audit with scoped package and advisory
  access instead of weakening the audit or suppressing the failure.
- A later inventory-summary command repeated the earlier escaped-newline error
  in an inline Python expression and stopped without changing files. This was
  avoidable after the first occurrence; use a straightforward tabular reader or
  the maintained inventory tooling for subsequent summaries.

## 2026-10-06 — R17 Companion Study Preparation

- The initial instruction-file discovery included an absent workspace `.agents`
  directory and returned exit 2. No files changed. Subsequent inspection used
  the known development paths and supplied repository instructions instead of
  assuming that optional directory exists. The `game-dev` CLI remains unavailable;
  retain the approved native Blender path and exact-invocation approval gate.

## 2026-10-06 — R17 Trial 03 Reopen Check

- The confirmed companion build saved its isolated candidate, then stopped before
  rendering because the original-object snapshot compared unevaluated world
  matrices after reopening on a different active scene. Blender returned process
  exit 0 despite the Python assertion; process exit alone is not success evidence.
  Preserve the candidate and snapshots; do not overwrite or relax exact comparisons.
- A read-only comparison initially reproduced identity world matrices for the
  inactive Night Grid scene. Evaluating every scene before the comparison removed
  all original object/collection differences. The only shader-record differences
  were expected `ID.users` counts from new scene instances. Retain exact transforms,
  original shader content and geometry gates; exclude only the documented reference
  counts. Use `--python-exit-code 1` for the proposed render-only continuation.

## 2026-10-07 — Project File Review Phase 3

- The initial package rename used `git mv`, but the project sandbox permits
  reading rather than writing the repository's `.git` metadata, so Git could
  not create `index.lock`. The command moved nothing. A following shell glob
  consequently had no match and also made no changes. Use a normal filesystem
  move inside the writable project tree; Git can still recognize the deleted
  and added paths as a rename when the owner later stages the change.
- The first full research verification used repository-wide Django test
  discovery. That imported commerce/account tests and migrations even though
  those apps are deliberately uninstalled in research mode, producing expected
  capability-boundary and missing-commerce-migration failures. No source or
  persistent database state changed. Use the documented installed-app labels
  (`web.core web.products web.survey web.waitlist`) for the authoritative
  research suite, as CI and `docs/ci.md` require.
- A final pre-commit verification set `PRE_COMMIT_HOME` to a new temporary
  directory. That discarded access to the already-built local hook environment
  and forced a network fetch for the pinned Gitleaks repository, which failed
  under restricted DNS. The attempted run changed no project files. Reuse the
  existing pre-commit cache for local verification; CI independently builds the
  pinned hook in its network-enabled job.
- The first post-refresh inventory summary queried a nonexistent `action`
  column instead of the documented `disposition` column and stopped with a
  `KeyError` after printing only the entry and byte totals. The inventory file
  itself had already been written correctly. Rerun the read-only summary using
  the actual TSV header; do not infer a failed inventory build from the summary
  script's error.

## 2026-10-07 — Project File Review Phase 4

- The first active design-workspace contract test changed its working directory
  to the design script folder but still invoked `.venv/bin/python` as though it
  were at the repository root. The shell stopped before running the test and no
  files changed. Use the absolute repository virtual-environment interpreter
  when a validation command must run from a nested workspace directory.

## 2026-10-07 — Project File Review Phase 5

- A read-only attempt to verify the current apex, `www`, and private research
  endpoints through the web inspection tool returned inaccessible-URL errors
  for all three hosts. No external or repository state changed. The README was
  corrected to date the available September evidence and explicitly leave all
  current external state unverified rather than treating historical evidence as
  a live-service assertion.

## 2026-10-07 — Project File Review Phase 7

- The first parallel final-suite orchestration did not retain the commerce
  process session identifier after the command exceeded its initial output
  window, so its final status could not be collected. A follow-up `ps` check was
  also blocked by the project sandbox and changed no state. The commerce suite
  was rerun once in a retained session and completed successfully; only that
  complete 289-test result is used as final evidence.
- The first two final `pip-audit` processes could not upgrade the isolated
  audit environment while network access was restricted. They changed no
  project files and produced no vulnerability result. The combined hash-locked
  audit was rerun with scoped advisory/package access and reported no known
  vulnerabilities.
