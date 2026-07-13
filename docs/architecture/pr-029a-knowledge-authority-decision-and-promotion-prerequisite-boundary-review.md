# PR-029A - Knowledge Authority Decision and Promotion Prerequisite Boundary Review

## 1. Review identity

| Item | Reviewed value |
|---|---|
| Review | PR-029A |
| Type | Review-only and documentation-only architecture assessment |
| Gate | Knowledge Authority Decision and Promotion Prerequisite Boundary Review |
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-029-knowledge-authority-decision-review` |
| Starting HEAD | `01a1249cd1e1222c74a84890dfb2709f5649181e` |
| Starting subject | `docs: review pairwise knowledge conflict assessment phase closure` |
| Project interpreter executed | No |
| Tests executed | None |

This review decides the smallest safe boundary after `KnowledgeConflictAssessmentRecord`. It creates no production code, tests, authority decision, promotion-prerequisite evaluation, promotion, governed Knowledge, lifecycle, acceptance, repository, or persistence behavior.

## 2. Repository and Phase 28 checkpoint

`HEAD`, `main`, `origin/main`, the local Phase 29 ref, the remote-tracking Phase 29 ref, and the live remote Phase 29 ref all resolve to `01a1249cd1e1222c74a84890dfb2709f5649181e`. Local-to-remote Phase 29 divergence is `0 0`; main-to-phase divergence is `0 0`. The initial working tree was clean, no staged file existed, this document did not exist, and the external report did not exist before its required creation.

The live remote check was read-only. No fetch or other ref mutation occurred.

## 3. Phase 28 tag verification

The official annotated tag is verified locally and remotely:

| Item | Verified value |
|---|---|
| Tag | `v0.28.0-rcis-pairwise-knowledge-conflict-assessment-phase` |
| Type | `tag` |
| Tag object | `bbfad5f05df9de7c61987cd7ad4b247dff5df117` |
| Peeled target | `01a1249cd1e1222c74a84890dfb2709f5649181e` |
| Message | `RCIS Pairwise Knowledge Conflict Assessment Phase 28` |
| Remote object | `bbfad5f05df9de7c61987cd7ad4b247dff5df117` |
| Remote peeled target | `01a1249cd1e1222c74a84890dfb2709f5649181e` |

## 4. Authoritative material inspected

The review inspected read-only all requested Phase 25 through Phase 28 architecture, implementation-result, and closure documents: `pr-025a`, `pr-025c`, `pr-025d`, `pr-026a`, `pr-026c`, `pr-026d`, `pr-027a`, `pr-027c`, `pr-027d`, `pr-028a`, `pr-028c`, and `pr-028d` under `docs/architecture`.

It also inspected the requested domain and application sources for `AcceptedEvidence`, candidate construction, review, governance, and conflict assessment; `src/official_source/official_source.py`; and every requested matching test file. All exact requested paths were present. The domain and application package initializers require no export edit.

The four requested PR-028 external reports were `ABSENT_NON_BLOCKING`. Their absence does not weaken the committed Phase 28 documents, source, tests, Git checkpoint, or annotated tag.

## 5. Current authoritative chain

The non-collapsible chain is:

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
-> future authority decision
-> future promotion-prerequisite evaluation
-> future promotion
-> future governed Knowledge
-> future acceptance and lifecycle
-> future Knowledge Repository
-> future Prompt Candidate
-> RCIS
```

Extraction output is not Evidence. `EvidenceCandidate` is not `AcceptedEvidence`. `AcceptedEvidence` is not Knowledge. `KnowledgeCandidate` is not governed Knowledge. Passed review is not governance authorization. Authorized governance means only eligibility for later promotion evaluation. Conflict assessment is pairwise evidence, not resolution. Authority decision is not promotion. Promotion is not acceptance. Governed Knowledge must be a new object, not a candidate mutated in place.

## 6. Current KnowledgeCandidate boundary

`KnowledgeCandidate` is a frozen deterministic construction result with one statement, ordered complete support, construction lineage, diagnostics, and fixed construction-time states:

```text
authority_status = unassessed
lifecycle_status = candidate
review_status = pending_review
conflict_status = not_assessed
conflict_ids = ()
```

Its source authority and lifecycle values are support provenance snapshots. Candidate authority remains permanently `unassessed`; neither this review nor a future authority decision may mutate it.

## 7. Current KnowledgeReviewRecord boundary

`KnowledgeReviewRecord` is frozen explicit review evidence for one exact candidate representation. It preserves `kc1_`, candidate contract, a complete candidate snapshot digest, ordered Evidence and acceptance lineage, decision, reasons, actor, time, and policy. Decisions are exactly `passed`, `rejected`, and `deferred`.

A passed review neither authorizes promotion nor assigns authority. Contradictory review records coexist; no ordering rule selects a winner.

## 8. Current KnowledgeGovernanceDecision boundary

`KnowledgeGovernanceDecision` is frozen explicit governance evidence for one exact candidate snapshot and ordered exact `kr1_` lineage. Decisions are exactly `authorized`, `denied`, and `deferred`; its only authorization scope is `eligible_for_future_promotion_evaluation`.

Authorized governance is not authority assignment. It does not execute promotion. Exact `kg1_` identities provide content-addressed review lineage, candidate lineage, actor, reasons, time, application policy, and identity policy without copying review objects into every later record.

## 9. Current KnowledgeConflictAssessmentRecord boundary

`KnowledgeConflictAssessmentRecord` is frozen exact pairwise semantic-assessment evidence for two canonical exact candidate snapshots. Its outcomes are caller supplied. The assessor does not infer meaning, select a winner, resolve conflict, or claim global comparison completeness.

The record contains candidate participant lineage only. It intentionally excludes review and governance IDs. It assigns no authority and executes no promotion.

## 10. Current absent-contract inventory

Repository inspection finds no authoritative `KnowledgeAuthorityDecision`, `KnowledgePromotionPrerequisiteEvaluation`, `KnowledgePromotionDecision`, `KnowledgePromotionRecord`, `GovernedKnowledge`, `KnowledgeAcceptanceRecord`, `KnowledgeLifecycleTransitionRecord`, or Knowledge repository/serialization/persistence contract under `src/rie`.

Those absences are correct. Legacy Knowledge, Prompt, official-source, and Evidence-repository surfaces do not satisfy these missing responsibilities.

## 11. Controlled authority vocabulary

The responsibilities remain distinct:

| Vocabulary | Controlled meaning |
|---|---|
| Intended authority value | The exact authority classification proposed for a future governed-Knowledge object |
| Authority-decision outcome | Whether that proposed value is authorized, denied, or deferred |
| Application result status | Whether a structurally valid supported request recorded a decision or was rejected |
| Rejection reason | The first exact policy, lineage, compatibility, or required-reason failure |
| Source authority status | `OfficialSource` provenance vocabulary only |
| Candidate authority status | Permanently `unassessed` construction history |
| Lifecycle status | Separate object-state responsibility |
| Review decision | `passed`, `rejected`, or `deferred` review evidence |
| Governance decision | `authorized`, `denied`, or `deferred` eligibility evidence |
| Conflict outcome | Pairwise semantic-assessment evidence only |

No vocabulary item substitutes for another.

## 12. Source authority versus Knowledge authority

`OfficialSource.AuthorityStatus` contains `official`, `source_of_truth_candidate`, `reference`, `draft`, and `unknown`. It classifies a source snapshot. It is not a governed-Knowledge authority vocabulary and cannot be reused safely.

Source type, document classification, source authority, source lifecycle, file path, source order, actor, timestamp, review order, governance order, conflict outcome, or lexical identity must not select or derive Knowledge authority. Unknown or insufficient source evidence must never become an affirmative Knowledge authority value automatically.

## 13. Authority-decision subject analysis

The application subject is one exact in-memory `KnowledgeCandidate` plus a non-empty exact tuple of exact `KnowledgeGovernanceDecision` objects. The record subject is the candidate's exact `kc1_` ID, candidate contract version, complete candidate snapshot digest, and the ordered unique `kg1_` identities.

The authority decision applies to an intended authority value for future governed Knowledge derived from that exact lineage. It does not apply the value to the candidate and does not create the future governed object.

The caller also supplies the intended authority value, decision outcome, ordered reasons, actor, timezone-aware time, and authority application policy ID/version. The service validates and records those values; it does not infer or repair them.

## 14. Candidate snapshot and lineage analysis

The exact candidate snapshot is the existing complete `knowledge-candidate-review-snapshot-json-v1` projection, computed through the established review/governance snapshot helper semantics. It covers every `KnowledgeCandidate` representation field: identity and contract, statement and type, construction rule, all support fields, source authority/lifecycle provenance, initial candidate states, conflict IDs, and diagnostics.

The authority record stores the resulting 64-lowercase-hex SHA-256 digest rather than duplicating the object. The request still requires the exact candidate object so identity and snapshot consistency can be recomputed without repository lookup.

## 15. Review and governance lineage analysis

At least one exact authorized `KnowledgeGovernanceDecision` is required. Every supplied governance record must have a valid deterministic identity, use governance application policy `rcis-knowledge-governance-authorization` version `1.0.0`, reference the same exact candidate ID and contract, and carry the recomputed complete candidate snapshot digest.

Review lineage is preserved indirectly through ordered content-addressed `kg1_` identities, each of which includes its ordered `kr1_` lineage. Directly copying review IDs into the authority record would duplicate lineage and create two consistency authorities.

Denied or deferred governance records are valid domain objects but are not eligible authority inputs. `authorized` plus `denied` is contradictory governance evidence; any non-contradictory set containing `deferred` is incomplete; a denied-only set is ineligible. Each condition returns an explicit rejected application result rather than a malformed-input exception.

## 16. Conflict-assessment independence analysis

Conflict evidence is independent of authority evidence. `KnowledgeConflictAssessmentRecord` answers the relationship between two candidate snapshots; it does not answer the intended authority of future governed Knowledge. The authority decision answers the latter and must not infer from the former.

Therefore conflict records are excluded from the authority request, record, and `ka1_` identity. A later promotion-prerequisite evaluator must join the complete applicable conflict branch and the authority branch with candidate, review, and governance lineage. This preserves both independent prerequisites without allowing either to determine the other.

## 17. AcceptedEvidence and source-provenance analysis

Accepted-Evidence support and source snapshots are preserved indirectly through the complete candidate snapshot digest. The authority record does not copy `AcceptedEvidence` objects, Evidence IDs, source paths, source authority values, or lifecycle values into separate fields.

This is sufficient for exact lineage because the full snapshot commits to all candidate support representation fields. Source authority and lifecycle remain provenance only and never become decision inputs by implication.

## 18. Authority-value vocabulary analysis

The repository has no safe governed-Knowledge authority vocabulary. The smallest new exact vocabulary is:

```text
authoritative_for_governed_knowledge
non_authoritative_for_governed_knowledge
```

Both values explicitly scope the classification to future governed Knowledge. Neither means official source, source of truth, final, locked, accepted, promoted, conflict-free, business-approved, or creative-approved. `unknown` and `unassessed` are not silently mapped into either value; inability to decide is represented by the separate decision outcome.

The exact scope field is:

```text
intended_future_governed_knowledge_authority
```

## 19. Authority-decision outcome analysis

The exact authority-decision outcomes are:

```text
authority_value_authorized
authority_value_denied
authority_value_deferred
```

The intended authority value remains explicit for all three outcomes so the record identifies what was authorized, denied, or deferred. Required reason codes are respectively:

```text
intended_knowledge_authority_authorized
intended_knowledge_authority_denied
intended_knowledge_authority_deferred
```

Application result statuses remain separately and exactly `recorded` and `rejected`.

## 20. Deferred and denied authority behavior

`authority_value_deferred` records that a supported explicit intended value was not decided under otherwise fully authorized governance lineage. It creates no affirmative authority and no readiness claim.

`authority_value_denied` records that the explicit intended value was denied under otherwise fully authorized governance lineage. It does not assign the opposite value automatically. A different intended value requires a separate explicit decision request and creates a separate record.

Neither outcome changes candidate state, governance status, conflict status, lifecycle, acceptance, or promotion state.

## 21. Contradictory authority-decision behavior

The minimal decider is repository-free and receives no prior authority decisions. Exact replay returns the same record; materially distinct requests create distinct records. Decisions with incompatible outcomes or intended values therefore remain explicit independent historical facts.

No decision silently overrides another by time, actor, order, policy, or lexical `ka1_` ID. A later promotion-prerequisite evaluator must receive the complete applicable authority-decision set and reject or defer when the set contains incompatible affirmative, negative, deferred, or value evidence. Resolution or winner selection requires a separate architecture review.

## 22. Promotion-prerequisite relationship

An authorized authority value is necessary evidence but is not sufficient promotion readiness. A later evaluator must independently validate exact candidate, compatible review and authorized governance lineage, complete applicable conflict-assessment coverage, a single compatible affirmative authority result, actor/reason/time/policy requirements, and any separately approved creation prerequisites.

The authority decider does not evaluate the aggregate, certify conflict completeness, or emit an eligibility result.

## 23. Governed-Knowledge creation separation

The decision names an intended value for future governed Knowledge but creates no governed object and no governed identity. A future promotion action must apply a compatible authorized value while creating a new immutable governed object and preserving all upstream lineage.

The future governed identity, promotion record, creation policy, statement/support application, and supersession rules remain unresolved and outside PR-029B.

## 24. Lifecycle and acceptance separation

Candidate lifecycle remains `candidate`. Future governed-Knowledge initial lifecycle is assigned only at creation under a separately reviewed rule; it is not a pre-creation transition. Later lifecycle changes require immutable transition evidence.

Acceptance applies only after governed Knowledge exists. Authority decision neither initializes lifecycle nor creates acceptance, finality, locking, supersession, or invalidation.

## 25. Deterministic identity analysis

The exact proposed contracts are:

```text
domain object = KnowledgeAuthorityDecision
application service = decide_knowledge_authority
record contract = knowledge-authority-decision-v1
identity prefix = ka1_
identity policy ID = rcis-knowledge-authority-decision-identity
identity policy version = 1.0.0
canonicalization = knowledge-authority-decision-json-v1
digest = sha256
application policy ID = rcis-knowledge-authority-decision
application policy version = 1.0.0
```

Frozen domain types are `KnowledgeAuthorityDiagnostic`, `KnowledgeAuthorityIdentityInput`, and `KnowledgeAuthorityDecision`. Frozen application types are `KnowledgeAuthorityDecisionRequest` and `KnowledgeAuthorityDecisionResult`.

Identity includes record contract; candidate ID, contract, and complete snapshot digest; ordered governance-decision IDs; authority scope; intended value; outcome; ordered reasons; actor; UTC-normalized caller time with exactly six fractional digits and trailing `Z`; exact application policy ID/version; and canonicalization contract. Canonical JSON uses UTF-8, Unicode NFC, sorted keys, compact separators, finite values, and SHA-256. Exact replay is stable.

Identity excludes diagnostics, direct review IDs, conflict records, copied AcceptedEvidence, repository location, filesystem path, implicit time, randomness, UUID, list position, mutable metadata, resolution, winner, promotion result, governed identity, lifecycle, acceptance, and persistence metadata.

## 26. Malformed and valid-unsupported behavior

Malformed programming inputs raise `ValueError`: wrong exact request, candidate, governance-record, diagnostic, identity-input, record, or result types; broken deterministic candidate/governance/authority identity; non-tuple, empty, duplicate, or unordered governance/reason collections; empty required strings; malformed IDs or digests; naive or non-`datetime` time; non-finite canonical values; unsupported values inside a constructed domain record; or inconsistent recorded/rejected result invariants.

Structurally valid requests with unsupported policies, values, outcomes, or incompatible lineage return `rejected`, no authority record, exactly one reason code, and one immutable warning diagnostic. The service does not insert reasons, reorder collections, normalize policy values, replace records, infer an authority value, or retry.

## 27. Application rejection model

The exact rejection vocabulary and first-applicable precedence after structural validation is:

1. `unsupported_authority_policy`;
2. `unsupported_authority_value`;
3. `unsupported_authority_decision_outcome`;
4. `unsupported_governance_evidence_policy`;
5. `governance_candidate_mismatch`;
6. `governance_candidate_contract_mismatch`;
7. `governance_candidate_snapshot_mismatch`;
8. `contradictory_governance_evidence`;
9. `ineligible_governance_evidence`;
10. `incomplete_governance_evidence`;
11. `missing_required_authority_reason`;
12. otherwise record one decision.

Governance composition is contradictory when both `authorized` and `denied` occur, regardless of deferral. A denied-only set is ineligible. Every other non-all-authorized set is incomplete. All-authorized evidence may record any supported authority-decision outcome when its exact required reason is present.

## 28. Dependency and import decision

The safe direction is:

```text
rie.application.knowledge_authority_decider
-> rie.domain.knowledge_authority_decision
-> existing candidate, governance, identity, and complete-snapshot helpers
-> rie.domain.knowledge_candidate
-> rie.domain.knowledge_governance_decision
```

`rie.domain.knowledge_conflict_assessment_record` remains an independent sibling prerequisite and is not imported. Existing candidate, review, governance, and conflict modules do not import the new authority boundary. No circular dependency, package-export change, interface, infrastructure, repository, persistence, database, filesystem, network, AI, Prompt, CLI, UI, legacy, or runtime integration is required.

## 29. Candidate next-boundary comparison

| Alternative | Exact subject | Responsibility | Required inputs | Forbidden effects | Dependencies | Identity implications | Repository/persistence | Safe now | Decision reason |
|---|---|---|---|---|---|---|---|---|---|
| Separate immutable `KnowledgeAuthorityDecision` | One exact candidate snapshot and exact governance lineage | Explicit intended future governed-authority decision | Candidate, governance records, value, outcome, reasons, actor, time, policy | Mutation, inference, conflict resolution, promotion | Existing candidate/governance/snapshot helpers | New independent `ka1_` | No | Yes | Complete subject and additive deterministic contract exist |
| Reuse `OfficialSource.AuthorityStatus` | Source snapshot, not Knowledge | Source classification | Official source metadata | Automatic inheritance | `official_source` legacy-adjacent vocabulary | Would conflate source and Knowledge identity | No | No | Wrong subject and semantics |
| Add authority to `KnowledgeGovernanceDecision` | Governance eligibility event | Collapsed authorization plus authority | Existing governance request plus new fields | Phase 27 mutation and responsibility collapse | Changes existing contract/tests | Rewrites `kg1_` policy | No | No | Violates immutable closed boundary |
| Mutate candidate authority | Construction result | Hidden state mutation | Candidate and authority value | History rewrite | Changes Phase 25 | Invalidates or forks `kc1_` semantics | No | No | Candidate authority must remain unassessed |
| Delay to prerequisite evaluation | Aggregate promotion request | Collapsed decision and evaluation | All future prerequisites | Hidden authority decision | Requires unresolved aggregate | No independent authority evidence | No | No | Evaluator needs explicit input evidence |
| Combine with governed creation | Future created object | Decision plus creation | All promotion prerequisites | Premature promotion and lifecycle | Many absent contracts | Conflates `ka1_` with governed identity | No | No | Creation prerequisites remain unresolved |
| Derive from conflict outcome | Candidate pair | Semantic inference | Conflict records | Winner selection and authority inference | Conflict branch | Makes `kcf1_` determine unrelated authority | No | No | Conflict evidence is not authority evidence |
| Require `KnowledgeRepository` first | Persisted records | Lookup/persistence | Repository and serialization | Persistence-driven policy | Absent interface/infrastructure | Adds location/duplicate concerns | Yes | No | Exact in-memory inputs suffice |
| Separate authority assessment record | Candidate authority evidence | Assessment before decision | New assessment policy and record | Unrequired extra stage | Additional domain/application contracts | Requires another identity and more than four files | No | No for next slice | Caller-supplied explicit decision is sufficient; revisit only if evidence assessment becomes distinct |

## 30. Preferred smallest next boundary

The preferred smallest next boundary is one immutable `KnowledgeAuthorityDecision` plus one side-effect-free authority decider. It records an explicit caller-supplied outcome about an explicit intended future governed-Knowledge authority value for one exact candidate/governance lineage.

It is honest now because conflict evidence has an established independent contract, the candidate snapshot and governance identity helpers are stable, and the decision can remain additive, deterministic, repository-free, persistence-free, and free of downstream effects.

## 31. Exact proposed next slice or unresolved gate

Outcome A is selected.

**PR-029B - Minimal KnowledgeAuthorityDecision and Authority Decider Contract Implementation**

Add exactly four files and modify none:

1. `src/rie/domain/knowledge_authority_decision.py`;
2. `src/rie/application/knowledge_authority_decider.py`;
3. `tests/domain/test_knowledge_authority_decision.py`;
4. `tests/application/test_knowledge_authority_decider.py`.

Domain matrix:

| ID | Exact assertion |
|---|---|
| D01 | Diagnostic, identity-input, and decision contracts are frozen, value-equal, and explicitly `ka1_` identified |
| D02 | Record, identity-policy, canonicalization, digest, scope, value, outcome, severity, and prefix constants are exact |
| D03 | Record ID requires `ka1_` plus 64 lowercase hex and matches canonical content |
| D04 | Candidate ID, contract, and complete snapshot digest are strict and required |
| D05 | Governance IDs require an exact non-empty ordered unique `kg1_` tuple |
| D06 | Authority scope and the two intended-value members are exact |
| D07 | Only the three exact authority-decision outcomes are recordable |
| D08 | Required strings, ordered reasons, policy values, and timezone-aware time fail closed |
| D09 | Diagnostics accept exact immutable info/warning members and remain outside identity |
| D10 | Canonical identity uses UTF-8, NFC, sorted keys, compact separators, UTC microseconds, and SHA-256 |
| D11 | Exact replay returns identical canonical bytes and `ka1_` identity |
| D12 | Candidate, governance, scope, value, outcome, reason, actor, time, policy, or contract changes identity |
| D13 | Direct review/conflict, source-path, promotion, governed identity, lifecycle, acceptance, repository, and persistence metadata are absent from identity |
| D14 | Candidate snapshot, governance identity, identity-input, and record helpers reject wrong exact and duck-typed inputs |
| D15 | Identity extraction from a valid record round-trips exactly |

Application matrix:

| ID | Exact assertion |
|---|---|
| A01 | Exact candidate plus all-authorized governance records `authority_value_authorized` without mutation |
| A02 | `authority_value_denied` records only with its exact required reason |
| A03 | `authority_value_deferred` records only with its exact required reason and no readiness claim |
| A04 | Both exact intended authority values are caller-selected and never source-derived |
| A05 | Record preserves exact candidate ID, contract, and recomputed complete snapshot digest |
| A06 | Multiple governance records are exact, ordered, unique, identity-valid, and all preserved |
| A07 | Exact replay produces the same record and `ka1_` identity |
| A08 | Material request changes produce distinct identities without override or winner selection |
| A09 | Unsupported authority policy has first rejection precedence |
| A10 | Unsupported intended value precedes unsupported outcome and lineage checks |
| A11 | Unsupported outcome precedes governance lineage and missing-reason checks |
| A12 | Unsupported governance evidence policy rejects with no record |
| A13 | Governance candidate ID, contract, and snapshot mismatches reject in exact precedence |
| A14 | Authorized plus denied governance evidence rejects as contradictory |
| A15 | Denied-only governance evidence rejects as ineligible |
| A16 | Deferred or mixed non-contradictory non-all-authorized evidence rejects as incomplete |
| A17 | Missing outcome-required authority reason rejects without insertion or repair |
| A18 | Empty/list/duplicate/unordered collections, raw IDs/paths/dicts, wrong domains, broken identities, and duck types fail closed |
| A19 | Candidate, governance, request, tuples, and results remain immutable; no source or semantic inference occurs |
| A20 | Runtime/import inspection proves no conflict resolution, aggregate evaluation, promotion, governed Knowledge, lifecycle, acceptance, repository, persistence, filesystem, network, AI, Prompt, retry, clock, randomness, UUID, CLI, UI, or legacy integration |

Exact counts:

```text
DOMAIN_MATRIX_ENTRY_COUNT = 15
APPLICATION_MATRIX_ENTRY_COUNT = 20
TOTAL_MATRIX_ENTRY_COUNT = 35
```

No tests are run during PR-029A.

## 32. Explicitly forbidden behavior

PR-029B must not mutate candidate, review, governance, or conflict objects; copy or infer source authority; infer from classification, lifecycle, paths, ordering, actor, time, policy order, conflict outcome, or lexical IDs; select a winner; resolve conflict; claim comparison completeness; evaluate all promotion prerequisites; execute promotion; create governed Knowledge; assign or transition lifecycle; create acceptance; supersede or invalidate Knowledge; persist; access repository/filesystem; call AI or external models; create Prompt Candidate; make business or creative decisions; modify Phase 25 through Phase 28 contracts; or add package exports, interfaces, infrastructure, database, CLI, API, UI, or legacy integration.

## 33. Deferred scope

Deferred work includes authority-decision-set aggregation and contradiction adjudication; promotion-prerequisite evaluation; conflict-universe completeness; governed-Knowledge and promotion identity; promotion decision, record, and creation; initial lifecycle and later transitions; acceptance; final/locked state; supersession and invalidation; repository interfaces; serialization and persistence; databases and migrations; Prompt Candidate; AI inference; business/creative policy; runtime integration; and legacy migration.

## 34. Required-question answers

| ID | Answer |
|---:|---|
| 1 | The smallest safe next boundary is a separate immutable `KnowledgeAuthorityDecision` plus side-effect-free decider. |
| 2 | Yes, it is implementable now as Outcome A. |
| 3 | Its application subject is one exact `KnowledgeCandidate` plus a non-empty exact tuple of exact governance decisions; its record subject is the exact candidate snapshot and ordered `kg1_` lineage. |
| 4 | It authorizes an intended authority value for future governed Knowledge; it does not apply authority to `KnowledgeCandidate`. |
| 5 | Yes. Candidate authority remains permanently `unassessed`. |
| 6 | Preserve the complete established review-snapshot digest covering every candidate representation field. |
| 7 | Yes. At least one exact compatible `authorized` `KnowledgeGovernanceDecision` is required. |
| 8 | They are valid governance objects but incompatible authority inputs: denied-only is ineligible and deferred-containing evidence is incomplete. |
| 9 | Review lineage is inherited indirectly through content-addressed governance-decision identities. |
| 10 | Conflict-assessment lineage is an independent promotion prerequisite, not an authority input. |
| 11 | AcceptedEvidence and source snapshots are preserved indirectly through the complete candidate snapshot; no direct copies are added. |
| 12 | No. `OfficialSource.AuthorityStatus` is source provenance and cannot be reused safely. |
| 13 | Exactly `authoritative_for_governed_knowledge` and `non_authoritative_for_governed_knowledge`. |
| 14 | Exactly `authority_value_authorized`, `authority_value_denied`, and `authority_value_deferred`. |
| 15 | Exactly `recorded` and `rejected`. |
| 16 | Record `authority_value_deferred` against the explicit intended value and exact authorized governance lineage. |
| 17 | Record `authority_value_denied` against the explicit intended value; do not assign its opposite. |
| 18 | Preserve contradictory decisions as independent immutable records; later prerequisite evaluation rejects or defers the complete incompatible set. |
| 19 | No authority decision may silently override another. |
| 20 | Non-empty actor, ordered non-empty caller reasons with the required reason, timezone-aware caller time, and exact authority application policy ID/version are mandatory. |
| 21 | Use frozen contracts, canonical UTF-8 NFC sorted compact finite JSON, UTC microseconds with `Z`, SHA-256, prefix `ka1_`, and exact replay stability. |
| 22 | Identity includes record contract, candidate ID/contract/snapshot, ordered governance IDs, scope, intended value, outcome, reasons, actor, time, policy, and canonicalization. |
| 23 | Identity excludes diagnostics, direct review/conflict data, paths, implicit/random data, resolution, promotion, governed identity, lifecycle, acceptance, and persistence metadata. |
| 24 | Wrong exact types, malformed identities, invalid record invariants, invalid collections/strings/digests, and naive or wrong timestamps raise `ValueError`. |
| 25 | Supported-shape requests with unsupported policy/value/outcome or incompatible governance policy, lineage, or composition return `rejected`. |
| 26 | The exact eleven rejection reasons are listed in section 27. |
| 27 | The exact first-applicable precedence is the eleven-step sequence in section 27. |
| 28 | No. The service does not infer, normalize, insert, reorder, repair, or retry caller values. |
| 29 | No. An authorized authority value is one prerequisite only. |
| 30 | No. Authority decision does not execute promotion. |
| 31 | No. Authority decision creates no governed Knowledge. |
| 32 | No. It initializes neither lifecycle nor acceptance. |
| 33 | No repository or persistence is required. |
| 34 | Application decider depends on the authority domain, which depends only on existing candidate/governance/snapshot helpers; conflict remains a sibling. |
| 35 | Yes. Implementation remains additive within exactly four new files. |
| 36 | Require the 15-domain, 20-application, 35-total matrix in section 31. |
| 37 | Return to architecture review on any existing-contract edit, fifth file, inferred authority, conflict dependency, mutation, repository/persistence need, unresolved vocabulary, or downstream creation requirement. |
| 38 | `PR-029B - Minimal KnowledgeAuthorityDecision and Authority Decider Contract Implementation`. |

## 35. Definition of Done and stop conditions

PR-029A is complete when the exact branch, refs, divergences, clean state, and local/remote Phase 28 tag are verified; all authoritative documents, sources, tests, and available reports are inspected; current boundaries and absent contracts are explicit; all nine alternatives are compared; subject, lineage, vocabulary, outcomes, reasons, deterministic identity, malformed/rejected behavior, precedence, contradictions, dependencies, and exclusions are exact; the four-file PR-029B and 35-entry matrix are defined; exactly this repository document is added; the external report contains its complete verified snapshot; and no interpreter, test, package, ACL, existing-file, Git-history, merge, or tag action occurs.

Stop PR-029B and return to architecture review if an exact candidate and exact governance records cannot remain the only authority inputs; candidate or upstream mutation is required; source or conflict evidence would determine authority; review IDs must be duplicated directly; conflict lineage cannot remain independent; the two-value or three-outcome vocabulary is insufficient; deterministic identity requires implicit time, randomness, path, repository state, or mutable data; prior decisions must be silently ordered; promotion evaluation, governed creation, lifecycle, acceptance, repository, persistence, Prompt, AI, business, runtime, legacy, existing-contract edits, package exports, or a fifth file become necessary.

## 36. Final decision

# APPROVED FOR ONE MINIMAL PHASE 29 KNOWLEDGE AUTHORITY DECISION IMPLEMENTATION SLICE

The smallest honest next boundary is one immutable `KnowledgeAuthorityDecision` and one side-effect-free authority decider for an explicit intended future governed-Knowledge authority value, one exact `KnowledgeCandidate` snapshot, and exact authorized `KnowledgeGovernanceDecision` lineage. Approval is limited to PR-029B and the four new files in section 31.

This decision does not claim implementation exists, Phase 29 tests passed, authority was assigned to a candidate or applied to governed Knowledge, promotion prerequisites are complete, promotion occurred, governed Knowledge or acceptance exists, lifecycle changed, repository or persistence exists, PR-029A was committed, or Phase 29 was merged or tagged.
