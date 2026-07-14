# PR-031A - Knowledge Promotion Decision Boundary and Dependency Review

## 1. Review identity

| Item | Reviewed value |
|---|---|
| Review | PR-031A |
| Type | Architecture review-only and documentation-only |
| Gate | Knowledge Promotion Decision Boundary and Dependency Review |
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-031-knowledge-promotion-decision-review` |
| Starting HEAD | `86a66811e5cb706ec1904a7c08d1378eee356000` |
| Tests executed | None |
| Project interpreter executed | No |

This review selects the smallest honest boundary after Phase 30. It creates no production code or tests and does not execute promotion, create governed Knowledge, initialize lifecycle, perform acceptance, persist data, or add runtime integration.

## 2. Repository checkpoint

| Item | Verified value |
|---|---|
| `HEAD` | `86a66811e5cb706ec1904a7c08d1378eee356000` |
| `main` | `86a66811e5cb706ec1904a7c08d1378eee356000` |
| `origin/main` | `86a66811e5cb706ec1904a7c08d1378eee356000` |
| Local Phase 31 ref | `86a66811e5cb706ec1904a7c08d1378eee356000` |
| Remote Phase 31 ref | `86a66811e5cb706ec1904a7c08d1378eee356000` |
| Local/remote Phase 31 divergence | `0 0` |
| Main/Phase 31 divergence | `0 0` |
| Starting tracked diff count | `0` |
| Starting staged file count | `0` |
| Starting repository status | Clean |
| Proposed document before review | Absent |

The branch, commit, refs, divergences, and clean state matched the required checkpoint before this document was created.

## 3. Phase 30 official tag verification

| Item | Verified value |
|---|---|
| Tag | `v0.30.0-rcis-knowledge-promotion-prerequisite-evaluation-phase` |
| Local type | `tag` |
| Local tag object | `96719a4a35bfaa17a2b5c42a85a1179bec7b9573` |
| Local peeled target | `86a66811e5cb706ec1904a7c08d1378eee356000` |
| Message | `RCIS Knowledge Promotion Prerequisite Evaluation Phase 30` |
| Remote tag object | `96719a4a35bfaa17a2b5c42a85a1179bec7b9573` |
| Remote peeled target | `86a66811e5cb706ec1904a7c08d1378eee356000` |
| Local verification | Passed |
| Remote verification without fetch | Passed |

The annotated tag establishes the authoritative Phase 30 prerequisite-evaluation checkpoint.

## 4. Authoritative material inspected

The review inspected the Phase 25 through Phase 30 architecture and closure chain:

- `docs/architecture/pr-025a-knowledge-construction-boundary-and-dependency-review.md` and `docs/architecture/pr-025d-knowledge-construction-phase-closure-review.md`;
- `docs/architecture/pr-026a-knowledge-governance-and-promotion-boundary-review.md` and `docs/architecture/pr-026d-knowledge-governance-phase-closure-review.md`;
- `docs/architecture/pr-027a-knowledge-governance-authorization-and-promotion-prerequisite-boundary-review.md` and `docs/architecture/pr-027d-knowledge-governance-authorization-phase-closure-review.md`;
- `docs/architecture/pr-028a-knowledge-promotion-prerequisite-and-next-domain-boundary-review.md` and `docs/architecture/pr-028d-pairwise-knowledge-conflict-assessment-phase-closure-review.md`;
- `docs/architecture/pr-029a-knowledge-authority-decision-and-promotion-prerequisite-boundary-review.md` and `docs/architecture/pr-029d-knowledge-authority-decision-phase-closure-review.md`;
- `docs/architecture/pr-030a-knowledge-promotion-prerequisite-evaluation-boundary-and-dependency-review.md` and `docs/architecture/pr-030d-knowledge-promotion-prerequisite-evaluation-phase-closure-review.md`.

The review inspected the corresponding Phase 25 through Phase 30 domain and application modules and their domain and application tests, including the exact Phase 30 files:

- `src/rie/domain/knowledge_promotion_prerequisite_evaluation.py`;
- `src/rie/application/knowledge_promotion_prerequisite_evaluator.py`;
- `tests/domain/test_knowledge_promotion_prerequisite_evaluation.py`;
- `tests/application/test_knowledge_promotion_prerequisite_evaluator.py`.

It also inspected `src/rie/domain/__init__.py`, `src/rie/application/__init__.py`, `pyproject.toml`, package discovery, and every filename containing promotion, governed, lifecycle, acceptance, repository, persistence, or knowledge. The initializers expose no manual export list, and setuptools discovers packages below `src`; no initializer or packaging edit is required.

The filename inventory contains Phase 30 promotion-prerequisite modules, earlier Evidence acceptance and Evidence repository contracts, and frozen legacy Knowledge surfaces. It contains no authoritative promotion decision, promotion execution, governed Knowledge, Knowledge acceptance, Knowledge lifecycle, Knowledge repository, or Knowledge persistence contract.

## 5. Current architecture chain

The exact non-collapsible chain is:

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
-> explicit pairwise semantic assessment
-> KnowledgeConflictAssessmentRecord
-> explicit authority decision
-> KnowledgeAuthorityDecision
-> promotion-prerequisite evaluation
-> KnowledgePromotionPrerequisiteEvaluation
-> future promotion decision
-> future promotion execution
-> future governed Knowledge
-> future acceptance/lifecycle
-> future Knowledge Repository
-> future Prompt Candidate
-> RCIS
```

Evaluation is not decision. Decision is not execution. Execution is not governed Knowledge creation unless a future architecture explicitly defines that action. Governed Knowledge is not acceptance. Acceptance is not lifecycle. Governed Knowledge is not repository persistence. Repository persistence is not Prompt Candidate creation. None of these responsibilities is business or creative approval.

## 6. Closed Phase 30 boundary

Phase 30 closed one immutable deterministic declared peer scope, one immutable `KnowledgePromotionPrerequisiteEvaluation`, and one side-effect-free evaluator. The `kpe1_` record binds the exact candidate ID, candidate contract, complete candidate snapshot digest, declared scope ID, ordered governance IDs, ordered conflict-assessment IDs, ordered authority-decision IDs, evaluation scope, declared-scope completeness basis, evaluation outcome, reasons, actor, caller time, and evaluation policy.

Its controlled outcomes are:

```text
prerequisites_satisfied_for_declared_scope
prerequisites_not_satisfied_for_declared_scope
prerequisites_deferred_for_declared_scope
```

A satisfied evaluation proves only that the supplied histories satisfy the Phase 30 prerequisites for the exact declared peer scope. It does not prove repository-global completeness, authorize promotion, execute promotion, create governed Knowledge, initialize lifecycle, perform acceptance, or persist anything.

## 7. Absent downstream-contract inventory

The authoritative `src/rie` boundary currently has no:

- `KnowledgePromotionDecision`;
- `KnowledgePromotionExecution`;
- governed `Knowledge` or `GovernedKnowledge`;
- governed Knowledge identity;
- Knowledge acceptance record;
- Knowledge lifecycle initialization or transition record;
- Knowledge supersession or invalidation record;
- `KnowledgeRepository` interface or adapter;
- Knowledge serialization or persistence contract;
- Prompt Candidate derived from the authoritative Knowledge chain.

Top-level legacy Knowledge and Prompt files remain frozen compatibility surfaces. Evidence acceptance and Evidence repository files govern Evidence, not governed Knowledge. Neither category fills a Phase 31 dependency.

## 8. Promotion-decision problem statement

Phase 30 produces evaluation evidence but deliberately does not decide whether promotion may proceed. A later action needs an explicit immutable record of one caller-supplied promotion decision while preserving exactly which candidate and evaluation were considered.

The decision must be narrow enough to avoid claiming global readiness and strong enough to prevent a satisfied evaluation from becoming implicit authorization. The smallest honest subject is one exact `KnowledgeCandidate` plus one exact `KnowledgePromotionPrerequisiteEvaluation` that references the same candidate representation.

No additional prerequisite producer is needed before that scope-limited decision can be represented. Repository-global completeness remains a separate future authority and is not silently supplied by Phase 31.

## 9. Evaluation-versus-decision separation

Evaluation answers whether Phase 30 prerequisites are satisfied, not satisfied, or deferred for one exact declared scope and exact supplied histories. Decision answers whether an explicit actor, under an explicit decision policy, authorizes only future execution, denies promotion, or defers the decision.

A satisfied evaluation is necessary for authorization but is not sufficient. The decision outcome, actor, reasons, time, and policy remain explicit caller inputs. The decider must not translate an evaluation outcome into a decision outcome, insert reasons, acquire current time, or retry.

## 10. Candidate and evaluation lineage

The decision request must receive one exact in-memory `KnowledgeCandidate` and one exact in-memory `KnowledgePromotionPrerequisiteEvaluation`. Unresolved IDs are insufficient because the application must recompute both deterministic identities and the complete candidate snapshot without repository lookup.

The decision record directly preserves:

- candidate ID;
- candidate contract version;
- complete candidate snapshot digest;
- prerequisite-evaluation ID;
- prerequisite-evaluation contract version;
- prerequisite-evaluation outcome.

The evaluation ID commits indirectly to its declared scope, governance, conflict, authority, evaluation reason, actor, time, and policy lineage. Direct governance, conflict, or authority records are unnecessary and would duplicate Phase 30. Review lineage remains indirect through governance and the evaluation. AcceptedEvidence lineage remains indirect through the complete candidate snapshot. No upstream object is copied, changed, or replaced.

## 11. Declared-scope versus global completeness

Declared-scope evidence is sufficient for a scope-limited decision because the decision binds the exact `kpe1_` record and preserves its outcome. It is not sufficient for a repository-global readiness claim.

The exact authorization scope is:

```text
eligible_for_future_promotion_execution_for_declared_scope
```

Every positive statement must retain `for_declared_scope`, `scope-limited`, or an equivalent explicit qualifier. The record does not assert that every candidate, peer, governance decision, conflict assessment, authority decision, or historical record in a repository was considered. A repository-aware global boundary remains future work.

## 12. Decision-subject alternatives

Binding only the candidate loses the exact evaluation event and its declared-scope evidence. Binding only an evaluation ID prevents exact runtime identity verification without lookup and omits direct candidate snapshot verification. Re-consuming all Phase 30 prerequisite records collapses evaluation and decision.

The exact candidate plus exact evaluation object pair is therefore the smallest complete in-memory subject. The candidate supplies direct immutable subject verification; the evaluation supplies the complete scope-relative prerequisite lineage.

## 13. Required input analysis

The proposed `KnowledgePromotionDecisionRequest` fields, in order, are:

1. `knowledge_candidate: KnowledgeCandidate`;
2. `promotion_prerequisite_evaluation: KnowledgePromotionPrerequisiteEvaluation`;
3. `promotion_decision: str`;
4. `reason_codes: tuple[str, ...]`;
5. `decided_by: str`;
6. `decided_at: datetime`;
7. `decision_policy_id: str`;
8. `decision_policy_version: str`.

The candidate and evaluation must be exact runtime types with valid recomputed identities. Reasons must be a non-empty exact tuple of non-empty strings, unique and lexicographically ordered. Actor and policy values must be non-empty exact strings. Time must be an exact timezone-aware `datetime` supplied by the caller.

Raw dictionaries, paths, IDs, legacy Knowledge, Prompt objects, Evidence objects, duck-typed substitutes, mutable collections, naive timestamps, and implicit values are forbidden.

## 14. Outcome semantics

The exact decision outcomes are:

| Outcome | Controlled meaning |
|---|---|
| `promotion_authorized_for_future_execution` | The exact candidate and exact satisfied declared-scope evaluation are eligible only for a separate future promotion-execution boundary |
| `promotion_denied` | The explicit policy decision does not authorize future execution; it does not mutate or erase the candidate or evaluation |
| `promotion_decision_deferred` | No authorization or denial is recorded; a later explicit decision may be represented independently |

The words `approved`, `ready`, `final`, `promoted`, `accepted`, `governed`, and `complete` are not decision values because they collapse later responsibilities or imply unproved completeness.

The exact matrix-required reasons are:

```text
satisfied_evaluation_supports_future_execution_authorization
promotion_denied_despite_satisfied_evaluation
promotion_decision_deferred_despite_satisfied_evaluation
promotion_denied_for_not_satisfied_evaluation
promotion_decision_deferred_for_not_satisfied_evaluation
promotion_decision_deferred_for_deferred_evaluation
```

The applicable reason must already appear in the caller's ordered tuple. Additional non-empty caller reasons may be present when unique and ordered. The application does not insert, remove, reorder, normalize, or repair reasons.

## 15. Evaluation-to-decision compatibility matrix

All nine combinations below are structurally well-formed when their individual values and objects are valid. Compatibility is an application-policy question, so incompatible combinations return an explicit rejected result rather than raising `ValueError`.

| Evaluation outcome | Requested decision | Application result | Required reason or rejection |
|---|---|---|---|
| `prerequisites_satisfied_for_declared_scope` | `promotion_authorized_for_future_execution` | Record | `satisfied_evaluation_supports_future_execution_authorization` |
| `prerequisites_satisfied_for_declared_scope` | `promotion_denied` | Record | `promotion_denied_despite_satisfied_evaluation` |
| `prerequisites_satisfied_for_declared_scope` | `promotion_decision_deferred` | Record | `promotion_decision_deferred_despite_satisfied_evaluation` |
| `prerequisites_not_satisfied_for_declared_scope` | `promotion_authorized_for_future_execution` | Reject | `ineligible_prerequisite_evaluation` |
| `prerequisites_not_satisfied_for_declared_scope` | `promotion_denied` | Record | `promotion_denied_for_not_satisfied_evaluation` |
| `prerequisites_not_satisfied_for_declared_scope` | `promotion_decision_deferred` | Record | `promotion_decision_deferred_for_not_satisfied_evaluation` |
| `prerequisites_deferred_for_declared_scope` | `promotion_authorized_for_future_execution` | Reject | `incomplete_prerequisite_evaluation` |
| `prerequisites_deferred_for_declared_scope` | `promotion_denied` | Reject | `incomplete_prerequisite_evaluation` |
| `prerequisites_deferred_for_declared_scope` | `promotion_decision_deferred` | Record | `promotion_decision_deferred_for_deferred_evaluation` |

No evaluation automatically creates an authorized, denied, or deferred decision. A not-satisfied evaluation constrains authorization but does not auto-deny. A deferred evaluation permits only an explicit deferred decision because incomplete evidence cannot authorize or deny.

## 16. Authorization-scope analysis

`promotion_authorized_for_future_execution` under scope `eligible_for_future_promotion_execution_for_declared_scope` means only that a future execution boundary may consider the exact subject. It is not execution authority by itself and does not waive future execution checks.

Authorization cannot execute promotion, create governed Knowledge, mutate the candidate, mutate the evaluation, alter governance/conflict/authority history, initialize lifecycle, accept Knowledge, select a historical winner, or persist state.

## 17. Historical coexistence and contradiction behavior

Exact replay produces an equal decision with the same deterministic ID. Materially different decisions produce different immutable records. Authorized, denied, and deferred decisions for the same candidate and evaluation may coexist as explicit history.

Contradictory decisions are represented by coexistence, not overwrite or winner selection. Actor, timestamp, record age, lexical ID, tuple position, source authority, or input order cannot rank them. No decision supersedes another without a separate future policy and record. Latest-wins is forbidden.

Durable duplicate suppression, historical queries, contradiction adjudication, supersession, and invalidation require a later repository-aware architecture. The Phase 31 decider performs none of them.

## 18. Identity analysis

The proposed deterministic identity contract is:

```text
class_name = KnowledgePromotionDecision
module = rie.domain.knowledge_promotion_decision
contract_version = knowledge-promotion-decision-v1
id_prefix = kpd1_
identity_policy_id = rcis-knowledge-promotion-decision-identity
identity_policy_version = 1.0.0
canonicalization_contract = knowledge-promotion-decision-json-v1
digest_algorithm = sha256
timestamp_normalization = UTC with six fractional digits
```

Identity includes:

1. decision-record contract version;
2. candidate ID, candidate contract, and complete candidate snapshot digest;
3. prerequisite-evaluation ID, evaluation contract, and evaluation outcome;
4. authorization scope;
5. promotion decision;
6. ordered reason codes;
7. `decided_by`;
8. caller-supplied `decided_at` normalized to UTC;
9. decision policy ID and version;
10. identity canonicalization contract.

Canonical bytes use UTF-8 JSON, NFC text, sorted keys, compact separators, finite values only, and SHA-256. Diagnostics are excluded.

Identity also excludes repository and filesystem paths, implicit current time, randomness, UUID, mutable metadata, tuple position as authority, latest-record selection, execution result, governed Knowledge identity, lifecycle state, acceptance state, persistence metadata, Prompt Candidate, and AI output.

## 19. Structural validity

Malformed programming inputs raise `ValueError` before application-policy evaluation. Malformed inputs include:

- wrong exact request, candidate, evaluation, diagnostic, or result types;
- duck-typed substitutes;
- invalid `kc1_`, `kpe1_`, or `kpd1_` form;
- candidate, evaluation, or decision ID that does not match canonical content;
- non-string, empty, or whitespace-only required values;
- non-tuple, empty, duplicate, unordered, non-string, or blank reason collections;
- wrong-type or timezone-naive `decided_at`;
- unsupported decision-record contract, authorization scope, or canonicalization contract;
- inconsistent recorded/rejected result invariants;
- mutable or non-canonical collection shapes.

Structural validation does not decide whether a well-formed policy or outcome is supported.

## 20. Unsupported-input behavior

Structurally valid but unsupported or incompatible requests return `result_status="rejected"`, no decision record, one exact rejection reason, and one matching warning diagnostic. They do not raise `ValueError` solely for the unsupported condition.

This category includes an unsupported decision policy, unsupported non-empty decision outcome, a valid evaluation from an unsupported evaluation policy, candidate/evaluation lineage mismatch, an evaluation/decision combination forbidden by section 15, and a compatible combination missing its required decision reason.

The application never repairs unsupported input, converts outcomes, selects a different evaluation, performs lookup, retries, or mutates an object.

## 21. Rejection vocabulary and precedence

The exact ordered rejection vocabulary is:

| Precedence | Reason | Exact condition |
|---:|---|---|
| 1 | `unsupported_promotion_decision_policy` | Decision application policy ID or version is unsupported |
| 2 | `unsupported_promotion_decision` | Caller-supplied non-empty decision value is unsupported |
| 3 | `unsupported_prerequisite_evaluation_policy` | Exact valid evaluation uses another evaluation policy ID or version |
| 4 | `decision_candidate_mismatch` | Evaluation references another candidate ID |
| 5 | `decision_candidate_contract_mismatch` | Evaluation references another candidate contract |
| 6 | `decision_candidate_snapshot_mismatch` | Evaluation snapshot differs from the recomputed complete candidate snapshot |
| 7 | `ineligible_prerequisite_evaluation` | Not-satisfied evaluation is asked to authorize |
| 8 | `incomplete_prerequisite_evaluation` | Deferred evaluation is asked to authorize or deny |
| 9 | `missing_required_promotion_decision_reason` | Otherwise compatible request omits its matrix-required reason |

This first-applicable precedence begins only after structural validation succeeds. No later compatible fact overrides an earlier rejection. Exactly one rejection is returned, and no automatic retry occurs.

## 22. Application-result and diagnostic vocabulary

The exact result statuses are:

```text
recorded
rejected
```

The exact diagnostic severities are:

```text
info
warning
```

`KnowledgePromotionDecisionResult` fields, in order, are:

1. `result_status: str`;
2. `promotion_decision_record: KnowledgePromotionDecision | None`;
3. `reason_codes: tuple[str, ...]`;
4. `diagnostics: tuple[KnowledgePromotionDecisionDiagnostic, ...]`.

A recorded result contains one exact record and empty result reasons and diagnostics. A rejected result contains no record, exactly one approved rejection reason, and exactly one warning diagnostic whose code equals that reason. Domain diagnostics are immutable and outside identity; the initial decider constructs no record diagnostics.

## 23. Dependency direction

The safe dependency direction is:

```text
rie.application.knowledge_promotion_decider
-> rie.domain.knowledge_promotion_decision
-> rie.domain.knowledge_candidate identity helpers
-> rie.domain.knowledge_promotion_prerequisite_evaluation identity helpers
```

The application may also import the exact Phase 30 evaluation-policy and outcome constants. Earlier Phase 25 through Phase 30 modules must not import Phase 31 modules. No circular dependency or package initializer edit is required.

No repository, persistence, serialization, interface, infrastructure, CLI, API, UI, dashboard, Prompt, AI, network, filesystem, database, subprocess, clock, randomness, UUID, or legacy dependency is permitted.

## 24. Repository and persistence decision

A repository is not required for one scope-limited in-memory decision because the caller supplies the exact candidate and exact evaluation objects. Repository-global completeness is not required and is not claimed. Persistence and serialization are not required because the application returns one immutable record or explicit rejection.

A future repository-aware boundary is still required for global candidate-universe completeness, complete-history claims, durable duplicate handling, contradiction queries, adjudication, supersession, invalidation, and persistence. The present decision remains honest only because its subject and authorization scope are explicitly declared-scope limited.

## 25. Downstream separation

The proposed boundary does not:

- execute promotion;
- create governed Knowledge;
- initialize or transition lifecycle;
- perform acceptance;
- persist or serialize;
- query a repository;
- claim global completeness;
- infer missing evaluations or authority;
- inherit source authority;
- resolve conflicts or select winners;
- mutate upstream records;
- acquire implicit current time;
- use randomness or UUID;
- retry;
- call AI or generate Prompt Candidates;
- introduce business or creative approval;
- introduce legacy, infrastructure, or interface integration.

`KnowledgePromotionExecution`, governed Knowledge, governed identity, lifecycle, acceptance, supersession, invalidation, repository persistence, serialization, Prompt Candidate, AI, CLI, API, UI, dashboard, infrastructure, interfaces, and legacy integration remain absent and future.

## 26. Alternative comparison matrix

| Alternative | Inputs | Identity | Lineage | Completeness semantics | Repository | Persistence | Forbidden side effects | Safety | Decision |
|---|---|---|---|---|---|---|---|---|---|
| A. Explicit decision bound to candidate and exact evaluation | Exact candidate and exact evaluation | Deterministic `kpd1_` | Direct candidate and evaluation; upstream indirect through `kpe1_` | Declared-scope only | No | No | No execution or mutation | Safe | Select |
| B. Decision bound only to candidate | Exact candidate | Could be deterministic but omits evidence | Evaluation lineage absent | Unstated | No | No | Risks evidence-free authorization | Unsafe | Reject |
| C. Decision bound only to evaluation ID | Unresolved `kpe1_` | ID cannot be recomputed from an object | Candidate snapshot verification absent | Hidden behind lookup | Yes | Not inherently | Requires resolution | Unsafe | Reject |
| D. Decision consumes all governance/conflict/authority records | Candidate and all Phase 30 inputs | Duplicates evaluation identity | Repeats and may diverge from `kpe1_` | Re-evaluates caller scope | No | No | Collapses evaluation and decision | Unsafe | Reject |
| E. Combined evaluation and decision | All prerequisites plus decision | One collapsed identity | Responsibilities indistinguishable | Declared scope may imply authorization | No | No | Automatic conversion risk | Unsafe | Reject |
| F. Combined decision and execution | Candidate, evaluation, execution inputs | Mixes intent and effect | Execution result contaminates decision | Unclear | Possibly | Possibly | Executes promotion | Unsafe | Reject |
| G. Combined decision and governed Knowledge creation | Candidate, evaluation, future object fields | Mixes decision and governed identity | Creation lineage incomplete | Unclear | No | No | Creates governed Knowledge | Unsafe | Reject |
| H. Candidate mutation with promotion status | Mutable candidate | Reuses `kc1_` incorrectly | Historical decision erased | Implied global state | No | No | Mutates upstream object | Unsafe | Reject |
| I. Latest-wins decision | Candidate, evaluation, prior decisions | Order-dependent | Loses contradictory history | Depends on selected history | Yes | Yes | Selects a winner | Unsafe | Reject |
| J. Repository-backed global decision | Repository universe and histories | Requires new global policy | Potentially global | Repository-global | Yes | Yes | Adds lookup and persistence | Premature | Defer |
| K. Authorization record without deterministic identity | Candidate and evaluation | None | Replay and material changes ambiguous | Declared scope possible | No | No | Weak auditability | Unsafe | Reject |
| L. Scope-relative future-execution-only decision | Exact candidate and exact evaluation | Deterministic `kpd1_` | Direct exact subject and `kpe1_` lineage | Explicitly non-global | No | No | No execution or creation | Safe | Same selected boundary |

Alternatives A and L describe the same selected minimal contract. L supplies the mandatory scope and authorization wording that makes A honest.

## 27. Preferred smallest next boundary

The preferred smallest next boundary is one immutable `KnowledgePromotionDecision` plus one side-effect-free promotion decider. It binds one exact `KnowledgeCandidate` and one exact `KnowledgePromotionPrerequisiteEvaluation` and records one explicit caller-supplied decision.

No additional prerequisite object is required before this scope-limited decision. Phase 30 already commits the exact declared scope and supplied governance, conflict, and authority histories. Phase 31 must consume that evaluation as evidence, not recompute it or treat it as automatic authorization.

## 28. Exact proposed domain contract

The proposed domain module is `rie.domain.knowledge_promotion_decision`.

Exact constants:

```text
KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION = knowledge-promotion-decision-v1
KNOWLEDGE_PROMOTION_DECISION_ID_PREFIX = kpd1_
KNOWLEDGE_PROMOTION_DECISION_IDENTITY_POLICY_ID = rcis-knowledge-promotion-decision-identity
KNOWLEDGE_PROMOTION_DECISION_IDENTITY_POLICY_VERSION = 1.0.0
KNOWLEDGE_PROMOTION_DECISION_IDENTITY_CANONICALIZATION_CONTRACT = knowledge-promotion-decision-json-v1
KNOWLEDGE_PROMOTION_DECISION_DIGEST_ALGORITHM = sha256
PROMOTION_DECISION_AUTHORIZATION_SCOPE = eligible_for_future_promotion_execution_for_declared_scope
PROMOTION_DECISION_OUTCOME_AUTHORIZED = promotion_authorized_for_future_execution
PROMOTION_DECISION_OUTCOME_DENIED = promotion_denied
PROMOTION_DECISION_OUTCOME_DEFERRED = promotion_decision_deferred
KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_INFO = info
KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING = warning
```

All three dataclasses are `@dataclass(frozen=True)`.

`KnowledgePromotionDecisionDiagnostic` fields, in order:

```text
code: str
severity: str
message: str
field: str
source: str
```

`KnowledgePromotionDecisionIdentityInput` fields, in order:

```text
decision_record_contract_version: str
knowledge_candidate_id: str
knowledge_candidate_contract_version: str
knowledge_candidate_snapshot_digest: str
knowledge_promotion_prerequisite_evaluation_id: str
knowledge_promotion_prerequisite_evaluation_contract_version: str
promotion_prerequisite_evaluation_outcome: str
authorization_scope: str
promotion_decision: str
reason_codes: tuple[str, ...]
decided_by: str
decided_at: datetime
decision_policy_id: str
decision_policy_version: str
```

`KnowledgePromotionDecision` fields, in order:

```text
knowledge_promotion_decision_id: str
contract_version: str
knowledge_candidate_id: str
knowledge_candidate_contract_version: str
knowledge_candidate_snapshot_digest: str
knowledge_promotion_prerequisite_evaluation_id: str
knowledge_promotion_prerequisite_evaluation_contract_version: str
promotion_prerequisite_evaluation_outcome: str
authorization_scope: str
promotion_decision: str
reason_codes: tuple[str, ...]
decided_by: str
decided_at: datetime
decision_policy_id: str
decision_policy_version: str
diagnostics: tuple[KnowledgePromotionDecisionDiagnostic, ...]
```

The module provides exact candidate/evaluation verification helpers, complete candidate snapshot projection through the established helper, canonical identity projection and bytes, `compute_knowledge_promotion_decision_id`, and identity-input extraction from a record. Every public helper rejects wrong exact and duck-typed values. Replay, identity inclusion/exclusion, collection ordering, uniqueness, and coexistence follow sections 17 through 19.

## 29. Exact proposed application contract

The proposed application module is `rie.application.knowledge_promotion_decider`.

Exact application constants:

```text
KNOWLEDGE_PROMOTION_DECISION_POLICY_ID = rcis-knowledge-promotion-decision
KNOWLEDGE_PROMOTION_DECISION_POLICY_VERSION = 1.0.0
PROMOTION_DECISION_RESULT_STATUS_RECORDED = recorded
PROMOTION_DECISION_RESULT_STATUS_REJECTED = rejected
```

The application surface is exactly:

```text
KnowledgePromotionDecisionRequest
KnowledgePromotionDecisionResult
decide_knowledge_promotion(request)
```

The request fields are exactly those in section 13. The result fields and invariants are exactly those in section 22. The function requires an exact request, reruns structural validation, checks the supported decision policy, supported decision value, exact upstream evaluation policy, candidate/evaluation compatibility, the complete section 15 matrix, and the required reason in the exact section 21 precedence.

The application copies caller policy, outcome, reasons, actor, and time unchanged into a recorded decision. It performs no inference, outcome conversion, reason insertion, lookup, I/O, mutation, retry, execution, governed creation, or integration.

## 30. Exact proposed implementation slice

The proposed follow-up title is:

```text
PR-031B - Minimal KnowledgePromotionDecision and Promotion Decider Contract Implementation
```

The proposed slice is exactly four additive files:

1. `src/rie/domain/knowledge_promotion_decision.py`;
2. `src/rie/application/knowledge_promotion_decider.py`;
3. `tests/domain/test_knowledge_promotion_decision.py`;
4. `tests/application/test_knowledge_promotion_decider.py`.

No fifth file, package initializer edit, existing contract edit, repository, persistence, serialization, interface, infrastructure, configuration, dependency, CLI, API, UI, dashboard, Prompt, AI, or legacy file is required.

## 31. Exact 20-domain/30-application test matrix

The implementation matrix is exactly 50 distinct, non-parametrized test functions: D01 through D20 and A01 through A30.

### Domain matrix

| ID | Exact assertion |
|---|---|
| D01 | Diagnostic, identity-input, and decision records are exact frozen dataclasses with exact field order |
| D02 | Contract, prefix, identity policy, canonicalization, digest, scope, outcome, reason, severity, result, and rejection constants are exact |
| D03 | Candidate ID requires exact `kc1_` form and candidate contract and snapshot are required |
| D04 | Evaluation ID requires exact `kpe1_` form and evaluation contract and outcome are required |
| D05 | Decision ID requires `kpd1_` plus 64 lowercase hex characters and must match canonical content |
| D06 | Authorization scope is exactly declared-scope future-execution eligibility |
| D07 | Only the three exact promotion decision outcomes are recordable |
| D08 | Reasons are an exact non-empty unique lexically ordered tuple of non-empty strings |
| D09 | Actor, policy values, and exact timezone-aware caller time fail closed |
| D10 | Diagnostics accept only exact immutable info/warning members |
| D11 | Diagnostics remain outside identity |
| D12 | Canonical identity uses UTF-8, NFC, sorted keys, compact separators, finite values, and UTC microseconds |
| D13 | Exact replay returns identical canonical bytes and `kpd1_` identity |
| D14 | Every material candidate field changes identity or fails closed |
| D15 | Every material evaluation field changes identity or fails closed |
| D16 | Scope, decision, reason, actor, time, policy, or contract changes identity |
| D17 | Candidate and evaluation identity verification helpers reject broken identities |
| D18 | Identity helpers reject wrong exact and duck-typed values |
| D19 | Repository/path, implicit/random, execution, governed, lifecycle, acceptance, persistence, Prompt, and AI metadata are absent |
| D20 | Identity extraction from a valid decision round-trips exactly |

### Application matrix

| ID | Exact assertion |
|---|---|
| A01 | Satisfied evaluation plus explicit authorized decision and exact reason records future-execution-only authorization |
| A02 | Satisfied evaluation does not auto-authorize and a missing required authorization reason rejects |
| A03 | Satisfied evaluation may record explicit denial with its exact reason |
| A04 | Satisfied evaluation may record explicit deferral with its exact reason |
| A05 | Not-satisfied evaluation cannot authorize and returns `ineligible_prerequisite_evaluation` |
| A06 | Not-satisfied evaluation may record explicit denial with its exact reason |
| A07 | Not-satisfied evaluation may record explicit deferral with its exact reason |
| A08 | Deferred evaluation cannot authorize and returns `incomplete_prerequisite_evaluation` |
| A09 | Deferred evaluation cannot deny and returns `incomplete_prerequisite_evaluation` |
| A10 | Deferred evaluation may record only explicit deferral with its exact reason |
| A11 | Unsupported decision policy ID or version rejects first |
| A12 | Unsupported non-empty decision outcome rejects after policy and before evaluation checks |
| A13 | Unsupported exact evaluation policy rejects before candidate compatibility checks |
| A14 | Evaluation candidate ID mismatch returns `decision_candidate_mismatch` |
| A15 | Evaluation candidate contract mismatch returns `decision_candidate_contract_mismatch` |
| A16 | Evaluation candidate snapshot mismatch returns `decision_candidate_snapshot_mismatch` |
| A17 | Every compatible combination missing its matrix reason rejects without repair |
| A18 | Rejection precedence is exact when multiple unsupported conditions coexist |
| A19 | Recorded result contains one exact decision and empty result reasons and diagnostics |
| A20 | Rejected result contains no record, one reason, and one matching warning diagnostic |
| A21 | Exact replay is equal and returns the same `kpd1_`; material request changes alter identity |
| A22 | Exact candidate and evaluation inputs and request/result records remain unchanged and frozen |
| A23 | Authorized and denied decisions for one subject coexist without winner selection |
| A24 | Deferred decisions coexist and no decision supersedes another |
| A25 | Actor, timestamp, lexical ID, age, and tuple position never select a winner |
| A26 | Wrong objects, raw IDs, paths, dictionaries, legacy Knowledge, Prompt, and duck types raise `ValueError` |
| A27 | No current-time acquisition, retry, randomness, UUID, logging, subprocess, filesystem, or network behavior occurs |
| A28 | No promotion execution, candidate/evaluation mutation, or governed Knowledge creation occurs |
| A29 | No repository, persistence, serialization, lifecycle, acceptance, Prompt, AI, interface, infrastructure, or legacy behavior occurs |
| A30 | Production imports preserve the exact Phase 31 dependency direction and earlier modules do not import Phase 31 |

The counts are exact:

```text
DOMAIN_MATRIX_ENTRY_COUNT = 20
APPLICATION_MATRIX_ENTRY_COUNT = 30
TOTAL_MATRIX_ENTRY_COUNT = 50
```

No parametrization or matrix-count change is approved.

## 32. Definition of Done

PR-031A is complete when:

- the required branch, commit, refs, divergences, clean start, and Phase 30 local/remote annotated tag are verified;
- Phase 25 through Phase 30 architecture, implementation contracts, tests, closures, initializers, package boundary, and requested filename inventory are inspected;
- the mandatory architecture chain remains non-collapsible;
- Phase 30 evaluation is preserved as evidence, not decision or execution;
- the exact candidate-plus-evaluation subject and direct/indirect lineage are defined;
- declared-scope authorization is distinguished from global completeness;
- the three decisions, one authorization scope, six required reasons, nine compatibility combinations, nine rejection reasons, and exact precedence are defined;
- deterministic `kpd1_` identity, replay, coexistence, and identity exclusions are explicit;
- malformed versus structurally valid unsupported behavior is explicit;
- repository, persistence, execution, governed Knowledge, lifecycle, acceptance, Prompt, AI, interfaces, infrastructure, and legacy work remain absent;
- exactly the four-file PR-031B proposal and 20-domain/30-application/50-total matrix are defined;
- exactly this documentation file and one external report are created;
- no interpreter, tests, existing repository file, Git history, package, permission, or line-ending action occurs.

## 33. Stop conditions

Do not proceed with PR-031B if:

- promotion decision cannot remain separate from execution;
- a positive evaluation must automatically authorize promotion;
- repository-global completeness, lookup, persistence, or serialization is required;
- upstream mutation, winner selection, latest-wins, supersession, or invalidation is required;
- implicit time, randomness, UUID, path, tuple position, or mutable metadata is required for identity;
- governed Knowledge creation, lifecycle, or acceptance is required;
- direct governance/conflict/authority inputs become necessary instead of exact evaluation lineage;
- exact candidate/evaluation compatibility or the nine-combination matrix cannot be enforced;
- a fifth file, existing-contract edit, or initializer edit is required;
- Prompt, AI, CLI, API, UI, dashboard, infrastructure, interface, business, creative, or legacy work is required;
- deterministic identity cannot be defined without side effects or hidden inference.

Any such condition requires another architecture review rather than scope expansion.

## 34. Required-question answers

| ID | Answer |
|---:|---|
| 1 | Yes. An explicit immutable promotion decision is the smallest honest next boundary. |
| 2 | It binds one exact candidate representation and one exact prerequisite-evaluation event. |
| 3 | Yes, one exact `KnowledgeCandidate` is required. |
| 4 | Yes, one exact `KnowledgePromotionPrerequisiteEvaluation` is required. |
| 5 | Yes, candidate ID, contract, and complete snapshot are preserved directly. |
| 6 | Yes, evaluation ID and evaluation contract are preserved directly. |
| 7 | Yes, evaluation outcome is preserved directly. |
| 8 | Yes, a satisfied evaluation is necessary for authorization. |
| 9 | No, a satisfied evaluation is not sufficient and never auto-authorizes. |
| 10 | Yes, authorization may exist only for a satisfied evaluation. |
| 11 | Yes, a satisfied evaluation may be explicitly denied with the required reason. |
| 12 | Yes, a satisfied evaluation may be explicitly deferred with the required reason. |
| 13 | Not-satisfied may deny or defer but must reject authorization. |
| 14 | Deferred evaluation permits only deferred decision; authorization and denial reject as incomplete. |
| 15 | Yes, decision outcomes remain caller-supplied and are never inferred. |
| 16 | `promotion_authorized_for_future_execution`, `promotion_denied`, and `promotion_decision_deferred`. |
| 17 | `eligible_for_future_promotion_execution_for_declared_scope`. |
| 18 | Yes, authorization means eligibility for a separate future execution boundary only. |
| 19 | No, authorization cannot execute promotion. |
| 20 | No, authorization cannot create governed Knowledge. |
| 21 | No, it cannot mutate `KnowledgeCandidate`. |
| 22 | No, it cannot mutate the evaluation. |
| 23 | No, it cannot alter governance, conflict, or authority history. |
| 24 | No, it cannot select a historical winner. |
| 25 | No actor, timestamp, lexical ID, record age, or tuple position may select a winner. |
| 26 | Yes, multiple promotion decisions coexist as immutable history. |
| 27 | Contradictions are represented by independent coexisting records. |
| 28 | No decision supersedes another without a separate future policy and record. |
| 29 | Latest-wins is forbidden. |
| 30 | No, repository-global completeness is not required or claimed. |
| 31 | Yes, declared-scope evidence is sufficient for one explicitly scope-limited decision. |
| 32 | The authorization scope and every positive statement explicitly say declared-scope or scope-limited and deny global readiness. |
| 33 | No direct governance, conflict, or authority records are required. |
| 34 | Exact evaluation lineage is sufficient. |
| 35 | Yes, review lineage remains indirect through governance and the evaluation. |
| 36 | Yes, AcceptedEvidence lineage remains indirect through the complete candidate snapshot. |
| 37 | Identity includes all fields enumerated in section 18. |
| 38 | Diagnostics and all location, implicit, mutable, downstream, persistence, Prompt, and AI metadata remain outside identity. |
| 39 | The malformed inputs in section 19 raise `ValueError`. |
| 40 | The unsupported and incompatible inputs in sections 20 and 21 return explicit rejection. |
| 41 | Exactly `recorded` and `rejected`. |
| 42 | Immutable info/warning diagnostics; rejection uses exactly one matching warning diagnostic. |
| 43 | The exact first-applicable nine-step precedence in section 21. |
| 44 | No persistence is required. |
| 45 | No repository is required. |
| 46 | No serialization is required. |
| 47 | No CLI, API, UI, or dashboard integration is required. |
| 48 | No package initializer edit is required. |
| 49 | Yes, the next implementation can remain exactly four additive files. |
| 50 | Exactly 20 domain plus 30 application tests, 50 total, one non-parametrized function per D01-D20 and A01-A30. |

## 35. Final decision

# APPROVED FOR ONE MINIMAL PHASE 31 KNOWLEDGE PROMOTION DECISION IMPLEMENTATION SLICE

The smallest honest next boundary is one immutable `KnowledgePromotionDecision` and one side-effect-free promotion decider bound to one exact `KnowledgeCandidate` and one exact `KnowledgePromotionPrerequisiteEvaluation`. Approval is limited to the proposed PR-031B title, four additive files, and exact 50-test matrix in sections 30 and 31.

Authorization remains scope-limited eligibility for a separate future promotion-execution boundary. This decision does not approve or perform execution, governed Knowledge creation, lifecycle, acceptance, repository-global completeness, persistence, serialization, Prompt Candidate creation, AI, business or creative approval, runtime integration, or legacy migration.
