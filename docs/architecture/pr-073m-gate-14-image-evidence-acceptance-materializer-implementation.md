# PR-073M Gate 14 Image Evidence Acceptance Materializer Implementation

Version: 1.0
Status: Selected-boundary implementation
Gate: 14
Phase: 73
Selected boundary: GATE_14_MINIMUM_PURE_IMAGE_EVIDENCE_ACCEPTANCE_MATERIALIZER

## 1. Purpose

This implementation materializes one exact eligible
`ImageEvidenceEligibilityResult` into the existing RCIS accepted Evidence
contracts without modifying any existing contract.

The selected boundary creates exactly:

1. one implementation document;
2. one pure application module; and
3. one targeted synthetic test module.

## 2. Governing contracts

The implementation is governed by:

- the published Gate 14 image Evidence eligibility contract;
- the published `ImageEvidenceCandidate` implementation;
- the published Gate 14 image Evidence acceptance materialization and
  relationship identity contract;
- the existing `AcceptedEvidence` contract;
- the existing `AcceptanceRecord` contract;
- the existing EV1 Evidence identity policy; and
- the existing AR1 Acceptance identity policy.

No existing file is modified.

## 3. Exact public surface

The new application module exposes exactly the selected public surface:

- `ImageEvidenceMaterializationDecision`;
- `AcceptedImageEvidenceRelationship`;
- `ImageEvidenceMaterializationRequest`;
- `ImageEvidenceMaterializationResult`; and
- `materialize_image_evidence_candidate`.

The only decisions are:

- `MATERIALIZED`;
- `REJECTED`; and
- `SAFE_STOP`.

## 4. Exact request boundary

The request contains:

- one exact `ImageEvidenceEligibilityResult`;
- one explicit accepted-Evidence contract version;
- one explicit candidate snapshot digest;
- exact existing source, producer, payload, provenance, and diagnostic bridge
  objects;
- explicit eligibility policy identity, evaluation actor, and evaluation time;
- explicit acceptance actor, reason, review identity, and acceptance time;
- explicit acceptance policy identity and version;
- explicit materializer identity and version;
- exact existing Acceptance diagnostics; and
- explicit false-by-default prohibited-attempt declarations.

All timestamps are caller supplied and timezone aware. The module has no clock
access.

## 5. Candidate and relationship preconditions

Materialization requires:

- exact `ELIGIBLE` result and exact candidate;
- the published candidate contract name and version;
- complete source and artifact identities;
- lower-case SHA-256 source and artifact checksums;
- canonical sorted factual structural fields;
- one exact relationship;
- relationship origin `SOURCE_BACKED` or `OPERATOR_DECLARED`;
- an existing EV1 relationship subject;
- relationship object `SELF_IMAGE_EVIDENCE` or the exact calculated EV1;
- complete relationship provenance;
- source-backed authority reference or complete operator declaration; and
- no real-asset relationship.

Incomplete or unsupported governed input is rejected. Prohibited execution
attempts safe-stop.

## 6. Exact bridge mapping

The request supplies exact existing bridge contracts.

The source snapshot must map:

- source identity;
- source revision through the controlled source path;
- source checksum;
- source authority;
- lifecycle state; and
- eligible state.

The producer snapshot binds the published image Evidence candidate contract.

The factual payload contains only canonical factual structural fields.

The locator contains the source revision, artifact identity and version,
artifact checksum, relationship type and origin, subject identity, the fixed
`SELF_IMAGE_EVIDENCE` object literal, relationship provenance, and explicit
authority or operator declaration values.

The provenance lineage preserves the same source, artifact, relationship,
rights, and mapping-contract bindings.

## 7. Existing EV1 identity

The module constructs one provisional exact `AcceptedEvidence` object and calls:

- `identity_input_from_accepted_evidence`; and
- `calculate_evidence_identity`.

It does not implement a parallel digest or identity algorithm.

The locator supplied to the existing EV1 identity surface contains the fixed
`SELF_IMAGE_EVIDENCE` literal. This removes circular identity input while
binding the relationship object side into the existing canonical identity
preimage.

The final EV1 is copied exactly to:

- `AcceptedEvidence.evidence_id`;
- `AcceptanceRecord.evidence_id`; and
- `AcceptedImageEvidenceRelationship.object_evidence_id`.

A caller-supplied EV1 relationship object must equal the calculated EV1.

## 8. Existing AR1 identity

The module constructs one provisional exact `AcceptanceRecord` and calls:

- `acceptance_identity_input_from_record`; and
- `calculate_acceptance_identity`.

It does not implement a parallel Acceptance digest or identity algorithm.

The calculated AR1 is copied exactly to:

- `AcceptanceRecord.acceptance_record_id`; and
- `AcceptedEvidence.materialization_record.acceptance_record_id`.

EV1 and AR1 are recomputed after final object construction. Any mismatch
safe-stops with no accepted output.

## 9. Result invariants

`MATERIALIZED` returns all three exact accepted outputs and no reason codes.

`REJECTED` and `SAFE_STOP` return:

- no `AcceptedEvidence`;
- no `AcceptanceRecord`;
- no accepted relationship; and
- deterministic reason codes and diagnostics.

Partial accepted output is impossible at the public result boundary.

All new request, result, and relationship contracts are frozen and slotted.

## 10. Purity boundary

The implementation performs no:

- filesystem access;
- network access;
- environment or process-state access;
- clock access;
- random access;
- image opening;
- pixel decoding;
- OCR;
- embedding;
- semantic inference;
- model or generator execution;
- repository or database access;
- persistence;
- Knowledge construction;
- conflict resolution; or
- Evidence-to-Knowledge promotion.

## 11. Exact targeted test matrix

The targeted synthetic test module contains exactly 28 tests covering:

1. materialized happy path;
2. deterministic replay;
3. exact existing output types and EV1/AR1 prefixes;
4. self-object resolution and subject preservation;
5. source-backed provenance preservation;
6. operator-declared relationship materialization;
7. frozen result contract;
8. frozen request contract;
9. frozen accepted relationship contract;
10. invalid request rejection;
11. non-eligible rejection;
12. missing candidate rejection;
13. unsupported candidate contract rejection;
14. incomplete identity rejection;
15. non-canonical factual field rejection;
16. missing relationship rejection;
17. invalid subject and real-asset relationship rejection;
18. mismatched supplied object EV1 safe-stop;
19. missing source-backed authority rejection;
20. incomplete operator declaration rejection;
21. timezone-aware caller time enforcement;
22. unsupported policy or materializer rejection;
23. source bridge mismatch rejection;
24. payload bridge mismatch rejection;
25. provenance lineage mismatch rejection;
26. all prohibited-attempt safe-stops;
27. EV1 recomputation mismatch safe-stop; and
28. AR1 recomputation mismatch safe-stop.

Only `tests/application/test_image_evidence_materializer.py` is executed.

## 12. Protected surfaces

This implementation does not modify:

- `src/rie/application/image_evidence_candidate.py`;
- `src/rie/domain/accepted_evidence.py`;
- `src/rie/domain/acceptance_record.py`;
- `src/rie/domain/evidence_identity.py`;
- `src/rie/domain/acceptance_identity.py`;
- `src/rie/application/evidence_materializer.py`;
- `src/rie/application/knowledge_constructor.py`;
- package initializers; or
- any existing test.

## 13. No-expansion boundary

This implementation does not authorize:

- package re-exports;
- a repository or persistence layer;
- a database or registry;
- a CLI or batch workflow;
- UI or approval workflow;
- real image assets;
- image parsing or decoding;
- OCR or text recognition;
- semantic image interpretation;
- embeddings, vector search, ontology, or knowledge graph;
- model reasoning or local generator integration;
- automatic conflict resolution;
- automatic Evidence-to-Knowledge promotion;
- multimodal Knowledge construction;
- broader Gate 14 runtime;
- Gate 14 closure; or
- Gate 15, Gate 16, Gate 17, or Gate 18 implementation.

A later independent result review is required before stage, commit, or push.
