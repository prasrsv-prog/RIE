# PR-073I Gate 14 Image Evidence Acceptance Materialization and Relationship Identity Contract

Version: 1.0
Status: Selected-gap architecture contract
Gate: 14
Phase: 73

## 1. Purpose

This contract defines the smallest fail-closed boundary required to map one
eligible `ImageEvidenceCandidate` into the existing RCIS accepted Evidence
contracts.

The boundary produces exactly:

1. one existing `AcceptedEvidence` object;
2. one existing `AcceptanceRecord` object; and
3. one explicit accepted relationship representation whose image-object
   Evidence identity is the same `ev1_` identity carried by both outputs.

This contract does not construct, review, promote, persist, or interpret
Knowledge.

## 2. Governing authority

The governing authority for this contract is:

- the Gate 14 image Evidence eligibility and provenance relationship contract;
- the accepted `ImageEvidenceCandidate` implementation published by PR-073G;
- the existing `AcceptedEvidence` domain contract;
- the existing `AcceptanceRecord` domain contract;
- the existing Evidence identity policy using the `ev1_` prefix;
- the existing Acceptance identity policy using the `ar1_` prefix; and
- the existing generic Evidence materialization boundary only as a compatibility
  reference.

No existing domain or identity contract may be modified by the implementation
of this contract.

## 3. Mandatory separation rules

The following separations remain mandatory:

- Source Material is not Evidence.
- An image extraction artifact is not Evidence.
- An `ImageEvidenceCandidate` is not `AcceptedEvidence`.
- Eligibility is not acceptance.
- Acceptance is not Knowledge construction.
- Relationship declaration is not semantic inference.
- Conflict traceability is not conflict resolution.
- Accepted Evidence is not a business decision.

No automatic promotion is permitted between these states.

## 4. Exact input boundary

A conforming materialization request must contain exactly one set of the
following inputs:

1. one exact `ImageEvidenceEligibilityResult`;
2. the result decision must be `ELIGIBLE`;
3. the result must contain one exact `ImageEvidenceCandidate`;
4. one explicit acceptance actor;
5. one explicit acceptance reason;
6. one explicit timezone-aware acceptance timestamp supplied by the caller;
7. one explicit review-record identity;
8. one declared acceptance policy identity and version;
9. one declared materializer identity and version; and
10. no real image file, decoded pixel data, OCR output, embedding, model output,
    semantic field, or inferred relationship.

The materializer must not obtain the current time itself. It must not read the
filesystem, network, environment, process state, random source, or model.

## 5. Eligible candidate preconditions

Materialization may continue only when all of the following are true:

- the eligibility result is exact and internally consistent;
- the decision is exactly `ELIGIBLE`;
- the candidate contract name and version are supported;
- the official image source identity is complete;
- the source revision and source checksum are complete;
- the accepted Gate 13 artifact identity and checksum are complete;
- source authority is eligible;
- source rights state is eligible;
- source lifecycle state is eligible;
- factual structural fields contain no semantic, OCR-derived, or model-derived
  content;
- relationship origin is exactly `SOURCE_BACKED` or `OPERATOR_DECLARED`;
- relationship provenance is complete;
- automatic relationship inference was not attempted;
- automatic Evidence-to-Knowledge promotion was not attempted;
- automatic conflict resolution was not attempted; and
- real-asset execution was not attempted.

Any failed precondition must produce a fail-closed rejection with no accepted
output.

## 6. Existing AcceptedEvidence output

A successful result must construct one exact existing `AcceptedEvidence`
instance without modifying its contract.

The mapping must be lossless and deterministic:

- `candidate_reference` must bind the exact image candidate contract, source
  identity, source revision, source checksum, artifact identity, artifact
  version, and artifact checksum;
- `source_snapshot` must preserve the exact official image source identity,
  authority, rights state, lifecycle state, and source revision;
- `producer_snapshot` must identify the Gate 14 image Evidence candidate
  materializer and its contract version;
- `factual_payload` must contain only the accepted factual structural fields;
- `provenance` must preserve the source binding, artifact binding, relationship
  origin, relationship subject identity, relationship provenance reference,
  and the self-object binding rule defined below;
- `eligibility_result` must preserve the accepted `ELIGIBLE` decision and its
  exact reasons without reinterpretation;
- `materialization_record` must preserve the caller-supplied acceptance
  timestamp, materializer identity, materializer version, mapping contract name,
  and mapping contract version; and
- `diagnostics` may contain only deterministic informational or warning
  diagnostics allowed by the existing contract.

The implementation must not add semantic summaries, classifications, inferred
labels, generated descriptions, or resolved conflicts.

## 7. Deterministic Evidence identity

The accepted image Evidence identity must use the existing Evidence identity
policy and must have the existing `ev1_` form.

The identity must be calculated through the existing Evidence identity surface.
No parallel identity algorithm, alternate prefix, additional digest policy, or
new canonicalization contract is permitted.

The identity input must be derived only from the exact accepted output fields
required by the existing Evidence identity contract.

Identical accepted inputs must produce the identical `ev1_` identity.
Any mismatch between the calculated identity result and the constructed
`AcceptedEvidence.evidence_id` must fail closed.

## 8. Relationship self-object identity binding

The image Evidence is the object of the accepted relationship.

A candidate relationship may represent the image-object side only by one of the
following forms:

1. the fixed contract literal `SELF_IMAGE_EVIDENCE`; or
2. an already calculated `ev1_` identity that exactly matches the identity
   calculated during this materialization.

The canonical identity preimage must represent the self-object side with the
fixed literal `SELF_IMAGE_EVIDENCE`. This prevents circular identity input while
preserving the relationship origin, subject Evidence identity, and provenance
reference.

After the existing Evidence identity function calculates the final `ev1_`
identity:

- the accepted relationship object identity must be resolved to that exact
  `ev1_` value;
- the same value must be carried by `AcceptedEvidence.evidence_id`;
- the same value must be carried by `AcceptanceRecord.evidence_id`; and
- recomputation from identical inputs must return the same value.

A supplied object identity that is neither the fixed literal nor the exact
calculated identity must fail closed.

The relationship subject identity must remain unchanged. This contract does not
create, replace, reinterpret, or resolve the subject Evidence.

## 9. Existing AcceptanceRecord output

A successful result must construct one exact existing `AcceptanceRecord`
instance without modifying its contract.

The record must preserve:

- the same accepted image `evidence_id`;
- the caller-supplied acceptance actor;
- the caller-supplied acceptance reason;
- the caller-supplied review-record identity;
- the caller-supplied timezone-aware acceptance timestamp;
- the declared acceptance policy identity and version;
- the existing Evidence identity policy identity and version;
- the declared materializer identity and version; and
- only deterministic diagnostics allowed by the existing contract.

The Acceptance identity must be calculated through the existing Acceptance
identity surface and must have the existing `ar1_` form.

No parallel Acceptance identity algorithm, alternate prefix, or automatic
acceptance decision is permitted.

Any mismatch between the calculated Acceptance identity and
`AcceptanceRecord.acceptance_record_id` must fail closed.

## 10. Result contract

A future implementation may return only one immutable result containing:

- a materialization decision;
- one `AcceptedEvidence` or `None`;
- one `AcceptanceRecord` or `None`;
- one accepted relationship representation or `None`;
- deterministic reason codes; and
- deterministic diagnostics.

The only permitted decisions are:

- `MATERIALIZED`;
- `REJECTED`; and
- `SAFE_STOP`.

`MATERIALIZED` requires all three accepted outputs.
`REJECTED` and `SAFE_STOP` require all three accepted outputs to be absent.

## 11. Fail-closed conditions

The implementation must reject or safe-stop for at least:

1. non-`ELIGIBLE` input;
2. missing candidate;
3. unsupported candidate contract or version;
4. incomplete source or artifact identity;
5. invalid authority, rights, or lifecycle state;
6. semantic, OCR-derived, model-derived, or inferred fields;
7. unsupported relationship origin;
8. missing relationship provenance;
9. invalid relationship subject Evidence identity;
10. invalid relationship self-object representation;
11. calculated Evidence identity mismatch;
12. calculated Acceptance identity mismatch;
13. inconsistent accepted Evidence and AcceptanceRecord Evidence identities;
14. missing acceptance actor, reason, review identity, or timestamp;
15. non-timezone-aware acceptance timestamp;
16. unsupported policy or materializer identity;
17. automatic Knowledge construction or promotion attempt;
18. automatic conflict resolution attempt;
19. repository, database, persistence, CLI, batch, or UI side effect; and
20. image file opening, pixel decoding, or real-asset execution.

No partial accepted output is allowed.

## 12. Determinism and purity

The future implementation must be:

- pure for identical explicit inputs;
- deterministic;
- immutable at its public result boundary;
- free of filesystem access;
- free of network access;
- free of clock access;
- free of randomness;
- free of image decoding;
- free of OCR;
- free of embeddings;
- free of semantic inference;
- free of model or generator execution; and
- free of persistence side effects.

## 13. Existing contracts protected from modification

The following existing surfaces are protected:

- `src/rie/domain/accepted_evidence.py`
- `src/rie/domain/acceptance_record.py`
- `src/rie/domain/evidence_identity.py`
- `src/rie/domain/acceptance_identity.py`
- `src/rie/application/evidence_materializer.py`
- `src/rie/application/knowledge_constructor.py`
- `src/rie/application/image_evidence_candidate.py`

Their matching tests are also protected unless a later exact review explicitly
authorizes a compatibility change.

## 14. Explicitly out of scope

This contract does not authorize:

- an Evidence repository or persistence;
- a database;
- a registry;
- a CLI;
- batch ingestion;
- a dashboard or approval UI;
- image file opening or pixel decoding;
- OCR or text recognition;
- semantic image interpretation;
- embeddings, a vector database, ontology, or knowledge graph;
- model reasoning or generator integration;
- automatic conflict resolution;
- automatic Evidence-to-Knowledge promotion;
- modification of the text-bound Knowledge constructor;
- multimodal Knowledge construction;
- Gate 15, Gate 16, Gate 17, or Gate 18 implementation; or
- Gate 14 closure.

## 15. Future implementation boundary review

This architecture contract does not authorize runtime implementation.

A later read-only implementation boundary review must independently determine:

- the minimum new source path;
- the minimum new test path;
- whether one implementation document is required;
- the exact existing imports permitted;
- the exact materialization request and result types;
- the exact mapping to existing AcceptedEvidence component contracts;
- the exact use of the existing EV1 and AR1 identity functions;
- the exact self-object identity binding representation;
- the synthetic test matrix;
- the targeted test execution boundary; and
- the no-expansion proof.

Until that review is accepted, only this one architecture contract may be
materialized.
