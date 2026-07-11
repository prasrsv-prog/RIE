# PR-021B - Controlled PDF Structural Metadata Capability Review

## Status

* Documentation-only capability review.
* PR-021A is committed and synchronized on the Phase 21 branch.
* No PDF asset is currently present in the controlled sandbox.
* No structural metadata inspection has been executed.
* No source code, tests, dependency, or virtual environment changes are authorized.
* No OCR, PDF page rendering, embedded-image extraction, Evidence, Knowledge, or Prompt Candidate workflow is authorized.

## Current checkpoint

* Branch: `phase-021-controlled-pdf-post-extraction-review`
* Branch HEAD before PR-021B: `1fb7d68`
* `main`: `fbb0c99`
* `origin/main`: `fbb0c99`
* Phase 21 branch is synchronized with its remote branch.
* Working-tree tracked diff: empty.
* Cached diff: empty.
* Controlled real-asset sandbox directory exists and remains empty.
* The Phase 20 real PDF target remains absent.

## Purpose

Determine whether a narrowly bounded PDF structural metadata capability should be introduced after the controlled PDF text-extraction phase.

PR-021B reviews:

* existing reusable upstream contracts
* existing PDF dependency availability
* separation from PDF text extraction
* candidate structural metadata fields
* prohibited metadata and content access
* required future contract layers
* required execution and result boundaries
* whether a new capability is architecturally justified

PR-021B does not implement or execute the capability.

## Reviewed components

The review covered:

* `ControlledRealAssetFixtureContract`
* `ControlledPdfTextExtractionContract`
* `ControlledPdfTextExtractionExecutionContract`
* `ControlledPdfTextExtractionImplementation`
* `ControlledPdfTextExtractionResultContract`
* declared PDF dependencies in `pyproject.toml`
* relevant tracked test paths

No PDF file was opened or processed during this review.

## Existing fixture authority

`ControlledRealAssetFixtureContract` already includes:

```text
allowed_for_metadata
```

The contract requires metadata access to be explicitly allowed and continues to prohibit:

* PDF text-extraction authority at the fixture layer
* image metadata authority
* Evidence creation authority
* unsupported fixture types
* duplicate fixture IDs
* duplicate fixture paths

This fixture contract can remain the upstream authority for a future PDF structural metadata capability.

It does not, however, define:

* which PDF structural metadata fields may be read
* whether execution is approved
* page limits
* output boundaries
* result validation
* parser errors
* metadata retention
* downstream authority

Therefore, the fixture contract is necessary but not sufficient.

## Existing PDF dependency

The project already declares:

```text
pypdf
```

The existing controlled text-extraction implementation imports:

```text
pypdf.PdfReader
```

The dependency is therefore already present in the project architecture.

PR-021B does not authorize dependency synchronization or environment modification.

The existing dependency may be considered sufficient for a future structural metadata implementation, subject to:

* contract review
* public API review
* synthetic verification
* bounded execution review
* no additional dependency being introduced without approval

## Text-extraction chain assessment

The existing PDF text-extraction chain is purpose-specific.

It enforces:

* fixture type `product_spec_pdf`
* extraction mode `text_only`
* explicit text-extraction execution authority
* extracted-character limits
* text-preview limits
* no full-text storage
* text-specific extraction statuses
* no Evidence creation

The implementation performs page iteration and calls text extraction on each page.

The result contract validates:

* text length
* text preview
* text truncation
* text extraction errors
* text-specific statuses
* prohibition on extracted-text storage

These contracts are not suitable for structural metadata.

They must not be generalized or extended with optional metadata fields because doing so would:

* combine two distinct capabilities
* weaken single responsibility
* mix text limits with structural metadata limits
* complicate result validation
* create ambiguous execution authority
* increase the risk of accidental content extraction

## Decision on contract reuse

The following components may be reused:

```text
ControlledRealAssetFixtureContract
pypdf dependency
product_spec_pdf fixture type
fixture identity and source path
metadata access gate
no-Evidence boundary
```

The following components must not be reused as structural metadata contracts:

```text
ControlledPdfTextExtractionContract
ControlledPdfTextExtractionExecutionContract
ControlledPdfTextExtractionImplementation
ControlledPdfTextExtractionResultContract
```

A new isolated structural metadata chain is required.

## Proposed capability chain

The proposed future capability chain is:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfStructuralMetadataContract
-> ControlledPdfStructuralMetadataExecutionContract
-> ControlledPdfStructuralMetadataImplementation
-> ControlledPdfStructuralMetadataResultContract
```

The names are provisional until PR-021C approves the contract design.

Each layer must remain single-purpose.

## Structural metadata definition

For this phase, structural metadata means bounded technical properties of the PDF container and its pages.

It does not mean:

* page text
* OCR text
* visual interpretation
* semantic metadata
* product specifications
* embedded media content
* document claims
* Evidence
* Knowledge

## Candidate permitted fields

The following fields may be considered in PR-021C:

### Document-level fields

* fixture ID
* source label
* fixture path
* fixture type
* parser availability status
* encrypted state
* page count
* inspection status
* bounded inspection error
* notes
* Evidence allowed, fixed to `False`

### Page-level structural fields

For an explicitly bounded number of pages:

* zero-based or one-based page index, to be selected consistently
* page width
* page height
* page rotation
* page inspection status

These fields are review candidates only.

PR-021B does not authorize reading them from a real PDF.

## Prohibited fields and access

The structural metadata capability must not read, expose, or store:

* page text
* text preview
* OCR output
* rendered page pixels
* embedded images
* image streams
* annotations
* form field values
* attachments
* outlines or bookmarks
* JavaScript
* links or destinations
* document title
* document author
* document subject
* document keywords
* creator or producer values
* XMP metadata
* product names
* product specifications
* product claims
* inferred labels
* inferred document classification
* Evidence
* Knowledge
* Prompt Candidates

Document information dictionaries and XMP metadata are excluded because they may contain semantic or user-authored content rather than strictly structural properties.

## Page-boundary requirement

A future structural metadata capability must not iterate over an unlimited number of pages without a reviewed limit.

PR-021C must define:

* maximum inspected page count
* behavior when document page count exceeds the limit
* whether only the first bounded pages are inspected
* whether the result records truncation
* whether page count may still be reported when detailed page inspection is bounded
* maximum result-item count

No numeric limit is authorized by PR-021B.

## Output boundary

A future structural metadata result may contain only bounded value objects.

It must not create:

* JSON files
* rendered images
* extracted assets
* OCR files
* text reports generated automatically
* parser dump files
* temporary scripts
* Evidence artifacts
* Knowledge artifacts

Initial verification output should remain bounded terminal output or in-memory result values.

Any persistent output requires a separate retention review.

## Error boundary

A future structural metadata result contract should distinguish at least:

* not run
* inspected
* partially inspected or bounded
* encrypted
* unreadable
* parser unavailable
* parser error
* blocked

Final status names must be approved in PR-021C.

Error values must:

* remain bounded
* avoid raw stack traces
* avoid filesystem disclosure beyond the approved fixture path
* avoid page content
* avoid parser object dumps

## Execution authority

Structural metadata inspection must require a dedicated execution contract.

The fixture-level `allowed_for_metadata=True` flag alone must not authorize execution.

Execution must require:

* an allowed fixture-contract result
* exact fixture identity
* exact fixture path
* fixture type `product_spec_pdf`
* explicit structural metadata execution approval
* approved page limit
* approved output fields
* no content extraction
* no output-file creation
* no Evidence creation

## No automatic fallback

The structural metadata capability must not automatically trigger:

* PDF text extraction
* page rendering
* embedded-image extraction
* OCR
* image understanding
* Evidence construction
* Knowledge construction

Its result must not decide that another capability should run.

A later capability may only consume structural metadata after a separately approved integration review.

## Test boundary

Future tests should be isolated from existing PDF text-extraction tests.

The future test sequence should include:

1. value-only contract tests
2. blocked execution tests
3. synthetic PDF structural metadata tests
4. page-boundary tests
5. encrypted or unreadable-state tests where safely reproducible
6. result-contract validation tests
7. no-content-extraction assertions
8. no-Evidence assertions

Existing Evidence-related PDF tests are outside the scope of Phase 21 and must not be modified by this capability.

## Real-asset boundary

No real PDF is required for PR-021B.

A future real-asset execution requires separate reviews for:

* fresh manual placement
* exact target metadata verification
* execution authority
* one controlled execution
* output review
* retention decision
* cleanup execution
* closure

The Phase 20 PDF must not be restored automatically.

## Dependency decision

PR-021B does not identify a need for a new dependency.

The existing `pypdf` dependency is the only approved dependency candidate for future review.

This decision does not guarantee that every candidate structural field is supported through an approved public API.

PR-021C must avoid contract fields that depend on:

* undocumented parser internals
* private attributes
* unstable object dumps
* implementation-specific raw objects

## Architectural decision

A controlled PDF structural metadata capability is justified, provided that it remains:

* structurally focused
* value-only at the contract level
* bounded by page and result limits
* isolated from text extraction
* isolated from visual extraction
* isolated from inference
* isolated from Evidence and Knowledge
* execution-gated
* non-persistent by default

The capability must use a new dedicated contract chain.

## Recommended next PR

The next PR is:

```text
PR-021C - Controlled PDF Structural Metadata Contract Review
```

PR-021C must remain documentation-only.

It should define:

* exact contract class responsibilities
* exact input and result fields
* allowed statuses
* page index convention
* page-count boundary
* per-page detail boundary
* truncation behavior
* error behavior
* execution flags
* no-content guarantees
* no-Evidence guarantees
* whether the proposed names should be adopted

PR-021C must not create source code or tests.

## Allowed work in PR-021B

PR-021B may:

* document reviewed source components
* classify reusable and non-reusable components
* define structural metadata boundaries
* recommend a dedicated capability chain
* identify the existing dependency candidate
* define the next contract-review step

## Prohibited work in PR-021B

PR-021B must not:

* place or restore a PDF
* instantiate `PdfReader`
* inspect PDF properties
* execute text extraction
* render pages
* extract embedded images
* run OCR
* install or update dependencies
* modify source code
* modify tests
* modify the virtual environment
* create result files
* inspect production paths
* create Evidence
* create Knowledge
* create Prompt Candidates
* modify locked or SSOT documents

## Git boundary

* Only the PR-021B document may be introduced.
* PR-021A must remain unchanged.
* No source code or test files may change.
* No real asset may be staged or committed.
* Any unexpected tracked or staged file is a hard stop.
* No merge or Phase 21 tag is authorized.

## Acceptance criteria

* PR-021B is documentation-only.
* Existing source components are reviewed without execution.
* The existing fixture contract is retained as upstream authority.
* Existing text-extraction contracts are not reused for structural metadata.
* A new dedicated structural metadata contract chain is required.
* Existing `pypdf` is identified as the only dependency candidate.
* No new dependency is authorized.
* Candidate structural fields are explicitly bounded.
* Semantic document metadata is prohibited.
* Text, image, OCR, Evidence, Knowledge, and Prompt Candidate access remain prohibited.
* A dedicated execution contract is required.
* No real asset is present or processed.
* PR-021C is identified as the next documentation-only review.
* Only the PR-021B document is the intended repository change.
