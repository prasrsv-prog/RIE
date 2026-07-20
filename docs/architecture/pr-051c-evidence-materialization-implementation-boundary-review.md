# PR-051C - Evidence Materialization Implementation Boundary Review

## 1. Boundary identity

Gate: `Gate 6 - Evidence Materialization`

Phase: `Phase 51 - Evidence Materialization`

Minimum boundary: `single_valid_extraction_artifact_explicitly_eligible_source_page_scoped_exact_traceable_evidence_collection_boundary`

Selected implementation boundary: `new_isolated_value_only_evidence_materialization_namespace_with_exact_contract_canonicalization_service_and_boundary_tests`

## 2. Implementation decision

Gate 6 implementation is authorized only as a new isolated, value-only namespace. It may consume the committed Gate 5 `ExtractionArtifact` value and one explicit Gate 6 `EvidenceEligibilitySnapshot` value.

No existing production or test path may be modified by PR-051D.

## 3. Exact authorized paths

Production paths (`4`, all new):
- `src/rie/evidence_materialization/__init__.py`
- `src/rie/evidence_materialization/evidence_materialization_contract.py`
- `src/rie/evidence_materialization/evidence_materialization_canonicalization.py`
- `src/rie/evidence_materialization/evidence_materialization_service.py`

Test paths (`4`, all new):
- `tests/evidence_materialization/test_evidence_materialization_contract.py`
- `tests/evidence_materialization/test_evidence_materialization_canonicalization.py`
- `tests/evidence_materialization/test_evidence_materialization_service.py`
- `tests/evidence_materialization/test_evidence_materialization_boundary.py`

Any implementation path outside these eight paths is unauthorized.

## 4. Module responsibilities

`__init__.py` exposes only the reviewed Gate 6 public API.

`evidence_materialization_contract.py` owns all immutable value contracts, exact version and field-order constants, status and issue enums, fixed issue messages, and validation.

`evidence_materialization_canonicalization.py` owns eligibility snapshot canonicalization/digest, Evidence identity canonicalization/ID, and collection identity canonicalization/ID.

`evidence_materialization_service.py` owns the pure deterministic transformation from exact `ExtractionArtifact` plus exact `EvidenceEligibilitySnapshot` to one `EvidenceMaterializationResult`.

## 5. Required public API

Contract-module public symbols (`29`):
- `EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION`
- `EVIDENCE_COLLECTION_CONTRACT_VERSION`
- `TRACEABLE_EVIDENCE_CONTRACT_VERSION`
- `EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION`
- `EVIDENCE_ELIGIBILITY_SNAPSHOT_CANONICALIZATION_VERSION`
- `TRACEABLE_EVIDENCE_IDENTITY_CANONICALIZATION_VERSION`
- `EVIDENCE_COLLECTION_IDENTITY_CANONICALIZATION_VERSION`
- `TRACEABLE_EVIDENCE_CONTENT_TYPE`
- `TRACEABLE_EVIDENCE_ID_PREFIX`
- `EVIDENCE_COLLECTION_ID_PREFIX`
- `EVIDENCE_ELIGIBILITY_FIELD_ORDER`
- `TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER`
- `TRACEABLE_EVIDENCE_FIELD_ORDER`
- `TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER`
- `EVIDENCE_COLLECTION_FIELD_ORDER`
- `EVIDENCE_COLLECTION_IDENTITY_FIELD_ORDER`
- `EVIDENCE_MATERIALIZATION_ISSUE_FIELD_ORDER`
- `EVIDENCE_MATERIALIZATION_RESULT_FIELD_ORDER`
- `EvidenceMaterializationStatus`
- `EvidenceMaterializationIssueCode`
- `EvidenceMaterializationIssue`
- `EvidenceMaterializationContractError`
- `EvidenceEligibilitySnapshot`
- `TraceableEvidenceProvenance`
- `TraceableEvidence`
- `EvidenceCollection`
- `EvidenceMaterializationResult`
- `evidence_materialization_issue`
- `raise_evidence_materialization_error`

Canonicalization-module public symbols (`6`):
- `canonicalize_evidence_eligibility_snapshot`
- `derive_evidence_eligibility_snapshot_digest`
- `canonicalize_traceable_evidence_identity`
- `derive_traceable_evidence_id`
- `canonicalize_evidence_collection_identity`
- `derive_evidence_collection_id`

Service-module public symbols (`1`):
- `materialize_evidence_collection`

The package root must re-export exactly the reviewed public API and no legacy Evidence symbols.

## 6. Import boundary

The authoritative implementation may import the Gate 5 `ExtractionArtifact` contract and its version constant. All other runtime behavior must be implemented inside the new namespace using Python standard-library value primitives.

The implementation must not import EvidenceCandidate, candidate snapshot, legacy accepted-Evidence materializer, AcceptedEvidence, legacy EvidenceIdentity, OfficialSource policy/gate/preflight runtime, repositories, SQLite, network libraries, subprocesses, or filesystem path helpers.

Eligibility is supplied as an already explicit immutable snapshot. Gate 6 must not evaluate, reconstruct, enrich, or reload eligibility.

## 7. Required behavior

The implementation and tests must cover these exact behavioral areas (`42`):
- exact version constants
- exact field-order constants
- exact identifier prefixes
- exact content type
- status enum values
- issue-code enum order
- fixed issue messages
- frozen issue value
- immutable contract error
- eligibility snapshot exact field validation
- eligibility snapshot eligible-only validation
- eligibility snapshot review rejection
- eligibility snapshot SHA-256 validation
- provenance exact field validation
- Evidence exact content preservation
- Evidence empty content preservation
- Evidence warning order preservation
- Evidence warning duplicate preservation
- Evidence content digest validation
- Evidence derived ID validation
- EvidenceCollection immutable item order
- EvidenceCollection zero-page support
- EvidenceCollection derived ID validation
- materialized result shape
- rejected result shape
- no partial Evidence on rejection
- eligibility canonical bytes
- eligibility digest determinism
- Evidence identity canonical bytes
- Evidence identity determinism
- collection identity canonical bytes
- collection identity determinism
- UTF-8 non-ASCII preservation
- no BOM no CR one final LF
- source ID exact match
- source path exact match
- source checksum exact match
- one Evidence per page extraction
- page locator exact mapping
- artifact value not mutated
- no legacy runtime imports
- no persistence network clock random or filesystem side effects

## 8. Deterministic rejection precedence

When more than one service-level failure is observable, the service returns the first issue in the exact PR-051B issue-code order. It never returns multiple issues or partial Evidence.

Direct invalid value construction raises the reviewed immutable contract error with the same fixed code-to-message mapping.

## 9. Explicit exclusions

PR-051D may not add serializers or deserializers for file publication, CLI, API, persistence, repositories, migrations, audit storage, Gate 7 idempotency, registry loading, source reading, PDF parsing, extraction, Knowledge construction, Prompt Candidate behavior, retries, fallbacks, background work, current-clock values, or random identifiers.

PR-051D may not modify, migrate, delete, wrap, or adapt legacy Evidence runtime paths.

## 10. Verification requirements

PR-051D acceptance requires:

- exact eight-path implementation scope;
- exact reviewed public API;
- targeted Gate 6 tests;
- full repository regression;
- import-boundary checks proving no prohibited imports;
- deterministic canonical bytes and identities;
- no repository mutation, publication, or Gate 7 behavior.

## 11. Decision

Decision:

`EVIDENCE_MATERIALIZATION_IMPLEMENTATION_BOUNDARY_SELECTED`

Status after this review:

- Gate 6 active closure target: `True`;

- Gate 6 minimum closure boundary selected: `True`;

- Gate 6 runtime contract selected: `True`;

- Gate 6 implementation boundary selected: `True`;

- Gate 6 implementation authorized: `True`;

- Gate 6 implementation started: `False`;

- Gate 6 closed: `False`;

- Gate 7 invoked: `False`.

The next safe operation is PR-051D - Evidence Materialization Contract Implementation.
