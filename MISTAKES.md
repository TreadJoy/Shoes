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
