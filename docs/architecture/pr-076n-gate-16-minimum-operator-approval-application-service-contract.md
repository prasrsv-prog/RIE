# PR-076N Gate 16 Minimum Operator Approval Application Service Contract

Status: bounded Gate 16 architecture contract
Gate: 16 - Operator Dashboard and Approval Workflow
Upstream accepted review: PR-076M
Selected gap: MINIMUM_OPERATOR_APPROVAL_APPLICATION_SERVICE_CONTRACT

## 1. Purpose

This contract defines the smallest application-service boundary required after
the accepted OperatorApprovalDecision and operator role-authority domain models.

The service boundary receives explicit approval intent plus explicit,
already-evaluated authorization and target-state evidence. It performs a
fail-closed orchestration assessment and returns an immutable, non-persistent
approval execution assessment.

This contract does not authorize target mutation. It does not approve, reject,
promote, publish, delete, persist, or otherwise change any governed object.

## 2. Accepted upstream authority

The following accepted identities remain authoritative:

- PR-076M raw report SHA256:
  `0ccbbd02455ae6b45183675f538a46954245bc4efd6694a33475b6cf8e97c36d`
- Accepted main commit:
  `cc88554eccdec33d5e7b695ade7979c339bd4893`
- Approval decision contract:
  `docs/architecture/pr-076b-gate-16-minimum-auditable-operator-approval-decision-contract.md`
- Approval decision model:
  `src/rie/domain/operator_approval_decision.py`
- Approval decision tests:
  `tests/domain/test_operator_approval_decision.py`
- Role-authority and permission contract:
  `docs/architecture/pr-076h-gate-16-minimum-operator-role-authority-and-permission-contract.md`
- Role-authority domain model:
  `src/rie/domain/operator_role_authority.py`
- Role-authority tests:
  `tests/domain/test_operator_role_authority.py`

The accepted models remain immutable and non-self-executing.

## 3. Fixed authority separations

The service boundary must preserve all of the following:

- Source Material != Extraction Result
- Extraction Result != Evidence
- Evidence != Knowledge
- Knowledge != business decision
- Prompt Candidate != final approved instruction
- OperatorApprovalDecision != executed lifecycle mutation
- Generated Output != Official Source
- Generated Output != Accepted Asset
- Generated Output != Approved Creative Asset

No automatic promotion is allowed between any layers.

## 4. Exact service responsibility

The application service may perform only these responsibilities:

1. accept one explicit `OperatorApprovalDecision`;
2. accept one explicit role-authority evaluation for the same operator, role,
   action, target type, reason, and audit context;
3. accept one explicit target approval context for the same target identity;
4. validate exact identity and reference agreement;
5. validate role-authority outcome;
6. validate current lifecycle eligibility;
7. validate provenance evidence;
8. validate rights evidence;
9. validate idempotency evidence;
10. validate conflict evidence;
11. validate reason and audit-context agreement; and
12. return one immutable non-persistent execution assessment.

The service must not discover data, read storage, infer missing facts, repair
inputs, select a target, or execute a lifecycle mutation.

## 5. Exact input boundary

A later separately authorized implementation must accept exactly three logical
inputs.

### 5.1 OperatorApprovalDecision

The accepted immutable decision supplies:

- `decision_id`
- `operator_reference`
- `role_reference`
- `target_type`
- `target_reference`
- `action`
- `reason_reference`
- `audit_context_reference`

Only `APPROVE` and `REJECT` are valid actions.

Only these target types are valid:

- `OFFICIAL_SOURCE_REGISTRY_ENTRY`
- `INGESTION_JOB`
- `EVIDENCE`
- `KNOWLEDGE`
- `KNOWLEDGE_CONFLICT`
- `PROMPT_CANDIDATE`
- `GOVERNED_ASSET_RECORD`

### 5.2 RoleAuthorityEvaluation

The accepted role-authority evaluation must provide explicit values for:

- `operator_reference`
- `role_reference`
- `target_type`
- `action`
- `outcome`
- `permission_reference`
- `reason_reference`
- `audit_context_reference`

The exact permitted authorization outcome is `ALLOW`.
Every other value, including an unknown or absent value, must deny execution
eligibility.

The service must verify exact equality between the decision and the
role-authority evaluation for operator, role, target type, action, reason, and
audit context.

### 5.3 TargetApprovalContext

The target approval context is immutable caller-supplied evidence. It must
contain:

- `target_type`
- `target_reference`
- `lifecycle_state`
- `lifecycle_eligibility`
- `lifecycle_reason_reference`
- `provenance_status`
- `provenance_reference`
- `rights_status`
- `rights_reference`
- `idempotency_status`
- `idempotency_reference`
- `conflict_status`
- `conflict_reference`
- `reason_reference`
- `audit_context_reference`

All fields are required non-empty ASCII text.

The service must verify exact equality between the decision and target context
for target type, target reference, reason reference, and audit context
reference.

## 6. Exact evidence vocabularies

The service accepts only the following positive evidence values:

- `lifecycle_eligibility = ELIGIBLE`
- `provenance_status = VERIFIED`
- `rights_status = CLEARED`
- `idempotency_status = NEW`
- `conflict_status = CLEAR`

Every other value is fail-closed and produces a denied assessment.

`idempotency_status = NEW` means only that the supplied, externally established
idempotency evidence reports no prior accepted execution for the exact
decision-id and target tuple. The service must not create, reserve, store, or
update an idempotency record.

`conflict_status = CLEAR` means only that supplied, externally established
conflict evidence reports no blocking conflict. The service must not discover,
resolve, persist, or mutate a conflict.

## 7. Ordered fail-closed checks

The application service must evaluate checks in this exact order:

1. decision type and required-field validity;
2. role-authority evaluation type and required-field validity;
3. target approval context type and required-field validity;
4. decision-to-role identity agreement;
5. decision-to-role action and target-type agreement;
6. decision-to-role reason and audit-context agreement;
7. authorization outcome equals `ALLOW`;
8. decision-to-target identity agreement;
9. decision-to-target reason and audit-context agreement;
10. lifecycle eligibility equals `ELIGIBLE`;
11. provenance status equals `VERIFIED`;
12. rights status equals `CLEARED`;
13. idempotency status equals `NEW`;
14. conflict status equals `CLEAR`; and
15. construct the immutable assessment.

Evaluation must stop at the first failed check. No later positive evidence may
override an earlier failure.

## 8. Immutable output

A later implementation must return an immutable
`OperatorApprovalExecutionAssessment` with exactly these fields:

- `decision_id`
- `operator_reference`
- `role_reference`
- `target_type`
- `target_reference`
- `action`
- `outcome`
- `reason_code`
- `reason_reference`
- `audit_context_reference`
- `permission_reference`
- `lifecycle_reason_reference`
- `provenance_reference`
- `rights_reference`
- `idempotency_reference`
- `conflict_reference`

Exact outcomes:

- `ELIGIBLE`
- `DENIED`

`ELIGIBLE` means only that the supplied evidence passed this contract. It does
not mean that a target mutation occurred or is automatically authorized.

`DENIED` means that execution eligibility was refused. It does not mutate or
reject the governed target.

## 9. Exact reason codes

The implementation may emit only these reason codes:

- `ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION`
- `INVALID_DECISION`
- `INVALID_ROLE_AUTHORITY_EVALUATION`
- `INVALID_TARGET_APPROVAL_CONTEXT`
- `OPERATOR_REFERENCE_MISMATCH`
- `ROLE_REFERENCE_MISMATCH`
- `TARGET_TYPE_MISMATCH`
- `TARGET_REFERENCE_MISMATCH`
- `ACTION_MISMATCH`
- `REASON_REFERENCE_MISMATCH`
- `AUDIT_CONTEXT_REFERENCE_MISMATCH`
- `ROLE_AUTHORITY_NOT_ALLOWED`
- `TARGET_LIFECYCLE_NOT_ELIGIBLE`
- `PROVENANCE_NOT_VERIFIED`
- `RIGHTS_NOT_CLEARED`
- `IDEMPOTENCY_NOT_NEW`
- `BLOCKING_CONFLICT_PRESENT`

No free-form reason code, inferred synonym, wildcard, or implicit fallback is
allowed.

## 10. Non-persistence and non-execution rules

The service contract explicitly prohibits:

- repository, database, filesystem, network, or direct-storage access;
- persistence of the decision, context, assessment, or audit history;
- mutation of an official-source registry entry;
- execution or cancellation of an ingestion job;
- evidence acceptance, rejection, promotion, or deletion;
- knowledge acceptance, rejection, promotion, or deletion;
- knowledge-conflict resolution;
- prompt-candidate approval or publication;
- governed-asset acceptance, rejection, publication, or lifecycle mutation;
- automatic retries, background jobs, or asynchronous execution; and
- automatic promotion from any candidate layer to an accepted layer.

A later mutation boundary must be separately reviewed, accepted, and
authorized. This contract does not pre-authorize it.

## 11. Application and adapter separation

The service is an application-layer orchestrator over already accepted domain
objects and caller-supplied evidence.

A future UI or CLI adapter may collect and submit explicit inputs only through
an accepted application service. An adapter must not:

- construct hidden authorization;
- bypass role-authority evaluation;
- read or write governed storage directly;
- infer lifecycle, provenance, rights, idempotency, or conflict status;
- modify the returned outcome; or
- execute a target mutation.

Authentication, identity-directory lookup, sessions, and multi-user runtime are
outside this boundary.

## 12. Exact future implementation paths

A later separately authorized implementation review may consider only:

- `src/rie/application/operator_approval_application_service.py`
- `tests/application/test_operator_approval_application_service.py`

The path names do not authorize implementation now.

No repository adapter, storage port, database migration, API route, web
framework, dashboard, or background worker may be introduced under this
contract materialization operation.

## 13. Minimum future acceptance criteria

A future implementation boundary must prove at minimum:

- immutable inputs and immutable output;
- exact ASCII non-empty validation;
- exact supported actions and target types;
- exact identity and reference agreement;
- deny-by-default behavior;
- first-failure deterministic ordering;
- exact positive evidence vocabularies;
- exact outcome and reason-code vocabularies;
- no mutation, persistence, I/O, network, clock, randomness, or hidden global
  state;
- no automatic promotion;
- deterministic equality and serialization-safe values;
- focused tests for every positive and negative branch; and
- preservation of all accepted Gate 14, Gate 15, and Gate 16 checkpoints.

## 14. Explicit non-goals

This contract does not authorize:

- application-service implementation;
- approval execution or target mutation;
- approval persistence or approval history;
- repository or database adapters;
- authentication providers;
- identity directories;
- sessions or multi-user collaboration;
- dashboard, UI, API, or web-framework work;
- direct storage access;
- background jobs;
- semantic search, embeddings, vector databases, ontologies, knowledge graphs,
  OCR, inference, or generalized AI/model abstractions;
- Gate 17 generator integration; or
- Gate 18 production implementation.

## 15. Closure statement

This contract closes only the minimum operator approval application-service
contract gap selected by PR-076M.

Gate 16 remains active and is not closed. The next operation after independent
acceptance is limited to publishing this exact contract. Any implementation
requires a later read-only gap review and a separately accepted boundary.
