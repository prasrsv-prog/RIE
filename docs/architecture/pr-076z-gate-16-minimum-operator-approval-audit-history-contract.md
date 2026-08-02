# PR-076Z Gate 16 Minimum Operator Approval Audit History Contract

Status: bounded Gate 16 architecture contract
Gate: 16 - Operator Dashboard and Approval Workflow
Upstream accepted review: PR-076Y Correction 1
Selected gap: MINIMUM_OPERATOR_APPROVAL_AUDIT_HISTORY_BOUNDARY

## 1. Purpose

This contract defines the smallest audit-history boundary required after the
accepted and published operator approval application service.

The boundary records immutable facts about one explicit
OperatorApprovalDecision and one explicit
OperatorApprovalExecutionAssessment. It defines deterministic append-only
history semantics and bounded pure read semantics.

This contract does not implement persistence. It does not execute an approval,
mutate a target, promote an object, or authorize a dashboard.

## 2. Accepted upstream authority

The following accepted identities remain authoritative:

- PR-076Y Correction 1 raw report SHA256:
  `984034fd338d86f84e43fa61b5eb60e3932efaa00d122962071abcbed4030a65`
- Accepted main commit:
  `7f500b5f1c5fca4e2b4f510b00a627f4c59bcbde`
- Operator approval decision model:
  `src/rie/domain/operator_approval_decision.py`
- Operator role-authority model:
  `src/rie/domain/operator_role_authority.py`
- Operator approval application-service contract:
  `docs/architecture/pr-076n-gate-16-minimum-operator-approval-application-service-contract.md`
- Operator approval application service:
  `src/rie/application/operator_approval_application_service.py`
- Operator approval application-service tests:
  `tests/application/test_operator_approval_application_service.py`

The application-service assessment remains non-persistent and
non-self-executing.

## 3. Fixed authority separations

The audit-history boundary must preserve all of the following:

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

## 4. Exact audit-record responsibility

A later separately authorized implementation may only:

1. accept one explicit valid OperatorApprovalDecision;
2. accept one explicit OperatorApprovalExecutionAssessment for that decision;
3. validate exact identity and reference agreement;
4. construct one immutable OperatorApprovalAuditRecord;
5. append that record to one immutable in-memory history value;
6. detect exact duplicates and identity conflicts deterministically; and
7. expose bounded pure reads over the supplied immutable history value.

The boundary must not discover data, infer missing facts, repair identifiers,
read storage, write storage, execute approval, or mutate a governed target.

## 5. Immutable OperatorApprovalAuditRecord

A future record value must contain exactly these fields:

- `audit_record_id`
- `decision_id`
- `operator_reference`
- `role_reference`
- `permission_reference`
- `target_type`
- `target_reference`
- `action`
- `assessment_outcome`
- `assessment_reason_code`
- `reason_reference`
- `audit_context_reference`
- `lifecycle_reason_reference`
- `provenance_reference`
- `rights_reference`
- `idempotency_reference`
- `conflict_reference`

All non-optional fields must be non-empty ASCII text without leading or
trailing whitespace or control characters.

The following assessment-derived reference fields may be absent only when the
assessment outcome is `DENIED`:

- `permission_reference`
- `lifecycle_reason_reference`
- `provenance_reference`
- `rights_reference`
- `idempotency_reference`
- `conflict_reference`

An `ELIGIBLE` assessment requires every reference field to be present and valid.

The audit record must copy facts exactly. It must not normalize, substitute,
generate, enrich, or infer any identifier or reference.

## 6. Exact decision and assessment agreement

The record constructor must verify exact equality between the decision and the
assessment for:

- `decision_id`
- `operator_reference`
- `role_reference`
- `target_type`
- `target_reference`
- `action`
- `reason_reference`
- `audit_context_reference`

The assessment outcome must be exactly one of:

- `ELIGIBLE`
- `DENIED`

The assessment reason code must be one of the exact reason codes accepted by
the application-service contract and implementation.

Any mismatch, unsupported outcome, unsupported reason code, malformed
reference, or inconsistent eligible assessment must fail closed and must not
produce an audit record.

## 7. Audit record identity

`audit_record_id` is explicit caller-supplied identity.

It must be non-empty ASCII text without leading or trailing whitespace or
control characters. The boundary must not generate it from a clock, random
value, hash, database sequence, network service, or hidden global state.

The same `audit_record_id` always denotes the same complete audit-record facts.

## 8. Immutable history value

A future OperatorApprovalAuditHistory value contains only an ordered immutable
tuple of OperatorApprovalAuditRecord values.

The empty history is valid.

The stored order is append order. A later implementation must not sort,
reorder, replace, update, or delete an existing record.

No timestamp is required or authorized by this minimum boundary.

## 9. Deterministic append outcomes

A future pure append operation may return only:

- `APPENDED`
- `EXACT_DUPLICATE`
- `CONFLICT`

The operation evaluates in this exact order:

1. validate the supplied history value;
2. validate the supplied audit record;
3. search existing records for the same `audit_record_id`;
4. if the same id has exact complete value equality, return
   `EXACT_DUPLICATE` with the original history unchanged;
5. if the same id has any different fact, return `CONFLICT` with the original
   history unchanged;
6. search existing records for the same pair of `decision_id` and
   `audit_context_reference`;
7. if that pair already exists under another audit-record id, return
   `CONFLICT` with the original history unchanged; and
8. otherwise append exactly one record and return `APPENDED`.

No later record may override an earlier record. No conflict may be repaired or
merged inside this boundary.

## 10. Append result

A future immutable OperatorApprovalAuditAppendResult contains exactly:

- `outcome`
- `history`
- `record`
- `conflicting_audit_record_id`

Rules:

- `APPENDED` returns the new history and the appended record.
- `EXACT_DUPLICATE` returns the original history and the existing exact record.
- `CONFLICT` returns the original history, no new record, and the conflicting
  existing audit-record id.
- `conflicting_audit_record_id` must be absent for `APPENDED` and
  `EXACT_DUPLICATE`.
- No free-form outcome or implicit fallback is allowed.

## 11. Bounded pure read boundary

A future implementation may expose only these pure reads:

1. find by exact `audit_record_id`, returning zero or one record;
2. list by exact `decision_id`;
3. list by exact `operator_reference`;
4. list by exact `target_type` plus exact `target_reference`; and
5. list by exact `audit_context_reference`.

Every list read requires an explicit integer `limit` from 1 through 100.

Results preserve append order and return at most `limit` records. Reads must not
sort, rank, infer, paginate through storage, mutate history, or perform I/O.

No fuzzy, semantic, wildcard, prefix, substring, or full-text search is
authorized.

## 12. Non-persistence boundary

This contract explicitly prohibits:

- repository adapters;
- database, filesystem, object-store, or network persistence;
- direct storage access;
- migrations or schemas;
- write-ahead logs or event buses;
- clock or timestamp acquisition;
- random or generated identifiers;
- background jobs, retries, or asynchronous processing;
- mutation or deletion of an existing audit record;
- approval execution or target lifecycle mutation; and
- automatic promotion.

A later persistence boundary requires a separate evidence-driven review and
explicit authorization.

## 13. Existing generic history remains separate

The accepted Phase 35 acceptance-decision history interpretation documents
remain valid and unchanged.

They do not substitute for this Gate 16 operator approval audit-history
contract. This contract does not modify, reinterpret, or merge those prior
boundaries.

## 14. Exact future implementation paths

A later separately authorized implementation review may consider only:

- `src/rie/domain/operator_approval_audit_history.py`
- `tests/domain/test_operator_approval_audit_history.py`

These path names do not authorize implementation now.

No application-service integration, repository adapter, storage port,
migration, API route, dashboard, web framework, or background worker may be
introduced under this contract materialization operation.

## 15. Minimum future acceptance criteria

A future implementation boundary must prove at minimum:

- immutable record, history, and append-result values;
- exact required and optional field validation;
- exact decision-to-assessment agreement;
- exact eligible-reference requirements;
- caller-supplied deterministic record identity;
- append-only behavior;
- exact duplicate idempotency;
- deterministic conflict handling;
- preservation of original history on duplicate or conflict;
- exact append outcome vocabulary;
- bounded reads with limits from 1 through 100;
- append-order preservation;
- no mutation, persistence, I/O, network, clock, randomness, or hidden global
  state;
- no automatic promotion;
- focused tests for every positive and negative branch; and
- preservation of all accepted Gate 14, Gate 15, and Gate 16 checkpoints.

## 16. Explicit non-goals

This contract does not authorize:

- audit-history implementation;
- audit-history persistence;
- application-service integration;
- approval execution or target mutation;
- repository or database adapters;
- dashboard, UI, API, or web-framework work;
- authentication providers;
- identity directories;
- sessions or multi-user collaboration;
- direct storage access;
- background jobs;
- semantic search, embeddings, vector databases, ontologies, knowledge graphs,
  OCR, inference, or generalized AI/model abstractions;
- Gate 17 generator integration; or
- Gate 18 production implementation.

## 17. Closure statement

This contract closes only the minimum operator approval audit-history contract
gap selected by PR-076Y Correction 1.

Gate 16 remains active and is not closed. The next operation after independent
acceptance is limited to publishing this exact contract. Any implementation
requires a later read-only gap review and a separately accepted boundary.
