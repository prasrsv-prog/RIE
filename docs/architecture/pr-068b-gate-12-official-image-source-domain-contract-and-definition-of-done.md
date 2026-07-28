# PR-068B Gate 12 Official Image Source Domain Contract and Definition of Done

Status: CANONICAL_GATE_12_CONTRACT_MATERIALIZED_PENDING_INDEPENDENT_REVIEW
Contract name: GATE_12_OFFICIAL_IMAGE_SOURCE_DOMAIN_CONTRACT_V1
Definition of Done name: GATE_12_OFFICIAL_IMAGE_SOURCE_DOMAIN_DEFINITION_OF_DONE_V1

## 1. Purpose

Define the minimum governed Official Image Source record and deterministic admission boundary required to complete Gate 12.

## 2. Scope

This contract is limited to source identity, source authority, usage rights, lifecycle state, checksum, byte length, provenance, admission status, registration metadata, and auditable validation behavior.

Supported source kinds:

- FILE
- REPOSITORY_ASSET
- CONTROLLED_EXTERNAL_REFERENCE

## 3. Required Official Image Source Record

The record contains exactly these twelve required fields:

1. source_id
2. source_locator
3. source_kind
4. content_sha256
5. byte_length
6. authority_class
7. rights_status
8. lifecycle_state
9. admission_status
10. provenance_parent_id
11. registered_at_utc
12. registered_by

## 4. Controlled Values

Authority classes:

- OFFICIAL_INTERNAL
- OFFICIAL_PARTNER
- CONTROLLED_EXTERNAL

Rights statuses:

- OWNED
- LICENSED
- APPROVED_INTERNAL_USE
- RESTRICTED

Lifecycle states:

- CANDIDATE
- ACTIVE
- SUPERSEDED
- RETIRED
- REVOKED

Admission statuses:

- PENDING
- ACCEPTED
- REJECTED

## 5. Deterministic Construction Validation

Construction must reject a record unless all required fields are present and valid.

The following validations are mandatory:

- source_id is a non-empty stable identifier.
- source_locator is non-empty.
- source_kind is one of the controlled source kinds.
- content_sha256 is exactly 64 lowercase hexadecimal characters.
- byte_length is a positive integer.
- authority_class is one of the controlled authority classes.
- rights_status is one of the controlled rights statuses.
- lifecycle_state is one of the controlled lifecycle states.
- admission_status is one of the controlled admission statuses.
- provenance_parent_id is either empty for a root source or a non-empty stable source identifier.
- registered_at_utc is a normalized UTC timestamp.
- registered_by is non-empty.

## 6. Contract Invariants

The contract enforces exactly these eight invariants:

1. source_id_is_stable_and_nonempty
2. content_sha256_is_lowercase_64_hex
3. byte_length_is_positive
4. authority_class_is_required
5. rights_status_is_required
6. accepted_source_requires_valid_identity_authority_rights_checksum_and_provenance
7. accepted_identity_fields_are_immutable
8. superseded_source_references_a_valid_predecessor

Accepted identity fields are source_id, source_locator, source_kind, content_sha256, byte_length, authority_class, rights_status, provenance_parent_id, registered_at_utc, and registered_by.

## 7. Lifecycle Boundary

The minimum lifecycle rules are:

- CANDIDATE may become ACTIVE only when admission_status is ACCEPTED and all construction validations pass.
- CANDIDATE may become RETIRED or REVOKED.
- ACTIVE may become SUPERSEDED, RETIRED, or REVOKED.
- SUPERSEDED, RETIRED, and REVOKED are terminal in Contract V1.
- A SUPERSEDED record must reference a valid predecessor through provenance_parent_id.

Lifecycle transition implementation is required by the Gate 12 Definition of Done but is not authorized by PR-068D.

## 8. Admission Boundary

An ACCEPTED source must satisfy all required field validation and all applicable contract invariants.

Admission decisions must be auditable before Gate 12 can close. Persistence and registry integration are outside the PR-068D boundary.

## 9. Gate 12 Definition of Done

Gate 12 is complete only when all ten criteria are independently accepted:

1. canonical_contract_is_materialized_and_accepted
2. official_image_source_record_model_is_implemented
3. authority_class_validation_is_deterministic
4. rights_status_validation_is_deterministic
5. lifecycle_transition_rules_are_enforced
6. checksum_and_byte_length_validation_are_enforced
7. provenance_parent_rules_are_enforced
8. admission_decision_is_auditable
9. persistence_round_trip_is_proven
10. targeted_tests_and_operator_evidence_are_accepted

## 10. Explicit Exclusions

The following capability classes are excluded from Gate 12 Contract V1:

- image_semantic_interpretation
- multimodal_knowledge
- image_extraction_artifact
- master_asset_library
- operator_dashboard
- local_ai_connector
- creative_workflow_orchestration

Gate 13 work, parser integration, CLI integration, real-asset execution, persistence, and registry integration are not authorized by PR-068D.

## 11. PR-068D Materialization Boundary

PR-068D is authorized only to:

- create branch phase-068-official-image-source-domain from the accepted Phase 67 checkpoint;
- materialize this canonical contract document at its selected path;
- verify that the selected source and test targets remain absent;
- emit external review evidence.

PR-068D does not authorize the Official Image Source record model, paired tests, persistence, registry integration, parser integration, CLI work, real assets, Gate 13, semantics, commit, push, tag, or release.
