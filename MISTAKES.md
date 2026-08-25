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
- Impact: no project database was changed, but the focused PostgreSQL suite
  remains unavailable in this sandbox.
- Containment: syntax, static checks, and the test code remain runnable; run
  the focused suite on a host/container that permits PostgreSQL shared memory
  before treating its database coverage as complete. A1.1 remains the durable
  CI solution.
