# Continuous Integration

TreadJoy requires four stable GitHub checks before `main` can advance:

- `Application / Commerce PostgreSQL`
- `Application / Research PostgreSQL`
- `Supply Chain / Dependency Audit`
- `Security / Gitleaks`

The application workflow runs for pushes to `main`, pull requests targeting
`main`, and manual dispatches. Each deployment mode receives a separate
PostgreSQL service and process environment. The research job does not define
any `STRIPE_*` variable and explicitly selects only installed research apps.

## Isolation and credentials

Each application job starts a fresh PostgreSQL service with two empty
databases:

- `treadjoy_ci` proves the installed mode migrates from zero.
- `treadjoy_ci_test` is the Django test database.

The bootstrap administrator creates those databases and transfers ownership
to `treadjoy_ci`. Django uses only that login, which is explicitly
`NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`, and
`NOREPLICATION`. Django receives the pre-created test database through
`Shoes.ci_settings` and uses `--keepdb` so the restricted login never needs to
create or drop databases. The PostgreSQL service is destroyed with the job;
`--keepdb` does not persist data between workflow runs.

All committed credentials are conspicuously synthetic CI placeholders. The
jobs do not use repository secrets, so pull requests from forks receive the
same safe checks. Commerce provider values are deliberately not shaped like
real Stripe credentials; research receives none. Django commands run with
HTTP and HTTPS directed to an unused local port, while localhost remains
available for PostgreSQL. Email uses Django's in-memory backend.

Only setup-python's pip download cache is enabled. Virtual environments,
PostgreSQL data, test databases, collected static files, provider payloads, and
application state are never cached or uploaded.

## What each job proves

Both application jobs install the hash-locked runtime manifest, run `pip
check`, verify PostgreSQL 17.11 and the database role flags, migrate an empty
database, detect unapplied or missing migrations, compile Python, run Django's
normal and warning-fatal deployment checks, and collect static files beneath
the runner's temporary directory.

Commerce uses full Django discovery. It then runs the stocked and preorder
allocation concurrency classes explicitly so the log proves their PostgreSQL
row-locking cases executed rather than skipped. Research runs `web.core`,
`web.products`, `web.survey`, `web.waitlist`, and `web.accounts`; blanket
discovery is intentionally not used because commerce migration tests are not
part of the research application graph. Both jobs explicitly run the shared
waitlist database-contract test proving a unique-constraint failure rolls back
its complete atomic write.

The dependency job installs the standalone development lock, runs `pip check`,
and audits both runtime and development manifests with hashes and no
suppression. The Gitleaks job checks out complete Git history and does not
create PR comments or upload artifacts. It runs the official Gitleaks CLI
image, pinned to its Linux/AMD64 registry digest, with the checkout mounted
read-only. The scan uses `git --log-opts="--all"`, redacts findings, and requires
no license, provider token, or repository secret.

## Local reproduction

Use a disposable PostgreSQL 17.11 cluster. As its bootstrap administrator,
create the restricted role and two empty databases:

```sql
CREATE ROLE treadjoy_ci
    LOGIN PASSWORD 'treadjoy-ci-database-password-not-secret'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION;
ALTER DATABASE treadjoy_ci OWNER TO treadjoy_ci;
CREATE DATABASE treadjoy_ci_test OWNER treadjoy_ci;
```

Set the normal Django database and deployment-mode variables, plus:

```sh
export DJANGO_SETTINGS_MODULE=Shoes.ci_settings
export TREADJOY_CI=true
export CI_DB_TEST_NAME=treadjoy_ci_test
export CI_STATIC_ROOT=/absolute/path/to/disposable/staticfiles
```

Commerce additionally requires nonempty synthetic `STRIPE_SECRET_KEY`,
`STRIPE_PUBLISHABLE_KEY`, and `STRIPE_WEBHOOK_SECRET`. A research deployment
must omit all three. When reproducing CI in a shared local worktree whose
commerce `.env` defines them, explicitly override all three with empty values
for that process so research settings cannot load the commerce values.

Run the same checks as the workflow:

```sh
python -m pip install --require-hashes --requirement requirements.txt
python -m pip check
python manage.py migrate --noinput
python manage.py migrate --check
python manage.py makemigrations --check --dry-run
python -m compileall -q Shoes web
python manage.py check
DJANGO_DEBUG=False python manage.py check --deploy --fail-level WARNING
python manage.py collectstatic --noinput --clear
```

Run `python manage.py test --keepdb --noinput` for commerce. For research, run:

```sh
python manage.py test web.core web.products web.survey web.waitlist web.accounts --keepdb --noinput
```

Reproduce the secret scan from a full checkout with Docker:

```sh
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/repo:ro" \
  --workdir /repo \
  ghcr.io/gitleaks/gitleaks:v8.30.1@sha256:b109bc5f8f76a38196a3e413704fc5b9e3c32360bce4e4b603bd6f45b3721dbb \
  git --redact --no-banner --log-opts="--all" /repo
```

## Pin updates

GitHub actions use full commit SHAs with release-tag comments. Review the
upstream release and security notes before changing either value, then verify
the tag resolves to the committed SHA. PostgreSQL and Gitleaks use exact
versions and registry digests. For an upgrade, review the upstream release and
security notes, resolve the architecture-specific image digest with `docker
buildx imagetools inspect`, update the tag and digest together, and require the
affected checks to pass before merging. Do not replace these pins with floating
major or `latest` references.

## Branch protection and failure proof

After the four checks have completed successfully at least once, preserve all
existing `main` protections and require the exact names at the top of this
document with strict branch freshness enabled. Verify enforcement on a pull
request by temporarily adding an unconditional failure to one required
application job. Record the failed workflow run and GitHub's blocked merge
state, revert the probe, and require all four checks to return to green before
merging. Never merge the failure probe.

## Troubleshooting

- A database-creation permission error means the test database was not
  pre-created or `--keepdb` was omitted; do not grant `CREATEDB` to fix it.
- A research startup error naming Stripe means the shell inherited commerce
  variables; remove them completely.
- A skipped concurrency or database-contract test means the job is not using
  PostgreSQL and must fail acceptance even if the remaining suite is green.
- A static-collection failure should be fixed through `CI_STATIC_ROOT`; do not
  add collected files to the repository or cache them.
- Audit outages should be rerun after the advisory service recovers. Do not
  suppress findings or bypass the required check.
- A Gitleaks image-pull failure should be diagnosed as registry availability or
  a stale digest. Do not switch back to the licensed Action wrapper or add a
  `GITLEAKS_LICENSE` secret merely to make CI green.
