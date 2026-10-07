# Repository File Standards

## Purpose

These conventions keep Shoes project files understandable, portable, and easy
to locate. They apply prospectively: existing nonconforming names are corrected
only in their approved review phase after references and compatibility risks are
checked.

## Naming

- Use descriptive English names; avoid unexplained abbreviations and generic
  names such as `misc`, `new`, `final-final`, or `stuff`.
- Use `snake_case` for Python modules, packages, tests, and Python scripts.
- Use `kebab-case` for ordinary documentation, asset directories, and static
  asset filenames.
- Use ISO `YYYY-MM-DD` dates when a date belongs in a filename.
- Use `vNN` for intentional design generations. Do not use versions in code
  filenames when source control already provides the history.
- Do not use spaces, control characters, backslashes, or leading/trailing
  whitespace in machine-used paths.
- Preserve ecosystem and repository conventions including `README.md`,
  `AGENTS.md`, `PROJECT_PLAN.md`, `MISTAKES.md`, Django migration filenames,
  `manage.py`, and dotfiles.

Names should communicate the artifact's subject and role. A rename is complete
only after imports, references, deployment configuration, documentation, and
tests are updated together.

## Locations

- Django domain behavior belongs in the owning `web/<domain>/` application.
- Shared project configuration belongs in the Django project package.
- Shared templates belong under `templates/`; reusable template fragments
  belong under `templates/partials/`.
- Browser-delivered source belongs under `static/`; generated static output does
  not belong in Git.
- Reusable operational tooling belongs under `scripts/` and its tests under
  `scripts/tests/`.
- Durable project documentation belongs under `docs/`; privacy records and ADRs
  retain their existing focused subdirectories.
- Runtime uploads and development-only website media belong under ignored
  `media/`. Private product-design sources belong under `design/active/` while
  superseded design generations belong under `design/archive/`; both bulky
  trees are ignored and governed by the tracked `design/README.md`.
- Dependencies, caches, local databases, secrets, and provider state remain
  ignored and reproducible or privately managed.

## Text and Formatting

- Text files use UTF-8, LF line endings, a final newline, and no trailing
  whitespace.
- Python uses four-space indentation and the Python 3.12 language target.
- Web, data, documentation, and configuration formats use two-space indentation
  unless their format requires otherwise.
- Ruff initially enforces correctness-focused `E4`, `E7`, `E9`, and `F` rules.
  Broader style rules require an evidence-based proposal to avoid noisy churn.

## Enforcement

Run the focused safeguards with:

```sh
.venv/bin/python scripts/check_repository_hygiene.py
.venv/bin/python -m ruff check manage.py treadjoy web scripts
.venv/bin/python -m unittest \
  scripts.tests.test_repository_hygiene \
  scripts.tests.test_build_file_review_inventory
```

Pre-commit runs the hygiene and Ruff checks alongside secret scanning. CI runs
the same checks from the hash-locked development environment. These checks do
not rewrite files; corrections remain explicit, reviewable changes.
