# PR-028A - Knowledge Promotion Prerequisite and Next Domain Boundary Review

## 1. Review identity

| Item | Reviewed value |
|---|---|
| Review | PR-028A |
| Type | Review-only and documentation-only |
| Gate | Knowledge Promotion Prerequisite and Next Domain Boundary Review |
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-028-knowledge-promotion-prerequisite-review` |
| Starting HEAD | `913817c60d44187127bbc69e8312f94b124382b2` |
| Tests executed | None |
| Project interpreter executed | No |

This review determines the smallest honest boundary after `KnowledgeGovernanceDecision`. It does not implement semantic assessment, authority, lifecycle, acceptance, promotion, governed Knowledge, persistence, or repository behavior.

## 2. Repository and Phase 27 checkpoint

| Item | Verified value |
|---|---|
| HEAD | `913817c60d44187127bbc69e8312f94b124382b2` |
| HEAD subject | `docs: review knowledge governance authorization phase closure` |
| `main` | `913817c60d44187127bbc69e8312f94b124382b2` |
| `origin/main` | `913817c60d44187127bbc69e8312f94b124382b2` |
| Local Phase 28 ref | `913817c60d44187127bbc69e8312f94b124382b2` |
| Remote Phase 28 ref | `913817c60d44187127bbc69e8312f94b124382b2` |
| Phase-ref divergence | `0 0` |
| Main-to-phase divergence | `0 0` |
| Initial repository status | Clean |
| Initial staged files | None |

The Phase 27 annotated tag `v0.27.0-rcis-knowledge-governance-decision-phase` is verified locally and remotely. It is a tag object at `95083d47b5a9ab307914e6e587de4863b8992ec0`, peels to `913817c60d44187127bbc69e8312f94b124382b2`, and carries message `RCIS Knowledge Governance Decision Phase 27`.

The read-only review covered the requested source and test files plus these relevant Phase 23 through Phase 27 documents:

- `docs/architecture/pr-023a-phase-23-knowledge-governance-boundary-and-dependency-review.md`;
- `docs/architecture/pr-023f-accepted-evidence-prerequisite-closure-and-knowledge-governance-readiness-reassessment.md`;
- `docs/architecture/pr-023g-phase-23-closure-and-accepted-evidence-implementation-phase-entry-review.md`;
- `docs/architecture/pr-023h-phase-23-controlled-merge-and-tag-readiness-review.md`;
- `docs/architecture/pr-024ai-phase-24-accepted-evidence-implementation-closure-review.md`;
- `docs/architecture/pr-025a-knowledge-construction-boundary-and-dependency-review.md`;
- `docs/architecture/pr-025c-knowledge-candidate-construction-result-and-full-regression-review.md`;
- `docs/architecture/pr-025d-knowledge-construction-phase-closure-review.md`;
- `docs/architecture/pr-026a-knowledge-governance-and-promotion-boundary-review.md`;
- `docs/architecture/pr-026c-knowledge-review-record-implementation-result-and-full-regression-review.md`;
- `docs/architecture/pr-026d-knowledge-governance-phase-closure-review.md`;
- `docs/architecture/pr-027a-knowledge-governance-authorization-and-promotion-prerequisite-boundary-review.md`;
- `docs/architecture/pr-027c-knowledge-governance-decision-implementation-result-and-full-regression-review.md`;
- `docs/architecture/pr-027d-knowledge-governance-authorization-phase-closure-review.md`.

## 3. Current authoritative chain

The non-collapsible chain remains:

```text
Repository
-> Repository Explorer
-> RepositoryExploration
-> EvidenceCollection
-> Evidence
-> AcceptedEvidence
-> deterministic Knowledge construction
-> KnowledgeCandidate
-> explicit review
-> KnowledgeReviewRecord
-> explicit governance authorization
-> KnowledgeGovernanceDecision
-> future prerequisite evaluation
-> future promotion
-> future governed Knowledge
-> future Knowledge Repository
-> future Prompt Candidate
-> RCIS
```

Extraction output is not Evidence. `EvidenceCandidate` is not `AcceptedEvidence`. `AcceptedEvidence` is not Knowledge. `KnowledgeCandidate` is not governed or accepted Knowledge. `KnowledgeReviewRecord` is review evidence only. A passed review is not authorization. `KnowledgeGovernanceDecision` is governance evidence only. `authorized` means only `eligible_for_future_promotion_evaluation`.

## 4. Current KnowledgeCandidate boundary

`KnowledgeCandidate` is an immutable deterministic construction result containing one statement, complete accepted-Evidence support, construction-rule lineage, diagnostics, and fixed initial governance states:

```text
authority_status = unassessed
lifecycle_status = candidate
review_status = pending_review
conflict_status = not_assessed
conflict_ids = ()
```

It must not be mutated, promoted in place, assigned authority, transitioned, accepted, or treated as governed Knowledge. Source authority and lifecycle remain provenance snapshots only.

## 5. Current KnowledgeReviewRecord boundary

`KnowledgeReviewRecord` is immutable evidence that one exact candidate snapshot was reviewed under an explicit policy by an explicit actor at an explicit time for explicit reasons. Its decisions are `passed`, `rejected`, and `deferred`.

It does not mutate the candidate, authorize promotion, assign authority, change lifecycle, assess semantic conflict, create Knowledge, or select a winner among contradictory records.

## 6. Current KnowledgeGovernanceDecision boundary

`KnowledgeGovernanceDecision` is immutable governance evidence for one exact candidate snapshot and exact ordered `kr1_` lineage. Its decisions are `authorized`, `denied`, and `deferred`.

`authorized` covers only `eligible_for_future_promotion_evaluation`. It does not execute promotion, accept Knowledge, create governed Knowledge, assign authority, transition lifecycle, clear conflict, persist state, or create a Prompt Candidate. Contradictory governance records remain independent historical records.

## 7. Current absent-contract inventory

There is no current authoritative:

- `KnowledgeConflictAssessmentRecord`;
- `KnowledgeAuthorityDecision`;
- `KnowledgeLifecycleTransitionRecord`;
- `KnowledgePromotionDecision` or `KnowledgePromotionRecord`;
- `KnowledgeAcceptanceRecord`;
- `GovernedKnowledge` or equivalent governed object;
- `KnowledgePromotionPrerequisiteEvaluation`;
- `KnowledgeRepository`, serialization, or persistence adapter.

Their absence is correct. Legacy Knowledge and Prompt modules are compatibility surfaces and do not fill any gap.

## 8. Controlled promotion vocabulary

| Term | Controlled meaning |
|---|---|
| Pairwise semantic assessment | Explicit actor-and-policy classification of the relationship between two exact candidate snapshots |
| Conflict evidence | Immutable assessment record; not conflict resolution or global completeness |
| Promotion prerequisite | Concrete evidence or decision required before a promotion-evaluation service may return eligible |
| Prerequisite evaluation | Later aggregate verification of exact candidate, review, governance, conflict, and authority inputs |
| Promotion | Later explicit creation action producing new governed Knowledge and a promotion audit record |
| Governed Knowledge | New immutable object with its own identity, initial authority, initial lifecycle, and complete lineage |
| Acceptance | Later decision about governed Knowledge, never about a candidate or promotion request |
| Lifecycle initialization | Initial governed-object state assigned at creation; not a transition from a nonexistent object |
| Lifecycle transition | Later immutable record changing a governed object's state without rewriting history |
| Supersession | Later explicit relationship replacing governed Knowledge while preserving both objects |
| Persistence | Later repository/adaptor concern, separate from in-memory domain creation |

Authorization is not promotion. Promotion is not acceptance. A candidate is not governed Knowledge. Governed Knowledge must not reuse `kc1_`, `kr1_`, `kg1_`, or the proposed conflict-assessment identity.

## 9. Promotion-prerequisite classification

| Item | Classification | Exact role |
|---|---|---|
| One exact `KnowledgeCandidate` | Required before promotion evaluation | Promotion subject |
| Complete exact candidate snapshot | Required before promotion evaluation | Prevents stale or changed subject |
| Exact compatible `KnowledgeReviewRecord` lineage | Required before promotion evaluation | Proves review evidence and contradiction set |
| Exact compatible authorized `KnowledgeGovernanceDecision` lineage | Required before promotion evaluation | Proves limited authorization evidence |
| Contradictory review evidence | Required during promotion evaluation | Blocks eligibility until separately adjudicated |
| Contradictory governance decisions | Required during promotion evaluation | Blocks eligibility; no winner inferred |
| Pairwise semantic-conflict records | Required before promotion evaluation | Covers every declared in-scope comparison |
| Conflict comparison-universe coverage | Required during promotion evaluation | Pairwise records alone do not prove completeness |
| Explicit authority decision for future governed Knowledge | Required before promotion evaluation | Prevents source-authority inheritance |
| Initial governed lifecycle rule | Required only when governed Knowledge is created | Assigns initial state; not a transition |
| Acceptance semantics | Required after governed Knowledge creation | Acceptance subject is the created governed object |
| Actor, reason, caller time, policy ID/version | Required during promotion evaluation | Explicit evaluation audit |
| New governed-Knowledge identity | Required only when governed Knowledge is created | Must be distinct from all prerequisite IDs |
| Complete provenance | Required only when governed Knowledge is created | Preserves candidate, Evidence, review, governance, conflict, authority, and promotion lineage |
| Supersession behavior | Required only when replacing governed Knowledge | Not applicable to an initial creation; otherwise separately reviewed |
| Repository and persistence | Required after governed Knowledge creation | Not required for in-memory creation; deferred |
| Final or locked Knowledge | Explicitly deferred | Later lifecycle and acceptance boundary |

## 10. Contradictory review and governance evidence analysis

Contradictory review evidence means review records for the same exact candidate snapshot contain incompatible decisions. Contradictory governance evidence means governance records for the same subject and relevant evidence contain incompatible decisions. Neither condition is semantic conflict between statements.

Review order, governance order, actor identity, timestamps, source authority, source lifecycle, policy ordering, lexical IDs, and repository paths cannot select a winner. A future promotion-prerequisite evaluator must inspect the complete supplied sets and reject or defer incompatible evidence. It must not relabel that evidence as semantic conflict.

## 11. Semantic conflict boundary analysis

Semantic conflict concerns the meaning of two claims, not their governance history. It must distinguish:

- conflict between distinct candidate statements;
- semantic equivalence between distinct candidates;
- no conflict identified for one exact pair under one policy;
- assessment deferred;
- later candidate-versus-governed-Knowledge conflict;
- later duplicate, supersession, and invalidation rules.

The smallest current subject is an exact pair of exact `KnowledgeCandidate` snapshots. The pair is canonical, unique, and lexicographically ordered by candidate ID. A pairwise record can remain frozen, deterministic, side-effect-free, repository-free, and persistence-free because the caller supplies both exact objects plus an explicit outcome, actor, reasons, time, and policy.

The service records caller-supplied assessment; it does not infer semantics, call AI, rank sources, or resolve a conflict. `no_conflict_identified` applies only to that exact pair and policy. It is not a global no-conflict certificate and does not prove comparison-universe completeness.

## 12. Authority-assignment boundary analysis

Authority may not be assigned to `KnowledgeCandidate` or `KnowledgeGovernanceDecision`. Candidate authority remains `unassessed`. Source authority, classification, lifecycle, path, review result, and governance authorization cannot determine Knowledge authority.

A future separate immutable `KnowledgeAuthorityDecision` should authorize the initial authority value intended for a future governed object while preserving the candidate snapshot and governance lineage. That record must exist before promotion evaluation can declare readiness, but its vocabulary and exact subject require a later review after conflict evidence is established. Authority is applied to governed Knowledge at creation and never by mutating the candidate.

## 13. Lifecycle-transition boundary analysis

Candidate lifecycle remains `candidate` permanently as construction-time history. Authorization does not imply a lifecycle transition, and promotion must not rewrite the candidate.

Governed Knowledge requires its own initial lifecycle value at creation. Assigning that initial value is initialization, not transition. A separate immutable `KnowledgeLifecycleTransitionRecord` is required only for later changes to an existing governed object. Lifecycle and authority remain separate responsibilities and records.

## 14. Knowledge-acceptance boundary analysis

Acceptance does not apply to `KnowledgeCandidate`, a review record, a governance decision, a promotion request, or an uncreated promotion result. The honest subject of a future `KnowledgeAcceptanceRecord` is exact governed Knowledge after creation, including its identity, authority, lifecycle, and complete creation lineage.

Acceptance may later lock, reject, or otherwise govern that object only through separately reviewed immutable records. It cannot be folded into construction, review, authorization, prerequisite evaluation, promotion, or creation.

## 15. Promotion decision or record analysis

A promotion record would be an immutable audit of a later creation action. Its subject would be one exact candidate snapshot plus exact compatible review, authorized governance, complete conflict coverage, authority, prerequisite-evaluation, actor, reason, time, and policy inputs.

It cannot be implemented next because concrete conflict and authority records, prerequisite aggregation, governed identity, initial lifecycle, and creation provenance are not yet defined. A future promotion service must create a separate promotion record and governed object without mutating any upstream object.

## 16. Governed-Knowledge object analysis

Governed Knowledge is created by a future promotion action. It is a new immutable object, not a subtype mutation or renamed candidate. Minimum creation inputs include exact candidate content and support, all accepted-Evidence provenance, review lineage, authorized governance lineage, complete conflict-assessment coverage, explicit authority decision, initial lifecycle rule, promotion record, actor, reasons, time, and policy.

The initial governed object must preserve the candidate statement and support exactly. Normalization, semantic rewriting, summarization, and multi-candidate composition require separate construction/promotion rules and are deferred. Conflict IDs may reference applicable assessment records, but they cannot imply resolution.

Governed Knowledge may exist in memory without a repository. Persistence is not part of honest object creation. Final or locked Knowledge is a later governed state, not the initial object.

## 17. Governed-Knowledge identity analysis

Promotion must create a new deterministic governed-Knowledge identity. It must not reuse `kc1_`, `kr1_`, `kg1_`, or proposed `kcf1_` identities. Its exact prefix and policy are intentionally deferred until the governed-object contract is reviewed.

Future identity must include the governed contract, exact statement and support, source and Evidence provenance, candidate snapshot, review IDs, governance IDs, conflict-assessment IDs, authority decision, initial lifecycle, promotion rule and policy, and any supersession predecessor when applicable. Repository location, implicit time, random values, list position, and mutable metadata remain excluded.

## 18. Provenance and lineage requirements

Future promotion and governed Knowledge must preserve:

- every supporting accepted-Evidence ID and acceptance lineage already captured by the candidate;
- source ID, content checksum, payload digest, and exact locator;
- exact `kc1_` candidate ID, contract, and complete snapshot digest;
- all relevant ordered `kr1_` review-record IDs;
- all relevant ordered `kg1_` governance-decision IDs;
- all applicable ordered pairwise conflict-assessment IDs;
- future authority-decision and prerequisite-evaluation IDs;
- promotion record ID, rule, actor, reasons, caller time, and policy;
- superseded governed-Knowledge ID when replacement occurs.

The pairwise conflict record itself preserves only the two candidate IDs, contracts, and snapshot digests because semantics is independent of review and authorization. A later prerequisite aggregate is responsible for joining `kr1_`, `kg1_`, and `kcf1_` lineage.

## 19. Supersession and invalidation analysis

Semantic conflict, equivalence, supersession, and invalidation are distinct. A conflict assessment must not supersede, invalidate, delete, or overwrite either candidate. Semantic equivalence does not authorize deduplication.

Supersession applies only after governed Knowledge exists and requires an explicit directional record preserving old and new identities, actor, reason, time, and policy. Invalidation likewise requires a separate immutable governance event. Neither belongs in the next pairwise assessment slice.

## 20. Repository and persistence analysis

`KnowledgeRepository` is not required for the next slice. Exact candidate objects are supplied in memory, and the pairwise result is returned in memory. Durable lookup, comparison-universe discovery, duplicate suppression, transactions, cross-record contradiction queries, serialization, and persistence remain later concerns.

A governed object can be created in memory before persistence. Repository interface review follows stable governed-Knowledge, promotion, acceptance, lifecycle, and serialization contracts. Infrastructure adapters follow the interface and must not determine domain identity or governance.

## 21. Dependency and ordering graph

```text
KnowledgeCandidate
  -> KnowledgeReviewRecord
    -> KnowledgeGovernanceDecision --------------------------+
                                                               |
canonical pair of KnowledgeCandidate snapshots                 |
  -> KnowledgeConflictAssessmentRecord ------------------------+
                                                               |
future KnowledgeAuthorityDecision -----------------------------+
                                                               v
                         KnowledgePromotionPrerequisiteEvaluation
                                                               |
                                                               v
                           KnowledgePromotionRecord + GovernedKnowledge
                                                               |
                      +----------------------+-----------------+
                      |                      |                 |
                      v                      v                 v
          KnowledgeAcceptanceRecord  LifecycleTransition  KnowledgeRepository
                                                               |
                                                               v
                                                           persistence
```

Mandatory predecessors for prerequisite evaluation are exact candidate/review/authorized-governance lineage, complete in-scope conflict records, and a future authority decision. Conflict and authority records are independent predecessor branches. Acceptance and later lifecycle transitions require governed Knowledge. Repository work requires a stable governed contract.

Existing candidate, review, and governance modules must not import conflict, promotion, governed-Knowledge, or repository modules. Conflict assessment must not import promotion or persistence. No circular dependency is permitted.

## 22. Candidate next-boundary comparison

| Candidate boundary | Exact subject | Responsibility type | Required inputs | Forbidden effects | Repository needed | Honest next? |
|---|---|---|---|---|---|---|
| `KnowledgeConflictAssessmentRecord` | Canonical pair of exact candidate snapshots | Explicit assessment evidence | Two exact `KnowledgeCandidate` objects, outcome, reasons, actor, time, policy | Mutation, inference, resolution, promotion | No | Yes |
| `KnowledgeAuthorityDecision` | Future governed authority for one candidate lineage | Decision/authorization | Candidate, governance lineage, authority vocabulary | Candidate mutation, source inheritance, creation | No | Not yet; exact future subject vocabulary remains open |
| `KnowledgeLifecycleTransitionRecord` | Existing governed Knowledge | Transition | Governed object, prior state, target state, actor, policy | Candidate transition, hidden mutation | No | No governed subject exists |
| `KnowledgePromotionDecision` or record | Candidate plus complete prerequisites | Creation decision/audit | Reviews, authorization, conflict, authority, lifecycle rule, provenance | Automatic acceptance or persistence | No | Blocked by missing prerequisites |
| `KnowledgeAcceptanceRecord` | Existing governed Knowledge | Acceptance decision | Governed object and governance state | Candidate acceptance or creation | No | No governed subject exists |
| `GovernedKnowledge` | Newly created governed fact | Object creation | Complete promotion prerequisites | Reused identity, candidate mutation | No | Blocked by missing contracts |
| `KnowledgeRepository` | Stable governed objects and records | Persistence | Stable domain, serialization, duplicate policy | Identity or governance inference | Yes | Premature |
| Promotion-prerequisite aggregate | One promotion subject and all prerequisite records | Evaluation result | Concrete review, governance, conflict, and authority types | Creation, acceptance, persistence | No | Blocked until conflict and authority inputs exist |

The pairwise assessment is the only listed boundary with a complete current subject and no dependency on a nonexistent governed object or future abstraction.

## 23. Preferred smallest next boundary

The preferred next boundary is `KnowledgeConflictAssessmentRecord`: one immutable, pairwise semantic-relationship assessment for two exact candidate snapshots, constructed by a side-effect-free application assessor.

This slice is implemented after Phase 27 chronologically but is semantically independent of review and governance decisions. Denied or deferred candidates may still conflict with another claim, so the assessor must not require or rank `kr1_` or `kg1_` inputs. A later promotion-prerequisite evaluator joins authorized governance lineage with complete applicable conflict lineage.

## 24. Exact proposed next slice, or exact unresolved review gate

Outcome A is selected.

**PR-028B - Minimal Pairwise KnowledgeConflictAssessmentRecord and Assessor Contract Implementation**

The domain file should define frozen `KnowledgeConflictDiagnostic`, `KnowledgeConflictParticipant`, `KnowledgeConflictIdentityInput`, and `KnowledgeConflictAssessmentRecord` contracts. The application file should define frozen request/result contracts and `assess_knowledge_candidate_conflict`.

Proposed record fields are:

| Field | Purpose |
|---|---|
| `knowledge_conflict_assessment_record_id` | Deterministic `kcf1_` identity |
| `contract_version` | `knowledge-conflict-assessment-record-v1` |
| `participants` | Exact tuple of two ordered unique candidate participant snapshots |
| `assessment_scope` | `pairwise_knowledge_candidate_semantic_relationship` |
| `assessment_outcome` | Exact controlled outcome |
| `reason_codes` | Non-empty ordered unique caller reasons |
| `assessed_by` | Explicit actor |
| `assessed_at` | Explicit timezone-aware caller time |
| `assessment_policy_id` | Exact caller application policy |
| `assessment_policy_version` | Exact caller policy version |
| `diagnostics` | Immutable info/warning diagnostics outside identity |

Each participant contains exact candidate ID, candidate contract version, and the same complete candidate snapshot digest used by current review/governance records.

Controlled outcomes are exactly:

```text
conflict_identified
equivalent_statement
no_conflict_identified
assessment_deferred
```

Required reasons are respectively:

```text
semantic_conflict_identified
semantic_equivalence_identified
pairwise_no_conflict_identified
semantic_assessment_deferred
```

## 25. Exact input-object boundary

`KnowledgeConflictAssessmentRequest` must receive:

- an exact tuple of exactly two exact `KnowledgeCandidate` objects;
- unique candidate IDs in lexicographic order;
- one explicit assessment outcome;
- non-empty ordered unique reason codes;
- explicit actor;
- caller-supplied timezone-aware timestamp;
- explicit assessment policy ID and version.

The assessor does not reorder, resolve IDs, read a repository, discover comparisons, infer an outcome, or insert a required reason. Raw dictionaries, paths, unresolved IDs, `EvidenceCandidate`, `AcceptedEvidence`, review records, governance decisions as substitutes, governed Knowledge, legacy Knowledge, Prompt types, and duck-typed objects are forbidden.

Exact candidates must have internally valid deterministic `kc1_` identities. A duplicate candidate or reversed/noncanonical pair is malformed rather than silently repaired.

## 26. Deterministic identity requirements when applicable

The proposed policies are separate:

```text
record contract = knowledge-conflict-assessment-record-v1
identity prefix = kcf1_
identity policy ID = rcis-knowledge-conflict-assessment-record-identity
identity policy version = 1.0.0
canonicalization = knowledge-conflict-assessment-record-json-v1
digest = sha256
application policy ID = rcis-knowledge-pairwise-conflict-assessment
application policy version = 1.0.0
```

Identity includes the record contract, two ordered participant IDs/contracts/snapshot digests, scope, outcome, ordered reasons, actor, UTC-normalized assessed-at time with six fractional digits, exact application policy, and canonicalization contract. UTF-8 JSON, Unicode NFC, sorted keys, compact separators, finite values, and SHA-256 are required.

Diagnostics, review IDs, governance IDs, source paths, repository location, implicit time, randomness, list position, authority, lifecycle, resolution, promotion, acceptance, governed-Knowledge IDs, and persistence metadata remain outside identity. Exact replay yields the same `kcf1_`; every material identity-field change yields a different ID.

## 27. Application behavior and rejection model when applicable

The application result is explicit:

```text
result_status = recorded | rejected
conflict_assessment_record = KnowledgeConflictAssessmentRecord | None
reason_codes = tuple[str, ...]
diagnostics = tuple[KnowledgeConflictDiagnostic, ...]
```

Malformed programming inputs raise `ValueError`: wrong exact request/candidate/diagnostic types, non-tuple or wrong-length participants, duplicate or unordered candidates, broken candidate identity, mutable/empty/duplicate/unordered reason collections, empty required strings, invalid identifiers, or naive/wrong timestamps.

Valid but unsupported or incompatible requests return `rejected` with no record. Rejection precedence after structural validation is:

1. `unsupported_conflict_assessment_policy`;
2. `unsupported_conflict_assessment_outcome`;
3. `missing_required_conflict_assessment_reason`;
4. otherwise record one assessment.

The service preserves the caller tuple unchanged. It performs no semantic inference, subset selection, winner selection, automatic retry, conflict resolution, supersession, invalidation, authority assignment, lifecycle transition, promotion, acceptance, governed-object creation, repository access, or persistence.

## 28. Dependency and import decision

The safe dependency direction is:

```text
rie.application.knowledge_conflict_assessor
-> rie.domain.knowledge_conflict_assessment_record
-> rie.domain.knowledge_review_record snapshot helper
-> rie.domain.knowledge_candidate
```

The domain boundary may reuse the existing complete candidate snapshot digest helper without accepting a review record. The application imports exact candidates and the new conflict contracts. Existing candidate, review, and governance modules must not import the new boundary.

No interface, infrastructure, repository, filesystem, database, parser, network, AI, Prompt, CLI, legacy Knowledge, or runtime import is required.

## 29. Explicitly forbidden behavior

PR-028B must not:

- mutate candidate, review, or governance objects;
- accept raw dictionaries, paths, unresolved IDs, or duck types;
- discover candidates through repository or filesystem lookup;
- infer semantic relationships from strings, embeddings, AI, source authority, lifecycle, actor, time, order, IDs, or paths;
- claim global comparison completeness;
- select a winner or resolve conflict;
- deduplicate, merge, suppress, supersede, invalidate, or overwrite a candidate;
- assign authority or change lifecycle;
- create acceptance, promotion, prerequisite aggregate, governed/final Knowledge, or Prompt Candidate objects;
- add serialization, persistence, database, interface, infrastructure, CLI, API, UI, dashboard, AI, business, or legacy integration;
- change existing Phase 23 through Phase 27 contracts.

## 30. Deferred scope

Deferred work includes:

- automated semantic comparison and AI inference;
- candidate-versus-governed-Knowledge assessment;
- comparison-universe discovery and coverage certification;
- multi-candidate conflict aggregation, adjudication, and resolution;
- authority vocabulary and `KnowledgeAuthorityDecision`;
- promotion-prerequisite aggregate evaluation;
- governed-Knowledge contract and identity;
- initial lifecycle rule and later transition records;
- promotion decision, promotion record, and creation service;
- acceptance, final/locked state, supersession, and invalidation;
- `KnowledgeRepository`, serialization, persistence, databases, and migrations;
- Prompt Candidate, generator, AI, business, runtime, and legacy work.

## 31. Required-question answers

| ID | Answer |
|---:|---|
| 1 | `KnowledgeConflictAssessmentRecord` follows as the smallest implementable prerequisite producer. |
| 2 | Its subject is one canonical ordered pair of exact `KnowledgeCandidate` snapshots. |
| 3 | It is immutable explicit assessment evidence, not authorization, transition, creation, resolution, or persistence. |
| 4 | It operates on exactly two candidates per record. |
| 5 | It requires exact in-memory candidate objects; unresolved IDs are forbidden. |
| 6 | It preserves both `kc1_` IDs, candidate contracts, and complete snapshot digests; `kr1_` and `kg1_` remain separate for later aggregation. |
| 7 | Yes. Complete applicable semantic-conflict assessment is mandatory before promotion evaluation may succeed. |
| 8 | Yes. Pairwise assessment can remain repository-free; later comparison-universe completeness is separate. |
| 9 | No. Contradictory review evidence is governance-process evidence, not semantic conflict. |
| 10 | No. Contradictory governance evidence is not semantic conflict. |
| 11 | No. Source authority cannot determine Knowledge authority. |
| 12 | No. Candidate authority remains `unassessed`; future authority applies to governed Knowledge. |
| 13 | No. Candidate lifecycle remains `candidate` as immutable history. |
| 14 | No. Authorization implies no lifecycle transition. |
| 15 | Yes. Promotion must create a new governed-Knowledge identity. |
| 16 | No. Promotion cannot mutate `KnowledgeCandidate`. |
| 17 | Acceptance applies to governed Knowledge after creation, not to a candidate. |
| 18 | An explicit authority decision must precede promotion eligibility; the authority field is assigned at governed-object creation. |
| 19 | The initial lifecycle rule must be verified before creation; the initial value is assigned at creation, not by pre-creation transition. |
| 20 | Yes. A separate immutable conflict-assessment record is required. |
| 21 | Yes. A separate immutable authority decision is required before promotion evaluation. |
| 22 | Not for initial lifecycle assignment; yes for any later governed-Knowledge transition. |
| 23 | Yes. A separate immutable promotion record is required for the creation event. |
| 24 | Yes. Governed Knowledge may exist in memory without persistence. |
| 25 | No. `KnowledgeRepository` is not required for the next slice. |
| 26 | Conflict assessment, authority, prerequisite evaluation, creation, lifecycle, acceptance, supersession, and persistence remain separate. |
| 27 | Candidate review precedes governance; conflict and authority are independent prerequisites; aggregate evaluation precedes promotion; creation precedes acceptance/transitions; domain precedes repository. |
| 28 | The smallest slice is pairwise `KnowledgeConflictAssessmentRecord` plus a side-effect-free assessor. |
| 29 | Add exactly the four files in section 32; modify none. |
| 30 | Require 15 domain and 18 application matrix entries, 33 total, as section 33 specifies. |
| 31 | Authority, aggregate evaluation, promotion, governed Knowledge, lifecycle, acceptance, repository, persistence, Prompt, AI, business, runtime, and legacy work remain deferred. |
| 32 | Return to architecture review if pairwise exact objects, deterministic identity, no-inference behavior, or four-file scope cannot be preserved. |

## 32. Proposed file scope when approved

PR-028B should add exactly:

1. `src/rie/domain/knowledge_conflict_assessment_record.py` - diagnostic, participant, identity input, record, snapshot projection, and deterministic `kcf1_` identity;
2. `src/rie/application/knowledge_conflict_assessor.py` - exact request/result, supported policy and outcomes, required-reason checks, and side-effect-free record construction;
3. `tests/domain/test_knowledge_conflict_assessment_record.py` - frozen contracts, validation, canonical identity, replay, and exclusion tests;
4. `tests/application/test_knowledge_conflict_assessor.py` - outcomes, rejection precedence, exact boundary, immutability, and side-effect tests.

No existing file needs modification. If implementation requires another file, layer, or existing-file edit, stop and return to architecture review.

## 33. Proposed focused test matrix when approved

Domain matrix:

| ID | Exact assertion |
|---|---|
| D01 | Diagnostic, participant, identity-input, and assessment records are frozen, value-equal, and explicitly `kcf1_` identified |
| D02 | Contract, identity policy, canonicalization, digest, scope, outcomes, severities, and prefix constants are exact |
| D03 | Record ID requires `kcf1_` plus 64 lowercase hex characters and matches canonical content |
| D04 | Participant requires exact valid `kc1_`, candidate contract, and complete snapshot digest |
| D05 | Participants require an exact tuple of length two, unique IDs, and lexical order |
| D06 | Scope is exactly `pairwise_knowledge_candidate_semantic_relationship` |
| D07 | Only four exact assessment outcomes are accepted by a record |
| D08 | Required strings, ordered reasons, policy values, and timezone-aware time fail closed |
| D09 | Diagnostics accept exact immutable info/warning members and remain outside identity |
| D10 | Canonical identity uses UTF-8, NFC, sorted keys, compact separators, UTC microseconds, and SHA-256 |
| D11 | Exact replay returns identical canonical bytes and `kcf1_` identity |
| D12 | Participant, scope, outcome, reason, actor, time, policy, or contract changes identity |
| D13 | Review, governance, authority, lifecycle, resolution, promotion, repository, and persistence metadata are absent from identity |
| D14 | Snapshot, identity, participant, and record helpers reject wrong exact and duck-typed inputs |
| D15 | Identity extraction from a valid record round-trips exactly |

Application matrix:

| ID | Exact assertion |
|---|---|
| A01 | Two exact canonical candidates record `conflict_identified` with required reason and no mutation |
| A02 | `equivalent_statement` records only with `semantic_equivalence_identified` |
| A03 | `no_conflict_identified` is pair-limited and requires `pairwise_no_conflict_identified` |
| A04 | `assessment_deferred` records only with `semantic_assessment_deferred` |
| A05 | Every participant preserves exact candidate ID, contract, and complete snapshot digest |
| A06 | Exact replay produces the same record and `kcf1_` identity |
| A07 | Material request changes produce distinct identities without selecting a winner |
| A08 | Unsupported policy returns `unsupported_conflict_assessment_policy` with no record |
| A09 | Unsupported outcome returns `unsupported_conflict_assessment_outcome` with no record |
| A10 | Missing outcome-required reason returns `missing_required_conflict_assessment_reason` without repair |
| A11 | Empty, single, triple, duplicate, list, and wrong-type participant collections fail closed |
| A12 | Reversed/noncanonical candidate order fails closed and is not reordered |
| A13 | Raw dictionaries, paths, IDs, Evidence, review/governance objects, legacy Knowledge, Prompt, and duck types are rejected as substitutes |
| A14 | Broken candidate identity or snapshot consistency fails closed |
| A15 | Candidates, request, reason tuple, and recorded/rejected results remain unchanged |
| A16 | Review decision, governance decision, source authority, time, and lexical ID do not infer an outcome or winner |
| A17 | Recording creates no resolution, supersession, invalidation, authority, lifecycle, acceptance, promotion, governed Knowledge, repository, or persistence result |
| A18 | Production imports and runtime exclude interfaces, infrastructure, repository, filesystem, database, parser, network, subprocess, clock, randomness, UUID, AI, Prompt, CLI, retry, and legacy integration |

Matrix counts are exact:

```text
DOMAIN_MATRIX_ENTRY_COUNT = 15
APPLICATION_MATRIX_ENTRY_COUNT = 18
TOTAL_MATRIX_ENTRY_COUNT = 33
```

Focused execution after implementation, not during this review:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/domain/test_knowledge_conflict_assessment_record.py tests/application/test_knowledge_conflict_assessor.py -q
```

## 34. Definition of Done

PR-028A is complete when:

- the synchronized Phase 28 branch and exact local/remote Phase 27 tag are verified;
- current contracts, tests, relevant Phase 23 through Phase 27 documents, and prior reports are inspected read-only;
- the authoritative chain and all current distinctions are preserved;
- eight possible next boundaries are compared without assuming promotion;
- prerequisites are classified by exact timing;
- contradictory review/governance evidence is separated from semantic conflict;
- authority, lifecycle, acceptance, promotion, governed Knowledge, identity, provenance, supersession, repository, and persistence ordering is explicit;
- pairwise conflict assessment is selected as the smallest honest next boundary;
- its exact subject, fields, policies, identity, outcomes, reasons, rejection model, scope, and exclusions are defined;
- one exact four-file PR-028B and 33-entry focused matrix are approved;
- exactly this architecture document is created;
- no implementation, test, interpreter, existing-file, Git history, merge, or tag operation occurs.

## 35. Stop conditions

Stop PR-028B and return to architecture review if:

- exact in-memory `KnowledgeCandidate` pairs cannot remain the sole semantic inputs;
- the pair cannot remain exactly two, unique, and canonically ordered without repair;
- complete candidate snapshots cannot be reused consistently;
- the assessment would infer semantics automatically or require AI, embeddings, source ranking, repository discovery, or asset reads;
- a pairwise result would claim global comparison completeness;
- review or governance decisions would determine semantic outcome;
- conflict resolution, winner selection, deduplication, supersession, or invalidation becomes necessary;
- candidate, review, or governance mutation becomes necessary;
- authority, lifecycle, acceptance, promotion, governed Knowledge, repository, persistence, Prompt, runtime, business, or legacy work becomes necessary;
- deterministic identity requires implicit time, randomness, source path, repository location, list position, or mutable data;
- an existing Phase 23 through Phase 27 contract defect is found;
- implementation exceeds the exact four files or overlaps unrelated changes.

## 36. Final decision

# APPROVED FOR ONE MINIMAL PHASE 28 IMPLEMENTATION SLICE

The smallest honest next boundary is one immutable pairwise `KnowledgeConflictAssessmentRecord` and one side-effect-free assessor for two exact canonical `KnowledgeCandidate` snapshots. It records explicit assessment evidence only and does not infer, resolve, suppress, or globally clear semantic conflict.

Approval is limited to PR-028B and the four files in section 32. It does not claim implementation exists, tests passed for Phase 28, semantic conflict was assessed, authority was assigned, lifecycle changed, acceptance exists, promotion occurred, governed or final Knowledge exists, persistence exists, PR-028A was committed, or Phase 28 was merged or tagged.
