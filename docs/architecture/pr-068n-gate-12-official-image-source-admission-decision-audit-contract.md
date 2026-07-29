# PR-068N Gate 12 Official Image Source Admission Decision Audit Contract Detail

Status: CANONICAL_SUBORDINATE_GATE_12_ADMISSION_DECISION_AUDIT_CONTRACT_DETAIL_MATERIALIZED_PENDING_INDEPENDENT_REVIEW
Contract detail name: GATE_12_OFFICIAL_IMAGE_SOURCE_ADMISSION_DECISION_AUDIT_CONTRACT_V1
Parent contract: GATE_12_OFFICIAL_IMAGE_SOURCE_DOMAIN_CONTRACT_V1
Parent Definition of Done criterion: admission_decision_is_auditable

## 1. Purpose

Define the minimum immutable audit evidence record required to prove that an Official Image Source admission decision is attributable, explainable, linked to a governed source, and independently reviewable.

## 2. Scope

This contract detail governs only the audit evidence for one terminal admission decision from PENDING to ACCEPTED or REJECTED.

The audit evidence record is separate from the twelve-field OfficialImageSource record. This contract detail does not add fields to, replace, or mutate the canonical OfficialImageSource record shape.

## 3. Required Admission Decision Audit Record

The record contains exactly these nine required fields:

1. decision_id
2. source_id
3. prior_admission_status
4. resulting_admission_status
5. reason_code
6. reason_detail
7. evidence_reference
8. decided_at_utc
9. decided_by

## 4. Controlled Values

Prior admission status:

- PENDING

Resulting admission statuses:

- ACCEPTED
- REJECTED

Reason codes:

- ACCEPTED_VALIDATED
- REJECTED_IDENTITY_INVALID
- REJECTED_AUTHORITY_INVALID
- REJECTED_RIGHTS_INVALID
- REJECTED_CHECKSUM_INVALID
- REJECTED_BYTE_LENGTH_INVALID
- REJECTED_PROVENANCE_INVALID
- REJECTED_OTHER_CONTRACT_VIOLATION

## 5. Deterministic Construction Validation

Construction must reject an audit record unless all nine required fields are present and valid.

The following validations are mandatory:

- decision_id is a non-empty stable identifier.
- source_id is a non-empty stable identifier.
- prior_admission_status is exactly PENDING.
- resulting_admission_status is ACCEPTED or REJECTED.
- reason_code is one of the controlled reason codes.
- reason_detail is non-empty and contains the human-reviewable decision explanation.
- evidence_reference is non-empty and identifies the evidence set used for the decision.
- decided_at_utc is a normalized UTC timestamp.
- decided_by is non-empty.

## 6. Contract Detail Invariants

This contract detail enforces exactly these ten invariants:

1. decision_id_is_stable_and_nonempty
2. source_id_is_stable_and_nonempty
3. prior_admission_status_is_pending
4. resulting_admission_status_is_terminal
5. accepted_decision_uses_accepted_validated_reason
6. rejected_decision_uses_rejection_reason
7. reason_detail_is_nonempty
8. evidence_reference_is_nonempty
9. decision_actor_and_utc_timestamp_are_required
10. accepted_audit_record_is_immutable

An ACCEPTED result must use reason_code ACCEPTED_VALIDATED.

A REJECTED result must use one of the seven REJECTED reason codes and must not use ACCEPTED_VALIDATED.

## 7. Source Linkage Boundary

The audit record source_id identifies the governed OfficialImageSource record whose admission status is decided.

A future admission-audit implementation must reject a decision whose source_id does not match its governed source record.

Applying the decision to the OfficialImageSource record, enforcing cross-record uniqueness, registry lookup, and persistence are outside the PR-068N materialization boundary.

## 8. Admission Auditability Definition of Done

The admission_decision_is_auditable criterion is proven only when all eight subordinate criteria are independently accepted:

1. admission_audit_contract_detail_is_materialized_and_accepted
2. admission_decision_audit_record_model_is_implemented
3. controlled_admission_result_validation_is_deterministic
4. result_and_reason_code_consistency_is_enforced
5. source_linkage_validation_is_enforced
6. decision_actor_timestamp_reason_and_evidence_are_required
7. accepted_admission_audit_record_is_immutable
8. targeted_tests_and_operator_evidence_are_accepted

## 9. Explicit Exclusions

The following capability classes are excluded from this contract detail:

- persistence
- registry_integration
- parser_integration
- cli_integration
- real_asset_execution
- gate_13_work
- image_semantic_interpretation
- operator_dashboard
- admission_decision_workflow_orchestration
- modification_of_the_twelve_field_official_image_source_record

## 10. PR-068N Materialization Boundary

PR-068N is authorized only to:

- preserve the canonical Gate 12 contract unchanged;
- materialize this subordinate contract-detail document at the selected path;
- verify that no admission-audit model or paired test mutation occurs;
- emit external review evidence.

PR-068N does not authorize admission-audit implementation, persistence, source or test mutation, Python, pytest, the full suite, stage, commit, push, Gate 13, tag, or release.
