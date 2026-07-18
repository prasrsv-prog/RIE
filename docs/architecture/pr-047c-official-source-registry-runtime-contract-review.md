# PR-047C - Official Source Registry Runtime Contract Review

## 1. Review identity

Branch: `phase-047-rie-v1-runtime-spine-gates-2-11-gap-review`

Starting commit: `954ce8115a59d7719ac319a2fc953d4357d51848`

Review type: architecture-only Gate 2 runtime contract and current-capability comparison.

This review does not implement the contract, run tests, start the project interpreter, mutate Git, close Gate 2, close Phase 47, merge, tag, or start Phase 48.

## 2. Governing requirements

Gate 2 requires a validated official source registry with a loader, schema validation, duplicate detection, enum mapping, explicit unknown handling, authority and lifecycle validation, deterministic ordering, validation report, official configuration, and operator CLI validation.

The runtime must not read referenced document content, scan directories, infer facts, or create Evidence or Knowledge.

## 3. Exact reviewed inputs

Committed input count: `8`
- `docs/architecture/pr-047b-official-source-registry-runtime-minimum-closure-boundary-review.md` - `19690cba9e87843996386af25bc13887e172ef202c45ab6fa1d1ea0f4b68fe91`
- `pyproject.toml` - `227d654d99c555302073395e182f169524999eae7dccf3c869e81fc5d6a1b445`
- `src/official_source/official_source.py` - `a535198e907f70ad37298a87ab9309e010a8c0ee7d5ee493fc0fd79973d2cdfb`
- `src/official_source/official_source_registry_loader.py` - `5001cb32d95ee0a02f3958ac40b8ecfcd469722b3eef6c4102d483285910d841`
- `src/rie/__main__.py` - `47fe63abbc09097725f85d96040bc5629e2e4407c5f2311c28bb5864a9e6668b`
- `src/rie/official_source/inspect_official_source_registry.py` - `935e65d171afae72e678db5ba52e6c0fa179d55c81cf4733a852ccb8eaf1633f`
- `tests/test_inspect_official_source_registry_cli.py` - `4c9d6c46f84bad99378b5335cc800565849ebdb739633133d27abed2ec27e4bb`
- `tests/test_official_source_registry_loader.py` - `001fd40d12465fe410178d6818f7bc450f27b19736c75338fe872edbfe57a95a`

Requirements snapshot SHA-256: `4d6b87dc6306ba39bbd624a3489345559f700ccb23173cc5e965f37801832c77`

## 4. Existing capability result

Existing capability evidence SHA-256: `0cee51dbddc0265c9d6e1301d8dc6ce7f19cd265d77f02a11c7892219b909730`

The current repository already contains substantial Gate 2 foundations:
- frozen Official Source domain objects and enums;
- explicit JSON-path registry loading;
- structural and field validation;
- duplicate `source_id` rejection;
- enum mapping and explicit `unknown` handling;
- authority and lifecycle enum validation;
- input-order preservation;
- module-level operator inspection with success and failure exit codes;
- deterministic sorting of aggregate enum counts;
- tests proving nonexistent referenced source paths are not opened.

These foundations are reusable. They do not yet constitute a complete Gate 2 runtime contract.

## 5. Contract-compliance matrix

Matrix SHA-256: `3b697b1985f0509c0b10c2bef69943433bc9774e029e71c1096c374eea758cbf`

Satisfied: `8`

Partial: `2`

Gap: `4`

| Requirement | Status | Evidence |
|---|---|---|
| `explicit_registry_path` | `SATISFIED` | loader accepts explicit str or Path; no default path |
| `json_decode` | `SATISFIED` | load_from_json_file reads UTF-8 registry JSON and decodes it |
| `schema_validation` | `SATISFIED` | root, list, item, required, optional, unknown, and forbidden fields validated |
| `duplicate_source_id` | `SATISFIED` | seen source IDs reject duplicates |
| `enum_mapping_and_unknown_handling` | `SATISFIED` | exact enum mapping includes explicit UNKNOWN members |
| `authority_and_lifecycle_validation` | `SATISFIED` | authority and lifecycle fields map through domain enums |
| `source_order_preserved` | `SATISFIED` | loader appends in input enumeration order and tests assert order |
| `no_source_document_content_read` | `SATISFIED` | nonexistent source paths remain accepted string references |
| `immutable_validation_request` | `GAP` | current entry point receives raw path argument without frozen request contract |
| `immutable_validation_result` | `GAP` | loader returns mutable list and CLI returns integer plus stdout |
| `typed_error_taxonomy` | `GAP` | current behavior exposes generic exceptions and free-text messages |
| `deterministic_validation_report` | `PARTIAL` | aggregate values are sorted but no versioned status/error report contract exists |
| `official_registry_configuration` | `GAP` | no tracked configs/official_source_registry.json exists |
| `operator_cli_command_acceptance` | `PARTIAL` | runnable module main exists but exact module command and repeated output are not acceptance-tested |

## 6. Selected runtime contract

Selected contract: `official_source_registry_validation_contract_v1`

Selected result contract: `immutable_fail_fast_order_preserving_registry_validation_result`

### 6.1 Request contract

The runtime request is an immutable value with exactly one explicit `registry_path` and no default path.

The path identifies only the registry JSON file. It does not authorize reading any referenced `source_path`.

### 6.2 Result contract

The validation result is immutable and has exactly these semantic fields:
- `contract_version`;
- `status`, with values `valid` or `invalid`;
- `sources`, as an order-preserving tuple of existing frozen `OfficialSource` values;
- `issues`, as a deterministic tuple of typed validation issues.

A valid result has ordered sources and no issues. An invalid fail-fast result has no sources and exactly one issue.

### 6.3 Minimum issue taxonomy

The minimum stable issue codes are:
- `registry_missing`;
- `registry_unreadable`;
- `invalid_json`;
- `invalid_registry_structure`;
- `invalid_registry_entry`;
- `duplicate_source_id`.

Each issue preserves a stable code, operator-readable message, optional item index, and optional field name. Raw exception type and wording are not the public contract.

### 6.4 Ordering and determinism

Source order is exactly registry input order.

Aggregate report sections use fixed section order and lexicographically sorted enum values.

The same registry bytes and contract version must produce the same status, source order, issue code, issue location, exit code, and report text.

No clock, randomness, network access, retry, fallback, directory scan, wildcard, recursive processing, or source-document read is permitted.

### 6.5 Operator command

Selected command: `python -m rie.official_source.inspect_official_source_registry <registry_json_path>`

Exit code `0` means valid. Exit code `1` means registry validation failed. Argparse usage failure remains exit code `2`.

A package installer entry point and root multi-command CLI are not required for Gate 2 and remain deferred to Gate 11.

### 6.6 Deterministic report boundary

The valid report contains:
- fixed report title;
- contract version;
- `status: valid`;
- total source count;
- fixed enum-count sections in deterministic order.

The invalid report contains:
- fixed report title;
- contract version;
- `status: invalid`;
- one stable issue code;
- one operator-readable issue message;
- optional item index and field name when available.

Neither valid nor invalid output prints referenced `source_path` values.

### 6.7 Official configuration contract

Required tracked path: `configs/official_source_registry.json`

The minimum valid initial shape is:

```json
{
  "official_sources": []
}
```

An empty initial registry validates runtime mechanics without asserting that official source population is complete. Population and promotion of actual official entries remain separately governed.

## 7. Proven remaining gaps

The following four gaps are proven:
1. no immutable validation request contract;
2. no immutable typed validation result and issue contract;
3. no tracked official registry configuration;
4. no acceptance evidence for exact repeated report text and the selected module command.

The current loader itself is not proven missing and must be reused unless the implementation-boundary review identifies an exact incompatibility.

## 8. Candidate implementation categories

The next boundary review may select only the smallest necessary work from these categories:
- add the immutable validation request, result, and issue contracts;
- add a thin validation service that adapts existing loader behavior into the selected result contract;
- adapt the existing inspection module to print the selected deterministic report;
- add the tracked official registry configuration;
- add focused tests for contract shape, error-code mapping, repeated output, selected module command, and no source-content reads.

No change to `pyproject.toml`, `src/rie/__main__.py`, the Official Source domain enums, or downstream eligibility and Evidence workflows is selected by PR-047C.

## 9. Targeted-semantics determination

No semantic-chain blocker is proven.

The remaining gaps are runtime-contract, configuration, reporting, and acceptance gaps. Additional lifecycle, assertion, contradiction, current-state, repository, persistence, and policy-framework semantics remain unauthorized.

## 10. Exact next review

Next review subject: `official_source_registry_runtime_implementation_boundary_review`

Planned document: `docs/architecture/pr-047d-official-source-registry-runtime-implementation-boundary-review.md`

PR-047D must select exact production, test, configuration, and existing-file boundaries for the smallest implementation that satisfies this contract.

PR-047C does not start implementation or PR-047D.

## 11. Repository scope

PR-047C creates exactly one untracked architecture document:

- `docs/architecture/pr-047c-official-source-registry-runtime-contract-review.md`

No tracked production, test, configuration, package, CLI, API, database, migration, or existing architecture file is modified.

## 12. Test and execution status

Tests run: 0.
Project interpreter processes: 0.
Git mutation commands: 0.
Referenced official source document-content reads: 0.

## 13. Final decision

# SELECTED RUNTIME CONTRACT: OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_V1

Current Gate 2 runtime status: PARTIAL.

Gate 2 remains OPEN. Implementation is not authorized by PR-047C.

Phase 47 remains open. PR-047D, merge, tag, closure, and Phase 48 do not start automatically.
