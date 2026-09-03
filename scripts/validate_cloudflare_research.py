#!/usr/bin/env python3
"""Validate the repository-only Cloudflare research edge contract.

This is deliberately a local, dependency-free check. It validates the policy
shape and fixed host/path invariants, but never calls the Cloudflare API.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "deploy" / "cloudflare" / "research" / "policy.json"


class PolicyError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PolicyError(message)


def validate(policy: dict) -> None:
    require(policy.get("schema_version") == 1, "schema_version must be 1")
    require(policy.get("status") == "review-before-apply", "policy must remain review-before-apply")
    require(policy.get("zone") == "tread-joy.com", "zone must be tread-joy.com")

    hosts = policy["hostnames"]
    require(hosts == {
        "application": "research.tread-joy.com",
        "media": "media.research.tread-joy.com",
    }, "application/media hostnames changed")

    dns = policy["dns"]
    app_dns = dns["application"]
    require(app_dns["type"] == "CNAME", "research must use a CNAME")
    require(app_dns["target_env"] == "RENDER_RESEARCH_ORIGIN_HOST", "origin target must remain secret/env supplied")
    require(app_dns["proxied"] is True and app_dns["ttl"] == 1, "research DNS must be proxied with automatic TTL")
    media_dns = dns["media"]
    require(media_dns["type"] == "R2_CUSTOM_DOMAIN", "media must be managed by the R2 custom-domain connection")
    require(media_dns["target"] == "managed-by-r2-custom-domain", "media DNS target must not be invented")
    require(media_dns["proxied"] is True, "media custom domain must be proxied")
    require(dns["forbidden"] == [
        "r2.dev",
        "r2.cloudflarestorage.com",
        "direct-origin-records",
        "unproxied-application-records",
    ], "unsafe DNS access paths changed")

    tls = policy["tls"]
    require(tls["zone_encryption_mode"] == "strict", "Full (strict) TLS is required")
    require(tls["always_use_https"] is True, "HTTPS redirect must be enabled")
    require(tls["minimum_tls_version"] == "1.2" and tls["tls_1_3"] is True, "TLS floor changed")
    require(tls["hsts"] == {
        "max_age_seconds": 3600,
        "include_subdomains": False,
        "preload": False,
    }, "HSTS must remain at the staged rollout")
    require(tls["origin_certificate"]["required"] is True, "origin certificate validation is required")

    access = policy["access"]
    require(access["default_decision"] == "deny", "Access default must deny")
    require(access["allow_email"] == ["ethan@tread-joy.com"], "POC Access must allow only the owner")
    require(access["scope"] == "all-paths-including-admin", "Access must cover admin and all application paths")
    media_access = access["media_poc_policy"]
    require(media_access["hostname"] == hosts["media"], "media Access hostname changed")
    require(media_access["default_decision"] == "deny", "media Access default must deny")
    require(media_access["allow_email"] == ["ethan@tread-joy.com"], "media Access must allow only the owner")

    origin = policy["origin_lock"]
    require(origin["header_name"] == "X-TreadJoy-Origin", "origin header name changed")
    require(origin["secret_env"] == "TREADJOY_ORIGIN_SHARED_SECRET", "origin secret must be env supplied")
    require(origin["cloudflare_action"] == "overwrite-request-header", "Cloudflare must overwrite the origin header")
    require(origin["direct_origin_expected_status"] == 403, "direct origin must be rejected")
    require(origin["health_exempt_paths"] == ["/health/live/", "/health/ready/"], "health exemptions changed")

    headers = policy["security_headers"]["application"]
    for name in ("X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy", "Permissions-Policy", "Strict-Transport-Security"):
        require(name in headers and headers[name], f"missing security header: {name}")
    require(headers["X-Frame-Options"] == "DENY", "framing must remain denied")
    require(headers["Strict-Transport-Security"] == "max-age=3600", "HSTS header must match staged rollout")

    waf = policy["waf"]
    managed = waf["managed_ruleset"]
    require(managed["phase"] == "http_request_firewall_managed", "managed WAF phase changed")
    require(managed["action"] == "execute", "managed WAF must execute")
    require(managed["ruleset_id"] == "efb7b8c949ac4650a09736fc376e9aee", "managed ruleset ID changed")
    require(waf["admin_perimeter"]["cache"] == "bypass", "admin cache must bypass")
    require(waf["admin_perimeter"]["django_authorization_remains_required"] is True, "Django authorization must remain required")

    rate = policy["rate_limiting"]
    require(rate["phase"] == "http_ratelimit", "rate-limit phase changed")
    require(rate["characteristics"] == ["ip.src"], "rate-limit characteristic changed")
    require(rate["rollout"] == ["log", "validate-ordinary-traffic", "block"], "rate rollout must start in log mode")
    require(rate["plan_capability_gate"]["minimum_rules"] == 2, "both A2.2 edge rules must remain explicit")
    rules = rate["rules"]
    require(len(rules) == 2, "exactly two A2.2 edge rules are required")
    waitlist, survey = rules
    require(waitlist["requests_per_period"] == 5 and waitlist["period_seconds"] == 60, "waitlist edge guard changed")
    require(waitlist["application_authority"] == {"requests": 5, "period_seconds": 3600, "source": "web/waitlist/views.py"}, "waitlist application limit changed")
    require(survey["requests_per_period"] == 60 and survey["period_seconds"] == 60, "survey edge guard changed")
    require(survey["application_authority"] == {"requests": 60, "period_seconds": 3600, "source": "web/survey/views.py"}, "survey application limit changed")
    for rule in rules:
        require(rule["mitigation_timeout_seconds"] == 60, f"{rule['name']} mitigation timeout changed")
        require(rule["staging_action"] == "log" and rule["enforced_action"] == "block", f"{rule['name']} rollout action changed")
        require(rule["count_cached_assets"] is False, f"{rule['name']} must not count cached assets")
        require("http.host eq \"research.tread-joy.com\"" in rule["expression"], f"{rule['name']} host scope missing")
        require("http.request.method eq \"POST\"" in rule["expression"], f"{rule['name']} must count POST only")

    cache = policy["cache"]
    required_bypasses = {"/admin/", "/accounts/", "/cart/", "/orders/", "/waitlist/", "/survey/", "/health/"}
    require(required_bypasses.issubset(set(cache["bypass_paths"])), "a private/dynamic path lost its cache bypass")
    require(set(cache["bypass_methods"]) == {"POST", "PUT", "PATCH", "DELETE", "OPTIONS"}, "unsafe methods must bypass cache")
    require(cache["default_html"] == "bypass", "dynamic HTML must not be cached")
    require(len(cache["rules"]) == 2, "static and R2 media cache rules are required")
    for rule in cache["rules"]:
        require(rule["methods"] == ["GET", "HEAD"], f"{rule['name']} must be read-only")
        require(rule["edge_ttl_seconds"] == 31536000, f"{rule['name']} edge TTL changed")

    r2 = policy["r2"]
    require(r2["custom_domain"] == hosts["media"], "R2 custom domain changed")
    require(r2["public_access"] == "custom-domain-only", "R2 must use the controlled custom domain")
    require(r2["public_development_url"] is False, "r2.dev access must remain disabled")
    require(r2["allowed_prefixes"] == ["media/"], "R2 allowed prefix changed")
    require(r2["poc_object_count"] == 0, "POC media must remain blank")
    require(r2["separate_from_commerce"] is True, "R2 media must remain mode-separated")

    verification = policy["verification"]
    require(verification["synthetic_only"] is True, "verification must use synthetic data")
    require(verification["media_probe"] == "/media/nonexistent-synthetic-object.txt", "media probe must remain synthetic")
    require(set(verification["required_headers"]) >= {"X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy", "Strict-Transport-Security"}, "header probes are incomplete")


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) == 2 else DEFAULT_POLICY
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
        validate(policy)
    except (OSError, json.JSONDecodeError, PolicyError, KeyError) as exc:
        print(f"Cloudflare research policy invalid: {exc}", file=sys.stderr)
        return 1
    print(f"Cloudflare research policy valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
