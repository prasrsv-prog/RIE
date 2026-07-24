# PR-058D - Controlled Fresh-Environment and Sample Workflow Execution Authorization Boundary Review

## Status

PROPOSED

## Identity

- Phase: 57
- PR boundary: PR-058D
- Phase branch: `phase-057-operational-activation-readiness`
- Required branch commit: `1fe7b4b65091139e418eba3200c32f7a2dcb46da`
- Required commit parent: `f8aaff06e7ea56c38796aab77d5fed541c6c2883`
- Required commit subject: `docs: define Phase 57 pre-existing environment boundary`
- Main checkpoint: `eeb1e2108b4dada892f360edba1450ba01d25b92`

## Purpose

PR-058D defines the exact future execution boundary for Phase 57 operational activation using only the committed synthetic Gate 11 sample.

PR-058D is an authorization review. It does not create an environment, install a package, write operator configuration, execute the CLI, run a sample workflow, or mutate governed artifacts.

## Accepted inputs

PR-058D depends on the independently accepted PR-058C commit publication.

The following committed inputs are authoritative:

- `pyproject.toml`;
- `requirements-lock.txt`;
- `docs/operator/installation-and-configuration.md`;
- `docs/operator/command-reference.md`;
- `docs/operator/sample-workflow.md`;
- `samples/rie-core-v1/official-source-registry.json`;
- `samples/rie-core-v1/sample-source.pdf`;
- `src/rie/__main__.py`;
- `src/rie/operator/operator_cli.py`.

## Environment disposition

The pre-existing repository environment remains:

`D:\PROJECT\RIE\.venv`

It must remain ignored, preserved, unexecuted, uninspected through Python or pip, and unmodified.

The only authorized future fresh environment path is:

`D:\PROJECT\RIE-PHASE57-FRESH-VENV`

The only authorized future execution root is:

`D:\PROJECT\RIE-PHASE57-CONTROLLED-EXECUTION`

Both paths must be absent before execution begins.

No future execution may delete, rename, move, copy, activate, inspect, or fall back to the pre-existing repository `.venv`.

## System interpreter boundary

A later execution step may use only the Windows Python launcher:

`py.exe -3`

Before environment creation, it must record:

- launcher resolution;
- `sys.executable`;
- Python implementation;
- full Python version;
- major and minor version;
- architecture.

The selected interpreter must be CPython 3.12 or later.

The selected system interpreter path must not be located under:

- `D:\PROJECT\RIE\.venv`;
- `D:\PROJECT\RIE-PHASE57-FRESH-VENV`;
- `D:\PROJECT\RIE-PHASE57-CONTROLLED-EXECUTION`.

If `py.exe -3` is missing or resolves below Python 3.12, execution must fail without trying another interpreter automatically.

## Fresh environment creation boundary

A later execution authorization may perform exactly one creation command:

`py.exe -3 -m venv D:\PROJECT\RIE-PHASE57-FRESH-VENV`

After creation, all Python and pip commands must use:

`D:\PROJECT\RIE-PHASE57-FRESH-VENV\Scripts\python.exe`

The execution must verify that:

- the fresh Python executable exists;
- its `sys.prefix` resolves inside the fresh environment;
- its `sys.base_prefix` differs from `sys.prefix`;
- it reports CPython 3.12 or later;
- it is not the pre-existing repository environment.

No activation script is required or authorized.

## Dependency installation boundary

The only authorized dependency input is:

`D:\PROJECT\RIE\requirements-lock.txt`

The required content is exactly:

`pypdf==6.14.2`

A later execution may invoke pip exactly once:

`D:\PROJECT\RIE-PHASE57-FRESH-VENV\Scripts\python.exe -m pip install --disable-pip-version-check --no-deps --only-binary=:all: --requirement D:\PROJECT\RIE\requirements-lock.txt`

The execution must not:

- upgrade pip;
- install the RIE project;
- use editable installation;
- build a wheel;
- install build requirements;
- install an unpinned pypdf version;
- invoke pip from another interpreter;
- retry automatically after failure.

After installation, the fresh interpreter must prove that imported `pypdf` reports version `6.14.2`.

The lock pins the runtime version but does not pin the distribution artifact hash. Phase 57 execution evidence must record this residual provenance limitation.

## Source-module execution boundary

The RIE project must not be installed into the fresh environment.

For each RIE command, the process-only environment must set:

`PYTHONPATH=D:\PROJECT\RIE\src`

The current directory must be:

`D:\PROJECT\RIE`

The authorized module entry point is:

`D:\PROJECT\RIE-PHASE57-FRESH-VENV\Scripts\python.exe -m rie`

The prior value of `PYTHONPATH` must be restored after execution.

## Controlled configuration

The future execution may create:

`D:\PROJECT\RIE-PHASE57-CONTROLLED-EXECUTION\operator-config.json`

The configuration must contain exactly:

```json
{
  "schema_version": "rie_operator_configuration_v1",
  "workspace_path": "D:\\PROJECT\\RIE-PHASE57-CONTROLLED-EXECUTION\\workspace",
  "audit_path": "D:\\PROJECT\\RIE-PHASE57-CONTROLLED-EXECUTION\\audit\\operator-audit.jsonl"
}
```

The configuration must be ASCII JSON with LF line endings, no BOM, and exactly one final LF.

## Controlled sample identity

The only authorized registry is:

`D:\PROJECT\RIE\samples\rie-core-v1\official-source-registry.json`

The only authorized source identifier is:

`RIE-SAMPLE-PDF-001`

The only authorized PDF is:

`D:\PROJECT\RIE\samples\rie-core-v1\sample-source.pdf`

The sample is synthetic controlled material. No real RSV PDF or asset is authorized.

## Controlled output paths

The execution may create only under:

`D:\PROJECT\RIE-PHASE57-CONTROLLED-EXECUTION`

Required artifact paths:

- `artifacts\01-pdf-ingestion.json`;
- `artifacts\02-evidence.json`;
- `artifacts\03-knowledge.json`;
- `artifacts\04-prompt-candidate.json`;
- `export\prompt-candidate.json`.

Required rendered result paths:

- `results\00-version.txt`;
- `results\01-registry-validate.json`;
- `results\02-source-inspect.json`;
- `results\03-ingest-pdf.json`;
- `results\04-evidence-build.json`;
- `results\05-evidence-inspect.json`;
- `results\06-knowledge-build.json`;
- `results\07-knowledge-inspect.json`;
- `results\08-prompt-candidate-build.json`;
- `results\09-audit-job.json`;
- `results\10-export.json`;
- `results\11-ingest-pdf-rerun.json`.

No output may be written inside the Git working tree.

## Authorized command sequence

Every non-version command must use:

- the fresh external Python executable;
- process-only `PYTHONPATH`;
- `--config D:\PROJECT\RIE-PHASE57-CONTROLLED-EXECUTION\operator-config.json`;
- `--format json`.

The exact sequence is:

1. `--version`
2. `registry validate`
3. `source inspect`
4. `ingest pdf`
5. `evidence build`
6. `evidence inspect`
7. `knowledge build`
8. `knowledge inspect`
9. `prompt-candidate build`
10. `audit job`
11. `export`
12. repeat the exact `ingest pdf` command and output path.

The audit command must inspect the `audit_id` emitted by the Prompt Candidate build result.

## Expected execution semantics

The first ten governed commands after version must return exit code `0`.

Expected initial statuses:

- registry validation: `SUCCEEDED`;
- source inspection: `SUCCEEDED`;
- PDF ingestion: `SUCCEEDED`;
- Evidence build: `SUCCEEDED`;
- Evidence inspection: `SUCCEEDED`;
- Knowledge build: `SUCCEEDED`;
- Knowledge inspection: `SUCCEEDED`;
- Prompt Candidate build: `SUCCEEDED`;
- audit inspection: `SUCCEEDED`;
- export: `SUCCEEDED`.

The repeated PDF ingestion must return:

`REUSED_EXISTING`

The rerun must use the exact same registry, source identifier, configuration, and output path.

The PDF ingestion artifact digest and byte count must remain unchanged across the rerun.

The exported Prompt Candidate bytes and SHA-256 must exactly match the Prompt Candidate artifact.

Every non-dry-run command must report persisted audit evidence.

## Repository invariants

Before and after future execution:

- active branch must remain `phase-057-operational-activation-readiness`;
- local, origin, and live Phase 57 refs must remain on the accepted authorization commit;
- main must remain unchanged;
- the working tree must remain clean;
- nothing may be staged;
- no source or documentation file may be modified;
- the Phase 56 tag must remain unchanged.

## Failure boundary

If any preflight, environment creation, installation, configuration, command, audit, export, rerun, digest, or repository check fails:

- preserve the fresh environment;
- preserve the controlled execution root;
- preserve all result and audit evidence already written;
- do not delete or overwrite evidence;
- do not retry automatically;
- do not fall back to the old repository `.venv`;
- do not reset or clean the repository;
- report exactly where execution stopped;
- open a separate correction boundary.

## Explicitly unauthorized by PR-058D materialization

PR-058D materialization does not perform or authorize immediately:

- execution of either environment;
- fresh environment creation;
- pip invocation;
- dependency installation;
- project installation;
- wheel build;
- configuration materialization;
- CLI execution;
- sample workflow execution;
- test-suite execution;
- real RSV asset selection or inspection;
- official-source registry mutation;
- source-code modification;
- hosted-release mutation;
- tag mutation;
- reset, clean, amend, rebase, or force-push.

Future execution becomes eligible only after this authorization document is independently accepted, committed, pushed, and independently verified.

## PR-058D acceptance boundary

PR-058D materialization is accepted only when:

- PR-058C commit publication is independently accepted;
- the repository and remote refs match commit `1fe7b4b65091139e418eba3200c32f7a2dcb46da`;
- main remains unchanged;
- the repository is clean before materialization;
- the pre-existing `.venv` remains ignored and unmodified;
- the fresh environment and controlled execution root do not exist;
- committed source inputs match the reviewed contracts;
- this document is the only new working-tree path;
- nothing is staged;
- no environment, pip, package, CLI, sample, test, real asset, registry, release, or tag operation occurs;
- the report ends with exactly one `FINAL_RESULT=PASSED`.

## Next operation after independent acceptance

After PR-058D materialization acceptance:

1. manually stage only this document;
2. manually commit with:
   `docs: authorize Phase 57 controlled sample execution`;
3. manually push the Phase 57 branch;
4. independently verify the commit publication;
5. prepare a separate execution launcher that implements this boundary exactly.
