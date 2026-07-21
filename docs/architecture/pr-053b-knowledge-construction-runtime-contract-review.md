# PR-053B - Knowledge Construction Runtime Contract Review

## 1. Review identity

This is an architecture-only and documentation-only Gate 8 runtime contract review.

Repository checkpoint: `27fc03ee15c769506d9d3e5955c2249c72e04447`

Branch: `phase-053-knowledge-construction`

Selected PR-053A boundary: `persisted_gate_7_evidence_revision_scoped_operational_knowledge_construction_orchestration_with_explicit_compatibility_mapping_and_existing_governance_lineage`

No production code, test code, package export, configuration, database, migration, CLI, API, or runtime behavior is changed.

No tests or project interpreter are run. No Git mutation is performed by this review.

## 2. Verified existing surface

The exact-surface extraction parsed 48 modules with zero parse errors, found all 10 existing Knowledge entrypoints, all 5 EvidenceCollectionRepository protocol methods, all 12 required compatibility surface classes, 12 request classes, and 19 result classes.

The existing KnowledgeCandidate constructor accepts `KnowledgeConstructionRequest`, whose exact fields are `accepted_evidence`, `acceptance_records`, `construction_rule_id`, and `construction_rule_version`.

The authoritative Gate 7 entry object is an already resolved `EvidenceRepositoryLookupResult`, which contains one exact revision, audit record, and EvidenceCollection when status is `found`.

No existing function directly accepts both surfaces. Automatic equivalence between TraceableEvidence and AcceptedEvidence remains forbidden.

## 3. Selected runtime contract

`resolved_gate_7_persisted_evidence_single_item_compatibility_bridge_to_existing_knowledge_candidate_construction_runtime_contract`

The runtime performs exactly one side-effect-free compatibility bridge and one existing KnowledgeCandidate construction call.

It does not query the repository, choose a latest revision, iterate all collection items, construct historical acceptance objects, or run downstream governance automatically.

## 4. Contract versions and fixed identifiers

- request: `persisted_evidence_knowledge_construction_request_contract_v1`;
- compatibility record: `persisted_evidence_knowledge_compatibility_record_contract_v1`;
- result: `persisted_evidence_knowledge_construction_result_contract_v1`;
- issue: `persisted_evidence_knowledge_construction_issue_contract_v1`;
- compatibility identity canonicalization: `persisted_evidence_knowledge_compatibility_identity_json_v1`;
- compatibility record ID prefix: `pekc1_`;
- compatibility policy ID: `rcis-persisted-evidence-knowledge-compatibility`;
- compatibility policy version: `1.0.0`;
- digest algorithm: lower-case `sha256`.

## 5. Request contract

`PersistedEvidenceKnowledgeConstructionRequest` has exactly six fields in this order:

1. `contract_version: str`;
2. `repository_lookup_result: EvidenceRepositoryLookupResult`;
3. `target_evidence_id: str`;
4. `knowledge_construction_request: KnowledgeConstructionRequest`;
5. `compatibility_policy_id: str`;
6. `compatibility_policy_version: str`.

The request contains a resolved lookup result. Repository IDs alone are not accepted, and the runtime performs no repository access.

The nested KnowledgeConstructionRequest is caller supplied and remains the sole authoritative source of AcceptedEvidence, AcceptanceRecord objects, construction rule ID, and construction rule version.

The runtime never fabricates accepted_by, reviewed_by, timestamps, acceptance reasons, producer metadata, locator values, or historical acceptance lineage.

## 6. Compatibility record contract

`PersistedEvidenceKnowledgeCompatibilityRecord` has exactly sixteen fields in this order:

1. `contract_version: str`;
2. `compatibility_record_id: str`;
3. `repository_revision_id: str`;
4. `source_id: str`;
5. `revision_number: int`;
6. `previous_revision_id: str | None`;
7. `collection_id: str`;
8. `collection_payload_digest: str`;
9. `repository_audit_id: str`;
10. `traceable_evidence_id: str`;
11. `accepted_evidence_id: str`;
12. `acceptance_record_ids: tuple[str, ...]`;
13. `construction_rule_id: str`;
14. `construction_rule_version: str`;
15. `compatibility_policy_id: str`;
16. `compatibility_policy_version: str`.

The identity projection contains the same fields except `compatibility_record_id`, in the listed order.

Acceptance record IDs are unique and stored in ascending lexical order. The record ID is `pekc1_` plus the lower-case SHA-256 digest of canonical UTF-8 JSON with no BOM, no insignificant whitespace, sorted object keys, and JSON number and string preservation.

## 7. Result and issue contracts

`PersistedEvidenceKnowledgeConstructionResult` has exactly six fields in this order:

1. `contract_version: str`;
2. `status: str`;
3. `mutation_performed: bool`;
4. `compatibility_record: PersistedEvidenceKnowledgeCompatibilityRecord | None`;
5. `knowledge_construction_result: KnowledgeConstructionResult | None`;
6. `issue: PersistedEvidenceKnowledgeConstructionIssue | None`.

Supported statuses are exactly `constructed` and `rejected`.

`mutation_performed` is always `False`.

`PersistedEvidenceKnowledgeConstructionIssue` has exactly two fields: `code` and `message`.

On `constructed`, compatibility_record and knowledge_construction_result are present, the nested construction decision is `constructed`, and issue is absent.

On `rejected`, issue is present. compatibility_record is absent unless compatibility completed before the existing constructor rejected. knowledge_construction_result is present only when the existing constructor was invoked.

## 8. Supported issue codes

The issue code set is exactly:

- `invalid_request`;
- `unsupported_contract_version`;
- `unsupported_compatibility_policy`;
- `invalid_repository_lookup_result`;
- `repository_lookup_not_found`;
- `repository_lookup_rejected`;
- `repository_linkage_mismatch`;
- `repository_identity_mismatch`;
- `collection_payload_digest_mismatch`;
- `target_evidence_not_found`;
- `target_evidence_identity_mismatch`;
- `ineligible_evidence`;
- `accepted_evidence_identity_mismatch`;
- `acceptance_record_identity_mismatch`;
- `evidence_compatibility_mismatch`;
- `knowledge_construction_rejected`;
- `internal_contract_violation`.

Issue messages are fixed one-to-one with issue codes and are not caller supplied.

## 9. Required validation and compatibility rules

The runtime must fail closed unless all of the following are true:

1. every outer and nested value has the exact supported type and passes its existing invariant checks;
2. the lookup status is `found`, issue is absent, and revision, audit record, and collection are all present;
3. revision, audit, collection, eligibility snapshot, and every TraceableEvidence identity are re-derived through existing Gate 6 and Gate 7 canonicalization functions;
4. revision source ID and collection ID match the collection, and audit revision ID, source ID, revision number, collection ID, and audit ID match the revision;
5. the collection repository payload digest exactly matches the revision payload digest;
6. exactly one collection item has `evidence_id == target_evidence_id`;
7. the collection eligibility snapshot permits evidence collection and declares the source eligible;
8. source ID, source path, source checksum or content digest anchor, authority status, lifecycle status, evidence eligibility, registry version, collection ID, content type, content value, and content digest agree wherever both Gate 7 and AcceptedEvidence expose the same semantic anchor;
9. AcceptedEvidence identity is re-derived through the frozen identity contract;
10. at least one AcceptanceRecord is present; every AcceptanceRecord identity is re-derived, every record references the same AcceptedEvidence ID, and all IDs are unique;
11. the AcceptedEvidence materialization acceptance record reference resolves to one supplied AcceptanceRecord;
12. the nested construction rule ID and version are passed unchanged to the existing constructor.

No equivalence is asserted for fields that do not share the same established semantics. Historical producer metadata, historical locator representation, reviewer identity, acceptance timestamps, and acceptance reasons remain independently validated historical inputs.

The compatibility record links both models without rewriting either model. Gate 7 warnings and provenance remain recoverable through traceable_evidence_id, collection_id, revision_id, and audit_id.

Source authority is provenance only. It does not automatically set KnowledgeCandidate authority, review, conflict, lifecycle, governance, promotion, or acceptance outcomes.

## 10. Failure precedence

When more than one failure is present, the runtime reports the first applicable category in this order:

1. invalid outer request, request contract version, or compatibility policy;
2. lookup type, status, and required object presence;
3. repository linkage, canonical identities, and collection payload digest;
4. target evidence selection and target evidence identity;
5. evidence eligibility;
6. AcceptedEvidence identity;
7. AcceptanceRecord identity and lineage;
8. cross-model semantic anchor compatibility;
9. compatibility record identity;
10. existing KnowledgeCandidate constructor result;
11. result wrapper invariant.

The runtime does not combine unrelated issue codes and does not hide the nested KnowledgeConstructionResult reason codes or diagnostics when that constructor was invoked.

## 11. Determinism and replay

The runtime uses no current clock, random source, filesystem lookup, database query, network call, retry loop, global mutable state, or environment-dependent normalization.

The same valid immutable request produces the same compatibility record ID, the same compatibility record, and the same nested KnowledgeConstructionResult.

Rejected requests are also deterministic for the same request value and supported implementation version.

There is no `unchanged_exact_replay` status because this contract performs no persistence or mutation.

## 12. Explicit downstream boundary

A successfully constructed KnowledgeCandidate may be supplied by the caller to the existing explicit review, governance, conflict, authority, promotion prerequisite, promotion decision, promotion execution, GovernedKnowledge construction, and GovernedKnowledge acceptance entrypoints.

This runtime contract does not construct those requests, choose their outcomes, invent their actors or timestamps, or invoke them automatically.

Cross-source support is formed only through caller-selected candidates and existing explicit conflict and promotion scope contracts. This runtime does not search for peer Evidence or Knowledge.

## 13. Scope exclusions

- no repository read or write operation;
- no latest-revision selection;
- no batch construction or iteration over all evidence items;
- no automatic conversion of TraceableEvidence into AcceptedEvidence;
- no automatic AcceptanceRecord creation;
- no mutation of frozen Gate 6, Gate 7, AcceptedEvidence, AcceptanceRecord, KnowledgeCandidate, or governance contracts;
- no automatic source-authority inheritance;
- no conflict winner selection or hidden contradiction resolution;
- no Knowledge persistence, current-state projection, supersession, lifecycle mutation, or Gate 9 behavior;
- no Prompt Candidate, AI inference, creative generation, CLI, API, or packaging behavior.

## 14. Decision

Selected runtime contract: `resolved_gate_7_persisted_evidence_single_item_compatibility_bridge_to_existing_knowledge_candidate_construction_runtime_contract`.

Gate 8 minimum closure boundary selected: `True`.

Gate 8 runtime contract selected: `True`.

Gate 8 compatibility mapping contract selected: `True`.

Gate 8 implementation boundary selected: `False`.

Gate 8 implementation authorized: `False`.

Gate 8 implementation started: `False`.

Gate 8 closed: `False`.

Gate 9 invoked: `False`.

## 15. Next safe review

`PR-053C - Knowledge Construction Implementation Boundary Review`

PR-053C must select the smallest isolated namespace, exact files, public symbols, and boundary tests required to implement this frozen contract. It must not implement code automatically.
