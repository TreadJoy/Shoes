#!/usr/bin/env python3
"""Run the safe local portion of the A2.3 research launch rehearsal.

The command writes logs and a sanitized evidence manifest outside the repository.
It never calls Render, Cloudflare, a provider API, or a production endpoint.
The resulting decision is always STOP until the external staging gates and owner
acceptance are recorded.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_TEST_LABELS = (
    "web.core.tests.test_health",
    "web.core.tests.test_observability",
    "web.core.tests.test_homepage",
    "web.core.tests.test_metadata",
    "web.core.tests.test_research_boundary",
    "web.core.tests.test_research_rehearsal",
    "web.survey.tests.test_survey_flow",
    "web.waitlist.tests",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence-dir",
        help="Existing or new directory outside the repository for evidence logs",
    )
    parser.add_argument(
        "--python",
        dest="python_bin",
        default=os.environ.get("PYTHON_BIN", str(REPO_ROOT / ".venv/bin/python")),
        help="Python executable used for Django checks (defaults to .venv/bin/python)",
    )
    return parser.parse_args()


def evidence_dir(value: str | None) -> Path:
    if value:
        target = Path(value).expanduser().resolve()
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = Path(os.environ.get("TMPDIR", "/tmp")) / (
            f"treadjoy-a2.3-rehearsal-{stamp}"
        )
        target = target.resolve()

    if target == REPO_ROOT or REPO_ROOT in target.parents:
        raise SystemExit("--evidence-dir must be outside the repository")
    target.mkdir(parents=True, exist_ok=True)
    return target


def command_result(
    name: str,
    command: list[str],
    *,
    environment: dict[str, str],
    output_dir: Path,
    expected_returncode: int = 0,
) -> dict[str, object]:
    safe_name = "".join(
        char if char.isalnum() or char in "-_" else "_" for char in name
    )
    output_path = output_dir / f"{safe_name}.log"
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    output_path.write_text(
        f"$ {' '.join(command)}\n\n{completed.stdout}{completed.stderr}",
        encoding="utf-8",
    )
    return {
        "name": name,
        "status": "passed" if completed.returncode == expected_returncode else "failed",
        "returncode": completed.returncode,
        "expected_returncode": expected_returncode,
        "evidence_file": output_path.name,
    }


def git_value(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def main() -> int:
    args = parse_args()
    output_dir = evidence_dir(args.evidence_dir)
    python_bin = Path(args.python_bin).expanduser()
    if not python_bin.is_absolute():
        python_bin = REPO_ROOT / python_bin
    if not python_bin.is_file() or not os.access(python_bin, os.X_OK):
        raise SystemExit(f"Python executable is not available: {python_bin}")

    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("STRIPE_"):
            environment.pop(key)
    environment.update(
        {
            "DJANGO_SETTINGS_MODULE": "Shoes.settings",
            "TREADJOY_ENVIRONMENT": "local",
            "TREADJOY_MODE": "research",
            "TREADJOY_RUNSERVER_DEFAULTS": "1",
            "SECRET_KEY": "treadjoy-a2.3-rehearsal-key-not-production",
        }
    )

    results: list[dict[str, object]] = []
    results.append(
        command_result(
            "cloudflare policy validator",
            [str(python_bin), "scripts/validate_cloudflare_research.py"],
            environment=environment,
            output_dir=output_dir,
        )
    )
    results.append(
        command_result(
            "django system check",
            [str(python_bin), "manage.py", "check"],
            environment=environment,
            output_dir=output_dir,
        )
    )
    results.append(
        command_result(
            "research smoke and failure-injection tests",
            [
                str(python_bin),
                "manage.py",
                "test",
                *RESEARCH_TEST_LABELS,
                "--verbosity",
                "0",
            ],
            environment=environment,
            output_dir=output_dir,
        )
    )
    results.append(
        command_result(
            "render promotion and rollback adapter rehearsal",
            [
                str(python_bin),
                "-m",
                "unittest",
                "scripts.tests.test_render_release",
                "-v",
            ],
            environment=environment,
            output_dir=output_dir,
        )
    )
    results.append(
        command_result(
            "release content gate",
            [str(python_bin), "manage.py", "check_release_content"],
            environment=environment,
            output_dir=output_dir,
            expected_returncode=1,
        )
    )
    content_log = (output_dir / "release_content_gate.log").read_text(encoding="utf-8")
    if not all(
        blocker in content_log
        for blocker in (
            "blocked-content-surface:homepage-development-media",
            "blocked-content-surface:pending-social-links",
        )
    ):
        results[-1]["status"] = "failed"
        results[-1]["failure"] = "unexpected release-content blocker output"

    results.append(
        command_result(
            "working tree whitespace check",
            ["git", "diff", "--check"],
            environment=environment,
            output_dir=output_dir,
        )
    )

    working_tree_clean = not bool(git_value("status", "--porcelain"))
    all_local_checks_passed = all(item["status"] == "passed" for item in results)
    stop_reasons = [
        "Private POC content intentionally leaves media and social URLs blocked.",
        "Render and Cloudflare staging resources, credentials, and live evidence are absent.",
        "PostgreSQL isolated restore and measured RTO/RPO evidence are absent.",
        "Owner launch acceptance has not been recorded.",
    ]
    manifest = {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "release_sha": git_value("rev-parse", "HEAD"),
        "working_tree_clean": working_tree_clean,
        "promotable": False,
        "deployment_mode": "research",
        "scope": "private development-team-only POC",
        "local_checks_passed": all_local_checks_passed,
        "checks": results,
        "synthetic_failure_coverage": {
            "database_readiness": "passed-by-test-injection",
            "email_delivery": "passed-by-provider-failure-test",
            "alert_delivery": "passed-by-structured-alert-test",
            "elevated_5xx": "runbook-defined; live monitor pending",
            "storage_scheduler": "runbook-defined; provider drill pending",
        },
        "external_gates": {
            "render_staging_smoke": "pending",
            "cloudflare_edge_and_origin_bypass": "pending",
            "postgresql_isolated_restore_rto_rpo": "pending",
            "prior_cloudflare_configuration_rollback": "pending",
            "owner_acceptance": "pending",
        },
        "launch_decision": "STOP",
        "stop_reasons": stop_reasons,
    }
    (output_dir / "release-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "owner-acceptance.json").write_text(
        json.dumps(
            {
                "status": "pending",
                "owner": "project owner",
                "required_evidence": [
                    "external staging smoke and alert evidence",
                    "isolated PostgreSQL restore with measured RTO/RPO",
                    "rollback rehearsal evidence",
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "launch-decision.json").write_text(
        json.dumps(
            {
                "decision": "STOP",
                "basis": "private POC and incomplete external launch gates",
                "manifest": "release-manifest.json",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Evidence bundle: {output_dir}")
    print(f"Local checks passed: {str(all_local_checks_passed).lower()}")
    print("Launch decision: STOP")
    return 0 if all_local_checks_passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Rehearsal stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from None
