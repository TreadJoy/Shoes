#!/usr/bin/env bash

# Run the bounded research jobs from a provider cron service or a controlled
# provider shell. A local scheduler requires an approved private database path;
# do not expose PostgreSQL to make it reachable. The ordinary web process must
# not receive the Resend management key used by the sync job.
set -euo pipefail

test "${TREADJOY_MODE:-}" = "research" || {
  echo "TREADJOY_MODE must be research for research jobs." >&2
  exit 1
}

job_limit="${RESEARCH_JOB_LIMIT:-100}"
case "$job_limit" in
  ''|*[!0-9]*) echo "RESEARCH_JOB_LIMIT must be an integer." >&2; exit 1 ;;
esac
test "$job_limit" -ge 1 && test "$job_limit" -le 1000 || {
  echo "RESEARCH_JOB_LIMIT must be between 1 and 1000." >&2
  exit 1
}

python manage.py clearsessions
python manage.py deliver_research_email --limit "$job_limit"

# Contact synchronization is intentionally skipped when the management key is
# absent. This keeps the key out of the web service and permits a send-only POC.
if [ -n "${RESEARCH_RESEND_MANAGEMENT_API_KEY:-}" ]; then
  python manage.py sync_research_resend --limit "$job_limit"
else
  echo "research_resend_sync=skipped management_key_unavailable"
fi

# Retention is report-only until an effective policy and an owner-approved
# destructive run are configured. The command itself refuses draft apply runs.
python manage.py enforce_research_retention
