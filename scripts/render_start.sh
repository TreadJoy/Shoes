#!/usr/bin/env bash

# Render start command for one private research POC instance. Migrations must
# run separately through render_migrate.sh with the migration-only database
# role; the ordinary web process must never receive that credential.
set -euo pipefail

python manage.py migrate --check
python manage.py check --deploy --fail-level WARNING

exec python -m gunicorn treadjoy.wsgi:application \
  --bind "0.0.0.0:${PORT:?PORT must be supplied by the origin}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --access-logfile - \
  --error-logfile - \
  --graceful-timeout 30 \
  --timeout 60
