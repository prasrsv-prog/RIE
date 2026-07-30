# PR-073B - Gate 14 Explicit Image Evidence Eligibility and Provenance Relationship Contract

Status: SELECTED GAP CONTRACT MATERIALIZATION
Gate: 14 - Multimodal Evidence and Knowledge
Selected gap: GATE_14_EXPLICIT_IMAGE_EVIDENCE_ELIGIBILITY_AND_PROVENANCE_RELATIONSHIP_CONTRACT
Implementation status: NOT IMPLEMENTED
Runtime authorization: NOT GRANTED

## 1. Purpose

Define the smallest versioned and immutable Gate 14 contract that links one
Official Image Source revision and one accepted Gate 13 factual image extraction
artifact to one Image Evidence Candidate while preserving authority, provenance,
rights, lifecycle, eligibility, conflict traceability, and the prohibition on
automatic promotion.

This contract is required before any multimodal Knowledge construction,
Evidence repository expansion, asset-library runtime, dashboard workflow,
semantic interpretation, OCR, embedding, inference, model execution, or
generator integration.

## 2. Authority and dependency boundary

This contract is bounded by:

1. the accepted Gate 13 / Phase 72 final checkpoint;
2. PR-073A Correction 1 Gate 14 readiness and single-gap selection;
3. the accepted Gate 6-10 Evidence and Knowledge governance boundaries;
4. the accepted Gate 12 Official Image Source domain;
5. the accepted Gate 13 factual structural image extraction boundary; and
6. Roadmap Alignment v5.

The following separations remain mandatory:

- Source Material != Evidence
- Extraction Result != Evidence
- Image Evidence Candidate != Accepted Evidence
- Evidence != Knowledge
- Knowledge != business decision
- Generated Output != Official Source
- Generated Output != Accepted Asset
- Generated Output != Approved Creative Asset

No automatic promotion is authorized between these layers.

## 3. Contract identity

Contract name:

`gate_14_explicit_image_evidence_eligibility_and_provenance_relationship`

Contract version:

`1.0`

Contract properties:

- versioned;
- immutable after construction;
- source-bound;
- artifact-bound;
- explicit about eligibility;
- explicit about provenance;
- explicit about relationship origin;
- fail-closed;
- non-semantic; and
- independent of model or generator execution.

This document defines the contract boundary only. It does not implement a
domain class, repository, service, CLI, parser, workflow, or persistence
adapter.

## 4. Required input identities

One contract evaluation requires exactly one Official Image Source revision and
exactly one accepted Gate 13 image extraction artifact.

### 4.1 Official Image Source revision

The input must carry exact values for:

- official image source identifier;
- official image source revision;
- source checksum;
- source authority;
- rights state;
- lifecycle state; and
- eligibility-relevant source status.

The source revision must be the same revision bound to the extraction artifact.
A later or earlier revision is not interchangeable.

### 4.2 Accepted Gate 13 image extraction artifact

The input must carry exact values for:

- image extraction artifact identifier;
- artifact contract version;
- artifact checksum;
- bound official image source identifier;
- bound official image source revision;
- bound source checksum; and
- the factual structural fields accepted by Gate 13.

Only a canonical artifact that passed the accepted Gate 13 boundary is eligible
for evaluation.

## 5. Image Evidence Candidate output boundary

A successful eligibility evaluation may construct one Image Evidence Candidate.

The candidate must record:

- contract name and version;
- exact source identity and revision;
- exact source checksum;
- exact artifact identity and version;
- exact artifact checksum;
- exact source-to-artifact binding;
- source authority;
- rights state;
- lifecycle state;
- factual structural image fields admitted from Gate 13;
- relationship declaration;
- relationship provenance;
- eligibility decision;
- eligibility decision reasons; and
- creation metadata required by the existing governed Evidence boundary.

Construction of a candidate does not mean acceptance as Evidence.

The output remains an Image Evidence Candidate until a separately authorized
Evidence acceptance boundary records an explicit acceptance decision.

## 6. Eligible factual field boundary

Only factual structural fields already accepted by Gate 13 may be carried into
the candidate.

The contract must not derive or add:

- recognized text;
- object labels;
- people or identity labels;
- scene meaning;
- inferred intent;
- aesthetic judgment;
- safety or quality judgment;
- similarity scores;
- embeddings;
- semantic categories;
- ontology membership;
- generated descriptions; or
- any model-produced assertion.

Absence of a semantic field is not an error. Semantic interpretation is outside
this contract.

## 7. Explicit relationship declaration

Text Evidence and Image Evidence remain distinct records.

A relationship may be recorded only when it is explicit and has one of these
origins:

1. `SOURCE_BACKED`
   - the relationship is directly supported by an authoritative source record;
   - the supporting source identity and revision must be recorded; or

2. `OPERATOR_DECLARED`
   - an authorized operator explicitly declares the relationship;
   - operator identity, declaration time, and declaration basis must be
     recorded.

The relationship declaration must include:

- relationship type;
- origin;
- subject Evidence identity;
- object Evidence identity;
- provenance reference;
- authority reference when source-backed;
- operator reference when operator-declared;
- lifecycle state; and
- traceable creation metadata.

No relationship may be inferred automatically from filename, location,
proximity, visual similarity, extracted dimensions, metadata resemblance,
shared folder, shared batch, or model output.

## 8. Eligibility preconditions

Eligibility is `ELIGIBLE` only when every required precondition is proven:

1. the Official Image Source identity exists and is exact;
2. the source revision exists and is exact;
3. the source checksum matches the bound checksum;
4. source authority is valid for the requested Evidence use;
5. rights state explicitly permits the requested governed use;
6. lifecycle state is eligible;
7. the Gate 13 artifact identity exists and is exact;
8. the artifact version is supported by this contract;
9. the artifact checksum is exact;
10. artifact source identifier matches the Official Image Source;
11. artifact source revision matches the Official Image Source revision;
12. artifact bound source checksum matches the Official Image Source checksum;
13. artifact status proves acceptance under the Gate 13 boundary;
14. every admitted field is within the factual Gate 13 field boundary;
15. relationship origin is explicit when a relationship is present; and
16. all required provenance is complete.

Missing, unknown, ambiguous, stale, conflicting, unsupported, or mismatched
values must not be treated as eligible.

## 9. Fail-closed decisions

The evaluation result is one of:

- `ELIGIBLE`;
- `INELIGIBLE`; or
- `SAFE_STOP`.

`ELIGIBLE` requires every precondition to pass.

`INELIGIBLE` is used when complete inputs prove that the source or artifact is
not eligible.

`SAFE_STOP` is used when required identity, authority, rights, lifecycle,
checksum, binding, provenance, or relationship facts are missing, ambiguous,
unsupported, malformed, or internally inconsistent.

A safe-stop must preserve the exact failure reasons. It must not repair,
substitute, infer, normalize away, or silently ignore a failed precondition.

## 10. Conflict traceability

Image Evidence and Text Evidence may disagree without either record being
deleted, overwritten, merged, or automatically preferred.

A conflict record must preserve:

- both Evidence identities;
- both provenance chains;
- both authority references;
- the exact conflicting fields or assertions;
- the conflict detection origin;
- lifecycle state;
- operator review state; and
- any later explicit authority decision.

This contract does not resolve conflicts. It only requires that conflicts remain
traceable and that no automatic resolution or authority override occurs.

## 11. Knowledge boundary

This contract does not construct Knowledge.

Multimodal Knowledge remains dependent on:

- governed eligible Evidence;
- explicit provenance;
- explicit authority;
- conflict traceability;
- lifecycle eligibility; and
- a separately authorized Knowledge construction boundary.

An Image Evidence Candidate, an accepted Image Evidence record, or an explicit
text-image relationship must not be promoted automatically to Knowledge.

## 12. Determinism and immutability requirements

For identical canonical inputs and the same contract version, evaluation must
produce the same eligibility decision, reason ordering, and candidate content.

Identity derivation and canonical serialization algorithms are deferred to a
separate implementation boundary, but that implementation must be deterministic
and must not use timestamps, random values, filesystem order, network results,
or model output as identity material.

After construction, the candidate content must be immutable. A changed source
revision, artifact version, checksum, authority, rights state, lifecycle state,
relationship, or provenance requires a new evaluation and a distinct candidate.

## 13. Definition of Done

This selected gap is complete only when all ten criteria are independently
proven:

1. One versioned immutable contract links one Official Image Source revision
   and one accepted image extraction artifact to one Image Evidence Candidate.
2. Exact source identifier, revision, checksum, authority, rights, and lifecycle
   state are required.
3. Exact artifact identifier, version, checksum, and source binding are
   required.
4. Identity, eligibility, rights, lifecycle, or binding mismatch fails closed.
5. Only factual structural image fields accepted by Gate 13 are allowed.
6. Relationship type and provenance are explicitly source-backed or
   operator-declared.
7. Text Evidence and Image Evidence remain distinct and use explicit
   relationships.
8. OCR, semantic interpretation, embeddings, inference, and model execution are
   prohibited.
9. Automatic Evidence-to-Knowledge promotion and automatic conflict resolution
   are prohibited.
10. Synthetic fail-closed acceptance cases are defined without real-asset
    execution.

## 14. Required synthetic acceptance cases

A later implementation boundary must prove at least:

### Passing cases

- exact eligible source and exact accepted artifact;
- exact source-backed relationship with complete provenance;
- exact operator-declared relationship with complete operator provenance; and
- deterministic repeated construction from identical canonical inputs.

### Failing or safe-stop cases

- source identifier mismatch;
- source revision mismatch;
- source checksum mismatch;
- artifact checksum mismatch;
- artifact version unsupported;
- artifact not accepted under Gate 13;
- invalid authority;
- rights not eligible;
- lifecycle not eligible;
- missing provenance;
- unknown relationship origin;
- semantic field supplied;
- OCR-derived field supplied;
- model-derived field supplied;
- automatic relationship inference attempted;
- automatic Evidence-to-Knowledge promotion attempted;
- automatic conflict resolution attempted; and
- real-asset execution attempted.

All acceptance assets must be synthetic.

## 15. Explicit out-of-scope boundary

This contract does not authorize:

- Evidence repository runtime or file persistence;
- multimodal Knowledge construction implementation;
- Master Asset Library work;
- registry scan or batch ingestion;
- dashboard, roles, approval, or UI work;
- OCR or text recognition;
- semantic image interpretation;
- embeddings or vector databases;
- ontology or knowledge graph work;
- automated inference or generalized model reasoning;
- local, cloud, or hybrid generator connectors;
- model orchestration;
- image file opening or pixel decoding;
- real-asset execution;
- production deployment or release;
- Gate 15, Gate 16, Gate 17, or Gate 18 implementation; or
- automatic promotion between Source, Extraction, Evidence, Knowledge, Asset,
  approval, and business-decision layers.

## 16. Authorized continuation after this contract

Materialization of this document authorizes no runtime implementation by itself.

After this document is independently verified and manually committed and
published on the controlled Phase 73 branch, the only eligible continuation is
a separate read-only implementation-boundary review for this exact selected
contract.

That later review must select the smallest implementation surface, exact paths,
synthetic tests, fail-closed cases, and no-expansion boundary before any Python
or test materialization is authorized.
