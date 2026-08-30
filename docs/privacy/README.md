# TreadJoy Privacy, Retention, and Security Policy Package

**Policy ID:** `TJ-PRIV-001`
**Version:** `0.1-draft`
**Evidence date:** 2026-08-30
**Status:** Owner-accepted draft; privacy/legal, accounting/tax, technical, and
operational review pending. Not in force.

This directory is the version-controlled working package for `PROJECT_PLAN.md`
step A1.4. It records repository facts, proposed operating rules, review gates,
and downstream implementation responsibilities. It is not a public privacy
notice, legal advice, proof of regulatory compliance, or evidence that a
provider or control is live.

## Authority and status rules

- `docs/privacy/data-register.csv` is the authoritative inventory and retention
  matrix. Its stable `data_class_id` values are the interface that future
  models, services, notices, cleanup jobs, permissions, and tests must cite.
- Every duration in the register is an owner-accepted draft proposal, but it
  remains non-operative until the approval record shows the required scoped
  adviser and technical decisions. A draft duration must not trigger deletion
  or be represented to a customer as policy.
- `current` means the repository currently contains the behavior or storage.
  It does not mean that a public deployment or provider has been provisioned.
- `current-limited` means some code or data exists but the intended control is
  incomplete.
- `planned-not-active` means a roadmap capability, unselected provider, or
  future record. Inventorying it does not approve or activate it.
- Research and commerce data remain in separate PostgreSQL databases. Raw
  records must not move between modes. Approved anonymous aggregate findings
  may be reported only after re-identification risk is reviewed.

## Package contents

- [Operating policy](operating-policy.md): minimization, governance, access,
  retention, disposal, backup, provider, legal-hold, and review rules.
- [Data register](data-register.csv): field-level data classes and proposed
  lifecycle decisions.
- [Processor register](processor-register.md): current and candidate external
  services plus activation gates.
- [Data flows](data-flows.md): research and commerce trust boundaries.
- [Privacy-request runbook](privacy-request-runbook.md): intake through closure.
- [Security-incident annex](security-incident-annex.md): severity and response.
- [Validation record](validation-record.md): traceability, tabletop results,
  access review, backup review, and redaction-test inventory.
- [Approval record](approval-record.md): outstanding decisions, sign-offs,
  launch blockers, and downstream handoff.

## Source hierarchy and evidence boundary

This package follows the repository source-of-truth order in `AGENTS.md`.
Inventory was produced from current models, migrations, settings, views,
services, templates, admin registrations, management commands, tests, and
locally reproduced research-mode pages. No real database rows, secrets,
provider consoles, customer records, or local `.env` values were opened.

Primary references used to structure the draft:

- [NIST Privacy Framework](https://www.nist.gov/privacy-framework), a voluntary
  risk-management framework.
- [FTC Data Breach Response: A Guide for Business](https://www.ftc.gov/business-guidance/resources/data-breach-response-guide-business).
- [IRS record-retention guidance](https://www.irs.gov/businesses/small-businesses-self-employed/how-long-should-i-keep-records),
  which makes clear that the applicable period depends on the underlying
  record and event.
- [Django 5.2 session cleanup guidance](https://docs.djangoproject.com/en/5.2/topics/http/sessions/#clearing-the-session-store).

## Completion boundary

A1.4 must remain open until the approval record contains the required scoped
approvals, all launch-relevant retention rows are accepted or revised, and the
required table-tops pass. Live backup/restore, provider, monitoring, and access
tests remain launch gates in their downstream roadmap tasks.
