#!/usr/bin/env bash

# Create the separate least-privilege database roles after Render Postgres is
# provisioned. Passwords are supplied through the shell environment only.
set -euo pipefail

: "${DATABASE_ADMIN_URL:?DATABASE_ADMIN_URL is required and must stay out of logs}"
: "${RESEARCH_RUNTIME_DB_PASSWORD:?RESEARCH_RUNTIME_DB_PASSWORD is required}"
: "${RESEARCH_MIGRATOR_DB_PASSWORD:?RESEARCH_MIGRATOR_DB_PASSWORD is required}"
: "${RESEARCH_BACKUP_DB_PASSWORD:?RESEARCH_BACKUP_DB_PASSWORD is required}"

export PGSSLMODE="${PGSSLMODE:-require}"

psql "$DATABASE_ADMIN_URL" \
  --set=ON_ERROR_STOP=1 \
  --set=runtime_password="$RESEARCH_RUNTIME_DB_PASSWORD" \
  --set=migrator_password="$RESEARCH_MIGRATOR_DB_PASSWORD" \
  --set=backup_password="$RESEARCH_BACKUP_DB_PASSWORD" <<'SQL'
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

ALTER DEFAULT PRIVILEGES FOR ROLE treadjoy_research_migrator IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO treadjoy_research_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE treadjoy_research_migrator IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO treadjoy_research_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE treadjoy_research_migrator IN SCHEMA public
  GRANT SELECT ON TABLES TO treadjoy_research_backup;
SQL

echo "research database roles provisioned (role names only)"
