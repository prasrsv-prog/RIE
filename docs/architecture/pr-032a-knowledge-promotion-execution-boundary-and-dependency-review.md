# PR-032A - Knowledge Promotion Execution Boundary and Dependency Review

## 1. Review identity

| Item | Reviewed value |
|---|---|
| Review | PR-032A |
| Type | Review-only and documentation-only |
| Gate | Knowledge Promotion Execution Boundary and Dependency Review |
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-032-knowledge-promotion-execution-review` |
| Starting HEAD | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |
| Tests executed | None |
| Project interpreter executed | No |

This review identifies the smallest honest execution boundary after `KnowledgePromotionDecision`. It creates no implementation, executes no promotion request, creates no governed Knowledge, performs no persistence, and changes no Git history.

## 2. Repository checkpoint

| Item | Verified value |
|---|---|
| Branch | `phase-032-knowledge-promotion-execution-review` |
| `HEAD` | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |
| `main` | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |
| `origin/main` | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |
| Local Phase 32 ref | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |
| Remote Phase 32 ref | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |
| Live remote Phase 32 ref | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |
| Local/remote divergence | `0 0` |
| `main`/Phase 32 divergence | `0 0` |
| `main` is ancestor | Yes |

The initial worktree was clean, with no tracked diff, staged file, or untracked file, and this proposed review document was absent. The `.pytest_cache` access warning was accepted only because `git status` completed successfully and returned exit code zero.

## 3. Phase 31 official tag verification

| Item | Verified value |
|---|---|
| Annotated tag | `v0.31.0-rcis-knowledge-promotion-decision-phase` |
| Tag type | `tag` |
| Tag object | `6232ad0f79c0872604a778fac2a33cb5d2a24e60` |
| Peeled target | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |
| Message | `RCIS Knowledge Promotion Decision Phase 31` |
| Remote tag object | `6232ad0f79c0872604a778fac2a33cb5d2a24e60` |
| Remote peeled target | `bf1777e738a6386e5c57c5ab73c39ff97fa1e35a` |

The local annotated tag and the live remote tag identify the same Phase 31 checkpoint.

## 4. Authoritative material inspected

Read-only inspection covered the Phase 25 through Phase 31 architecture and closure reviews, the corresponding authoritative domain and application contracts, and their focused domain and application tests:

- `KnowledgeCandidate` and the Knowledge constructor;
- `KnowledgeReviewRecord` and the reviewer;
- `KnowledgeGovernanceDecision` and the governor;
- `KnowledgeConflictAssessmentRecord` and the conflict assessor;
- `KnowledgeAuthorityDecision` and the authority decider;
- `KnowledgePromotionPrerequisiteEvaluation` and the prerequisite evaluator;
- `KnowledgePromotionDecision` and the promotion decider.

Inspection also covered `src/rie/domain/__init__.py`, `src/rie/application/__init__.py`, `pyproject.toml`, package discovery under `src`, and repository-wide names and contents concerning execution, governed Knowledge, lifecycle, acceptance, repositories, persistence, serialization, orchestration, commands, transactions, and idempotency. Evidence-specific repository implementations and controlled-ingestion execution contracts are unrelated to Knowledge promotion execution. Top-level Knowledge and Prompt types and `rie.knowledge` and `rie.prompt` wrappers remain frozen compatibility surfaces.

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
-> explicit KnowledgePromotionDecision
-> future promotion execution
-> future governed Knowledge
-> future acceptance/lifecycle
-> future Knowledge Repository
-> future Prompt Candidate
-> RCIS
```

Adjacent responsibilities remain distinct. Phase 32 may replace only the first `future promotion execution` label with a reviewed execution-record boundary; it may not collapse that boundary into the Phase 31 decision or future governed Knowledge.

## 6. Closed Phase 31 boundary

Phase 31 closed an immutable `KnowledgePromotionDecision` and a side-effect-free `decide_knowledge_promotion` application service. The record has deterministic `kpd1_` identity, exact candidate and prerequisite-evaluation lineage, exact declared-scope authorization, explicit actor, time, policy, and reasons, and exactly these outcomes:

```text
promotion_authorized_for_future_execution
promotion_denied
promotion_decision_deferred
```

Its authorization scope is exactly `eligible_for_future_promotion_execution_for_declared_scope`. Authorization is permission to approach a later execution boundary. It is not execution, authorization consumption, governed Knowledge construction, lifecycle initialization, acceptance, persistence, or duplicate suppression. Phase 31 contracts and tests remain unchanged.

## 7. Absent downstream-contract inventory

There is no authoritative `KnowledgePromotionExecution`, `KnowledgePromotionExecutionRecord`, governed `Knowledge`, `GovernedKnowledge`, Knowledge acceptance record, Knowledge lifecycle transition, Knowledge repository, or Knowledge persistence contract under `src/rie`. There is also no authoritative promotion-execution transaction, lock, idempotency store, orchestration command, CLI, API, or runtime integration.

Those absences are correct at the Phase 31 checkpoint. Evidence repositories and legacy Knowledge/Prompt surfaces do not supply missing promotion semantics and must not be imported, adapted, or treated as precedent for this boundary.

## 8. Promotion-execution problem statement

The smallest unresolved problem is to record a new immutable fact after one exact Phase 31 decision has authorized future execution. Repeating the authorization would add no new fact. Creating governed Knowledge would skip an unreviewed identity, lifecycle, acceptance, and repository boundary.

The honest intermediate fact is narrower: an explicit caller requested the exact authorized decision to be exercised, and the side-effect-free execution boundary accepted and completed that scope-limited execution-record action. This is evidence of a distinct Phase 32 action. It is not evidence that a governed Knowledge object exists or that authorization was durably and exclusively consumed.

## 9. Decision-versus-execution separation

The responsibilities are exact:

| Responsibility | Meaning |
|---|---|
| Promotion decision | Immutable policy evidence that future execution is authorized, denied, or deferred |
| Promotion execution request | Caller request to record the next allowed, scope-limited execution action |
| Promotion execution record | Immutable evidence that the execution boundary accepted and completed that distinct action |
| Governed Knowledge construction | Future creation of a new governed Knowledge identity and object |
| Persistence | Future durable storage of any record or governed object |

An authorized decision is necessary but not sufficient for a recorded execution. Exact candidate, evaluation, decision, policy, scope, outcome, execution reference, reason, actor, and time are also required. No decision outcome automatically invokes or creates execution.

## 10. Execution-versus-governed-Knowledge separation

Phase 32 execution creates no `GovernedKnowledge` object, governed Knowledge ID, lifecycle state, acceptance state, repository entry, or serialized representation. `promotion_execution_completed_for_declared_scope` means only that the Phase 32 execution-record action completed for the lineage and scope carried by the record.

A future governed-Knowledge constructor may accept the exact execution record together with other separately reviewed inputs. The execution record itself is the complete Phase 32 downstream handoff, so Phase 32 requires no additional construction-eligibility artifact or fifth file. Governed-Knowledge construction remains a distinct later boundary.

## 11. New execution fact analysis

The new fact is:

```text
At executed_at, executed_by explicitly completed one promotion-execution
record action, identified by execution_reference, for the exact candidate,
prerequisite evaluation, authorized promotion decision, and declared scope
under the exact execution policy.
```

This fact is an immutable event record. It is not a command awaiting execution, an operational attempt log, a state mutation, or a governed Knowledge result. The caller-supplied execution reference distinguishes separately declared real events with otherwise equal material fields. It is evidence supplied to and preserved by the boundary, not a repository uniqueness guarantee.

## 12. Execution subject alternatives

| Subject | Analysis | Decision |
|---|---|---|
| Exact decision only | Preserves indirect lineage but cannot independently recompute the candidate snapshot or validate the supplied evaluation object | Reject |
| Exact candidate plus decision | Recomputes the candidate but cannot independently validate the exact prerequisite evaluation | Reject |
| Exact candidate, evaluation, and decision | Enables exact identity recomputation and complete compatibility checks without repository lookup | Select |
| Decision ID only | Requires unresolved lookup and loses exact-object validation | Reject |
| Decision plus direct governance/conflict/authority histories | Duplicates the complete Phase 30 `kpe1_` lineage | Reject |
| Repository-resolved subject | Introduces persistence and lookup before review | Reject |

The smallest complete subject is one exact in-memory `KnowledgeCandidate`, one exact `KnowledgePromotionPrerequisiteEvaluation`, and one exact `KnowledgePromotionDecision`.

## 13. Candidate, evaluation, and decision lineage

The recorder must independently:

1. require exact upstream runtime types and reject subclasses and duck-typed substitutes;
2. recompute and verify the `kc1_`, `kpe1_`, and `kpd1_` identities;
3. recompute the complete candidate review snapshot digest;
4. require the evaluation and decision to reference the exact candidate ID, contract, and snapshot;
5. require the decision to reference the supplied evaluation ID, contract, and evaluation outcome;
6. require the exact supported evaluation and decision application-policy lineage;
7. require the Phase 31 authorization scope already enforced by the exact valid decision.

Governance, conflict, authority, and declared-peer-scope histories remain indirect through the content-addressed `kpe1_` evaluation and `kpd1_` decision. Copying those exact objects into Phase 32 would widen and duplicate the closed upstream boundaries.

## 14. Authorized-decision compatibility

| Phase 31 decision | Phase 32 behavior |
|---|---|
| `promotion_authorized_for_future_execution` | May record execution only after all policy, scope, exact-lineage, outcome, reference, and required-reason checks pass |
| `promotion_denied` | Reject with `promotion_decision_not_authorized_for_execution`; do not convert it or create an attempt/completion record |
| `promotion_decision_deferred` | Reject as incomplete with `promotion_decision_deferred_for_execution`; do not create an attempt/completion record |

Authorization is necessary but not sufficient. The authorized decision must use policy `rcis-knowledge-promotion-decision` version `1.0.0`, match the exact supplied evaluation and candidate, and retain authorization scope `eligible_for_future_promotion_execution_for_declared_scope`. No outcome automatically executes.

## 15. Execution outcome semantics

The initial domain record supports exactly one execution outcome:

```text
promotion_execution_completed_for_declared_scope
```

The exact execution scope is:

```text
promotion_execution_for_declared_scope
```

The required reason is:

```text
authorized_promotion_execution_completed_for_declared_scope
```

`promotion_execution_recorded_for_declared_scope` is too tautological to identify the completed action. `promotion_authorization_consumed_for_declared_scope` falsely implies durable exclusivity. `promotion_executed` is globally ambiguous. `governed_knowledge_construction_eligible_after_execution` crosses the future construction gate. `promotion_execution_deferred` and `promotion_execution_rejected` are application results, not successful execution records. Additional ordered caller reasons may coexist with the required reason, but the service does not insert or repair it.

## 16. Execution attempt and completion analysis

Attempt and completion are distinct operational concepts, but Phase 32 needs only one immutable completion record. The proposed pure function performs no external operation whose partial failure needs an attempt log. A malformed or rejected request creates no execution event and is represented only by the application result.

Separate attempt, failure, retry, and completion records would require an effectful workflow, durable correlation, and likely repository or transaction semantics. They remain deferred. If later requirements make both attempt and completion records necessary, the four-file slice must stop and return to architecture review.

## 17. Declared-scope versus global completeness

The execution record inherits no global-completeness claim. Its `authorization_scope` preserves Phase 31's `eligible_for_future_promotion_execution_for_declared_scope`, while its separate `execution_scope` is `promotion_execution_for_declared_scope`.

Completion therefore applies only to the exact content-addressed candidate, exact prerequisite evaluation, exact decision, and the evaluation's declared peer scope. It does not prove repository-global peer discovery, global conflict absence, global authority, durable uniqueness, or readiness of every future governed-Knowledge prerequisite.

## 18. Replay, duplicate, and idempotency semantics

Exact material replay, including the same execution reference and timestamp, reconstructs an equal record with the same `kpx1_` ID. This is deterministic record reconstruction, not proof that only one physical or business execution occurred.

A caller intending a distinct event must supply a distinct execution reference, timestamp, or other material field, producing a distinct ID. Multiple records for one decision are allowed as immutable history. The in-memory recorder does not query state, prevent duplicates, reserve references, consume authorization, or provide durable idempotency. Repository-aware uniqueness and idempotency are future policies.

## 19. Historical coexistence behavior

Execution records for the same `kpd1_` decision may coexist. Exact replays are value-equal; materially different events have different identities. No record supersedes, invalidates, contradicts, or erases another within Phase 32.

Actor, timestamp, lexical ID, age, tuple position, and input order do not select a winner. There is no latest-wins rule. Later adjudication, revocation, duplicate classification, or authorization-consumption policy requires a separately reviewed repository-aware boundary.

## 20. Repository and persistence decision

Repository required: No. Persistence required: No.

The approved fact is an in-memory immutable record returned directly to the caller. Completion means completion of the scope-limited record action, not a durable write. Repository lookup is unnecessary because Phase 32 makes no duplicate-prevention, authorization-consumption, cross-record, or global-completeness claim.

A future repository is unavoidable for durable uniqueness, consumption, lookup, storage, revocation, and cross-record adjudication, but none is required or approved in PR-032B.

## 21. Transaction and concurrency decision

Transaction required: No. Locking required: No. Concurrency control required: No.

The recorder mutates no shared state and performs no check-then-write sequence. Its deterministic output depends only on exact caller inputs. Transaction and lock semantics would become necessary only with durable authorization consumption, uniqueness enforcement, or governed-Knowledge persistence. Those claims are explicitly absent.

## 22. Structural validity

Malformed programming inputs raise `ValueError` before application policy evaluation. These include:

- a request, candidate, evaluation, decision, diagnostic, or record of the wrong exact runtime type;
- raw mappings, paths, unresolved IDs, subclasses, and duck-typed substitutes;
- broken `kc1_`, `kpe1_`, `kpd1_`, or `kpx1_` identity;
- a non-tuple reason or diagnostic collection;
- empty, duplicate, unordered, non-string, or whitespace-only required strings or reasons;
- a wrong-type or timezone-naive timestamp;
- an invalid execution-record contract, canonical collection, ID prefix, digest, or controlled domain value;
- a Phase 31 decision with a broken authorization scope, which is already invalid under the exact Phase 31 domain contract;
- a supplied decision whose identity does not match its contents.

Validation never repairs, coerces, sorts, trims, normalizes caller policy values, inserts time, or generates a reference.

## 23. Unsupported-input behavior

Structurally valid but unsupported or incompatible requests return `result_status="rejected"`, no execution record, one exact rejection reason, and one matching warning diagnostic. Examples are unsupported application policy, outcome, or scope; valid upstream records from unsupported application policies; denied or deferred decisions; exact-object lineage mismatch; and a missing required execution reason.

Unsupported strings remain valid domain inputs until policy evaluation and do not raise `ValueError` solely because they are unsupported. A valid denied decision is not malformed. A valid deferred decision is incomplete for execution. No rejection is converted, retried, or automatically recorded as an attempt.

## 24. Rejection vocabulary and precedence

The exact rejection vocabulary is:

| Reason | Exact condition |
|---|---|
| `unsupported_promotion_execution_policy` | Execution application policy ID or version is unsupported |
| `unsupported_promotion_execution_outcome` | Requested execution outcome is unsupported |
| `unsupported_promotion_execution_scope` | Requested execution scope is unsupported |
| `unsupported_promotion_decision_policy` | Valid decision uses another decision application policy ID or version |
| `unsupported_prerequisite_evaluation_policy` | Valid evaluation uses another prerequisite-evaluation policy ID or version |
| `promotion_decision_deferred_for_execution` | Exact decision outcome is deferred |
| `promotion_decision_not_authorized_for_execution` | Exact decision outcome is denied or otherwise non-authorized |
| `execution_candidate_mismatch` | Evaluation or decision candidate ID differs from the supplied candidate |
| `execution_candidate_contract_mismatch` | Evaluation or decision candidate contract differs from the supplied candidate |
| `execution_candidate_snapshot_mismatch` | Evaluation or decision snapshot differs from the recomputed candidate snapshot |
| `execution_prerequisite_evaluation_mismatch` | Decision evaluation ID, contract, or outcome differs from the supplied evaluation |
| `missing_required_promotion_execution_reason` | Otherwise compatible request omits the required execution reason |

After structural validation succeeds, evaluation stops at the first applicable condition in the table order. Within each candidate-lineage row, evaluation is checked before decision. Within prerequisite mismatch, ID is checked before contract, then outcome. A broken decision identity or authorization scope is malformed and raises `ValueError`; it is not an unreachable application rejection. No later condition overrides an earlier rejection.

## 25. Identity analysis

The deterministic execution identity policy is:

```text
class_name = KnowledgePromotionExecutionRecord
module = rie.domain.knowledge_promotion_execution
contract_version = knowledge-promotion-execution-v1
id_prefix = kpx1_
identity_policy_id = rcis-knowledge-promotion-execution-identity
identity_policy_version = 1.0.0
canonicalization_contract = knowledge-promotion-execution-json-v1
digest_algorithm = sha256
timestamp_normalization = UTC with fixed microsecond precision
```

Identity includes the execution contract, candidate ID/contract/snapshot, evaluation ID/contract, decision ID/contract/outcome, authorization scope, execution scope/outcome/reference, ordered reasons, actor, caller time, exact execution application policy ID/version, and canonicalization contract. Canonical bytes use UTF-8 JSON, NFC text normalization, sorted keys, compact separators, no non-finite numbers, and UTC timestamps with six fractional digits.

Identity excludes diagnostics, object identity, paths, implicit time, randomness, generated UUID, mutable metadata, input position, latest/winner selection, direct governance/conflict/authority histories, governed Knowledge identity, lifecycle, acceptance, repository, persistence, Prompt, and AI data.

## 26. Dependency direction

The safe dependency direction is:

```text
rie.application.knowledge_promotion_executor
-> rie.domain.knowledge_promotion_execution
-> rie.domain.knowledge_promotion_decision
-> rie.domain.knowledge_promotion_prerequisite_evaluation
-> rie.domain.knowledge_candidate and established snapshot helpers
```

The application service may import all four domain contracts. The new execution domain module may import the exact upstream types and identity/projection helpers needed for validation. Phase 25 through Phase 31 modules must not import Phase 32. No package initializer change is needed because setuptools discovers packages under `src`.

No repository, persistence, serialization, database, filesystem, network, subprocess, clock acquisition, random, UUID, retry, logging side effect, infrastructure, interface, CLI, API, UI, dashboard, Prompt, AI, business, or legacy dependency is permitted.

## 27. Forbidden behavior confirmation

The proposed boundary does not auto-execute a decision; mutate the decision, candidate, or evaluation; create governed Knowledge or its identity; initialize lifecycle; perform acceptance; serialize or persist; query a repository; claim duplicate prevention or global completeness; infer lineage, source authority, time, or references; resolve conflicts; select winners; use latest-wins; supersede or invalidate records; retry; use randomness or generated UUID; call AI; create Prompt Candidates; make business or creative approvals; or integrate legacy/runtime surfaces.

It also does not call operating-system, parser, filesystem, database, network, subprocess, logging, interface, infrastructure, CLI, API, UI, or dashboard behavior. Exact inputs remain immutable and unchanged.

## 28. Alternative comparison matrix

| Alternative | Inputs | New fact, identity, and lineage | Scope and side effects | Repository / persistence / transaction | Duplicate semantics | Governed-Knowledge implication | Safety and decision |
|---|---|---|---|---|---|---|---|
| A. Record bound to authorized decision | Exact decision | Event identity with indirect candidate/evaluation lineage | Scope-limited, pure | No / No / No | Coexistence only | None | Incomplete independent validation; reject |
| B. Record bound to candidate, evaluation, decision | Three exact objects | New `kpx1_` event with verified direct lineage | Scope-limited, pure | No / No / No | Replay deterministic; no prevention | Future input only | Complete and minimal; select |
| C. Record bound only to decision ID | Unresolved ID | Identity lacks exact-object proof | Requires lookup | Yes / likely / likely | Repository-defined | None | Unsafe; reject |
| D. Mutate decision with executed status | Decision | Overwrites authorization history | Mutation | State required / Yes / likely | State overwrite | None | Violates immutability; reject |
| E. Mutate candidate with promoted status | Candidate | Collapses lifecycle into candidate | Mutation | State required / Yes / likely | State overwrite | Implies promotion | Reject |
| F. Combined decision and execution | Candidate/evaluation | One identity collapses permission and action | Hidden automatic action | Maybe / maybe / maybe | Ambiguous | None | Reject |
| G. Execution plus governed Knowledge | Full downstream inputs | Event plus new governed identity | Creates governed object | Likely / likely / likely | Requires uniqueness | Creates governed Knowledge | Too broad; reject |
| H. Command without immutable record | Command data | No durable or content-addressed event fact | Effect or no evidence | Unclear / unclear / unclear | Unspecified | None | Unauditable; reject |
| I. Attempt plus completion records | Three exact objects plus correlation | Two event identities | Operational workflow | Likely / likely / likely | Correlated history | None | Premature fifth boundary; defer |
| J. Repository-backed idempotent execution | Exact objects plus repository | Durable execution and key reservation | Stateful | Yes / Yes / Yes | Can prevent duplicates | None | Useful later, outside slice |
| K. Authorization-consumption record | Decision plus consumption key | Claims exclusive consumption | Stateful | Yes / Yes / Yes | Requires uniqueness | None | Cannot be proven in memory; reject now |
| L. Governed-construction eligibility record | Execution plus future policy | Adds another permission fact | Pure or stateful | Undetermined | Undetermined | Crosses next gate | Redundant fifth artifact; reject now |
| M. Scope-limited in-memory execution record | Three exact objects | Same `kpx1_` fact as B | Pure and declared-scope only | No / No / No | Explicitly no prevention | None | Safe; selected formulation |

Alternatives B and M describe the same selected boundary from lineage and operational perspectives.

## 29. Preferred smallest next boundary

The preferred slice is **PR-032B - Minimal KnowledgePromotionExecutionRecord and Promotion Execution Recorder Contract Implementation**.

It adds one immutable `KnowledgePromotionExecutionRecord` plus one side-effect-free `record_knowledge_promotion_execution` application service. The record proves only completion of the exact Phase 32 declared-scope execution-record action for one exact authorized decision. It is a new event fact, not repeated permission, durable authorization consumption, governed Knowledge, or persistence.

## 30. Exact proposed domain contract

`rie.domain.knowledge_promotion_execution` should define three frozen dataclasses.

`KnowledgePromotionExecutionDiagnostic` field order:

1. `code: str`
2. `severity: str`
3. `message: str`
4. `field: str`
5. `source: str`

`KnowledgePromotionExecutionIdentityInput` field order:

1. `execution_record_contract_version: str`
2. `knowledge_candidate_id: str`
3. `knowledge_candidate_contract_version: str`
4. `knowledge_candidate_snapshot_digest: str`
5. `knowledge_promotion_prerequisite_evaluation_id: str`
6. `knowledge_promotion_prerequisite_evaluation_contract_version: str`
7. `knowledge_promotion_decision_id: str`
8. `knowledge_promotion_decision_contract_version: str`
9. `promotion_decision_outcome: str`
10. `authorization_scope: str`
11. `execution_scope: str`
12. `execution_outcome: str`
13. `execution_reference: str`
14. `reason_codes: tuple[str, ...]`
15. `executed_by: str`
16. `executed_at: datetime`
17. `execution_policy_id: str`
18. `execution_policy_version: str`

`KnowledgePromotionExecutionRecord` field order:

1. `knowledge_promotion_execution_id: str`
2. `contract_version: str`
3. `knowledge_candidate_id: str`
4. `knowledge_candidate_contract_version: str`
5. `knowledge_candidate_snapshot_digest: str`
6. `knowledge_promotion_prerequisite_evaluation_id: str`
7. `knowledge_promotion_prerequisite_evaluation_contract_version: str`
8. `knowledge_promotion_decision_id: str`
9. `knowledge_promotion_decision_contract_version: str`
10. `promotion_decision_outcome: str`
11. `authorization_scope: str`
12. `execution_scope: str`
13. `execution_outcome: str`
14. `execution_reference: str`
15. `reason_codes: tuple[str, ...]`
16. `executed_by: str`
17. `executed_at: datetime`
18. `execution_policy_id: str`
19. `execution_policy_version: str`
20. `diagnostics: tuple[KnowledgePromotionExecutionDiagnostic, ...]`

Exact constants are `knowledge-promotion-execution-v1`, `kpx1_`, `rcis-knowledge-promotion-execution-identity`, `1.0.0`, `knowledge-promotion-execution-json-v1`, `sha256`, `promotion_execution_for_declared_scope`, and `promotion_execution_completed_for_declared_scope`. Diagnostic severities are exactly `info` and `warning`.

All runtime checks use exact types. IDs are their exact prefix plus 64 lowercase hexadecimal characters; the candidate snapshot is 64 lowercase hexadecimal characters. Required strings are non-empty. Reasons are a non-empty exact tuple of unique lexicographically ordered strings and must include `authorized_promotion_execution_completed_for_declared_scope` when the application records a result. Diagnostics are an exact tuple of exact diagnostic objects and remain outside identity. `executed_at` is an exact timezone-aware `datetime`, normalized only for identity to UTC with six fractional digits. Exact replay and coexistence follow sections 18 and 19.

The module should expose candidate snapshot, upstream identity-verification, canonical projection/bytes, ID computation, and record-to-identity-input helpers. Helpers reject wrong exact types and never repair input.

## 31. Exact proposed application contract

`rie.application.knowledge_promotion_executor` should own:

```text
KNOWLEDGE_PROMOTION_EXECUTION_POLICY_ID = rcis-knowledge-promotion-execution
KNOWLEDGE_PROMOTION_EXECUTION_POLICY_VERSION = 1.0.0
```

It should define frozen `KnowledgePromotionExecutionRequest` fields in this order:

1. `knowledge_candidate: KnowledgeCandidate`
2. `promotion_prerequisite_evaluation: KnowledgePromotionPrerequisiteEvaluation`
3. `promotion_decision: KnowledgePromotionDecision`
4. `execution_scope: str`
5. `execution_outcome: str`
6. `execution_reference: str`
7. `reason_codes: tuple[str, ...]`
8. `executed_by: str`
9. `executed_at: datetime`
10. `execution_policy_id: str`
11. `execution_policy_version: str`

It should define frozen `KnowledgePromotionExecutionResult` fields in this order:

1. `result_status: str`
2. `promotion_execution_record: KnowledgePromotionExecutionRecord | None`
3. `reason_codes: tuple[str, ...]`
4. `diagnostics: tuple[KnowledgePromotionExecutionDiagnostic, ...]`

The application function is `record_knowledge_promotion_execution(request)`. `recorded` returns exactly one valid record, empty result reasons and diagnostics, and empty record diagnostics. `rejected` returns no record, one approved reason, and one matching warning diagnostic. It enforces the first-applicable order in section 24, copies caller policy values without normalization, and never infers time, reference, reason, scope, or lineage.

The service is a pure record constructor. It performs no operating-system action, repository lookup, persistence, serialization, transaction, lock, governed-Knowledge construction, mutation, hidden inference, automatic retry, or automatic invocation from Phase 31.

## 32. Exact proposed implementation slice

PR-032B should add exactly four files:

1. `src/rie/domain/knowledge_promotion_execution.py`
2. `src/rie/application/knowledge_promotion_executor.py`
3. `tests/domain/test_knowledge_promotion_execution.py`
4. `tests/application/test_knowledge_promotion_executor.py`

No fifth file, package initializer edit, existing contract edit, repository, persistence, serialization, transaction, interface, infrastructure, CLI, API, UI, Prompt, AI, or legacy file is required. If implementation cannot stay within these four additive files, stop and return to architecture review.

## 33. Exact 20-domain/30-application test matrix

The proposed matrix contains exactly 20 non-parametrized domain tests and 30 non-parametrized application tests, one function per ID.

| Domain ID | Exact assertion |
|---|---|
| D01 | Diagnostic, identity-input, and execution-record dataclasses are frozen, value-equal, and have the exact field order |
| D02 | Contract, prefix, identity-policy, canonicalization, digest, scope, outcome, reason, and severity constants are exact |
| D03 | Execution ID is exactly `kpx1_` plus 64 lowercase hexadecimal characters and must match canonical content |
| D04 | Candidate ID, contract, and complete snapshot digest are strict and required |
| D05 | Prerequisite-evaluation ID and contract are strict and required |
| D06 | Promotion-decision ID, contract, outcome, and authorization scope are strict and required |
| D07 | Execution scope and outcome accept only the exact controlled values |
| D08 | Execution reference, actor, policy values, and reasons are exact non-empty strings or tuples as specified |
| D09 | Reason tuples must be non-empty, unique, and lexicographically ordered |
| D10 | `executed_at` must be an exact timezone-aware datetime and canonicalizes to UTC with six fractional digits |
| D11 | Diagnostics accept only exact immutable info/warning members |
| D12 | Canonical identity is NFC UTF-8 JSON with sorted keys, compact separators, finite values, and SHA-256 |
| D13 | Exact replay returns equal canonical bytes and the same `kpx1_` ID |
| D14 | Candidate identity, contract, or snapshot changes execution identity |
| D15 | Evaluation identity or contract changes execution identity |
| D16 | Decision identity, contract, outcome, or authorization scope changes execution identity |
| D17 | Execution scope, outcome, reference, reason, actor, time, policy, or contract changes identity |
| D18 | Diagnostics and forbidden repository, persistence, governed-Knowledge, lifecycle, and acceptance metadata are outside identity and record fields |
| D19 | Projection and identity helpers reject wrong exact types, malformed identities, subclasses, and duck-typed inputs |
| D20 | Record identity extraction round-trips exactly; coexistence is allowed and no duplicate-prevention claim is encoded |

| Application ID | Exact assertion |
|---|---|
| A01 | One exact authorized matching decision records one completed declared-scope execution with exact lineage and required reason |
| A02 | No authorized decision automatically invokes the recorder or creates a record |
| A03 | A denied decision rejects with `promotion_decision_not_authorized_for_execution` and creates no event |
| A04 | A deferred decision rejects with `promotion_decision_deferred_for_execution` and creates no attempt or completion event |
| A05 | Unsupported execution policy ID, version, or both reject first |
| A06 | Unsupported execution outcome rejects after supported execution policy |
| A07 | Unsupported execution scope rejects after supported outcome |
| A08 | A valid decision from an unsupported decision policy rejects explicitly |
| A09 | A valid evaluation from an unsupported evaluation policy rejects explicitly |
| A10 | Evaluation candidate-ID mismatch rejects explicitly |
| A11 | Decision candidate-ID mismatch rejects explicitly after the evaluation candidate check |
| A12 | Evaluation or decision candidate-contract mismatch rejects explicitly in exact order |
| A13 | Evaluation or decision candidate-snapshot mismatch rejects against the recomputed candidate snapshot |
| A14 | Decision evaluation-ID, contract, or outcome mismatch rejects explicitly in exact order |
| A15 | Broken candidate, evaluation, or decision identities raise `ValueError` before policy evaluation |
| A16 | Broken decision authorization scope or identity raises `ValueError`, not an application rejection |
| A17 | A compatible request missing the required execution reason rejects without insertion or repair |
| A18 | Combined failures return only the first applicable rejection from the exact precedence |
| A19 | A recorded result contains one exact record and empty result/record diagnostics and result reasons |
| A20 | A rejected result contains no record, one approved reason, and one matching warning diagnostic |
| A21 | Exact replay reconstructs an equal record and the same `kpx1_` identity without claiming one occurrence |
| A22 | A distinct caller reference or timestamp creates a distinct execution identity |
| A23 | Multiple records for one decision coexist without duplicate prevention, winner selection, latest-wins, supersession, or invalidation |
| A24 | Candidate, evaluation, decision, request, reason tuple, and results remain immutable and unchanged |
| A25 | Raw mappings, paths, unresolved IDs, legacy objects, subclasses, and duck-typed substitutes raise `ValueError` |
| A26 | Recording creates no decision, candidate, or evaluation mutation and no automatic downstream action |
| A27 | Recording creates no governed Knowledge, governed ID, lifecycle, acceptance, Prompt, or AI result |
| A28 | Runtime behavior performs no repository, persistence, serialization, transaction, locking, interface, or infrastructure operation |
| A29 | Runtime behavior uses no implicit clock, retry, randomness, generated UUID, filesystem, network, subprocess, or logging side effect |
| A30 | Production imports preserve the exact dependency direction and exclude CLI, API, UI, dashboard, Prompt, AI, business, and legacy integration |

Matrix counts are exact:

```text
DOMAIN_MATRIX_ENTRY_COUNT = 20
APPLICATION_MATRIX_ENTRY_COUNT = 30
TOTAL_MATRIX_ENTRY_COUNT = 50
```

## 34. Definition of Done

PR-032A is complete when:

- the synchronized Phase 32 branch and official Phase 31 annotated tag are verified locally and remotely;
- Phase 25 through Phase 31 contracts, tests, architecture reviews, closures, package boundaries, and downstream inventory are inspected read-only;
- the non-collapsible architecture chain and closed Phase 31 boundary are preserved;
- the new execution fact is explicit and distinct from authorization and governed Knowledge;
- exact candidate, evaluation, decision, policy, scope, outcome, reference, reason, actor, and time requirements are defined;
- authorized, denied, and deferred compatibility is exact and no outcome auto-executes;
- `kpx1_` deterministic identity, replay, coexistence, and duplicate disclaimers are exact;
- no repository, persistence, transaction, locking, durable consumption, or global-completeness claim is made;
- structural failure, application rejection vocabulary, first-applicable precedence, and result invariants are exact;
- one exact four-file implementation slice and exact 20-domain/30-application matrix are approved;
- exactly this review document is created, with no code, test, existing documentation, configuration, Git history, merge, or tag change.

## 35. Stop conditions and required-question answers

Stop PR-032B and return to architecture review if execution cannot remain distinct from decision and governed Knowledge; merely repeats authorization; requires repository lookup, persistence, transaction, lock, duplicate prevention, durable authorization consumption, mutation, governed identity/object, lifecycle, acceptance, winner selection, latest-wins, implicit time, randomness, generated UUID, separate attempt and completion records, a fifth file, an initializer or existing-contract edit, or any Prompt, AI, CLI, API, UI, interface, infrastructure, persistence, or legacy work.

The 50 required semantic answers are:

| ID | Answer |
|---:|---|
| 1 | Execution creates immutable evidence that one explicit declared-scope execution-record action completed for exact authorized lineage. |
| 2 | It is a completed event represented by an immutable record, not a command, mutable state, or governed object. |
| 3 | Yes; the scope-limited event record can be created without governed Knowledge. |
| 4 | The Phase 32 record action completed; no downstream governed construction occurred. |
| 5 | It is evidence that authorization was exercised, but not durably or exclusively consumed. |
| 6 | Yes; it adds actor, time, policy, scope, outcome, reference, reasons, and a new event identity. |
| 7 | Yes; exactly one authorized `KnowledgePromotionDecision` is required. |
| 8 | Yes; the exact candidate is required for identity and snapshot recomputation. |
| 9 | Yes; the exact prerequisite evaluation is required for independent identity and lineage checks. |
| 10 | No; indirect lineage alone is insufficient for the selected exact-object validation boundary. |
| 11 | Yes; candidate, evaluation, and decision identities are independently recomputed and verified. |
| 12 | Yes; the decision must be exactly `promotion_authorized_for_future_execution`. |
| 13 | No; denied and deferred decisions cannot produce successful execution records. |
| 14 | Yes; denied and deferred decisions return their distinct exact rejections. |
| 15 | No separate execution-deferred record exists; an unready request is rejected and records no event. |
| 16 | Request incompatibility is an application rejection, not a domain execution outcome. |
| 17 | Yes operationally, but the initial pure boundary records completion only. |
| 18 | No; requiring both records would exceed the minimal four-file slice. |
| 19 | Yes; one immutable record honestly represents completion of the Phase 32 scope-limited action. |
| 20 | Use exactly `promotion_execution_completed_for_declared_scope`. |
| 21 | Use exactly `promotion_execution_for_declared_scope` and retain the Phase 31 authorization scope. |
| 22 | Yes; multiple immutable records may coexist for one decision. |
| 23 | Coexistence is allowed; the contract neither classifies nor prevents business duplicates. |
| 24 | Exact material replay reconstructs the same record; a distinct event needs a material input change. |
| 25 | Contract, all lineage, scopes, outcomes, reference, reasons, actor, time, policy, and canonicalization are material. |
| 26 | A caller-supplied execution reference is required; a caller-supplied record ID is not. |
| 27 | Yes; randomness and generated UUID are forbidden. |
| 28 | Yes; caller time is material, though a distinct event should also use its explicit distinct reference. |
| 29 | It supports deterministic replay, not durable idempotent effect execution. |
| 30 | Durable idempotency would require repository or equivalent state, so it is deferred. |
| 31 | No; the in-memory contract explicitly disclaims duplicate prevention. |
| 32 | No; declared-scope completeness is sufficient for this record. |
| 33 | No; persistence is outside the slice. |
| 34 | No; there is no stateful check-and-write operation. |
| 35 | No; there is no shared mutable state. |
| 36 | No; durable authorization consumption is neither required nor claimed. |
| 37 | No; the decision remains immutable. |
| 38 | No; the candidate remains immutable. |
| 39 | No; the evaluation remains immutable. |
| 40 | No; governed lifecycle remains a later boundary. |
| 41 | No; governed Knowledge identity remains a later boundary. |
| 42 | Yes; the execution record itself can be a future constructor input. |
| 43 | It is an immutable execution result record, not another authorization or construction command. |
| 44 | Yes; governed-Knowledge construction remains separately required. |
| 45 | Phase 32 provides the exact `KnowledgePromotionExecutionRecord`. |
| 46 | Wrong exact types, malformed identities/collections/strings/timestamps/contracts, and broken authorization scope raise `ValueError`. |
| 47 | Unsupported policies/outcome/scope, denied/deferred decisions, lineage mismatches, and missing required reason reject. |
| 48 | The exact first-applicable order is the section 24 table order. |
| 49 | Results are exactly `recorded` or `rejected`; rejections have one reason and one matching warning diagnostic. |
| 50 | Yes; the complete boundary fits exactly four additive files. |

No stop condition is present in the inspected repository or selected contract.

## 36. Final decision

# APPROVED FOR ONE MINIMAL PHASE 32 KNOWLEDGE PROMOTION EXECUTION IMPLEMENTATION SLICE

Approval is limited to PR-032B, the exact four additive files in section 32, and the exact contracts and 50-test matrix in sections 30, 31, and 33. The slice records one deterministic, scope-limited execution event for exact authorized lineage. It does not approve automatic execution, durable authorization consumption, duplicate prevention, governed Knowledge construction, identity, lifecycle, acceptance, repository, persistence, serialization, transaction, locking, Prompt, AI, business, runtime, merge, or tag work.
