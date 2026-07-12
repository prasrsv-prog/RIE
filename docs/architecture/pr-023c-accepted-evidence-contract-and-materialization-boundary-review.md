# PR-023C — Accepted Evidence Contract and Materialization Boundary Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-023-knowledge-governance-review` |
| Reviewed HEAD | `6cc26a79476251cb579e25f2227ef9c660d5abc0` |
| Gate type | Documentation-only |
| Inherited PR-023B decision | `READY FOR ACCEPTED EVIDENCE CONTRACT REVIEW` |
| Final PR-023C decision | **ACCEPTED EVIDENCE CONTRACT BOUNDARY APPROVED; IMPLEMENTATION DEFERRED** |
| Recommended next gate | **PR-023D - Deterministic Evidence Identity and Idempotency Contract Review** |
| Recommended next gate type | **Documentation-only** |

## 2. Purpose

PR-023C defines the authoritative accepted-Evidence contract boundary and the materialization boundary without creating code.

The review separates:

- application-layer `EvidenceCandidate`;
- eligibility/preflight/workflow results;
- accepted factual Evidence;
- deterministic identity;
- materialization result;
- repository persistence;
- Knowledge construction.

Only the contract boundary is approved. Identity, repository, persistence, tests, and production implementation remain deferred.

## 3. Checkpoint and preservation

PR-023B was verified as an exact one-file documentation commit:

- Commit: `6cc26a79476251cb579e25f2227ef9c660d5abc0`
- Parent: `0a765c1a9af907dadb1efc03821b73402755694e`
- Subject: `docs: review accepted evidence prerequisites`
- File: `docs/architecture/pr-023b-accepted-evidence-materialization-identity-and-repository-prerequisite-review.md`
- File SHA-256: `e189c0f4830d03a4dfc1cb9a841566c1e083a68cdda66fbf087b619c89fbd85a`

The Phase 23 branch is synchronized with its remote at divergence `0 0`.

Phase 22 remains preserved:

- Branch: `phase-022-evidence-candidate-boundary-review`
- Branch target: `e41269e764979f94f23f93692136c63cc603f2e2`
- Official tag: `v0.22.0-rcis-evidence-candidate-boundary-phase`
- Tag object: `1a7488e7cc2830aea2506182e6a6aba797cbebcf`
- Peeled target: `e41269e764979f94f23f93692136c63cc603f2e2`

The controlled PDF sandbox and `D:\PROJECT\pytest-temp` were verified empty. The real and synthetic PDF targets were absent. The known read-only `.pytest_cache` warning was not repaired or deleted.

## 4. Current contract observations

### 4.1 Application EvidenceCandidate

- `src/rie/application/evidence_candidate.py` line 33: `@dataclass(frozen=True)`
- `src/rie/application/evidence_candidate.py` line 34: `class EvidenceCandidate:`
- `src/rie/application/evidence_candidate.py` line 35: `source_id: str`
- `src/rie/application/evidence_candidate.py` line 36: `source_type: str`
- `src/rie/application/evidence_candidate.py` line 37: `source_checksum_algorithm: str`
- `src/rie/application/evidence_candidate.py` line 38: `source_checksum: str`
- `src/rie/application/evidence_candidate.py` line 39: `source_authority: str`
- `src/rie/application/evidence_candidate.py` line 40: `source_lifecycle_state: str`
- `src/rie/application/evidence_candidate.py` line 41: `source_reference: str`
- `src/rie/application/evidence_candidate.py` line 42: `execution_id: str`
- `src/rie/application/evidence_candidate.py` line 43: `producer_name: str`
- `src/rie/application/evidence_candidate.py` line 44: `producer_version: str`
- `src/rie/application/evidence_candidate.py` line 45: `result_contract_version: str`
- `src/rie/application/evidence_candidate.py` line 46: `execution_timestamp: str`
- `src/rie/application/evidence_candidate.py` line 47: `payload_type: str`
- `src/rie/application/evidence_candidate.py` line 48: `raw_payload: str`
- `src/rie/application/evidence_candidate.py` line 49: `locator: tuple[tuple[str, str \| int \| float], ...]`
- `src/rie/application/evidence_candidate.py` line 50: `warnings: tuple[str, ...]`
- `src/rie/application/evidence_candidate.py` line 51: `errors: tuple[str, ...]`
- `src/rie/application/evidence_candidate.py` line 52: `candidate_contract_version: str`
- `src/rie/application/evidence_candidate.py` line 136: `field_name: str,`
- `src/rie/application/evidence_candidate.py` line 137: `value: str,`
- `src/rie/application/evidence_candidate.py` line 138: `pattern: re.Pattern[str],`
- `src/rie/application/evidence_candidate.py` line 174: `pairs: list[tuple[str, object]],`
- `src/rie/application/evidence_candidate.py` line 220: `locator: tuple[tuple[str, str \| int \| float], ...],`
- `src/rie/application/evidence_candidate.py` line 309: `field_name: str,`
- `src/rie/application/evidence_candidate.py` line 310: `diagnostics: tuple[str, ...],`

### 4.2 Existing generic Evidence shape

- `src/evidence/evidence.py` line 8: `@dataclass(frozen=True)`
- `src/evidence/evidence.py` line 9: `class Evidence:`
- `src/evidence/evidence.py` line 10: `asset_path: Path`
- `src/evidence/evidence.py` line 11: `filename: str`
- `src/evidence/evidence.py` line 12: `metadata: Metadata`
- `src/evidence/evidence.py` line 13: `analysis: AssetAnalysis`

### 4.3 Existing EvidenceBuilder behavior

- `src/evidence/evidence_builder.py` line 8: `class EvidenceBuilder:`
- `src/evidence/evidence_builder.py` line 11: `def build(`
- `src/evidence/evidence_builder.py` line 17: `return Evidence(`

### 4.4 Existing text-extraction Evidence shape

- `src/evidence/text_extraction_evidence.py` line 4: `@dataclass(frozen=True)`
- `src/evidence/text_extraction_evidence.py` line 5: `class TextExtractionEvidence:`
- `src/evidence/text_extraction_evidence.py` line 6: `source_path: str`
- `src/evidence/text_extraction_evidence.py` line 7: `content: str`
- `src/evidence/text_extraction_evidence.py` line 8: `size_bytes: int`

### 4.5 Existing PDF-text-extraction Evidence shape

- `src/evidence/pdf_text_extraction_evidence.py` line 4: `@dataclass(frozen=True)`
- `src/evidence/pdf_text_extraction_evidence.py` line 5: `class PdfTextExtractionEvidence:`
- `src/evidence/pdf_text_extraction_evidence.py` line 6: `source_path: str`
- `src/evidence/pdf_text_extraction_evidence.py` line 7: `content: str`
- `src/evidence/pdf_text_extraction_evidence.py` line 8: `size_bytes: int`
- `src/evidence/pdf_text_extraction_evidence.py` line 9: `page_number: int`
- `src/evidence/pdf_text_extraction_evidence.py` line 10: `extraction_index: int`
- `src/evidence/pdf_text_extraction_evidence.py` line 11: `extraction_method: str`
- `src/evidence/pdf_text_extraction_evidence.py` line 12: `warnings: list[str]`
- `src/evidence/pdf_text_extraction_evidence.py` line 13: `evidence_index: int`

### 4.6 Official-source authority, lifecycle, and eligibility foundations

- `src/official_source/official_source.py` line 28: `class AuthorityStatus(Enum):`
- `src/official_source/official_source.py` line 36: `class LifecycleStatus(Enum):`
- `src/official_source/official_source.py` line 45: `class EvidenceEligibility(Enum):`
- `src/official_source/official_source.py` line 72: `class OfficialSource:`
- `src/official_source/official_source.py` line 73: `source_id: str`
- `src/official_source/official_source.py` line 74: `source_path: str`
- `src/official_source/official_source.py` line 75: `source_type: SourceType`
- `src/official_source/official_source.py` line 76: `document_classification: DocumentClassification`
- `src/official_source/official_source.py` line 77: `authority_status: AuthorityStatus`
- `src/official_source/official_source.py` line 78: `lifecycle_status: LifecycleStatus`
- `src/official_source/official_source.py` line 79: `evidence_eligibility: EvidenceEligibility`
- `src/official_source/official_source.py` line 80: `version: str \| None`
- `src/official_source/official_source.py` line 81: `review_notes: str \| None`

### 4.7 Eligibility, preflight, and workflow contracts

- `src/official_source/official_source_evidence_eligibility_policy.py` line 7: `@dataclass(frozen=True)`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 8: `class EvidenceEligibilityDecision:`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 9: `source_id: str`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 10: `evidence_eligibility: EvidenceEligibility`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 11: `allowed: bool`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 12: `requires_review: bool`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 13: `reason: str`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 16: `class OfficialSourceEvidenceEligibilityPolicy:`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 19: `def evaluate(`
- `src/official_source/official_source_evidence_eligibility_policy.py` line 20: `source: OfficialSource,`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 8: `@dataclass(frozen=True)`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 9: `class EvidenceEligibilityGateResult:`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 10: `source_id: str`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 11: `allowed: bool`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 12: `requires_review: bool`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 13: `reason: str`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 16: `class EvidenceEligibilityGate:`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 19: `def check(`
- `src/official_source/official_source_evidence_eligibility_gate.py` line 20: `decision: EvidenceEligibilityDecision,`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 8: `@dataclass(frozen=True)`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 9: `class EvidenceWorkflowPreflightResult:`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 10: `source_id: str`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 11: `evidence_collection_allowed: bool`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 12: `requires_review: bool`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 13: `reason: str`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 16: `class EvidenceWorkflowPreflight:`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 19: `def check(`
- `src/official_source/official_source_evidence_workflow_preflight.py` line 20: `gate_result: EvidenceWorkflowGateResult,`
- `src/official_source/official_source_evidence_workflow_gate.py` line 8: `@dataclass(frozen=True)`
- `src/official_source/official_source_evidence_workflow_gate.py` line 9: `class EvidenceWorkflowGateResult:`
- `src/official_source/official_source_evidence_workflow_gate.py` line 10: `source_id: str`
- `src/official_source/official_source_evidence_workflow_gate.py` line 11: `workflow_allowed: bool`
- `src/official_source/official_source_evidence_workflow_gate.py` line 12: `requires_review: bool`
- `src/official_source/official_source_evidence_workflow_gate.py` line 13: `reason: str`
- `src/official_source/official_source_evidence_workflow_gate.py` line 16: `class EvidenceWorkflowGate:`
- `src/official_source/official_source_evidence_workflow_gate.py` line 19: `def check(`
- `src/official_source/official_source_evidence_workflow_gate.py` line 20: `gate_result: EvidenceEligibilityGateResult,`

These observations are read-only evidence. Existing names and builders do not automatically establish the authoritative accepted-Evidence contract.

## 5. Authoritative type and ownership

The future authoritative accepted-Evidence type is:

- Name: `AcceptedEvidence`
- Ownership: RIE domain
- Intended module ownership: `src/rie/domain/accepted_evidence.py`
- Mutability: immutable
- Construction: only through an explicit application-layer materialization service
- Persistence: outside the contract and not authorized by this gate
- Knowledge coupling: prohibited

The current files under `src/evidence` remain compatibility or historical shapes until a later migration review. They are not silently renamed or promoted.

`EvidenceCandidate` remains in the application layer and is not moved into the domain.

## 6. AcceptedEvidence top-level contract

The accepted-Evidence contract contains exactly these top-level fields:

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `evidence_id` | `str` | Yes | Deterministic factual Evidence identity supplied by the approved identity boundary |
| `contract_version` | `str` | Yes | Accepted-Evidence contract version |
| `candidate_reference` | `EvidenceCandidateReference` | Yes | Immutable link to the originating candidate snapshot |
| `source_snapshot` | `EvidenceSourceSnapshot` | Yes | Source authority/lifecycle/content snapshot at acceptance time |
| `producer_snapshot` | `EvidenceProducerSnapshot` | Yes | Producer and producer-contract identity |
| `factual_payload` | `EvidencePayload` | Yes | Immutable factual payload, schema, digest, and locator |
| `provenance` | `EvidenceProvenance` | Yes | Traceability and lineage record |
| `eligibility_result` | `AcceptedEligibilityResult` | Yes | Explicit successful eligibility decision |
| `materialization_record` | `EvidenceMaterializationRecord` | Yes | Auditable construction record |
| `diagnostics` | `tuple[EvidenceDiagnostic, ...]` | Yes | Immutable warnings and informational diagnostics; may be empty |

No optional top-level fields and no default values are approved.

## 7. EvidenceCandidateReference contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `candidate_contract_version` | `str` | Yes | Non-empty supported version |
| `candidate_snapshot_digest` | `str` | Yes | Digest of the complete canonical candidate snapshot |
| `candidate_source_id` | `str` | Yes | Must equal the source snapshot source identifier |
| `candidate_producer_name` | `str` | Yes | Must equal the producer snapshot producer name |
| `candidate_producer_version` | `str` | Yes | Must equal the producer snapshot producer version |
| `candidate_payload_digest` | `str` | Yes | Must equal the factual payload digest |

This is a reference contract, not a second mutable copy of `EvidenceCandidate`.

The candidate snapshot digest is not the accepted-Evidence identity.

## 8. EvidenceSourceSnapshot contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `source_id` | `str` | Yes | Stable source registry identifier |
| `source_path` | `str` | Yes | Traceability only; never authority or identity by itself |
| `source_type` | `str` | Yes | Explicit supported source type value |
| `document_classification` | `str` | Yes | Explicit classification snapshot |
| `authority_status` | `str` | Yes | Explicit authority snapshot |
| `lifecycle_status` | `str` | Yes | Explicit lifecycle snapshot |
| `evidence_eligibility` | `str` | Yes | Source-level eligibility declaration snapshot |
| `source_content_digest` | `str` | Yes | Content fingerprint used for factual identity inputs |

Path existence is not validated by this immutable contract.

Authority is not inferred from directory location, filename, extension, or recency.

## 9. EvidenceProducerSnapshot contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `producer_name` | `str` | Yes | Stable producer name |
| `producer_version` | `str` | Yes | Explicit producer implementation or contract version |
| `producer_kind` | `str` | Yes | Controlled producer category |
| `producer_contract_version` | `str` | Yes | Version of the producer-output contract |

The producer snapshot contains no runtime object, callable, filesystem handle, parser, or dependency instance.

## 10. EvidencePayload contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `payload_type` | `str` | Yes | Controlled factual payload type |
| `payload_schema_version` | `str` | Yes | Explicit supported schema version |
| `payload` | immutable scalar, tuple, or immutable mapping representation | Yes | Factual value only; no business interpretation |
| `payload_digest` | `str` | Yes | Digest of canonical factual payload |
| `locator` | `EvidenceLocator` | Yes | Reproducible source locator |

The payload must not contain:

- Knowledge summaries;
- product or brand decisions;
- persona or creative judgments;
- Prompt Candidate content;
- generator instructions;
- mutable runtime objects;
- parser handles;
- repository handles;
- filesystem streams.

## 11. EvidenceLocator contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `locator_type` | `str` | Yes | Controlled locator category |
| `locator_value` | immutable scalar or tuple | Yes | Exact reproducible location |
| `locator_schema_version` | `str` | Yes | Explicit schema version |

Examples may include page/index/span/field coordinates, but this gate does not authorize PDF parsing or asset execution.

A source path alone is not a sufficient Evidence locator.

## 12. EvidenceProvenance contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `collection_id` | `str` | Yes | Stable collection or workflow reference |
| `producer_output_digest` | `str` | Yes | Digest of the complete producer output used by the candidate |
| `lineage` | `tuple[str, ...]` | Yes | Ordered immutable lineage identifiers; may not be empty |
| `observed_at` | timezone-aware timestamp | Yes | Audit metadata only; excluded from factual identity |
| `source_registry_version` | `str` | Yes | Registry/configuration version used during review |

Timestamps support audit. They do not establish factual identity or duplicate status.

## 13. AcceptedEligibilityResult contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `decision` | literal `eligible` | Yes | Any other decision blocks materialization |
| `policy_id` | `str` | Yes | Stable policy identity |
| `policy_version` | `str` | Yes | Explicit version |
| `candidate_snapshot_digest` | `str` | Yes | Must match `candidate_reference` |
| `source_id` | `str` | Yes | Must match `source_snapshot` |
| `reason_codes` | `tuple[str, ...]` | Yes | Must contain at least one explicit acceptance reason |
| `evaluated_at` | timezone-aware timestamp | Yes | Audit metadata only |
| `evaluated_by` | `str` | Yes | Explicit policy/service/reviewer identity |
| `diagnostics` | `tuple[EvidenceDiagnostic, ...]` | Yes | Must not contain error-severity diagnostics |

This result is distinct from source-level `EvidenceEligibility` configuration and distinct from workflow preflight/gate status.

## 14. EvidenceMaterializationRecord contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `materializer_id` | `str` | Yes | Stable materializer identity |
| `materializer_version` | `str` | Yes | Explicit version |
| `materialized_at` | timezone-aware timestamp | Yes | Audit metadata; excluded from factual identity |
| `acceptance_record_id` | `str` | Yes | Governance record identity distinct from `evidence_id` |
| `accepted_by` | `str` | Yes | Explicit service or reviewer identity |
| `acceptance_reason` | `str` | Yes | Non-empty human-readable reason |
| `review_record_id` | `str` | Yes | Stable review trace |
| `identity_policy_id` | `str` | Yes | Identity policy used to supply `evidence_id` |
| `identity_policy_version` | `str` | Yes | Identity policy version |

Materialization does not generate identity silently. It receives a validated identity result from the later approved identity boundary.

## 15. EvidenceDiagnostic contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `code` | `str` | Yes | Stable machine-readable code |
| `severity` | `info` or `warning` | Yes | Error severity is forbidden in successful accepted Evidence |
| `message` | `str` | Yes | Non-empty diagnostic text |
| `field` | `str` | Yes | Affected field or boundary |
| `source` | `str` | Yes | Producer, policy, validator, or materializer origin |

Diagnostics are audit information. Diagnostic ordering and timestamps must not silently change factual identity.

## 16. Validation boundary

The immutable contract validates only structural invariants:

- all required fields exist;
- strings are non-empty after trimming;
- tuples and nested contracts have correct types;
- cross-field identifiers and digests agree;
- eligibility decision is exactly `eligible`;
- no error-severity diagnostic exists;
- versions and policy identifiers are explicit;
- payload and locator are immutable representations;
- timestamps are timezone-aware;
- identity fields are supplied and non-empty.

The immutable contract must not:

- read the filesystem;
- parse PDFs or images;
- access networks;
- inspect repository state;
- query a database;
- calculate identity;
- calculate payload/source digests;
- infer authority;
- infer Knowledge;
- resolve conflicts;
- write persistence;
- use AI or LLM inference;
- call clocks internally to fill missing values.

All values are supplied explicitly.

## 17. Materialization input boundary

The future application service receives exactly:

1. one immutable `EvidenceCandidate`;
2. one explicit successful eligibility result;
3. one validated deterministic identity result;
4. one explicit materialization context containing reviewer/service identity and audit timestamp.

It may produce one `EvidenceMaterializationResult`.

It must not receive:

- a repository adapter;
- database session;
- parser;
- filesystem handle;
- Knowledge builder;
- Prompt Candidate builder;
- AI client;
- hidden global policy;
- implicit clock;
- random identifier generator.

## 18. EvidenceMaterializationResult contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `status` | `materialized` or `rejected` | Yes | Explicit result |
| `accepted_evidence` | `AcceptedEvidence` or null | Yes | Present only when materialized |
| `reason_codes` | `tuple[str, ...]` | Yes | Explicit success or rejection reasons |
| `diagnostics` | `tuple[EvidenceDiagnostic, ...]` | Yes | Complete immutable diagnostics |

Invariants:

- `materialized` requires one `AcceptedEvidence` and no error diagnostics;
- `rejected` requires null accepted Evidence and at least one rejection reason;
- the result performs no repository write;
- the result does not construct Knowledge.

## 19. Materialization preconditions

Materialization succeeds only when all conditions hold:

1. candidate contract version is supported;
2. candidate snapshot is immutable and complete;
3. eligibility decision is exactly `eligible`;
4. eligibility candidate digest matches the candidate reference digest;
5. eligibility source identifier matches the source snapshot;
6. source authority/lifecycle/eligibility snapshots are explicit;
7. producer contract version is supported;
8. payload type and schema version are supported;
9. source content digest and payload digest are present;
10. locator is structurally valid and reproducible;
11. deterministic identity result references the same canonical identity inputs;
12. identity policy identifier/version is supported;
13. no error diagnostic exists;
14. materialization context is explicit;
15. no repository, parser, filesystem, network, AI, Knowledge, or Prompt dependency is present.

## 20. Materialization rejection codes

The future boundary uses explicit reason codes, including:

- `candidate_contract_unsupported`
- `candidate_snapshot_incomplete`
- `candidate_reference_mismatch`
- `eligibility_decision_not_eligible`
- `eligibility_policy_unsupported`
- `eligibility_reference_mismatch`
- `source_snapshot_incomplete`
- `source_authority_not_accepted`
- `source_lifecycle_not_accepted`
- `payload_type_unsupported`
- `payload_schema_unsupported`
- `payload_digest_missing`
- `source_content_digest_missing`
- `locator_invalid`
- `identity_result_missing`
- `identity_reference_mismatch`
- `identity_policy_unsupported`
- `error_diagnostic_present`
- `materialization_context_incomplete`

No exception swallowing, hidden fallback, automatic retry, or partial accepted Evidence is permitted.

## 21. Factual identity versus governance identity

Two identities remain separate:

### Factual `evidence_id`

Represents the factual Evidence and stable provenance inputs.

Candidate identity inputs for later review:

- accepted-Evidence contract version;
- source identifier;
- source content digest;
- producer name/version/kind/contract version;
- payload type/schema version/digest;
- canonical locator;
- producer output digest.

Excluded from factual identity:

- source path alone;
- authority/lifecycle status;
- eligibility decision;
- policy decision timestamps;
- materialization timestamp;
- acceptance actor;
- review record;
- diagnostic message wording;
- repository location;
- Knowledge or Prompt content.

### Governance `acceptance_record_id`

Represents the acceptance event and governance context.

Its exact identity algorithm is deferred to the next gate.

## 22. Compatibility classification

| Existing shape | PR-023C treatment |
|---|---|
| `src/rie/application/evidence_candidate.py` | Retained as immutable application input DTO |
| `src/evidence/evidence.py` | Historical/generic compatibility shape; not authoritative accepted Evidence |
| `src/evidence/evidence_builder.py` | Historical builder; no automatic promotion path |
| `TextExtractionEvidence` | Producer-specific factual shape; may be source material for candidate creation only |
| `PdfTextExtractionEvidence` | Producer-specific factual shape; may be source material for candidate creation only |
| Evidence collections/collectors | Collection/transport behavior; not repository authority |
| Official-source eligibility policy/gate/preflight/workflow | Eligibility foundations; not accepted Evidence |
| Existing Knowledge modules | Outside materialization boundary |
| Existing Prompt modules | Outside materialization boundary |

No file is deprecated, renamed, moved, or modified by this gate.

## 23. Layer ownership

| Concern | Owner |
|---|---|
| `EvidenceCandidate` | Application layer |
| Source authority/lifecycle models | Official-source/domain boundary |
| Eligibility result | Explicit reviewed application/domain contract |
| `AcceptedEvidence` | RIE domain |
| Materialization orchestration | Application service |
| Deterministic identity | Separate policy/service reviewed next |
| Repository interface | Later application/domain-facing contract |
| Persistence adapter | Later infrastructure adapter |
| Knowledge construction | Later phase after Evidence prerequisites |
| Prompt Candidate | Downstream of validated Knowledge only |

## 24. Options reviewed

### Option A — Reuse generic `Evidence` as accepted Evidence

**Rejected.** The observed shape is too small and does not carry the required governance, provenance, eligibility, and identity boundaries.

### Option B — Promote text/PDF extraction Evidence directly

**Rejected.** Producer-specific extraction forms cannot be the authoritative accepted-Evidence domain contract.

### Option C — Extend `EvidenceCandidate` until it becomes accepted Evidence

**Rejected.** This collapses application candidate and accepted domain Evidence.

### Option D — Let the repository construct accepted Evidence

**Rejected.** Persistence must not own eligibility, identity, or materialization semantics.

### Option E — Approve a new immutable `AcceptedEvidence` contract and separate materialization result

**Selected.** This preserves domain, application, identity, and repository boundaries.

## 25. Final architecture decision

# ACCEPTED EVIDENCE CONTRACT BOUNDARY APPROVED; IMPLEMENTATION DEFERRED

The accepted-Evidence contract and materialization boundary are approved at documentation level.

Implementation is not authorized because deterministic factual identity, governance acceptance identity, duplicate classification, replay behavior, collision handling, and repository idempotency are not yet approved.

## 26. Exact next safe gate

**PR-023D - Deterministic Evidence Identity and Idempotency Contract Review**

Type: **Documentation-only**

The next gate must define, without coding:

1. canonical factual identity inputs;
2. canonical serialization rules;
3. digest algorithm and versioning;
4. factual `evidence_id` format;
5. governance `acceptance_record_id` identity;
6. exact replay versus duplicate versus collision classification;
7. idempotent no-op behavior;
8. conflict and supersession boundaries;
9. repository key requirements without implementing a repository;
10. exactly one final decision and one next review-only gate.

## 27. Acceptance assessment

| Acceptance area | Result |
|---|---|
| PR-023B commit/push checkpoint | PASSED |
| Phase 22 branch/tag preservation | PASSED |
| Sandbox/temp preservation | PASSED |
| Read-only contract inspection | PASSED |
| Authoritative type ownership | PASSED |
| Exact top-level accepted-Evidence fields | PASSED |
| Exact nested contract fields | PASSED |
| Structural validation boundary | PASSED |
| Materialization input/result boundary | PASSED |
| Preconditions and rejection codes | PASSED |
| Factual/governance identity separation | PASSED |
| Compatibility classification | PASSED |
| Layer ownership | PASSED |
| Five architecture options | PASSED |
| Exactly one final decision | PASSED — `ACCEPTED EVIDENCE CONTRACT BOUNDARY APPROVED; IMPLEMENTATION DEFERRED` |
| Exactly one next review-only gate | PASSED |
| Code/test/asset boundary | PASSED |

## 28. Action truth table

| Action | Performed |
|---|---|
| Read-only checkpoint verification | True |
| Read-only exact-file contract inspection | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project Python interpreter executed | False |
| Dependency/venv/pyproject/config changed | False |
| PDF/image/OCR/parser/ingestion executed | False |
| Real asset processed | False |
| Accepted Evidence created | False |
| Materializer created | False |
| Identity service created | False |
| EvidenceRepository or persistence created | False |
| Knowledge or Prompt Candidate created | False |
| AI/LLM inference executed | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/history rewrite performed | False |
| Tag action performed | False |
| Automatic retry performed | False |

## 29. Gate conclusion

PR-023C concludes **ACCEPTED EVIDENCE CONTRACT BOUNDARY APPROVED; IMPLEMENTATION DEFERRED**.

Only `PR-023D - Deterministic Evidence Identity and Idempotency Contract Review` is recommended. No production implementation is authorized.
