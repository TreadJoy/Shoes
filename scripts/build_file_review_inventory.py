#!/usr/bin/env python3
"""Build the Shoes project file-review inventory.

The inventory covers repository files and project-owned ignored material while
excluding dependency/build trees that can be recreated. Secret configuration
and local databases are recorded by path and size but are never read or hashed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs/file-review-inventory.tsv"
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".pnpm-store",
    ".ruff_cache",
    ".venv",
    ".wrangler",
    "__pycache__",
    "node_modules",
    "staticfiles",
}

CURRENT_REVIEW_PATHS = {
    ".editorconfig",
    "design/README.md",
    "docs/file-review.md",
    "docs/repository-file-standards.md",
    "pyproject.toml",
    "scripts/build_file_review_inventory.py",
    "scripts/check_repository_hygiene.py",
    "scripts/tests/test_build_file_review_inventory.py",
    "scripts/tests/test_repository_hygiene.py",
}


@dataclass(frozen=True)
class InventoryEntry:
    path: str
    source: str
    size_bytes: int
    sha256: str
    disposition: str
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Inventory destination (defaults to docs/file-review-inventory.tsv)",
    )
    return parser.parse_args()


def tracked_paths() -> set[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    )
    return {
        value.decode("utf-8", errors="surrogateescape")
        for value in completed.stdout.split(b"\0")
        if value
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sensitive_local_file(relative_path: str) -> bool:
    name = Path(relative_path).name
    is_private_environment = name == ".env" or (
        name.startswith(".env.") and name != ".env.example"
    )
    is_local_database = Path(relative_path).suffix.lower() in {
        ".db",
        ".sqlite",
        ".sqlite3",
    }
    return is_private_environment or is_local_database


def classification(relative_path: str, is_tracked: bool) -> tuple[str, str]:
    parts = Path(relative_path).parts
    name = parts[-1]

    if is_sensitive_local_file(relative_path):
        return "preserve", "private local state; contents deliberately not reviewed"
    if name == ".DS_Store" or name.endswith((".pyc", ".pyo")):
        return "delete", "reproducible operating-system or Python cache file"
    if relative_path.startswith("design/archive/treadjoy-modular-v1/"):
        return "archive", "superseded design generation; verify references before moving"
    if relative_path.startswith("design/archive/treadjoy-modular-v2/"):
        return "archive", "superseded design generation; verify references before moving"
    if relative_path.startswith("design/active/treadjoy-heritage-court-v3/"):
        return "review", "current design workspace candidate"
    if relative_path in CURRENT_REVIEW_PATHS or relative_path.startswith(
        "treadjoy/"
    ):
        return "review", "current reviewed project file"
    if relative_path == "media/development/treadjoy-ai-logo.png":
        return (
            "preserve",
            "development-only placeholder; unapproved for public deployment",
        )
    if parts and parts[0] == ".impeccable":
        return "investigate", "ignored project-tool state; confirm whether reproducible"
    if is_tracked:
        return "review", "tracked project file"
    return "investigate", "untracked or ignored project-local file"


def iter_project_files(output: Path) -> list[Path]:
    output = output.resolve()
    files: list[Path] = []
    for root, directories, filenames in os.walk(REPO_ROOT, followlinks=False):
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in EXCLUDED_DIRECTORY_NAMES
        )
        root_path = Path(root)
        for filename in sorted(filenames):
            path = root_path / filename
            if path.resolve() == output or path.is_symlink() or not path.is_file():
                continue
            files.append(path)
    return files


def build_inventory(output: Path) -> list[InventoryEntry]:
    tracked = tracked_paths()
    entries: list[InventoryEntry] = []
    for path in iter_project_files(output):
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        is_tracked = relative_path in tracked
        disposition, reason = classification(relative_path, is_tracked)
        digest = "not-read-sensitive" if is_sensitive_local_file(relative_path) else sha256(path)
        entries.append(
            InventoryEntry(
                path=relative_path,
                source="tracked" if is_tracked else "ignored-or-untracked",
                size_bytes=path.stat().st_size,
                sha256=digest,
                disposition=disposition,
                reason=reason,
            )
        )
    return sorted(entries, key=lambda entry: entry.path)


def write_inventory(output: Path, entries: list[InventoryEntry]) -> None:
    output = output.expanduser().resolve()
    try:
        output.relative_to(REPO_ROOT)
    except ValueError as error:
        raise SystemExit("--output must remain inside the Shoes repository") from error

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.writer(destination, delimiter="\t", lineterminator="\n")
        writer.writerow(
            ("path", "source", "size_bytes", "sha256", "disposition", "reason")
        )
        for entry in entries:
            writer.writerow(
                (
                    entry.path,
                    entry.source,
                    entry.size_bytes,
                    entry.sha256,
                    entry.disposition,
                    entry.reason,
                )
            )


def main() -> int:
    args = parse_args()
    entries = build_inventory(args.output)
    write_inventory(args.output, entries)
    total_bytes = sum(entry.size_bytes for entry in entries)
    print(f"Wrote {len(entries)} entries ({total_bytes} bytes) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
