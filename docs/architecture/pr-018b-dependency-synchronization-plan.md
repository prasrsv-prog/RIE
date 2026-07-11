# PR-018B - Dependency Synchronization Plan

Status: Docs-only dependency synchronization plan.

Current checkpoint:

- v0.18.0-rcis-pdf-parser-environment-review
- 5e478df docs: review pdf parser environment

## Purpose

PR-018B plans a safe dependency synchronization step before successful PDF
parser execution is enabled.

PR-018B does not install dependencies, modify pyproject.toml, modify lock
files, modify production code, modify tests, or change the active virtual
environment. It does not parse PDFs, touch real RSV assets, create Evidence,
Knowledge, or Prompt Candidate artifacts, or authorize AI inference.

This is a plan only. No synchronization command is approved or executed by
this PR.

## Context

PR-018A found that pyproject.toml declares pypdf, but the active repository
virtual environment could not import it. The import failed with
ModuleNotFoundError. Deterministic unsupported_pdf fallback remains active,
and successful parser execution is not currently enabled.

## Environment Findings

The authorized checks reported:

- Active Python executable:
  `D:\PROJECT\RIE\.venv\Scripts\python.exe`
- pyproject.toml declares pypdf: yes
- pypdf import succeeded: no
- Import failure category: `ModuleNotFoundError`
- Import failure detail: `No module named 'pypdf'`
- Build backend: `setuptools.build_meta`
- Dependency declaration format: PEP 621 project dependencies
- Root lock files found: none
- Root requirements files found: none
- Root uv, Poetry, or PDM files found: none

The dependency state does not appear synchronized. The project declares
pypdf, but the active interpreter cannot import it. The repository also does
not currently expose a lock file or a tool-specific dependency workflow that
would identify one canonical synchronization command.

## Dependency Synchronization Boundary

- synchronization is a separate explicit operation
- dependency installation must not happen inside docs-only PRs
- dependency installation may happen only after explicit approval
- any synchronization must preserve the existing pyproject and lock policy
- production code must not be changed to force parser availability
- real asset tests must not validate dependency installation
- synchronization commands, expected file effects, and rollback must be
  reviewed before execution

No pip install, uv sync, poetry install, environment recreation, or equivalent
operation is performed by PR-018B.

## Safe Synchronization Options

### Option A: Use The Existing Project Dependency Manager

What it would do:

- use an established project command to synchronize the environment from
  declared and locked dependencies

Risk level: Low when a canonical manager and lock file already exist; otherwise
the risk is unclear.

Files it may affect:

- the virtual environment and dependency caches
- a lock file if the selected command resolves or updates dependencies

Lock-file effect: It may preserve, create, or modify a lock file depending on
the manager and command.

Suitability before parser execution: Preferred when an existing canonical
workflow is present. The current repository findings do not identify such a
workflow, so this option is not immediately actionable without a policy
decision.

### Option B: Recreate The Virtual Environment From Declared Dependencies

What it would do:

- replace the active virtual environment and install the dependencies declared
  by the project configuration

Risk level: Medium to high because it replaces the complete local environment
and may change versions beyond pypdf.

Files it may affect:

- the entire `.venv` directory
- dependency caches and generated environment metadata
- dependency files if a separate resolution or lock command is included

Lock-file effect: Environment recreation alone need not modify a lock file,
but an unlocked resolution can produce non-reproducible versions. A manager
may create or update a lock file if that is part of the chosen procedure.

Suitability before parser execution: Suitable only after the environment
recreation procedure, version policy, rollback, and full-suite verification
are explicitly approved.

### Option C: Install Only The Already-Declared pypdf Dependency

What it would do:

- repair the active local environment by installing only pypdf, which is
  already declared in pyproject.toml

Risk level: Medium. It is narrowly scoped but can still resolve transitive
dependencies or produce a developer-specific environment.

Files it may affect:

- `.venv` site-packages and installation metadata
- dependency caches
- normally no tracked project file when used as a local repair

Lock-file effect: A direct local install normally does not change a lock file,
but it also does not establish a reproducible locked environment.

Suitability before parser execution: Potentially suitable as an explicitly
approved local repair, but weaker than a documented reproducible
synchronization workflow.

### Option D: Defer Dependency Synchronization

What it would do:

- preserve the current environment and keep deterministic unsupported_pdf
  fallback behavior

Risk level: Low because it makes no environment or repository change.

Files it may affect: None.

Lock-file effect: None.

Suitability before parser execution: Safe for continued fallback testing, but
not suitable for enabling successful parser execution.

## Recommended Plan

Create a separate approved PR or task to synchronize the active virtual
environment without changing production code. Before any command runs, that
step should select the dependency-management procedure, state whether a lock
file will be introduced, record expected environment changes, define rollback,
and require post-synchronization verification.

Because the repository uses setuptools project metadata but has no discovered
lock or tool-specific dependency file, PR-018C - Dependency Synchronization
Execution Review is the recommended next PR. An execution review is safer than
immediately installing pypdf because it resolves the missing environment and
lock policy first.

## Testing Plan After Approved Synchronization

After synchronization is separately approved and performed, verify that:

- pypdf imports successfully from the repository virtual environment
- the installed pypdf version is recorded
- the existing full test suite still passes
- the PR-017L implementation reaches the parser path with synthetic input
- the PR-017M smoke flow remains bounded
- no real RSV assets are touched
- the final result still does not expose extracted_text
- evidence_allowed remains False

## Parser Execution Remains Out Of Scope

Successful parser execution is not enabled by PR-018B. Controlled Synthetic
PDF Parser Execution requires a later approved PR.

Real RSV PDF processing requires later approval, a confirmed sandbox copy
policy, explicit approved fixture selection, and PDF Evidence boundary review.

## Plan Acceptance

- Only this docs file is added.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed or changed.
- No PDF or real RSV asset is accessed.
- No commit is created by PR-018B preparation.
