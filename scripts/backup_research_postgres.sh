#!/usr/bin/env bash

# Produce an encrypted logical export outside the repository. Recent recovery
# remains provider PITR; this export is the portable, owner-controlled copy.
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL is required and must stay out of logs}"
: "${BACKUP_ENCRYPTION_KEY_FILE:?BACKUP_ENCRYPTION_KEY_FILE is required}"
: "${BACKUP_DIR:?BACKUP_DIR is required}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
backup_dir="$(cd "$BACKUP_DIR" 2>/dev/null && pwd || true)"
test -n "$backup_dir" || {
  echo "BACKUP_DIR must already exist." >&2
  exit 1
}
case "$backup_dir" in
  "$repo_root"|"$repo_root"/*)
    echo "BACKUP_DIR must be outside the repository." >&2
    exit 1
    ;;
esac
test -f "$BACKUP_ENCRYPTION_KEY_FILE" || {
  echo "BACKUP_ENCRYPTION_KEY_FILE must point to an existing protected file." >&2
  exit 1
}

export PGSSLMODE="${PGSSLMODE:-require}"

umask 077
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
output="$backup_dir/treadjoy-research-${stamp}.dump.gz.enc"
temporary="${output}.tmp"
trap 'rm -f "$temporary"' EXIT

pg_dump "$DATABASE_URL" --format=custom --no-owner --no-acl \
  | gzip -c \
  | openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 \
      -pass "file:$BACKUP_ENCRYPTION_KEY_FILE" \
      -out "$temporary"
mv "$temporary" "$output"
sha256sum "$output" > "${output}.sha256"

# Keep no more than the approved 35-day rolling window.
find "$backup_dir" -type f -name 'treadjoy-research-*.dump.gz.enc*' -mtime +35 -delete
echo "encrypted research backup created: $(basename "$output")"
