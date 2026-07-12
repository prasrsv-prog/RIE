# PR-022I — Revised Phase 22 Regression Execution Review

## Status

PASSED — documentation-only revised execution review.

This review does not execute tests and does not create the parent or child temporary directory.

## Current checkpoint

- Branch: `phase-022-evidence-candidate-boundary-review`
- Local and remote Phase 22 HEAD: `2ae6b5a`
- Phase divergence: `0 0`
- Local main and origin/main: `3642955`
- Main divergence: `0 0`
- Repository before review: clean
- Index before review: clean
- Untracked files before review: none

## Purpose

This review defines the exact safe procedure for a new Phase 22 regression execution after PR-022G failed because the parent directory for the nested controlled basetemp was absent.

PR-022G remains immutable and officially NOT PASSED.

## PR-022H failure-review baseline

PR-022H concluded:

- PR-022G was execution-contract compliant.
- PR-022G result was `653 passed, 290 errors`.
- Exit code was `1`.
- Execution count was `1`.
- Retry count was `0`.
- No assertion failure was recorded.
- Primary classification was `regression environmental precondition defect`.
- Selected remediation direction was Option A.
- Immediate rerun was not authorized.

## Failed execution preservation

The following failed evidence must remain unchanged:

`D:\PROJECT\pr-022g-phase-22-regression-execution-output.txt`

PR-022G must not be amended, overwritten, renamed as passed, or reused as the identity for the revised execution.

## Parent-directory policy

Selected parent:

`D:\PROJECT\pytest-temp`

Future PR-022J must apply this exact policy:

1. If the path exists as a directory, preserve it and all unrelated children.
2. If the path is absent, create exactly this directory.
3. If the path exists but is not a directory, stop before pytest.
4. Do not delete the parent after execution.
5. Do not recursively clean the parent.
6. Do not use wildcard deletion.
7. Do not access, repair, or delete `.pytest_cache`.

Exact preparation logic:

```powershell
$ParentTemp = "D:\PROJECT\pytest-temp"
$ParentCreatedByExecution = $false

if (Test-Path -LiteralPath $ParentTemp) {
    if (-not (Test-Path -LiteralPath $ParentTemp -PathType Container)) {
        throw "STOP: parent temp path exists but is not a directory"
    }
}
else {
    New-Item -ItemType Directory -Path $ParentTemp | Out-Null
    $ParentCreatedByExecution = $true
}
```

The creation is environmental preparation only and does not modify the Git repository.

## New execution identity

Future execution gate:

**PR-022J — Revised Phase 22 Regression Execution**

New child basetemp:

`D:\PROJECT\pytest-temp\pr-022j`

New external output:

`D:\PROJECT\pr-022j-revised-phase-22-regression-execution-output.txt`

The child and output must both be absent before execution. If either already exists, PR-022J must stop without running pytest.

## Interpreter, working directory, and test target

- Interpreter: `D:\PROJECT\RIE\.venv\Scripts\python.exe`
- Working directory: `D:\PROJECT\RIE`
- `PYTHONPATH`: `src`
- Test target: `tests`

Global Python or another virtual environment is not authorized.

## Exact revised regression command

After successful parent preparation and all other preflight checks, PR-022J may execute exactly once:

```powershell
$env:PYTHONPATH = "src"
& "D:\PROJECT\RIE\.venv\Scripts\python.exe" -m pytest -q -p no:cacheprovider --basetemp "D:\PROJECT\pytest-temp\pr-022j" tests
```

No command argument may be added, removed, or changed.

The command must not include parallelism, retry, random ordering, fail-fast, coverage, warning suppression, collection-only, filters, parser-specific targets, or PDF-specific targets.

## Expected regression result

Accepted historical baseline:

- Phase 21 full regression: `898 passed`
- Phase 22 EvidenceCandidate focused collection: `45 tests`
- Expected total: `943`

Exact success result:

- Passed: `943`
- Failed: `0`
- Errors: `0`
- Skipped: `0`
- Xfailed: `0`
- Xpassed: `0`
- Warnings: `0`
- Process exit code: `0`
- Execution count: `1`
- Retry count: `0`

The baseline must not be revised during execution.

## Pre-execution stop conditions

PR-022J must stop without running pytest if:

- branch or checkpoint differs;
- phase or main divergence differs from `0 0`;
- repository has tracked, staged, or untracked files;
- interpreter, source, or test file is absent;
- Phase 21 branch or tag differs;
- controlled sandbox is non-empty;
- real or synthetic PDF target exists;
- parent path exists but is not a directory;
- new child `pr-022j` already exists;
- new external output already exists;
- exact command cannot be used.

No failed precondition may be repaired except the explicitly authorized creation of the absent parent directory.

## Execution and retry contract

- Full-regression execution count: exactly `1`
- Retry count: exactly `0`
- Automatic rerun: prohibited
- Manual immediate rerun: prohibited
- Command modification after failure: prohibited
- Source or test modification after failure: prohibited
- Dependency or configuration modification after failure: prohibited

Any failure must be captured and reported without rerun.

## Output capture contract

PR-022J must write complete evidence to:

`D:\PROJECT\pr-022j-revised-phase-22-regression-execution-output.txt`

The output must include:

- preflight checkpoint;
- parent existence before preparation;
- whether the parent was created;
- unrelated parent children before execution;
- child and output pre-existence;
- exact command;
- raw final pytest summary;
- exit code and all result counts;
- execution and retry counts;
- post-execution repository and sandbox state;
- child cleanup evidence;
- parent retention evidence;
- no-Evidence and no-Knowledge decisions;
- final revised execution decision.

## Child cleanup contract

After pytest exits and all result evidence is captured:

1. Inspect only `D:\PROJECT\pytest-temp\pr-022j`.
2. If it exists from this execution, remove only that exact child.
3. Use `-LiteralPath`.
4. Do not delete `D:\PROJECT\pytest-temp`.
5. Do not touch unrelated children.
6. Do not use wildcard or broad recursive cleanup.
7. Do not touch `.pytest_cache`.

Required final state:

- child cleanup attempted: `True` when the child exists;
- child cleanup successful: `True`;
- child exists afterward: `False`;
- parent exists afterward: `True`;
- unrelated parent children preserved: `True`.

Cleanup failure means the revised execution gate is not passed.

## Repository, sandbox, and authority boundary

Before and after execution:

- tracked changes: `0`;
- staged files: `0`;
- untracked files: `0`;
- source changes: `0`;
- test changes: `0`;
- dependency changes: `0`;
- configuration changes: `0`;
- controlled sandbox item count: `0`;
- real PDF target: absent;
- synthetic PDF target: absent.

PR-022J does not authorize:

- source or test modification;
- dependency or configuration modification;
- PDF access or processing;
- parser or ingestion workflows;
- Evidence or EvidenceRelationship creation;
- Knowledge, Product Knowledge, Official Knowledge, or Prompt Candidate creation;
- persistence;
- staging, commit, push, merge, tag, or release operations.

## Acceptance criteria

1. **SATISFIED** — Current branch is the approved Phase 22 branch.
2. **SATISFIED** — Local HEAD equals `2ae6b5a`.
3. **SATISFIED** — Remote HEAD equals `2ae6b5a`.
4. **SATISFIED** — Phase divergence is `0 0`.
5. **SATISFIED** — main and origin/main remain `3642955`.
6. **SATISFIED** — Repository is clean before PR-022I creation.
7. **SATISFIED** — PR-022H decision is recorded.
8. **SATISFIED** — PR-022G remains preserved as NOT PASSED.
9. **SATISFIED** — Failed PR-022G output remains present.
10. **SATISFIED** — Exact parent temp path is selected.
11. **SATISFIED** — Parent path may be created only when absent.
12. **SATISFIED** — An existing parent directory must be preserved.
13. **SATISFIED** — A non-directory object at the parent path causes a stop.
14. **SATISFIED** — Unrelated parent children must be preserved.
15. **SATISFIED** — Exact new child basetemp is selected.
16. **SATISFIED** — The new child differs from PR-022G.
17. **SATISFIED** — Pre-existing new child causes a stop.
18. **SATISFIED** — Exact new external output path is selected.
19. **SATISFIED** — The new output differs from PR-022G output.
20. **SATISFIED** — Existing new output causes a stop.
21. **SATISFIED** — Exact parent preparation command is defined.
22. **SATISFIED** — Exact regression command is defined.
23. **SATISFIED** — Exact interpreter is selected.
24. **SATISFIED** — Exact working directory is selected.
25. **SATISFIED** — Exact test target is `tests`.
26. **SATISFIED** — `PYTHONPATH` is explicitly `src`.
27. **SATISFIED** — Cache provider is disabled.
28. **SATISFIED** — Expected passed count is `943`.
29. **SATISFIED** — Expected failed count is zero.
30. **SATISFIED** — Expected error count is zero.
31. **SATISFIED** — Expected skipped count is zero.
32. **SATISFIED** — Expected warning count is zero.
33. **SATISFIED** — Expected exit code is zero.
34. **SATISFIED** — Execution count is exactly one.
35. **SATISFIED** — Retry count is zero.
36. **SATISFIED** — Automatic and manual immediate reruns are prohibited.
37. **SATISFIED** — Failure stop conditions are defined.
38. **SATISFIED** — Result and exit code capture requirements are defined.
39. **SATISFIED** — Exact child-only cleanup is defined.
40. **SATISFIED** — Parent-directory deletion is prohibited.
41. **SATISFIED** — Wildcard and recursive cleanup are prohibited.
42. **SATISFIED** — `.pytest_cache` access or modification is prohibited.
43. **SATISFIED** — Post-execution repository checks are defined.
44. **SATISFIED** — Post-execution sandbox and asset checks are defined.
45. **SATISFIED** — No source, test, dependency, or configuration modification is authorized.
46. **SATISFIED** — No PDF, parser, ingestion, Evidence, Knowledge, or persistence action is authorized.
47. **SATISFIED** — PR-022I executes no tests or interpreter.
48. **SATISFIED** — PR-022I creates no parent or child temp directory.
49. **SATISFIED** — Exactly one next execution gate is recommended.
50. **SATISFIED** — PR-022J authority is limited to the reviewed revised execution procedure.

## Revised execution review decision

**READY FOR REVISED PHASE 22 REGRESSION EXECUTION**

## Recommended PR-022J

**PR-022J — Revised Phase 22 Regression Execution**

PR-022J may perform only the exact parent preparation, one exact regression execution, external evidence capture, exact child cleanup, and post-state verification defined by this review.
