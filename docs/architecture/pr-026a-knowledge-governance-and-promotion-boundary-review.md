# PR-026A - Knowledge Governance and Promotion Boundary Review

## 1. Review identity

| Item | Reviewed value |
|---|---|
| Review | PR-026A |
| Type | Review-only and documentation-only |
| Gate | Knowledge Governance and Promotion Boundary Review |
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-026-knowledge-governance-review` |
| Tests executed | None |
| Project interpreter executed | No |

This review identifies the smallest honest governance boundary after `KnowledgeCandidate`. It does not implement review, acceptance, promotion, governed Knowledge, final Knowledge, persistence, merge, or tag behavior.

## 2. Repository and Phase 25 checkpoint

| Item | Verified value |
|---|---|
| Starting HEAD | `972206fc1cd1cb97284286a4a67eb23a96db7cf8` |
| `main` | `972206fc1cd1cb97284286a4a67eb23a96db7cf8` |
| `origin/main` | `972206fc1cd1cb97284286a4a67eb23a96db7cf8` |
| Local Phase 26 ref | `972206fc1cd1cb97284286a4a67eb23a96db7cf8` |
| Remote Phase 26 ref | `972206fc1cd1cb97284286a4a67eb23a96db7cf8` |
| Phase 25 annotated tag | `v0.25.0-rcis-knowledge-construction-phase` |
| Tag object | `7c6bd4a8d98e9ec6265807888eb2f08c69d8be43` |
| Peeled tag target | `972206fc1cd1cb97284286a4a67eb23a96db7cf8` |

The repository was clean and no file was staged before this document was created. Phase 25 is therefore the authoritative starting checkpoint for this review.

## 3. Current authoritative contracts

The current authoritative upstream contracts are:

| Layer | Contract | Role |
|---|---|---|
| Domain | `rie.domain.accepted_evidence.AcceptedEvidence` | Immutable accepted factual prerequisite with eligibility, materialization, payload, provenance, and locator data |
| Domain | `rie.domain.acceptance_record.AcceptanceRecord` | Immutable Evidence acceptance-governance event |
| Domain | `rie.domain.acceptance_identity` | Deterministic `ar1_` acceptance-record identity |
| Domain | `rie.domain.knowledge_candidate.KnowledgeCandidate` | Immutable, deterministic, reviewable construction result with `kc1_` identity |
| Application | `rie.application.knowledge_constructor` | Side-effect-free exact AcceptedEvidence-to-KnowledgeCandidate construction boundary |

The approved chain remains:

```text
Repository
-> Repository Explorer
-> RepositoryExploration
-> EvidenceCollection
-> Evidence
-> AcceptedEvidence
-> deterministic Knowledge construction
-> KnowledgeCandidate
-> future governed Knowledge
-> Knowledge Repository
-> Prompt Candidate
-> RCIS
```

Extraction output is not Evidence. `EvidenceCandidate` is not `AcceptedEvidence`. `AcceptedEvidence` is not Knowledge. `KnowledgeCandidate` is not final, reviewed, or accepted Knowledge and is not a Prompt Candidate.

## 4. Current absence or presence of governed Knowledge contracts

There is no current `KnowledgeReviewRecord`, `KnowledgeGovernanceDecision`, `KnowledgeAcceptanceRecord`, governed `Knowledge`, final `Knowledge`, Knowledge lifecycle-transition record, Knowledge authority-decision record, conflict record, or `KnowledgeRepository` contract under `src/rie`.

The only current Phase 25 Knowledge domain type is `KnowledgeCandidate`. Its states are fixed to `authority_status="unassessed"`, `lifecycle_status="candidate"`, `review_status="pending_review"`, and `conflict_status="not_assessed"`. No state-changing method exists.

The absence of governed Knowledge is correct. Phase 25 deliberately stopped before human or policy review, governance decisions, promotion, persistence, and downstream Prompt Candidate work.

## 5. Legacy Knowledge classification

The top-level `src/knowledge/*` types and `src/rie/knowledge/*` command wrappers are frozen compatibility surfaces, not current governance contracts.

| Legacy surface | Classification |
|---|---|
| `knowledge.TextKnowledge` | Historical four-field artifact using source path and positional Evidence index |
| `knowledge.TextKnowledgeBuilder` | Historical dictionary-to-artifact builder that bypasses AcceptedEvidence |
| `knowledge.OfficialKnowledgeSourceItem` | Historical input DTO with nullable/manual ID and incomplete status/governance strings |
| `knowledge.OfficialKnowledgeItem` | Historical copied artifact with positional index rather than deterministic domain identity |
| `knowledge.OfficialKnowledgeCollector` | Historical list-order copier without current eligibility, provenance, review, identity, or conflict rules |
| legacy serializers, collections, inspectors, and CLI wrappers | Compatibility and export surfaces only |

These modules must not be modified, migrated, renamed, deleted, imported into the new boundary, or treated as evidence that reviewed or governed Knowledge exists. Legacy Prompt Candidate modules remain downstream historical surfaces and are also excluded.

## 6. KnowledgeCandidate role and limits

`KnowledgeCandidate` is the immutable output of deterministic construction from eligible `AcceptedEvidence`. It preserves statement, construction rule, support, source snapshots, accepted-Evidence references, acceptance-record references, digests, and locator data.

It is reviewable because it has stable identity and complete support provenance. It is not itself a review event. Its `pending_review` state does not prove that review occurred, and its `not_assessed` conflict state does not claim that no conflict exists.

`KnowledgeCandidate` must remain unchanged in the next slice. Review must be represented beside it as a new immutable record. Mutation, replacement, subclassing, or a "reviewed candidate" variant would collapse candidate construction and governance history.

## 7. Governance vocabulary

| Term | Controlled meaning |
|---|---|
| Candidate construction | Deterministic creation of `KnowledgeCandidate` from exact eligible AcceptedEvidence and matching acceptance records |
| Review | Explicit actor-and-policy evaluation of one exact candidate snapshot, recorded immutably |
| Review decision | `passed`, `rejected`, or `deferred`; a statement about the review only |
| Governance decision | A later explicit authorization or denial of a lifecycle/authority action; not implemented in the next slice |
| Promotion | A later application action that creates a new governed Knowledge object from an eligible candidate and compatible governance records |
| Governed Knowledge | A future immutable domain object with its own identity, authority, lifecycle, provenance, and governance lineage |
| Final Knowledge | Not approved terminology for the next slice; acceptance and locking require explicit later contracts |
| Persistence | Storage of approved domain and governance records behind a separately reviewed repository boundary |

A passed review is not acceptance, authority assignment, lifecycle promotion, conflict clearance, or Knowledge creation.

## 8. Review-record boundary analysis

The preferred next domain object is `rie.domain.knowledge_review_record.KnowledgeReviewRecord`.

It is the smallest honest boundary because it records that an explicit actor applied an explicit versioned policy to one exact immutable candidate snapshot. It adds governance evidence without changing the candidate or claiming that promotion requirements are complete.

The record should be a frozen dataclass with these exact fields:

| Field | Contract |
|---|---|
| `knowledge_review_record_id` | Deterministic `kr1_<sha256>` identifier |
| `contract_version` | Exact `knowledge-review-record-v1` |
| `knowledge_candidate_id` | Exact referenced `kc1_` identifier |
| `knowledge_candidate_contract_version` | Exact reviewed candidate contract version |
| `knowledge_candidate_snapshot_digest` | SHA-256 of the complete canonical reviewed candidate snapshot |
| `review_decision` | Exact `passed`, `rejected`, or `deferred` |
| `reason_codes` | Non-empty, unique, lexicographically ordered immutable tuple |
| `reviewed_evidence_ids` | Exact ordered unique Evidence IDs projected from candidate support |
| `reviewed_acceptance_record_ids` | Exact ordered unique acceptance-record IDs projected from candidate support |
| `reviewed_acceptance_review_record_ids` | Exact ordered unique upstream review IDs projected from candidate support |
| `reviewed_by` | Non-empty explicit actor identifier |
| `reviewed_at` | Explicit timezone-aware timestamp supplied by the caller |
| `review_policy_id` | Exact policy identity |
| `review_policy_version` | Exact policy version |
| `diagnostics` | Immutable informational or warning diagnostics outside identity |

The candidate ID, full candidate snapshot digest, and exact support-reference projections are the review evidence. They prove which immutable subject and upstream accepted-Evidence support were reviewed without asset reads or repository lookup.

## 9. Governance-decision boundary analysis

A separate `KnowledgeGovernanceDecision` domain object is not required in the next implementation slice. Introducing both a review record and a governance-decision record would force unreviewed assumptions about authority assignment, lifecycle transitions, conflict clearance, acceptance, supersession, and promotion ordering.

The three review decisions mean only:

| Decision | Meaning |
|---|---|
| `passed` | The reviewed candidate snapshot satisfied the supported review policy; it may be considered by a later governance gate |
| `rejected` | The reviewed candidate snapshot did not satisfy the supported review policy; the immutable candidate and record remain historical facts |
| `deferred` | The reviewer could not complete a pass/reject determination, including when another reviewed prerequisite is required |

Forbidden decisions include `accept`, `promote`, `lock`, `supersede`, `resolve_conflict`, `assign_authority`, `create_prompt_candidate`, and any automatic or inferred equivalent.

## 10. Promotion boundary analysis

Promotion is not included in the recommended slice. It must be a separate application action after a later architecture review.

At minimum, a later promotion action may proceed only when all of these are explicit and compatible:

1. one exact `KnowledgeCandidate` is supplied;
2. its complete snapshot matches one or more exact `passed` KnowledgeReviewRecord values;
3. duplicate and contradictory review policy is defined;
4. authority is assigned by an explicit reviewed rule rather than inherited from source metadata;
5. conflict assessment is explicit and does not silently select a winner;
6. the target lifecycle transition is defined and valid;
7. actor, reason, policy, version, and time are recorded;
8. the new governed Knowledge identity and provenance contract are approved.

Promotion must preserve `knowledge_candidate_id` as immutable lineage. It must not reuse the candidate ID as the governed Knowledge ID. A later governed Knowledge contract requires its own identity policy, likely with a separately reviewed prefix such as `kn1_`; PR-026A does not approve that exact future prefix or contract.

## 11. Final Knowledge boundary analysis

Final Knowledge must not be implemented next. The term would imply completed review, authority assignment, lifecycle transition, conflict treatment, acceptance, replacement lineage, and repository semantics that do not yet exist.

The next review record creates no governed or final Knowledge. A later governed Knowledge object must be created only by a separate promotion service from exact reviewed inputs. A later Knowledge acceptance or locking event may require a separate `KnowledgeAcceptanceRecord`; it must not be folded into the first review record.

## 12. Authority and lifecycle analysis

The next slice permits no new candidate authority or lifecycle state.

| Concern | Permitted value in the next slice |
|---|---|
| Candidate authority | Remains exactly `unassessed` |
| Candidate lifecycle | Remains exactly `candidate` |
| Candidate review state | Remains exactly `pending_review`; the separate record proves review occurred |
| Candidate conflict state | Remains exactly `not_assessed` |
| Review-record decision | `passed`, `rejected`, or `deferred` |

Source authority and lifecycle are provenance snapshots only. They may not automatically affect review outcome, candidate governance, future Knowledge authority, or future Knowledge lifecycle. The review policy must not infer governance from source path, document classification, list position, timestamp ordering, or legacy status strings.

## 13. Conflict-handling analysis

Conflict detection, conflict records, semantic comparison, and conflict resolution are deferred. The one-candidate review record must preserve `conflict_status="not_assessed"` and must not reinterpret it as `no_conflict`.

Multiple candidates cannot be composed in the next slice. Each review request concerns exactly one candidate. A reviewer may record `deferred` with an explicit reason code such as `conflict_assessment_required`, but that does not create a conflict record or identify a winner.

Contradictory review records must remain independently visible. Neither time, input order, lexical order, source authority, equality, nor persistence may select one silently. Their adjudication belongs to a later governance policy and repository review.

## 14. Deterministic identity requirements

The recommended review-record identity policy is:

```text
policy_id = rcis-knowledge-review-record-identity
policy_version = 1.0.0
canonicalization_contract = knowledge-review-record-json-v1
digest_algorithm = sha256
id_prefix = kr1_
candidate_snapshot_contract = knowledge-candidate-review-snapshot-json-v1
```

Review-record identity includes:

1. review-record contract version;
2. candidate ID and candidate contract version;
3. complete candidate snapshot digest;
4. review decision;
5. ordered reason codes;
6. ordered reviewed Evidence, acceptance-record, and upstream review-record IDs;
7. actor;
8. reviewed-at timestamp normalized to UTC with fixed precision;
9. review policy ID and version;
10. the identity and snapshot canonicalization contract versions.

Diagnostics, Python object identity, filesystem paths, raw asset content, list position, repository location, future promotion metadata, future governed Knowledge ID, and future persistence metadata remain outside review-record identity.

Actor, reasons, policy, and reviewed-at time participate in review-record identity because the record identifies an immutable governance event. They remain outside KnowledgeCandidate identity and must remain outside any future factual Knowledge identity unless separately reviewed. Exact replay with the same canonical inputs produces the same `kr1_` ID. A changed decision, actor, reason, policy, timestamp, candidate snapshot, or review basis produces a different review-record ID.

The full candidate snapshot digest must include every candidate field, including diagnostics and support fields excluded from `kc1_` identity, so the record proves the exact candidate representation that was reviewed. Snapshot digesting does not mutate the candidate or change its `kc1_` identity.

## 15. Provenance requirements

The review record preserves AcceptedEvidence provenance indirectly through the exact KnowledgeCandidate ID and complete snapshot digest, and directly records the candidate's ordered Evidence and acceptance-governance reference projections.

The application service must derive these projections from the exact candidate object. It must reject inconsistency rather than accept caller-supplied replacement IDs. It must not resolve EvidenceRepository identifiers, reread source assets, reconstruct locators, or copy source authority into governance.

Review rejection is represented as a separate immutable record. It does not delete or mutate the candidate and is not silently reversible. A later policy may permit another review, but a new actor, time, reason, policy, or decision creates another immutable record. Historical records are never overwritten.

## 16. Dependency and import review

The next domain contract belongs under `rie.domain` because it represents immutable review facts and deterministic identity. A small application service is required to validate the exact candidate input, derive its complete snapshot and review-basis projections, apply the one supported review policy contract, and return an explicit result.

The dependency direction is safe:

```text
rie.application.knowledge_reviewer
-> rie.domain.knowledge_review_record
-> rie.domain.knowledge_candidate
```

`knowledge_candidate` must not import the review record, so no circular dependency is introduced. The application service may import both domain modules. It must not import `rie.interfaces`, `rie.infrastructure`, top-level `knowledge`, `prompting`, `rie.prompt`, filesystem, database, parser, network, AI, or CLI modules.

Existing Phase 23-25 contracts are sufficient upstream. No new dependency or configuration is required. Legacy Knowledge imports remain prohibited.

## 17. Repository/persistence decision

Repository lookup, `KnowledgeRepository`, interfaces, infrastructure, serialization, database schema, migration, and persistence are not required for the next implementation.

The application request must receive one exact in-memory `KnowledgeCandidate`, not an ID requiring lookup. The result returns one immutable review record or an explicit rejection. Storage, uniqueness enforcement, cross-record contradiction queries, concurrency, and durable replay behavior require a separate repository architecture gate.

## 18. Explicitly forbidden behavior

The recommended implementation must not:

- mutate or replace KnowledgeCandidate;
- accept raw dictionaries, paths, repository IDs, or duck-typed substitutes;
- accept `EvidenceCandidate`, extraction output, legacy Evidence, or legacy Knowledge;
- read the filesystem, source assets, network, database, or repository;
- infer authority or lifecycle from source metadata;
- assign Knowledge authority or lifecycle;
- approve, accept, promote, lock, reject, or supersede governed Knowledge;
- claim conflict absence, detect conflicts, resolve conflicts, or select a winner;
- compose multiple candidates;
- create final Knowledge, Prompt Candidate, prompts, or generator inputs;
- summarize, normalize, infer, classify, embed, or call AI;
- make business, brand, benefit, priority, or creative decisions;
- retry automatically, overwrite history, or hide contradictory records;
- import or retrofit legacy Knowledge modules.

## 19. Deferred scope

The following remain deferred by default:

- `KnowledgeGovernanceDecision` as a separate lifecycle/authority authorization record;
- `KnowledgeAcceptanceRecord`;
- reviewed-candidate mutation or subclassing;
- governed or final Knowledge;
- authority-decision and lifecycle-transition records;
- conflict detection, conflict representation, adjudication, and resolution;
- multiple-candidate composition;
- promotion and governed Knowledge identity;
- `KnowledgeRepository`, interfaces, infrastructure, serialization, persistence, databases, and migrations;
- repository orchestration, CLI, UI, API, and dashboards;
- Prompt Candidate and generators;
- embeddings, AI inference, and semantic synthesis;
- business and creative decisions;
- legacy Knowledge migration.

## 20. Preferred smallest implementation slice

**PR-026B - Minimal KnowledgeReviewRecord and Reviewer Contract Implementation**

The preferred slice implements one immutable review record plus one deterministic, side-effect-free application reviewer. It records review only and deliberately stops before governance authorization or promotion.

Recommended domain classes and functions:

- `KnowledgeReviewDiagnostic`;
- `KnowledgeReviewIdentityInput`;
- `KnowledgeReviewRecord`;
- `compute_knowledge_candidate_review_snapshot_digest(candidate)`;
- `canonical_knowledge_review_identity_bytes(identity_input)`;
- `compute_knowledge_review_record_id(identity_input)`;
- `knowledge_review_identity_input_from_record(record)`.

Recommended application contracts:

```text
KnowledgeReviewRequest
  knowledge_candidate: KnowledgeCandidate
  review_decision: "passed" | "rejected" | "deferred"
  reason_codes: tuple[str, ...]
  reviewed_by: str
  reviewed_at: timezone-aware datetime
  review_policy_id: "rcis-knowledge-candidate-review"
  review_policy_version: "1.0.0"

review_knowledge_candidate(request)
  -> KnowledgeReviewResult

KnowledgeReviewResult
  result_status: "recorded" | "rejected"
  review_record: KnowledgeReviewRecord | None
  reason_codes: tuple[str, ...]
  diagnostics: tuple[KnowledgeReviewDiagnostic, ...]
```

Malformed programming inputs raise `ValueError`: wrong exact request/candidate/record/diagnostic types, raw dictionaries or paths, non-tuple collections, empty or whitespace strings, naive timestamps, malformed IDs or digests, duplicate or non-canonical tuples, and a record ID inconsistent with its identity input.

Valid but unsupported review requests return an explicit rejected result with no record. Initial exact reason codes are `unsupported_review_policy` and `unsupported_review_decision`. The constructor must not silently repair a request.

Exact replay produces the same record and `kr1_` ID in memory. The application service does not perform durable duplicate detection. Contradictory decisions produce distinct immutable records and no automatic winner.

### 20.1 Required-question answers

| Question | Decision |
|---:|---|
| 1 | Implement `KnowledgeReviewRecord` next. |
| 2 | It adds explicit review evidence without assuming promotion, authority, lifecycle, conflict, or persistence contracts. |
| 3 | It references one exact candidate ID and complete candidate snapshot; it exists beside the candidate. |
| 4 | Yes. KnowledgeCandidate remains immutable and unchanged. |
| 5 | The application accepts exact `KnowledgeCandidate`, exact strings/tuples, and a timezone-aware `datetime`. |
| 6 | The application requires the exact candidate object. An unresolved ID is forbidden; the record stores the ID and digest. |
| 7 | Actor, ordered reasons, policy ID/version, reviewed-at time, candidate snapshot digest, and exact support-reference projections are recorded. |
| 8 | Only `passed`, `rejected`, and `deferred` review decisions are permitted. |
| 9 | Acceptance, promotion, locking, supersession, authority assignment, lifecycle change, conflict resolution, Prompt creation, and automatic decisions are forbidden. |
| 10 | The review record only records a decision. It creates no governed Knowledge. |
| 11 | Promotion requires a later compatible passed review plus explicit authority, conflict, lifecycle, actor, policy, identity, and provenance contracts. |
| 12 | Yes. Promotion must be a separate later application action. |
| 13 | Promotion must preserve the original candidate ID as lineage, not reuse it as governed Knowledge identity. |
| 14 | The next slice requires `kr1_` review-record identity. Governed Knowledge identity remains separately deferred. |
| 15 | Review subject, snapshot, decision, reasons, basis IDs, actor, time, policy, and canonicalization versions participate in review-record identity. |
| 16 | Diagnostics, paths, raw assets, Python identity, repository location, promotion, persistence, and future Knowledge metadata remain outside identity. |
| 17 | Candidate authority remains only `unassessed`; no new Knowledge authority state is introduced. |
| 18 | Candidate lifecycle remains only `candidate`; no lifecycle transition is introduced. |
| 19 | The candidate remains `pending_review`; the separate record decision is `passed`, `rejected`, or `deferred`. |
| 20 | No. Source authority and lifecycle cannot influence governance automatically. |
| 21 | Conflict detection and representation are deferred; the record preserves `not_assessed` and cannot claim no conflict. |
| 22 | No. Each request reviews exactly one candidate. |
| 23 | Rejection is a separate immutable historical record, not candidate mutation. Later review policy may permit another record. |
| 24 | Exact replay is idempotent by identity; contradictory records coexist; durable duplicate and adjudication policy are deferred. |
| 25 | Wrong exact types, raw/duck inputs, malformed identifiers, empty values, naive times, mutable/noncanonical collections, and identity mismatch raise `ValueError`. |
| 26 | Unsupported policy or decision returns an explicit rejected result with no record. |
| 27 | No repository lookup, persistence, serialization, CLI, database, API, interface, or infrastructure is required. |
| 28 | AcceptedEvidence, AcceptanceRecord, their identities, KnowledgeCandidate, knowledge constructor, EvidenceRepository, and all Phase 23-25 contracts remain unchanged. |
| 29 | All `src/knowledge/*`, `src/rie/knowledge/*`, legacy prompting modules, and their compatibility tests remain frozen. |
| 30 | Implement the exact four-file scope in section 21 with the focused matrix in section 22. |

## 21. Exact proposed file scope

PR-026B should add exactly four files:

1. `src/rie/domain/knowledge_review_record.py` - frozen review record, diagnostic, candidate snapshot digest, deterministic identity policy, and identity helpers;
2. `src/rie/application/knowledge_reviewer.py` - request, explicit result, supported review policy, validation, and record construction;
3. `tests/domain/test_knowledge_review_record.py` - domain, snapshot, and identity coverage;
4. `tests/application/test_knowledge_reviewer.py` - application decision, rejection, boundary, and side-effect coverage.

No existing file needs modification. If implementation requires another layer or file, stop and return to architecture review rather than widening scope silently.

## 22. Exact focused test matrix

### 22.1 Domain tests - `tests/domain/test_knowledge_review_record.py`

| ID | Exact assertion |
|---|---|
| D01 | Review diagnostic, identity input, and record are frozen with value equality and explicit `kr1_` identity |
| D02 | Constants exactly match record, identity-policy, canonicalization, snapshot, digest, and prefix contracts |
| D03 | Record ID requires `kr1_` plus exactly 64 lowercase hex characters and must match canonical identity |
| D04 | Candidate ID requires the exact valid `kc1_` form; snapshot digest requires 64 lowercase hex characters |
| D05 | Required strings reject empty or whitespace values; reviewed-at requires an exact timezone-aware datetime |
| D06 | Reason and review-basis collections require exact tuples, non-empty values, uniqueness, and lexical ordering |
| D07 | Only review decisions `passed`, `rejected`, and `deferred` are accepted |
| D08 | Diagnostics accept only exact immutable info/warning members and remain outside identity |
| D09 | Candidate review snapshot includes every candidate field, including diagnostics and non-`kc1_` provenance fields |
| D10 | Snapshot hashing is stable, canonical UTF-8 JSON with fixed separators, sorted keys, NFC text, and no mutation |
| D11 | Review identity is stable on replay and equals `kr1_<sha256(canonical bytes)>` |
| D12 | Candidate snapshot, decision, reason, basis IDs, actor, time, policy, or contract changes alter record identity |
| D13 | Diagnostics, paths, repository metadata, promotion data, and future Knowledge IDs are absent from record identity |
| D14 | Identity and snapshot helpers reject duck-typed substitutes and wrong exact contract types |
| D15 | Identity extraction from a valid record round-trips exactly |

### 22.2 Application tests - `tests/application/test_knowledge_reviewer.py`

| ID | Exact assertion |
|---|---|
| A01 | Exact candidate plus supported policy and `passed` decision records one review without changing candidate |
| A02 | `rejected` and `deferred` produce records with exact decisions and ordered reason codes |
| A03 | Record preserves candidate ID, contract version, full snapshot digest, Evidence IDs, acceptance IDs, and upstream review IDs |
| A04 | Actor, policy, version, timestamp, and reason codes are copied exactly |
| A05 | Exact replay produces the same record and `kr1_` ID |
| A06 | A material input change produces a distinct review-record identity |
| A07 | Unsupported policy ID or version returns explicit `unsupported_review_policy` rejection and no record |
| A08 | Unsupported decision returns explicit `unsupported_review_decision` rejection and no record |
| A09 | Raw dictionaries, paths, IDs, EvidenceCandidate, AcceptedEvidence, legacy Knowledge, and duck-typed objects are rejected |
| A10 | Mutable, empty, duplicate, unordered, or wrong-type reason codes fail closed without repair |
| A11 | Naive or wrong-type timestamps and empty actor/policy values raise `ValueError` |
| A12 | Source authority/lifecycle do not alter candidate state or create automatic review outcome |
| A13 | `passed` does not create governed/final Knowledge, authority, lifecycle, acceptance, conflict, persistence, or Prompt behavior |
| A14 | Two contradictory requests create independent records; time/order does not select a winner |
| A15 | Inputs remain unchanged after recorded and rejected results |
| A16 | Source imports contain no interface, infrastructure, repository, filesystem, database, parser, network, AI, Prompt, CLI, or legacy Knowledge dependency |
| A17 | No filesystem, source-asset, repository, persistence, network, subprocess, clock, randomness, or automatic retry side effect occurs |

Focused execution after implementation, not during this review:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/domain/test_knowledge_review_record.py tests/application/test_knowledge_reviewer.py -q
```

## 23. Definition of Done

PR-026A is complete when:

- the exact Phase 25 annotated checkpoint and synchronized Phase 26 branch are verified;
- authoritative AcceptedEvidence, AcceptanceRecord, KnowledgeCandidate, constructor, tests, and Phase 23-25 decisions are inspected;
- governed Knowledge is confirmed absent;
- legacy Knowledge and Prompt surfaces remain frozen and disconnected;
- `KnowledgeReviewRecord` is selected as the smallest honest next object;
- the record's exact relationship to one immutable KnowledgeCandidate is defined;
- actor, reasons, policy, version, timestamp, candidate snapshot, and review evidence are explicit;
- only `passed`, `rejected`, and `deferred` review decisions are permitted;
- review, governance, promotion, governed Knowledge, final Knowledge, and persistence are distinguished;
- deterministic `kr1_` identity and full candidate snapshot requirements are defined;
- authority, lifecycle, conflict, composition, replay, duplicate, and contradiction boundaries are explicit;
- repository, persistence, interfaces, infrastructure, dependencies, runtime integration, AI, business, and legacy migration remain deferred;
- exactly one four-file implementation PR and exact focused matrix are recommended;
- exactly this review document is created in the repository;
- no existing repository file is modified;
- no project interpreter or test is run;
- no Git staging, history, remote, merge, or tag operation occurs.

## 24. Stop conditions

Stop PR-026B and return to architecture review if:

- exact `KnowledgeCandidate` input cannot remain the sole reviewed subject;
- KnowledgeCandidate would need mutation, a reviewed subclass, or state promotion;
- review cannot preserve the exact candidate snapshot and accepted-Evidence support references;
- a review decision would implicitly accept, promote, assign authority, change lifecycle, clear conflict, or create Knowledge;
- duplicate or contradictory records would be suppressed or overwritten;
- raw paths, assets, dictionaries, repository lookup, persistence, interfaces, infrastructure, CLI, API, database, Prompt, AI, business logic, or legacy Knowledge becomes necessary;
- deterministic identity would depend on randomness, implicit current time, mutable data, list position, or source path;
- an existing Phase 23-25 contract defect is found;
- implementation scope must exceed the exact four proposed files without a reviewed reason;
- unrelated worktree changes overlap the approved scope.

## 25. Final decision

# APPROVED FOR MINIMAL KNOWLEDGE GOVERNANCE IMPLEMENTATION

The smallest honest next boundary is an immutable `KnowledgeReviewRecord` and side-effect-free reviewer for one exact `KnowledgeCandidate`. Approval is limited to PR-026B and the four files in section 21. It does not approve candidate mutation, governance promotion, governed or final Knowledge, authority or lifecycle assignment, conflict handling, composition, persistence, repository lookup, Prompt Candidate, AI, business decisions, runtime integration, or legacy migration.
