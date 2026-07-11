# PR-021G - Controlled PDF Structural Metadata Result Contract Review

## Status

* Documentation-only result-contract review.
* PR-021F synthetic contract smoke flow is committed and synchronized.
* The base structural metadata contract exists.
* The structural metadata execution contract exists.
* Value-only contract-chain verification exists.
* No structural metadata result contract exists.
* No structural metadata parser implementation exists.
* No real or synthetic PDF is present.
* No PDF has been opened or inspected.
* No parser, OCR, rendering, image extraction, Evidence, Knowledge, or Prompt Candidate execution is authorized.

## Current checkpoint

* Branch: `phase-021-controlled-pdf-post-extraction-review`
* Branch HEAD before PR-021G: `165609b`
* `main`: `fbb0c99`
* `origin/main`: `fbb0c99`
* Phase 21 branch is synchronized with its remote branch.
* Working-tree tracked diff: empty.
* Cached diff: empty.
* Controlled sandbox directory exists and remains empty.
* Phase 20 real PDF target remains absent.

## Previous PR outcome

PR-021F introduced one value-only synthetic smoke-flow test.

The approved chain was:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfStructuralMetadataContract
-> ControlledPdfStructuralMetadataExecutionContract
```

PR-021F verified:

* fixture metadata authority
* structural metadata contract authority
* explicit execution authority
* bounded maximum inspected pages
* content extraction prohibition
* output-file creation prohibition
* Evidence prohibition

PR-021F did not introduce:

* `PdfReader`
* PDF creation
* parser execution
* structural metadata implementation
* structural metadata result values
* page count
* page dimensions
* page rotation
* encryption inspection
* persistent output

## Purpose

Define the exact value-only result contract required before any structural metadata parser implementation can be reviewed.

PR-021G determines:

* result value-object responsibilities
* page-detail value-object responsibilities
* result input and output fields
* document status vocabulary
* page status vocabulary
* status-specific consistency rules
* page-index and page-count rules
* bounded error behavior
* execution-contract consistency
* content and downstream prohibitions
* the safest next implementation step

PR-021G does not create source code or tests.

## Architectural position

The approved future chain is refined as:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfStructuralMetadataContract
-> ControlledPdfStructuralMetadataExecutionContract
-> ControlledPdfStructuralMetadataImplementation
-> ControlledPdfStructuralMetadataResultContract
```

Although the implementation appears before the result contract during runtime, the result contract must be designed and implemented before parser implementation work begins.

The safe development sequence is therefore:

```text
result-contract review
-> result-contract skeleton
-> parser implementation review
-> parser implementation skeleton
-> synthetic parser verification review
```

No parser implementation may be created before the result-contract skeleton is approved.

## Result-contract responsibility

`ControlledPdfStructuralMetadataResultContract` must:

* accept one approved structural metadata execution-contract result
* accept one immutable structural metadata result input
* validate fixture identity
* validate fixture path
* validate fixture type
* validate inspection mode
* validate maximum inspected-page limit
* validate document-level status
* validate page-detail items
* validate page indices
* validate dimensions
* validate rotations
* validate truncation behavior
* validate bounded errors
* preserve output-file prohibition
* preserve content-extraction prohibition
* preserve Evidence prohibition
* return a value-only immutable result

It must not:

* open a PDF
* call parser APIs
* create parser values
* normalize parser objects
* render pages
* extract text
* extract images
* run OCR
* create output files
* create Evidence or Knowledge

## Proposed source file

The approved proposed source path is:

```text
src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py
```

PR-021G does not create this file.

## Proposed test file

The approved proposed unit-test path is:

```text
tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py
```

PR-021G does not create this file.

## Page-detail value object

The result contract requires one immutable page-detail value object.

Approved name:

```text
ControlledPdfStructuralMetadataPageItem
```

Required fields:

```text
page_index: int
width_points: float
height_points: float
rotation_degrees: int
inspection_status: str
```

The value object must contain no parser object, page text, image data, annotation, semantic metadata, or raw exception.

## Page-detail statuses

Approved page-detail statuses:

```text
inspected
page_error
```

They must be represented by an immutable set:

```text
ALLOWED_PAGE_INSPECTION_STATUSES
```

## Inspected page-item rules

For:

```text
inspection_status = "inspected"
```

the page item must satisfy:

* `page_index >= 0`
* `width_points` is numeric
* `height_points` is numeric
* width is finite
* height is finite
* `width_points > 0`
* `height_points > 0`
* `rotation_degrees` is one of `0`, `90`, `180`, or `270`

Boolean values must not be accepted as dimensions even though Python booleans are integer subclasses.

No conversion to pixels is permitted.

Page dimensions are PDF points only.

## Page-error item rules

For:

```text
inspection_status = "page_error"
```

the page item must satisfy:

```text
page_index >= 0
width_points = 0
height_points = 0
rotation_degrees = 0
```

No page-level raw error message is included.

A page error only reports that one bounded page-detail slot could not be structurally inspected.

It does not authorize fallback processing.

## Page-index convention

Page indices remain zero-based.

The first page is:

```text
page_index = 0
```

Page details must represent a contiguous prefix.

For three page-detail items, valid indices are:

```text
0
1
2
```

The result contract must reject:

* negative indices
* duplicate indices
* non-contiguous indices
* out-of-order indices
* a first index other than zero
* indices greater than or equal to `page_count`

Arbitrary page selection remains outside Phase 21.

## Result-input value object

Approved name:

```text
ControlledPdfStructuralMetadataResultInput
```

Required fields:

```text
fixture_id: str
source_label: str
fixture_path: str
fixture_type: str
inspection_mode: str
inspection_status: str
encrypted: bool
page_count: int
inspected_page_count: int
page_details_truncated: bool
page_details: tuple[ControlledPdfStructuralMetadataPageItem, ...]
max_inspected_pages: int
inspection_error: str
evidence_allowed: bool
notes: str
```

The input must not include:

* page text
* text preview
* extracted text
* OCR text
* rendered pixels
* image bytes
* embedded images
* annotations
* form values
* attachments
* semantic document metadata
* raw parser objects
* stack traces
* Evidence or Knowledge values

## Result-contract output

Approved name:

```text
ControlledPdfStructuralMetadataResultContractResult
```

Required fields:

```text
allowed: bool
reason: str
fixture_id: str
source_label: str
fixture_path: str
fixture_type: str
inspection_mode: str
inspection_status: str
encrypted: bool
page_count: int
inspected_page_count: int
page_details_truncated: bool
page_details: tuple[ControlledPdfStructuralMetadataPageItem, ...]
max_inspected_pages: int
inspection_error: str
evidence_allowed: bool
notes: str
```

The successful result must always set:

```text
evidence_allowed = False
```

## Document inspection statuses

PR-021C originally approved:

```text
not_run
inspected
bounded
encrypted
unreadable
parser_unavailable
parser_error
blocked
```

PR-021G identifies that page-detail status `page_error` requires a coherent document-level state.

A result containing both successfully inspected pages and page errors cannot accurately use:

* `inspected`
* `bounded`
* a fatal parser-error status

PR-021G therefore adds:

```text
partial
```

The approved immutable status set becomes:

```text
not_run
inspected
bounded
partial
encrypted
unreadable
parser_unavailable
parser_error
blocked
```

This is an explicit refinement of PR-021C.

PR-021C remains unchanged in Git history.

## Successful and non-fatal statuses

The non-fatal statuses are:

```text
not_run
inspected
bounded
partial
```

Fatal or blocked statuses are:

```text
encrypted
unreadable
parser_unavailable
parser_error
blocked
```

## Meaning of inspected_page_count

`inspected_page_count` means the number of bounded page-detail slots that were attempted and represented in `page_details`.

It includes page items with:

```text
inspection_status = "inspected"
```

and:

```text
inspection_status = "page_error"
```

It is therefore not a count of successful pages only.

The contract must require:

```text
inspected_page_count = len(page_details)
```

A future separate field for successful-page count is not approved in Phase 21.

## Maximum inspected pages

The result input must contain:

```text
max_inspected_pages
```

It must exactly match:

```text
execution_contract_result.max_inspected_pages
```

It must satisfy:

```text
1 <= max_inspected_pages <= 10
```

The result contract must not accept a caller-provided value that differs from the execution authority.

## Page-count rules

`page_count` must:

* be an integer
* not be a boolean
* be greater than or equal to zero
* represent the parser-provided total number of pages
* remain bounded as one integer value
* not cause unbounded page-detail creation

For all non-fatal successful results:

```text
inspected_page_count <= page_count
inspected_page_count <= max_inspected_pages
```

For zero-page inspection:

```text
page_count = 0
inspected_page_count = 0
page_details = ()
```

## Page-detail count formula

For fully completed bounded structural inspection:

```text
expected_page_detail_count = min(page_count, max_inspected_pages)
```

For statuses `inspected` and `bounded`:

```text
inspected_page_count = expected_page_detail_count
len(page_details) = expected_page_detail_count
```

For `partial`, the result must still contain the full bounded prefix attempted:

```text
inspected_page_count = expected_page_detail_count
len(page_details) = expected_page_detail_count
```

At least one item must be `inspected`.

At least one item must be `page_error`.

If every attempted page fails, the result must use a fatal `parser_error` result with no page details rather than `partial`.

## Truncation rules

`page_details_truncated` refers only to bounded omission of page-detail values.

It does not mean:

* text truncation
* byte truncation
* image truncation
* semantic truncation

The required formula is:

```text
page_details_truncated = page_count > max_inspected_pages
```

This formula applies to:

* `inspected`
* `bounded`
* `partial`

Status-specific requirements remain:

### inspected

```text
page_count <= max_inspected_pages
page_details_truncated = False
```

### bounded

```text
page_count > max_inspected_pages
page_details_truncated = True
```

### partial

`page_details_truncated` may be `True` or `False` according to the same formula.

## not_run status

For:

```text
inspection_status = "not_run"
```

the result must require:

```text
encrypted = False
page_count = 0
inspected_page_count = 0
page_details_truncated = False
page_details = ()
inspection_error = ""
```

`not_run` does not authorize execution.

## inspected status

For:

```text
inspection_status = "inspected"
```

the result must require:

* `encrypted = False`
* `page_count >= 0`
* `page_count <= max_inspected_pages`
* `inspected_page_count = page_count`
* page-detail count equals `page_count`
* all page items use `inspection_status="inspected"`
* `page_details_truncated = False`
* `inspection_error = ""`

A zero-page PDF may use `inspected` with no page details.

## bounded status

For:

```text
inspection_status = "bounded"
```

the result must require:

* `encrypted = False`
* `page_count > max_inspected_pages`
* `inspected_page_count = max_inspected_pages`
* page-detail count equals `max_inspected_pages`
* all page items use `inspection_status="inspected"`
* `page_details_truncated = True`
* `inspection_error = ""`

`bounded` means the page-detail prefix reached its approved limit.

It does not imply a parser error.

## partial status

For:

```text
inspection_status = "partial"
```

the result must require:

* `encrypted = False`
* `page_count > 0`
* `inspected_page_count = min(page_count, max_inspected_pages)`
* page-detail count equals `inspected_page_count`
* at least one page item uses `inspection_status="inspected"`
* at least one page item uses `inspection_status="page_error"`
* page indices remain a contiguous prefix
* truncation flag follows `page_count > max_inspected_pages`
* `inspection_error` is a controlled non-empty message

Approved generic partial error:

```text
one or more pages could not be structurally inspected
```

No raw page-level exception is permitted.

## Fatal and blocked statuses

Fatal and blocked statuses:

```text
encrypted
unreadable
parser_unavailable
parser_error
blocked
```

All must require:

```text
page_count = 0
inspected_page_count = 0
page_details_truncated = False
page_details = ()
```

All must require a non-empty bounded `inspection_error`.

## Encryption rules

For:

```text
inspection_status = "encrypted"
```

the result must require:

```text
encrypted = True
```

Approved error:

```text
pdf is encrypted
```

For every other status:

```text
encrypted = False
```

The result contract must reject `encrypted=True` with any non-encrypted status.

Encrypted files must not be decrypted or inspected further.

## Unreadable status

For:

```text
inspection_status = "unreadable"
```

approved error:

```text
pdf file is unreadable
```

No filesystem exception or operating-system message may be exposed.

## Parser-unavailable status

For:

```text
inspection_status = "parser_unavailable"
```

approved error:

```text
pdf parser dependency is unavailable
```

The status does not authorize installation or dependency modification.

## Parser-error status

For:

```text
inspection_status = "parser_error"
```

approved error:

```text
pdf parser error
```

Raw exception strings and parser dumps remain prohibited.

## Blocked status

For:

```text
inspection_status = "blocked"
```

approved bounded errors may include:

```text
implementation safety checks failed
implementation request is required
```

The result contract may return its own blocked reasons for invalid values.

## Error-length boundary

Approved constant:

```text
MAX_INSPECTION_ERROR_CHARACTERS = 500
```

The result contract must reject:

* `inspection_error is None`
* an error longer than 500 characters
* non-empty errors for `not_run`, `inspected`, or `bounded`
* empty errors for fatal statuses
* an unexpected partial-status error

For `partial`, the initial skeleton should accept only the approved generic partial error.

## Source-label rule

`source_label` must:

* be a string
* contain at least one non-whitespace character
* remain a caller-supplied traceability value
* not be inferred from PDF content

## Notes rule

`notes` must not be `None`.

An empty string remains valid.

Notes must not be populated automatically from parser content.

## Fixture consistency

The result contract must compare its input against the execution-contract result.

It must reject:

* fixture ID mismatch
* fixture path mismatch
* fixture type mismatch
* inspection-mode mismatch
* maximum-inspected-pages mismatch
* Evidence-authority mismatch

The required fixture type remains:

```text
product_spec_pdf
```

The required inspection mode remains:

```text
structural_metadata_only
```

## Execution-contract preconditions

The result contract must block when:

* execution-contract result is missing or wrong type
* execution-contract result is not allowed
* `execution_allowed=False`
* `allow_content_extraction=True`
* `allow_output_file_creation=True`
* `evidence_allowed=True`
* permitted fields differ from the approved field set
* maximum inspected pages is outside its approved boundary

The result contract does not repair an invalid execution authority.

## Numeric boundary

Dimensions may be `int` or `float`, except boolean.

They must pass finite-number validation.

The future skeleton may use:

```text
math.isfinite
```

The contract must reject:

* NaN
* positive infinity
* negative infinity
* zero dimensions for an inspected page
* negative dimensions
* string dimensions
* boolean dimensions

No rounding or unit conversion is performed by the result contract.

## Rotation boundary

Approved rotations:

```text
0
90
180
270
```

The result contract validates normalized rotation values only.

Parser-specific normalization belongs to a future implementation layer.

The result contract must not normalize arbitrary values itself.

## Immutable collection boundary

`page_details` must be a tuple.

Lists and mutable collections must be blocked.

Each member must be:

```text
ControlledPdfStructuralMetadataPageItem
```

The result contract must not accept raw dictionaries or parser page objects.

## Content-extraction prohibition

The result input and output must not contain fields for:

* text
* text preview
* extracted text
* OCR
* images
* rendered pages
* annotations
* forms
* attachments
* links
* outlines
* XMP
* document title
* author
* subject
* keywords
* creator
* producer
* semantic classification

The result contract validates structural values only.

## Output-file prohibition

The result contract produces an in-memory immutable value only.

It must not write:

* JSON
* CSV
* text reports
* parser logs
* rendered images
* extracted assets
* temporary files
* Evidence artifacts
* Knowledge artifacts

## Evidence prohibition

The result input must require:

```text
evidence_allowed = False
```

The output must always set:

```text
evidence_allowed = False
```

The result contract must reject:

```text
evidence_allowed = True
```

Structural metadata output is not Evidence.

## No automatic fallback

No result status may automatically trigger:

* text extraction
* page rendering
* embedded-image extraction
* OCR
* image understanding
* Evidence construction
* Knowledge construction

This includes:

* `partial`
* `encrypted`
* `parser_error`
* `bounded`

The result contract ends after validation.

## Blocked-result behavior

A blocked result should preserve bounded input values where safe and available.

It must not:

* include raw parser objects
* expose stack traces
* infer missing values
* change Evidence authority to true
* create persistent output

The blocked result must always set:

```text
allowed = False
evidence_allowed = False
```

## Unit-test scope

The future result-contract unit tests must cover at least:

1. valid zero-page inspected result
2. valid inspected result
3. valid bounded result
4. valid partial result
5. valid encrypted result
6. invalid execution-contract result
7. fixture identity mismatch
8. maximum-page mismatch
9. negative page count
10. page-detail count mismatch
11. duplicate page index
12. non-contiguous page index
13. invalid page dimensions
14. NaN dimensions
15. invalid rotation
16. incorrect truncation flag
17. invalid partial result without mixed page statuses
18. invalid fatal result containing page details
19. oversized inspection error
20. Evidence authority enabled

The exact test count is not fixed by PR-021G.

Tests must remain value-only and parser-free.

## Recommended next PR

The next PR is:

```text
PR-021H - Controlled PDF Structural Metadata Result Contract Skeleton
```

PR-021H may introduce exactly:

```text
src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py
tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py
```

PR-021H must remain:

* parser-free
* filesystem-free
* PDF-free
* output-file-free
* Evidence-free
* Knowledge-free

## PR-021H permitted scope

PR-021H may implement:

* approved constants
* immutable page-detail value object
* immutable result-input value object
* immutable result-contract output
* value-only validation
* blocked-result helpers
* isolated result-contract unit tests

## PR-021H prohibited scope

PR-021H must not:

* create a parser implementation
* import `PdfReader`
* import `pypdf`
* create a PDF
* open a PDF
* inspect a path
* normalize parser values
* render pages
* extract text
* extract images
* run OCR
* create persistent output
* modify existing contracts unless a separate review identifies a defect
* modify Evidence or Knowledge workflows
* modify locked or SSOT documents

## Roadmap refinement

The Phase 21 sequence is refined after PR-021F:

1. PR-021G - Controlled PDF Structural Metadata Result Contract Review
2. PR-021H - Controlled PDF Structural Metadata Result Contract Skeleton
3. PR-021I - Controlled PDF Structural Metadata Implementation Review
4. PR-021J - Controlled PDF Structural Metadata Implementation Skeleton
5. PR-021K - Controlled PDF Structural Metadata Synthetic Parser Verification Review

Later execution, cleanup, closure, and phase-tag PRs require separate review and may extend beyond PR-021K.

This refinement supersedes the earlier provisional sequencing after PR-021F.

It does not alter already completed PRs.

## Allowed work in PR-021G

PR-021G may:

* define result-contract value objects
* define document and page statuses
* resolve page-error document-state ambiguity
* define validation rules
* refine the Phase 21 roadmap
* recommend PR-021H

## Prohibited work in PR-021G

PR-021G must not:

* create source code
* create tests
* create or open a PDF
* invoke parser APIs
* inspect metadata
* render pages
* extract text or images
* run OCR
* install dependencies
* modify the virtual environment
* create persistent output
* create Evidence or Knowledge
* modify locked or SSOT documents

## Git boundary

* Only the PR-021G documentation file may be introduced.
* PR-021A through PR-021F must remain unchanged.
* No source or test file may change.
* No real or synthetic asset may be staged or committed.
* Any unexpected tracked, staged, or untracked file is a hard stop.
* No merge or Phase 21 tag is authorized.

## Acceptance criteria

* PR-021G is documentation-only.
* The result contract is designed before parser implementation.
* Page-detail and result value objects are explicitly defined.
* Page indices remain zero-based and contiguous.
* Page dimensions are finite positive PDF-point values.
* Rotations are limited to `0`, `90`, `180`, and `270`.
* `partial` is added as an explicit document status.
* Status-specific page-count and error rules are defined.
* Maximum inspected pages must match execution authority.
* Inspection errors remain bounded to 500 characters.
* Content extraction remains prohibited.
* Output-file creation remains prohibited.
* Evidence and Knowledge remain prohibited.
* No automatic fallback is permitted.
* PR-021H is identified as the next parser-free result-contract skeleton.
* Only the PR-021G document is the intended repository change.
