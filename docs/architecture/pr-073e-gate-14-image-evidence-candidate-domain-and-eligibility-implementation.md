# PR-073E - Gate 14 Image Evidence Candidate Domain and Eligibility Implementation

Status: IMPLEMENTATION MATERIALIZATION
Gate: 14 - Multimodal Evidence and Knowledge
Authorized source: PR-073D Correction 1
Selected surface: ONE_PURE_IMMUTABLE_IMAGE_EVIDENCE_CANDIDATE_EVALUATION_MODULE

## 1. Scope

This implementation materializes only the selected Gate 14 contract surface:

- one pure application module;
- one paired synthetic test module; and
- this implementation record.

No existing Evidence, Evidence identity, Accepted Evidence, Official Image
Source, Gate 13 extraction artifact, package initializer, repository, parser,
CLI, persistence, asset, dashboard, OCR, semantic, model, or generator path is
modified.

## 2. Materialized paths

- `src/rie/application/image_evidence_candidate.py`
- `tests/application/test_image_evidence_candidate.py`
- `docs/architecture/pr-073e-gate-14-image-evidence-candidate-domain-and-eligibility-implementation.md`

## 3. Domain surface

The implementation provides immutable enums and dataclasses for:

- `ImageEvidenceEligibilityDecision`
- `ImageEvidenceRelationshipOrigin`
- `ImageEvidenceRelationship`
- `ImageEvidenceCandidate`
- `ImageEvidenceEligibilityResult`

It also provides immutable source-revision and accepted-artifact binding inputs
required by the pure evaluator.

## 4. Evaluation boundary

`evaluate_image_evidence_candidate` accepts exactly one source revision binding,
one accepted Gate 13 artifact binding, and an optional explicit relationship.

The function performs no filesystem, network, clock, random, parser, image,
OCR, embedding, semantic, model, generator, repository, or persistence work.

It returns exactly one of:

- `ELIGIBLE` with one immutable Image Evidence Candidate;
- `INELIGIBLE` with explicit complete-input eligibility reasons; or
- `SAFE_STOP` with explicit mismatch, missing, unsupported, prohibited, or
  ambiguous-input reasons.

## 5. Preserved separations

The implementation preserves:

- Source Material != Evidence
- Extraction Result != Evidence
- Image Evidence Candidate != Accepted Evidence
- Evidence != Knowledge
- Knowledge != business decision

It does not perform automatic relationship inference, automatic
Evidence-to-Knowledge promotion, or automatic conflict resolution.

## 6. Factual-field boundary

Only factual structural fields explicitly supplied by an accepted Gate 13
artifact binding may enter the candidate. Semantic, OCR-derived, and
model-derived fields fail closed.

Factual fields are canonicalized deterministically as a sorted immutable tuple.
Duplicate field names, malformed fields, missing names, or non-text values fail
closed.

## 7. Relationship boundary

Relationships remain optional and explicit.

Supported origins are:

- `SOURCE_BACKED`, requiring provenance and authority references; and
- `OPERATOR_DECLARED`, requiring provenance, operator identity, and declaration
  basis.

Unknown origins and incomplete provenance fail closed. No relationship is
inferred from metadata, filenames, folders, proximity, or model output.

## 8. Synthetic acceptance matrix

The paired test module covers the 22 cases authorized by PR-073D Correction 1:

Passing:

1. exact eligible source and accepted artifact;
2. source-backed relationship with complete provenance;
3. operator-declared relationship with complete provenance; and
4. identical inputs produce identical results.

Fail-closed or ineligible:

1. source identifier mismatch;
2. source revision mismatch;
3. source checksum mismatch;
4. artifact checksum mismatch;
5. unsupported artifact version;
6. artifact not accepted under Gate 13;
7. invalid source authority;
8. rights not eligible;
9. lifecycle not eligible;
10. missing relationship provenance;
11. unknown relationship origin;
12. semantic field supplied;
13. OCR-derived field supplied;
14. model-derived field supplied;
15. automatic relationship inference attempted;
16. automatic Evidence-to-Knowledge promotion attempted;
17. automatic conflict resolution attempted; and
18. real-asset input attempted.

No real asset is opened, decoded, copied, parsed, or executed.

## 9. No-expansion boundary

This implementation does not authorize or implement:

- Evidence repository or persistence;
- Accepted Evidence materialization;
- multimodal Knowledge construction;
- conflict resolution runtime;
- Master Asset Library;
- dashboard, approval, or UI;
- OCR or text recognition;
- semantic image interpretation;
- embeddings, vector databases, ontologies, or knowledge graphs;
- model or generator integration;
- image opening or pixel decoding;
- real-asset execution;
- CLI, registry, batch, or production runtime; or
- Gate 15, Gate 16, Gate 17, or Gate 18 work.

## 10. Continuation

Materialization and targeted synthetic-test success do not authorize staging,
commit, push, broader Gate 14 runtime work, or downstream gates.

A separate implementation-result review is required before any publication or
continuation.
