# PR-022C - Phase 22 Evidence Candidate Contract Implementation Review

## Status

Documentation-only implementation review for the future Evidence Candidate contract.

PR-022C locks the exact two-file scope, dataclass declaration, validation order, standard-library helpers, error policy, canonical JSON procedure, timestamp and locator behavior, and 45-test inventory for a later code-bearing PR. It creates no source or test file and executes no test, parser, ingestion, Evidence, or Knowledge workflow.

## Current checkpoint

- Current branch: `phase-022-evidence-candidate-boundary-review`
- Local Phase 22 HEAD: `0f683a3`
- Remote Phase 22 HEAD: `0f683a3`
- Phase divergence: `0 0`
- Local `main`: `3642955`
- `origin/main`: `3642955`
- Main/origin divergence: `0 0`
- Repository: clean
- Index: clean
- Untracked files: none
- Controlled sandbox exists and is empty
- Real PDF target: absent
- Synthetic PDF target: absent
- Controlled basetemp: absent
- Phase 21 local HEAD: `355e424`
- Phase 21 remote HEAD: `355e424`
- Phase 21 tag object: `f5c812437bab39be3d648784fbe32a9eeb0f7e11`
- Phase 21 tag target: `f4a246f0fdc695dca9a78f620e2c42dd0bb5de53`

## Purpose

PR-022C defines the exact future implementation plan for the approved Evidence Candidate DTO and tests. It locks:

- imports and declaration
- 18 field annotations and order
- constructor validation boundary and sequence
- exception/failure behavior
- string, token, checksum, timestamp, JSON, locator, and diagnostic validation
- equality, hashing, imports, exports, and side effects
- exact private helper scope
- exact synthetic test strategy and test inventory
- exact PR-022D file and execution boundary

No code implementation is authorized until this review passes and a separate PR-022D execution is approved.

## PR-022B contract baseline

PR-022B recorded:

- Acceptance criteria: `50 of 50 SATISFIED`
- Decision: `READY FOR EVIDENCE CANDIDATE CONTRACT IMPLEMENTATION REVIEW`
- Future source module: `src/rie/application/evidence_candidate.py`
- Future public type: `EvidenceCandidate`
- Proposed test module: `tests/application/test_evidence_candidate.py`
- Dataclass: frozen
- Slots: not required
- Central package re-export: not authorized initially
- Field count: `18`
- All fields: required
- Eligibility: separate future contract
- Persistence: absent
- Evidence creation: absent
- Knowledge creation: absent
- Implementation authorized by PR-022B: `False`

PR-022A Option B and every no-lifecycle, no-persistence, no-ingestion, no-automatic-materialization, and no-Knowledge boundary remain controlling.

## Repository implementation evidence

Read-only inspection included:

- `src/rie/application/asset.py`, `src/rie/application/batch.py`, `src/rie/application/metadata.py`, and empty `src/rie/application/__init__.py`
- Frozen ingestion contracts including `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py`
- Tuple validation and finite-number helpers in `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py`
- Constructor validation in `src/official_source/official_source.py`
- Existing Evidence and collection modules under `src/evidence` and `src/collection`
- JSON loading/dumping and explicit `ValueError` behavior across extraction, collection, Knowledge, and ingestion modules
- Parametrized tests and stable message-fragment assertions under `tests/` and `tests/ingestion/`
- `docs/architecture/pr-022a-phase-22-evidence-candidate-boundary-architecture-review.md`
- `docs/architecture/pr-022b-phase-22-evidence-candidate-contract-review.md`
- `pyproject.toml`

Repository-supported implementation conventions:

- standard-library imports, absolute project imports, and PEP 604 union annotations
- `@dataclass(frozen=True)` for immutable contracts
- `__post_init__` for dataclass constructor validation
- private module-level helpers for repeated validation
- explicit boolean exclusion from integer validation
- `isfinite` for numeric finiteness
- `ValueError` for invalid value-contract fields
- field-specific error messages and tests asserting exception type plus stable fragments
- tuples for immutable repeated contract values
- direct module imports where package `__init__.py` is empty
- `pytest.mark.parametrize` for repeated invalid-value cases
- synthetic values and dependency substitution to keep tests filesystem/parser independent

No current repository code implements duplicate-key JSON parsing or RFC 3339 validation, so PR-022C defines those repository-local rules explicitly without claiming an existing convention or external standard beyond the scoped checks.

## Exact implementation file scope

PR-022D may create exactly:

- `src/rie/application/evidence_candidate.py`
- `tests/application/test_evidence_candidate.py`

No other file is technically required.

- `tests/application` does not currently exist, but pytest discovers layer directories without package markers; existing `tests/ingestion` and `tests/extraction` also have no `__init__.py`.
- `src/rie/application/__init__.py` remains unchanged.
- No package export, dependency, configuration, existing Evidence, collector, ingestion, Phase 21, or shared validation file changes are authorized.
- No cleanup, refactor, or utility extraction is authorized.

If either reviewed file requires a third repository file change, PR-022D must stop and return to review.

## Exact imports

The future source file requires exactly these standard-library imports:

```python
import json
import re
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
```

No typing import is required because the field annotations and private helper annotations can use built-in generics and `object`. No third-party or project import is required. Unused imports are prohibited.

## Exact dataclass declaration

The future declaration characteristics are:

- `@dataclass(frozen=True)`
- no `slots=True`
- no inheritance or custom metaclass
- one `__post_init__` validation method
- no defaults
- no lifecycle, persistence, parser, Evidence-conversion, Knowledge-conversion, setter, mutation, or hidden-ID methods

Reviewed declaration shape:

```python
@dataclass(frozen=True)
class EvidenceCandidate:
    source_id: str
    source_type: str
    source_checksum_algorithm: str
    source_checksum: str
    source_authority: str
    source_lifecycle_state: str
    source_reference: str
    execution_id: str
    producer_name: str
    producer_version: str
    result_contract_version: str
    execution_timestamp: str
    payload_type: str
    raw_payload: str
    locator: tuple[tuple[str, str | int | float], ...]
    warnings: tuple[str, ...]
    errors: tuple[str, ...]
    candidate_contract_version: str
```

## Field declaration order

The exact declaration order is:

1. `source_id: str`
2. `source_type: str`
3. `source_checksum_algorithm: str`
4. `source_checksum: str`
5. `source_authority: str`
6. `source_lifecycle_state: str`
7. `source_reference: str`
8. `execution_id: str`
9. `producer_name: str`
10. `producer_version: str`
11. `result_contract_version: str`
12. `execution_timestamp: str`
13. `payload_type: str`
14. `raw_payload: str`
15. `locator: tuple[tuple[str, str | int | float], ...]`
16. `warnings: tuple[str, ...]`
17. `errors: tuple[str, ...]`
18. `candidate_contract_version: str`

All 18 fields are required. `warnings` and `errors` require explicit tuple arguments even when empty. No defaults are introduced.

## Validation philosophy

The constructor validates structural contract correctness only.

Exact validation sequence:

1. Validate exact `str` runtime type, non-empty value, whitespace boundary, and control-character rules for required string fields in declaration order.
2. Validate token-like field syntax using the assigned regular expression.
3. Validate checksum algorithm/value structure.
4. Validate RFC 3339 execution timestamp syntax and calendar/offset validity.
5. Parse and validate repository-canonical JSON, duplicate keys, and finite numbers; compare without rewriting.
6. Validate locator outer/entry types, key order/uniqueness, value types/finiteness, scope, and generic numeric rules.
7. Validate `warnings` tuple and entries.
8. Validate `errors` tuple and entries.

The first violation stops construction. Validation is deterministic and side-effect free.

The constructor does not validate source truth/admission, authority or lifecycle eligibility, production support, payload-specific business schema, Evidence authority, duplicates, accepted Evidence identity, Knowledge meaning, or business validity.

## Exception contract

Select one policy: every constructor contract violation raises `ValueError`, including incorrect runtime types.

This follows `OfficialSource` value-object behavior and avoids a mixed exception surface. No custom exception is justified.

Message style:

- immediate and field-specific
- starts with or contains the exact field name
- short statement of required type/shape/value
- deterministic and free of raw exception/stack-trace leakage
- tests assert `ValueError` plus a stable field-name or rule fragment
- complete message strings are not public API unless PR-022D explicitly pins one for an exceptional reason

No error is swallowed, converted into a default, logged, or accumulated after the first failure.

## Required string validation

The exact runtime type for every string field must be `str`; subclasses and non-strings are rejected.

Common rules for `source_id`, `source_reference`, `execution_id`, and all token/version fields:

- non-empty
- not whitespace-only
- leading or trailing whitespace rejected, not trimmed
- C0/C1 control characters, DEL, carriage return, and newline prohibited
- caller value preserved exactly
- Unicode permitted for opaque identifiers/reference values, subject to control/whitespace rules
- token-like fields are ASCII-only through their token regex

`execution_timestamp` and `raw_payload` receive their specialized validation after base type/non-empty checks. Canonical JSON comparison rejects insignificant outer whitespace. No string is silently lowercased, stripped, normalized, or otherwise mutated.

Diagnostic entries use the same exact-`str`, non-empty, no-edge-whitespace, and no-control/newline rules. Unicode diagnostic text is permitted.

## Token-like field validation

Use three exact repository-local token patterns:

1. Lower underscore identifier: `^[a-z][a-z0-9_]*$`
   - `source_type`
   - `source_authority`
   - `source_lifecycle_state`
   - `payload_type`
2. Lower algorithm token: `^[a-z0-9][a-z0-9._-]*$`
   - `source_checksum_algorithm`
3. General component/version token: `^[A-Za-z0-9][A-Za-z0-9._:+-]*$`
   - `producer_name`
   - `producer_version`
   - `result_contract_version`
   - `candidate_contract_version`

The general pattern permits ASCII letters, digits, period, underscore, hyphen, plus, and colon so semantic versions and adapter identifiers are not over-restricted. Spaces, slash, backslash, controls, and Unicode are prohibited in token fields.

No token regex applies to `source_id`, `execution_id`, `source_reference`, `execution_timestamp`, or `raw_payload`.

## Source and execution identifier validation

`source_id` and `execution_id` use required opaque-string validation only.

They do not require UUID syntax. The constructor performs no random generation, path inference, timestamp generation, prefix assignment, or case normalization. Both must be supplied explicitly and preserved exactly.

`execution_id` is provenance, not Evidence identity and not sufficient for duplicate detection.

## Source reference validation

`source_reference` is an opaque controlled reference string.

The constructor validates only exact string type, non-empty/non-whitespace value, no edge whitespace, and no control/newline characters. It performs no:

- `Path` construction
- path resolution or normalization
- existence/file checks
- filesystem access
- authority inference
- source open/read/write

It is never treated as the sole identity input.

## Checksum validation

`source_checksum_algorithm` and `source_checksum` are explicit required strings.

Constructor checks:

- algorithm matches the lower algorithm token pattern
- checksum matches `^[0-9a-f]+$`
- checksum length is even
- no prefix, whitespace, or uppercase is accepted
- neither value is mutated

The DTO does not calculate a checksum, hard-code/default an algorithm, validate algorithm-specific digest lengths, establish source authority, or access source bytes. Algorithm support and length semantics remain future eligibility/source-admission rules.

## Execution timestamp validation

The accepted repository-local RFC 3339 subset is:

```text
YYYY-MM-DDTHH:MM:SS[.fraction](Z|+HH:MM|-HH:MM)
```

Exact procedure:

1. Require regex match: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$`.
2. For validation only, replace a terminal `Z` with `+00:00`; otherwise use the supplied offset text.
3. Parse the temporary validation value with `datetime.fromisoformat`.
4. Reject invalid calendar/time/offset values and any result with no UTC offset.
5. Preserve the original input string unchanged in the DTO.

Upper-case `Z` and explicit numeric offsets are accepted. Lower-case `z`, date-only values, space separators, missing seconds, and timezone-naive values are rejected.

No clock, default timestamp, environment timezone, or timezone conversion is used.

## Canonical JSON validation

Select Option 1: validate that `raw_payload` is already repository-canonical. Never canonicalize or replace it inside the DTO.

Repository-canonical JSON is scoped to this exact procedure and is not claimed to implement RFC 8785:

1. Parse with `json.loads` using a duplicate-key-rejecting `object_pairs_hook` and a non-finite-constant-rejecting `parse_constant`.
2. Permit any valid top-level JSON value structurally: object, array, string, number, boolean, or null. Payload-specific eligibility decides whether it is supported.
3. Serialize the parsed value with:
   - `ensure_ascii=False`
   - `sort_keys=True`
   - `separators=(",", ":")`
   - `allow_nan=False`
4. Compare the serialized string exactly with the original `raw_payload`.
5. Raise `ValueError` containing `raw_payload` and a stable rule fragment if parsing, finiteness, or exact comparison fails.

Consequences:

- object keys must be lexicographically ordered
- insignificant spaces/newlines are rejected
- canonical separators are compact
- literal Unicode is preserved; alternative `\u` escaping that serializes differently is rejected
- Python standard-library numeric round-trip output defines the accepted numeric spelling
- negative zero or exponent spellings that round-trip differently are rejected
- input is never rewritten

## Duplicate key and non-finite number handling

Duplicate keys cause immediate rejection at every nested object level.

The private `object_pairs_hook` receives `list[tuple[str, object]]`, tracks seen keys, raises `ValueError` on a repeated key, and otherwise returns a normal dictionary for the canonical dump comparison.

Non-finite values are rejected in two ways:

- `parse_constant` immediately raises `ValueError` for `NaN`, `Infinity`, or `-Infinity`.
- `json.dumps(..., allow_nan=False)` rejects a finite-looking numeric token such as an overflowing exponent if parsing produced non-finite float state.

No external JSON package is added.

## Payload type boundary

The constructor structurally accepts any `payload_type` matching the lower underscore identifier pattern. It does not maintain an authorization allowlist.

Distinction:

- Structurally valid token: DTO constructor responsibility.
- Currently reviewed direction: `document_structural_metadata`.
- Currently authorized Evidence materialization: none.
- Supported payload contract and source type: future eligibility/contract responsibility.

This avoids coupling the generic application DTO to Phase 21 alone while granting no extracted-text, image, OCR, or production authority.

## Locator validation

`locator` is required and must be non-empty.

Constructor structural checks:

- outer value exact type is `tuple`
- every entry exact type is a two-item `tuple`
- key exact type is `str`, matches `^[a-z][a-z0-9_]*$`, and is non-empty
- keys are unique and already in lexicographic order
- allowed keys are `column_index`, `height`, `page_index`, `row_index`, `scope`, `width`, `x`, and `y`
- value exact type is `str`, `int`, or `float`; `bool` is rejected
- string values follow required string rules
- float values are finite using `isfinite`
- `scope` is required and must be one of `source`, `document`, `page`, `region`, or `table_cell`
- indexes, when present, are integers and non-negative
- `x` and `y`, when present, are finite numeric values and non-negative
- `width` and `height`, when present, are finite numeric values and greater than zero
- no nested mutable value is possible under the field type

Generic scope/key-set checks:

- `source` and `document`: only `scope`
- `page`: exactly `page_index` and `scope`
- `region`: exactly `height`, `scope`, `width`, `x`, and `y`, with optional `page_index`
- `table_cell`: exactly `column_index`, `row_index`, and `scope`, with optional `page_index`

Page index is zero-based. One-based `page_number` is not a locator key.

Coordinate system, units, document/image association, payload-type/scope compatibility, and semantic support remain future payload-specific eligibility rules. Structural acceptance of `region` or `table_cell` grants no image/table processing authority.

## Diagnostic tuple validation

`warnings` and `errors`:

- must each be exact `tuple` values
- may be empty
- must contain exact `str` items only
- reject empty, whitespace-only, edge-whitespace, control-character, carriage-return, and newline entries
- preserve input order and exact Unicode text
- reject lists and exception objects without conversion

Duplicate diagnostic strings are permitted and preserved. Deduplication would be semantic mutation and is not a DTO responsibility.

Diagnostic presence or absence does not decide eligibility, rejection, or Evidence authority.

## Candidate contract version

`candidate_contract_version` is a required explicit general token. The constructor validates type, non-empty value, edge/control rules, and the general token regex.

PR-022C assigns no global initial version and authorizes no module constant. Future tests may use synthetic data such as `candidate-contract-test-v1`; that value is fixture data, not an official version decision.

No package, environment, Git, or current-version lookup is permitted.

## Immutability and equality

- Assignment after construction raises `FrozenInstanceError` through standard frozen-dataclass behavior.
- Default dataclass equality compares all 18 fields.
- No custom `__eq__` is authorized.
- All field types are hashable, so default frozen-dataclass hashing may exist.
- No custom `__hash__` is authorized.
- Hash values are not asserted as stable across processes and are not candidate identity or repository identity.
- DTO equality and hash remain distinct from future deterministic candidate identity.

## Public API

Reviewed import:

```python
from rie.application.evidence_candidate import EvidenceCandidate
```

Direct module import must work. No changes to `src/rie/application/__init__.py`, another package export, or `pyproject.toml` are required or authorized.

Tests may construct the DTO directly. Future production adapters should use a separately reviewed application builder rather than ad hoc construction once that builder exists.

## Side-effect prohibition

Construction and private validation perform no:

- filesystem access or source existence check
- checksum calculation
- parser or ingestion call
- network access
- environment-variable access
- package-version or Git lookup
- current-clock or timezone lookup
- random generation
- logging
- persistence or global-state mutation
- Evidence/collection insertion
- EvidenceRelationship, Knowledge, Product Knowledge, Official Knowledge, or Prompt Candidate creation

Validation consumes only provided immutable values and standard-library pure parsing/validation operations.

## Private helper boundary

The future source may define only these small private module-level helpers, or fewer if behavior remains identical:

- `_validate_required_string`
- `_validate_token`
- `_validate_checksum`
- `_validate_execution_timestamp`
- `_reject_duplicate_object_pairs`
- `_reject_non_finite_constant`
- `_validate_canonical_json`
- `_validate_locator`
- `_validate_diagnostics`
- `_contains_control_character`

Private compiled regex constants for the reviewed patterns are permitted. No public helper, helper class, shared utility module, registry, serializer, builder, or validation framework is authorized.

## Exact test file scope

All PR-022D tests must be contained in:

```text
tests/application/test_evidence_candidate.py
```

The new `tests/application` directory requires no `__init__.py`; current layer test directories are discovered without package markers. Existing tests must not change.

## Test fixture strategy

Use one small private helper such as `_candidate(**overrides)` returning a candidate built from neutral synthetic strings, canonical structural JSON, a document locator, and explicit empty diagnostic tuples.

The helper:

- has no broad fixture framework
- reads no file and uses no PDF
- calls no parser, clock, network, environment, package metadata, or Git command
- generates no random ID or checksum
- uses literal synthetic checksum, timestamp, versions, payload, and reference values

Parametrization should cover repeated string/token/locator invalid cases without obscuring the asserted field boundary.

## Exact test inventory

PR-022D must implement at least these exact 45 tests:

1. Valid construction with all 18 required fields.
2. Exact field values are preserved.
3. Frozen assignment raises `FrozenInstanceError`.
4. Identical values compare equal.
5. Changing one field produces inequality.
6. List passed as `warnings` raises `ValueError`.
7. List passed as `errors` raises `ValueError`.
8. List passed as `locator` raises `ValueError`.
9. Invalid locator entry shape raises `ValueError`.
10. Duplicate locator key raises `ValueError`.
11. Unordered locator keys raise `ValueError`.
12. Non-string locator key raises `ValueError`.
13. Boolean locator value raises `ValueError`.
14. Non-finite float locator value raises `ValueError`.
15. Every required string field rejects an empty string.
16. Every required string field rejects whitespace-only input.
17. Malformed execution timestamp raises `ValueError`.
18. Timezone-naive timestamp raises `ValueError`.
19. Upper-case `Z` and explicit-offset timestamps are accepted.
20. Invalid JSON raises `ValueError`.
21. Duplicate JSON key raises `ValueError`.
22. `NaN`, `Infinity`, `-Infinity`, and overflow-produced non-finite JSON raise `ValueError`.
23. Non-canonical JSON raises `ValueError`.
24. Repository-canonical JSON is accepted.
25. `raw_payload` is preserved exactly.
26. `source_reference` construction performs no filesystem access.
27. Construction performs no checksum calculation.
28. No default/current timestamp exists; omission fails normal dataclass construction.
29. Dataclass fields contain no eligibility/acceptance/rejection fields.
30. Dataclass fields contain no Evidence ID.
31. Dataclass fields contain no Knowledge or Prompt Candidate fields.
32. Construction creates no Evidence.
33. Construction inserts nothing into EvidenceCollection.
34. Construction performs no persistence.
35. Construction performs no parser call.
36. Construction performs no network call.
37. Direct module import works.
38. No central `rie.application` re-export is required.
39. Diagnostic tuple order and duplicate entries are preserved.
40. Empty diagnostic tuples are accepted.
41. Empty, whitespace-only, or newline diagnostic item raises `ValueError`.
42. A syntactically valid future payload token is accepted structurally without authorizing it.
43. A canonical `document_structural_metadata` payload and document locator are accepted structurally.
44. Unsupported payload authorization remains absent from the DTO.
45. Repeated construction from identical inputs is deterministic.

Payload-specific eligibility mismatch, source authority/lifecycle, and algorithm-specific checksum tests remain outside this DTO test file until their contracts are reviewed.

## Test assertion boundary

Tests assert:

- exact exception type `ValueError`
- stable field-name or rule fragment with `pytest.raises(..., match=...)`
- exact preserved values and field inventory where contract-critical

Tests do not pin every complete error sentence. Full error text is not unnecessarily made public API. Frozen assignment specifically asserts `FrozenInstanceError`.

## PR-022D implementation boundary

The exact future code-bearing PR is:

**PR-022D - Evidence Candidate Contract Implementation**

PR-022D may:

- create only the reviewed source and test files
- implement exactly the reviewed dataclass, validation, private helpers, and tests
- run only `tests/application/test_evidence_candidate.py` initially

PR-022D must not:

- modify existing source, tests, package exports, dependencies, or configuration
- integrate Evidence collectors or ingestion
- create eligibility result/validator, deterministic identity, Evidence, persistence, or Knowledge
- process real assets or PDFs
- modify Phase 21 code or branches
- broaden canonical JSON, payload, locator, or public API behavior

PR-022D must stop if implementation requires another file, dependency, behavior, authority, or test scope.

## Acceptance criteria

1. **SATISFIED** - Current branch is the approved Phase 22 branch.
2. **SATISFIED** - Local Phase 22 HEAD equals `0f683a3`.
3. **SATISFIED** - Remote Phase 22 HEAD equals `0f683a3`.
4. **SATISFIED** - Phase divergence is `0 0`.
5. **SATISFIED** - `main` and `origin/main` remain `3642955`.
6. **SATISFIED** - PR-022B decision is recorded.
7. **SATISFIED** - Future source path remains exact.
8. **SATISFIED** - Future test path remains exact.
9. **SATISFIED** - No additional implementation path is required.
10. **SATISFIED** - Exact standard-library imports are reviewed.
11. **SATISFIED** - Dataclass declaration is exact.
12. **SATISFIED** - Frozen behavior is required.
13. **SATISFIED** - Slots remain unrequired.
14. **SATISFIED** - Field order remains exact.
15. **SATISFIED** - Field annotations remain exact.
16. **SATISFIED** - All 18 fields remain required.
17. **SATISFIED** - No defaults are introduced silently.
18. **SATISFIED** - Constructor structural-validation boundary is defined.
19. **SATISFIED** - Eligibility validation remains outside the DTO.
20. **SATISFIED** - Evidence materialization remains outside the DTO.
21. **SATISFIED** - One exception policy is selected.
22. **SATISFIED** - String validation rules are defined.
23. **SATISFIED** - Token-field validation is defined.
24. **SATISFIED** - Source reference causes no filesystem access.
25. **SATISFIED** - Checksum validation remains structural.
26. **SATISFIED** - Timestamp validation is exact.
27. **SATISFIED** - Current-time lookup is prohibited.
28. **SATISFIED** - Raw payload canonical JSON rule is exact.
29. **SATISFIED** - Duplicate JSON keys are rejected.
30. **SATISFIED** - Non-finite JSON values are rejected.
31. **SATISFIED** - Raw payload is not silently rewritten.
32. **SATISFIED** - Payload-type structural/support distinction is explicit.
33. **SATISFIED** - Locator structure validation is exact.
34. **SATISFIED** - Boolean locator values are rejected.
35. **SATISFIED** - Non-finite locator values are rejected.
36. **SATISFIED** - Payload-specific locator semantics remain separate where appropriate.
37. **SATISFIED** - Diagnostic tuple validation is exact.
38. **SATISFIED** - Diagnostic presence does not decide eligibility.
39. **SATISFIED** - Candidate contract version handling is defined.
40. **SATISFIED** - Equality is distinguished from deterministic identity.
41. **SATISFIED** - No custom identity generation is introduced.
42. **SATISFIED** - Direct-module public import is selected.
43. **SATISFIED** - Central re-export remains unauthorized.
44. **SATISFIED** - Side-effect prohibition is complete.
45. **SATISFIED** - Private-helper scope is bounded.
46. **SATISFIED** - Exact future test inventory is defined.
47. **SATISFIED** - Test fixture strategy is synthetic and side-effect free.
48. **SATISFIED** - Test assertion boundary is defined.
49. **SATISFIED** - PR-022D file scope is exact.
50. **SATISFIED** - PR-022D execution boundary is exact.
51. **SATISFIED** - No source file was created or modified.
52. **SATISFIED** - No test file was created or modified.
53. **SATISFIED** - No dependency, configuration, or prior document was modified.
54. **SATISFIED** - No tests, parser, ingestion, Evidence, or Knowledge workflow was executed.
55. **SATISFIED** - PR-022C does not authorize work outside the reviewed PR-022D scope.

All 55 implementation-review acceptance criteria are satisfied.

## Recommended PR-022D

The single recommended next PR is:

**PR-022D - Evidence Candidate Contract Implementation**

Its authority is limited to the two reviewed files and the exact focused test execution described above.

## Implementation review decision

**READY FOR EVIDENCE CANDIDATE CONTRACT IMPLEMENTATION**
