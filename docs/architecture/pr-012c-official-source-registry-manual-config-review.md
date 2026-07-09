# PR-012C Official Source Registry Manual Config Architecture Review

## Status

PR-012C is docs-only.

No registry config file is introduced.
No registry reader is introduced.
No CLI is introduced.
No production behavior changes are introduced.

## Context

PR-012 established the Official Source Registry governance boundary.

PR-012B added the minimal `OfficialSource` domain skeleton with separate
concepts for `SourceType`, `DocumentClassification`, `AuthorityStatus`,
`LifecycleStatus`, and `EvidenceEligibility`.

PR-012C defines the future manual config format and future reader boundary
before any implementation.

## Decision

The future manual official source registry config format should be JSON.

JSON is the preferred first format because it:

- aligns with the existing project artifact style
- uses the Python standard library
- is deterministic
- is data-only
- avoids executable registry declarations
- avoids introducing YAML or TOML dependencies

The first manual registry format should explicitly reject these options for now:

- YAML
- TOML
- Python object declarations

## Future Config Location

Future config files may be added only after separate approval.

Synthetic example location after approval:

```text
examples/official_source/official-source-registry.example.json
```

Real registry location after approval:

```text
configs/official_source_registry.json
```

PR-012C does not create either file.

A future reader should accept an explicit path.

A future reader should not auto-load a default registry.

## Conceptual JSON Shape

This shape is documentation only. It is synthetic example data and does not use
real RSV locked content.

```json
{
  "official_sources": [
    {
      "source_id": "SRC-001",
      "source_path": "docs/example-source.pdf",
      "source_type": "pdf",
      "document_classification": "project_rulebook",
      "authority_status": "source_of_truth_candidate",
      "lifecycle_status": "locked",
      "evidence_eligibility": "eligible_with_review",
      "version": "v1.0",
      "review_notes": "Synthetic example only."
    }
  ]
}
```

## Required Fields

Future manual registry entries should require:

- `source_id`
- `source_path`
- `source_type`
- `document_classification`
- `authority_status`
- `lifecycle_status`
- `evidence_eligibility`

## Optional Fields

Future manual registry entries may allow:

- `version`
- `review_notes`

`source_local_id` remains a future open question. It must not be accepted until
the domain model or a registry-entry wrapper explicitly supports it.

## Future Reader Allowed Validation

A future reader may:

- parse JSON
- require a top-level object
- require an `official_sources` list
- require each item to be an object
- reject unknown or forbidden fields
- require a non-empty manual `source_id`
- require a non-empty `source_path`
- reject duplicate `source_id`
- map exact enum string values to existing enum instances
- allow explicit `"unknown"` enum values
- preserve input order
- return deprecated and superseded entries for traceability
- construct `OfficialSource` rather than bypass its validation

## Future Reader Forbidden Validation

A future reader must not:

- check whether `source_path` exists
- read source documents
- read locked documents
- parse PDFs
- extract content
- infer classification from filename, path, or content
- infer authority from lifecycle
- infer eligibility from source type
- generate source IDs
- generate knowledge IDs
- create Evidence
- create Official Knowledge
- create Product Knowledge
- create Prompt Candidate
- create Final Prompt
- call AI
- convert PDF Evidence into Official Knowledge

## Forbidden Downstream Fields

Manual registry entries must reject downstream workflow fields such as:

- `content`
- `text`
- `evidence`
- `evidence_index`
- `knowledge`
- `knowledge_id`
- `official_knowledge`
- `official_knowledge_index`
- `product_type`
- `prompt`
- `final_prompt`
- `ai_generated`

## Future Tests

Future implementation tests should cover:

- valid JSON maps to `OfficialSource`
- missing required fields fail
- blank `source_id` and `source_path` fail
- duplicate `source_id` fails
- invalid enum string fails
- explicit `"unknown"` passes
- downstream fields fail
- nonexistent `source_path` still passes as a string reference
- deprecated and superseded entries remain returned
- input order is preserved
- input is not mutated
- no real RSV locked content is used

## Future PR Slices

Future slices only:

- PR-012D - Manual registry dict loader
- PR-012E - Optional JSON file loader
- PR-012F - Registry inspection CLI
- Later only - Evidence eligibility integration

## Risks and Mitigations

### Risk: Config Mistaken As Extraction Layer

Mitigation: Keep the registry config limited to source governance declarations.
Do not allow content fields, extraction fields, or downstream workflow outputs.

### Risk: Source Path Mistaken As Filesystem Truth

Mitigation: Treat `source_path` as a string reference only. A future reader must
not check existence, read the path, normalize it, or mutate the target document.

### Risk: Filename Inference Creep

Mitigation: Require explicit manual fields for classification, authority,
lifecycle, and eligibility. Filename and path may not determine authority.

### Risk: ID Generation Creep

Mitigation: Require manually provided stable `source_id` values. Do not generate
source IDs or knowledge IDs.

### Risk: Downstream Fields Creep

Mitigation: Reject fields that belong to Evidence, Official Knowledge, Product
Knowledge, Prompt Candidate, Final Prompt, AI output, or PDF conversion flows.

### Risk: Source Local ID Support Needed Later

Mitigation: Keep `source_local_id` as a documented future question until a
domain model extension or wrapper is approved.

### Risk: Deprecated Or Superseded Traceability Lost

Mitigation: Future readers should keep deprecated and superseded sources
registry-visible so historical decisions remain traceable.

## Non-Scope

PR-012C does not include:

- implementation
- config files
- registry reader
- CLI
- tests
- evidence integration
- official knowledge integration
- Product Knowledge
- Prompt Candidate
- Final Prompt
- AI
- PDF conversion
- locked document reads
- source ID generation
- knowledge ID generation
