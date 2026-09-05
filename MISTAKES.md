# Verification Limitations

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
