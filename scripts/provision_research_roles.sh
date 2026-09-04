#!/usr/bin/env bash

# Create the separate least-privilege database roles after Render Postgres is
# provisioned. Passwords and the admin connection are supplied through the
# shell environment only; neither is passed as a process argument.
set -euo pipefail

: "${DATABASE_ADMIN_URL:?DATABASE_ADMIN_URL is required and must stay out of logs}"
: "${RESEARCH_RUNTIME_DB_PASSWORD:?RESEARCH_RUNTIME_DB_PASSWORD is required}"
: "${RESEARCH_MIGRATOR_DB_PASSWORD:?RESEARCH_MIGRATOR_DB_PASSWORD is required}"
: "${RESEARCH_BACKUP_DB_PASSWORD:?RESEARCH_BACKUP_DB_PASSWORD is required}"

eval "$(
  python3 - <<'PY'
import os
import shlex
from urllib.parse import unquote, urlsplit

raw = os.environ["DATABASE_ADMIN_URL"]
parsed = urlsplit(raw)
if parsed.scheme not in {"postgres", "postgresql"}:
    raise SystemExit("DATABASE_ADMIN_URL must use a PostgreSQL URL")
if not parsed.hostname or not parsed.username or not parsed.path.strip("/"):
    raise SystemExit("DATABASE_ADMIN_URL must include host, username, and database")

values = {
    "PGHOST": parsed.hostname,
    "PGPORT": str(parsed.port or 5432),
    "PGUSER": unquote(parsed.username),
    "PGPASSWORD": unquote(parsed.password or ""),
    "PGDATABASE": unquote(parsed.path.lstrip("/")),
}
for key, value in values.items():
    print(f"export {key}={shlex.quote(value)}")
PY
)"
unset DATABASE_ADMIN_URL
export PGSSLMODE="${PGSSLMODE:-require}"

psql --dbname="$PGDATABASE" --set=ON_ERROR_STOP=1 <<'SQL'
\getenv runtime_password RESEARCH_RUNTIME_DB_PASSWORD
\getenv migrator_password RESEARCH_MIGRATOR_DB_PASSWORD
\getenv backup_password RESEARCH_BACKUP_DB_PASSWORD
SELECT format(
  'CREATE ROLE treadjoy_research_runtime LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION',
  :'runtime_password'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'treadjoy_research_runtime')\gexec
SELECT format(
  'CREATE ROLE treadjoy_research_migrator LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION',
  :'migrator_password'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'treadjoy_research_migrator')\gexec
SELECT format(
  'CREATE ROLE treadjoy_research_backup LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION',
  :'backup_password'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'treadjoy_research_backup')\gexec

ALTER ROLE treadjoy_research_runtime PASSWORD :'runtime_password';
ALTER ROLE treadjoy_research_migrator PASSWORD :'migrator_password';
ALTER ROLE treadjoy_research_backup PASSWORD :'backup_password';

SELECT current_database() AS database_name \gset
GRANT CONNECT ON DATABASE :"database_name" TO treadjoy_research_runtime;
GRANT CONNECT ON DATABASE :"database_name" TO treadjoy_research_migrator;
GRANT CONNECT ON DATABASE :"database_name" TO treadjoy_research_backup;

GRANT USAGE ON SCHEMA public TO treadjoy_research_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO treadjoy_research_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO treadjoy_research_runtime;

GRANT USAGE, CREATE ON SCHEMA public TO treadjoy_research_migrator;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO treadjoy_research_migrator;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO treadjoy_research_migrator;

GRANT USAGE ON SCHEMA public TO treadjoy_research_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO treadjoy_research_backup;
SQL

# Only the role itself can change its default privileges. Connect as the
# migrator after the owner connection has created it, rather than attempting
# to grant default privileges for another role (which PostgreSQL rejects).
PGUSER=treadjoy_research_migrator \
PGPASSWORD="$RESEARCH_MIGRATOR_DB_PASSWORD" \
psql --dbname="$PGDATABASE" --set=ON_ERROR_STOP=1 <<'SQL'
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO treadjoy_research_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO treadjoy_research_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO treadjoy_research_backup;
SQL

echo "research database roles provisioned (role names only)"
