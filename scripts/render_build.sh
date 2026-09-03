#!/usr/bin/env bash

# Render build command for the research origin. Runtime dependencies remain
# hash-locked. Migrations run separately through render_migrate.sh because the
# selected POC web tier does not provide Render's paid pre-deploy hook.
set -euo pipefail

python -m pip install --require-hashes --requirement requirements.txt
python -m pip check
python manage.py collectstatic --noinput --clear
