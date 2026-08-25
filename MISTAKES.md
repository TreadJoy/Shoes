# Verification Limitations

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
