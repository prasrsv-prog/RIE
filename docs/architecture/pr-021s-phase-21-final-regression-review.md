# PR-021S - Phase 21 Final Regression Review

## Status

Documentation-only review of the proposed Phase 21 final regression.

PR-021S defines the exact command, preflight, execution boundary, output capture, pass/fail conditions, and post-regression verification. It does not execute regression, tests, parsers, or ingestion code and does not authorize merge or tag operations.

## Current checkpoint

- Branch: `phase-021-controlled-pdf-post-extraction-review`
- HEAD: `d8c849b`
- Remote phase HEAD: `d8c849b`
- `main`: `fbb0c99`
- `origin/main`: `fbb0c99`
- Local/remote phase divergence: `0 0`
- Working tree before PR-021S: clean
- Index before PR-021S: clean
- Sandbox directory exists and is empty
- Real PDF target is absent
- Synthetic PDF target is absent

## Prior closure decision

PR-021R determined:

**READY FOR FINAL REGRESSION REVIEW**

PR-021R recorded all `19` Phase 21 closure criteria as satisfied. Final regression has not yet been executed. Merge has not been authorized, and tag creation has not been authorized.

## Purpose

PR-021S defines and reviews:

- the exact Phase 21 final regression command
- the required checkpoint before execution
- the required complete test scope
- output capture outside the repository
- acceptable warnings
- pass and fail conditions
- post-regression repository verification
- the prohibition on merge and tag during regression

PR-021S itself does not execute regression.

## Final regression scope

The final regression must run the complete repository test suite from:

```text
D:\PROJECT\RIE
```

The exact approved PowerShell command is:

```powershell
$env:PYTHONPATH = "src"
python -m pytest -q -p no:cacheprovider
```

Execution requirements:

- The active Python environment must be the existing approved project environment.
- No dependency installation or update is permitted.
- No test selection, deselection, filtering, xfail change, or marker exclusion is permitted.
- No parallel execution is permitted unless it is already the repository default.
- No coverage configuration change is permitted.
- No source or test modification is permitted before or during regression.
- The exact command may be executed only in the separately authorized PR-021T execution step.

## Cache boundary

- The pytest cache provider is explicitly disabled with `-p no:cacheprovider`.
- This reduces interaction with the known inaccessible `.pytest_cache` directory.
- The historical `.pytest_cache Permission denied` warning is acceptable only if emitted during read-only Git status operations.
- A permission warning must not hide or excuse a test failure.
- No deletion, permission change, ownership change, recursive operation, or manual repair of `.pytest_cache` is authorized.

## Output capture

The complete PR-021T final regression output must be saved outside the repository at:

```text
D:\PROJECT\pr-021t-phase-21-final-regression-output.txt
```

The output must contain:

- repository checkpoint
- exact regression command
- Python executable path
- Python version
- pytest version
- start and completion markers
- complete pytest summary
- process exit code
- elapsed time, if available
- final repository verification
- final sandbox state

No regression output file may be created inside `D:\PROJECT\RIE`.

## Pre-regression checkpoint

Before running tests, PR-021T must verify:

- Repository root: `D:\PROJECT\RIE`
- Branch: `phase-021-controlled-pdf-post-extraction-review`
- HEAD: `d8c849b`
- Remote phase HEAD: `d8c849b`
- `main`: `fbb0c99`
- `origin/main`: `fbb0c99`
- Local/remote phase divergence: `0 0`
- No tracked changes
- No staged files
- No untracked files
- Sandbox directory exists
- Sandbox item count: `0`
- Real PDF target is absent
- Synthetic PDF target is absent

Required source files must exist:

- `src/rie/ingestion/controlled_pdf_structural_metadata_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py`

Required Phase 21 tests must exist:

- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py`

PR-021T must stop before test execution if any pre-regression check fails.

## Execution boundary

PR-021T may:

- run the exact approved full-suite command once
- capture complete terminal output outside the repository
- record the process exit code and pytest summary
- perform read-only Git and sandbox verification afterward

PR-021T must not:

- edit source or tests
- rerun automatically after failure
- run only a subset as a replacement
- install dependencies
- update lock files
- clear caches
- open or create PDF fixtures manually
- execute prior synthetic or real-asset parser workflows
- stage, commit, push, merge, or tag

## One-time regression boundary

- The final regression command may be executed exactly once.
- Retry count must remain `0`.
- Failure does not authorize source modification.
- Failure does not authorize dependency changes.
- Failure does not authorize selective retesting.
- Any remediation requires a separate reviewed PR.

## Pass condition

Final regression passes only if:

- pytest process exit code equals `0`
- no failed tests
- no error tests
- no interrupted test session
- no unexpected collection error
- no repository file changed
- no repository output file was created
- no PDF appeared in the sandbox
- Git state remains clean
- sandbox remains empty

The last recorded full suite at PR-021J was `898 passed`. This count is historical context only. The final pass count may be equal or higher if documentation or legitimate committed tests changed. A lower count requires explicit explanation. Exit code `0` remains mandatory. Warnings alone do not constitute failure unless they indicate a boundary violation.

## Fail condition

Final regression fails if any of the following occurs:

- non-zero process exit code
- failed or error tests
- collection error
- interrupted execution
- missing required test files
- unexpected repository modification
- unexpected untracked file
- PDF created or left in the sandbox
- dependency or environment modification
- incomplete output capture
- retry performed without review

A failed regression does not authorize remediation, rerun, or selective testing in PR-021T.

## Post-regression verification

After test execution, PR-021T must verify:

- Branch remains `phase-021-controlled-pdf-post-extraction-review`.
- HEAD remains `d8c849b`.
- Remote phase HEAD remains `d8c849b`.
- `main` and `origin/main` remain `fbb0c99`.
- Local/remote phase divergence remains `0 0`.
- No tracked changes exist.
- No staged files exist.
- No untracked files exist.
- Real PDF target remains absent.
- Synthetic PDF target remains absent.
- Sandbox directory still exists.
- Sandbox item count remains `0`.
- No commit or push occurred.

## Regression result classification

PR-021T must end with exactly one result marker:

```text
=== PR-021T PHASE 21 FINAL REGRESSION PASSED ===
```

or:

```text
=== PR-021T PHASE 21 FINAL REGRESSION FAILED ===
```

A passed result does not authorize merge or tag operations.

## Recommended PR-021T

The recommended next execution step is:

**PR-021T - Phase 21 Final Regression Execution**

PR-021T is authorized only after PR-021S is separately approved, committed, and synchronized at a new explicit checkpoint. It may execute the exact full-suite command once and perform read-only post-regression verification. It must make no repository changes and must not merge or tag.

## Recommended PR-021U

If PR-021T passes, recommend:

**PR-021U - Phase 21 Final Regression Result and Closure Review**

PR-021U must remain documentation-only and decide:

- whether regression output is acceptable
- whether Phase 21 closure criteria remain satisfied
- whether the phase branch is ready for controlled merge review
- whether temporary assets remain absent
- whether Evidence and Knowledge boundaries remain intact

If regression fails, PR-021U must not be created as a successful closure record. A separate remediation review is required.

## Merge and tag boundary

- PR-021S does not authorize test execution.
- PR-021T may authorize only the exact regression execution.
- Neither PR-021S nor PR-021T authorizes merge.
- Neither PR-021S nor PR-021T authorizes tag creation.
- No push to `main` is allowed.
- No Phase 21 tag may be created before post-merge verification.

## Git boundary

- Only the PR-021S document may be introduced.
- No source, test, dependency, configuration, virtual-environment file, or prior document may change.
- No PDF may be opened, copied, staged, or committed.
- No test or parser may be executed in PR-021S.
- No merge or tag is authorized.

The PR-021S document must remain untracked and unstaged during review. PR-021S does not authorize commit, push, merge, or tag operations.

## Acceptance criteria

- The current checkpoint remains branch `phase-021-controlled-pdf-post-extraction-review` at `d8c849b` locally and remotely.
- `main` and `origin/main` remain at `fbb0c99`.
- Local/remote phase divergence remains `0 0`.
- PR-021R's `READY FOR FINAL REGRESSION REVIEW` decision is recorded.
- The exact full-suite command and execution directory are recorded.
- The existing approved environment and dependency boundary are explicit.
- The cache-provider and acceptable-warning boundary are explicit.
- The external output path and required output contents are recorded.
- The complete pre-regression checkpoint and required files are recorded.
- Execution is restricted to one exact command invocation with zero retries.
- Pass and fail conditions are complete and explicit.
- Post-regression Git and sandbox verification is required.
- Both permitted PR-021T result markers are recorded exactly.
- PR-021T remains a separately authorized execution step.
- PR-021U depends on a passing regression result.
- Merge, tag, and `main` push remain unauthorized.
- Only this PR-021S document is the intended repository change.
- The document remains untracked and unstaged.
- No test, parser, or PDF operation occurs in PR-021S.
