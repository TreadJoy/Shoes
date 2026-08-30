# Verification Limitations

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
