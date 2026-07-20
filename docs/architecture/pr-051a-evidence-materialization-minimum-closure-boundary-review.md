# PR-051A - Evidence Materialization Minimum Closure Boundary Review

## 1. Review identity

Gate: `Gate 6 - Evidence Materialization`

Phase: `Phase 51 - Evidence Materialization`

Required outcome: `Traceable factual Evidence`

Selected minimum boundary: `single_valid_extraction_artifact_explicitly_eligible_source_page_scoped_exact_traceable_evidence_collection_boundary`

Review type: architecture-only minimum closure boundary selection.

## 2. Authoritative Gate 6 requirement

Gate 6 converts one valid Gate 5 Extraction Artifact into exact, traceable Evidence only when one explicit OfficialSource evidence-eligibility snapshot proves that the source is eligible.

The required runtime outcome is an immutable, ordered EvidenceCollection whose Evidence items remain page-scoped and preserve exact extracted factual content, source identity, source checksum, extraction job identity, provenance, evidence eligibility, warnings, and extraction status.

## 3. Selected minimum closure boundary

The minimum Gate 6 closure boundary contains exactly:

1. one validated `extraction_artifact_contract_v1` value from Gate 5;
2. one explicit, successful OfficialSource evidence-eligibility snapshot that matches the artifact source identity and source checksum;
3. one deterministic materialization operation with no parser, filesystem discovery, network, current-clock, AI, repository, or persistence side effects;
4. one immutable, ordered EvidenceCollection result;
5. zero or more page-scoped Evidence items, each originating from exactly one artifact page extraction and never from an implicit cross-page combination;
6. explicit rejection with no partial Evidence when the artifact, eligibility snapshot, identity compatibility, provenance, or supported content contract is invalid.

## 4. Required factual preservation

Materialization must copy accepted factual values without summarization, inference, semantic correction, normalization, paraphrase, enrichment, or business interpretation.

Every materialized Evidence item must trace to:

- the artifact contract version;
- the artifact ID;
- the Gate 4 extraction job ID;
- the official source ID;
- the exact source checksum;
- one exact page index;
- the exact extracted content and content type;
- the exact extraction method and status;
- the carried warning sequence;
- explicit provenance and eligibility snapshots;
- one deterministic, versioned Evidence identity.

## 5. Eligibility rule

No Evidence may be created from an ineligible, review-required, mismatched, missing, or unsupported source snapshot.

Eligibility is an explicit input dependency. Gate 6 must not silently rerun or reconstruct OfficialSource registry, authority, lifecycle, or eligibility decisions.

## 6. Existing foundation classification

The committed Gate 5 Extraction Artifact runtime is the authoritative direct upstream.

Existing EvidenceCandidate, candidate snapshot, AcceptedEvidence, EvidenceIdentity, and evidence materializer implementations are compatibility candidates and advanced semantic foundations. Their existence does not automatically make any one shape the authoritative Gate 6 runtime contract.

Existing OfficialSource eligibility policy, gate, workflow, preflight, and registry assets are dependency candidates. PR-051B must select the exact eligibility snapshot input rather than inferring it from filenames, legacy DTOs, or current repository state.

## 7. Explicitly deferred runtime decisions

PR-051A does not yet decide:

- the exact Evidence and EvidenceCollection field orders and contract versions;
- the exact content-type vocabulary;
- the exact eligibility snapshot shape and compatibility rules;
- the deterministic Evidence identity payload, canonicalization, and version;
- the exact handling of empty page content, warnings, extraction status, and unsupported content;
- the exact issue codes, rejection messages, and result envelope;
- compatibility or replacement rules for existing Evidence-related classes.

These are required PR-051B runtime-contract decisions.

## 8. Excluded boundaries

The selected Gate 6 boundary excludes:

- Evidence repository save/load/list/export, duplicate detection, revision history, persistence, and audit storage, which belong to Gate 7;
- source discovery, source file reading, PDF parsing, extraction reruns, and Extraction Artifact publication;
- Knowledge construction, acceptance, lifecycle decisions, Prompt Candidate creation, CLI, API, packaging, migration, retries, fallbacks, and background processing;
- cross-page claim combination unless a later independently approved explicit rule authorizes it.

## 9. Gate 6 closure sequence

- PR-051A: minimum closure boundary review;
- PR-051B: runtime contract review;
- PR-051C: implementation boundary review;
- PR-051D: contract implementation and verification;
- PR-051E: Gate 6 closure review.

## 10. Decision

Decision:

`EVIDENCE_MATERIALIZATION_MINIMUM_CLOSURE_BOUNDARY_SELECTED`

Status after this review:

- Gate 6 active closure target: `True`;

- Gate 6 minimum closure boundary selected: `True`;

- Gate 6 runtime contract selected: `False`;

- Gate 6 implementation boundary selected: `False`;

- Gate 6 implementation authorized: `False`;

- Gate 6 implementation started: `False`;

- Gate 6 closed: `False`;

- Gate 7 invoked: `False`.

The next safe review is PR-051B - Evidence Materialization Runtime Contract Review.
