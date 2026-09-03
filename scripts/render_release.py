"""Promote or roll back one immutable Render service release.

The workflow supplies the Render API key through the environment only. This
module intentionally prints identifiers and statuses, never API responses or
provider error bodies that could contain configuration details.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import NoReturn
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_ROOT = "https://api.render.com/v1"
SERVICE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DEPLOY_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
TERMINAL_FAILURES = {
    "build_failed",
    "canceled",
    "cancelled",
    "deactivated",
    "deploy_failed",
    "failed",
    "update_failed",
}


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def validate_identifier(value: str, pattern: re.Pattern[str], name: str) -> str:
    if not pattern.fullmatch(value):
        fail(f"{name} has an invalid format")
    return value


def api_key() -> str:
    value = os.environ.get("RENDER_API_KEY", "").strip()
    if not value:
        fail("RENDER_API_KEY is required in the protected deployment environment")
    return value


def request_json(method: str, path: str, payload: dict | None = None) -> object:
    body = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key()}",
    }
    if payload is not None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(
        f"{API_ROOT}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"Render API request failed with HTTP {error.code}") from None
    except (URLError, TimeoutError, json.JSONDecodeError):
        raise RuntimeError("Render API request failed without a usable response") from None


def commit_id(deploy: dict) -> str:
    commit = deploy.get("commit")
    if isinstance(commit, dict):
        return str(commit.get("id") or "")
    return str(deploy.get("commitId") or commit or "")


def current_live_deploy(deploys: object) -> tuple[str, str]:
    if not isinstance(deploys, list):
        return "", ""
    for deploy in deploys:
        if isinstance(deploy, dict) and deploy.get("status") == "live":
            return str(deploy.get("id") or ""), commit_id(deploy)
    return "", ""


def write_manifest(path: str, values: dict[str, object]) -> None:
    Path(path).write_text(
        json.dumps(values, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def promote(service_id: str, release_sha: str, target: str) -> None:
    deploys = request_json("GET", f"/services/{service_id}/deploys")
    previous_deploy_id, previous_commit = current_live_deploy(deploys)
    response = request_json(
        "POST",
        f"/services/{service_id}/deploys",
        {"clearCache": "do_not_clear", "commitId": release_sha},
    )
    if not isinstance(response, dict):
        fail("Render returned an invalid deploy response")
    deploy_id = validate_identifier(str(response.get("id") or ""), DEPLOY_ID_RE, "deploy ID")

    timeout_seconds = int(os.environ.get("RENDER_DEPLOY_TIMEOUT_SECONDS", "900"))
    poll_seconds = int(os.environ.get("RENDER_DEPLOY_POLL_SECONDS", "10"))
    deadline = time.monotonic() + max(timeout_seconds, poll_seconds)
    while True:
        status_response = request_json(
            "GET", f"/services/{service_id}/deploys/{deploy_id}"
        )
        if not isinstance(status_response, dict):
            fail("Render returned an invalid deploy status")
        status = str(status_response.get("status") or "").casefold()
        deployed_commit = commit_id(status_response)
        if status == "live":
            if deployed_commit != release_sha:
                fail("Render reported live for a different commit")
            break
        if status in TERMINAL_FAILURES:
            fail(f"Render deploy ended in terminal status: {status}")
        if time.monotonic() >= deadline:
            fail("Render deploy did not become live before the timeout")
        time.sleep(max(poll_seconds, 1))

    timestamp = datetime.now(timezone.utc).isoformat()
    write_manifest(
        "release-promotion.json",
        {
            "target": target,
            "release_sha": release_sha,
            "deploy_id": deploy_id,
            "completed_at": timestamp,
        },
    )
    write_manifest(
        "rollback-manifest.json",
        {
            "target": target,
            "release_sha": release_sha,
            "previous_deploy_id": previous_deploy_id or None,
            "previous_commit": previous_commit or None,
            "captured_at": timestamp,
        },
    )
    print(
        f"Render promotion succeeded: target={target} "
        f"deploy_id={deploy_id} release_sha={release_sha}"
    )


def rollback(service_id: str, deploy_id: str, target: str) -> None:
    response = request_json(
        "POST",
        f"/services/{service_id}/rollback",
        {"deployId": deploy_id},
    )
    response_deploy_id = ""
    if isinstance(response, dict):
        response_deploy_id = str(response.get("id") or "")
    write_manifest(
        "rollback-result.json",
        {
            "target": target,
            "requested_deploy_id": deploy_id,
            "response_deploy_id": response_deploy_id or None,
            "requested_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    print(
        f"Render rollback requested: target={target} "
        f"deploy_id={deploy_id}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("promote", "rollback"))
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--target", required=True, choices=("staging", "production"))
    parser.add_argument("--release-sha")
    parser.add_argument("--deploy-id")
    args = parser.parse_args()

    validate_identifier(args.service_id, SERVICE_ID_RE, "service ID")
    if args.operation == "promote":
        if not args.release_sha:
            fail("--release-sha is required for promotion")
        validate_identifier(args.release_sha, SHA_RE, "release SHA")
        promote(args.service_id, args.release_sha, args.target)
    else:
        if not args.deploy_id:
            fail("--deploy-id is required for rollback")
        validate_identifier(args.deploy_id, DEPLOY_ID_RE, "deploy ID")
        rollback(args.service_id, args.deploy_id, args.target)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"Release operation stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from None
