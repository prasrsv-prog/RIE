# PR-056C - Gate 11 CLI, Audit, Packaging, and Release Implementation Boundary Review

## Status

Gate 11 implementation-boundary review.

## Review outcome

Selected implementation boundary:

`twenty_eight_path_isolated_operator_console_audit_recovery_packaging_documentation_sample_and_fresh_environment_acceptance_implementation_boundary`

This boundary contains exactly 28 paths:

- 3 existing integration paths that may be modified;
- 8 new operator production paths;
- 1 new controlled dependency-lock path;
- 5 new operator documentation paths;
- 3 new controlled sample paths;
- 8 new test and acceptance paths.

PR-056C does not modify production, test, packaging, documentation, sample, or
acceptance paths. It does not run tests, install the package, create a PDF,
authorize release publication, or close Gate 11.

## Starting checkpoint

- Phase 56 branch:
  `phase-056-end-to-end-cli-audit-packaging-release`
- PR-056B commit:
  `1a2df93f6a6c1139a10020763837e67d8c5f4b4a`
- PR-056B parent:
  `26aef31f7c26890552b5f28f4b5356b30f58c262`
- Published `main`:
  `b348506541584d3b420a59af167a957834744801`
- Gate 11 minimum closure boundary is operationally committed.
- Gate 11 operator workflow contract is operationally committed.
- Gate 11 implementation has not started.

## Current-state findings

The accepted PR-056B review established:

- `src/rie/__main__.py` exists as the only detected CLI entry-module path;
- `pyproject.toml` has no `[project.scripts]` section;
- no installed `rie` console entry is declared;
- no controlled dependency-lock path is present;
- no audit-specific operational path is present;
- no recovery-specific operational path is present;
- no controlled sample or example path is present;
- package version and supported Python requirement already exist.

These findings define an integration gap. They do not authorize replacement of
the frozen Gates 2-10 domain implementations.

## Boundary rule

Gate 11 must be implemented as an operator layer around the frozen Gates 2-10
public contracts.

The implementation must not duplicate or rewrite:

- official-source registry validation;
- source inspection and eligibility;
- ingestion-job construction;
- extraction;
- Evidence construction or repositories;
- Knowledge construction, lifecycle, or repositories;
- exact-revision lookup;
- Prompt Candidate construction.

The operator layer may validate CLI arguments, load explicit configuration,
route commands, map domain issues to process results, coordinate the accepted
workflow, persist audit records, emit outputs, and provide deterministic
recovery guidance.

## Exact implementation paths

- `README.md`
- `pyproject.toml`
- `src/rie/__main__.py`
- `requirements-lock.txt`
- `src/rie/operator/__init__.py`
- `src/rie/operator/operator_audit.py`
- `src/rie/operator/operator_cli.py`
- `src/rie/operator/operator_configuration.py`
- `src/rie/operator/operator_contract.py`
- `src/rie/operator/operator_recovery.py`
- `src/rie/operator/operator_result.py`
- `src/rie/operator/operator_service.py`
- `docs/operator/installation-and-configuration.md`
- `docs/operator/command-reference.md`
- `docs/operator/audit-and-recovery.md`
- `docs/operator/sample-workflow.md`
- `docs/operator/fresh-environment-acceptance.md`
- `samples/rie-core-v1/README.md`
- `samples/rie-core-v1/official-source-registry.json`
- `samples/rie-core-v1/sample-source.pdf`
- `tests/operator/test_operator_audit.py`
- `tests/operator/test_operator_cli.py`
- `tests/operator/test_operator_contract.py`
- `tests/operator/test_operator_public_api.py`
- `tests/operator/test_operator_recovery.py`
- `tests/operator/test_operator_result.py`
- `tests/operator/test_operator_service.py`
- `tests/acceptance/test_rie_core_v1_fresh_environment.py`

No other production, test, packaging, documentation, sample, or acceptance path
is authorized by this boundary.

## Existing integration paths

### `pyproject.toml`

Authorized changes are limited to:

- one `[project.scripts]` declaration;
- exactly one installed console command named `rie`;
- dependency and package metadata changes required by the selected operator
  layer;
- controlled inclusion of documentation and sample assets where packaging
  requires it.

The console entry must resolve to:

`rie.operator.operator_cli:main`

No second console command, plugin entry point, or provider-specific entry point
is authorized.

### `src/rie/__main__.py`

This module must delegate to the same `main` callable used by the installed
console command.

It must not contain a second parser, a second command grammar, or independent
domain workflow logic.

`python -m rie` and the installed `rie` command must therefore share one
operator contract.

### `README.md`

README changes are limited to a concise RIE Core v1 operator entry point,
installation reference, command reference, sample-workflow reference, and
fresh-environment acceptance reference.

Detailed contracts remain in the selected operator documentation paths.

## Operator production paths

### `src/rie/operator/__init__.py`

Exports only the frozen public operator symbols selected by implementation.

### `src/rie/operator/operator_contract.py`

Defines:

- command names and normalized request contracts;
- stable statuses;
- stable process exit codes `0` through `8`;
- shared result-field names;
- audit and recovery contracts;
- public immutable value objects.

It must contain no repository, filesystem, environment, or subprocess access.

### `src/rie/operator/operator_result.py`

Constructs deterministic human and canonical JSON representations from one
logical operator result.

Human and JSON outputs must preserve equivalent status, issue, identifier,
provenance, audit, output, and recovery semantics.

### `src/rie/operator/operator_configuration.py`

Loads only explicit operator configuration.

It must:

- fail closed on missing or invalid configuration;
- expose a deterministic configuration identity and digest;
- exclude secrets from output and audit records;
- avoid hidden source discovery and hidden defaults that select governed
  identities.

### `src/rie/operator/operator_audit.py`

Defines and persists one logical audit record for each non-help invocation,
including rejection and failure.

Audit identity must be deterministic from normalized governed inputs and
contract versions. Observational timestamps may be recorded separately but
must not alter canonical operation identity.

Audit persistence must be fail closed and must not silently drop a failed or
rejected invocation.

### `src/rie/operator/operator_recovery.py`

Maps deterministic failures and partial-state markers to one explicit,
repeatable recovery instruction.

It must never recommend blind deletion, manual persisted-artifact editing,
history reset, force push, hidden replacement, or contract bypass.

### `src/rie/operator/operator_service.py`

Coordinates validation-before-mutation across the ten required commands and
the frozen Gates 2-10 public contracts.

It owns:

- command routing;
- dry-run planning;
- mutation ordering;
- safe-rerun and reuse decisions;
- result and exit-code mapping;
- audit coordination;
- export coordination;
- recovery-state reporting.

It must not reimplement domain behavior already owned by Gates 2-10.

### `src/rie/operator/operator_cli.py`

Defines the only parser and installed `main` callable.

It must provide:

- `rie --help`;
- `rie --version`;
- the ten required subcommands;
- `--format human|json`;
- `--output` where relevant;
- `--dry-run` where relevant;
- deterministic process exit behavior;
- no automatic retry.

Parser construction and process termination must remain testable without
starting subprocesses.

## Dependency-lock boundary

### `requirements-lock.txt`

This path records the exact accepted direct and transitive dependency versions
needed to install and execute RIE Core v1 in the supported Python environment.

It must be generated from the accepted package dependency set and must not
silently include unrelated development tools.

The later implementation report must record its exact generation command,
digest, byte format, and compatibility with fresh-environment installation.

## Documentation boundary

### `docs/operator/installation-and-configuration.md`

Covers supported Python, installation, package verification, explicit
configuration, configuration identity, and secret handling.

### `docs/operator/command-reference.md`

Covers the complete grammar, required arguments, output formats, statuses,
exit codes, issue codes, dry-run behavior, and command examples.

### `docs/operator/audit-and-recovery.md`

Covers audit interpretation, rejection and failure visibility, partial-state
markers, repeatable recovery, and prohibited unsafe recovery actions.

### `docs/operator/sample-workflow.md`

Covers the exact sample registry, sample PDF, end-to-end command sequence,
expected Prompt Candidate export, audit inspection, and safe rerun.

### `docs/operator/fresh-environment-acceptance.md`

Defines the controlled environment setup, package installation, command
availability, sample execution, human/JSON equivalence, audit linkage,
idempotent rerun, deterministic rejection, recovery, and release-target checks.

## Controlled sample boundary

### `samples/rie-core-v1/official-source-registry.json`

Contains only synthetic controlled sample data and one exact registered PDF
source.

It must not contain production RSV data, credentials, personal data, or an
uncontrolled external dependency.

### `samples/rie-core-v1/sample-source.pdf`

Contains a small synthetic text-only PDF suitable for deterministic extraction
and complete end-to-end acceptance.

Its source content, generator procedure, checksum, byte count, and licensing
status must be documented.

### `samples/rie-core-v1/README.md`

Records sample provenance, generation procedure, expected source checksum,
registry linkage, and permitted use.

## Test boundary

The seven `tests/operator/` paths verify:

- immutable operator contracts;
- public API;
- statuses and exit codes;
- equivalent human and JSON semantics;
- audit identity and persistence;
- failure visibility;
- recovery mapping;
- dry-run;
- validation-before-mutation;
- safe rerun and idempotency;
- parser and command routing;
- absence of hidden fallback and retry;
- delegation to frozen Gates 2-10 public contracts.

No operator unit test may replace the required fresh-environment acceptance.

## Fresh-environment acceptance path

### `tests/acceptance/test_rie_core_v1_fresh_environment.py`

This acceptance test must:

1. create a fresh controlled Python environment outside the development
   interpreter;
2. install the package using the controlled dependency set;
3. prove the installed `rie` command and version;
4. prove all ten required commands are present;
5. copy or reference only the controlled sample assets;
6. execute the sample PDF-to-Prompt Candidate workflow;
7. compare human and JSON result semantics;
8. inspect complete audit linkage;
9. rerun the workflow and prove no duplicate governed state;
10. exercise one deterministic rejection and its recovery guidance;
11. verify repository integrity after success, rejection, and rerun;
12. record package, lock, sample, output, and audit digests.

The test must not publish a release tag.

## Test-execution boundary

Implementation acceptance requires exactly:

- one targeted operator and acceptance test command;
- one full regression command;
- no automatic retries;
- no hidden rerun after failure.

The targeted command must include all seven operator test files and the
fresh-environment acceptance test.

The full regression must include the entire repository test suite.

A failed fresh-environment acceptance blocks Gate 11 closure and release
authorization.

## Binary and byte-format boundary

All new text paths must be ASCII-only, LF-only, no BOM, and exactly one final
LF unless an existing governed format explicitly requires otherwise.

The sample PDF is the only authorized binary path. Its exact SHA-256 and byte
count must be recorded in implementation and acceptance evidence.

## Implementation sequence

The implementation may be developed in one controlled PR-056D worktree state,
but acceptance must be reported in these ordered checkpoints:

1. operator contract, result, configuration, audit, recovery, service, and CLI;
2. package entry point and dependency lock;
3. documentation and controlled samples;
4. targeted operator tests;
5. fresh-environment acceptance;
6. full regression;
7. exact 28-path scope and fingerprint verification.

No stage authorizes release publication.

## Forbidden expansion

PR-056D must not add or modify:

- existing Gate 2-10 domain modules;
- provider or model integration;
- prompt execution;
- image or multimodal runtime;
- dashboard or multi-user workflow;
- production RSV data;
- remote service dependencies;
- plugin architecture;
- background daemon;
- automatic retry;
- telemetry;
- release tag or Phase 56 publication state.

Any required path outside the exact 28-path boundary requires a new
architecture review before modification.

## Boundary decision

- Gate 11 invoked: `True`
- Gate 11 minimum closure boundary operationally committed: `True`
- Gate 11 operator workflow contract operationally committed: `True`
- Gate 11 implementation boundary selected: `True`
- Gate 11 implementation boundary committed: `False`
- Gate 11 implementation authorized: `False`
- Gate 11 implementation started: `False`
- Fresh-environment acceptance authorized: `False`
- RIE Core v1 release authorized: `False`
- Gate 11 closed: `False`
- Gate 12 invoked: `False`

## Next safe operation

After PR-056C is independently accepted, committed, pushed, and post-commit
verified, the next eligible operation is:

`pr_056d_implement_exact_twenty_eight_path_gate_11_operator_boundary`

That implementation must remain inside this exact boundary and must preserve
all frozen Gates 2-10 contracts.

PR-056C does not start or authorize PR-056D.
