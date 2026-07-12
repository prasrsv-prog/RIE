# PR-022A - Phase 22 Evidence Candidate Boundary Architecture Review

## Status

Documentation-only architecture and terminology review for the Phase 22 Evidence Candidate boundary.

PR-022A inventories the current repository, distinguishes factual extraction and inspection outputs from accepted Evidence and Knowledge, and selects one next contract-review direction. It does not implement Evidence Candidate, materialize Evidence, create Knowledge, modify an existing workflow, or authorize implementation.

## Current checkpoint

The approved checkpoint before creation of this document is:

- Current branch: `phase-022-evidence-candidate-boundary-review`
- Local branch HEAD: `3642955`
- Remote branch HEAD: `3642955`
- Local/remote branch divergence: `0 0`
- Local `main`: `3642955`
- `origin/main`: `3642955`
- Main/origin divergence: `0 0`
- Phase 21 branch: `phase-021-controlled-pdf-post-extraction-review`
- Phase 21 local HEAD: `355e424`
- Phase 21 remote HEAD: `355e424`
- Phase 21 official tag: `v0.21.0-rcis-controlled-pdf-structural-metadata-inspection-phase`
- Phase 21 tag object: `f5c812437bab39be3d648784fbe32a9eeb0f7e11`
- Phase 21 tag target: `f4a246f0fdc695dca9a78f620e2c42dd0bb5de53`
- Repository: clean
- Index: clean
- Untracked files: none
- Controlled sandbox exists and is empty
- Real PDF target: absent
- Synthetic PDF target: absent
- Controlled basetemp: absent

## Purpose

PR-022A defines the boundary between:

- source material
- extraction or inspection output
- structural metadata result
- Evidence Candidate
- accepted Evidence
- rejected or ineligible candidate
- Knowledge

It determines what Evidence currently means in the repository, identifies existing components and gaps, evaluates four Evidence Candidate options, defines minimum eligibility and provenance requirements, assigns future layer ownership, and proposes a gated implementation sequence.

This is a boundary review only. It does not implement Evidence Candidate or Evidence creation.

## Phase 21 authority baseline

Phase 21 formally completed only controlled PDF structural metadata inspection.

Phase 21 did not authorize:

- PDF text or content extraction
- OCR
- rendering
- image extraction
- semantic metadata extraction
- Evidence creation
- EvidenceRelationship creation
- Knowledge creation
- Product Knowledge creation
- Official Knowledge creation
- Prompt Candidate creation
- production directory scanning
- wildcard discovery
- recursive production processing
- automatic parser retry
- parser fallback
- password guessing
- PDF repair workflows

Phase 22 preserves every boundary. Any extension requires a later, narrowly scoped review and execution gate.

## Repository evidence inspected

Read-only inspection covered:

- Package configuration: `pyproject.toml`
- Original asset Evidence path: `src/evidence/evidence.py`, `src/evidence/evidence_builder.py`, `src/collection/evidence_collection.py`, `src/collection/evidence_collector.py`
- Asset analysis used by original Evidence: `src/analysis/asset_analysis.py`, `src/analysis/asset_analyzer.py`
- Text extraction Evidence path: `src/evidence/text_extraction_evidence.py`, `src/evidence/text_extraction_evidence_builder.py`, `src/collection/text_extraction_evidence_collection.py`, `src/collection/text_extraction_evidence_collector.py`
- PDF text Evidence path: `src/evidence/pdf_text_extraction_evidence.py`, `src/evidence/pdf_text_extraction_evidence_builder.py`, `src/collection/pdf_text_extraction_evidence_collection.py`, `src/collection/pdf_text_extraction_evidence_collector.py`
- Evidence artifact inspection and export: `src/collection/text_extraction_evidence_artifact_inspector.py`, `src/evidence/pdf_text_extraction_evidence_artifact_inspector.py`, `src/rie/extraction/export_text_extraction_evidence.py`, `src/rie/extraction/export_pdf_text_evidence.py`
- Extraction models: `src/rie/extraction/text_asset_extraction.py`, `src/rie/extraction/text_asset_extraction_report.py`, `src/rie/extraction/pdf_page_text_extraction.py`, `src/rie/extraction/pdf_text_extraction_report.py`
- Controlled PDF text contracts: `src/rie/ingestion/controlled_pdf_text_extraction_contract.py`, `src/rie/ingestion/controlled_pdf_text_extraction_execution_contract.py`, `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py`
- Controlled structural metadata contracts and implementation: `src/rie/ingestion/controlled_pdf_structural_metadata_contract.py`, `src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py`, `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py`, `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py`
- Official-source governance: `src/official_source/official_source.py`, `src/official_source/official_source_evidence_eligibility_policy.py`, `src/official_source/official_source_evidence_eligibility_gate.py`, `src/official_source/official_source_evidence_workflow_gate.py`, `src/official_source/official_source_evidence_workflow_preflight.py`
- Knowledge and prompt boundaries: `src/knowledge/text_knowledge.py`, `src/knowledge/text_knowledge_builder.py`, `src/knowledge/official_knowledge_source_item.py`, `src/knowledge/official_knowledge_item.py`, `src/knowledge/official_knowledge_collector.py`, `src/prompting/text_prompt_candidate.py`, `src/prompting/text_prompt_candidate_builder.py`
- Application, infrastructure, and interfaces: `src/rie/application`, `src/rie/infrastructure`, `src/rie/interfaces/batch_discovery.py`
- Focused Evidence tests: `tests/test_evidence_builder.py`, `tests/test_evidence_collector.py`, `tests/test_text_extraction_evidence_builder.py`, `tests/test_text_extraction_evidence_collector.py`, `tests/test_pdf_text_extraction_evidence_builder.py`, and `tests/test_pdf_text_extraction_evidence_collector.py`
- Focused eligibility tests: `tests/test_official_source_evidence_eligibility_policy.py`, `tests/test_official_source_evidence_eligibility_gate.py`, `tests/test_official_source_evidence_workflow_gate.py`, and `tests/test_official_source_evidence_workflow_preflight.py`
- Focused structural metadata tests: `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` and `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py`
- Focused downstream-boundary tests: `tests/test_text_knowledge_builder.py` and `tests/test_text_prompt_candidate_builder.py`
- Architecture evidence: `docs/architecture/pr-015b-evidence-workflow-gate-integration-contract-review.md`, `docs/architecture/pr-017e-controlled-pdf-text-evidence-review.md`, `docs/architecture/pr-017i-controlled-pdf-text-extraction-result-boundary-review.md`, `docs/architecture/pr-021a-controlled-pdf-post-extraction-boundary-review.md`, and `docs/architecture/pr-021g-controlled-pdf-structural-metadata-result-contract-review.md`

Search results establish:

- No source or test defines `EvidenceCandidate` or `Evidence Candidate`.
- No source defines `EvidenceRelationship`.
- No `KnowledgeRepository`, `EvidenceRepository`, or Evidence-specific persistence port exists.
- `src/rie/domain` does not exist; domain-like models currently live in top-level packages such as `evidence`, `knowledge`, and `official_source`.
- `src/rie/application` contains no Evidence, Knowledge, candidate, eligibility, or provenance component.
- `src/rie/infrastructure` contains repository scanning/configuration support but no Evidence persistence adapter.
- `src/rie/interfaces` exposes `BatchDiscovery`; it has no Evidence repository or materialization port.

## Current architecture inventory

| Component and exact path | Layer | Current responsibility and I/O | Creates Evidence | Inference | Persistence | Current use and test evidence |
|---|---|---|---:|---:|---:|---|
| `src/evidence/evidence.py`, `src/evidence/evidence_builder.py` | Top-level domain-like Evidence | `Asset` -> frozen `Evidence(asset_path, filename, metadata, analysis)`; builder invokes `AssetAnalyzer` | Yes | Yes, size classification | No | Used by `EvidenceCollector`, core engine/analyzer; tested by `tests/test_evidence_builder.py` |
| `src/collection/evidence_collection.py`, `src/collection/evidence_collector.py` | Collection | `list[Asset]` -> `EvidenceCollection`; no eligibility gate | Yes | Through builder | No | Used by core engine/pipeline and repository analyzer; tested by `tests/test_evidence_collector.py` |
| `src/evidence/text_extraction_evidence.py`, builder, collection, collector | Evidence and collection | Successful `TextAssetExtraction` records -> exact `source_path`, `content`, `size_bytes`; failed extraction skipped/rejected | Yes | No | No | Used by export CLI; tested by text Evidence builder/collector/smoke tests |
| `src/evidence/pdf_text_extraction_evidence.py`, builder, collection, collector | Evidence and collection | Page-extraction dictionaries -> page-scoped Evidence with method, warnings, and positional indexes; invalid records skipped | Yes | No | No | Used by PDF Evidence export CLI; tested by PDF Evidence builder/collector/smoke tests |
| `src/rie/extraction/text_asset_extraction.py`, report | Extraction | File read outcome -> factual path, size, exact content, optional error | No | No | No | Used by text extraction and Evidence flow; extraction tests exist |
| `src/rie/extraction/pdf_page_text_extraction.py`, report | Extraction | PDF page extraction -> exact content, page number, method, warnings; asset errors separate | No | No | No | Used by PDF extraction flow and tests |
| `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py` | Ingestion result contract | Controlled extraction input -> bounded factual result/status; `evidence_allowed=False` | No | No | No | Used by implementation and controlled PDF tests |
| `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py` | Ingestion result contract | Execution authority plus structural values -> immutable validated result with page details/status/errors; `evidence_allowed=False` | No | No | No | Used by structural implementation; extensively tested under `tests/ingestion/` |
| `src/official_source/official_source.py` | Domain-like source governance | Registered source identity/path/type/classification/authority/lifecycle/manual eligibility | No | No | No | Used by registry, eligibility policy, CLI, and tests |
| Eligibility policy, gate, workflow gate, preflight under `src/official_source/` | Governance boundary | `OfficialSource` manual eligibility flag -> decisions allowing or blocking workflow/collection | No | No | No | Policy used by CLI; gate/preflight are test-covered but not wired to Evidence collectors |
| Text and PDF Evidence artifact inspectors | Artifact validation | Serialized artifact -> counts invalid/forbidden fields; no governance or materialization | No | No | No | Used by inspection CLIs and tests |
| Evidence export CLIs under `src/rie/extraction/` | Interface/application script | Read extraction artifact/report, call collector, write Evidence JSON | Yes, through collector | No | Yes, explicit output file only | Directly callable CLIs with tests |
| `src/knowledge/text_knowledge.py`, builder/collector | Knowledge | Evidence-shaped records -> factual `TextKnowledge` copy with evidence index | No | No | No | Used by Knowledge CLI flow and tests |
| Official Knowledge source/item/collector | Knowledge | Curated source items -> one-to-one Official Knowledge items with traceability and index | No | No | No | Used by Official Knowledge flow and tests |
| Text Prompt Candidate model/builder/collector | Prompting | Knowledge-shaped record -> factual prompt candidate copy with indexes | No | No | No | Used by prompt CLI flow and tests |
| `src/rie/interfaces/batch_discovery.py` | Interface/port | Path -> `Batch` discovery abstraction | No | No | No | Implemented by discovery infrastructure/application; unrelated to Evidence materialization |

Inventory conclusions:

- There are three incompatible accepted-Evidence shapes: original asset/analysis Evidence, text extraction Evidence, and PDF page text Evidence.
- Text and PDF Evidence builders perform structural validation but not complete source governance, checksum, execution provenance, authority/lifecycle evaluation, or idempotency.
- `OfficialSourceEvidenceEligibilityPolicy` evaluates only the explicit `evidence_eligibility` enum. Current tests explicitly show lifecycle, authority, source type, path existence, and filesystem access do not affect its decision.
- The preflight boundary correctly does not create Evidence, but it carries only `source_id`, allow/review flags, and reason; it has no candidate payload or provenance and is not integrated with collectors.
- Evidence export CLIs can currently materialize and write Evidence from extraction artifacts without the official-source preflight chain.
- `allowed=True` on extraction or structural result contracts means the factual result satisfies that contract; it does not mean Evidence eligibility.
- Structural metadata is factual and strongly validated, but every Phase 21 contract fixes `evidence_allowed=False`.
- Current Knowledge naming is broader than behavior: `TextKnowledgeBuilder` copies Evidence fields exactly, while Official Knowledge is curated and traceable. The repository does not establish that every Knowledge object is inferred.
- No Evidence repository, persistence abstraction, deterministic identity policy, candidate rejection result, or duplicate/idempotency service exists.

## Existing Evidence model

The repository currently uses “Evidence” for a factual artifact accepted into one of several collections, but acceptance rules differ by path:

- Original asset Evidence includes metadata and derived `AssetAnalysis.size_class` and is created for every supplied `Asset`.
- `TextExtractionEvidence` is an exact factual copy of successful text extraction output; failure is the only builder rejection rule.
- `PdfTextExtractionEvidence` preserves page extraction values and warnings; schema-invalid records and asset errors are skipped, while empty page content remains accepted Evidence.

The common current meaning is therefore not “fully governed and provenance-complete evidence.” It is “a repository-labeled factual or analyzed record admitted by its path-specific builder.” PR-022A establishes a stricter normative definition for future materialization without retroactively changing these components.

Existing Evidence collections are in-memory frozen dataclasses wrapping mutable lists. They do not enforce identity, uniqueness, source authority, provenance completeness, or persistence.

No existing class supports the full proposed accepted-Evidence contract. Existing paths must be treated as compatibility paths and must not be silently rewritten or integrated by PR-022A.

## Existing extraction and inspection model

- `TextAssetExtraction` and `TextAssetExtractionReport` are factual extraction outputs with path, size, exact content, and error state.
- `PdfPageTextExtraction` and `PdfTextExtractionReport` are factual page extraction outputs with source path, size, page number, extraction order, method, exact content, warnings, and asset errors.
- `ControlledPdfTextExtractionResultContractResult` is a bounded ingestion result with source label, status, counts/preview, truncation, error, and `evidence_allowed=False`.
- `ControlledPdfStructuralMetadataResultContractResult` is a deterministic inspection result containing fixture/source references, status, encryption, page count, bounded page detail values, truncation, approved errors, notes, and `evidence_allowed=False`.
- Result contracts validate result integrity and execution authority. They do not establish source checksum, job identity, extractor version, candidate identity, accepted-Evidence identity, or duplicate behavior.
- Structural metadata tests prove page-index continuity, dimensions, rotations, bounded/truncated status, errors, and permanent Evidence prohibition within Phase 21.

Extraction and inspection results remain upstream factual outputs. Their validity is necessary but insufficient for accepted Evidence.

## Boundary terminology

### Source Material

A specifically admitted and identified source selected under an explicit inspection or extraction authority. Current `Asset`, `OfficialSource`, and controlled fixture contracts are source representations, but only `OfficialSource` carries authority/lifecycle classifications. A path alone is not source authority.

### Inspection Result

A factual output produced by inspecting source structure without interpreting source meaning. This definition is confirmed by the structural metadata result contract.

### Extraction Result

A factual output produced by extracting source content without accepting it as Evidence or converting it to Knowledge. This definition is confirmed by text and PDF extraction reports and controlled result contracts.

### Structural Metadata Result

A deterministic inspection result describing document structure, including page count, dimensions, rotations, encryption state, inspection status, truncation, and parser errors. It is an Inspection Result subtype, not automatically Evidence.

### Evidence Candidate

A proposed immutable application-layer record containing one factual extraction or inspection payload plus sufficient identity, provenance, execution, and locator inputs for an explicit eligibility decision. It is not accepted Evidence, has no Evidence identity or persistence authority, and may be rejected.

This is a new term. No current source or test defines it.

### Accepted Evidence

A factual and reproducible record that has passed explicit source eligibility, provenance completeness, payload validation, authority, deterministic identity, and duplicate/idempotency checks, then has been deliberately materialized by a separately reviewed builder. This is a normative future definition; current Evidence classes do not all satisfy it.

### Rejected Candidate

A candidate with an explicit ineligible, review-required, duplicate, conflicting, or invalid result. It must not enter an accepted Evidence collection. Rejection must be returned visibly and must not be silently discarded or overwritten.

### Knowledge

A separately authorized downstream representation derived from accepted Evidence or explicitly curated source items. It may be normalized, composed, inferred, or interpreted only under its own reviewed rules. Current `TextKnowledge` is a transparent factual copy and current Official Knowledge is curated, so the repository does not support defining all Knowledge as inferred. The controlling boundary is separation and explicit authority, not an assumption about transformation style.

## Evidence Candidate necessity review

| Option | Single responsibility and domain purity | Traceability and testability | Persistence/lifecycle cost | Authority drift and compatibility | Assessment |
|---|---|---|---|---|---|
| A. No candidate; validate extraction result directly in Evidence builder | Conflates eligibility orchestration with construction or requires a large builder input surface | Can be tested, but rejected state and provenance are implicit | Low type count | Repeats current direct-builder weakness and risks automatic promotion; source-specific builders diverge | Not selected |
| B. Immutable application-layer DTO | Keeps ingestion factual, domain materialization explicit, and candidate non-authoritative | Makes provenance, eligibility input, rejection, and cross-source tests explicit | No identity/lifecycle persistence required | Fits existing frozen-dataclass style and can adapt text, PDF, structural, and future image outputs without putting policy in ingestion | Selected |
| C. Domain entity with identity and lifecycle | Treats a pre-acceptance transport record as durable domain state | Strong lifecycle modeling | Requires identity, state transitions, repository, and persistence semantics absent today | High over-engineering and premature authority; candidate may be mistaken for accepted domain Evidence | Not selected |
| D. Candidate inside ingestion result contract | Convenient for one ingestion path | Good local traceability | Low initial persistence cost | Couples Evidence governance to PDF/ingestion contracts, duplicates across source types, and weakens domain/application separation | Not selected |

Option B best addresses the demonstrated gap: current extraction-to-Evidence builders lack a complete pre-materialization boundary, while the existing source preflight lacks the payload and provenance required for Evidence construction.

## Selected architecture option

Select **Option B: Evidence Candidate as an application-layer immutable DTO**.

Recommended boundary flow:

```text
admitted source + valid factual extraction/inspection result
-> application candidate construction
-> immutable Evidence Candidate
-> pure eligibility evaluation
-> explicit eligibility result
-> accepted: domain Evidence builder
-> duplicate/idempotency check
-> accepted Evidence collection insertion

or

-> rejected/review-required result
-> no Evidence construction
```

The candidate must:

- contain factual payload and provenance only
- carry no accepted-Evidence status by implication
- have no mutable lifecycle
- perform no I/O, persistence, inference, normalization, summarization, or collection insertion
- remain source-agnostic enough for text, PDF page text, structural metadata, and future image facts
- preserve source-specific payload type and locator rather than flattening meaning

PR-022A selects the next contract review only. It does not approve a field schema or implementation file.

## Eligibility boundary

| Condition before accepted Evidence | Classification | Review outcome |
|---|---|---|
| Source explicitly admitted | Mandatory | Candidate construction requires an admitted source record, not an arbitrary path |
| Source identity known | Mandatory | Stable `source_id` required |
| Source authority known and permitted | Mandatory | `UNKNOWN`, unreviewed draft, or disallowed authority must not auto-pass |
| Lifecycle eligible | Mandatory | Active/locked/final policy must be explicit; deprecated/superseded/unknown must not auto-pass |
| Source checksum present | Mandatory | Required for traceability and deterministic identity; absent today |
| Execution/job identity present | Mandatory | Required to reproduce and audit the producing run |
| Extractor/inspector name and version known | Mandatory | Implementation identity must be explicit |
| Result contract version known | Mandatory | Payload interpretation must be versioned |
| Payload data type supported | Mandatory | Unknown payload type is rejected |
| Controlled source reference traceable | Mandatory | Path/reference is provenance, never authority by itself |
| Page, region, or equivalent locator | Conditional | Mandatory when the payload describes a sub-document location; document-level facts use an explicit document locator |
| Candidate payload factual | Mandatory | Must represent observed/extracted values |
| Candidate payload reproducible | Mandatory | Same admitted source and versioned process must reproduce it within defined deterministic rules |
| Inferred content | Prohibited | Must be rejected before materialization |
| Semantically rewritten or summarized content | Prohibited | Must not be a candidate payload |
| Unsupported claim | Prohibited | Must be rejected |
| Candidate validation succeeds | Mandatory | Shape, type, bounds, status, warnings/errors, and provenance validation must pass |
| Duplicate/idempotency rule succeeds | Mandatory | Duplicate outcome may be idempotent/no-op but must never silently create another record |
| Authority boundary permits materialization | Mandatory | Separate reviewed authority must explicitly allow the Evidence type |

Deferred until later contract reviews:

- exact lifecycle eligibility matrix
- exact supported payload-type registry
- exact deterministic identity encoding/hash algorithm
- conflict-resolution policy
- durable audit and rejected-candidate persistence

“Deferred” means the rule detail is not defined here; it does not waive mandatory checks before production materialization.

## Provenance requirements

The minimum conceptual model is grouped as follows. Field names are contract candidates, not an implemented persistence schema.

### Identity fields

- `source_id`
- source checksum
- payload type
- source-specific locator
- deterministic candidate identity derived under a versioned rule

### Provenance fields

- source type
- source authority
- source lifecycle state
- controlled source reference or controlled path reference
- source/document classification where applicable

### Payload fields

- exact raw factual payload
- payload type/version
- page index, region, field, or document locator where applicable
- factual warnings attached to the payload

### Execution fields

- `execution_id` or `job_id`
- extractor/inspector name
- extractor/inspector version
- result contract version
- execution timestamp
- extraction/inspection status
- errors

### Eligibility fields

- eligibility decision: eligible, rejected, review-required, or duplicate
- reason codes and human-readable reason
- eligibility rule version
- authority decision reference

### Audit fields

- decision timestamp
- reviewer/operator reference when manual review occurs
- prior conflicting identity reference when applicable
- immutable record of warnings, errors, and decision inputs

The application DTO should carry the factual and decision inputs needed for evaluation. Eligibility decision and audit output should live in a separate immutable eligibility result rather than mutating the candidate.

## Identity and idempotency review

Candidate identity should be deterministically derived from a canonical combination of:

- `source_id`
- source checksum
- source-specific locator
- payload type
- normalized raw-payload byte representation or payload hash
- extractor/inspector version
- result contract version

“Normalized” here means deterministic byte/field serialization only. It must not rewrite or normalize semantic meaning.

Identity must not use:

- mutable absolute local path as the sole identity
- current timestamp as identity
- random UUID as the only deduplication mechanism
- semantic summary
- Knowledge text
- unstable field ordering

Recommended ownership:

- Evidence Candidate carries identity inputs and the identity-rule version.
- A pure domain identity policy owns canonical component ordering and deterministic derivation rules.
- The eligibility validator verifies completeness and consistency of identity inputs.
- The accepted Evidence builder verifies the eligible decision and maps the deterministic identity into accepted Evidence.
- An Evidence repository port, if later approved, owns uniqueness enforcement and idempotent insert semantics.
- An infrastructure adapter may implement storage-specific uniqueness but must not define domain identity.

No hashing, ID generation, repository, or persistence behavior is implemented or authorized here.

## Structural metadata boundary

### Group A - document-structure facts

- page count
- page dimensions
- page rotation
- encryption state
- inspection status
- truncation state
- parser warnings/errors

Group A may become Evidence of document structure only after explicit source eligibility, provenance, payload, identity, and materialization review. Structural metadata is not Evidence of product meaning or document semantics.

### Group B - document-content facts

- exact extracted text
- exact field values
- image or region facts
- tables
- product specifications as exact source content

Group B requires a future controlled content-extraction authority before eligibility review. Phase 22 does not reactivate or broaden past extraction authority.

### Group C - semantic or business interpretations

- product benefit
- persona suitability
- campaign claim
- recommendation
- brand positioning
- creative direction

Group C is not factual Evidence materialization input. It belongs to later Knowledge or business decision processes with separate authority.

Critical rule:

**Structural metadata, extraction output, and inspection results must not be promoted automatically into accepted Evidence. Promotion requires a separately reviewed Evidence eligibility and materialization process.**

PR-022A does not state that structural metadata can never be Evidence. It may later qualify as Evidence of document structure, never automatically and never as proof of product meaning.

## Rejected and ineligible data

Future workflows should return a structured eligibility result for every candidate. Rejection must not be silent.

| Condition | Future treatment |
|---|---|
| Missing source identity or checksum | Reject; no Evidence; report missing provenance |
| Unknown/disallowed authority or lifecycle | Reject or explicit review-required outcome according to future policy |
| Unsupported source or payload type | Reject |
| Missing required locator | Reject; document-level facts require explicit document locator semantics |
| Parser warning | Evaluate by versioned rule; retain warning; never silently accept or discard |
| Parser error | Reject |
| Partial or truncated result | Review-required or rejected according to payload-specific rule; never auto-accept |
| Encrypted source | Reject unless a separately reviewed authority defines a non-content structural fact policy |
| Duplicate candidate | Return explicit duplicate/idempotent outcome; do not insert or overwrite silently |
| Non-deterministic payload | Reject |
| Inferred, summarized, normalized-meaning, or rewritten content | Reject as Evidence Candidate input |
| Conflicting payload for the same deterministic identity | Reject and defer for operator review; never overwrite |

The minimum behavior is to return rejected/review-required/duplicate results to the caller. Durable audit storage is deferred to a persistence review. Reviewable candidates may be routed to an operator-review interface only after a separate contract. Rejected data must not enter accepted collections.

## Layer ownership

| Responsibility | Recommended owner | Boundary |
|---|---|---|
| Factual extraction/inspection | Ingestion/extraction | Produces versioned factual result only; never Evidence |
| Candidate construction | Application | Adapts admitted source plus factual result into immutable DTO; no policy or I/O |
| Eligibility validation | Domain policy/service | Pure evaluation of candidate and authority inputs; returns immutable result |
| Accepted Evidence construction | Domain Evidence builder | Requires eligible decision; creates accepted Evidence only |
| Deterministic identity rules | Domain policy | Defines canonical identity inputs and rule version |
| Duplicate detection orchestration | Application | Queries port before insertion and returns explicit outcome |
| Evidence collection insertion | Application calling existing/new collection boundary | Only accepted Evidence may be inserted |
| Evidence persistence abstraction | Interface/port | Future review; no current port exists |
| Storage and uniqueness enforcement | Infrastructure | Future adapter implementing port; no authority/policy |
| Rejection reporting | Application result | Structured rejected/review/duplicate outcome |
| Audit reporting | Application plus future audit port | Persistence deferred; no silent loss |
| Synthetic candidate fixtures | Test fixture only | Neutral factual data; no real governed source content |

Existing collectors and builders remain unchanged until a dedicated integration review. The official-source preflight may be an input to future orchestration, but it is insufficient alone because it carries neither payload nor complete provenance.

## No-Knowledge rule

- Evidence Candidate contains no inference.
- Accepted Evidence contains no inference introduced during materialization.
- Evidence Candidate does not normalize meaning.
- Evidence Candidate does not summarize content.
- Evidence Candidate does not combine unrelated facts.
- Evidence Candidate makes no brand, product, campaign, persona, or creative decision.
- Accepted Evidence does not become Knowledge automatically.
- Existing Knowledge classes do not authorize candidate or Evidence materialization.
- Knowledge creation remains a separate phase and reviewed authority.
- Product Knowledge creation remains prohibited.
- Official Knowledge creation remains prohibited.
- Prompt Candidate creation remains prohibited.

## Security and data hygiene

Future candidate/materialization work must enforce:

- no arbitrary directory scanning
- no wildcard production ingestion
- no uncontrolled recursive traversal
- no hidden parser fallback
- no automatic retry
- no password guessing
- no source mutation
- no external source deletion
- no temporary asset leakage
- no path-based authority assumptions
- no silent candidate acceptance
- no silent candidate rejection
- no silent duplicate overwrite
- no automatic Evidence, Knowledge, or Prompt Candidate chaining
- exact controlled source and execution authority at every real-asset gate

## Test strategy

Future implementation requires, in gated order:

- Contract tests: exact immutable fields, type validation, no extra semantics
- Construction tests: adapters preserve exact factual payload and provenance
- Eligibility tests: each mandatory, conditional, deferred, and prohibited rule
- Provenance tests: missing identity/checksum/authority/lifecycle/execution/version/locator cases
- Deterministic identity tests: stable ordering, same-input stability, changed-input distinction
- Duplicate/idempotency tests: no double insertion and no silent overwrite
- Rejection tests: rejected, review-required, duplicate, conflict, partial, truncated, warning, and error outcomes
- Boundary tests: extraction/inspection result is not accepted Evidence
- No-Knowledge tests: no summary, semantic rewrite, inference, Product Knowledge, Official Knowledge, or Prompt Candidate
- No-persistence tests for pure candidate, eligibility, identity, and builder layers
- Port contract tests before any persistence adapter
- Synthetic source tests with neutral factual values
- Controlled real-asset tests only under a separate reviewed execution gate
- Full regression tests only at an explicitly authorized regression gate

PR-022A writes no tests and executes no tests.

## Future implementation sequence

The safe proposed sequence is:

1. **PR-022B - Evidence Candidate Contract Review**
2. **PR-022C - Evidence Candidate Contract Skeleton**
3. **PR-022D - Evidence Eligibility Result Contract Review**
4. **PR-022E - Evidence Eligibility Result Contract Skeleton**
5. **PR-022F - Evidence Eligibility Validator Review**
6. **PR-022G - Evidence Eligibility Validator Skeleton**
7. **PR-022H - Deterministic Evidence Identity Strategy Review**
8. **PR-022I - Deterministic Evidence Identity Skeleton**
9. **PR-022J - Accepted Evidence Materialization Contract Review**
10. **PR-022K - Accepted Evidence Builder Skeleton**
11. **PR-022L - Evidence Collection Integration Review**
12. **PR-022M - Evidence Persistence Port Review**
13. **PR-022N - Synthetic Evidence Candidate Smoke Flow Review**
14. **PR-022O - Controlled Real-Asset Evidence Candidate Execution Review**
15. **PR-022P - Phase 22 Final Regression and Closure Review**

This sequence is a planning recommendation only. Each code-bearing step requires its own approved contract/review gate. Persistence, collection integration, and real-asset execution must not be pulled into earlier steps.

## Acceptance criteria

1. **SATISFIED** - Current branch equals the approved Phase 22 branch.
2. **SATISFIED** - Local and remote Phase 22 HEAD equal `3642955`.
3. **SATISFIED** - Local and remote Phase 22 divergence is `0 0`.
4. **SATISFIED** - `main` and `origin/main` equal `3642955`.
5. **SATISFIED** - Phase 21 branch remains preserved.
6. **SATISFIED** - Phase 21 tag object remains unchanged.
7. **SATISFIED** - Phase 21 tag target remains unchanged.
8. **SATISFIED** - Repository architecture was inspected read-only.
9. **SATISFIED** - Existing Evidence components are inventoried.
10. **SATISFIED** - Existing extraction and inspection components are inventoried.
11. **SATISFIED** - Existing structural metadata components are inventoried.
12. **SATISFIED** - Existing tests are inventoried.
13. **SATISFIED** - Evidence Candidate term usage was searched.
14. **SATISFIED** - Evidence definition is grounded in repository evidence.
15. **SATISFIED** - Knowledge definition is grounded in repository evidence.
16. **SATISFIED** - Inspection Result is distinguished from Evidence.
17. **SATISFIED** - Extraction Result is distinguished from Evidence.
18. **SATISFIED** - Structural Metadata Result is distinguished from Evidence.
19. **SATISFIED** - Evidence Candidate is distinguished from accepted Evidence.
20. **SATISFIED** - Rejected Candidate is distinguished from accepted Evidence.
21. **SATISFIED** - Accepted Evidence is distinguished from Knowledge.
22. **SATISFIED** - Automatic promotion into Evidence is prohibited.
23. **SATISFIED** - Structural metadata may only become Evidence after explicit eligibility review.
24. **SATISFIED** - Product meaning is not inferred from structural metadata.
25. **SATISFIED** - Evidence Candidate necessity options were compared.
26. **SATISFIED** - Exactly one architecture recommendation is selected: Option B.
27. **SATISFIED** - Eligibility conditions are classified.
28. **SATISFIED** - Provenance requirements are defined.
29. **SATISFIED** - Identity and idempotency ownership is reviewed.
30. **SATISFIED** - Structural, content, and semantic fact groups are separated.
31. **SATISFIED** - Rejected and ineligible handling is reviewed.
32. **SATISFIED** - Layer ownership is defined.
33. **SATISFIED** - No-Knowledge rules are explicit.
34. **SATISFIED** - Security and data hygiene rules are explicit.
35. **SATISFIED** - Test strategy is defined without writing tests.
36. **SATISFIED** - Future implementation sequence is defined.
37. **SATISFIED** - No source code was modified.
38. **SATISFIED** - No test file was modified.
39. **SATISFIED** - No dependency or configuration was modified.
40. **SATISFIED** - No prior document was modified.
41. **SATISFIED** - No tests were executed.
42. **SATISFIED** - No parser or ingestion workflow was executed.
43. **SATISFIED** - No Evidence was created.
44. **SATISFIED** - No Knowledge was created.
45. **SATISFIED** - PR-022A does not authorize implementation.

All 45 architecture-review acceptance criteria are satisfied.

## Recommended PR-022B

The single recommended next review is:

**PR-022B - Evidence Candidate Contract Review**

PR-022B should define the exact immutable application-layer DTO contract, supported factual payload envelope, provenance inputs, prohibited fields, and adaptation boundary. It must remain a contract review and must not implement materialization, eligibility policy, persistence, collection integration, Knowledge, or Prompt Candidate behavior.

## Architecture decision

**READY FOR EVIDENCE CANDIDATE CONTRACT REVIEW**
