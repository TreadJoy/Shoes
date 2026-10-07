# Shoes Project File Review

## Purpose

This record governs the naming, location, correctness, archival, and deletion
review for files owned by the Shoes project. It does not authorize changes to
live services, external repositories, cloud storage, production databases, or
files outside this repository.

The machine-readable companion inventory is
`docs/file-review-inventory.tsv`. Rebuild it with:

```sh
.venv/bin/python scripts/build_file_review_inventory.py
```

## Baseline

- Review started: 2026-10-06.
- Repository root: `/Users/ethanschoen/Shoes`.
- Baseline commit: `8eac5397c483cd9a7b014d912134395f207b53fb`.
- Baseline working tree: clean.
- Tracked files before review artifacts: 307.
- Project-owned design material: approximately 13.5 GB under
  `media/development/`, dominated by `treadjoy-heritage-court-v3`.
- Local secrets and database contents are excluded from content inspection.

## Inventory Boundaries

The inventory includes tracked repository files, project-owned ignored design
files, ignored tool-state files, local configuration/database placeholders,
and operating-system litter. SHA-256 hashes are recorded for ordinary files.
`.env` and `db.sqlite3` are recorded by path and size but deliberately not read
or hashed.

The following reproducible trees are represented by this boundary record rather
than by one inventory row per dependency or cache file:

- `.git/`
- `.venv/`, `venv/`, and `env/`
- `.pnpm-store/`
- all `.ruff_cache/`, `node_modules/`, `.wrangler/`, `__pycache__/`, and
  `staticfiles/` trees

These locations are not reviewed as project source. They may be recreated from
the repository's dependency locks, source files, and documented tooling.

## Preliminary Classifications

| Classification | Meaning |
| --- | --- |
| `review` | Current tracked source or current design-workspace candidate. |
| `investigate` | Ownership, usefulness, or correct destination needs evidence. |
| `archive` | Superseded but meaningful material to retain indefinitely. |
| `preserve` | Private local state that must not be exposed or casually removed. |
| `delete` | Reproducible litter; removal occurs only in the deletion phase. |

The classifications are intentionally preliminary. No source, design asset,
secret, or database has been deleted or moved in Phase 1.

## Safeguards for Later Phases

1. Search references and confirm owning workflows before every rename, move, or
   tracked-file deletion.
2. Preserve Django URL names, model identities, migrations, database tables,
   and mode boundaries during structural work.
3. Verify asset hashes and destination completeness before removing an original.
4. Archive meaningful creative history indefinitely; do not treat an older
   design generation as disposable merely because a newer one exists.
5. Do not encode unresolved product, commerce, privacy, security, or operations
   policy while correcting files.
6. Keep secrets, customer data, local databases, generated dependencies, and
   unapproved media out of Git.
7. Record attempted actions that fail and their resolution in `MISTAKES.md`.

## Phase Status

| Phase | Status | Evidence |
| --- | --- | --- |
| 1. Inventory and safeguards | Complete | 3,160 files and 14,154,802,383 bytes inventoried at the initial snapshot. |
| 2. Naming and repository standards | Complete | Documented conventions, EditorConfig, Ruff, hygiene checks, and CI/pre-commit enforcement verified. |
| 3. Django project-package rename | Complete | Internal package is `treadjoy`; both supported mode suites and package-reference checks pass. |
| 4. File location and design cleanup | Complete | Private design sources are separated from runtime media with verified active/archive placement. |
| 5. Correctness and content review | Complete | Source, configuration, documentation, templates, and structured-data checks passed after focused corrections. |
| 6. Archival and deletion | Complete | Superseded design history is retained; confirmed OS/tool/bytecode residue was removed. |
| 7. Final verification and handoff | Complete | Full supported-mode, migration, dependency, secret, hygiene, and inventory checks passed. |

## Phase 1 Verification

- Inventory: 3,160 entries at the initial snapshot—307 tracked and 2,853
  ignored or untracked project-owned files.
- Preliminary actions: 2,843 review, 302 archive, 8 delete, 5 investigate,
  and 2 preserve.
- Inventory-classification tests: 7 passed.
- Commerce local suite: 287 passed, 42 skipped.
- Research local suite: 181 passed, 8 skipped.
- Commerce and research system checks: passed.
- Migration drift: no changes detected.
- Python compilation and dependency consistency: passed.
- PostgreSQL service at `127.0.0.1:5432`: unavailable locally, so PostgreSQL
  concurrency and constraint behavior remains covered by the existing CI job
  rather than this local Phase 1 run.
- Expected SQLite warnings were limited to unsupported database comments and
  `nulls_distinct` constraints; they are not PostgreSQL acceptance evidence.

## Phase 2 Verification

- Added prospective, ecosystem-aware naming and location conventions; existing
  path renames remain gated to their planned phases.
- Added EditorConfig plus non-mutating repository-hygiene, Ruff, pre-commit, and
  CI checks.
- Mechanically corrected 19 missing final newlines and one trailing-whitespace
  occurrence without changing rendered content or application behavior.
- Removed four unused Python imports/bindings identified by Ruff. Stripe webhook
  signature verification remains in place and its focused six-test suite passed.
- Added hash-locked Ruff 0.16.10. The dependency audit then exposed existing
  advisories in PyJWT 2.13.0, urllib3 2.7.0, and virtualenv 21.7.5; explicit
  security floors now resolve to PyJWT 2.15.1, urllib3 2.8.0, and virtualenv
  21.14.5. Both regenerated locks report no known vulnerabilities.
- Cloudflare Access JWT tests: 8 passed.
- Repository safeguard tests: 13 passed.
- Commerce local suite: 287 passed, 42 skipped.
- Research local suite: 181 passed, 8 skipped.
- Both mode checks, migration drift, compilation, dependency consistency,
  pre-commit hygiene, and Ruff checks passed.
- The final inventory refresh preserved concurrent additions under the current
  `heritage-court-v3` design workspace; Phase 2 did not edit those assets.
- PostgreSQL remained unavailable locally; existing PostgreSQL CI remains the
  authority for backend-specific constraints and concurrency.

## Phase 3 Verification

- Renamed the internal Django project package from the ambiguous `Shoes` to
  `treadjoy` without changing the repository/root name, catalog label, public
  copy, URL namespaces, model identities, or migrations.
- Updated settings modules, WSGI/ASGI entry points, middleware, structured
  logger names, health checks, tests, scripts, CI, pre-commit, Ruff, and current
  operational documentation to the canonical package name.
- Added a clean-process regression test proving `treadjoy` is importable and
  the former `Shoes` Python package is not.
- Commerce local suite: 288 passed, 42 skipped.
- Installed-app research suite: 182 passed, 8 skipped.
- Focused settings, deployment-mode, health, observability, and Cloudflare
  Access tests: 51 passed in each mode.
- Both mode checks, migration drift, Python compilation, dependency
  consistency, repository hygiene, Ruff, pre-commit, and diff whitespace checks
  passed. Expected SQLite limitations remain unchanged; PostgreSQL CI is still
  authoritative for PostgreSQL-specific behavior.
- The refreshed inventory contains 3,181 entries and 14,263,839,765 bytes, with
  ten `treadjoy/` package files and no `Shoes/` paths. Because this sandbox
  cannot write Git's index, those moved files appear as delete/untracked until
  the owner stages them; Git can then detect the renames normally.

## Phase 4 Verification

- Established `design/` as the documented private product-design workspace and
  ignored its bulky `active/` and `archive/` trees while keeping the governing
  `design/README.md` reviewable in Git.
- Moved the current Heritage Court V3 workspace to
  `design/active/treadjoy-heritage-court-v3/` and the superseded V1/V2
  generations to `design/archive/`. Runtime `media/` now contains only its empty
  product-upload directory, the intentional development logo placeholder, and
  operating-system litter reserved for Phase 6.
- Verified 2,854 untouched design files against the pre-move inventory by
  relative path, byte size, and SHA-256 hash. Three current files were then
  intentionally edited: the active R17 audit root, its pending continuation
  command, and the archived V2 validation command. Historical reports and
  executed commands retain their original paths as audit evidence.
- Active module-contract tests: 27 passed. Archived V2 documentation contract:
  passed. Public release-content tests: 23 passed in research and 23 passed in
  commerce; both application mode checks passed.
- Inventory classification, repository hygiene, and Ruff safeguards passed.
  The refreshed inventory contains 3,182 entries; active design files remain
  under review, 302 superseded artifacts remain marked for indefinite archive,
  and no design asset was deleted or exposed as public media.

## Phase 5 Verification

- Reviewed project source and current documentation for demonstrable mistakes,
  stale assertions, malformed examples, unresolved markers, and contradictory
  deployment claims without changing approved business policy.
- Restored an actionable `manage.py` error when Django cannot be imported and
  added a clean-process regression test for that failure path.
- Corrected the README research-boundary command example, an `AGENTS.md`
  grammar error, the active R17 design path, and chronological design-trial
  status in `PROJECT_PLAN.md`.
- Reconciled current deployment wording across the README, project plan,
  provider records, and `render.yaml`: repository evidence proves the private
  POC state recorded in September 2026, while the recorded October 3 database
  expiration has passed and the present provider, DNS, certificate, and edge
  state remains unverified. No external-service state was inferred.
- Verified all 38 Django templates parse in both modes. Markdown local-link,
  JSON, YAML, TOML, CSV, shell, and JavaScript syntax checks passed for
  project-owned files; dependency trees and private design outputs were kept
  outside source-data claims. Unresolved placeholders and policy markers are
  intentional launch gates rather than silently completed work.
- Commerce local suite: 289 passed, 42 skipped. Installed-app research suite:
  183 passed, 8 skipped. Both mode checks and migration-drift checks passed.
- Repository safeguard tests: 13 passed. Python compilation, dependency
  consistency, repository hygiene, Ruff, pre-commit, and diff whitespace checks
  passed.
- The Phase 5 inventory contains 3,185 entries and 14,263,875,770 bytes:
  2,849 remained under review, 302 were designated for archive, 21 required
  final investigation, 2 private-state records remained preserved, and 11
  reproducible `.DS_Store` files were confirmed deletion candidates.
- No approved launch policy, historical audit evidence, customer-facing claim,
  private design asset, or public-service configuration was changed. PostgreSQL
  remained unavailable locally; PostgreSQL CI remains authoritative for
  backend-specific constraints and concurrency.

## Phase 6 Verification

- Confirmed the two superseded design generations are correctly isolated under
  `design/archive/` and are not consumed as active inputs. Their 302 meaningful
  records remain intact: 236 V1 files totaling 464,185,978 bytes and 66 V2
  files totaling 38,282,197 bytes.
- Recorded deterministic path/size/content manifest digests for the preserved
  archive state: V1
  `3eea448a564c78bd9112bbd9cf282fa13dd6072c5e94097585f8a05c064478b8`
  and V2
  `d71299ec6f03197491710a644de75f946a260b324d8b29fd94b2026c9398a681`.
- Deleted 11 confirmed `.DS_Store` files, six generated Python bytecode files
  from the V2 archive, and one stale Impeccable hook cache containing obsolete
  absolute design paths. These files are not recoverable from this working tree
  but are reproducible operating-system/tool artifacts and contain no retained
  project source or evidence.
- Preserved the local `.env` and SQLite database without reading their contents.
  The development AI logo is now explicitly classified as a private,
  development-only placeholder that remains unapproved for public deployment.
- Resolved all remaining inventory classifications. The refreshed inventory has
  3,173 entries and 14,263,781,663 bytes: 2,868 current records under review,
  302 archived records, and 3 intentionally preserved private records. No item
  remains classified for investigation or deletion.

## Phase 7 Verification And Handoff

- Commerce local suite: 289 passed, 42 skipped. Installed-app research suite:
  183 passed, 8 skipped. Both release-content checks passed in each suite.
- Commerce and research system checks passed, and both modes reported no
  migration drift. Expected SQLite limitations are not PostgreSQL acceptance
  evidence; the PostgreSQL CI jobs remain authoritative for database-specific
  constraints, locking, and concurrency.
- The combined hash-locked runtime/development dependency audit reported no
  known vulnerabilities, and `pip check` reported no broken requirements.
  Pre-commit Gitleaks passed for Git-visible files; the new unstaged package,
  scripts, standards, and review artifacts were also scanned directly with no
  leaks found.
- Repository hygiene, Ruff, Python compilation, 15 safeguard tests, pre-commit,
  and diff whitespace checks passed. The final package/reference scan found no
  operational `Shoes.*` imports or active references to the former design
  locations.
- The final inventory contains 3,173 records totaling 14,263,784,419 bytes:
  2,868 reviewed current records, 302 archived design records, and 3
  intentionally preserved private records. Nothing remains classified for
  investigation or deletion.
- This review does not claim current external POC availability; the provider,
  DNS, certificate, and edge state still require owner-authorized live
  verification. No external service or database was changed.
- Git staging remains an owner action because this workspace cannot write the
  repository index. Until staged, Git presents the `Shoes/` to `treadjoy/`
  package move as ten deletions plus ten untracked files, and the new review
  safeguards also remain untracked. Stage the complete reviewed working tree
  together so Git can detect the package renames and preserve one coherent
  change set.
