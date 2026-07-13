# PR-027A - Knowledge Governance Authorization and Promotion Prerequisite Boundary Review

## 1. Review identity

| Item | Reviewed value |
|---|---|
| Review | PR-027A |
| Type | Review-only and documentation-only |
| Gate | Knowledge Governance Authorization and Promotion Prerequisite Boundary Review |
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-027-knowledge-governance-authorization-review` |
| Tests executed | None |
| Project interpreter executed | No |

This review identifies the smallest honest governance boundary after `KnowledgeReviewRecord`. It does not implement authorization, acceptance, promotion, governed Knowledge, persistence, merge, or tag behavior.

## 2. Repository and Phase 26 checkpoint

| Item | Verified value |
|---|---|
| Starting HEAD | `5798018cb7c7084fe477232c32a1b334f98916cb` |
| `main` | `5798018cb7c7084fe477232c32a1b334f98916cb` |
| `origin/main` | `5798018cb7c7084fe477232c32a1b334f98916cb` |
| Local Phase 27 ref | `5798018cb7c7084fe477232c32a1b334f98916cb` |
| Remote Phase 27 ref | `5798018cb7c7084fe477232c32a1b334f98916cb` |
| Phase-ref divergence | `0 0` |
| Phase 26 annotated tag | `v0.26.0-rcis-knowledge-review-record-phase` |
| Tag type | `tag` |
| Tag object | `7b2ea284b07012ece88d3c7a2bb552ae2ec4a786` |
| Peeled tag target | `5798018cb7c7084fe477232c32a1b334f98916cb` |

The Phase 26 tag and synchronized Phase 27 branch establish the authoritative starting checkpoint. The repository was clean and no file was staged before this document was created.

## 3. Current authoritative contracts

The current authoritative chain is:

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
-> future governance authorization
-> future promotion
-> future governed Knowledge
-> future Knowledge Repository
-> future Prompt Candidate
-> RCIS
```

Current authoritative contracts include immutable `AcceptedEvidence`, `AcceptanceRecord`, `KnowledgeCandidate`, and `KnowledgeReviewRecord`, deterministic `ev1_`, `ar1_`, `kc1_`, and `kr1_` identities, the side-effect-free Knowledge constructor, and the side-effect-free Knowledge reviewer.

Extraction output is not Evidence. `EvidenceCandidate` is not `AcceptedEvidence`. `AcceptedEvidence` is not Knowledge. `KnowledgeCandidate` is not reviewed or governed Knowledge. `KnowledgeReviewRecord` is review evidence only. A passed review is neither acceptance nor governance authorization.

## 4. KnowledgeCandidate role and limits

`KnowledgeCandidate` is the immutable deterministic construction result for one accepted factual statement and its support. Its complete representation can be canonically snapshot-digested. Its governance states remain fixed:

```text
authority_status = unassessed
lifecycle_status = candidate
review_status = pending_review
conflict_status = not_assessed
```

The candidate is the exact subject of review and future governance decisions. It must not be mutated, replaced, promoted in place, or represented by an unresolved ID in the next slice.

## 5. KnowledgeReviewRecord role and limits

`KnowledgeReviewRecord` is immutable review evidence for one exact candidate snapshot. It records candidate identity and snapshot digest, review decision, ordered reason codes, review-basis IDs, actor, time, and policy. Its decisions are `passed`, `rejected`, and `deferred`.

A passed record proves only that the exact candidate snapshot satisfied one explicit review event under one explicit policy. It does not accept, authorize, promote, assign authority, change lifecycle, clear conflict, create governed Knowledge, or select itself over contradictory records.

## 6. Current governed-Knowledge and governance-contract inventory

There is no current `KnowledgeGovernanceDecision`, `KnowledgePromotionAuthorization`, `KnowledgeAcceptanceRecord`, `KnowledgeConflictAssessmentRecord`, `KnowledgeAuthorityDecision`, `KnowledgeLifecycleTransitionRecord`, governed `Knowledge`, final `Knowledge`, or `KnowledgeRepository` under `src/rie`.

The absence is correct. Phase 26 deliberately stopped at immutable review evidence. Current Phase 23 through Phase 26 contracts are sufficient inputs for a separate authorization decision without redesign.

## 7. Legacy Knowledge and Prompt classification

Top-level `src/knowledge/*` types, `src/rie/knowledge/*` command wrappers, top-level `src/prompting/*` types, and `src/rie/prompt/*` command wrappers are frozen compatibility surfaces. Their manual IDs, positional indexes, mutable collections, historical status strings, export behavior, and direct legacy Knowledge-to-Prompt flow are not authoritative governance contracts.

They must not be modified, migrated, imported into the new boundary, or treated as evidence that governed Knowledge, a Knowledge repository, or a current Prompt Candidate boundary exists.

## 8. Governance vocabulary

| Term | Controlled meaning |
|---|---|
| Candidate construction | Deterministic creation of one immutable `KnowledgeCandidate` from exact accepted Evidence inputs |
| Candidate review | Explicit actor-and-policy evaluation of one exact candidate snapshot |
| Review evidence | One immutable `KnowledgeReviewRecord`; even `passed` is not authorization |
| Governance authorization | An explicit immutable decision that the reviewed candidate may or may not proceed to a later promotion-evaluation gate |
| Knowledge acceptance | A later governance event concerning governed Knowledge; not part of authorization |
| Conflict assessment | A later explicit record of conflict analysis; not inferred from review order or source authority |
| Promotion | A later application action that may create new governed Knowledge after every prerequisite is verified |
| Governed Knowledge | A future immutable object with its own identity, authority, lifecycle, provenance, and governance lineage |
| Authority assignment | A future explicit governance action; never inherited from source metadata |
| Lifecycle transition | A future explicit transition record; never implied by authorization |
| Persistence | A later storage concern behind a separately reviewed repository boundary |

## 9. Governance-decision boundary analysis

The next domain object should be `rie.domain.knowledge_governance_decision.KnowledgeGovernanceDecision`. It is an immutable governance authorization record, not another review record, acceptance event, promotion instruction, or lifecycle transition.

It is the smallest honest boundary because it can record an explicit governance decision about one exact reviewed candidate while changing no candidate state and creating no Knowledge. Its controlled decisions are:

```text
authorized
denied
deferred
```

`authorized` means only that the exact candidate snapshot is eligible to be considered by a future promotion-evaluation action under the recorded policy. It does not waive conflict, authority, lifecycle, acceptance, identity, or provenance prerequisites.

The initial side-effect-free governor supports exactly one governance application policy:

```text
KNOWLEDGE_GOVERNANCE_POLICY_ID = rcis-knowledge-governance-authorization
KNOWLEDGE_GOVERNANCE_POLICY_VERSION = 1.0.0
```

This application policy controls whether a `KnowledgeGovernanceRequest` is supported. It is not the deterministic governance-decision identity policy and is not the upstream review-evidence policy. The three responsibilities remain exact and separate:

| Responsibility | Exact policy ID | Version |
|---|---|---|
| Governance application | `rcis-knowledge-governance-authorization` | `1.0.0` |
| Governance-decision identity | `rcis-knowledge-governance-decision-identity` | `1.0.0` |
| Eligible review evidence | `rcis-knowledge-candidate-review` | `1.0.0` |

The governor must not reuse one policy identifier for another responsibility.

The initial governor accepts review evidence from exactly one review policy:

```text
review_policy_id = rcis-knowledge-candidate-review
review_policy_version = 1.0.0
```

Every supplied `KnowledgeReviewRecord` must independently carry both exact values. A valid record from another review policy remains valid domain review evidence but is unsupported governance evidence. Any ineligible record, including one mixed with eligible records, returns application status `rejected`, no governance decision record, and `("unsupported_review_evidence_policy",)`. No eligible record overrides an ineligible one.

The application result contract must be explicit:

```text
result_status = recorded | rejected
governance_decision_record = KnowledgeGovernanceDecision | None
reason_codes = tuple[str, ...]
diagnostics = tuple[KnowledgeGovernanceDiagnostic, ...]
```

For `unsupported_review_evidence_policy`, the exact result is `result_status="rejected"`, `governance_decision_record=None`, and `reason_codes=("unsupported_review_evidence_policy",)`.

## 10. Promotion-authorization boundary analysis

A separate `KnowledgePromotionAuthorization` is too broad for the next slice because its name implies authorization of the promotion action itself. The proposed governance record authorizes only eligibility for later promotion evaluation.

Promotion remains a separate future application action. It must not occur automatically after an `authorized` decision and must not be included in the same four-file slice.

## 11. Knowledge-acceptance boundary analysis

`KnowledgeAcceptanceRecord` is not the next object. There is no governed Knowledge object to accept, and candidate acceptance would collapse construction, review, governance, and promotion.

Authorization does not imply acceptance. Future acceptance or locking requires an explicit separately reviewed subject, state model, actor, policy, reason, time, and immutable audit record.

## 12. Conflict and contradiction analysis

The candidate remains `conflict_status="not_assessed"`. The next slice does not detect semantic conflict, create a conflict record, clear conflict, or claim `no_conflict`.

Review contradiction is narrower than semantic Knowledge conflict. A supplied review set containing both `passed` and `rejected` records for the same candidate snapshot is contradictory governance evidence. No input order, timestamp, actor, policy, source authority, or lexical record ID may select a winner.

Before evidence composition is classified, the tuple must be non-empty, exact, unique, and lexicographically ordered by `knowledge_review_record_id`. Every record must match the exact candidate ID, candidate contract version, recomputed complete candidate snapshot digest, valid `kr1_` identity, and eligible review policy `rcis-knowledge-candidate-review` version `1.0.0`.

### Exact initial review-evidence decision matrix

| Matrix | Complete evidence composition | Permitted requested governance decision and required reason | Forbidden request and explicit application rejection |
|---|---|---|---|
| A | All records are `passed` | `authorized` requires `eligible_review_evidence`; `deferred` requires `governance_evaluation_deferred` | `denied` returns `("incompatible_governance_decision",)` |
| B | All records are `rejected` | `denied` requires `review_evidence_rejected`; `deferred` requires `governance_evaluation_deferred` | `authorized` returns `("ineligible_review_evidence",)` |
| C | All records are `deferred` | Only `deferred`, requiring `incomplete_review_evidence` | `authorized` or `denied` returns `("incomplete_review_evidence",)` |
| D | At least one `passed` and one `rejected`, with or without `deferred`; this includes both passed-plus-rejected and passed-plus-rejected-plus-deferred | Only `deferred`, requiring `contradictory_review_evidence` | `authorized` or `denied` returns `("contradictory_review_evidence",)` |
| E | At least one `passed` and one `deferred`, with no `rejected` | Only `deferred`, requiring `incomplete_review_evidence` | `authorized` or `denied` returns `("incomplete_review_evidence",)` |
| F | At least one `rejected` and one `deferred`, with no `passed` | Only `deferred`, requiring `incomplete_review_evidence` | `authorized` or `denied` returns `("incomplete_review_evidence",)` |

The matrix classifies the complete supplied set. No subset or record silently overrides another. Passed records cannot override deferred records, and rejected records cannot turn incomplete evidence into denial. No input order, actor, timestamp, policy ordering, source authority, source lifecycle, record ID, or lexical rule selects a winner.

No separate conflict-assessment record is required merely to record this limited authorization decision. Semantic conflict detection and representation remain deferred, and explicit conflict assessment remains a required later promotion prerequisite.

## 13. Authority-assignment analysis

Authorization assigns no Knowledge authority. Candidate authority remains `unassessed`, and source authority remains provenance only. The authorization record must not contain a resulting authority status or derive a decision from source authority, classification, path, or lifecycle metadata.

Authority assignment requires a later reviewed contract and policy after governed Knowledge identity and promotion prerequisites are defined.

## 14. Lifecycle-transition analysis

Authorization performs no lifecycle transition. Candidate lifecycle remains `candidate`; its review status remains `pending_review` because the separate records provide review and governance evidence without candidate mutation.

No `reviewed`, `authorized`, `accepted`, `promoted`, `locked`, `rejected`, or `superseded` candidate state is introduced. A later lifecycle transition must be a separate immutable event.

## 15. Governed and final Knowledge analysis

Governed and final Knowledge must not be implemented next. Creating either would require approved identity, authority, lifecycle, conflict, acceptance, provenance, supersession, and repository semantics that do not yet exist.

The next slice creates no Knowledge object. Future governed Knowledge must receive a new identity and preserve the original `kc1_` candidate ID plus `kr1_` review and `kg1_` governance lineage. It must not reuse any of those identities.

## 16. Exact input-object boundary

The proposed `KnowledgeGovernanceRequest` must receive:

- one exact in-memory `KnowledgeCandidate`;
- one non-empty exact tuple of exact `KnowledgeReviewRecord` objects;
- one explicit governance decision;
- non-empty ordered unique reason codes;
- explicit actor ID;
- explicit caller-supplied timezone-aware timestamp;
- explicit `governance_policy_id` exactly `rcis-knowledge-governance-authorization` for a recorded result;
- explicit `governance_policy_version` exactly `1.0.0` for a recorded result.

The request carries both application-policy values. The governor copies the exact caller-supplied values unchanged into a recorded `KnowledgeGovernanceDecision`, and those values participate in `kg1_` identity. It must not insert, replace, normalize, repair, or infer them. A structurally valid request with another governance policy ID, version, or both is valid but unsupported application input: it returns `result_status="rejected"`, `governance_decision_record=None`, and `reason_codes=("unsupported_governance_policy",)`. An unsupported policy alone does not raise `ValueError`; non-string, empty, or whitespace-only policy values remain malformed programming inputs and do raise `ValueError`.

Every supplied review record must use exact review policy ID `rcis-knowledge-candidate-review` and version `1.0.0`. This requirement is independent for every tuple member. Mixed eligible and ineligible review-policy records are not partially accepted.

Unresolved candidate or review-record IDs, raw dictionaries, paths, `EvidenceCandidate`, `AcceptedEvidence`, extraction output, legacy Knowledge, Prompt Candidate, and duck-typed substitutes are forbidden.

## 17. Candidate and review-record consistency requirements

Every supplied review record must:

1. reference the supplied candidate's exact `knowledge_candidate_id`;
2. reference its exact candidate contract version;
3. carry the exact digest recomputed from the supplied complete candidate snapshot;
4. have a valid deterministic `kr1_` identity matching its contents;
5. use exact review policy ID `rcis-knowledge-candidate-review`;
6. use exact review policy version `1.0.0`;
7. appear once in a tuple ordered lexicographically by review-record ID.

The service must reject mismatched candidate IDs, candidate contracts, stale or different snapshot digests, duplicates, and unordered sets. It must not repair or replace review evidence, resolve IDs through a repository, or reread source assets.

One passed review is sufficient for `authorized` under the exact initial governance policy version only when every supplied record is passed, eligible, and consistent. Multiple passed records are permitted but not required. A future policy may require a different threshold only through a new reviewed version.

A malformed review-record object or broken identity raises `ValueError`. A valid `KnowledgeReviewRecord` using another review policy ID or version is not malformed; it returns an explicit rejected application result with reason `unsupported_review_evidence_policy` and no governance record.

## 18. Deterministic identity requirements

The proposed governance-decision identity policy is:

```text
class_name = KnowledgeGovernanceDecision
module = rie.domain.knowledge_governance_decision
contract_version = knowledge-governance-decision-v1
id_prefix = kg1_
identity_policy_id = rcis-knowledge-governance-decision-identity
identity_policy_version = 1.0.0
canonicalization_contract = knowledge-governance-decision-json-v1
digest_algorithm = sha256
timestamp_normalization = UTC with fixed microsecond precision
```

`KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_ID = rcis-knowledge-governance-decision-identity` and `KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_VERSION = 1.0.0` govern only deterministic identity construction. They are distinct from the request's application-policy values `KNOWLEDGE_GOVERNANCE_POLICY_ID = rcis-knowledge-governance-authorization` and `KNOWLEDGE_GOVERNANCE_POLICY_VERSION = 1.0.0`.

Identity fields are:

1. governance-decision contract version;
2. candidate ID and candidate contract version;
3. complete candidate snapshot digest;
4. ordered unique KnowledgeReviewRecord IDs;
5. authorization scope `eligible_for_future_promotion_evaluation`;
6. governance decision;
7. ordered reason codes;
8. actor;
9. caller-supplied decided-at timestamp normalized to UTC with six fractional digits;
10. governance policy ID and version;
11. identity canonicalization contract version.

Diagnostics, Python object identity, raw assets, paths, repository location, list position, implicit current time, random values, future conflict records, authority/lifecycle results, promotion metadata, governed Knowledge IDs, persistence metadata, and future acceptance data remain outside identity.

Use canonical UTF-8 JSON with NFC text normalization, sorted keys, compact separators, and no non-finite numbers. Exact replay produces the same `kg1_` ID. A material change to candidate snapshot, review evidence, scope, decision, reason, actor, time, policy, or contract creates a different ID.

## 19. Provenance and governance-lineage requirements

`KnowledgeGovernanceDecision` should contain exactly:

| Field | Purpose |
|---|---|
| `knowledge_governance_decision_id` | Deterministic `kg1_` identity |
| `contract_version` | Exact governance-decision contract |
| `knowledge_candidate_id` | Immutable candidate lineage |
| `knowledge_candidate_contract_version` | Reviewed candidate contract |
| `knowledge_candidate_snapshot_digest` | Complete exact candidate representation |
| `knowledge_review_record_ids` | Non-empty ordered unique exact `kr1_` lineage |
| `authorization_scope` | Exact limited action being authorized |
| `governance_decision` | `authorized`, `denied`, or `deferred` |
| `reason_codes` | Explicit non-empty ordered unique reasons |
| `decided_by` | Explicit governance actor |
| `decided_at` | Explicit timezone-aware caller time |
| `governance_policy_id` | Explicit policy identity |
| `governance_policy_version` | Explicit policy version |
| `diagnostics` | Immutable info/warning diagnostics outside identity |

The stable candidate snapshot digest and content-addressed review-record IDs preserve complete review and candidate lineage without copying mutable objects or requiring persistence.

Because every `kr1_` identity includes its review policy ID and version, the ordered record IDs preserve the exact reviewed policy lineage. The application must still inspect each supplied exact record and verify the eligible review policy before constructing a governance record.

## 20. Replay, duplicate, rejection, and contradiction handling

Exact replay is idempotent by identity and returns an equal record with the same `kg1_` ID. The side-effect-free service performs no durable duplicate suppression because no repository exists.

Contradictory governance decisions for the same candidate and review set remain independent immutable records. Neither time nor order selects a winner. Their later adjudication requires a separate governance policy and repository review.

A `denied` decision is not candidate mutation and is not silently reversible or terminal. A later explicit request may create another immutable record; it never overwrites the denial. Compatibility among historical decisions remains deferred.

For a recorded governance decision, `reason_codes` remains an exact non-empty immutable tuple whose values are unique and lexicographically ordered. The matrix-required reason code must already be present. Additional caller-supplied reason codes are permitted when valid, unique, and ordered. The service does not insert, reorder, remove, normalize, or repair reasons.

If the requested decision is otherwise matrix-compatible but the required reason is absent, the service returns application status `rejected`, no record, and `("missing_required_governance_reason",)`. This is a valid but incompatible request.

Malformed programming inputs raise `ValueError`, including wrong exact request/candidate/record/diagnostic types, non-tuple collections, empty or whitespace-only required values, non-string policy values, duplicate or unordered IDs/reasons, invalid identifiers, naive or wrong-type timestamps, broken record identity, and non-canonical collections. A well-formed but unsupported governance application policy is not malformed and does not raise `ValueError` solely because it is unsupported.

Valid but unsupported or policy-incompatible requests return an explicit rejected application result with no record. The initial rejection vocabulary is:

| Reason code | Exact condition |
|---|---|
| `unsupported_governance_policy` | Governance policy ID or version is unsupported |
| `unsupported_governance_decision` | Requested governance decision is unsupported |
| `unsupported_review_evidence_policy` | Any supplied valid review record uses another review policy ID or version |
| `review_candidate_mismatch` | A review record references another candidate ID |
| `review_candidate_contract_mismatch` | A review record references another candidate contract version |
| `review_candidate_snapshot_mismatch` | A review record snapshot digest differs from the recomputed candidate snapshot |
| `ineligible_review_evidence` | All-rejected evidence is asked to authorize |
| `contradictory_review_evidence` | Passed-plus-rejected evidence is asked to authorize or deny |
| `incomplete_review_evidence` | All-deferred, passed-plus-deferred, or rejected-plus-deferred evidence is asked to authorize or deny |
| `incompatible_governance_decision` | All-passed evidence is asked to deny |
| `missing_required_governance_reason` | A compatible request omits its matrix-required reason |

For every structurally valid request, application evaluation stops at the first applicable rejection in this exact precedence:

1. unsupported governance application policy ID or version: `unsupported_governance_policy`;
2. unsupported governance decision: `unsupported_governance_decision`;
3. any supplied review record using an unsupported review-evidence policy: `unsupported_review_evidence_policy`;
4. review candidate-ID mismatch: `review_candidate_mismatch`;
5. review candidate-contract mismatch: `review_candidate_contract_mismatch`;
6. review candidate-snapshot mismatch: `review_candidate_snapshot_mismatch`;
7. evidence-composition versus requested-decision incompatibility: the applicable exact matrix reason `ineligible_review_evidence`, `contradictory_review_evidence`, `incomplete_review_evidence`, or `incompatible_governance_decision`;
8. otherwise compatible request missing its matrix-required governance reason: `missing_required_governance_reason`;
9. otherwise record one `KnowledgeGovernanceDecision`.

This precedence begins only after request-domain validation succeeds. No later compatible evidence may override an earlier rejection. No eligible record compensates for an unsupported-policy record, and no evidence subset overrides the complete matrix classification.

## 21. Dependency and import review

The safe dependency direction is:

```text
rie.application.knowledge_governor
-> rie.domain.knowledge_governance_decision
-> rie.domain.knowledge_candidate
-> rie.domain.knowledge_review_record
```

The new domain file may import `KnowledgeCandidate` and `KnowledgeReviewRecord` for exact validation and projection helpers. Existing candidate and review-record modules must not import the new record, avoiding circular dependencies. The application service may import all three domain modules.

The application module owns the exact supported request-policy constants `KNOWLEDGE_GOVERNANCE_POLICY_ID = "rcis-knowledge-governance-authorization"` and `KNOWLEDGE_GOVERNANCE_POLICY_VERSION = "1.0.0"`. The governance-decision domain module owns its separate identity-policy constants `KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_ID = "rcis-knowledge-governance-decision-identity"` and `KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_VERSION = "1.0.0"`. Eligible upstream records independently carry review policy `rcis-knowledge-candidate-review` version `1.0.0`; neither new module replaces that lineage.

No new dependency is required. Legacy Knowledge, Prompt, interface, infrastructure, repository, filesystem, database, parser, network, AI, CLI, and runtime imports remain prohibited.

## 22. Repository, persistence, interface, and infrastructure decision

No interface, infrastructure, repository, serialization, database, migration, CLI, API, or UI file is required. The application request supplies exact objects, and the result returns one immutable governance record or an explicit rejection.

Durable uniqueness, lookup, cross-record contradiction queries, transactionality, and persistence require a later separately reviewed `KnowledgeRepository` boundary.

## 23. Explicitly forbidden behavior

The next implementation must not:

- mutate or replace `KnowledgeCandidate` or `KnowledgeReviewRecord`;
- accept raw dictionaries, paths, unresolved IDs, or duck-typed substitutes;
- perform repository lookup, filesystem reads, source-asset reads, or persistence;
- infer current time, generate randomness, or use UUID identity;
- infer governance from source authority, lifecycle, path, classification, actor rank, time, order, or lexical ID;
- reuse the governance application, governance-decision identity, or review-evidence policy ID for another responsibility;
- insert, replace, normalize, repair, or infer caller-supplied governance application policy values;
- raise `ValueError` solely because a structurally valid governance application policy ID or version is unsupported;
- evaluate a later decision or review-evidence condition before the supported governance application policy check;
- accept an unsupported review-evidence policy because another supplied record is eligible;
- classify valid unsupported-policy review evidence as malformed or raise `ValueError` solely for that policy mismatch;
- insert, reorder, remove, normalize, or repair governance reason codes;
- evaluate only a favorable subset of the supplied review tuple;
- automatically select a review winner or resolve conflict;
- automatically accept, authorize from incompatible evidence, promote, or retry;
- assign authority or change lifecycle;
- create conflict, acceptance, promotion, governed/final Knowledge, or Prompt Candidate objects;
- call AI or make business, brand, benefit, priority, or creative decisions;
- import, retrofit, migrate, rename, or delete legacy Knowledge or Prompt surfaces.

## 24. Deferred scope

The following remain deferred by default:

- promotion and promotion execution;
- governed Knowledge and final Knowledge;
- `KnowledgeAcceptanceRecord`;
- `KnowledgeConflictAssessmentRecord`, detection, representation, and adjudication;
- `KnowledgeAuthorityDecision` and authority assignment;
- `KnowledgeLifecycleTransitionRecord` and lifecycle transitions;
- multi-candidate composition;
- governed Knowledge identity;
- `KnowledgeRepository`, interfaces, infrastructure, serialization, persistence, databases, and migrations;
- repository orchestration, CLI, UI, API, and dashboards;
- Prompt Candidate, generators, embeddings, AI inference, and semantic synthesis;
- business and creative decisions;
- legacy Knowledge migration.

## 25. Preferred smallest implementation slice

**PR-027B - Minimal KnowledgeGovernanceDecision and Governor Contract Implementation**

The smallest safe slice is exactly one immutable governance decision and one side-effect-free application governor. It records authorization evidence only and stops before promotion or governed Knowledge.

### Required-question answers

| ID | Answer |
|---:|---|
| 1 | Implement `KnowledgeGovernanceDecision` next. |
| 2 | It is the first immutable boundary that can distinguish review evidence from explicit governance authorization without creating Knowledge. |
| 3 | It is a governance authorization decision record, not review, acceptance, promotion, or lifecycle transition. |
| 4 | It references one exact candidate ID, contract version, and complete snapshot digest. |
| 5 | It references a non-empty ordered tuple of exact compatible `KnowledgeReviewRecord` identities supplied as exact objects. |
| 6 | Yes. The exact `KnowledgeCandidate` object is required. |
| 7 | Yes. Exact `KnowledgeReviewRecord` objects are required. |
| 8 | No unresolved candidate or review-record identifier is accepted. |
| 9 | Yes. Every review record must reference the same supplied candidate ID. |
| 10 | Yes. Every review-record candidate snapshot digest must equal the recomputed supplied-candidate digest. |
| 11 | `passed`, `rejected`, and `deferred` are valid evidence only from review policy `rcis-knowledge-candidate-review` version `1.0.0`; `authorized` requires every supplied record to be eligible and passed. |
| 12 | Yes, one passed review is sufficient only under governance application policy `rcis-knowledge-governance-authorization` version `1.0.0` when the complete supplied set is passed, eligible, and consistent. |
| 13 | Multiple passed reviews are permitted, unique, and ordered; they are not required by policy `1.0.0`. |
| 14 | The exact six-composition matrix controls rejected/deferred evidence: all rejected may deny or defer; all deferred and every mixed deferred set may only defer; all outcomes require their matrix reason. |
| 15 | Passed-plus-rejected evidence, with or without deferred, is contradictory and may only yield explicit deferred with `contradictory_review_evidence`. |
| 16 | No order, time, actor, policy, source authority, or lexical ID selects a winner automatically. |
| 17 | No separate semantic conflict assessment is required merely to record limited eligibility authorization; the complete evidence matrix must still be enforced, and conflict assessment is required before later promotion. |
| 18 | Conflict representation is deferred; the next record makes no conflict-status claim. |
| 19 | Exactly `authorized`, `denied`, and `deferred`. |
| 20 | Use those controlled nouns as decision values; do not use `accept`, `promote`, or `approve Knowledge`. |
| 21 | Authorization covers eligibility of the exact reviewed candidate snapshot for a future promotion-evaluation gate only. |
| 22 | No governed Knowledge is created. |
| 23 | No authority status is assigned. |
| 24 | No lifecycle status changes. |
| 25 | Authorization does not imply acceptance. |
| 26 | Yes. Promotion remains a separate future application action. |
| 27 | Promotion must verify exact candidate and snapshot, compatible `authorized` governance evidence, non-contradictory reviews and governance decisions, explicit conflict assessment, authority assignment rule, lifecycle transition, actor/reason/policy/time, new identity, and provenance. |
| 28 | Yes. Candidate ID remains immutable lineage. |
| 29 | Yes. Future governed Knowledge requires a separately approved new identity. |
| 30 | Use `kg1_`, identity policy `rcis-knowledge-governance-decision-identity` version `1.0.0`, canonical JSON, and SHA-256; this is separate from the governance application policy. |
| 31 | Identity includes contracts, candidate ID/version/snapshot, ordered review IDs, scope, decision, reasons, actor, time, exact caller-supplied governance application policy ID/version, and canonicalization version. |
| 32 | Diagnostics, paths, raw assets, object identity, ordering position, implicit time, random data, conflict/authority/lifecycle/promotion/Knowledge/persistence metadata remain outside identity. |
| 33 | Record actor, caller-supplied reason codes including the required matrix reason, exact caller-supplied governance application policy `rcis-knowledge-governance-authorization` version `1.0.0`, explicit time, candidate snapshot evidence, and exact eligible review-record IDs without insertion or repair. |
| 34 | Exact replay returns the same identity; durable duplicate suppression is deferred. |
| 35 | Contradictory governance records coexist without winner selection and require later adjudication policy. |
| 36 | Denial is an immutable historical record, not mutation or terminal erasure; later records never overwrite it. |
| 37 | Wrong exact types, malformed IDs, empty strings/tuples, mutable/duplicate/unordered collections, naive timestamps, broken identities, and canonical collection violations raise `ValueError`. |
| 38 | Unsupported governance policy/decision, unsupported review-evidence policy, consistency mismatch, matrix-incompatible decision, and missing required reason return explicit rejection with no record in the exact first-applicable precedence defined in section 20. |
| 39 | No repository, persistence, serialization, interface, infrastructure, database, CLI, API, or UI is required. |
| 40 | Phase 23-26 Evidence, acceptance, candidate, review-record, identity, constructor, reviewer, repository, and adapter contracts remain unchanged. |
| 41 | All top-level Knowledge/Prompt types, `rie.knowledge` and `rie.prompt` wrappers, and any historical governance/lifecycle/authority/conflict/repository strings remain frozen compatibility surfaces. |
| 42 | Implement exactly the four files in section 26 and the focused matrix in section 27. |

## 26. Exact proposed file scope

PR-027B should add exactly:

1. `src/rie/domain/knowledge_governance_decision.py` - immutable diagnostic, identity input, governance decision record, candidate/review consistency projections, and deterministic `kg1_` identity;
2. `src/rie/application/knowledge_governor.py` - exact request, explicit result, policy checks, compatibility validation, and record construction;
3. `tests/domain/test_knowledge_governance_decision.py` - domain, identity, candidate snapshot, and review-lineage tests;
4. `tests/application/test_knowledge_governor.py` - application decisions, contradiction, rejection, boundary, and side-effect tests.

No existing file needs modification. If implementation requires another layer or file, stop and return to architecture review rather than widening scope.

## 27. Exact focused test matrix

### 27.1 Domain tests - `tests/domain/test_knowledge_governance_decision.py`

| ID | Exact assertion |
|---|---|
| D01 | Diagnostic, identity-input, and decision records are frozen, value-equal, and explicitly `kg1_` identified |
| D02 | Contract, identity policy, canonicalization, digest, scope, decision, and prefix constants are exact |
| D03 | Decision ID requires `kg1_` plus 64 lowercase hex characters and must match canonical content |
| D04 | Candidate ID, candidate contract, and complete snapshot digest are strict and required |
| D05 | Review-record IDs require a non-empty exact tuple, valid `kr1_` form, uniqueness, and lexical order |
| D06 | Scope is exactly `eligible_for_future_promotion_evaluation` |
| D07 | Only `authorized`, `denied`, and `deferred` governance decisions are accepted |
| D08 | Required strings, ordered reasons, and exact timezone-aware decided-at fail closed |
| D09 | Diagnostics accept only exact immutable info/warning members and remain outside identity |
| D10 | Canonical identity is UTF-8 JSON with NFC, sorted keys, fixed separators, fixed UTC microseconds, and SHA-256 |
| D11 | Exact replay returns the same canonical bytes and `kg1_` ID |
| D12 | Candidate snapshot, review IDs, scope, decision, reason, actor, time, policy, or contract changes identity |
| D13 | Paths, raw assets, diagnostics, conflict, authority, lifecycle, promotion, Knowledge, and persistence metadata are absent from identity |
| D14 | Identity and projection helpers reject wrong exact and duck-typed inputs |
| D15 | Identity extraction from a valid record round-trips exactly |

### 27.2 Application tests - `tests/application/test_knowledge_governor.py`

| ID | Exact assertion |
|---|---|
| A01 | One exact eligible matching passed review records one authorized decision without candidate or review mutation and requires `eligible_review_evidence` |
| A02 | Multiple exact eligible ordered matching passed reviews may authorize and all review IDs are preserved |
| A03 | All-passed evidence may record deferred only when `governance_evaluation_deferred` is present |
| A04 | All-passed evidence cannot record denied and returns `incompatible_governance_decision` |
| A05 | All-rejected evidence may record denied only when `review_evidence_rejected` is present |
| A06 | All-rejected evidence may record deferred only when `governance_evaluation_deferred` is present |
| A07 | All-rejected evidence cannot authorize and returns `ineligible_review_evidence` |
| A08 | All-deferred evidence may only record deferred with `incomplete_review_evidence`; authorized or denied requests reject explicitly |
| A09 | Passed-plus-rejected evidence may only record deferred with `contradictory_review_evidence`; authorized or denied requests reject explicitly |
| A10 | Passed-plus-rejected-plus-deferred evidence follows the same contradiction rule and never selects a winner |
| A11 | Passed-plus-deferred evidence may only record deferred with `incomplete_review_evidence` |
| A12 | Rejected-plus-deferred evidence may only record deferred with `incomplete_review_evidence` and may not silently become denied |
| A13 | A valid review record with an unsupported review policy ID or version returns `unsupported_review_evidence_policy` with no governance record, including mixed eligible/ineligible tuples |
| A14 | Candidate ID, candidate contract version, complete candidate snapshot digest, and `kr1_` identity must match every review record |
| A15 | A matrix-compatible decision missing its required governance reason returns `missing_required_governance_reason` without repairing the caller tuple |
| A16 | Unsupported governance policy ID, unsupported governance policy version, both unsupported policy values, or unsupported governance decision returns an explicit rejected result with no record; governance policy is checked before decision and review-evidence compatibility in the exact rejection precedence |
| A17 | Exact replay produces the same governance record and `kg1_` identity; material request changes produce a distinct identity |
| A18 | Raw dictionaries, paths, unresolved IDs, wrong domain objects, legacy Knowledge, Prompt objects, and duck-typed substitutes are rejected |
| A19 | Candidate, review records, request, reason tuples, and recorded or rejected results remain immutable and unchanged |
| A20 | Recorded authorization, denial, or deferral creates no acceptance, promotion, governed/final Knowledge, authority, lifecycle, conflict record, repository, persistence, Prompt, or AI result; contradictory governance records coexist without winner selection |
| A21 | Production imports and runtime behavior contain no interface, infrastructure, repository, filesystem, database, parser, network, subprocess, clock, randomness, UUID, AI, Prompt, CLI, logging side effect, automatic retry, or legacy Knowledge integration |

Matrix counts are exact:

```text
DOMAIN_MATRIX_ENTRY_COUNT = 15
APPLICATION_MATRIX_ENTRY_COUNT = 21
TOTAL_MATRIX_ENTRY_COUNT = 36
```

Focused execution after implementation, not during this review:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/domain/test_knowledge_governance_decision.py tests/application/test_knowledge_governor.py -q
```

## 28. Definition of Done

PR-027A is complete when:

- the synchronized Phase 27 branch and exact Phase 26 annotated checkpoint are verified;
- Phase 23-26 authoritative contracts and legacy surfaces are inspected;
- current governance, acceptance, promotion, conflict, authority, lifecycle, Knowledge, repository, and Prompt states are classified;
- `KnowledgeGovernanceDecision` is selected as the smallest honest next object;
- its exact relationship to one candidate and exact review records is defined;
- governance application policy `rcis-knowledge-governance-authorization` version `1.0.0`, governance-decision identity policy `rcis-knowledge-governance-decision-identity` version `1.0.0`, and eligible review-evidence policy `rcis-knowledge-candidate-review` version `1.0.0` are explicitly distinct;
- exact caller-supplied governance application policy values are required, copied unchanged into recorded decisions, and included in `kg1_` identity;
- unsupported but well-formed governance policy values return `unsupported_governance_policy` rather than `ValueError`;
- the exact first-applicable application rejection precedence is defined and begins only after request-domain validation;
- contradiction handling permits no winner selection;
- every review record independently uses eligible review policy `rcis-knowledge-candidate-review` version `1.0.0`;
- the exact six-composition evidence matrix and required governance reasons are explicit;
- unsupported review-evidence policy and missing required reason are explicit application rejections rather than malformed inputs;
- authorization is limited to future promotion-evaluation eligibility;
- deterministic `kg1_` identity and complete lineage are specified;
- replay, duplicate, denial, rejection, and contradiction behavior are explicit;
- promotion, acceptance, conflict assessment, governed/final Knowledge, authority, lifecycle, persistence, Prompt, AI, business, and legacy work remain deferred;
- one exact four-file implementation slice and exact focused matrix are approved;
- exactly this review document is created;
- no existing file, test, interpreter, Git history, merge, or tag is changed.

## 29. Stop conditions

Stop PR-027B and return to architecture review if:

- exact candidate and review-record objects cannot remain the sole inputs;
- complete candidate snapshot or review identities cannot be verified;
- exact governance application policy `rcis-knowledge-governance-authorization` version `1.0.0` cannot remain distinct from the governance-decision identity and review-evidence policies;
- caller-supplied governance application policy values cannot be preserved unchanged in the record and `kg1_` identity;
- unsupported governance policy cannot remain an explicit application rejection after malformed input validation;
- the exact first-applicable rejection precedence cannot be enforced without repair, inference, or later evidence overriding an earlier rejection;
- exact eligible review policy cannot be enforced independently for every supplied record;
- the complete evidence-decision matrix or required reason behavior cannot be implemented without inference or repair;
- authorization would require candidate mutation, acceptance, promotion, authority, lifecycle, or governed Knowledge;
- contradictory review evidence would be suppressed, ranked, or resolved automatically;
- semantic conflict assessment must be implemented in the same slice;
- raw paths, assets, unresolved IDs, repository lookup, persistence, interfaces, infrastructure, database, CLI, API, Prompt, AI, business logic, or legacy Knowledge becomes necessary;
- deterministic identity would require implicit time, randomness, list position, source path, or mutable data;
- an existing Phase 23-26 contract defect is found;
- implementation scope must exceed the exact four files without a reviewed reason;
- unrelated worktree changes overlap the approved scope.

## 30. Final decision

# APPROVED FOR MINIMAL KNOWLEDGE GOVERNANCE AUTHORIZATION IMPLEMENTATION

The smallest honest next boundary is an immutable `KnowledgeGovernanceDecision` and side-effect-free governor for one exact `KnowledgeCandidate` plus exact compatible `KnowledgeReviewRecord` values. Approval is limited to PR-027B and the four files in section 26. It does not claim or approve implementation, candidate mutation, Knowledge acceptance, promotion, governed/final Knowledge, authority or lifecycle assignment, conflict assessment or resolution, persistence, repository lookup, Prompt Candidate, AI, business decisions, runtime integration, merge, tag, or legacy migration.

Approval requires governance application policy `rcis-knowledge-governance-authorization` version `1.0.0`, separate governance-decision identity policy `rcis-knowledge-governance-decision-identity` version `1.0.0`, exact eligible review policy `rcis-knowledge-candidate-review` version `1.0.0`, the first-applicable rejection precedence, six-composition decision matrix, governance-reason behavior, and explicit application rejection vocabulary defined in this corrected review. No policy identifier substitutes for another responsibility, no evidence subset may override another, and authorization remains only eligibility for future promotion evaluation. Later promotion still requires separately reviewed conflict assessment, authority, lifecycle, identity, provenance, and governance prerequisites.
