# PR-076B - Gate 16 Minimum Auditable Operator Approval Decision Contract

## 1. Authority and scope

This contract is the first bounded Gate 16 materialization after the accepted PR-076A Correction 2 initiation and reconciliation review.

Gate 16 remains the Operator Dashboard and Approval Workflow phase. This document defines only the minimum auditable operator approval-decision boundary selected by PR-076A Correction 2. It does not implement a dashboard, web framework, authentication provider, persistence, storage access, workflow execution, or multi-user behavior.

The governing boundaries remain:

- every critical operator action must pass through a domain or application service;
- a UI adapter may present information and collect operator intent, but it may not write governed storage directly;
- validation, lifecycle, rights, provenance, and promotion rules may not be bypassed;
- every approval or rejection must preserve explicit operator, role, target, reason, and audit-context references;
- an approval decision is not self-executing;
- no automatic promotion is allowed.

## 2. Selected smallest gap

The selected smallest remaining Gate 16 gap is:

`MINIMUM_AUDITABLE_OPERATOR_APPROVAL_DECISION_CONTRACT`

This gap is narrower than approval persistence, approval-history storage, role-directory integration, authentication, authorization-policy execution, dashboard implementation, web routing, multi-user sessions, background jobs, notifications, or direct storage mutation.

## 3. Minimum operator approval decision

A minimum auditable operator approval decision contains exactly the following eight fields:

1. `decision_id`
   - Required stable identity for the decision.
   - Non-empty ASCII text.
   - Immutable after creation.
   - It identifies the decision value, not the target object and not an audit-history database row.

2. `operator_reference`
   - Required explicit reference to the operator who made the decision.
   - Non-empty ASCII text.
   - It is never inferred from a workstation, process owner, UI session label, filename, or network identity.

3. `role_reference`
   - Required explicit reference to the governed operator role asserted for the decision.
   - Non-empty ASCII text.
   - It records the role reference only; it does not implement authentication, role lookup, or authorization-policy evaluation.

4. `target_type`
   - Required exact controlled target classification.
   - Allowed values are exactly:
     - `OFFICIAL_SOURCE_REGISTRY_ENTRY`
     - `INGESTION_JOB`
     - `EVIDENCE`
     - `KNOWLEDGE`
     - `KNOWLEDGE_CONFLICT`
     - `PROMPT_CANDIDATE`
     - `GOVERNED_ASSET_RECORD`
   - No free-form target type is accepted.

5. `target_reference`
   - Required explicit reference to the governed target.
   - Non-empty ASCII text.
   - It is not inferred from a display row, current selection, route parameter, filesystem path, or mutable UI state.

6. `action`
   - Required exact decision action.
   - Allowed values are exactly `APPROVE` or `REJECT`.
   - No implicit, default, unknown, pending, or toggle state is accepted.

7. `reason_reference`
   - Required explicit reference to the controlled reason, review note, or reason record supporting the decision.
   - Non-empty ASCII text.
   - A missing reason reference makes the decision invalid.

8. `audit_context_reference`
   - Required explicit reference to the bounded audit context for the decision.
   - Non-empty ASCII text.
   - It does not itself define audit-history persistence, timestamps, event storage, or log transport.

No optional field is introduced by this contract.

## 4. Deterministic invariants

An operator approval decision conforms to this contract only when all of the following are true:

1. All eight fields are present.
2. All identity and reference fields are non-empty ASCII text.
3. `decision_id` is treated as an immutable identity.
4. `target_type` is one of the seven exact allowed values.
5. `action` is exactly `APPROVE` or `REJECT`.
6. `operator_reference` is explicit and is not inferred from execution environment state.
7. `role_reference` is explicit and is not inferred from operator identity or UI placement.
8. `target_reference` is explicit and is not inferred from a current view, selected row, filename, or storage location.
9. `reason_reference` is mandatory for both approval and rejection.
10. `audit_context_reference` is mandatory for both approval and rejection.
11. Missing or unsupported values fail closed.
12. The decision remains immutable after creation.
13. The decision does not directly mutate, delete, promote, accept, reject, publish, or persist its target.
14. The decision does not prove that the referenced role was authorized at execution time.
15. Duplicate, superseding, contradictory, or revoked decisions are not resolved by this contract.
16. No model output, heuristic, filename convention, UI default, or external tool result may create or alter the decision automatically.

## 5. Authority behavior

This contract records explicit operator intent only.

- `decision_id` identifies the immutable decision value.
- `operator_reference` identifies the asserted operator reference.
- `role_reference` identifies the asserted governed role reference.
- `target_type` and `target_reference` identify the governed subject of the decision.
- `action` records approval or rejection.
- `reason_reference` preserves the explicit reason boundary.
- `audit_context_reference` preserves the explicit audit-context boundary.

The decision is not itself:

- an authentication result;
- an authorization-policy result;
- a persisted approval-history entry;
- a database transaction;
- a storage mutation command;
- a lifecycle transition;
- a promotion execution;
- a publication command;
- a dashboard event;
- a notification;
- an automatic instruction to use or discard the target.

## 6. Application-service boundary

A future application service may consume this decision only through a separately accepted contract.

Before any target mutation, that service must independently validate:

1. the operator and role authority applicable at execution time;
2. the current target identity and state;
3. the target-specific lifecycle and governance rules;
4. provenance, rights, eligibility, and promotion prerequisites where applicable;
5. idempotency and conflict behavior;
6. persistence and audit-history requirements.

A UI adapter may submit the eight explicit fields to an accepted application service. It may not bypass that service, write storage directly, or treat a successful form submission as proof that the target mutation occurred.

## 7. Explicit non-expansion boundary

PR-076B does not authorize or define:

- dashboard, UI, HTML, CSS, JavaScript, desktop UI, or web framework implementation;
- authentication provider, identity provider, session management, or credential handling;
- role directory, policy engine, permission matrix, or authorization runtime;
- multi-user behavior, tenancy, collaboration, locking, or concurrent review;
- approval-history persistence, database schema, filesystem storage, event store, or migration;
- target mutation, lifecycle transition, promotion, publication, deletion, or rollback execution;
- direct UI access to repositories, databases, filesystems, or governed storage;
- background jobs, queues, notifications, email, webhook, or scheduled processing;
- search, semantic search, embeddings, vector databases, ontologies, knowledge graphs, or inference;
- OCR, AI connectors, model orchestration, local generator integration, or GPU management;
- tests, runtime source code, configuration, packaging, deployment, or branch creation;
- Gate 17 or Gate 18 implementation.

## 8. Contract acceptance evidence

PR-076B is complete only when independent evidence confirms:

1. the accepted PR-076A Correction 2 report is validated by exact SHA256 and semantics;
2. Gate 15 / Phase 74 remains officially closed;
3. main, origin/main, live main, and Phase 74 remain at the exact accepted checkpoint;
4. the repository begins clean;
5. the canonical target path is absent before materialization;
6. exactly one ASCII, LF-only Markdown document is created;
7. the document matches the exact expected SHA256, byte count, LF count, and Git blob;
8. the repository ends with exactly one untracked target path and no staged or tracked modification;
9. HEAD and all validated refs remain unchanged;
10. no branch creation, test execution, commit, push, UI implementation, persistence, or runtime implementation occurs.

## 9. Authorized continuation boundary

After independent acceptance of PR-076B, the only candidate continuation is:

`PR_076C_GATE_16_MINIMUM_AUDITABLE_OPERATOR_APPROVAL_DECISION_CONTRACT_STAGE_COMMIT_PUSH`

PR-076C may only stage, commit, and push the exact accepted contract document under a separately generated fail-closed artifact.

PR-076B does not authorize Gate 16 runtime implementation, dashboard implementation, approval persistence, branch creation, test execution, Gate 17, or Gate 18.
