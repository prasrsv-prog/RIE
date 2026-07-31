# PR-073Q Gate 14 Image Evidence to Knowledge Candidate Construction and Support Contract

Version: 1.0
Status: Selected-gap architecture contract
Gate: 14
Phase: 73

## 1. Purpose

This contract defines the minimum explicit, fail-closed, non-automatic boundary
for constructing one Knowledge Candidate from one already materialized and
accepted image Evidence result.

The boundary starts only after image Evidence eligibility, Evidence identity,
Acceptance identity, and accepted relationship materialization have completed.
It does not open an image, decode pixels, recognize text, infer meaning, or
generate a statement from visual content.

This contract does not authorize runtime implementation.

## 2. Governing authority

The governing accepted baseline is:

- the Gate 14 image Evidence eligibility and provenance relationship contract;
- the Gate 14 image Evidence acceptance materialization and relationship
  identity contract;
- the published `ImageEvidenceMaterializationResult`;
- the existing `AcceptedEvidence` contract and `ev1_` identity;
- the existing `AcceptanceRecord` contract and `ar1_` identity;
- the existing `KnowledgeCandidate` contract and `kc1_` identity;
- the existing Knowledge construction governance states.

Where an existing runtime surface is narrower than this architecture contract,
the runtime must continue to fail closed until a later implementation boundary
review explicitly authorizes the minimum required change.

## 3. Mandatory separation rules

The following separations are mandatory:

1. Source Material is not Evidence.
2. Extraction Result is not Evidence.
3. Eligible Image Evidence Candidate is not Accepted Evidence.
4. Accepted Evidence is not Knowledge.
5. Knowledge Candidate is not accepted Knowledge.
6. Accepted image relationship provenance is not a business decision.
7. Caller selection of a factual field is not image interpretation.
8. Construction is never automatic promotion.

No success at an earlier boundary implies success at a later boundary.

## 4. Current accepted baseline

The accepted baseline already provides one materialized image Evidence result
containing:

- one exact `AcceptedEvidence` with an `ev1_` identity;
- one exact `AcceptanceRecord` with an `ar1_` identity;
- one exact accepted image Evidence relationship;
- an immutable `image_structural_facts` factual payload;
- preserved source authority, rights, lifecycle, artifact, and relationship
  provenance;
- a prohibition on automatic Evidence-to-Knowledge promotion.

The existing Knowledge constructor remains text-rule-bound, and the existing
Knowledge Candidate remains limited to its accepted statement surface. This
contract defines the next boundary but does not modify those existing contracts.

## 5. Exact input boundary

A construction request must contain exactly:

1. one `ImageEvidenceMaterializationResult`;
2. materialization decision `MATERIALIZED`;
3. one non-null `AcceptedEvidence`;
4. one non-null `AcceptanceRecord`;
5. one non-null accepted image Evidence relationship;
6. one explicit caller-supplied construction rule identifier and version;
7. one explicit caller-supplied factual field name;
8. one explicit caller-supplied statement text;
9. one explicit constructor identifier and version;
10. one caller-supplied timezone-aware construction timestamp;
11. explicit false values for every prohibited-operation attempt flag.

The `AcceptedEvidence.evidence_id` must equal the
`AcceptanceRecord.evidence_id`.

The accepted relationship must reference the same `ev1_` Evidence identity
required by the materialized result.

No input may be obtained through filesystem, network, clock, randomness, image
access, OCR, embedding, semantic inference, or model execution.

## 6. Caller-selected statement boundary

The caller must select exactly one existing factual field from the immutable
`image_structural_facts` payload.

The selected factual field:

- must exist exactly once;
- must have one non-empty string value;
- must not be synthesized from multiple fields;
- must not be normalized, summarized, translated, classified, completed, or
  rewritten;
- must not be inferred from image content;
- must not be produced by OCR, embedding, semantic interpretation, or a model.

The caller-supplied statement text must be byte-for-byte equal to the selected
factual field value.

The exact statement type defined by this contract is:

`image_structural_fact`

The exact construction rule defined by this contract is:

`rcis-accepted-image-structural-fact-selection`

The construction rule version is:

`1.0.0`

Any other statement type, rule identifier, rule version, or transformed
statement must fail closed.

## 7. Construction output contract

A successful construction produces exactly:

1. one existing `KnowledgeCandidate` with a canonical `kc1_` identity;
2. one immutable image Knowledge relationship support record;
3. decision `CONSTRUCTED`;
4. zero failure reasons.

A rejected or safe-stopped construction produces:

1. zero `KnowledgeCandidate`;
2. zero image Knowledge relationship support record;
3. one non-empty immutable ordered reason tuple.

No partial output is allowed.

The image Knowledge relationship support record is a construction-result
support sidecar. It does not modify the existing Knowledge Candidate contract
and does not independently represent accepted Knowledge.

## 8. Existing KC1 identity requirement

Knowledge Candidate identity must be calculated through the existing canonical
`kc1_` identity contract.

No parallel identity algorithm is allowed.

The identity-bearing inputs must use the exact existing Knowledge Candidate
identity surface and include the exact caller-selected statement text, exact
statement type, exact construction rule identity, exact Evidence support
identity, and exact initial governance states required by the existing
contract.

The constructed `KnowledgeCandidate.knowledge_candidate_id` must equal the
identity calculated from its final immutable content.

Any identity mismatch must safe-stop with zero output.

Identical valid inputs must produce the identical `kc1_` identity.

## 9. Image Knowledge relationship support

The immutable image Knowledge relationship support record must preserve:

- exact `kc1_` Knowledge Candidate identity;
- exact supporting `ev1_` Evidence identity;
- exact supporting `ar1_` Acceptance Record identity;
- exact accepted relationship subject identity;
- exact accepted relationship object identity;
- exact relationship type;
- exact relationship origin;
- exact authority reference when source-backed;
- exact declaration actor, reason, and timestamp when operator-declared;
- exact source and materialization lineage references needed to prove the
  relationship came from the accepted image Evidence result.

The support record must not reinterpret the relationship.

The support record must not change relationship subject, object, type, origin,
authority, declaration, or lineage values.

The support record must not create a new Evidence, Acceptance, or Knowledge
identity algorithm.

## 10. Initial governance states

Every successfully constructed image Knowledge Candidate must begin with:

- review state `PENDING_REVIEW`;
- authority state `UNASSESSED`;
- conflict state `NOT_ASSESSED`.

Construction must not:

- accept the Knowledge Candidate;
- assess authority;
- resolve conflicts;
- merge text and image claims;
- make a business decision;
- persist accepted Knowledge.

Any request for a different initial governance state must fail closed.

## 11. Decision contract

The construction boundary has exactly three decisions:

- `CONSTRUCTED`;
- `REJECTED`;
- `SAFE_STOP`.

`CONSTRUCTED` requires both the exact Knowledge Candidate and exact image
Knowledge relationship support record.

`REJECTED` is used for complete, explicit, non-ambiguous input that is outside
the supported construction rule.

`SAFE_STOP` is used for malformed, contradictory, ambiguous, prohibited,
identity-inconsistent, or side-effect-seeking input.

`REJECTED` and `SAFE_STOP` require zero output.

## 12. Fail-closed conditions

The boundary must fail closed for any of the following:

1. input is not an exact image Evidence materialization result;
2. materialization decision is not `MATERIALIZED`;
3. any required materialized output is absent;
4. `ev1_` or `ar1_` identity is malformed;
5. Acceptance Record points to another Evidence identity;
6. accepted relationship is absent, ambiguous, or inconsistent;
7. selected factual field is absent, duplicated, or non-string;
8. selected statement differs from the selected factual field value;
9. multiple fields are combined into one statement;
10. statement transformation or interpretation is requested;
11. statement type, construction rule, or version is unsupported;
12. construction timestamp is not timezone-aware;
13. calculated `kc1_` identity differs from the constructed candidate;
14. relationship support differs from accepted relationship provenance;
15. automatic Evidence-to-Knowledge promotion is attempted;
16. automatic conflict resolution is attempted;
17. Knowledge approval or persistence is attempted;
18. image file opening or pixel decoding is attempted;
19. real-asset execution is attempted;
20. OCR, embedding, semantic interpretation, inference, or model execution is
    attempted;
21. filesystem, network, clock, randomness, database, repository, CLI, batch,
    UI, or external-service access is attempted;
22. any partial output would result.

## 13. Determinism, immutability, and purity

For identical explicit inputs, the construction result must be:

- deterministic;
- immutable at its public boundary;
- independent of process time;
- independent of environment state;
- free of filesystem access;
- free of network access;
- free of clock access;
- free of randomness;
- free of image opening or pixel decoding;
- free of OCR;
- free of embeddings;
- free of semantic inference;
- free of model or generator execution;
- free of persistence side effects.

All public request, result, and relationship-support representations must be
immutable.

## 14. Existing contracts protected

This architecture contract does not authorize modification of:

- `src/rie/application/image_evidence_materializer.py`;
- `src/rie/application/knowledge_constructor.py`;
- `src/rie/domain/knowledge_candidate.py`;
- `src/rie/domain/accepted_evidence.py`;
- `src/rie/domain/acceptance_record.py`;
- any existing Evidence, Acceptance, or Knowledge identity contract;
- any package initializer;
- any repository, persistence, CLI, batch, UI, or asset runtime.

A later read-only implementation boundary review must determine whether the
minimum compliant implementation requires:

- one new application constructor;
- one new immutable relationship-support representation;
- a narrowly authorized extension of an existing Knowledge Candidate statement
  boundary;
- or another smaller compatible surface.

Until that later review is accepted, none of those runtime changes is
authorized.

## 15. Explicitly out of scope

The following remain out of scope:

- automatic Evidence-to-Knowledge promotion;
- image interpretation;
- image file opening or pixel decoding;
- OCR or text recognition;
- embeddings or vector databases;
- semantic search;
- ontology or knowledge graph work;
- model reasoning or generator integration;
- multimodal inference;
- automatic text-image conflict detection or resolution;
- Knowledge approval;
- Knowledge persistence;
- database or repository implementation;
- CLI or batch ingestion;
- dashboard or approval UI;
- asset library runtime;
- real image assets;
- full-suite execution;
- Gate 14 closure;
- Gate 15, Gate 16, Gate 17, or Gate 18 implementation.

## 16. Future implementation boundary review

This architecture contract authorizes no runtime implementation.

A later read-only implementation boundary review must independently verify:

1. exact existing Knowledge Candidate and `kc1_` identity surfaces;
2. the minimum compatible representation for image statement type
   `image_structural_fact`;
3. the minimum immutable image Knowledge relationship support representation;
4. exact request, result, and decision symbols;
5. fail-closed reason taxonomy;
6. exact targeted synthetic test boundary;
7. protected existing files;
8. absence of image access, OCR, semantic interpretation, models, persistence,
   and automatic promotion;
9. whether any existing Knowledge contract modification is strictly necessary;
10. that no broader Gate 14 runtime or Gate 14 closure is implied.

Until that review is accepted, only this architecture contract may be
materialized.
