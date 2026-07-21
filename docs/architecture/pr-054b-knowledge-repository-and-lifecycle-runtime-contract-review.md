# PR-054B - Knowledge Repository and Lifecycle Runtime Contract Review

## 1. Review identity

This document selects the minimum runtime contract for Gate 9 - Knowledge Repository and Lifecycle.

Repository checkpoint: `8640272b3abba152d5e4283448280d299ea69173`.

Phase branch: `phase-054-knowledge-repository-and-lifecycle`.

Selected PR-054A boundary: `persisted_existing_governed_knowledge_exact_revision_repository_with_explicit_idempotent_lifecycle_transition_records_and_verified_gate_8_candidate_lineage`.

Accepted exact-surface report SHA-256: `8ed1fdd1c8e857d1f7422eb7d292b9ecee954d6fb995a30d588f0e0214d4e645`.

This review selects contract surfaces only. It does not select implementation files, a storage backend, a schema, migrations, a CLI, packaging, or Gate 10 behavior.

## 2. Selected runtime contract

Selected runtime contract: `caller_supplied_governed_knowledge_verified_gate_8_lineage_append_only_exact_revision_repository_and_explicit_structural_lifecycle_transition_runtime_contract`.

Repository protocol: `GovernedKnowledgeRepository`.

The repository accepts only an already-existing `GovernedKnowledge` and caller-supplied, verifiable lineage to one exact Gate 8 `KnowledgeCandidate`. It never constructs, governs, accepts, promotes, interprets, or infers knowledge.

A lifecycle transition means an append-only change from one exact persisted structural lifecycle interpretation result to another. It is not a semantic state machine and does not invent lifecycle values.

## 3. Existing frozen dependencies

- `GovernedKnowledge` with contract version `governed-knowledge-v1`;
- `KnowledgeCandidate` and its deterministic review snapshot digest;
- `PersistedEvidenceKnowledgeConstructionResult`;
- `PersistedEvidenceKnowledgeCompatibilityRecord`;
- `GovernedKnowledgeConstructionResult`;
- `GovernedKnowledgeLifecycleAssertionInterpretationResult`;
- existing lifecycle result statuses `empty_assertion_collection`, `uniform_assertion_value`, and `contradictory_assertion_values`;
- existing deterministic identity functions for governed knowledge, knowledge candidates, lifecycle premises, lifecycle assertions, and lifecycle interpretation results;
- Gate 7 revision, audit, exact replay, and repository protocol patterns as precedent only.

The Gate 7 repository types are not inherited or reused as Gate 9 storage objects. Gate 9 owns a separate aggregate and separate contract versions.

## 4. Contract versions

- initial write request: `knowledge_repository_initial_write_request_contract_v1`
- lifecycle transition request: `knowledge_repository_lifecycle_transition_request_contract_v1`
- lineage record: `knowledge_repository_lineage_record_contract_v1`
- repository revision: `knowledge_repository_revision_contract_v1`
- lifecycle transition record: `knowledge_repository_lifecycle_transition_record_contract_v1`
- audit record: `knowledge_repository_audit_record_contract_v1`
- write result: `knowledge_repository_write_result_contract_v1`
- lookup result: `knowledge_repository_lookup_result_contract_v1`
- history result: `knowledge_repository_history_result_contract_v1`
- issue: `knowledge_repository_issue_contract_v1`

## 5. Policy and identity constants

- repository policy: `rcis-governed-knowledge-repository` / `1.0.0`
- lifecycle transition policy: `rcis-governed-knowledge-lifecycle-transition` / `1.0.0`
- digest algorithm: `sha256`
- lineage ID prefix: `gkrl1_`
- revision ID prefix: `gkr1_`
- transition ID prefix: `gkrt1_`
- audit ID prefix: `gkra1_`
- initial audit action: `persist_initial_governed_knowledge`
- transition audit action: `append_explicit_lifecycle_transition`

## 6. Canonicalization contracts

- payload canonicalization: `knowledge_repository_payload_json_v1`
- lineage identity canonicalization: `knowledge_repository_lineage_identity_json_v1`
- revision identity canonicalization: `knowledge_repository_revision_identity_json_v1`
- lifecycle transition identity canonicalization: `knowledge_repository_lifecycle_transition_identity_json_v1`
- audit identity canonicalization: `knowledge_repository_audit_identity_json_v1`

All canonical bytes are compact UTF-8 JSON with lexically sorted keys, no BOM, no trailing newline, no NaN, explicit UTC timestamps, and deterministic ordering of unique string collections.

Full payload digests include the complete frozen dataclass payload, including diagnostics. Existing domain identity functions continue to verify the embedded domain identities independently.

## 7. Exact data shapes

### KnowledgeRepositoryInitialWriteRequest

Field count: `9`.

- `contract_version`
- `governed_knowledge`
- `persisted_evidence_knowledge_construction_result`
- `governed_knowledge_construction_result`
- `lifecycle_interpretation_result`
- `actor_id`
- `recorded_at_utc`
- `repository_policy_id`
- `repository_policy_version`

### KnowledgeRepositoryLifecycleTransitionRequest

Field count: `10`.

- `contract_version`
- `governed_knowledge_id`
- `expected_prior_revision_id`
- `expected_prior_revision_number`
- `next_lifecycle_interpretation_result`
- `transition_reason_codes`
- `actor_id`
- `recorded_at_utc`
- `transition_policy_id`
- `transition_policy_version`

### KnowledgeRepositoryLineageRecord

Field count: `21`.

- `contract_version`
- `lineage_record_id`
- `governed_knowledge_id`
- `governed_knowledge_contract_version`
- `knowledge_candidate_id`
- `knowledge_candidate_contract_version`
- `knowledge_candidate_snapshot_digest`
- `persisted_evidence_knowledge_compatibility_record_id`
- `evidence_repository_revision_id`
- `evidence_repository_audit_id`
- `source_id`
- `source_revision_number`
- `traceable_evidence_id`
- `accepted_evidence_id`
- `acceptance_record_ids`
- `construction_rule_id`
- `construction_rule_version`
- `governed_knowledge_construction_policy_id`
- `governed_knowledge_construction_policy_version`
- `lineage_policy_id`
- `lineage_policy_version`

### KnowledgeRepositoryRevision

Field count: `14`.

- `contract_version`
- `revision_id`
- `governed_knowledge_id`
- `revision_number`
- `previous_revision_id`
- `governed_knowledge_payload_digest`
- `lineage_record_id`
- `lifecycle_interpretation_result_id`
- `lifecycle_interpretation_result_contract_version`
- `lifecycle_interpretation_result_payload_digest`
- `transition_record_id`
- `actor_id`
- `recorded_at_utc`
- `audit_id`

### KnowledgeRepositoryLifecycleTransitionRecord

Field count: `12`.

- `contract_version`
- `transition_record_id`
- `governed_knowledge_id`
- `from_revision_id`
- `from_revision_number`
- `previous_lifecycle_interpretation_result_id`
- `next_lifecycle_interpretation_result_id`
- `transition_reason_codes`
- `actor_id`
- `recorded_at_utc`
- `transition_policy_id`
- `transition_policy_version`

### KnowledgeRepositoryAuditRecord

Field count: `10`.

- `contract_version`
- `audit_id`
- `action`
- `revision_id`
- `governed_knowledge_id`
- `revision_number`
- `lineage_record_id`
- `transition_record_id`
- `actor_id`
- `recorded_at_utc`

### KnowledgeRepositoryWriteResult

Field count: `10`.

- `contract_version`
- `status`
- `mutation_performed`
- `revision`
- `lineage_record`
- `transition_record`
- `audit_record`
- `governed_knowledge`
- `lifecycle_interpretation_result`
- `issue`

### KnowledgeRepositoryLookupResult

Field count: `9`.

- `contract_version`
- `status`
- `revision`
- `lineage_record`
- `transition_record`
- `audit_record`
- `governed_knowledge`
- `lifecycle_interpretation_result`
- `issue`

### KnowledgeRepositoryHistoryResult

Field count: `10`.

- `contract_version`
- `status`
- `governed_knowledge_id`
- `governed_knowledge`
- `lineage_record`
- `revisions`
- `lifecycle_interpretation_results`
- `transition_records`
- `audit_records`
- `issue`

### KnowledgeRepositoryIssue

Field count: `2`.

- `code`
- `message`

## 8. Repository protocol

`GovernedKnowledgeRepository` exposes exactly five methods:

- `persist_initial(self, request: KnowledgeRepositoryInitialWriteRequest) -> KnowledgeRepositoryWriteResult`
- `append_lifecycle_transition(self, request: KnowledgeRepositoryLifecycleTransitionRequest) -> KnowledgeRepositoryWriteResult`
- `get_by_revision_id(self, revision_id: str) -> KnowledgeRepositoryLookupResult`
- `get_by_governed_knowledge_revision(self, governed_knowledge_id: str, revision_number: int) -> KnowledgeRepositoryLookupResult`
- `list_governed_knowledge_history(self, governed_knowledge_id: str) -> KnowledgeRepositoryHistoryResult`

There is no `get_latest`, `get_current`, mutable current pointer, overwrite, delete, or destructive update method.

## 9. Initial persistence validation

Before any mutation, `persist_initial` must validate in deterministic order:

1. request type and request contract version;
2. repository policy ID and version;
3. frozen `GovernedKnowledge` type, contract, and recomputed identity;
4. `PersistedEvidenceKnowledgeConstructionResult` type, contract, constructed status, non-null compatibility record, non-null constructed `KnowledgeConstructionResult`, and no issue;
5. exact identity of the Gate 8 `KnowledgeCandidate`;
6. exact match between the Gate 8 candidate ID, contract version, and review snapshot digest and the corresponding fields embedded in `GovernedKnowledge`;
7. `GovernedKnowledgeConstructionResult` type, constructed status, and exact governed-knowledge payload match;
8. structural lifecycle interpretation result type, contract, allowed existing result status, exact identity, and governed-knowledge subject linkage;
9. deterministic payload digests and lineage record identity;
10. deterministic initial revision and audit identities.

The initial revision number is exactly `1`, `previous_revision_id` is `None`, and `transition_record_id` is `None`.

## 10. Lifecycle transition validation

`append_lifecycle_transition` requires one exact expected prior revision ID and revision number supplied by the caller.

The repository verifies the exact prior revision, subject identity, next structural interpretation result identity, subject linkage, transition policy, and deterministic transition/revision/audit identities.

A newly appended transition produces exactly one transition record, one immutable revision numbered prior plus one, and one audit record.

The repository does not call `interpret_governed_knowledge_lifecycle_assertion_premise_structurally`. The caller supplies an already-existing result. The repository verifies it only.

A new transition whose next lifecycle interpretation result is identical to the prior result is rejected as `lifecycle_transition_no_change`.

## 11. Non-cyclic identity derivation

Identity derivation order is fixed:

1. canonical full payload digests;
2. lineage record ID;
3. lifecycle transition record ID when applicable;
4. repository revision ID;
5. audit ID.

The transition identity projection does not contain the resulting revision ID. The revision identity projection contains the transition record ID but excludes `audit_id`. The audit identity projection contains the completed revision ID. This prevents cyclic identities.

## 12. Write statuses

- `persisted_initial`
- `appended_lifecycle_transition`
- `unchanged_exact_replay`
- `rejected`

`mutation_performed` is `True` only for `persisted_initial` and `appended_lifecycle_transition`. It is `False` for `unchanged_exact_replay` and `rejected`.

## 13. Lookup and history statuses

- `found`
- `not_found`
- `rejected`

Exact revision lookup never selects the latest revision implicitly. History results are ordered by ascending revision number and contain aligned immutable revisions, lifecycle results, transition records, and audit records.

## 14. Existing lifecycle result statuses

- `empty_assertion_collection`
- `uniform_assertion_value`
- `contradictory_assertion_values`

All three existing structural statuses are persistable. The repository does not reinterpret them as active, inactive, approved, deprecated, or any other new semantic lifecycle state.

## 15. Deterministic issue precedence

Issue code count: `34`.

1. `invalid_request`
2. `unsupported_contract_version`
3. `unsupported_repository_policy`
4. `unsupported_transition_policy`
5. `invalid_governed_knowledge`
6. `governed_knowledge_identity_mismatch`
7. `invalid_persisted_evidence_knowledge_construction_result`
8. `persisted_evidence_knowledge_construction_rejected`
9. `missing_persisted_evidence_knowledge_compatibility_record`
10. `invalid_gate_8_knowledge_candidate`
11. `gate_8_knowledge_candidate_identity_mismatch`
12. `governed_knowledge_candidate_lineage_mismatch`
13. `invalid_governed_knowledge_construction_result`
14. `governed_knowledge_construction_rejected`
15. `governed_knowledge_construction_result_mismatch`
16. `invalid_lifecycle_interpretation_result`
17. `lifecycle_interpretation_subject_mismatch`
18. `lifecycle_interpretation_identity_mismatch`
19. `lifecycle_transition_no_change`
20. `initial_revision_already_bound_to_different_content`
21. `expected_prior_revision_not_found`
22. `expected_prior_revision_identity_mismatch`
23. `expected_prior_revision_number_mismatch`
24. `stale_expected_prior_revision`
25. `lifecycle_transition_conflict`
26. `lineage_record_id_mismatch`
27. `revision_id_mismatch`
28. `transition_record_id_mismatch`
29. `audit_id_mismatch`
30. `unsupported_schema`
31. `repository_busy`
32. `repository_corrupt`
33. `repository_unavailable`
34. `internal_contract_violation`

The first applicable issue in this exact order is returned. Rejected results contain no partial mutation.

## 16. Idempotency and concurrency

Initial exact replay returns the original revision, lineage record, audit record, governed knowledge, and lifecycle result with `unchanged_exact_replay` and no mutation.

A repeated lifecycle request against the same prior revision returns `unchanged_exact_replay` only when the already-existing child transition, child revision, audit record, and all canonical payloads match exactly.

A competing non-identical child for the same prior revision is rejected deterministically. A request whose expected prior revision has already been advanced is rejected as stale after the exact-replay check.

## 17. Mutation limits

- at most one initial revision and one initial audit record per successful initial request;
- at most one transition record, one revision, and one audit record per successful lifecycle request;
- no mutation of caller-supplied frozen objects;
- no partial writes;
- no hidden retry that changes identity inputs;
- no cross-subject transaction.

## 18. Explicit exclusions

- calling `construct_knowledge_from_persisted_evidence`;
- calling `construct_governed_knowledge`;
- calling acceptance, governance, authority, conflict, promotion, assertion, or interpretation entrypoints;
- creating or modifying `KnowledgeCandidate` or `GovernedKnowledge`;
- automatic source-authority inheritance;
- semantic lifecycle state machines;
- implicit latest or current revision selection;
- mutable pointers, overwrite, delete, compaction, or history rewriting;
- search, ranking, graph traversal, aggregation, or bulk orchestration;
- selecting SQLite or any other backend in this review;
- Gate 10 Prompt Candidate behavior;
- Gate 11 CLI, packaging, or release behavior.

## 19. Runtime contract decision

Gate 9 minimum closure boundary selected: `True`.

Gate 9 minimum closure boundary committed: `True`.

Gate 9 runtime contract selected: `True`.

Gate 9 runtime contract committed: `False`.

Gate 9 implementation boundary selected: `False`.

Gate 9 implementation authorized: `False`.

Gate 9 implementation started: `False`.

Gate 9 closed: `False`.

Gate 10 invoked: `False`.

## 20. Next safe operation

`PR-054B_POST_COMMIT - Gate 9 Runtime Contract Review Post-Commit Verification`

After that verification is accepted, the next architecture operation is PR-054C - Knowledge Repository and Lifecycle Implementation Boundary Review.
