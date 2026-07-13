# PR-025A — Knowledge Construction Boundary and Dependency Review

## 1. Review identity and repository checkpoint

| Item | Reviewed value |
|---|---|
| Review | PR-025A |
| Type | Review-only and documentation-only |
| Repository | `D:\PROJECT\RIE` |
| Expected branch | `phase-025-knowledge-construction` |
| Observed branch | `phase-025-knowledge-construction` |
| Required and observed HEAD | `07e3266b2eed501895ab286739def4490b3748bf` |
| Official completed phase tag | `v0.24.0-rcis-accepted-evidence-implementation-phase` |
| Tag target | `07e3266b2eed501895ab286739def4490b3748bf` |
| Inherited verified regression | `1581 passed` |
| Tests executed by this review | None |

The required commit and official Phase 24 tag are present and agree. The branch checkpoint was corrected to `phase-025-knowledge-construction` and independently verified at the required commit before commit. This review does not switch branches, stage, commit, or otherwise mutate Git state.

The required non-collapsible chain is:

```text
Repository
-> Repository Explorer
-> RepositoryExploration
-> EvidenceCollection
-> Evidence
-> AcceptedEvidence
-> Knowledge Construction
-> Knowledge
-> Knowledge Repository
-> Prompt Candidate
-> RCIS
```

For the first implementation slice, `KnowledgeCandidate` is the explicit reviewable output of Knowledge Construction on the path to governed `Knowledge`. It is not Accepted Evidence, reviewed Knowledge, accepted Knowledge, a business decision, or a Prompt Candidate.

## 2. Existing Knowledge-related inventory

### 2.1 Current Phase 24 foundations under `src/rie`

| Layer | Existing foundation | Knowledge assessment |
|---|---|---|
| Domain | `rie.domain.accepted_evidence.AcceptedEvidence` and nested immutable contracts | Current authoritative upstream fact contract |
| Domain | `rie.domain.evidence_identity` | Current deterministic Evidence identity; must not be reused as Knowledge identity |
| Domain | `rie.domain.acceptance_record.AcceptanceRecord` | Current immutable acceptance-governance record |
| Domain | `rie.domain.acceptance_identity` | Current deterministic acceptance-record identity |
| Application | `rie.application.evidence_materializer` | Current explicit candidate-to-AcceptedEvidence gate; not a Knowledge builder |
| Interface | `rie.interfaces.evidence_repository.EvidenceRepository` | Current retrieval boundary for accepted Evidence and acceptance records |
| Infrastructure | in-memory and SQLite EvidenceRepository adapters plus serialization | Current accepted-Evidence persistence only; not Knowledge persistence |
| CLI namespace | `src/rie/knowledge/*` | Legacy export/inspection command wrappers, not a current domain or application Knowledge boundary |

There is no current Knowledge domain contract in `src/rie/domain`, no Knowledge construction service in `src/rie/application`, no Knowledge repository protocol in `src/rie/interfaces`, and no Knowledge persistence adapter in `src/rie/infrastructure`.

### 2.2 Legacy top-level Knowledge implementation

| Path/type | Existing behavior | Status for Phase 25 |
|---|---|---|
| `knowledge.TextKnowledge` | Carries `source_path`, raw `content`, `size_bytes`, and positional `evidence_index` | Legacy and incompatible |
| `knowledge.TextKnowledgeBuilder` | Converts an untyped dictionary directly into `TextKnowledge` | Legacy; bypasses AcceptedEvidence and acceptance records |
| `knowledge.OfficialKnowledgeSourceItem` | Accepts manually supplied content, nullable ID, page/index hints, nullable status and governance level | Legacy input DTO; incomplete governance |
| `knowledge.OfficialKnowledgeItem` | Copies the source item and adds a positional index | Legacy artifact type; not deterministic domain identity |
| `knowledge.OfficialKnowledgeCollector` | Performs list-order copying without eligibility, provenance, identity, review, or conflict rules | Legacy and unsafe for Phase 25 construction |
| legacy serializers/inspectors/collections | Validate artifact shapes and support exports | Compatibility surfaces only |

The legacy types are frozen compatibility surfaces for this phase. They must not be renamed, retrofitted, deleted, imported, or used as the new construction output in the minimal implementation PR.

### 2.3 Existing Prompt Candidate implementation

`prompting.TextPromptCandidateBuilder` consumes the legacy four-field Knowledge dictionary and produces `TextPromptCandidate` with positional `evidence_index` and `knowledge_index`. It is a historical downstream pipeline, not evidence that reviewed Knowledge exists. All `src/prompting`, `src/rie/prompt`, and related tests remain deferred.

### 2.4 Existing test foundations

Current focused Phase 24 coverage exists in:

- `tests/domain/test_accepted_evidence.py`;
- `tests/domain/test_evidence_identity.py`;
- `tests/domain/test_acceptance_record.py`;
- `tests/domain/test_acceptance_identity.py`;
- `tests/application/test_evidence_materializer.py`;
- `tests/interfaces/test_evidence_repository.py`;
- `tests/infrastructure/test_evidence_repository_serialization.py`;
- `tests/infrastructure/test_in_memory_evidence_repository.py`;
- `tests/infrastructure/test_sqlite_evidence_repository.py`.

Legacy Knowledge tests under `tests/knowledge` and top-level `tests/test_*knowledge*` protect historical behavior but do not establish the Phase 25 contract. There are no current tests under `tests/domain` or `tests/application` for governed Knowledge construction.

### 2.5 Configuration and dependencies

`pyproject.toml` exposes `src` packages, requires Python 3.12 or later, and declares only `pypdf`. Minimal Knowledge construction requires no new dependency, configuration, database, asset, parser, CLI, or framework.

## 3. Current accepted-Evidence input contract

The exact authoritative upstream object is the frozen `rie.domain.accepted_evidence.AcceptedEvidence` dataclass:

| Field | Contract |
|---|---|
| `evidence_id` | Stable accepted-Evidence identity |
| `contract_version` | Accepted-Evidence schema version |
| `candidate_reference` | Candidate contract version, snapshot digest, source ID, producer name/version, payload digest |
| `source_snapshot` | Source ID/path/type, classification, authority status, lifecycle status, eligibility label, source-content digest |
| `producer_snapshot` | Producer name/version/kind/contract version |
| `factual_payload` | Payload type/schema/value/digest and immutable locator |
| `provenance` | Collection ID, producer-output digest, non-empty lineage, observation time, source-registry version |
| `eligibility_result` | Exact eligible decision, policy ID/version, candidate digest, source ID, reasons, evaluation time/actor, diagnostics |
| `materialization_record` | Materializer ID/version/time, acceptance-record ID, accepting actor/reason, review-record ID, Evidence identity policy ID/version |
| `diagnostics` | Immutable informational/warning diagnostics |

The locator provides `locator_type`, immutable `locator_value`, and `locator_schema_version`; it is the authoritative page, extraction, section, or other producer-defined location when available. `source_snapshot.source_content_digest` is the authoritative accepted snapshot checksum. No constructor may recover these values from a path, asset read, or legacy index.

The separate frozen `AcceptanceRecord` supplies `acceptance_record_id`, `evidence_id`, accepting actor/reason/time, `review_record_id`, acceptance policy ID/version, Evidence identity policy ID/version, materializer ID/version, and diagnostics. The Phase 24 repository can retrieve accepted Evidence and list its acceptance records in stable ID order.

The first Knowledge constructor must receive exact in-memory `AcceptedEvidence` and `AcceptanceRecord` objects. Repository lookup orchestration is not part of the constructor and is deferred. A caller may obtain these objects through `EvidenceRepository`, but PR-025B must remain repository-agnostic and side-effect free.

## 4. Gap analysis

| Required capability | Current state | Gap decision |
|---|---|---|
| Eligible accepted-Evidence input | Implemented in Phase 24 | Reuse without redesign |
| Stable Evidence and acceptance identities | Implemented | Reference; do not duplicate or weaken |
| Knowledge construction output | No current governed type | Add a new immutable `KnowledgeCandidate` |
| Knowledge identity | Only legacy nullable/manual IDs or positional indexes | Add deterministic candidate identity policy |
| Complete Knowledge provenance | Legacy types keep only paths/pages/indexes | Add typed accepted-Evidence support references |
| Construction rule | Legacy builders copy dictionaries | Add one explicit, versioned, payload-constrained rule |
| Knowledge authority | Legacy nullable strings | Emit `unassessed`; never inherit source authority automatically |
| Lifecycle/review | No authoritative state machine | Emit only `candidate` and `pending_review`; transitions deferred |
| Conflict handling | No current explicit representation | Emit `not_assessed`; retain support independently; never select a winner |
| Knowledge persistence | Absent | Correctly deferred |
| Prompt Candidate boundary | Legacy direct coupling exists | Keep frozen and disconnected |

No exact defect was found in the Phase 24 contracts. They must not be redesigned in PR-025B.

## 5. Proposed minimal Knowledge Construction contract

The initial output must be a new `rie.domain.knowledge_candidate.KnowledgeCandidate`, not legacy `TextKnowledge`, `OfficialKnowledgeItem`, or final `Knowledge`.

Producing final `Knowledge` would imply a completed authority review, lifecycle transition, conflict assessment, and acceptance decision. Those governance actions are intentionally absent from the minimal deterministic constructor. `KnowledgeCandidate` is therefore the smallest honest domain result: constructed, immutable, traceable, and pending explicit review.

The application boundary should expose:

```text
KnowledgeConstructionRequest
  accepted_evidence: AcceptedEvidence
  acceptance_records: tuple[AcceptanceRecord, ...]
  construction_rule_id: "rcis-accepted-text-verbatim"
  construction_rule_version: "1.0.0"

construct_knowledge_candidate(request)
  -> KnowledgeConstructionResult
```

The result must be explicit rather than exception-driven for supported business rejection:

```text
decision: "constructed" | "rejected"
knowledge_candidate: KnowledgeCandidate | None
reason_codes: tuple[str, ...]
diagnostics: tuple[KnowledgeDiagnostic, ...]
```

Malformed programming inputs may raise `ValueError`; valid but unsupported or incompatible accepted Evidence must return a rejected result without a candidate.

The constructor must not accept `EvidenceCandidate`, raw dictionaries, filesystem paths, repository IDs without resolved objects, legacy Evidence, extraction output, or arbitrary duck-typed substitutes.

## 6. Proposed data fields

### 6.1 `KnowledgeCandidate`

| Field | Purpose |
|---|---|
| `knowledge_candidate_id` | Deterministic `kc1_<sha256>` identity |
| `contract_version` | Exact candidate contract version |
| `statement_type` | Initial exact value `verbatim_text_fact` |
| `statement` | Non-empty accepted text copied byte-for-code-point without semantic rewriting |
| `support` | Non-empty tuple of exact `KnowledgeEvidenceSupport` values; one in PR-025B |
| `construction_rule_id` | Exact rule identity |
| `construction_rule_version` | Exact rule version |
| `authority_status` | Exact initial value `unassessed` |
| `lifecycle_status` | Exact initial value `candidate` |
| `review_status` | Exact initial value `pending_review` |
| `conflict_status` | Exact initial value `not_assessed` |
| `conflict_ids` | Empty immutable tuple in PR-025B |
| `diagnostics` | Immutable informational/warning diagnostics only |

Do not add a construction timestamp to candidate identity. If a non-identity observation timestamp is later required, it needs a separate reviewed contract; PR-025B does not need it.

### 6.2 `KnowledgeEvidenceSupport`

| Field | Preserved value |
|---|---|
| `evidence_id` | `AcceptedEvidence.evidence_id` |
| `acceptance_record_ids` | Unique, lexicographically ordered IDs for supplied matching records |
| `acceptance_review_record_ids` | Unique, lexicographically ordered review IDs from those records |
| `source_id` | `source_snapshot.source_id` |
| `source_content_digest` | `source_snapshot.source_content_digest` |
| `source_authority_status` | Snapshot only; not promoted to candidate authority |
| `source_lifecycle_status` | Snapshot only; not promoted to candidate lifecycle |
| `payload_digest` | `factual_payload.payload_digest` |
| `locator_type` | `factual_payload.locator.locator_type` |
| `locator_value` | Exact immutable locator value |
| `locator_schema_version` | `factual_payload.locator.locator_schema_version` |

The candidate does not need to duplicate the full accepted payload or acceptance records because their stable IDs and digests provide durable references. The statement is the one deliberately constructed value. Callers and later reviewers resolve complete upstream records through the EvidenceRepository.

## 7. Deterministic identity recommendation

Define a separate Knowledge-candidate identity policy:

```text
policy_id: rcis-knowledge-candidate-identity
policy_version: 1.0.0
canonicalization_contract: knowledge-candidate-json-v1
digest_algorithm: sha256
id_prefix: kc1_
```

Canonical identity input must contain only:

1. candidate contract version;
2. statement type and exact statement;
3. construction rule ID and version;
4. the ordered support projection: Evidence ID, ordered acceptance-record IDs, source ID, source-content digest, payload digest, and canonical locator;
5. initial authority, lifecycle, review, and conflict states.

Use UTF-8 canonical JSON with Unicode NFC normalization, lexicographically sorted object keys, fixed separators, no insignificant whitespace, and an explicit canonicalization version. Support and acceptance-record IDs are unique and lexicographically ordered before hashing. A replay of the same fact and rule must produce the same ID regardless of input record order.

Diagnostics, actor timestamps, Python object equality, list position, source path, and future review metadata are not identity inputs. A future change to statement content, supporting Evidence, source checksum, locator, rule version, or initial governance state creates a new candidate identity; historical candidates are not overwritten.

## 8. Construction-rule boundary

PR-025B implements exactly one deterministic rule: `rcis-accepted-text-verbatim` version `1.0.0`.

The rule constructs one candidate from one exact `AcceptedEvidence` when all conditions hold:

1. input objects are exact `AcceptedEvidence` and non-empty exact `AcceptanceRecord` tuple members;
2. every acceptance record references the same Evidence ID;
3. the acceptance record named by `materialization_record.acceptance_record_id` is present;
4. materialization and standalone acceptance fields agree for actor, reason, review record, materializer ID/version, and accepted/materialized time;
5. `eligibility_result.decision` is `eligible` as guaranteed by the accepted-Evidence contract;
6. `factual_payload.payload_type` is exactly `text`;
7. the immutable payload is exactly one mapping entry named `text` whose value is a non-empty string;
8. the candidate statement is that string unchanged;
9. provenance support is copied exactly;
10. initial governance states are fixed to `unassessed`, `candidate`, `pending_review`, and `not_assessed`.

No trimming, case folding, summarization, joining, deduplication by meaning, source ranking, authority propagation, inference, conflict detection, conflict resolution, or business interpretation is allowed. Unsupported payload types/schemas or shapes return an explicit rejection. This narrow text rule is sufficient to prove the boundary while structural metadata and multi-Evidence composition remain later rule versions or separate reviewed rules.

## 9. Provenance requirements

Complete minimum provenance means the candidate can be traced without asset rereads to:

- every supporting accepted Evidence ID;
- every supplied acceptance-record ID and its review-record ID;
- the accepted source ID;
- the exact source-content checksum;
- the factual payload digest;
- the exact page, extraction, section, or other locator when Phase 24 provides it;
- the construction rule ID and version;
- the Knowledge-candidate contract and identity-policy versions.

The constructor must reject missing, mismatched, duplicate, or unordered provenance rather than repair it silently. A locator is always preserved as typed upstream data; the constructor does not interpret whether its type means a page or extraction index.

## 10. Authority and lifecycle boundary

The source snapshot's authority and lifecycle values describe the accepted source at Evidence materialization time. They are provenance, not Knowledge governance decisions.

PR-025B may emit only:

| Concern | Initial state | Meaning |
|---|---|---|
| Authority | `unassessed` | No Knowledge authority decision has occurred |
| Lifecycle | `candidate` | Construction completed; no lifecycle promotion occurred |
| Review | `pending_review` | Human/governance review remains required |
| Conflict | `not_assessed` | Construction made no conflict claim |

Future reviewed states may include reviewed, accepted, locked, rejected, and superseded forms, but their transition inputs, actors, reasons, timestamps, replacement lineage, and audit rules belong to a later lifecycle review. PR-025B must not implement them or expose a mutable state-changing method.

## 11. Conflict representation

The minimal candidate includes `conflict_status="not_assessed"` and `conflict_ids=()`. This explicitly says conflict analysis did not occur; it does not claim that no conflict exists.

Each accepted Evidence item remains independently identifiable. The initial one-Evidence/one-candidate rule cannot hide a competing fact by input ordering or aggregation. A later conflict contract must use stable conflict IDs, reference all involved Knowledge-candidate and accepted-Evidence IDs, preserve each claim, and record an explicit review outcome. It must create a new immutable governance record or superseding Knowledge version, never mutate or overwrite historical facts.

## 12. Explicitly deferred scope

The following remain outside PR-025B:

- final or reviewed `Knowledge`;
- Knowledge authority decisions and propagation;
- lifecycle transitions, review decisions, acceptance, locking, rejection, and supersession;
- conflict detection, semantic comparison, conflict records, and conflict resolution;
- multi-Evidence composition and structural-metadata construction rules;
- `KnowledgeRepository`, serialization, database schema, migrations, and persistence adapters;
- EvidenceRepository lookup orchestration or runtime repository selection;
- changes to Phase 24 contracts, repositories, adapters, or schemas;
- legacy Knowledge migration, retrofit, rename, or deletion;
- Prompt Candidate creation or changes to legacy prompting modules;
- AI/local-model inference, summarization, classification, or embeddings;
- business decisions, brand claims, benefit invention, prioritization, or creative direction;
- runtime CLI integration, UI/dashboard/API integration, generator integration, and asset reads;
- configuration, dependencies, and production database paths.

## 13. Recommended smallest next implementation PR

**PR-025B — Minimal KnowledgeCandidate Construction Contract Implementation**

Recommended exact scope:

- `src/rie/domain/knowledge_candidate.py` — immutable candidate, support, diagnostic, and identity contract/policy;
- `src/rie/application/knowledge_constructor.py` — request, explicit result, compatibility validation, and the single verbatim-text rule;
- `tests/domain/test_knowledge_candidate.py` — domain and identity tests;
- `tests/application/test_knowledge_constructor.py` — deterministic construction/rejection/boundary tests.

No interface or infrastructure file is required. Keeping identity beside the small candidate contract avoids a ceremonial identity-only PR while preserving a separable policy API. If implementation makes either source file too large to review safely, stop and reassess file factoring within the same PR; do not widen layers.

After PR-025B, use one focused result review/commit and one full regression before Phase 25 closure. A separate architecture PR is required only when final Knowledge review/lifecycle or KnowledgeRepository work begins.

## 14. Exact focused test matrix

### 14.1 Domain tests — `tests/domain/test_knowledge_candidate.py`

| ID | Exact assertion |
|---|---|
| D01 | Valid candidate and support contracts are frozen and equality is value-based but identity is the explicit ID |
| D02 | Candidate requires `kc1_` plus exactly 64 lowercase hex characters |
| D03 | Required strings reject empty/whitespace values; tuples reject lists and wrong exact member types |
| D04 | Support requires valid `ev1_` Evidence ID, non-empty ordered unique `ar1_` IDs, and matching ordered unique review IDs |
| D05 | Source ID/checksum, payload digest, and locator are required and immutable |
| D06 | Candidate rejects empty support, duplicate support Evidence IDs, and non-canonical support ordering |
| D07 | Only initial states `unassessed`, `candidate`, `pending_review`, `not_assessed` are accepted in PR-025B |
| D08 | `not_assessed` requires empty conflict IDs; unsupported state combinations fail closed |
| D09 | Canonical projection is stable across repeated calls and Unicode-equivalent input normalizes identically |
| D10 | Canonical JSON has fixed keys/encoding/separators and computes `kc1_<sha256>` |
| D11 | Acceptance-record input ordering does not change identity after canonical ordering |
| D12 | Changing statement, Evidence ID, acceptance ID, source ID/checksum, payload digest, locator, rule version, or initial state changes identity |
| D13 | Diagnostics, source path, and non-identity timestamps are absent from the identity projection |
| D14 | Identity extraction requires an exact candidate/input contract, not a duck-typed substitute |

### 14.2 Application tests — `tests/application/test_knowledge_constructor.py`

| ID | Exact assertion |
|---|---|
| A01 | Exact valid text AcceptedEvidence plus matching AcceptanceRecord constructs one candidate |
| A02 | Statement is copied exactly with no trimming, case change, summarization, or normalization of visible content |
| A03 | Result preserves Evidence ID, all acceptance/review IDs, source ID/checksum, payload digest, and exact locator |
| A04 | Source authority/lifecycle remain provenance while candidate states remain fixed initial states |
| A05 | Exact replay returns the same candidate ID and content |
| A06 | Reordered matching acceptance records produce the same canonical candidate and ID |
| A07 | Missing materialization acceptance record returns explicit rejection and no candidate |
| A08 | Acceptance record for another Evidence ID returns explicit rejection and no candidate |
| A09 | Any materialization/acceptance compatibility mismatch returns explicit reason codes and no candidate |
| A10 | Unsupported payload type, schema, mapping shape, missing `text`, non-string text, or empty text returns explicit rejection |
| A11 | `EvidenceCandidate`, raw dictionary, legacy Evidence, extraction output, path, and duck-typed object are rejected |
| A12 | No repository, filesystem, network, parser, AI, CLI, Prompt, or legacy Knowledge import exists in the constructor source |
| A13 | No Knowledge authority propagation, conflict claim, review approval, lifecycle promotion, or automatic acceptance occurs |
| A14 | Input objects and tuples remain unchanged after construction and rejection |
| A15 | Multiple independent accepted facts construct independently; neither input order nor timestamp selects a winner |

Focused execution after implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/domain/test_knowledge_candidate.py tests/application/test_knowledge_constructor.py -q
```

## 15. Risks and stop conditions

Stop PR-025B and return to architecture review if any of the following occurs:

- the working branch is not the approved Phase 25 branch or is not based on the required Phase 24 commit;
- accepted input cannot remain exact `AcceptedEvidence` plus exact matching `AcceptanceRecord` values;
- an exact Phase 24 contract defect is found;
- construction requires raw paths, asset reads, extraction output, `EvidenceCandidate`, or legacy Knowledge;
- the supported text payload shape cannot be stated and tested without guessing producer semantics;
- authority, review, lifecycle, or conflict decisions are required to construct the candidate;
- final `Knowledge`, persistence, repository wiring, Prompt Candidate, AI, CLI, UI, generator, config, or dependency changes become necessary;
- deterministic identity would require time, list position, random values, source path, or mutable data;
- provenance cannot preserve accepted Evidence, acceptance, source checksum, and locator references completely;
- a conflict would be suppressed, ranked, merged, or overwritten;
- implementation scope must extend beyond the four proposed source/test files without a reviewed reason;
- unrelated worktree changes overlap the approved files or prevent exact scope verification.

The approved Phase 25 branch `phase-025-knowledge-construction` and required Phase 24 base commit `07e3266b2eed501895ab286739def4490b3748bf` are now verified.

## 16. Definition of Done

PR-025A is complete when:

- the exact Phase 24 commit and official tag are verified;
- the current and legacy Knowledge surfaces are inventoried;
- the authoritative accepted-Evidence and acceptance-record inputs are identified;
- `KnowledgeCandidate` is selected as the first honest construction result;
- one deterministic verbatim-text construction rule is bounded;
- complete support provenance and deterministic identity are specified;
- initial authority, lifecycle, review, and conflict states are explicit;
- persistence, transitions, Prompt Candidate, AI, business, CLI, UI, generator, config, dependency, database, and asset work are deferred;
- one four-file implementation PR and exact focused tests are named;
- exactly this review document is changed or untracked;
- no tests are run for this documentation-only review;
- no Git staging, commit, push, merge, tag, rebase, reset, amend, or force operation occurs.

## 17. Final decision

# APPROVED FOR MINIMAL KNOWLEDGE CONSTRUCTION IMPLEMENTATION

The architecture and Phase 24 dependencies are sufficient for one focused `KnowledgeCandidate` construction slice. Approval is limited to **PR-025B — Minimal KnowledgeCandidate Construction Contract Implementation** and the four files listed in section 13. It does not approve final Knowledge, KnowledgeRepository, lifecycle transitions, Prompt Candidate, AI, business decisions, runtime integration, or legacy migration.

The branch checkpoint condition has been resolved: the approved Phase 25 branch is verified at the required Phase 24 base commit.
