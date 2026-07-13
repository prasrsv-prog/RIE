# PR-030A — Knowledge Promotion Prerequisite Evaluation Boundary and Dependency Review

## 1. Review identity

This document records the review-only and documentation-only PR-030A architecture assessment. It selects the smallest honest boundary after `KnowledgeAuthorityDecision` and before any promotion decision, promotion execution, governed-Knowledge creation, lifecycle, acceptance, repository, or persistence behavior.

No production source, tests, existing document, package export, configuration, dependency, interface, infrastructure, Git history, tag, permission, or ACL was modified. Python, pytest, pip, and project interpreters were not executed.

## 2. Repository and Phase 30 checkpoint

| Item | Verified value |
| --- | --- |
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-030-knowledge-promotion-prerequisite-evaluation-review` |
| Starting HEAD | `0d5d179a25a00761d4c1805f576c3cd7ffa9d8f8` |
| Starting subject | `docs: review knowledge authority decision phase closure` |
| `main` | `0d5d179a25a00761d4c1805f576c3cd7ffa9d8f8` |
| `origin/main` | `0d5d179a25a00761d4c1805f576c3cd7ffa9d8f8` |
| Local Phase 30 ref | `0d5d179a25a00761d4c1805f576c3cd7ffa9d8f8` |
| Remote-tracking Phase 30 ref | `0d5d179a25a00761d4c1805f576c3cd7ffa9d8f8` |
| Local/remote divergence | `0 0` |
| Main-to-Phase-30 divergence | `0 0` |
| Initial worktree | clean |
| Initial staged-file count | `0` |

The proposed PR-030A document and its external report were absent before the report was created.

## 3. Phase 29 tag verification

The official annotated tag is exact:

| Item | Verified value |
| --- | --- |
| Tag | `v0.29.0-rcis-knowledge-authority-decision-phase` |
| Local type | `tag` |
| Tag object | `1f0d96630da7753c4bb45c8071d913ae05fdf2e6` |
| Peeled target | `0d5d179a25a00761d4c1805f576c3cd7ffa9d8f8` |
| Message | `RCIS Knowledge Authority Decision Phase 29` |

Live remote inspection returned the same tag object and peeled target without fetching or changing refs.

## 4. Authoritative material inspected

The following architecture documents were inspected read-only:

- `docs/architecture/pr-025a-knowledge-construction-boundary-and-dependency-review.md`
- `docs/architecture/pr-025c-knowledge-candidate-construction-result-and-full-regression-review.md`
- `docs/architecture/pr-025d-knowledge-construction-phase-closure-review.md`
- `docs/architecture/pr-026a-knowledge-governance-and-promotion-boundary-review.md`
- `docs/architecture/pr-026c-knowledge-review-record-implementation-result-and-full-regression-review.md`
- `docs/architecture/pr-026d-knowledge-governance-phase-closure-review.md`
- `docs/architecture/pr-027a-knowledge-governance-authorization-and-promotion-prerequisite-boundary-review.md`
- `docs/architecture/pr-027c-knowledge-governance-decision-implementation-result-and-full-regression-review.md`
- `docs/architecture/pr-027d-knowledge-governance-authorization-phase-closure-review.md`
- `docs/architecture/pr-028a-knowledge-promotion-prerequisite-and-next-domain-boundary-review.md`
- `docs/architecture/pr-028c-pairwise-knowledge-conflict-assessment-implementation-result-and-full-regression-review.md`
- `docs/architecture/pr-028d-pairwise-knowledge-conflict-assessment-phase-closure-review.md`
- `docs/architecture/pr-029a-knowledge-authority-decision-and-promotion-prerequisite-boundary-review.md`
- `docs/architecture/pr-029c-knowledge-authority-decision-implementation-result-and-full-regression-review.md`
- `docs/architecture/pr-029d-knowledge-authority-decision-phase-closure-review.md`

The exact requested AcceptedEvidence, candidate, review, governance, conflict, authority, constructor, reviewer, governor, assessor, decider, and OfficialSource production files were inspected with all twelve matching test files. `src/rie/application/__init__.py` is empty and `src/rie/domain/__init__.py` contains only its package docstring; no future package-export edit is necessary.

All five Phase 29 external reports were present, fingerprinted, complete, and non-blocking. PR-029B and PR-029B-R1 record 35/35 focused tests; PR-029C records 1890/1890 full regression; PR-029D records closure readiness. PR-030A did not rerun tests.

## 5. Current authoritative chain

The exact non-collapsible chain is:

`Repository -> Repository Explorer -> RepositoryExploration -> EvidenceCollection -> Evidence -> AcceptedEvidence -> deterministic Knowledge construction -> KnowledgeCandidate -> explicit review -> KnowledgeReviewRecord -> explicit governance authorization -> KnowledgeGovernanceDecision -> explicit pairwise semantic assessment -> KnowledgeConflictAssessmentRecord -> explicit authority decision -> KnowledgeAuthorityDecision -> future promotion-prerequisite evaluation -> future promotion decision -> future promotion execution -> future governed Knowledge -> future acceptance and lifecycle -> future Knowledge Repository -> future Prompt Candidate -> RCIS`.

Extraction output is not Evidence; `EvidenceCandidate` is not `AcceptedEvidence`; `AcceptedEvidence` is not Knowledge; `KnowledgeCandidate` is not governed Knowledge; review is not governance; governance is not authority; conflict evidence is not resolution; authority evidence is not promotion readiness; evaluation is not promotion decision; decision is not execution; execution must create a new governed object; promotion is not acceptance; authority is not lifecycle; and governed Knowledge is not persistence.

## 6. KnowledgeCandidate boundary

`KnowledgeCandidate` is frozen deterministic construction history with `kc1_` identity. It preserves the complete AcceptedEvidence and source-provenance representation. At construction, authority is `unassessed`, lifecycle is `candidate`, review is `pending_review`, and conflict is `not_assessed`.

Phase 30 may verify its exact identity and complete established review-snapshot digest. It may not mutate the candidate, derive authority from source metadata, or write prerequisite state into the candidate.

## 7. KnowledgeReviewRecord boundary

`KnowledgeReviewRecord` is immutable explicit review evidence for one exact candidate snapshot with deterministic `kr1_` identity. `passed` does not authorize governance or promotion.

Review lineage remains indirect through content-addressed governance identities. Phase 30 must not require direct review records or duplicate `kr1_` IDs in its record.

## 8. KnowledgeGovernanceDecision boundary

`KnowledgeGovernanceDecision` is immutable explicit governance authorization evidence with deterministic `kg1_` identity and ordered review lineage. Its only authorization scope is `eligible_for_future_promotion_evaluation`.

Phase 30 must receive exact governance records directly so it can verify identity, application policy, candidate ID, candidate contract, complete snapshot, ordering, uniqueness, and composition. `authorized` means eligibility for evaluation only; it is not promotion authorization.

## 9. KnowledgeConflictAssessmentRecord boundary

`KnowledgeConflictAssessmentRecord` is immutable caller-supplied pairwise semantic evidence with deterministic `kcf1_` identity. It preserves two canonically ordered exact candidate participants and one of four explicit outcomes.

It does not infer semantics, select a winner, resolve a conflict, or claim a globally complete comparison universe. Phase 30 may evaluate pairwise coverage only against an explicit declared peer scope.

## 10. KnowledgeAuthorityDecision boundary

`KnowledgeAuthorityDecision` is immutable explicit evidence about a caller-supplied intended authority value for future governed Knowledge with deterministic `ka1_` identity and exact governance lineage.

It does not aggregate historical decisions, overwrite another decision, assign authority to the candidate, certify readiness, promote, create governed Knowledge, initialize lifecycle, accept, or persist. Phase 30 must aggregate exact authority records without latest-wins or actor-priority behavior.

## 11. Current absent-contract inventory

Repository inspection found no authoritative contract for:

- `KnowledgePromotionEvaluationScope`
- `KnowledgePromotionPrerequisiteEvidenceBundle`
- `KnowledgePromotionPrerequisiteEvaluation`
- `KnowledgePromotionPrerequisiteEvaluationRecord`
- `KnowledgePromotionDecision`
- `KnowledgePromotionRecord`
- `KnowledgePromotionExecution`
- `GovernedKnowledge`
- `KnowledgeAcceptanceRecord`
- `KnowledgeLifecycleTransitionRecord`
- Knowledge Repository serialization or persistence

No promotion-named source file exists. Legacy Knowledge, Prompt, official-source, or Evidence-repository surfaces do not satisfy any absence.

## 12. Promotion-prerequisite problem statement

A tuple supplied by a caller proves only what is inside that tuple. It does not prove that all repository candidates, all applicable candidate pairs, or all historical governance and authority decisions were supplied.

The safe next boundary must evaluate exact evidence without silently converting caller selection into repository-global completeness. It must produce an immutable evidence result before any promotion decision.

## 13. Structural validity versus evidence compatibility

Structural validity covers exact runtime types, deterministic IDs, digest formats, required strings, aware times, tuple shape, ordering, uniqueness, canonical identity, and domain/result invariants. Malformed structural inputs raise `ValueError`.

Evidence compatibility is separate: supported policies and exact candidate ID, contract, snapshot, scope, peer, and governance-lineage relationships. Structurally valid but unsupported or incompatible requests return an explicit rejected application result.

Evidence composition is separate again: denied, deferred, contradictory, incomplete, or blocking records are valid history and normally produce a recorded not-satisfied or deferred evaluation rather than being discarded.

## 14. Declared-scope versus global-completeness distinction

Declared-scope completeness means that exact conflict evidence covers only the peers explicitly committed by one immutable scope and that the evaluation preserves exactly the supplied governance and authority histories. It never means those sets are repository-global.

Global completeness requires a future repository-aware authority that defines the candidate universe and complete historical decision universe. A caller-declared scope cannot make that claim. Accordingly, all Phase 30 positive language ends with `for_declared_scope` and does not mean promotion readiness.

## 15. Candidate next-boundary alternatives

| Alternative | Subject | Completeness semantics | Repository | Safe now | Decision |
| --- | --- | --- | --- | --- | --- |
| A. Candidate plus governance, conflict, and authority tuples | Exact supplied objects | No conflict denominator | No | No | Missing explicit scope |
| B. Candidate plus immutable declared scope and exact records | Exact candidate/scope/evidence | Declared-scope only | No | Yes | Preferred complete evaluation subject |
| C. Candidate plus evidence bundle | Exact bundled objects | Bundle-relative only | No | Yes, but unnecessary | Adds identity and indirection without more truth |
| D. Repository-derived global universe | Repository candidate/history set | Global | Yes | No | Repository contract absent |
| E. One latest record | Selected history | Implicit winner | Maybe | No | No latest authority |
| F. Candidate plus authority only | Partial evidence | Incomplete | No | No | Omits governance/conflict |
| G. Candidate plus conflict only | Partial evidence | Incomplete | No | No | Omits governance/authority |
| H. Combined evaluation and promotion decision | Evidence plus authorization | Collapsed | No | No | Responsibility collapse |
| I. Combined evaluation, execution, and creation | Evidence plus side effects | Collapsed | No | No | Downstream policies absent |
| J. Candidate mutation | Existing candidate | Hidden mutable state | No | No | Immutable-history violation |

## 16. Evaluation-subject analysis

The application module defines exactly two frozen dataclasses. Exact-type validation means `type(value) is ExpectedType`; subclasses, dictionaries, and duck substitutes are rejected.

```text
@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteEvaluationRequest:
    knowledge_candidate: KnowledgeCandidate
    evaluation_scope: KnowledgePromotionEvaluationScope
    knowledge_governance_decisions: tuple[KnowledgeGovernanceDecision, ...]
    knowledge_conflict_assessment_records: tuple[KnowledgeConflictAssessmentRecord, ...]
    knowledge_authority_decisions: tuple[KnowledgeAuthorityDecision, ...]
    reason_codes: tuple[str, ...]
    evaluated_by: str
    evaluated_at: datetime
    evaluation_policy_id: str
    evaluation_policy_version: str

@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteEvaluationResult:
    result_status: str
    evaluation: KnowledgePromotionPrerequisiteEvaluation | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgePromotionPrerequisiteDiagnostic, ...]
```

The module exposes exactly one public application function: `evaluate_knowledge_promotion_prerequisites(request)`. It accepts exactly one exact `KnowledgePromotionPrerequisiteEvaluationRequest`; no positional expansion, keyword alternative, raw constituent arguments, second public application function, method façade, or alias is approved.

The request subject is one exact candidate, one exact scope, a non-empty ordered governance tuple, an ordered conflict tuple, a non-empty ordered authority tuple, the exact computed outcome-reason tuple, evaluator actor, aware caller time, and exact policy. The immutable evaluation preserves exact candidate ID/contract/snapshot, deterministic `kps1_`, ordered `kg1_`/`kcf1_`/`ka1_` IDs, controlled scope/completeness/outcome/reasons, evaluator, time, and policy. No raw dictionary, unresolved ID, path, legacy object, Prompt object, or duck type is accepted.

## 17. Declared evaluation-scope analysis

The domain module defines exactly six frozen dataclasses with these fields and no others:

```text
@dataclass(frozen=True)
class KnowledgePromotionEvaluationScopePeer:
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str

@dataclass(frozen=True)
class KnowledgePromotionEvaluationScopeIdentityInput:
    scope_contract_version: str
    target_knowledge_candidate_id: str
    target_knowledge_candidate_contract_version: str
    target_knowledge_candidate_snapshot_digest: str
    peers: tuple[KnowledgePromotionEvaluationScopePeer, ...]
    completeness_qualifier: str
    scoped_by: str
    reason_codes: tuple[str, ...]
    scoped_at: datetime
    scope_policy_id: str
    scope_policy_version: str

@dataclass(frozen=True)
class KnowledgePromotionEvaluationScope:
    knowledge_promotion_evaluation_scope_id: str
    contract_version: str
    target_knowledge_candidate_id: str
    target_knowledge_candidate_contract_version: str
    target_knowledge_candidate_snapshot_digest: str
    peers: tuple[KnowledgePromotionEvaluationScopePeer, ...]
    completeness_qualifier: str
    scoped_by: str
    reason_codes: tuple[str, ...]
    scoped_at: datetime
    scope_policy_id: str
    scope_policy_version: str

@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteDiagnostic:
    code: str
    severity: str
    message: str
    field: str
    source: str

@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteIdentityInput:
    evaluation_record_contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_promotion_evaluation_scope_id: str
    knowledge_governance_decision_ids: tuple[str, ...]
    knowledge_conflict_assessment_record_ids: tuple[str, ...]
    knowledge_authority_decision_ids: tuple[str, ...]
    evaluation_scope: str
    completeness_basis: str
    evaluation_outcome: str
    reason_codes: tuple[str, ...]
    evaluated_by: str
    evaluated_at: datetime
    evaluation_policy_id: str
    evaluation_policy_version: str

@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteEvaluation:
    knowledge_promotion_prerequisite_evaluation_id: str
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_promotion_evaluation_scope_id: str
    knowledge_governance_decision_ids: tuple[str, ...]
    knowledge_conflict_assessment_record_ids: tuple[str, ...]
    knowledge_authority_decision_ids: tuple[str, ...]
    evaluation_scope: str
    completeness_basis: str
    evaluation_outcome: str
    reason_codes: tuple[str, ...]
    evaluated_by: str
    evaluated_at: datetime
    evaluation_policy_id: str
    evaluation_policy_version: str
    diagnostics: tuple[KnowledgePromotionPrerequisiteDiagnostic, ...]
```

Every one of the six domain values requires exact runtime types and exact field invariants. A scope peer requires strict `kc1_` plus 64 lowercase hexadecimal characters, a non-empty candidate contract, and a strict 64-lowercase-hex snapshot digest. Scope target identity and snapshot use the same strict forms.

`peers` is an exact tuple. Empty is structurally valid. A non-empty tuple is unique by `knowledge_candidate_id` and lexicographically ordered by that ID; no peer ID may equal the target ID; and the same peer ID cannot recur with another contract or snapshot. Target-as-peer or any duplicate peer ID is malformed and raises `ValueError`. No automatic sorting, replacement, normalization, or deduplication occurs. The scope itself has no `diagnostics` field.

Scope and evaluation reason collections are exact, non-empty tuples of exact non-empty strings, unique and lexicographically ordered. Scope actor and evaluator are non-empty exact strings; timestamps are exact aware `datetime` values; policy fields are non-empty exact strings. All invariant failures raise `ValueError`.

The evaluation's governance, conflict, and authority ID collections are exact tuples of exact strict IDs, unique and lexicographically ordered by `kg1_`, `kcf1_`, and `ka1_` respectively. Governance and authority ID tuples are non-empty; the conflict ID tuple may be empty. They must exactly project the corresponding request record tuples. No automatic sorting, replacement, or deduplication occurs.

The scope contract is `knowledge-promotion-evaluation-scope-v1`; prefix `kps1_`; identity policy `rcis-knowledge-promotion-evaluation-scope-identity` version `1.0.0`; canonicalization `knowledge-promotion-evaluation-scope-json-v1`; and scope policy `rcis-declared-knowledge-promotion-evaluation-scope` version `1.0.0`.

An empty peer tuple is structurally valid so it can be represented honestly, but it always records `prerequisites_deferred_for_declared_scope` with `declared_peer_scope_empty`. It cannot produce a positive evaluation. A non-empty declared scope can support only a scope-relative positive result; no scope alone supports a global claim.

## 18. Evidence-bundle analysis

A separate `KnowledgePromotionPrerequisiteEvidenceBundle` is unnecessary for PR-030B. The exact request already groups the candidate, scope, governance, conflict, and authority objects; the evaluation identity preserves the scope ID and every ordered upstream record ID.

A bundle would add a second aggregation identity without adding a completeness authority or outcome. Review lineage remains indirect through `kg1_`; AcceptedEvidence and source provenance remain indirect through the complete candidate snapshot. No evaluation outcome belongs in a bundle.

## 19. Candidate identity and snapshot lineage

The evaluator recomputes the target `kc1_` identity from the exact candidate and reuses the complete `knowledge-candidate-review-snapshot-json-v1` digest. The scope target, every governance record, every target conflict participant, and every authority decision must match the same exact candidate ID, contract, and digest.

Every declared peer preserves exact `kc1_` identity, candidate contract, and complete snapshot digest. Conflict participants must match those values; statement text, source classification, and source authority are never reinterpreted.

## 20. Review and governance lineage

Exact governance records are direct non-empty inputs in an exact tuple, unique and lexicographically ordered by strict `kg1_` ID. Each identity is recomputed; policy must be `rcis-knowledge-governance-authorization` version `1.0.0`; and candidate ID, candidate contract, and candidate snapshot lineage must match. The evaluation's `knowledge_governance_decision_ids` is exactly the ordered projection of this tuple. No sorting or repair occurs.

All-authorized governance satisfies the governance prerequisite. If there is no authorized record and at least one denied record, denial is a definite blocker even when deferred governance is also present. Authorized plus denied evidence is contradictory and deferred. With neither denial nor contradiction, any deferred record defers evaluation. Direct review records are forbidden because their ordered identities already live inside each governance identity.

## 21. Conflict lineage and pairwise coverage

Conflict records form an exact tuple, may be empty, and when non-empty are unique and lexicographically ordered by strict `kcf1_` ID. Each exact identity is recomputed and must use `rcis-knowledge-pairwise-conflict-assessment` version `1.0.0`. Its canonical pair must contain the target and one declared peer with exact IDs, contracts, and snapshots. The evaluation's `knowledge_conflict_assessment_record_ids` is exactly the ordered projection of this tuple; no sorting or repair occurs.

Exact duplicate record IDs are malformed. Records outside the declared scope are rejected. Missing declared pairs defer evaluation. Exactly one accepted assessment per declared peer is required for a positive result. `no_conflict_identified` and `equivalent_statement` satisfy that pair; `conflict_identified` is a definite blocker; `assessment_deferred` defers.

Pairwise coverage is complete only relative to the declared scope. It is never repository-global.

## 22. Conflict contradiction and deferral behavior

Distinct immutable assessments for the same pair coexist as history. The evaluator never chooses by actor, time, ID, or position. Multiple records for one pair make the scope evaluation deferred; incompatible outcomes make the evidence contradictory and deferred.

No result selects a winner, resolves conflict, infers semantics, suppresses a record, supersedes history, or asserts that no undeclared candidate conflicts with the target.

## 23. Authority lineage

Authority decisions are direct non-empty inputs in an exact tuple, unique and lexicographically ordered by strict `ka1_` ID. Each exact authority record must pass deterministic identity verification, use application policy `rcis-knowledge-authority-decision` version `1.0.0`, and match the exact candidate ID, candidate contract, and candidate snapshot. The evaluation's `knowledge_authority_decision_ids` is exactly the ordered projection of this tuple; no sorting or repair occurs.

Every authority decision contains its own complete non-empty, unique, lexicographically ordered `kg1_` lineage. Every referenced `kg1_` must exist in the direct governance-record input, and its exact governance object must pass deterministic identity, supported policy, candidate ID, candidate contract, and candidate snapshot validation. Each authority lineage is therefore an exact ordered subset—an order-preserving subsequence—of the direct governance tuple. Direct governance input represents the exact governance history supplied for this evaluation; authority records preserve their own historical subsets.

Full-tuple equality is not required. Different valid historical authority decisions may reference different compatible governance subsets, and direct governance records need not all be referenced by every authority record. No authority decision is discarded or selected because its lineage differs. A referenced governance ID missing from the direct input returns `authority_governance_lineage_mismatch`. Tuple age, actor, timestamp, lexical ID, and position never choose a lineage winner. Governance IDs alone are not a substitute for direct governance objects.

## 24. Authority-decision-set aggregation

A positive authority prerequisite requires one unique compatible affirmative pair: `authoritative_for_governed_knowledge` with `authority_value_authorized`. Multiple distinct decisions with that same pair may coexist and jointly agree.

An exact duplicate ID is malformed. Authorized `non_authoritative_for_governed_knowledge` is a definite blocker. Denied authoritative evidence is a definite blocker. Denied non-authoritative evidence cannot imply the opposite and therefore defers. Deferred decisions defer unless another prerequisite already yields a definite not-satisfied result.

Aggregation considers every supplied compatible authority decision even when valid decisions preserve different governance subsets. No lineage-subset difference, age, actor, timestamp, lexical ID, or tuple position discards a record or selects a winner. Aggregation is limited to the supplied tuple and does not claim the caller supplied all historical decisions.

## 25. Authority contradiction and deferral behavior

Authorized and denied outcomes for the same intended value are contradictory. Authorized outcomes for both intended values are contradictory. Both cases defer evaluation; no record silently overrides another.

Latest-wins, oldest-wins, lexical-ID-wins, actor-priority, timestamp-priority, and tuple-position selection are forbidden. Contradiction is not automatically converted into a negative opposite authority value.

## 26. Prerequisite taxonomy

| Prerequisite | Phase 30 status |
| --- | --- |
| Candidate deterministic validity | Evaluable now |
| Exact candidate snapshot | Evaluable now |
| Compatible review lineage | Evaluable indirectly through governance |
| Compatible authorized governance lineage | Evaluable now |
| Declared conflict-comparison scope | Evaluable now |
| Pairwise coverage within declared scope | Evaluable now |
| Conflict-outcome compatibility | Evaluable now |
| Compatible authority evidence | Evaluable now |
| Authority-set consistency | Evaluable now |
| Actor, reason, time, and policy values | Evaluable now |
| Governed-Knowledge creation policy | Deferred; absent |
| Promotion decision policy | Deferred; absent |
| Promotion execution policy | Deferred; absent |
| Lifecycle initialization policy | Deferred; absent |
| Acceptance policy | Deferred; absent |
| Repository-global completeness | Deferred; absent |
| Supersession and invalidation policy | Deferred; absent |

No absent downstream prerequisite is silently marked satisfied.

## 27. Evaluation outcome vocabulary

The evaluation scope is `candidate_governance_conflict_authority_for_declared_peer_scope`; completeness basis is `declared_scope_only`. Outcomes are exactly:

- `prerequisites_satisfied_for_declared_scope`
- `prerequisites_not_satisfied_for_declared_scope`
- `prerequisites_deferred_for_declared_scope`

A complete composition pass first determines every applicable definite blocker and every applicable deferred, incomplete, ambiguous, or contradictory condition after structural validation and first-applicable rejection checks. Outcome precedence is exact:

1. one or more definite blockers selects `prerequisites_not_satisfied_for_declared_scope`;
2. otherwise, one or more deferred, incomplete, ambiguous, or contradictory conditions selects `prerequisites_deferred_for_declared_scope`;
3. otherwise the outcome is `prerequisites_satisfied_for_declared_scope`.

No early blocker return may hide another applicable blocker. No deferred condition may override a definite blocker. Only complete compatible evidence yields satisfied.

Unsafe terms—`promotion_ready`, `globally_complete`, `approved_for_promotion`, `promoted`, `accepted`, `final`, and `governed`—are not contract values.

## 28. Application result and diagnostic vocabulary

Application result statuses are exactly `recorded` and `rejected`. Diagnostic severities are exactly `info` and `warning`.

The deterministic outcome-reason vocabulary is:

- satisfied: `declared_scope_prerequisites_satisfied`;
- not-satisfied general: `declared_scope_prerequisites_not_satisfied`;
- not-satisfied details: `governance_evidence_denied`, `declared_scope_conflict_identified`, `authority_value_not_authoritative`, `authoritative_value_denied`;
- deferred general: `declared_scope_prerequisites_deferred`;
- deferred details: `declared_peer_scope_empty`, `governance_evidence_deferred`, `governance_evidence_contradictory`, `declared_scope_conflict_coverage_incomplete`, `declared_scope_conflict_evidence_ambiguous`, `declared_scope_conflict_evidence_deferred`, `authority_evidence_deferred`, `authority_evidence_contradictory`, and `authority_evidence_not_affirmative`.

Reason construction is exact. For satisfied, the tuple is exactly `("declared_scope_prerequisites_satisfied",)`. For not satisfied, collect `declared_scope_prerequisites_not_satisfied` plus every applicable not-satisfied detail, exclude all deferred-only details, deduplicate, and lexicographically sort the entire tuple. For deferred, collect `declared_scope_prerequisites_deferred` plus every applicable deferred, incomplete, ambiguous, or contradictory detail, exclude not-satisfied-only details because no definite blocker exists, deduplicate, and lexicographically sort the entire tuple.

The caller-supplied request `reason_codes` must equal this exact computed tuple. The evaluator must not insert, delete, reorder, normalize, deduplicate, or repair it. Multiple simultaneous blockers contribute every blocker detail. Multiple simultaneous deferred conditions contribute every deferred detail. Governance denied plus deferred is not satisfied and includes only the general not-satisfied reason and `governance_evidence_denied`. Positive affirmative authority plus denied non-authoritative evidence is deferred with `authority_evidence_not_affirmative`. A conflict blocker plus deferred authority evidence is not satisfied and includes the conflict blocker detail while excluding `authority_evidence_deferred`.

A recorded result has exactly `result_status == "recorded"`, an exact `KnowledgePromotionPrerequisiteEvaluation`, `reason_codes == ()`, and `diagnostics == ()`; the evaluation contains the computed outcome and exact computed reason tuple. A rejected result has exactly `result_status == "rejected"`, `evaluation is None`, a reason tuple containing exactly one approved rejection reason, and exactly one exact warning diagnostic whose `code` equals that rejection reason. Wrong or internally inconsistent recorded/rejected result invariants raise `ValueError`.

## 29. Malformed-input behavior

Malformed programming inputs raise `ValueError`: wrong exact domain/request/result type; subclass or duck substitute; malformed or broken `kc1_`, `kg1_`, `kcf1_`, `ka1_`, `kps1_`, or `kpe1_` identity; invalid digest; non-tuple collection; empty required governance or authority tuple; duplicate or unordered collection; target-as-peer; duplicate peer candidate ID even with another contract or snapshot; empty required string or reason tuple; naive or invalid timestamp; non-finite canonical value; or inconsistent scope, evaluation, recorded-result, or rejected-result invariant.

An empty peer scope and an empty conflict tuple are deliberate structural exceptions: both are representable, but neither can produce a positive result when declared peer coverage is absent.

## 30. Valid unsupported-input behavior

Structurally valid requests with unsupported application, scope, governance, conflict, or authority policies, or incompatible candidate/scope/upstream lineage, return `rejected`. Extra-scope conflict records reject. Missing or mismatched required outcome reasons reject.

Denied, deferred, contradictory, incomplete, and blocking evidence compositions are not malformed and normally produce recorded not-satisfied or deferred evaluations.

## 31. Rejection vocabulary and precedence

After structural validation, first-applicable rejection precedence is exactly:

1. `unsupported_promotion_prerequisite_evaluation_policy`
2. `unsupported_promotion_evaluation_scope_policy`
3. `scope_candidate_mismatch`
4. `scope_candidate_contract_mismatch`
5. `scope_candidate_snapshot_mismatch`
6. `unsupported_governance_evidence_policy`
7. `governance_candidate_mismatch`
8. `governance_candidate_contract_mismatch`
9. `governance_candidate_snapshot_mismatch`
10. `unsupported_conflict_evidence_policy`
11. `conflict_record_outside_declared_scope`
12. `conflict_participant_contract_mismatch`
13. `conflict_participant_snapshot_mismatch`
14. `unsupported_authority_evidence_policy`
15. `authority_candidate_mismatch`
16. `authority_candidate_contract_mismatch`
17. `authority_candidate_snapshot_mismatch`
18. `authority_governance_lineage_mismatch`
19. `missing_or_mismatched_required_evaluation_reason`

`authority_governance_lineage_mismatch` applies when any structurally valid authority decision references a `kg1_` absent from the direct governance input; it does not require equality with the full governance tuple. `missing_or_mismatched_required_evaluation_reason` compares the request tuple against the exact outcome/reason algorithm in section 28. The evaluator returns only the first applicable rejection and never retries or repairs.

## 32. Deterministic identity

The frozen domain types are `KnowledgePromotionEvaluationScopePeer`, `KnowledgePromotionEvaluationScopeIdentityInput`, `KnowledgePromotionEvaluationScope`, `KnowledgePromotionPrerequisiteDiagnostic`, `KnowledgePromotionPrerequisiteIdentityInput`, and `KnowledgePromotionPrerequisiteEvaluation`.

The exact public constants are frozen as follows; string quotes show the complete value:

```text
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION = "knowledge-promotion-evaluation-scope-v1"
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_ID_PREFIX = "kps1_"
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_POLICY_ID = "rcis-knowledge-promotion-evaluation-scope-identity"
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_CANONICALIZATION_CONTRACT = "knowledge-promotion-evaluation-scope-json-v1"
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_DIGEST_ALGORITHM = "sha256"

KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION = "knowledge-promotion-prerequisite-evaluation-v1"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_ID_PREFIX = "kpe1_"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_POLICY_ID = "rcis-knowledge-promotion-prerequisite-evaluation-identity"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_CANONICALIZATION_CONTRACT = "knowledge-promotion-prerequisite-evaluation-json-v1"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_DIGEST_ALGORITHM = "sha256"

PROMOTION_EVALUATION_SCOPE_COMPLETENESS_QUALIFIER_COMPLETE_ONLY_FOR_DECLARED_PEER_SCOPE = "complete_only_for_declared_peer_scope"
PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE = "candidate_governance_conflict_authority_for_declared_peer_scope"
PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY = "declared_scope_only"

PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE = "prerequisites_satisfied_for_declared_scope"
PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE = "prerequisites_not_satisfied_for_declared_scope"
PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE = "prerequisites_deferred_for_declared_scope"

PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED = "declared_scope_prerequisites_satisfied"
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED = "declared_scope_prerequisites_not_satisfied"
PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED = "governance_evidence_denied"
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_IDENTIFIED = "declared_scope_conflict_identified"
PROMOTION_PREREQUISITE_REASON_AUTHORITY_VALUE_NOT_AUTHORITATIVE = "authority_value_not_authoritative"
PROMOTION_PREREQUISITE_REASON_AUTHORITATIVE_VALUE_DENIED = "authoritative_value_denied"
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED = "declared_scope_prerequisites_deferred"
PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY = "declared_peer_scope_empty"
PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DEFERRED = "governance_evidence_deferred"
PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_CONTRADICTORY = "governance_evidence_contradictory"
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_COVERAGE_INCOMPLETE = "declared_scope_conflict_coverage_incomplete"
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_AMBIGUOUS = "declared_scope_conflict_evidence_ambiguous"
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_DEFERRED = "declared_scope_conflict_evidence_deferred"
PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_DEFERRED = "authority_evidence_deferred"
PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_CONTRADICTORY = "authority_evidence_contradictory"
PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_NOT_AFFIRMATIVE = "authority_evidence_not_affirmative"

KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_INFO = "info"
KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING = "warning"

PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED = "recorded"
PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED = "rejected"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID = "rcis-knowledge-promotion-prerequisite-evaluation"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION = "1.0.0"
PROMOTION_EVALUATION_SCOPE_POLICY_ID = "rcis-declared-knowledge-promotion-evaluation-scope"
PROMOTION_EVALUATION_SCOPE_POLICY_VERSION = "1.0.0"
```

The nineteen rejection values in section 31 are also the complete controlled rejection/diagnostic-code constants; no additional rejection value is approved.

Both use SHA-256, UTF-8, Unicode NFC, sorted keys, compact separators, finite values, aware caller time normalized to UTC with six fractional digits and trailing `Z`.

Scope identity includes scope contract; target ID/contract/snapshot; ordered peer IDs/contracts/snapshots; completeness qualifier; actor; reasons; time; scope policy; and canonicalization. Evaluation identity includes evaluation contract; candidate ID/contract/snapshot; `kps1_`; ordered `kg1_`, `kcf1_`, and `ka1_`; evaluation scope; completeness basis; outcome; reasons; evaluator; time; application policy; and canonicalization.

Identity excludes diagnostics, repository location, paths, implicit time, randomness, UUID, mutable metadata, list position, record-selection rules, winner, resolution, promotion result, governed identity, lifecycle, acceptance, and persistence metadata.

## 33. Replay and historical coexistence

Exact replay produces identical canonical bytes, `kps1_`, `kpe1_`, scope, and evaluation values. Every material scope, evidence, outcome, reason, actor, time, or policy change produces a distinct identity or fails closed.

Distinct governance, conflict, authority, scope, and evaluation records coexist as immutable history. The evaluator never deletes, replaces, normalizes, deduplicates semantically, or selects a historical winner.

## 34. Dependency and import direction

The safe direction is:

`rie.application.knowledge_promotion_prerequisite_evaluator -> rie.domain.knowledge_promotion_prerequisite_evaluation -> existing candidate, review-snapshot, governance, conflict, authority identity helpers`.

The new domain owns the six exact frozen scope/evaluation structures, identity, canonicalization, replay, collection ordering, and record/result invariants. The application owns the two exact frozen request/result structures, upstream deterministic verification, supported policies, candidate/scope/lineage compatibility, authority ordered-subset validation, coverage and composition, exact outcome/reason calculation, and evaluation/result construction.

Existing Phase 25–29 modules must not import the Phase 30 boundary. No circular dependency or package initializer edit is required.

## 35. Repository and persistence decision

An exact in-memory evaluator is honest now only because its output is explicitly limited to a declared non-global scope and exact supplied history. It does not require repository lookup, persistence, serialization, database, filesystem, or network behavior.

A repository-aware candidate-universe and historical-decision authority is required before any global completeness or promotion-readiness claim. Repository absence is stated, never hidden by caller assertion.

## 36. Downstream separation

The evaluation neither authorizes nor executes promotion and creates no `KnowledgePromotionDecision`, `KnowledgePromotionRecord`, `KnowledgePromotionExecution`, `GovernedKnowledge`, governed identity, lifecycle, acceptance, supersession, invalidation, repository record, Prompt Candidate, or AI result.

It performs no business or creative approval. All downstream responsibilities require separate architecture review.

## 37. Ten-alternative comparison matrix

| ID | Boundary | Inputs | Identity/dependency | Repository/persistence | Forbidden effects | Safe now | Decision |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | Immutable evaluation with declared scope | Candidate, `kps1_` scope, exact governance/conflict/authority histories; each authority lineage is an ordered subset of direct governance | New `kps1_` and `kpe1_`; downstream-only imports; no lineage winner | No | Global claim, authorization, execution, creation | Yes | Approved |
| 2 | Scope first | Candidate and peer snapshots | `kps1_` only | No | Evaluation outcome | Technically, but incomplete | Too narrow; include scope inside evaluation slice |
| 3 | Evidence bundle first | Candidate, scope, all records | Additional bundle identity | No | Evaluation outcome | Technically | Unnecessary indirection |
| 4 | Repository-backed global evaluator | Global candidate/history universe | Repository dependency | Yes | Caller-only completeness | Future | Required only for global claims |
| 5 | Direct promotion decision | Candidate and prerequisite records | Promotion policy absent | No | Skipped evaluation | No | Reject |
| 6 | Evaluation plus execution | All evidence and side-effect command | Collapsed identities | Likely | Execution | No | Reject |
| 7 | Evaluation plus governed creation | All evidence and new governed fields | Governed identity absent | No | Creation/lifecycle | No | Reject |
| 8 | Candidate mutation | Candidate plus status | Rewrites `kc1_` history | No | Mutation | No | Reject |
| 9 | Latest/priority selection | Historical records | Hidden selection identity | Maybe | Silent override | No | Reject |
| 10 | Authority-only or conflict-only shortcut | Partial record branch | Missing dependencies | No | Incomplete evidence | No | Reject |

## 38. Preferred smallest next boundary

The preferred boundary is `KnowledgePromotionPrerequisiteEvaluation` with an immutable deterministically identified declared scope in the same domain contract module.

It is the smallest honest boundary because it converts the existing candidate, governance, pairwise conflict, and authority histories into a new immutable scope-relative evaluation without mutation, repository assumptions, persistence, promotion authorization, execution, or governed creation. A scope-only slice does not evaluate anything; a bundle-only slice adds no completeness authority.

Review outcome is A: approve one minimal evaluation slice.

## 39. Exact proposed next implementation slice

The exact next PR is `PR-030B — Minimal KnowledgePromotionPrerequisiteEvaluation and Evaluator Contract Implementation`.

Its exact four-file scope is:

1. `src/rie/domain/knowledge_promotion_prerequisite_evaluation.py`
2. `src/rie/application/knowledge_promotion_prerequisite_evaluator.py`
3. `tests/domain/test_knowledge_promotion_prerequisite_evaluation.py`
4. `tests/application/test_knowledge_promotion_prerequisite_evaluator.py`

No fifth file, package export, existing-contract edit, repository, persistence, serialization, configuration, interface, infrastructure, database, CLI, API, UI, Prompt, AI, or legacy integration is approved.

## 40. Exact implementation test matrix

Each matrix ID requires one distinct test function.

### Domain matrix

| ID | Required assertion |
| --- | --- |
| D01 | All six domain contracts have exactly the fields in section 17, are frozen, exact-type, and value-equal; scope has no diagnostics field |
| D02 | Contract, policy, prefix, canonicalization, digest, vocabulary, and severity constants are exact |
| D03 | Scope peer requires strict `kc1_`, candidate contract, and complete snapshot digest |
| D04 | Scope target ID, contract, and snapshot are strict |
| D05 | Peer tuple is exact; peer IDs are unique and candidate-ID-sorted; target-as-peer and duplicate IDs, including changed contract/snapshot duplicates, raise `ValueError`; empty is structurally valid |
| D06 | Scope actor, reasons, aware time, and policy fail closed |
| D07 | `kps1_` is strict and matches canonical scope content |
| D08 | `kpe1_` is strict and matches canonical evaluation content |
| D09 | Governance/conflict/authority ID collections are exact unique lexicographically ID-ordered tuples; governance and authority are non-empty, conflict may be empty; no automatic sorting or repair |
| D10 | Evaluation scope, completeness basis, and three outcomes are exact |
| D11 | Scope/evaluation reasons are exact non-empty unique lexicographically ordered tuples; evaluator, aware time, and policy fail closed |
| D12 | Diagnostics are exact immutable info/warning values outside identity |
| D13 | Scope bytes are UTF-8, NFC, sorted, compact, finite, and UTC normalized |
| D14 | Evaluation bytes are UTF-8, NFC, sorted, compact, finite, and UTC normalized |
| D15 | Exact scope and evaluation replay is byte- and identity-stable |
| D16 | Every material scope field changes `kps1_` |
| D17 | Every material evaluation field changes `kpe1_` |
| D18 | Repository, path, implicit/random, winner, resolution, promotion, governed, lifecycle, acceptance, and persistence metadata are absent from identity |
| D19 | Scope/evaluation identity helpers reject wrong exact and duck types |
| D20 | Identity extraction from scope and evaluation records round-trips exactly |

### Application matrix

| ID | Required assertion |
| --- | --- |
| A01 | Complete compatible non-empty declared scope records satisfied with no mutation |
| A02 | Empty peer scope records deferred and never positive |
| A03 | Missing declared peer assessment records deferred for incomplete coverage |
| A04 | Exactly one compatible assessment per declared peer permits positive coverage |
| A05 | `conflict_identified` makes prerequisites not satisfied without resolution |
| A06 | `assessment_deferred` makes evaluation deferred |
| A07 | Distinct same-pair records coexist but defer without selection |
| A08 | Incompatible same-pair outcomes defer as contradiction |
| A09 | Extra-scope conflict record rejects in precedence |
| A10 | Participant candidate, contract, or snapshot mismatch rejects |
| A11 | All direct exact authorized governance records satisfy governance prerequisite |
| A12 | Denied governance without authorized evidence makes prerequisite not satisfied |
| A13 | Deferred governance makes evaluation deferred |
| A14 | Authorized plus denied governance is contradictory and deferred |
| A15 | Governance identity, policy, lineage, order, and uniqueness are verified directly |
| A16 | Consistent authorized authoritative decisions satisfy authority prerequisite |
| A17 | Consistent authorized non-authoritative decisions make prerequisite not satisfied |
| A18 | Denied authoritative evidence makes prerequisite not satisfied without opposite inference |
| A19 | Deferred or non-affirmative authority evidence defers |
| A20 | Distinct consistent authority decisions coexist without winner selection |
| A21 | Same-value authorized/denied authority outcomes are contradictory and deferred |
| A22 | Authorized incompatible intended values are contradictory and deferred |
| A23 | Every authority decision's complete `kg1_` lineage is an ordered subset of the direct governance input; a missing referenced governance ID rejects without repair |
| A24 | Actor, timestamp, lexical ID, and position never select a winner |
| A25 | Unsupported evaluation, scope, governance, conflict, and authority policies reject in precedence |
| A26 | Scope/candidate and upstream-lineage mismatches reject in precedence |
| A27 | The exact blocker-first outcome and general-plus-all-applicable-detail reason algorithm is computed; a missing, extra, duplicate, or misordered request reason rejects without repair |
| A28 | Wrong types, ducks, malformed identities/collections, and inconsistent recorded/rejected result invariants raise `ValueError` |
| A29 | Replay is stable; material changes alter identity; inputs remain unchanged |
| A30 | Imports/runtime preserve the full forbidden boundary: no repository/global completeness, persistence, mutation, selection, promotion authorization/execution, governed creation, lifecycle, acceptance, Prompt, AI, interface, infrastructure, or legacy integration |

Domain count: 20. Application count: 30. Total count: 50.

## 41. Definition of Done and stop conditions

### Required-question answers

| No. | Answer |
| ---: | --- |
| 1 | `KnowledgePromotionPrerequisiteEvaluation` with an explicit immutable declared scope. |
| 2 | Yes, but only as a declared-scope evaluator that makes no global or readiness claim. |
| 3 | Yes. Conflict coverage has no honest denominator without it. |
| 4 | No. The exact request and evaluation identity already preserve the evidence set. |
| 5 | The exact frozen request fields in section 16: candidate, scope, three exact record tuples, computed reasons, actor, aware time, and exact policy. |
| 6 | Supported candidate/governance/conflict/authority prerequisites are satisfied only for the exact declared scope and supplied history. |
| 7 | It does not mean globally complete, promotion ready, authorized, promoted, governed, accepted, or persisted. |
| 8 | No. |
| 9 | No. |
| 10 | Exact pairwise coverage for declared peers, the direct supplied governance history, and every authority record's own ordered governance subset. |
| 11 | Structurally valid, but always deferred with `declared_peer_scope_empty`; never positive. |
| 12 | Yes, deterministic `kps1_`. |
| 13 | Yes, direct exact `KnowledgeGovernanceDecision` inputs are required. |
| 14 | Yes, indirectly through governance identities; direct duplication is forbidden. |
| 15 | Yes, indirectly through the complete candidate snapshot. |
| 16 | Yes, direct exact `KnowledgeConflictAssessmentRecord` inputs are required. |
| 17 | Record deferred with `declared_scope_conflict_coverage_incomplete`. |
| 18 | Reject with `conflict_record_outside_declared_scope`. |
| 19 | Duplicate exact IDs raise `ValueError`; distinct same-pair records coexist but defer. |
| 20 | Defer as contradictory; select no winner. |
| 21 | `conflict_identified` is not satisfied; `assessment_deferred` is deferred. |
| 22 | Yes, direct exact `KnowledgeAuthorityDecision` inputs are required. |
| 23 | Recompute `ka1_`; verify policy and candidate lineage; require each complete non-empty ordered unique `kg1_` lineage to be an ordered subset of direct governance, rejecting a missing referenced ID. |
| 24 | Duplicate exact IDs raise `ValueError`; distinct compatible decisions, including decisions with different valid historical governance subsets, coexist without selection or discard. |
| 25 | Authorized incompatible values defer as contradiction. |
| 26 | Consistent authorized authoritative satisfies; authorized non-authoritative or denied authoritative blocks; deferred and non-affirmative denied evidence defer. |
| 27 | No. Timestamp, actor, lexical ID, age, and position have no winner authority. |
| 28 | No decision may override another. |
| 29 | Candidate validity/snapshot, governance lineage, declared scope, pair coverage/outcomes, authority lineage/consistency, and audit policy. |
| 30 | Global completeness, promotion decision/execution, governed creation, lifecycle, acceptance, repository, persistence, supersession, and invalidation. |
| 31 | `prerequisites_satisfied_for_declared_scope`, `prerequisites_not_satisfied_for_declared_scope`, and `prerequisites_deferred_for_declared_scope`. |
| 32 | `recorded` and `rejected`. |
| 33 | Compute all conditions, apply blocker-before-deferred outcome precedence, include the applicable general reason plus every detail of the selected class, exclude the other class, deduplicate, and lexicographically sort; satisfied is the exact singleton. |
| 34 | Wrong exact types/subclasses/ducks, broken IDs/identity, invalid digests/collections/strings/times, target-as-peer, duplicate peer IDs, and inconsistent scope/evaluation/recorded/rejected invariants. |
| 35 | Unsupported policies and compatible-shape candidate/scope/governance/conflict/authority/reason mismatches. |
| 36 | The nineteen controlled reasons in section 31. |
| 37 | The exact first-applicable order in section 31. |
| 38 | Deterministic `kps1_` scope identity and `kpe1_` evaluation identity over the exact six domain contracts and their fields. |
| 39 | Exact candidate/scope/upstream IDs; ordered direct histories and authority subsets; bounded scope/completeness/outcome/reasons; actor/time/policy; and canonicalization. |
| 40 | Diagnostics, location/path, implicit/random values, selection/resolution, promotion, governed identity, lifecycle, acceptance, and persistence. |
| 41 | No, not for declared-scope evaluation. A repository is required for global claims. |
| 42 | No. |
| 43 | No. |
| 44 | No. |
| 45 | No. |
| 46 | No. |
| 47 | Yes, exactly four additive files with no export edit. |
| 48 | `PR-030B — Minimal KnowledgePromotionPrerequisiteEvaluation and Evaluator Contract Implementation`. |

PR-030A is complete when the exact checkpoint and Phase 29 tag are verified; all requested architecture, source, tests, initializers, and reports are inspected; closed and absent contracts are explicit; structural, compatibility, declared-scope, and global-completeness meanings are separated; all requested lineage, aggregation, outcome, rejection, identity, dependency, repository, downstream, and alternative questions are answered; the exact four-file PR-030B and 50-test matrix are defined; exactly this document is added; its complete verified snapshot is written externally; and no interpreter, test, existing-file, Git-history, package, or permission action occurs.

Stop PR-030B and return to architecture review if scope-relative wording cannot be preserved; a positive result must claim global completeness or readiness; exact candidate/governance/conflict/authority inputs are insufficient; record selection or upstream mutation becomes necessary; scope/evaluation identity needs repository state, implicit time, randomness, paths, or mutable metadata; a fifth file or existing-contract/export edit is required; or promotion decision, execution, governed creation, lifecycle, acceptance, repository, persistence, Prompt, AI, business, creative, interface, infrastructure, or legacy work becomes necessary.

Final repository status for this review must contain exactly `?? docs/architecture/pr-030a-knowledge-promotion-prerequisite-evaluation-boundary-and-dependency-review.md`, with zero staged files.

## 42. Final decision

# APPROVED FOR ONE MINIMAL PHASE 30 PROMOTION PREREQUISITE EVALUATION IMPLEMENTATION SLICE

The smallest honest next boundary is one immutable `KnowledgePromotionPrerequisiteEvaluation` with an immutable deterministic declared scope and one side-effect-free evaluator. Approval is limited to `PR-030B — Minimal KnowledgePromotionPrerequisiteEvaluation and Evaluator Contract Implementation`, the four files in section 39, and the 20-domain/30-application/50-total matrix in section 40.

The approved slice must not mutate upstream history, infer semantics or source authority, select winners, resolve conflicts, claim repository-global completeness, override authority history, authorize or execute promotion, create governed Knowledge, assign lifecycle, create acceptance, access or persist through a repository, serialize, call AI, create Prompt Candidate, or add integration surfaces.
