# PR-076H Gate 16 Minimum Operator Role Authority and Permission Contract

Status: bounded Gate 16 architecture contract
Gate: 16 - Operator Dashboard and Approval Workflow
Upstream accepted review: PR-076G Correction 3
Selected gap: MINIMUM_OPERATOR_ROLE_AUTHORITY_AND_PERMISSION_BOUNDARY

## 1. Purpose

This contract defines the smallest authorization boundary required after the accepted
OperatorApprovalDecision domain model. It determines whether one explicitly
identified operator, acting under one explicitly identified role, is permitted to
submit one exact approval action for one exact governed target type.

This boundary is authorization evaluation only. It does not execute, persist,
promote, publish, delete, or otherwise mutate any governed target.

## 2. Accepted upstream authority

The following accepted identities remain authoritative:

- PR-076G Correction 3 raw report SHA256:
  `106b50dcabedc8bae4a40466c26252176b881a3780f0f622491410c91684e411`
- Accepted main commit:
  `bfa8cb8b3d60f55b1956bf787baa169b747946f0`
- Accepted approval decision contract:
  `docs/architecture/pr-076b-gate-16-minimum-auditable-operator-approval-decision-contract.md`
- Accepted approval decision model:
  `src/rie/domain/operator_approval_decision.py`
- Accepted approval decision tests:
  `tests/domain/test_operator_approval_decision.py`

The accepted OperatorApprovalDecision remains immutable and non-self-executing.

## 3. Fixed authority separations

The implementation governed by this contract must preserve all of the following:

- Source Material != Extraction Result
- Extraction Result != Evidence
- Evidence != Knowledge
- Knowledge != business decision
- Prompt Candidate != final approved instruction
- OperatorApprovalDecision != executed lifecycle mutation
- Generated Output != Official Source
- Generated Output != Accepted Asset
- Generated Output != Approved Creative Asset

No automatic promotion is allowed between any of these layers.

## 4. Exact supported approval vocabulary

The authorization boundary supports only the accepted approval actions:

- `APPROVE`
- `REJECT`

It supports only the accepted approval target types:

- `OFFICIAL_SOURCE_REGISTRY_ENTRY`
- `INGESTION_JOB`
- `EVIDENCE`
- `KNOWLEDGE`
- `KNOWLEDGE_CONFLICT`
- `PROMPT_CANDIDATE`
- `GOVERNED_ASSET_RECORD`

No wildcard action, wildcard target type, implicit alias, role hierarchy,
permission inheritance, or inferred permission is allowed.

## 5. Minimum authority records

A later separately authorized implementation must define immutable value records
with the following exact responsibilities.

### 5.1 OperatorRoleBinding

An OperatorRoleBinding proves only that one explicit operator reference is bound
to one explicit role reference for the supplied authorization context.

Required fields:

- `operator_reference`
- `role_reference`
- `binding_reference`
- `reason_reference`
- `audit_context_reference`

The binding does not authenticate a person, create a session, manage an identity
directory, or grant any action-target permission by itself.

### 5.2 RoleActionTargetPermission

A RoleActionTargetPermission expresses one exact permission tuple.

Required fields:

- `role_reference`
- `target_type`
- `action`
- `permission_reference`
- `reason_reference`
- `audit_context_reference`

The tuple is exact. A permission for one action or target type cannot authorize a
different action or target type.

### 5.3 OperatorRolePermissionEvaluation

An OperatorRolePermissionEvaluation records the deterministic result of evaluating
one explicit operator-role binding and one exact action-target permission request.

Required fields:

- `operator_reference`
- `role_reference`
- `target_type`
- `action`
- `outcome`
- `reason_code`
- `reason_reference`
- `audit_context_reference`

Exact outcomes:

- `ALLOW`
- `DENY`

The evaluation result is immutable, auditable, and non-self-executing.

## 6. Required input validation

All identity and reference fields are required non-empty ASCII text.

The evaluator must reject leading or trailing whitespace, control characters,
empty values, unsupported actions, and unsupported target types.

The following values must match exactly across the approval decision, operator-role
binding, permission request, and evaluation result:

- `operator_reference`
- `role_reference`
- `target_type`
- `action`

No value may be normalized into a different identity or inferred from another
record.

## 7. Deny-by-default evaluation

The evaluator must return `DENY` unless every required condition is proven.

An `ALLOW` result requires all of the following:

1. The approval decision is structurally valid.
2. The approval decision action and target type are in the exact supported
   vocabulary.
3. Exactly one supplied OperatorRoleBinding matches the decision's
   `operator_reference` and `role_reference`.
4. Exactly one supplied RoleActionTargetPermission matches the decision's
   `role_reference`, `target_type`, and `action`.
5. The binding, permission, and decision carry non-empty reason and audit context
   references.
6. No input is ambiguous, conflicting, incomplete, or unsupported.

Missing evidence, multiple conflicting matches, mismatched references, unsupported
values, or any ambiguity must produce `DENY`.

The evaluator must not consult a database, filesystem, network service,
authentication provider, session store, or UI state.

## 8. Exact reason codes

Every evaluation must expose exactly one deterministic reason code.

Allowed reason codes:

- `AUTHORIZED_EXACT_MATCH`
- `INVALID_INPUT`
- `UNSUPPORTED_ACTION`
- `UNSUPPORTED_TARGET_TYPE`
- `OPERATOR_REFERENCE_MISMATCH`
- `ROLE_REFERENCE_MISMATCH`
- `NO_EXACT_OPERATOR_ROLE_BINDING`
- `NO_EXACT_ROLE_ACTION_TARGET_PERMISSION`
- `AMBIGUOUS_AUTHORITY_EVIDENCE`

`AUTHORIZED_EXACT_MATCH` is valid only for an `ALLOW` outcome.
Every other reason code requires a `DENY` outcome.

A reason code is a deterministic classification. `reason_reference` and
`audit_context_reference` remain explicit external references and must not be
invented by the evaluator.

## 9. Relationship to OperatorApprovalDecision

The evaluator may inspect an accepted OperatorApprovalDecision, but it must not
modify it.

An `ALLOW` result means only that the exact operator-role-action-target tuple is
authorized to be submitted to a future separately accepted application-service
boundary.

An `ALLOW` result does not:

- approve or reject the target;
- mutate target lifecycle state;
- persist an approval;
- append approval history;
- promote evidence, knowledge, prompts, assets, or generated output;
- prove that the current target state is eligible for mutation;
- bypass provenance, rights, lifecycle, idempotency, or conflict checks.

A future application service must independently validate all execution
preconditions before any lifecycle mutation.

## 10. Determinism and auditability

For identical ordered inputs, the evaluator must return an equal immutable result.

The result must retain the explicit operator reference, role reference, action,
target type, outcome, reason code, reason reference, and audit context reference.

The evaluator must not use timestamps, randomness, environment variables, global
mutable state, network responses, storage lookups, model inference, or UI state to
derive the result.

## 11. Fail-closed behavior

Invalid construction and invalid evaluation input must fail closed.

The implementation must not silently:

- substitute an operator or role;
- choose one permission from conflicting permission evidence;
- treat missing permission as allow;
- expand a role through hierarchy or inheritance;
- convert an unsupported action or target type;
- execute a lifecycle mutation;
- persist an evaluation;
- access governed storage directly.

## 12. Future bounded implementation path

This contract does not authorize implementation by itself.

After this contract is independently accepted and published, a later separately
authorized implementation boundary may create only:

- `src/rie/domain/operator_role_authority.py`
- `tests/domain/test_operator_role_authority.py`

That later implementation must remain a pure domain authorization evaluator. It
must not add an application service, repository adapter, persistence schema,
authentication provider, identity directory, session runtime, dashboard, web
framework, or direct storage access.

## 13. Explicit non-expansion boundary

This contract does not authorize:

- authentication-provider integration;
- identity-directory implementation;
- login, session, token, or multi-user runtime;
- approval persistence or approval history;
- application-service execution;
- dashboard, UI, API, or web-framework work;
- repository, database, filesystem, or governed-storage access;
- background jobs;
- automatic target mutation or promotion;
- semantic search, embeddings, vector databases, ontology, knowledge graph, OCR,
  inference, or generalized AI/model abstractions;
- Gate 17 generator integration;
- Gate 18 production implementation;
- candidate Phase 75 branch creation;
- reopening Gate 14 or Gate 15.

## 14. Acceptance criteria

This contract is satisfied only when all of the following are independently
verified:

1. The contract exists at the exact authorized documentation path.
2. Its bytes, SHA256, line endings, encoding, and final-LF contract match the
   accepted PR-076H report.
3. The repository contained no pre-existing target path before materialization.
4. PR-076H changed only the exact contract path.
5. Main, origin/main, live main, Gate 14, and Gate 15 refs remain unchanged.
6. Candidate Phase 75 remains absent.
7. No tests, build, install, stage, commit, push, fetch, pull, branch, tag, or
   lifecycle mutation was performed during contract materialization.
8. The contract preserves deny-by-default behavior and all stated authority
   separations.
9. The next operation remains separately authorized and fail closed.

## 15. Current authorization result

PR-076H authorizes materialization of this documentation contract only.

It does not authorize the future domain implementation, application service,
approval persistence, audit history, dashboard, authentication, multi-user
runtime, Gate 17, or Gate 18.
