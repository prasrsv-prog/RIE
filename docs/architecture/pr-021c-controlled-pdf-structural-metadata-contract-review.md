# PR-021C - Controlled PDF Structural Metadata Contract Review

## Status

* Documentation-only contract review.
* PR-021A and PR-021B are committed and synchronized on the Phase 21 branch.
* No structural metadata contract has been implemented.
* No PDF asset is present in the controlled sandbox.
* No PDF has been opened or inspected.
* No source code, tests, dependencies, or virtual environment changes are authorized.
* No text extraction, page rendering, embedded-image extraction, OCR, Evidence, Knowledge, or Prompt Candidate workflow is authorized.

## Current checkpoint

* Branch: `phase-021-controlled-pdf-post-extraction-review`
* Branch HEAD before PR-021C: `7c5a2fd`
* `main`: `fbb0c99`
* `origin/main`: `fbb0c99`
* Phase 21 branch is synchronized with its remote branch.
* Working-tree tracked diff: empty.
* Cached diff: empty.
* Controlled real-asset sandbox directory exists and remains empty.
* The Phase 20 real PDF target remains absent.

## Purpose

Define the exact contract responsibilities and value boundaries for a future controlled PDF structural metadata capability.

PR-021C defines:

* the dedicated capability chain
* class responsibilities
* exact contract and result fields
* inspection mode
* permitted metadata fields
* prohibited content fields
* page-index convention
* page-detail boundary
* status vocabulary
* execution authority
* error handling
* no-content guarantees
* no-Evidence guarantees

PR-021C does not create source code or tests.

## Architectural basis

PR-021B established that:

* `ControlledRealAssetFixtureContract` remains the upstream fixture authority
* `allowed_for_metadata=True` is required
* the existing `pypdf` dependency is the only approved dependency candidate
* text-extraction contracts must not be generalized
* structural metadata requires a separate contract chain
* no new dependency is currently justified

The structural metadata chain must therefore remain isolated from:

* `ControlledPdfTextExtractionContract`
* `ControlledPdfTextExtractionExecutionContract`
* `ControlledPdfTextExtractionImplementation`
* `ControlledPdfTextExtractionResultContract`

## Approved provisional chain

The proposed class chain is:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfStructuralMetadataContract
-> ControlledPdfStructuralMetadataExecutionContract
-> ControlledPdfStructuralMetadataImplementation
-> ControlledPdfStructuralMetadataResultContract
```

These names are approved for future implementation planning.

PR-021C authorizes names and responsibilities only.

It does not authorize source creation.

## Single-responsibility boundary

Each layer has one responsibility.

### ControlledRealAssetFixtureContract

Responsibilities:

* validate fixture identity
* validate fixture path value
* validate supported fixture type
* require metadata access authority
* prohibit Evidence authority
* prohibit duplicate fixtures

It must not:

* authorize execution
* define PDF structural fields
* inspect a file
* expose parser results
* create Evidence

### ControlledPdfStructuralMetadataContract

Responsibilities:

* accept an allowed fixture-contract result
* select exactly one fixture
* require fixture type `product_spec_pdf`
* require inspection mode `structural_metadata_only`
* define the permitted structural field set
* prohibit content-oriented fields
* preserve `evidence_allowed=False`

It must not:

* authorize execution
* open the PDF
* define parser output values
* create output files
* create Evidence

### ControlledPdfStructuralMetadataExecutionContract

Responsibilities:

* accept an allowed structural metadata contract result
* require explicit execution approval
* define the maximum number of detailed pages
* require output-file creation to remain disabled
* require content extraction to remain disabled
* require Evidence creation to remain disabled
* preserve exact fixture identity and inspection mode

It must not:

* open the PDF
* inspect metadata
* render pages
* extract text
* create result objects from parser data

### ControlledPdfStructuralMetadataImplementation

Responsibilities:

* validate an approved implementation request
* perform only the approved structural inspection
* return bounded values to the result contract
* map parser failures to approved bounded statuses
* avoid persistent output

It must not:

* extract text
* render pages
* extract images
* inspect semantic document metadata
* invoke OCR
* create Evidence or Knowledge
* write output files

### ControlledPdfStructuralMetadataResultContract

Responsibilities:

* validate implementation result values
* validate field and fixture consistency
* enforce page-detail limits
* enforce status-specific rules
* enforce bounded errors
* prohibit content values
* return a value-only result

It must not:

* execute inspection
* open files
* infer metadata
* create Evidence
* create persistent artifacts

## Inspection mode

The only approved inspection-mode value is:

```text
structural_metadata_only
```

The mode must be represented by a constant:

```text
STRUCTURAL_METADATA_ONLY_MODE = "structural_metadata_only"
```

Any other mode must be blocked.

The mode must not be extended to include:

* text
* OCR
* images
* annotations
* forms
* attachments
* semantic metadata
* Evidence

## Fixture boundary

The capability accepts only:

```text
fixture_type = "product_spec_pdf"
```

The selected fixture must:

* exist exactly once in the fixture-contract result
* have a non-empty fixture ID
* have a non-empty fixture path
* have `allowed_for_metadata=True`
* have `allowed_for_pdf_text_extraction=False`
* have `allowed_for_image_metadata=False`
* have `allowed_for_evidence=False`

A fixture flag does not authorize execution by itself.

## Permitted structural fields

The approved structural field identifiers are:

```text
encrypted
page_count
page_width_points
page_height_points
page_rotation_degrees
```

The structural metadata contract must use a fixed tuple or immutable set of approved field identifiers.

No caller-defined arbitrary field names are permitted.

## Document-level result fields

A future result may contain:

* `allowed`
* `reason`
* `fixture_id`
* `source_label`
* `fixture_path`
* `fixture_type`
* `inspection_mode`
* `inspection_status`
* `encrypted`
* `page_count`
* `inspected_page_count`
* `page_details_truncated`
* `page_details`
* `inspection_error`
* `evidence_allowed`
* `notes`

No raw parser object may be included.

## Page-detail result item

A dedicated immutable page-detail value object is required.

Proposed name:

```text
ControlledPdfStructuralMetadataPageItem
```

Required fields:

* `page_index`
* `width_points`
* `height_points`
* `rotation_degrees`
* `inspection_status`

The item must not include:

* page text
* page labels
* images
* annotations
* links
* form values
* raw PDF objects
* parser-specific dictionaries
* semantic interpretation

## Page-index convention

Page indices must be zero-based.

The first page is:

```text
page_index = 0
```

The contract must reject:

* negative page indices
* duplicate page indices
* indices greater than or equal to reported `page_count`
* non-contiguous indices in an inspected prefix

The detailed page sequence must represent a bounded prefix beginning at page index `0`.

Arbitrary page selection is not part of Phase 21.

## Page-detail execution limit

The execution contract must require:

```text
max_inspected_pages
```

The approved Phase 21 upper limit is:

```text
MAX_INSPECTED_PAGES_LIMIT = 10
```

Execution must be blocked when:

* `max_inspected_pages <= 0`
* `max_inspected_pages > 10`

This limit applies to detailed page dimensions and rotation.

It does not permit page rendering or text extraction.

## Page-count handling

The implementation may report the parser-provided document page count as one non-negative integer.

The implementation must not create one result item for every page when the PDF exceeds `max_inspected_pages`.

Detailed inspection count must be:

```text
min(page_count, max_inspected_pages)
```

When:

```text
page_count > max_inspected_pages
```

the result must set:

```text
page_details_truncated = True
```

When:

```text
page_count <= max_inspected_pages
```

the result must set:

```text
page_details_truncated = False
```

## Page dimensions

Page dimensions may be represented as numeric point values:

* `width_points`
* `height_points`

They must:

* be finite numeric values
* be greater than zero for successfully inspected pages
* not contain raw parser objects
* not be converted to pixels
* not imply rendering resolution
* not be interpreted as product dimensions

The contract must reject NaN and infinite values.

## Page rotation

Page rotation must be represented as a normalized integer:

```text
0
90
180
270
```

A parser-specific rotation value must be normalized before result validation.

Any unsupported normalized rotation value must produce a page inspection error or blocked result according to the future implementation review.

Rotation must not be interpreted semantically.

## Page inspection status

Each page-detail item must use one of:

```text
inspected
page_error
```

For `inspected`:

* width must be greater than zero
* height must be greater than zero
* rotation must be one of `0`, `90`, `180`, or `270`

For `page_error`:

* width must be `0`
* height must be `0`
* rotation must be `0`

Phase 21 does not authorize raw per-page error messages.

## Document inspection statuses

The approved result statuses are:

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

These values must be represented by an immutable set.

## Successful statuses

Successful or non-error statuses are:

```text
not_run
inspected
bounded
```

### not_run

Requires:

* `page_count = 0`
* `inspected_page_count = 0`
* empty page details
* `page_details_truncated = False`
* empty inspection error

### inspected

Requires:

* inspection completed
* `page_count >= 0`
* `inspected_page_count = page_count`
* `page_details_truncated = False`
* empty inspection error
* page-detail count equals `inspected_page_count`

For a zero-page PDF, an inspected result may contain:

* `page_count = 0`
* `inspected_page_count = 0`
* empty page details

### bounded

Requires:

* `page_count > max_inspected_pages`
* `inspected_page_count = max_inspected_pages`
* page-detail count equals `max_inspected_pages`
* `page_details_truncated = True`
* empty inspection error

The term `bounded` means detailed page inspection was intentionally limited.

It does not mean content truncation.

## Error statuses

Error statuses are:

```text
encrypted
unreadable
parser_unavailable
parser_error
blocked
```

All error statuses require:

* `page_count = 0`
* `inspected_page_count = 0`
* empty page details
* `page_details_truncated = False`
* non-empty bounded inspection error

No raw exception text or stack trace is permitted.

## Error boundary

The result must include:

```text
inspection_error
```

The approved limit is:

```text
MAX_INSPECTION_ERROR_CHARACTERS = 500
```

The result contract must reject errors longer than 500 characters.

Future implementation must use controlled error constants such as:

```text
pdf parser dependency is unavailable
pdf file is unreadable
pdf parser error
pdf is encrypted
implementation safety checks failed
implementation request is required
```

Filesystem details, raw parser dumps, and stack traces must not be exposed.

## Encryption handling

The capability may report:

```text
encrypted = True
```

when the parser identifies the PDF as encrypted.

Encrypted PDFs must not be decrypted, password-guessed, or further inspected.

For status `encrypted`:

* page count must remain zero
* page details must remain empty
* inspection error must be the approved bounded encrypted error
* no further capability may run automatically

For successful unencrypted inspection:

```text
encrypted = False
```

## Structural metadata contract result

Proposed immutable result name:

```text
ControlledPdfStructuralMetadataContractResult
```

Required fields:

* `allowed`
* `reason`
* `fixture_id`
* `fixture_path`
* `fixture_type`
* `inspection_mode`
* `permitted_fields`
* `evidence_allowed`
* `notes`

The successful result must always set:

```text
evidence_allowed = False
```

## Structural metadata execution contract result

Proposed immutable result name:

```text
ControlledPdfStructuralMetadataExecutionContractResult
```

Required fields:

* `allowed`
* `reason`
* `fixture_id`
* `fixture_path`
* `fixture_type`
* `inspection_mode`
* `execution_allowed`
* `permitted_fields`
* `max_inspected_pages`
* `allow_content_extraction`
* `allow_output_file_creation`
* `evidence_allowed`
* `notes`

Successful execution authority must require:

```text
execution_allowed = True
allow_content_extraction = False
allow_output_file_creation = False
evidence_allowed = False
```

## Execution parameters

The future execution contract should accept:

* structural metadata contract result
* `allow_execution`
* `max_inspected_pages`
* `allow_content_extraction`
* `allow_output_file_creation`
* `allow_evidence_creation`
* `notes`

The following values must be blocked:

```text
allow_execution = False
allow_content_extraction = True
allow_output_file_creation = True
allow_evidence_creation = True
```

## Result input

Proposed immutable input name:

```text
ControlledPdfStructuralMetadataResultInput
```

Required fields:

* `fixture_id`
* `source_label`
* `fixture_path`
* `fixture_type`
* `inspection_mode`
* `inspection_status`
* `encrypted`
* `page_count`
* `inspected_page_count`
* `page_details_truncated`
* `page_details`
* `max_inspected_pages`
* `inspection_error`
* `evidence_allowed`
* `notes`

The result input must not include:

* text
* text preview
* extracted text
* images
* rendered pages
* semantic metadata
* raw parser objects

## Result contract output

Proposed immutable output name:

```text
ControlledPdfStructuralMetadataResultContractResult
```

The output fields should match the validated result input, plus:

* `allowed`
* `reason`

The output must always set:

```text
evidence_allowed = False
```

## Result consistency rules

The result contract must reject:

* fixture identity mismatch
* fixture path mismatch
* fixture type mismatch
* inspection mode mismatch
* maximum-page mismatch
* unsupported status
* negative page count
* negative inspected-page count
* inspected-page count greater than page count
* inspected-page count greater than maximum
* page-detail count mismatch
* duplicate page indices
* non-contiguous page indices
* invalid page dimensions
* invalid rotations
* incorrect truncation flag
* semantic or content-oriented values
* Evidence authority
* missing notes value
* oversized inspection error

## Content-extraction prohibition

The structural metadata contracts must explicitly preserve:

```text
allow_content_extraction = False
```

Content extraction includes:

* page text
* OCR text
* rendered pixels
* embedded images
* annotations
* attachments
* form values
* semantic document metadata

Structural metadata execution must be blocked if content extraction is enabled.

## Output-file prohibition

The execution contract must preserve:

```text
allow_output_file_creation = False
```

The capability must not create:

* JSON
* CSV
* text reports
* rendered pages
* extracted images
* parser dumps
* temporary scripts
* Evidence artifacts
* Knowledge artifacts

Persistent output requires a later independent review.

## Evidence prohibition

All structural metadata layers must preserve:

```text
evidence_allowed = False
```

Structural metadata output is not Evidence.

The contracts must block:

```text
allow_evidence_creation = True
```

No automatic conversion to Evidence, Knowledge, Product Knowledge, Official Knowledge, or Prompt Candidates is permitted.

## No automatic fallback

No structural metadata result may automatically trigger:

* text extraction
* page rendering
* image extraction
* OCR
* image understanding
* Evidence creation
* Knowledge creation

Status `bounded`, `encrypted`, or `parser_error` does not authorize another capability.

## Parser boundary

The future implementation may use the existing public `pypdf` dependency.

It must not depend on:

* private parser attributes
* undocumented internal objects
* raw object dumps
* repository-wide scans
* production paths
* automatic dependency installation

The exact parser API calls must be reviewed before implementation.

## Proposed source files

Future implementation planning may use:

```text
src/rie/ingestion/controlled_pdf_structural_metadata_contract.py
src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py
src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py
src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py
```

PR-021C does not create these files.

## Proposed test files

Future isolated tests may use:

```text
tests/ingestion/test_controlled_pdf_structural_metadata_contract.py
tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py
tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py
tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py
```

Synthetic verification tests must be reviewed separately.

PR-021C does not create tests.

## Recommended next PR

The next PR is:

```text
PR-021D - Controlled PDF Structural Metadata Contract Skeleton
```

PR-021D may implement only the value-only contract layers approved by this review.

The safest initial PR-021D scope is:

* structural metadata base contract
* structural metadata execution contract
* their unit tests

Implementation and parser access should remain deferred.

The result contract and parser implementation may be split into later PRs if review shows that combining them would weaken reviewability.

## PR-021D permitted scope

Subject to separate execution approval, PR-021D may create:

* immutable contract input and result value objects
* structural metadata base contract
* execution contract
* isolated contract tests
* constants approved in PR-021C

PR-021D must remain parser-free.

## PR-021D prohibited scope

PR-021D must not:

* import `PdfReader`
* open a PDF
* create an implementation class
* create parser result values
* place a real asset
* create synthetic PDFs
* modify text-extraction contracts
* modify Evidence workflows
* create persistent output
* run OCR or image processing
* modify locked or SSOT documents

## Git boundary

* Only the PR-021C documentation file may be introduced.
* PR-021A and PR-021B must remain unchanged.
* No source code or tests may change.
* No real asset may be staged or committed.
* Any unexpected tracked or staged file is a hard stop.
* No merge or Phase 21 tag is authorized.

## Acceptance criteria

* PR-021C is documentation-only.
* The structural metadata chain remains separate from text extraction.
* Class responsibilities are explicitly separated.
* The inspection mode is fixed to `structural_metadata_only`.
* Fixture type is fixed to `product_spec_pdf`.
* Permitted structural fields are explicitly defined.
* Semantic and content-oriented metadata remain prohibited.
* Page indices are zero-based.
* Detailed page inspection is bounded to a maximum of 10 pages.
* Document and page statuses are explicitly defined.
* Errors are bounded to 500 characters.
* Output-file creation remains prohibited.
* Content extraction remains prohibited.
* Evidence creation remains prohibited.
* No automatic fallback is permitted.
* Exact proposed source and test paths are documented.
* PR-021D is identified as the next contract-skeleton step.
* Only the PR-021C document is the intended repository change.
