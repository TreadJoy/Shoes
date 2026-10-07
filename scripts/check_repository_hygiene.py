#!/usr/bin/env python3
"""Check tracked project files for portable names and text hygiene."""

from __future__ import annotations

import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DIRECTORY_NAMES = {
    ".pnpm-store",
    ".ruff_cache",
    ".venv",
    ".wrangler",
    "__pycache__",
    "node_modules",
    "staticfiles",
}
FORBIDDEN_FILE_NAMES = {".DS_Store", ".env"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}


@dataclass(frozen=True)
class HygieneIssue:
    path: str
    message: str


def reviewable_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    )
    return sorted(
        value.decode("utf-8", errors="surrogateescape")
        for value in completed.stdout.split(b"\0")
        if value
    )


def path_issues(relative_path: str) -> list[HygieneIssue]:
    path = PurePosixPath(relative_path)
    issues: list[HygieneIssue] = []

    for component in path.parts:
        if component != component.strip():
            issues.append(HygieneIssue(relative_path, "path component has outer whitespace"))
        if any(unicodedata.category(character).startswith("C") for character in component):
            issues.append(HygieneIssue(relative_path, "path contains a control character"))

    if any(component in FORBIDDEN_DIRECTORY_NAMES for component in path.parts[:-1]):
        issues.append(HygieneIssue(relative_path, "generated directory must not be tracked"))
    if path.name in FORBIDDEN_FILE_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
        issues.append(HygieneIssue(relative_path, "generated or private file must not be tracked"))
    if "\\" in relative_path:
        issues.append(HygieneIssue(relative_path, "path contains a non-portable backslash"))
    return issues


def text_issues(relative_path: str, content: bytes) -> list[HygieneIssue]:
    if not content or b"\0" in content:
        return []
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        return []

    issues: list[HygieneIssue] = []
    if b"\r\n" in content:
        issues.append(HygieneIssue(relative_path, "text file uses CRLF line endings"))
    if not content.endswith(b"\n"):
        issues.append(HygieneIssue(relative_path, "non-empty text file lacks a final newline"))
    for line_number, line in enumerate(content.splitlines(keepends=True), start=1):
        body = line.rstrip(b"\r\n")
        if body.endswith((b" ", b"\t")):
            issues.append(
                HygieneIssue(relative_path, f"line {line_number} has trailing whitespace")
            )
    return issues


def check_repository() -> list[HygieneIssue]:
    issues: list[HygieneIssue] = []
    for relative_path in reviewable_paths():
        issues.extend(path_issues(relative_path))
        path = REPO_ROOT / relative_path
        if path.is_file() and not path.is_symlink():
            issues.extend(text_issues(relative_path, path.read_bytes()))
    return issues


def main() -> int:
    issues = check_repository()
    if issues:
        for issue in issues:
            print(f"{issue.path}: {issue.message}")
        print(f"repository hygiene failed with {len(issues)} issue(s)")
        return 1
    print("repository hygiene passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
