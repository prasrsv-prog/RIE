# PR-021A - Controlled PDF Post-Extraction Boundary Review

## Status

* Documentation-only post-extraction boundary review.
* Phase 20 is closed, merged, pushed, and officially tagged.
* No PDF asset is currently present in the local sandbox.
* No post-extraction capability has been authorized.
* No OCR, page rendering, image extraction, Evidence, Knowledge, or Prompt Candidate workflow is active.

## Current checkpoint

* Branch: `phase-021-controlled-pdf-post-extraction-review`
* Branch base: `fbb0c99`
* `main`: `fbb0c99`
* `origin/main`: `fbb0c99`
* Official Phase 20 tag: `v0.20.0-rcis-controlled-real-asset-pdf-extraction-phase`
* Phase 20 tag target: `fbb0c99`
* Phase 21 branch has not yet been pushed.
* Working-tree tracked diff: empty.
* Cached diff: empty.
* Local real-asset sandbox directory remains empty.
* No real PDF is present.

## Purpose

Define the architectural boundary for any capability that may follow controlled PDF text extraction.

PR-021A answers only:

* what the Phase 20 `empty` extraction result means
* which possible post-extraction capabilities may be reviewed later
* which capabilities must remain separated
* which downstream activities remain prohibited
* what review gates are required before any implementation or execution

PR-021A does not implement or execute a post-extraction capability.

## Previous phase outcome

Phase 20 completed exactly one controlled real PDF text-extraction execution.

The bounded result was:

* extraction status: `empty`
* text length: `0`
* bounded text preview: empty
* extracted text included: `False`
* truncated: `False`
* extraction error: empty
* Evidence allowed: `False`

The local real PDF was subsequently removed through the approved cleanup gate.

The PDF:

* was never staged
* was never committed
* is no longer present in the sandbox
* must not be restored automatically
* must not be processed again without a new separately reviewed execution boundary

## Meaning of the empty result

The `empty` result establishes only that the approved text parser did not return extractable text through the bounded `text_only` flow.

It does not establish that:

* the PDF was blank
* the PDF contained no visible pages
* the PDF contained no images
* the PDF contained no useful information
* the PDF required OCR
* OCR would produce useful output
* page rendering is required
* embedded-image extraction is required
* product specifications can be inferred
* Evidence or Knowledge can be created

The empty result is parser output only.

It has no downstream authority.

## Core architectural rule

Post-extraction capabilities must not be treated as automatic fallbacks.

The following transition is prohibited:

```text
text extraction returned empty
-> automatically run OCR
-> automatically inspect images
-> automatically infer product information
-> automatically create Evidence or Knowledge
```

Every capability after text extraction requires:

1. a separate capability definition
2. a separate architecture review
3. a separate execution review
4. an explicit approved input
5. bounded output
6. cleanup and retention handling
7. closure review

An `empty` result does not bypass these gates.

## Capability separation

The following capabilities are architecturally distinct and must remain separate.

### 1. PDF structural metadata inspection

Potential structural metadata may include:

* page count
* encrypted state
* PDF format information exposed by the approved parser
* page dimensions
* page rotation
* presence of page objects
* bounded document properties

Structural metadata inspection must not:

* extract page text
* render pages
* extract embedded images
* run OCR
* interpret page content
* create product claims
* create Evidence or Knowledge

This capability may be considered for a future metadata-only review.

### 2. PDF page rendering

Page rendering means producing a visual representation of one or more PDF pages.

It is distinct from:

* text extraction
* embedded-image extraction
* OCR
* image understanding
* Evidence creation

A future page-rendering capability would require boundaries for:

* exact page selection
* maximum page count
* maximum resolution
* output format
* temporary output location
* retention and deletion
* prohibition on automatic AI interpretation
* prohibition on production or repository-wide scanning

Page rendering is not authorized by PR-021A.

### 3. Embedded-image extraction

Embedded-image extraction means extracting image objects contained inside a PDF.

It is not equivalent to rendering a complete page.

A future embedded-image capability would require boundaries for:

* exact PDF target
* maximum extracted image count
* allowed image formats
* maximum dimensions and byte size
* temporary output directory
* naming rules
* duplicate handling
* cleanup
* prohibition on automatic interpretation

Embedded-image extraction is not authorized by PR-021A.

### 4. OCR

OCR means deriving machine-readable text from rendered page pixels or image content.

OCR is a separate extraction capability and not a continuation of the existing `text_only` parser contract.

A future OCR capability would require review of:

* OCR dependency
* supported languages
* exact page limit
* exact character limit
* confidence handling
* bounded preview
* output retention
* error states
* deterministic behavior
* prohibition on treating OCR output as Evidence or Knowledge

OCR is not authorized by PR-021A.

### 5. Image understanding

Image understanding means interpreting visual content such as:

* product appearance
* labels
* tables
* diagrams
* specifications
* logos
* layout relationships
* visual claims

Image understanding is distinct from page rendering, embedded-image extraction, and OCR.

It introduces inference and must remain outside any low-level extraction contract.

Image understanding is not authorized by PR-021A.

### 6. Evidence creation

Evidence creation is a downstream domain operation.

Neither structural metadata, rendered pages, extracted images, nor OCR text automatically becomes Evidence.

Evidence creation requires its own reviewed workflow and must preserve:

* traceability
* reproducibility
* source identity
* extraction method
* exact boundaries
* uncertainty
* validation state

Evidence creation is not authorized by PR-021A.

### 7. Knowledge creation

Knowledge is inferred, normalized, composed, or interpreted from Evidence.

Raw parser output, OCR output, rendered pages, and extracted images are not Knowledge.

Knowledge creation is not authorized by PR-021A.

## Candidate post-extraction paths

PR-021A recognizes the following review candidates.

### Candidate A - Stop after text extraction

No additional PDF-processing capability is opened.

This remains the default state until another capability is explicitly approved.

Advantages:

* lowest architectural risk
* no new dependencies
* no additional asset exposure
* no temporary output
* no inference risk

This candidate remains valid.

### Candidate B - Structural metadata-only capability

Review a narrowly bounded capability that inspects only approved structural PDF metadata.

Potential advantages:

* lower risk than page rendering or OCR
* no page pixel output
* no content interpretation
* useful for deciding whether a later capability review is technically appropriate

This candidate may be reviewed next but is not yet selected for execution.

### Candidate C - Controlled page-rendering capability

Review a capability that renders only explicitly selected pages to temporary image outputs.

Potential advantages:

* establishes a controlled visual representation layer
* could support later separately reviewed OCR or image workflows

Risks:

* creates temporary visual assets
* requires new dependency and output-retention boundaries
* may expose page content
* must not automatically invoke OCR or AI

This candidate requires a separate architecture review.

### Candidate D - Controlled embedded-image extraction capability

Review a capability that extracts bounded embedded image objects.

Potential advantages:

* may preserve original embedded image quality
* avoids rendering complete pages when the PDF contains discrete images

Risks:

* PDF object structure varies
* extracted assets may lack clear page context
* duplicate or transformed image objects may occur
* requires strict temporary-output cleanup

This candidate requires a separate architecture review.

### Candidate E - Controlled OCR capability

Review a capability that performs bounded OCR on explicitly approved rendered input.

Potential advantages:

* may recover text unavailable through direct PDF parsing

Risks:

* nondeterministic or confidence-sensitive output
* language and layout limitations
* possible text errors
* new dependency and environment changes
* risk of treating OCR output as factual Evidence

This candidate requires page-input and OCR-specific reviews and must not be selected automatically.

## Decision

PR-021A establishes that no post-extraction capability is automatically authorized.

The safest next review candidate is:

```text
Candidate B - Structural metadata-only capability
```

This selection is for review sequencing only.

It does not authorize metadata execution.

Structural metadata review is selected first because it:

* introduces less exposure than page rendering
* creates no page images
* does not require OCR
* does not require AI
* can remain bounded to one explicit PDF
* can help determine whether a visual-processing capability should later be reviewed
* preserves separation between extraction and inference

## Recommended next PR

The recommended next PR is:

```text
PR-021B - Controlled PDF Structural Metadata Capability Review
```

PR-021B must remain documentation-only and review-first.

It should determine:

* whether existing contracts already support the required metadata
* which structural fields are permitted
* which structural fields are prohibited
* whether a new contract is necessary
* whether an existing dependency is sufficient
* maximum page and property boundaries
* bounded terminal output
* no asset-output files
* no PDF content extraction
* no OCR
* no image rendering
* no Evidence or Knowledge creation

PR-021B must not create an implementation.

## Allowed work in PR-021A

PR-021A may:

* document the post-extraction boundary
* classify candidate capabilities
* preserve separation between extraction and downstream workflows
* recommend the next documentation review

## Prohibited work in PR-021A

PR-021A must not:

* restore or place a PDF
* open or inspect PDF content
* execute the existing parser
* run structural metadata inspection
* render PDF pages
* extract embedded images
* use OCR
* use AI or image understanding
* install a dependency
* alter the virtual environment
* modify source code
* modify tests
* create output directories or extracted assets
* create Evidence
* create Evidence Candidates
* create Knowledge
* create Product Knowledge
* create Official Knowledge
* create Prompt Candidates
* create Final Prompts
* modify locked or SSOT documents

## Real-asset boundary

No real asset is required for PR-021A.

The local sandbox state must remain:

* directory may remain present
* exact Phase 20 PDF target remains absent
* sandbox item count remains zero
* no new PDF, image, or extraction output is placed
* no production source path is requested or recorded

A future real-asset placement requires a separately reviewed placement PR.

## Dependency boundary

PR-021A does not authorize:

* new PDF libraries
* page-rendering libraries
* OCR libraries
* image-processing libraries
* system packages
* virtual-environment changes
* lock-file changes
* project metadata changes

Dependency review must occur before dependency synchronization or execution.

## Output boundary

PR-021A creates only this documentation file.

It must not create:

* rendered page images
* extracted image objects
* OCR text
* metadata JSON
* parser logs
* extraction reports generated by code
* temporary scripts
* repository fixtures
* production outputs

## Git boundary

* Only the PR-021A documentation file may be staged and committed.
* The Phase 21 branch must remain based on `fbb0c99`.
* No real asset may be staged or committed.
* No source code or test file may be changed.
* Any unexpected tracked change is a hard stop.
* The branch must be pushed only after document review and commit approval.
* No merge or Phase 21 tag is authorized at this stage.

## Downstream boundary

PR-021A does not authorize:

* automatic capability fallback
* OCR after an empty parser result
* page rendering after an empty parser result
* image extraction after an empty parser result
* parser output to Evidence conversion
* OCR output to Evidence conversion
* image output to Knowledge conversion
* product specification inference
* product claim generation
* creative prompt generation

Any downstream capability requires its own explicit architecture boundary.

## Phase 21 provisional roadmap

The provisional Phase 21 roadmap is:

1. PR-021A - Controlled PDF Post-Extraction Boundary Review
2. PR-021B - Controlled PDF Structural Metadata Capability Review
3. PR-021C - Controlled PDF Structural Metadata Contract Review
4. PR-021D - Controlled PDF Structural Metadata Contract Skeleton
5. PR-021E - Controlled PDF Structural Metadata Synthetic Verification Review
6. PR-021F - Controlled PDF Structural Metadata Synthetic Verification
7. PR-021G - Controlled PDF Structural Metadata Real-Asset Execution Review
8. PR-021H - Controlled PDF Structural Metadata Real-Asset Execution
9. PR-021I - Controlled PDF Structural Metadata Cleanup Review
10. PR-021J - Controlled PDF Structural Metadata Cleanup Execution
11. PR-021K - Controlled PDF Post-Extraction Phase Closure Review

This roadmap is provisional.

Later PR reviews may reduce or reorganize it, but must not combine review, implementation, real-asset execution, cleanup, and closure into a single uncontrolled step.

## Acceptance criteria

* PR-021A is documentation-only.
* Phase 20 remains closed and unchanged.
* The Phase 20 PDF remains absent.
* No post-extraction capability is executed.
* The `empty` result is not reinterpreted as authorization.
* Structural metadata, page rendering, embedded-image extraction, OCR, image understanding, Evidence, and Knowledge are treated as separate capabilities.
* Automatic fallback from empty extraction to OCR or image processing is prohibited.
* Structural metadata-only review is selected as the safest next review candidate.
* PR-021B is identified as the next documentation-only review.
* No dependency, source code, tests, virtual environment, real assets, or locked documents are changed.
* Only the PR-021A document is the intended repository change.
