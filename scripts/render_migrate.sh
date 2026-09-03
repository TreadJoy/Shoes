#!/usr/bin/env bash

# Run the initial/expand migration gate with the separate migrator role. Keep
# MIGRATION_DATABASE_URL out of the Render web service and ordinary logs.
set -euo pipefail

: "${MIGRATION_DATABASE_URL:?MIGRATION_DATABASE_URL is required and must stay out of logs}"
export DATABASE_URL="$MIGRATION_DATABASE_URL"
export DB_SSLMODE="${DB_SSLMODE:-require}"

python manage.py migrate --noinput
python manage.py migrate --check
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py check_research_boundary
python manage.py check_research_engagement
echo "research migration gate passed"
