# PR-056B - Gate 11 Operator Workflow, CLI, Audit, Packaging, and Release Contract Review

## Status

Gate 11 operator-facing runtime contract review.

## Review outcome

Selected Gate 11 operator contract:

`single_installed_rie_console_explicit_subcommand_versioned_dual_output_deterministic_exit_code_audit_linked_fail_closed_dry_run_safe_rerun_recovery_packaging_fresh_environment_and_verified_release_operator_contract`

This review selects the complete operator contract required to turn the frozen
Gates 2-10 runtime spine into an installable RIE Core v1 workflow.

It does not select implementation paths, modify production or test code, run
tests, install a package, create sample assets, execute a fresh-environment
acceptance run, create a release tag, or close Gate 11.

## Starting checkpoint

- Phase 56 branch:
  `phase-056-end-to-end-cli-audit-packaging-release`
- PR-056A commit:
  `26aef31f7c26890552b5f28f4b5356b30f58c262`
- Published `main`:
  `b348506541584d3b420a59af167a957834744801`
- Gate 11 has been invoked.
- Gate 11 minimum closure boundary is operationally committed.
- Gate 11 implementation remains unauthorized.

## Contract hierarchy

The operator contract has six inseparable layers:

1. one installed `rie` console entry point;
2. one explicit command grammar;
3. one shared result and exit-code contract;
4. one complete audit and provenance contract;
5. one fail-closed rerun and recovery contract;
6. one packaging, fresh-environment, and verified-release contract.

A command is not Gate 11 compliant when only its domain operation works.
Every command must satisfy all shared layers that apply to it.

## Installed console contract

The operator invokes exactly one installed command:

`rie`

The command must be provided by package metadata through one console entry
point. The operator must not run repository scripts directly, modify
`PYTHONPATH`, open source files, or depend on the development checkout.

Required global commands:

- `rie --help`
- `rie --version`

Required global options:

- `--format human|json`
- `--output <path>` where the command supports an output artifact
- `--dry-run` where the command can mutate governed state

The default format is `human`. Machine-readable automation must explicitly use
`--format json`.

## Minimum command grammar

Gate 11 requires these commands:

- `rie registry validate`
- `rie source inspect`
- `rie ingest pdf`
- `rie evidence build`
- `rie evidence inspect`
- `rie knowledge build`
- `rie knowledge inspect`
- `rie prompt-candidate build`
- `rie audit job`
- `rie export`

No command may infer an omitted official source, ingestion job, repository
revision, Knowledge revision, Prompt Candidate, or export target.

## Deterministic exit-code contract

The installed console uses these stable process exit codes:

- `0` - `SUCCESS`
- `1` - `UNEXPECTED_INTERNAL_FAILURE`
- `2` - `CLI_USAGE_INVALID`
- `3` - `CONFIGURATION_INVALID`
- `4` - `SOURCE_OR_INPUT_INVALID`
- `5` - `CONTRACT_OR_ELIGIBILITY_REJECTED`
- `6` - `STATE_CONFLICT_OR_IDEMPOTENCY_VIOLATION`
- `7` - `PERSISTENCE_OR_IO_FAILURE`
- `8` - `AUDIT_OR_EXPORT_FAILURE`

A rejected operation must never return `0`. Domain issue codes remain more
specific than process exit codes and must be included in both human and JSON
results.

No command may silently replace one failure class with another or collapse all
failures into a generic success or generic nonzero result.

## Shared result contract

Every command returns one logical result with these fields:

- `schema_version`
- `command`
- `status`
- `exit_code`
- `issue_code`
- `message`
- `dry_run`
- `identifiers`
- `provenance`
- `audit`
- `outputs`
- `recovery`

JSON output must use a stable key order and canonical serialization. Human
output must expose the same status, identifiers, issue code, provenance
summary, audit reference, output paths, and recovery instruction.

Human output must not contain materially different success or failure semantics
from JSON output.

## Status contract

Allowed result statuses are:

- `SUCCEEDED`
- `REUSED_EXISTING`
- `NO_CHANGE`
- `DRY_RUN_VALID`
- `REJECTED`
- `FAILED`

`REUSED_EXISTING` and `NO_CHANGE` are successful idempotent outcomes and return
exit code `0`.

`REJECTED` is a deterministic contract decision and uses exit code `2`, `3`,
`4`, `5`, or `6` according to the failure class.

`FAILED` is reserved for persistence, I/O, audit, export, or unexpected
internal failures and uses exit code `1`, `7`, or `8`.

## Validation-before-mutation contract

Every mutating command has these ordered phases:

1. parse and normalize arguments;
2. load explicit configuration;
3. validate referenced identities and inputs;
4. evaluate frozen Gate 2-10 contracts;
5. construct the complete mutation plan;
6. emit a dry-run result or execute the plan;
7. persist governed state atomically;
8. persist the audit result;
9. emit the final operator result.

No governed repository mutation may occur before phases 1-5 pass.

A failed downstream operation must not leave a partially successful governed
state. Where more than one repository is involved, the implementation must use
a documented commit order and recovery marker sufficient to prove and recover
the exact partial state.

## Command-specific contract

### `rie registry validate`

Requires an explicit registry path or explicit configured registry identity.

Returns deterministic ordering, validation status, issue codes, source count,
and registry digest.

It does not inspect document contents, scan directories, or create jobs.

### `rie source inspect`

Requires an exact registered `source_id`.

Returns the exact registry identity, authority, lifecycle, source location,
media type, checksum state where available, and deterministic eligibility
summary.

It does not select a source implicitly or read unrelated sources.

### `rie ingest pdf`

Requires an exact registered PDF source and explicit operator-controlled input.

Returns the immutable ingestion-job identity, source checksum, extraction
artifact identity, result status, and audit reference.

Safe rerun must reuse the exact accepted job and artifacts or return a
deterministic conflict. It must not duplicate repository state.

### `rie evidence build`

Requires an exact accepted ingestion job or extraction artifact.

Returns exact Evidence identities, source spans, eligibility status,
repository revisions, reuse outcome, and audit reference.

It must preserve factual extraction boundaries and must not construct
Knowledge.

### `rie evidence inspect`

Requires exact Evidence identity and repository revision where applicable.

Returns canonical Evidence data, provenance, eligibility, and repository
metadata without mutation.

### `rie knowledge build`

Requires explicit eligible Evidence identities and the exact construction
contract inputs.

Returns Knowledge identity, provenance, repository revision, lifecycle state,
reuse outcome, and audit reference.

It must not silently promote, accept, replace, or select the latest Knowledge.

### `rie knowledge inspect`

Requires exact Knowledge identity and exact repository revision.

Returns canonical Knowledge content, Evidence provenance, lifecycle state,
authority and acceptance metadata, and repository metadata without mutation.

### `rie prompt-candidate build`

Requires an exact governed Knowledge lookup result and explicit prompt intent.

Returns the immutable Prompt Candidate identity, exact Knowledge provenance,
canonical structural representation, reuse outcome, and audit reference.

It does not execute a prompt, invoke a model, select a provider, or generate
creative output.

### `rie audit job`

Requires an exact audit, ingestion-job, or operator-invocation identity.

Returns the complete linked audit chain across registry validation, source
inspection, ingestion, extraction, Evidence, Knowledge, Prompt Candidate, and
export events that exist for that identity.

Rejected and failed operations must remain visible.

### `rie export`

Requires an exact supported artifact identity and explicit output target.

Returns output path, canonical media type, digest, byte count, source identity,
repository revision where applicable, overwrite decision, and audit reference.

It must fail closed on implicit overwrite unless the exact overwrite behavior
is explicitly requested and supported.

## Audit record contract

Every non-help invocation produces one logical audit record, including
validation rejection and failed operations.

The audit record contains:

- `audit_schema_version`
- `invocation_id`
- `command`
- normalized non-secret arguments
- package version
- contract versions
- configuration identity and digest
- exact input identities and digests
- planned mutation identities
- committed output identities and revisions
- result status
- process exit code
- domain issue codes
- rerun or reuse outcome
- recovery state
- export identities and digests
- links to prior and child audit records

Secrets and machine-specific credentials must not be recorded.

The canonical operation digest excludes observational timestamps and
machine-specific paths that are not part of the governed input. Observational
time may be recorded separately without changing deterministic operation
identity.

## Dry-run contract

`--dry-run` performs complete validation and mutation planning but makes zero
governed repository changes.

A valid dry run returns status `DRY_RUN_VALID`, exit code `0`, the exact planned
identifiers where deterministically knowable, and a non-persistent audit
preview.

An invalid dry run returns the same rejection exit code and issue codes that
the real command would return before mutation.

Dry run must not become a weaker validation path.

## Safe-rerun and idempotency contract

The same normalized command, exact identities, contract versions, and input
digests must not create duplicate governed state.

A safe rerun returns:

- `REUSED_EXISTING` when an exact accepted artifact already exists; or
- `NO_CHANGE` when inspection, audit, or export state requires no mutation.

A changed digest, changed exact revision, or incompatible prior state must
return a deterministic rejection or conflict. The command must not
automatically retry, replace, repair, or create a hidden new revision.

## Failure and recovery contract

Every non-success result includes:

- one primary issue code;
- optional ordered supporting issue codes;
- whether governed mutation started;
- whether any repository commit completed;
- the exact recoverable state;
- one deterministic recovery instruction;
- the audit identity or audit preview.

Recovery commands or procedures must be safe to repeat.

The operator must never be told to delete repository state blindly, reset
history, force push, edit persisted artifacts manually, or bypass frozen
contracts.

## Packaging contract

Gate 11 requires:

- completed package metadata in `pyproject.toml`;
- one `rie` console entry point;
- one deterministic package version;
- one controlled dependency lock artifact;
- explicit supported Python version;
- installation instructions;
- configuration instructions;
- operator command reference;
- audit interpretation guide;
- failure and recovery guide;
- sample official-source registry;
- sample PDF;
- sample end-to-end workflow;
- fresh-environment acceptance procedure.

The implementation-boundary review must select the exact paths and packaging
tooling. PR-056B selects only the required behavior.

## Fresh-environment acceptance contract

Gate 11 cannot close from the development checkout alone.

A later acceptance run must start from a fresh controlled environment and
prove:

1. package installation succeeds;
2. `rie --version` reports the accepted package identity;
3. all minimum commands are available through `rie --help`;
4. the sample registry validates;
5. the sample PDF reaches a reviewable Prompt Candidate export;
6. JSON and human outputs carry equivalent semantics;
7. audit linkage is complete;
8. safe rerun creates no duplicate governed state;
9. deterministic rejection and recovery are observable;
10. no source-code editing or development-path injection is required.

## Verified-release contract

The RIE Core v1 release is authorized only after fresh-environment acceptance
is independently accepted.

The annotated release tag must target the exact accepted build and package
version. Local tag object, remote tag object, peeled target, package version,
and acceptance evidence must all agree.

A failed acceptance run cannot produce or preserve an official release tag.

## Existing-foundation comparison rule

Existing CLI, inspector, exporter, package, README, audit, or recovery paths are
foundation only.

The repository inventory must be compared against this complete contract.
Presence of a file or test does not prove:

- one installed console entry point;
- unified command grammar;
- deterministic shared exit codes;
- equivalent human and JSON results;
- complete audit linkage;
- safe rerun;
- fail-closed recovery;
- fresh-environment usability;
- verified release readiness.

## Explicit non-scope

PR-056B does not authorize:

- implementation changes;
- dependency or package changes;
- sample asset creation;
- test execution;
- package installation;
- fresh-environment acceptance;
- Phase 56 merge or release;
- production RSV data admission;
- prompt execution or model invocation;
- Gate 12 or later RCIS extensions.

## Contract decision

- Gate 11 invoked: `True`
- Gate 11 minimum closure boundary operationally committed: `True`
- Gate 11 operator workflow contract selected: `True`
- Gate 11 operator workflow contract committed: `False`
- Gate 11 implementation boundary selected: `False`
- Gate 11 implementation authorized: `False`
- Gate 11 implementation started: `False`
- Fresh-environment acceptance authorized: `False`
- RIE Core v1 release authorized: `False`
- Gate 11 closed: `False`
- Gate 12 invoked: `False`

## Next safe review

After PR-056B is independently accepted, committed, pushed, and post-commit
verified, the next eligible architecture subject is:

`gate_11_cli_audit_packaging_release_implementation_boundary_review`

That review must select the exact production, test, packaging, documentation,
sample, and acceptance paths needed to satisfy this contract.

PR-056B does not start or authorize that implementation-boundary review.
