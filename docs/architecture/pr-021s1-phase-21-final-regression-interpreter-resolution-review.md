# PR-021S1 - Phase 21 Final Regression Interpreter Resolution Review

## Status

Documentation-only amendment resolving the interpreter ambiguity discovered during PR-021T environment preflight.

PR-021S1 records the approved project interpreter and corrected exact regression command. It does not invoke Python, pytest, tests, parsers, or virtual-environment activation and does not authorize merge or tag operations.

## Current checkpoint

- Branch: `phase-021-controlled-pdf-post-extraction-review`
- HEAD: `dbe3c3c`
- Remote phase HEAD: `dbe3c3c`
- `main`: `fbb0c99`
- `origin/main`: `fbb0c99`
- Local/remote phase divergence: `0 0`
- Working tree before PR-021S1: clean
- Index before PR-021S1: clean
- Sandbox directory exists and is empty
- Real PDF target is absent
- Synthetic PDF target is absent

## Controlled failure outcome

- PR-021T stopped during environment preflight.
- Regression execution count remained `0`.
- Retry count remained `0`.
- No test result was produced.
- No regression command was executed.
- No dependency installation or environment modification occurred.
- The repository and sandbox remained clean.

The stopped preflight was an interpreter-resolution failure, not a Phase 21 test failure. Because no regression execution occurred, no pass count, failure count, or collection result was produced.

## Interpreter discovery

Verified project interpreter:

```text
D:\PROJECT\RIE\.venv\Scripts\python.exe
```

- Python version: `3.12.10`
- pytest version: `9.1.1`

The global interpreter that lacks pytest is:

```text
C:\Users\CHRIST\AppData\Local\Programs\Python\Python312\python.exe
```

The global interpreter failure was `No module named pytest`. No dependency was installed and no environment was changed in response.

## Interpreter authority

- `D:\PROJECT\RIE\.venv\Scripts\python.exe` is the only approved Phase 21 final-regression interpreter.
- No global Python may be used.
- No alternate interpreter fallback is allowed.
- No PATH-based interpreter resolution is allowed for the regression command.
- No virtual-environment activation command is required or authorized.
- No dependency installation or update is permitted.

The absolute interpreter path removes PATH ambiguity while preserving the existing approved project environment unchanged.

## Corrected exact regression command

Execution directory:

```text
D:\PROJECT\RIE
```

Exact PowerShell commands:

```powershell
$env:PYTHONPATH = "src"
& "D:\PROJECT\RIE\.venv\Scripts\python.exe" -m pytest -q -p no:cacheprovider
```

The absolute interpreter removes PATH ambiguity. No activation command is required. No dependency installation is permitted, and no global Python may be used.

The corrected test command may still be executed exactly once because the prior PR-021T regression execution count was `0`.

## Pre-execution assertions

Before regression execution, the resumed PR-021T must verify:

- The exact interpreter exists at `D:\PROJECT\RIE\.venv\Scripts\python.exe`.
- The interpreter path reported by `sys.executable` matches `D:\PROJECT\RIE\.venv\Scripts\python.exe` exactly.
- Python version is `3.12.10`.
- pytest version is `9.1.1`.
- The pytest version check exits with code `0`.
- The repository and sandbox checkpoint remains unchanged.
- Branch remains `phase-021-controlled-pdf-post-extraction-review`.
- Local and remote phase HEAD remain `dbe3c3c`.
- `main` and `origin/main` remain `fbb0c99`.
- Local/remote divergence remains `0 0`.
- No tracked, staged, or untracked file exists.
- Both PDF targets remain absent and the sandbox item count remains `0`.

Any failed assertion is a hard stop before regression execution.

## One-time execution decision

- PR-021T has not consumed its single regression execution.
- Environment and interpreter discovery are not regression executions.
- The corrected regression command may run exactly once.
- Regression execution count may advance from `0` to `1` only for that command.
- Retry count must remain `0` after the single run.
- No automatic rerun is authorized.
- A failed run does not authorize an interpreter switch, dependency change, or selective retest.

## Output boundary

The resumed PR-021T must use the replacement output path outside the repository:

```text
D:\PROJECT\pr-021t-phase-21-final-regression-retry-output.txt
```

No output file may be created inside `D:\PROJECT\RIE`. The output must preserve the interpreter assertions, exact corrected command, complete pytest output, process exit code, execution and retry counts, and final Git and sandbox verification.

## Recommended PR-021T

Resume:

**PR-021T - Phase 21 Final Regression Execution**

The resumed PR-021T must use only the exact `.venv` interpreter and corrected command recorded above. It may run that command once because the prior execution count was `0`. It must not install dependencies, switch interpreters, rerun automatically, modify repository files, merge, or tag.

No merge or tag is authorized by PR-021S1.

## Git boundary

- Only the PR-021S1 document may be introduced.
- No source, test, dependency, configuration, virtual-environment file, or prior document may change.
- No test or parser may be executed in PR-021S1.
- No PDF may be opened, created, copied, moved, staged, or committed.
- No staging, commit, push, merge, or tag is authorized.

The PR-021S1 document must remain untracked and unstaged during review.

## Acceptance criteria

- The current checkpoint remains branch `phase-021-controlled-pdf-post-extraction-review` at `dbe3c3c` locally and remotely.
- `main` and `origin/main` remain at `fbb0c99` with divergence `0 0`.
- The PR-021T controlled environment-preflight failure is distinguished from a test failure.
- Regression execution and retry counts remain `0`.
- The project and global interpreter paths are recorded exactly.
- Python `3.12.10` and pytest `9.1.1` are recorded.
- The project `.venv` interpreter is the sole approved regression interpreter.
- Global and alternate-interpreter fallback are prohibited.
- The corrected absolute-interpreter command is recorded exactly.
- The complete pre-execution interpreter assertions are recorded.
- The corrected regression remains eligible for exactly one execution.
- The replacement external output path is recorded.
- Merge and tag remain unauthorized.
- Only this PR-021S1 document is the intended repository change.
- The document remains untracked and unstaged.
- No test, parser, environment modification, dependency operation, or PDF operation occurs in PR-021S1.
