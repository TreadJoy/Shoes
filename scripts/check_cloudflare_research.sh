#!/usr/bin/env bash
set -euo pipefail

# Read-only synthetic edge checks. All URLs, cookie files, and origin targets
# are supplied at run time; no provider credentials belong in this script.

: "${RESEARCH_URL:?Set RESEARCH_URL to the HTTPS research hostname}"
: "${MEDIA_URL:?Set MEDIA_URL to the HTTPS media hostname}"
: "${RESEARCH_ACCESS_COOKIE_FILE:?Set RESEARCH_ACCESS_COOKIE_FILE to an owner-only cookie-jar outside the repository}"

[[ -f "$RESEARCH_ACCESS_COOKIE_FILE" ]] || {
  echo "RESEARCH_ACCESS_COOKIE_FILE does not exist" >&2
  exit 2
}

case "$RESEARCH_URL" in
  https://research.tread-joy.com|https://research.tread-joy.com/*) ;;
  *) echo "RESEARCH_URL must be the HTTPS research.tread-joy.com hostname" >&2; exit 2 ;;
esac
case "$MEDIA_URL" in
  https://media.research.tread-joy.com|https://media.research.tread-joy.com/*) ;;
  *) echo "MEDIA_URL must be the HTTPS media.research.tread-joy.com hostname" >&2; exit 2 ;;
esac

if [[ "${REQUIRE_ORIGIN_CHECK:-false}" == "true" && -z "${ORIGIN_URL:-}" ]]; then
  echo "REQUIRE_ORIGIN_CHECK=true requires ORIGIN_URL" >&2
  exit 2
fi

umask 077
work_dir="$(mktemp -d "${TMPDIR:-/tmp}/treadjoy-cloudflare-check.XXXXXX")"
trap 'rm -rf "$work_dir"' EXIT

cookie_args=(--cookie "$RESEARCH_ACCESS_COOKIE_FILE")

request_status() {
  local url="$1"
  local output="$2"
  curl --silent --show-error --location --max-time 20 \
    "${cookie_args[@]}" --dump-header "$output" --output /dev/null \
    --write-out '%{http_code}' "$url"
}

header_contains() {
  local file="$1"
  local name="$2"
  local value="$3"
  grep --ignore-case --fixed-strings -- "$name: $value" "$file" >/dev/null
}

check_public_response() {
  local label="$1"
  local url="$2"
  local expected_status="$3"
  local header_file="$work_dir/$label.headers"
  local status
  status="$(request_status "$url" "$header_file")"
  [[ "$status" == "$expected_status" ]] || {
    echo "$label returned HTTP $status; expected $expected_status" >&2
    exit 1
  }
  header_contains "$header_file" "X-Content-Type-Options" "nosniff" || {
    echo "$label is missing X-Content-Type-Options: nosniff" >&2
    exit 1
  }
  header_contains "$header_file" "X-Frame-Options" "DENY" || {
    echo "$label is missing X-Frame-Options: DENY" >&2
    exit 1
  }
  grep --ignore-case --fixed-strings "Referrer-Policy:" "$header_file" >/dev/null || {
    echo "$label is missing Referrer-Policy" >&2
    exit 1
  }
  header_contains "$header_file" "Strict-Transport-Security" "max-age=3600" || {
    echo "$label is missing staged HSTS" >&2
    exit 1
  }
  echo "$label: HTTP $status and required security headers"
}

check_public_response "research-home" "$RESEARCH_URL/" "200"
check_public_response "research-health" "$RESEARCH_URL/health/live/" "200"

health_headers="$work_dir/research-health.headers"
header_contains "$health_headers" "Cache-Control" "no-store" || {
  echo "research health response is cacheable" >&2
  exit 1
}

static_headers="$work_dir/static.headers"
static_status="$(request_status "$RESEARCH_URL/static/css/style.css" "$static_headers")"
[[ "$static_status" == "200" ]] || {
  echo "research static probe returned HTTP $static_status; expected 200" >&2
  exit 1
}
grep --ignore-case --fixed-strings "CF-Cache-Status:" "$static_headers" >/dev/null || {
  echo "research static probe is missing CF-Cache-Status" >&2
  exit 1
}
grep --ignore-case --fixed-strings "Cache-Control:" "$static_headers" >/dev/null || {
  echo "research static probe is missing Cache-Control" >&2
  exit 1
}
echo "research static probe: HTTP $static_status with edge cache status"

media_headers="$work_dir/media.headers"
media_status="$(request_status "$MEDIA_URL/media/nonexistent-synthetic-object.txt" "$media_headers")"
[[ "$media_status" == "404" ]] || {
  echo "blank-media probe returned HTTP $media_status; expected 404" >&2
  exit 1
}
header_contains "$media_headers" "X-Content-Type-Options" "nosniff" || {
  echo "media probe is missing X-Content-Type-Options: nosniff" >&2
  exit 1
}
grep --ignore-case --fixed-strings "CF-Cache-Status:" "$media_headers" >/dev/null || {
  echo "media probe is missing CF-Cache-Status" >&2
  exit 1
}
grep --ignore-case --fixed-strings "Cache-Control:" "$media_headers" >/dev/null || {
  echo "media probe is missing Cache-Control" >&2
  exit 1
}
header_contains "$media_headers" "Strict-Transport-Security" "max-age=3600" || {
  echo "media probe is missing staged HSTS" >&2
  exit 1
}
echo "blank media probe: HTTP $media_status with edge cache status"

echo "owner Access session: authenticated checks used the supplied cookie file"

if [[ -n "${ORIGIN_URL:-}" ]]; then
  case "$ORIGIN_URL" in
    https://*) ;;
    *) echo "ORIGIN_URL must use HTTPS" >&2; exit 2 ;;
  esac
  for header in "" "invalid-origin-secret"; do
    direct_args=()
    if [[ -n "$header" ]]; then
      direct_args+=(--header "X-TreadJoy-Origin: $header")
    fi
    direct_status="$(curl --silent --show-error --location --max-time 20 \
      "${direct_args[@]}" --output /dev/null --write-out '%{http_code}' \
      "$ORIGIN_URL/")"
    [[ "$direct_status" == "403" ]] || {
      echo "direct origin accepted an invalid request: HTTP $direct_status" >&2
      exit 1
    }
  done
  echo "direct origin rejected requests without and with an invalid lock header"
else
  echo "ORIGIN_URL not set; direct-origin bypass check remains pending"
fi

echo "Cloudflare research synthetic checks passed"
