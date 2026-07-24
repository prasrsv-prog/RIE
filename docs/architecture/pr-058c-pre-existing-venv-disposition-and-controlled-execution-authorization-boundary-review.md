# PR-058C - Pre-existing Virtual Environment Disposition and Controlled Execution Authorization Boundary Review

## Status

PROPOSED

## Identity

- Phase: 57
- PR boundary: PR-058C
- Phase branch: `phase-057-operational-activation-readiness`
- Required branch commit: `f8aaff06e7ea56c38796aab77d5fed541c6c2883`
- Required commit parent: `53ae8b486da7dc8add93b07b648bbb30e359aced`
- Required commit subject: `docs: define Phase 57 installation and configuration contract`
- Main checkpoint: `eeb1e2108b4dada892f360edba1450ba01d25b92`

## Observed condition

A repository-local `D:\PROJECT\RIE\.venv` existed before Phase 57 fresh-environment execution.

The accepted PR-058B commit-publication correction report proves:

- the pre-existing `.venv` existed;
- Git ignored it;
- it was not executed;
- it was not used for commit or verification;
- it was not modified by the correction;
- no pip command was invoked;
- no dependency was installed;
- no RIE CLI or sample workflow was executed.

The pre-existing environment is local historical state. It is not Phase 57 acceptance evidence and must not be trusted as a fresh environment.

## Decision

Selected disposition:

`PRESERVE_PREEXISTING_REPOSITORY_VENV_AND_CREATE_SEPARATE_PHASE57_FRESH_VENV`

The pre-existing repository-local `.venv` must remain in place, ignored, unexecuted, and unmodified during Phase 57.

The controlled fresh Phase 57 environment path is changed to:

`D:\PROJECT\RIE-PHASE57-FRESH-VENV`

This is a narrow exception to the path selected in PR-058B. All other PR-058B installation and configuration controls remain authoritative.

## Rationale

This boundary avoids:

- deleting unreviewed local state;
- trusting a non-fresh environment;
- copying or renaming an environment;
- contaminating the repository working tree;
- changing `.gitignore` or local exclude rules;
- silently reusing installed packages;
- destructive recovery.

The fresh environment remains local to the operator computer but outside the Git working tree.

## Pre-existing `.venv` boundary

The existing `D:\PROJECT\RIE\.venv` is:

- preserved as local historical state;
- excluded from acceptance;
- prohibited from execution;
- prohibited from activation;
- prohibited from package inspection through its Python or pip executables;
- prohibited from modification;
- prohibited from deletion or rename by Phase 57 automation;
- prohibited from staging or commit;
- not considered a backup or rollback environment.

Read-only filesystem metadata may be recorded. Its package contents must not be treated as source of truth.

## Fresh environment boundary

A later execution authorization may create only:

`D:\PROJECT\RIE-PHASE57-FRESH-VENV`

Before creation, it must require:

- the path does not exist;
- the Phase 57 branch and commit are exact;
- the repository working tree is clean;
- nothing is staged;
- the pre-existing repository `.venv` still exists and remains ignored;
- no Python process from either environment is active;
- the selected system CPython satisfies Python 3.12 or later.

Creation must use the selected system interpreter and standard `venv`.

After creation, all Phase 57 Python and pip operations must use executables under the fresh external environment path.

## Dependency boundary

The only dependency installation input remains:

`D:\PROJECT\RIE\requirements-lock.txt`

The only authorized runtime package version remains:

`pypdf==6.14.2`

A later execution authorization must use:

`D:\PROJECT\RIE-PHASE57-FRESH-VENV\Scripts\python.exe -m pip`

It must not:

- use global pip;
- use the pre-existing repository `.venv`;
- upgrade pip unless separately authorized;
- install the RIE project;
- build a wheel;
- use editable installation;
- substitute another dependency version;
- retry automatically after failure.

## RIE execution boundary

The authorized future module entry point becomes:

`D:\PROJECT\RIE-PHASE57-FRESH-VENV\Scripts\python.exe -m rie`

The command must run from:

`D:\PROJECT\RIE`

This keeps source execution tied to the reviewed repository while isolating runtime dependencies in the fresh external environment.

## Configuration and sample boundary

A later execution authorization must still define a fresh controlled configuration and may use only:

- `samples/rie-core-v1/sample-source.pdf`;
- `samples/rie-core-v1/official-source-registry.json`;
- committed operator documentation;
- a separately authorized controlled output sandbox.

No real RSV PDF or asset is authorized.

## Cleanup and rollback boundary

PR-058C does not authorize environment creation or cleanup.

If future fresh environment creation fails:

- preserve the failed environment path;
- do not delete it automatically;
- do not retry automatically;
- do not fall back to the old repository `.venv`;
- preserve execution evidence;
- open a separate correction boundary.

The old repository `.venv` remains untouched regardless of later success or failure.

## Explicitly unauthorized now

PR-058C does not authorize or perform:

- execution of the pre-existing `.venv`;
- inspection through its Python or pip executables;
- deletion, rename, move, or modification of `.venv`;
- creation of `RIE-PHASE57-FRESH-VENV`;
- pip invocation;
- dependency installation;
- project installation;
- wheel build;
- CLI invocation;
- committed sample workflow execution;
- test-suite execution;
- real RSV asset selection or inspection;
- official-source registry mutation;
- pilot execution;
- source-code implementation;
- hosted-release mutation;
- tag mutation;
- reset, clean, amend, rebase, or force-push.

## PR-058C acceptance boundary

PR-058C is accepted only when:

- PR-058B commit publication correction-1 is independently accepted;
- local, origin, and live Phase 57 refs match commit `f8aaff06e7ea56c38796aab77d5fed541c6c2883`;
- main remains at the Phase 56 release commit;
- the repository working tree is clean before materialization;
- the pre-existing `.venv` exists and is ignored by Git;
- the fresh external environment path does not exist;
- this document is the only new working-tree path;
- nothing is staged;
- neither environment is executed or modified;
- no package, CLI, sample, test, asset, registry, release, or tag operation occurs;
- the report ends with exactly one `FINAL_RESULT=PASSED`.

## Next operation after independent acceptance

After PR-058C materialization acceptance:

1. manually stage only this document;
2. manually commit with:
   `docs: define Phase 57 pre-existing environment boundary`;
3. manually push the Phase 57 branch;
4. independently verify the commit publication;
5. prepare a separate execution authorization for exact interpreter discovery, fresh external environment creation, locked dependency installation, configuration materialization, and committed sample workflow execution.
