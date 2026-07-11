# PR-018C - Dependency Synchronization Execution Review

Status: Docs-only dependency synchronization execution review.

Current checkpoint:

- v0.18.1-rcis-dependency-synchronization-plan
- 0289f86 docs: plan dependency synchronization

## Purpose

PR-018C reviews the exact dependency synchronization execution path before any
dependency installation or virtual environment mutation is allowed.

PR-018C does not install dependencies, run pip install, run uv sync, run
poetry install, or run pdm install. It does not change the active virtual
environment, modify pyproject.toml, modify lock files, modify production code,
or modify tests.

PR-018C does not parse PDFs, touch real RSV assets, create Evidence, Knowledge,
or Prompt Candidate artifacts, or authorize AI inference. Candidate commands
in this document are proposals only and are not executed by this review.

## Context

PR-018A and PR-018B established that:

- pyproject.toml declares pypdf
- the active `.venv` cannot import pypdf
- the import fails with `ModuleNotFoundError`
- no root lock, requirements, uv, Poetry, or PDM files were found
- the project uses setuptools with PEP 621 metadata
- deterministic unsupported_pdf fallback remains active
- successful parser execution is not currently enabled

## Environment Findings

The authorized checks reported:

- Active Python executable:
  `D:\PROJECT\RIE\.venv\Scripts\python.exe`
- pyproject.toml declares pypdf: yes
- pypdf import succeeded: no
- Import failure category: `ModuleNotFoundError`
- Import failure detail: `No module named 'pypdf'`
- Root dependency or lock files found: none
- Build backend: `setuptools.build_meta`
- Dependency declaration format: PEP 621 project dependencies

Dependency manager conclusion: the project metadata is compatible with a
pip/setuptools installation path, but the repository has no discovered lock
file or manager-specific workflow that defines one canonical synchronization
command. The active environment is not synchronized with the declared pypdf
dependency.

## Execution Boundary

- any dependency synchronization is an explicit environment operation
- synchronization may happen only after this review is approved and merged
- synchronization must not be mixed with production code changes
- synchronization must not be mixed with parser behavior changes
- synchronization must not be validated with real RSV assets
- synchronization must not create or update lock files unless explicitly
  approved
- synchronization must preserve repository state unless the approved command
  intentionally changes tracked dependency files
- command, network access, expected version behavior, verification, and
  rollback must be known before execution

## Candidate A: Install The Local Project In Editable Mode

Proposed command, not executed:

```text
python -m pip install -e .
```

Purpose:

- install the local project in editable mode using dependencies declared in
  pyproject.toml

Potential effect:

- may install pypdf and any other declared dependencies into `.venv`
- should not modify tracked files
- may depend on pip and setuptools behavior
- may access a package index or network when dependencies are missing

Risk: Medium, because the command installs the project and may install more
than the single missing parser dependency.

## Candidate B: Install The Already-Declared Missing Dependency

Proposed command, not executed:

```text
python -m pip install pypdf
```

Purpose:

- install only the already-declared missing dependency into the active
  `.venv`

Potential effect:

- repairs the local parser dependency gap
- changes `.venv` site-packages and installation metadata
- should not modify tracked files
- may access a package index or network
- does not establish lock reproducibility

Risk: Low to medium for a local environment repair, but weaker than a locked
and reproducible synchronization workflow.

## Candidate C: Recreate The Virtual Environment

Proposed operation, not executed:

- recreate `.venv`
- install the local project and its dependencies from pyproject.toml

Purpose:

- rebuild a clean local environment from declared project dependencies

Potential effect:

- changes the entire `.venv`
- may install all project and build dependencies
- may be slower and riskier than a targeted repair
- should not modify tracked files unless additional lock tooling is used
- may resolve different package versions because no lock file was found

Risk: Medium to high because the entire local environment is replaced.

## Candidate D: Defer Synchronization

Proposed operation:

- make no environment change and keep unsupported_pdf fallback active

Purpose:

- avoid environment mutation until dependency policy is stronger

Potential effect:

- no environment or repository change
- no successful parser execution
- current deterministic fallback behavior remains available

Risk: Low, but it blocks successful synthetic parser execution.

## Recommended Execution Path

Candidate B is the primary recommendation:

```text
python -m pip install pypdf
```

This is the smallest environment repair because pypdf is already declared,
the active issue is the missing package in `.venv`, and no lock file or
canonical manager workflow is present. It avoids production code changes and
should not modify tracked files.

The execution step must still be separately approved. It should use the
repository virtual environment interpreter explicitly, record the installed
version, acknowledge that an unpinned package may be selected, and verify that
the worktree remains unchanged.

## Post-Execution Verification Plan

After the synchronization command is separately approved and run, execute:

```text
.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
.venv\Scripts\python.exe -c "import pypdf; print(pypdf.__version__)"
.venv\Scripts\python.exe -m pytest --basetemp=.\.pytest_tmp_pr018_dependency_sync_verify
git status --short -uall
```

Then remove the verification basetemp:

```text
Remove-Item -Recurse -Force .\.pytest_tmp_pr018_dependency_sync_verify -ErrorAction SilentlyContinue
```

Expected success criteria:

- pypdf import succeeds
- the installed pypdf version is recorded
- the full test suite passes
- no tracked files change
- unsupported_pdf fallback remains available for missing-parser environments
- no real RSV assets are touched
- no Evidence, Knowledge, or Prompt artifacts are created

## Parser Execution Remains Out Of Scope

Even after dependency synchronization, PR-018C does not approve parser
execution changes. Controlled Synthetic PDF Parser Execution requires a later
approved PR.

Real RSV PDF processing remains forbidden until later explicit approval.

## Recommended Next PR

PR-018D - Dependency Synchronization Execution

PR-018D may execute only the separately approved local environment repair
command. It must not modify production code or tests, parse real PDFs, or touch
real RSV assets. It must report the pypdf import result and version, full test
result, cleanup result, and final git status.

## Review Acceptance

- Only this docs file is added.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed.
- No virtual environment mutation occurs.
- No PDF or real RSV asset is accessed.
- No commit is created by PR-018C preparation.
