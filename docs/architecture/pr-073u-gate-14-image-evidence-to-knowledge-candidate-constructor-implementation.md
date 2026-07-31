# PR-073U Gate 14 Image Evidence to Knowledge Candidate Constructor Implementation

Version: 1.0
Status: Exact selected-boundary implementation
Gate: 14
Phase: 73

## Purpose

This implementation materializes the minimum explicit, fail-closed,
non-automatic Image Evidence to Knowledge Candidate construction boundary
accepted by PR-073T.

It does not interpret images. It consumes only an already materialized
`ImageEvidenceMaterializationResult`, one caller-selected factual field, and
one caller-supplied statement that must be byte-for-byte equal to that field
value.

## Exact implementation paths

The implementation changes exactly five paths:

1. this implementation document;
2. `src/rie/domain/knowledge_candidate.py`;
3. `tests/domain/test_knowledge_candidate.py`;
4. `src/rie/application/image_knowledge_constructor.py`;
5. `tests/application/test_image_knowledge_constructor.py`.

No other path is modified.

## Narrow domain extension

The existing Knowledge Candidate domain receives exactly one additional
statement-type constant:

`IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE = "image_structural_fact"`

Statement-type validation accepts exactly:

- `verbatim_text_fact`;
- `image_structural_fact`.

The existing KC1 identity projection already includes `statement_type`.
No identity field, canonicalization rule, prefix, digest algorithm, or
parallel identity implementation is added.

## Application constructor

The application module exposes exactly:

- `ImageKnowledgeConstructionDecision`;
- `ImageKnowledgeRelationshipSupport`;
- `ImageKnowledgeConstructionRequest`;
- `ImageKnowledgeConstructionResult`;
- `construct_image_knowledge_candidate`.

The decisions are exactly:

- `CONSTRUCTED`;
- `REJECTED`;
- `SAFE_STOP`.

A successful result contains one existing `KnowledgeCandidate` and one
immutable image Knowledge relationship-support sidecar. Rejected and
safe-stopped results contain zero output.

## Caller-selected statement

The request names one factual field in the immutable
`image_structural_facts` payload.

The selected field must exist exactly once, contain one non-empty string, and
remain in canonical order with unique field names.

The caller-supplied statement must be byte-for-byte equal to the selected
value. No normalization, synthesis, translation, summarization,
classification, completion, OCR, semantic interpretation, inference, or
model execution is performed.

The exact rule is:

- ID: `rcis-accepted-image-structural-fact-selection`;
- version: `1.0.0`.

## Existing identity and support

The constructor uses existing:

- `KnowledgeEvidenceSupport`;
- `KnowledgeCandidateIdentityInput`;
- `compute_knowledge_candidate_id`;
- `identity_input_from_knowledge_candidate`;
- KC1 identity and canonicalization contracts.

The Knowledge Evidence support is populated from the exact accepted Evidence,
Acceptance Record, source snapshot, payload digest, and locator.

The relationship-support sidecar preserves exact:

- KC1 identity;
- EV1 identity;
- AR1 identity;
- relationship subject, object, type, and origin;
- provenance, authority, operator, and declaration fields;
- source identity and digest;
- payload digest;
- source lineage;
- Evidence materializer identity and version.

## Initial governance states

Every constructed candidate begins with existing exact initial states:

- authority `unassessed`;
- lifecycle `candidate`;
- review `pending_review`;
- conflict `not_assessed`;
- no conflict IDs;
- no diagnostics.

Construction does not approve Knowledge, assess authority, resolve conflict,
or persist Knowledge.

## Fail-closed boundary

The constructor rejects or safe-stops for invalid request types, prohibited
operation flags, non-materialized Evidence results, identity-link mismatch,
incomplete relationship provenance, unsupported payloads, unsupported rules,
naive timestamps, malformed factual mappings, missing fields, transformed
statements, domain construction failure, and KC1 recomputation mismatch.

No partial output is allowed.

## Protected surfaces

This implementation does not modify:

- `src/rie/application/knowledge_constructor.py`;
- `KnowledgeEvidenceSupport`;
- `src/rie/application/image_evidence_materializer.py`;
- Accepted Evidence or Acceptance Record contracts;
- Evidence, Acceptance, or Knowledge identity algorithms;
- package initializers;
- repositories, persistence, CLI, batch, UI, or asset runtime.

## Test boundary

Exactly two targeted modules are executed:

- `tests/domain/test_knowledge_candidate.py`;
- `tests/application/test_image_knowledge_constructor.py`.

The application module contains exactly 30 test functions.
The domain extension adds exactly 4 test functions.

The full test suite is not authorized.

## Out of scope

Image access, pixel decoding, real assets, OCR, embeddings, semantic search,
ontology, knowledge graphs, model reasoning, generator integration,
multimodal inference, automatic promotion, automatic conflict resolution,
Knowledge approval, Knowledge persistence, broader Gate 14 runtime, Gate 14
closure, and Gates 15-18 remain unauthorized.
