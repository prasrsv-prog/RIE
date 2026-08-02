# PR-076Q Gate 16 Minimum Operator Role-Authority Evaluation Permission-Reference Reconciliation Contract

Status: bounded Gate 16 reconciliation contract
Gate: 16 - Operator Dashboard and Approval Workflow
Upstream accepted review: PR-076P Correction 1
Selected gap: MINIMUM_OPERATOR_ROLE_AUTHORITY_EVALUATION_PERMISSION_REFERENCE_RECONCILIATION

## 1. Purpose

This contract resolves one exact compatibility gap between the accepted
role-authority domain model and the accepted operator-approval application
service contract.

The accepted `RoleActionTargetPermission` contains `permission_reference`.
The accepted `OperatorRolePermissionEvaluation` does not contain that field.
The accepted application-service contract requires the authorization
evaluation and later execution assessment to preserve `permission_reference`.

A valid positive approval path therefore cannot currently preserve the exact
permission evidence that authorized it.

This reconciliation contract defines only how that reference must be carried
forward. It does not implement the application service and does not execute any
approval or lifecycle mutation.

## 2. Accepted upstream authority

The following accepted identities remain authoritative:

- PR-076P Correction 1 raw report SHA256:
  `73eae7781f3f382875050a470a665d0c49868159da4679b114d2fc3325508a76`
- Accepted main commit:
  `b5eb9993a70d8588b71c573f688760d4c43cb578`
- Operator approval decision contract:
  `docs/architecture/pr-076b-gate-16-minimum-auditable-operator-approval-decision-contract.md`
- Operator approval decision model:
  `src/rie/domain/operator_approval_decision.py`
- Operator approval decision tests:
  `tests/domain/test_operator_approval_decision.py`
- Role-authority and permission contract:
  `docs/architecture/pr-076h-gate-16-minimum-operator-role-authority-and-permission-contract.md`
- Role-authority domain model:
  `src/rie/domain/operator_role_authority.py`
- Role-authority tests:
  `tests/domain/test_operator_role_authority.py`
- Operator approval application-service contract:
  `docs/architecture/pr-076n-gate-16-minimum-operator-approval-application-service-contract.md`

All accepted models remain immutable and non-self-executing.

## 3. Proven incompatibility

The accepted evidence establishes all of the following:

1. `RoleActionTargetPermission.permission_reference` is required immutable
   authority evidence.
2. `OperatorRolePermissionEvaluation` contains operator, role, target, action,
   outcome, reason, and audit fields.
3. `OperatorRolePermissionEvaluation` currently omits
   `permission_reference`.
4. The application-service contract requires `permission_reference` in the
   role-authority evaluation.
5. The application-service contract also requires the later execution
   assessment to expose `permission_reference`.
6. The application service is not allowed to infer, discover, or fabricate
   missing evidence.

Therefore the current positive `ALLOW` evaluation cannot satisfy the accepted
application-service contract without an explicit reconciliation.

## 4. Fixed reconciliation decision

The accepted role-authority evaluation must be extended with exactly one
additional evidence field:

```python
permission_reference: str | None
```

This field is part of the immutable evaluation result.

The field has these exact semantics:

- `ALLOW` requires one non-empty ASCII `permission_reference`.
- The value for `ALLOW` must equal the
  `RoleActionTargetPermission.permission_reference` from the unique exact
  permission evidence that produced the authorization.
- The evaluator must not accept a caller-supplied override.
- The evaluator must not synthesize, normalize, shorten, expand, or otherwise
  transform the reference.
- `DENY` may use `None` when no unique exact permission evidence exists.
- A `DENY` result must never be converted to `ALLOW` because a reference is
  present.
- A missing reference must never be compatible with an `ALLOW` result.

No other accepted evaluation field is removed, renamed, or relaxed.

## 5. Exact domain-model amendment

A later separately authorized implementation may modify only:

- `src/rie/domain/operator_role_authority.py`
- `tests/domain/test_operator_role_authority.py`

The source amendment must be limited to the following.

### 5.1 Evaluation value

`OperatorRolePermissionEvaluation` must include
`permission_reference: str | None`.

Validation must enforce:

- `None` is permitted only for fail-closed outcomes;
- a text value must pass the existing required ASCII-text validation;
- an empty string is never valid;
- `AUTHORIZED_EXACT_MATCH` requires `outcome = ALLOW`;
- `AUTHORIZED_EXACT_MATCH` also requires a non-empty
  `permission_reference`;
- every other reason code continues to require `outcome = DENY`; and
- no permission reference can independently authorize an outcome.

### 5.2 Evaluation construction

The internal evaluation constructor must accept the permission reference
explicitly.

Every deny path that has not resolved one unique exact permission evidence must
set:

```python
permission_reference=None
```

The unique exact allow path must set:

```python
permission_reference=exact_permissions[0].permission_reference
```

No other source may populate that value.

### 5.3 Existing authority behavior

All existing behavior must remain unchanged:

- exact operator-role binding is required;
- exact role-action-target permission is required;
- ambiguous evidence denies;
- unsupported action denies;
- unsupported target type denies;
- invalid input denies;
- no matching binding denies;
- no matching permission denies;
- the evaluator remains deterministic;
- the evaluator performs no I/O;
- the evaluator performs no lifecycle mutation; and
- deny-by-default remains mandatory.

## 6. Application-service compatibility

A later application-service implementation may consume the reconciled field
only as follows:

- `ELIGIBLE` requires `role_evaluation.outcome = ALLOW`;
- `ELIGIBLE` requires a non-empty
  `role_evaluation.permission_reference`;
- the resulting execution assessment must preserve that exact value;
- the application service must not accept a separate permission-reference
  argument;
- the application service must not look up permission evidence;
- the application service must not invent a fallback reference; and
- `None`, empty, malformed, or conflicting references must fail closed.

For an ineligible assessment, the permission reference may remain `None` when
the supplied authorization evaluation contains no unique exact permission
evidence.

This contract does not otherwise expand or replace PR-076N.

## 7. Exact test boundary

A later separately authorized implementation must preserve every accepted
role-authority test and add focused evidence for at least:

1. an exact allow evaluation preserves the exact permission reference;
2. a different permission reference is not substituted;
3. every no-match deny path returns `permission_reference is None`;
4. ambiguous permission evidence returns `permission_reference is None`;
5. unsupported action and target outcomes return `None`;
6. invalid collection input returns `None`;
7. direct construction of `ALLOW` without a reference is rejected;
8. direct construction of `AUTHORIZED_EXACT_MATCH` without a reference is
   rejected;
9. empty, non-ASCII, whitespace-padded, and control-character references are
   rejected when supplied as text;
10. a deny result cannot become allowed merely because a reference is present;
11. immutability remains enforced; and
12. existing decision and role-authority behavior remains regression-safe.

The bounded targeted verification set for that later implementation is:

- `tests/domain/test_operator_approval_decision.py`
- `tests/domain/test_operator_role_authority.py`

Full-suite execution is not authorized by this contract.

## 8. Authority separations

The reconciliation must preserve all of the following:

- Source Material != Extraction Result
- Extraction Result != Evidence
- Evidence != Knowledge
- Knowledge != business decision
- Prompt Candidate != final approved instruction
- OperatorApprovalDecision != executed lifecycle mutation
- Role-authority evaluation != executed approval
- Application-service assessment != persisted approval history
- Generated Output != Official Source
- Generated Output != Accepted Asset
- Generated Output != Approved Creative Asset

No automatic promotion is allowed between any layers.

## 9. Non-expansion boundary

This contract does not authorize:

- application-service implementation;
- repository adapters;
- persistence or database work;
- approval-history materialization;
- target mutation;
- dashboard or UI work;
- web frameworks;
- authentication providers;
- identity directories;
- sessions;
- multi-user runtime;
- background jobs;
- direct storage access;
- clock or randomness;
- network access by domain code;
- automatic promotion;
- semantic search;
- embeddings;
- vector databases;
- ontologies;
- knowledge graphs;
- OCR;
- inference;
- generalized AI-model abstraction;
- Gate 17 implementation; or
- Gate 18 implementation.

## 10. Materialization boundary

This PR may materialize exactly one documentation path:

`docs/architecture/pr-076q-gate-16-minimum-operator-role-authority-evaluation-permission-reference-reconciliation-contract.md`

It must not modify the accepted source or tests.

The document must remain untracked after materialization. Stage, commit, and
push require a separate independently authorized operation.

## 11. Acceptance criteria

This contract is complete only when all of the following are true:

1. PR-076P Correction 1 is independently validated.
2. The accepted repository checkpoint remains exact.
3. The accepted application-service contract remains exact.
4. The accepted role-authority source and tests remain exact.
5. The compatibility gap is described without broadening Gate 16.
6. The permission reference source is the unique exact accepted permission
   evidence only.
7. Positive and negative evaluation semantics are explicit.
8. No implementation is performed.
9. Exactly one documentation path is materialized.
10. The target byte contract is exact.
11. The Git index remains unchanged.
12. No prohibited operation is performed.

## 12. Next sequencing

After independent acceptance of this materialization, the only candidate next
operation is a separately bounded stage, commit, and push of this exact
contract path.

No role-authority source amendment or application-service implementation is
authorized until that publication is independently accepted and a later
evidence-driven review explicitly selects the next gap.
