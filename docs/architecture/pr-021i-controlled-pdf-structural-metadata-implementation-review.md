# PR-021I - Controlled PDF Structural Metadata Implementation Review

## Status

* Documentation-only parser implementation review.
* PR-021H result-contract skeleton is committed and synchronized.
* The structural metadata capability contract exists.
* The structural metadata execution contract exists.
* The structural metadata result contract exists.
* Value-only contract tests and smoke-flow tests exist.
* No structural metadata parser implementation exists.
* No real or synthetic PDF is present.
* No PDF has been opened during PR-021I.
* No parser execution, rendering, text extraction, image extraction, OCR, Evidence, Knowledge, or Prompt Candidate execution is authorized by this review.

## Current checkpoint

* Branch: `phase-021-controlled-pdf-post-extraction-review`
* Branch HEAD before PR-021I: `021e8f3`
* `main`: `fbb0c99`
* `origin/main`: `fbb0c99`
* Phase 21 branch is synchronized with its remote branch.
* Working tree is clean.
* Cached diff is empty.
* Controlled sandbox directory exists and remains empty.
* Phase 20 real PDF target remains absent.

## Previous PR outcome

PR-021H introduced:

```text
src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py
tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py
```

It introduced immutable values for:

* page-detail results
* parser result input
* result-contract output

It also introduced validation for:

* zero-based contiguous page indices
* positive finite PDF-point dimensions
* normalized rotations
* bounded page inspection
* partial page errors
* fatal parser states
* bounded error messages
* Evidence prohibition

PR-021H did not:

* import `pypdf`
* import `PdfReader`
* open a PDF
* create a PDF
* inspect filesystem paths
* create output files
* invoke downstream workflows

## Purpose

Define the exact parser implementation boundary required before structural PDF metadata inspection code is introduced.

PR-021I determines:

* the locally available `pypdf` public API
* the implementation request contract
* implementation preconditions
* the permitted parser calls
* encryption handling
* bounded page access
* page-dimension conversion
* rotation normalization
* per-page error behavior
* document-level status mapping
* parser exception mapping
* result-contract integration
* test boundaries
* the exact scope of PR-021J

PR-021I does not create implementation source code or tests.

## Local parser verification

Read-only environment introspection verified:

```text
pypdf version: 6.14.2
PdfReader import: pypdf._reader.PdfReader
```

The locally installed `PdfReader` accepts:

```text
stream: str | IO | pathlib.Path
strict: bool = False
password: str | bytes | None = None
```

The following public properties were verified:

```text
PdfReader.pages
PdfReader.is_encrypted
PageObject.mediabox
PageObject.rotation
```

The following export is not available from the top-level package:

```text
pypdf.RectangleObject
```

PR-021J must therefore not use:

```python
from pypdf import RectangleObject
```

The implementation must access page dimensions through:

```python
page.mediabox.width
page.mediabox.height
```

No dependency installation, upgrade, or version change is required.

The implementation must not hardcode an exact `pypdf` version check.

## Approved runtime chain

The approved runtime chain is:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfStructuralMetadataContract
-> ControlledPdfStructuralMetadataExecutionContract
-> ControlledPdfStructuralMetadataImplementation
-> ControlledPdfStructuralMetadataResultContract
```

The implementation must not bypass:

* fixture authority
* structural metadata authority
* explicit execution authority
* result-contract validation

## Recommended next implementation PR

PR-021J - Controlled PDF Structural Metadata Implementation

PR-021J is the parser implementation skeleton governed by this review.
## Proposed implementation source

PR-021J may introduce:

```text
src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py
```

No other source file is approved for modification.

## Proposed implementation tests

PR-021J may introduce:

```text
tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py
```

No existing test file is approved for modification.

## Implementation request value

The implementation requires one immutable request value.

Approved name:

```text
ControlledPdfStructuralMetadataImplementationRequest
```

Approved fields:

```text
execution_contract_result:
    ControlledPdfStructuralMetadataExecutionContractResult

source_label: str
allow_implementation_execution: bool
notes: str
```

The request must be a frozen dataclass.

The request must not contain:

* a parser object
* PDF bytes
* a file handle
* a page object
* a custom path
* a second fixture path
* a password
* text-extraction settings
* rendering settings
* OCR settings
* output-file paths
* Evidence settings
* Knowledge settings

The only PDF path used by the implementation must come from:

```text
execution_contract_result.fixture_path
```

## Implementation entry point

Approved class:

```text
ControlledPdfStructuralMetadataImplementation
```

Approved entry point:

```text
ControlledPdfStructuralMetadataImplementation.execute(request)
```

Approved return type:

```text
ControlledPdfStructuralMetadataResultContractResult
```

The implementation must not expose raw parser values.

## Parser import boundary

The implementation may use:

```python
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
```

This import boundary supports the approved status:

```text
parser_unavailable
```

PR-021J must not import:

* `RectangleObject`
* `PageObject`
* private `pypdf` modules
* `pypdf._reader`
* `pypdf._page`
* PDF rendering dependencies
* OCR dependencies
* image-processing dependencies

The implementation may rely only on the verified public `PdfReader` interface.

## Parser construction

The approved reader construction is:

```python
PdfReader(fixture_path)
```

where:

```text
fixture_path =
    request.execution_contract_result.fixture_path
```

PR-021J must not:

* replace the path
* infer a path
* search for a PDF
* resolve alternative paths
* scan directories
* use recursive discovery
* open a production asset
* accept a caller-supplied file handle

No `strict` override is required.

No password may be supplied.

## Filesystem boundary

The implementation may allow `PdfReader` itself to open the approved fixture path.

It must not separately call:

```text
Path.exists
Path.resolve
Path.read_bytes
Path.read_text
open
os.path.exists
glob
rglob
walk
```

There must be one controlled parser access point only:

```python
PdfReader(fixture_path)
```

A missing or inaccessible path is mapped through controlled parser error handling.

## Implementation preconditions

Before constructing `PdfReader`, the implementation must verify:

1. request is a `ControlledPdfStructuralMetadataImplementationRequest`
2. implementation execution is explicitly approved
3. execution-contract result has the correct type
4. execution-contract result is allowed
5. execution-contract result has `execution_allowed=True`
6. inspection mode is `structural_metadata_only`
7. fixture type is `product_spec_pdf`
8. permitted fields exactly match the approved immutable tuple
9. `allow_content_extraction=False`
10. `allow_output_file_creation=False`
11. `evidence_allowed=False`
12. maximum inspected pages is within `1..10`
13. fixture ID is non-empty
14. fixture path is non-empty
15. source label is a non-empty string
16. notes is a string

Parser construction must not occur when any precondition fails.

## Explicit implementation authority

The request must contain:

```text
allow_implementation_execution
```

The implementation must require:

```text
allow_implementation_execution = True
```

When false, the implementation must return:

```text
inspection_status = "blocked"
inspection_error = "implementation request is required"
allowed = False
evidence_allowed = False
```

Fixture metadata authority and execution-contract authority do not automatically authorize the implementation call.

## Safety-check failure

Invalid or expanded execution authority must return:

```text
inspection_status = "blocked"
inspection_error = "implementation safety checks failed"
allowed = False
evidence_allowed = False
```

This includes:

* invalid request type
* invalid execution-contract result
* disallowed execution contract
* content extraction enabled
* output creation enabled
* Evidence enabled
* unsupported fixture type
* unsupported inspection mode
* unsupported permitted fields
* invalid page limit

No parser call may occur after a safety-check failure.

## Result-contract integration

For parser outcomes produced after valid implementation preconditions, the implementation must:

1. build one `ControlledPdfStructuralMetadataResultInput`
2. call `ControlledPdfStructuralMetadataResultContract.evaluate`
3. return its immutable result

The implementation must not return:

* raw dictionaries
* parser pages
* raw exceptions
* mutable lists
* unvalidated parser output

The result contract remains the final authority for structural metadata result values.

## Pre-parser blocked result

When the request or execution authority is too invalid to construct a coherent result input, the implementation may construct a controlled blocked:

```text
ControlledPdfStructuralMetadataResultContractResult
```

directly.

That direct blocked result must contain:

```text
allowed = False
inspection_status = "blocked"
encrypted = False
page_count = 0
inspected_page_count = 0
page_details_truncated = False
page_details = ()
evidence_allowed = False
```

The direct path is permitted only before parser execution.

All valid parser outcomes must pass through the result contract.

## Permitted parser calls

After all safety checks pass, PR-021J may access only:

```python
reader = PdfReader(fixture_path)
reader.is_encrypted
len(reader.pages)
reader.pages[index]
page.mediabox
page.mediabox.width
page.mediabox.height
page.rotation
```

No other parser property or method is approved.

## Prohibited parser access

PR-021J must not access:

```text
reader.metadata
page.extract_text
page.images
page.annotations
page.get_contents
page.inline_images
reader.attachments
reader.outline
reader.xmp_metadata
reader.named_destinations
```

It must not access:

* document title
* author
* subject
* keywords
* creator
* producer
* forms
* links
* annotations
* attachments
* text content
* image content
* raw content streams

## Encryption handling

The implementation must check:

```python
reader.is_encrypted
```

before accessing:

```python
len(reader.pages)
```

When encrypted:

```text
inspection_status = "encrypted"
encrypted = True
page_count = 0
inspected_page_count = 0
page_details_truncated = False
page_details = ()
inspection_error = "pdf is encrypted"
```

The implementation must not:

* attempt an empty-password decrypt
* accept a password
* call `decrypt`
* inspect encrypted page count
* inspect encrypted pages
* trigger fallback extraction

## Page-count handling

For an unencrypted document:

```python
page_count = len(reader.pages)
```

`page_count` is the total parser-reported page count.

The implementation must not create one page item for every page when the total exceeds the approved limit.

The bounded detail count is:

```python
detail_count = min(
    page_count,
    execution_contract_result.max_inspected_pages,
)
```

Only indices in:

```python
range(detail_count)
```

may be accessed.

## Bounded page access

The implementation must inspect a contiguous zero-based prefix:

```text
0
1
2
...
detail_count - 1
```

It must not:

* skip indices
* select arbitrary pages
* inspect pages beyond the approved maximum
* use a caller-defined page list
* inspect the last page separately
* perform sampling

## Page dimension access

For each approved page index:

```python
page = reader.pages[index]
box = page.mediabox
width = float(box.width)
height = float(box.height)
```

The implementation must not import or require a rectangle class.

The dimensions remain PDF points.

The implementation must not:

* convert points to pixels
* apply DPI
* round values for presentation
* infer orientation labels
* calculate aspect-ratio classifications
* infer paper sizes
* infer product knowledge

## Dimension validation

Before creating an inspected page item, the implementation must verify:

* width is finite
* height is finite
* width is greater than zero
* height is greater than zero
* booleans are not accepted as numbers

Invalid dimensions cause a page-level failure.

The implementation must not repair or substitute invalid dimensions.

## Rotation access

The approved parser value is:

```python
page.rotation
```

The implementation may normalize rotation because parser-specific normalization belongs to the implementation layer.

Approved normalization:

1. `None` becomes `0`
2. boolean is invalid
3. integer values divisible by `90` may be normalized with modulo `360`
4. resulting value must be one of `0`, `90`, `180`, `270`
5. non-integer values are invalid
6. integer values not divisible by `90` are invalid

Examples:

```text
None -> 0
0 -> 0
90 -> 90
360 -> 0
450 -> 90
-90 -> 270
45 -> invalid
True -> invalid
"90" -> invalid
```

The result contract receives normalized values only.

## Per-page success item

A successfully inspected page produces:

```text
ControlledPdfStructuralMetadataPageItem(
    page_index=index,
    width_points=width,
    height_points=height,
    rotation_degrees=normalized_rotation,
    inspection_status="inspected",
)
```

No additional page field is approved.

## Per-page failure item

A page-level failure produces:

```text
ControlledPdfStructuralMetadataPageItem(
    page_index=index,
    width_points=0,
    height_points=0,
    rotation_degrees=0,
    inspection_status="page_error",
)
```

No raw page exception is retained.

Page-level failure may result from:

* page access failure
* media-box access failure
* width conversion failure
* height conversion failure
* invalid dimensions
* rotation access failure
* invalid rotation

## Per-page exception boundary

The implementation may use one bounded `try/except Exception` around inspection of each individual page.

The exception must not escape.

The exception string must not be stored.

The implementation must continue to the next approved page index after one page-level failure.

This broad page-level boundary is allowed because:

* it is limited to one page
* output remains generic
* raw exceptions are discarded
* page count remains bounded
* no fallback is triggered

## Document status selection

After bounded page inspection, document status is selected as follows.

### Zero-page document

When:

```text
page_count = 0
```

return:

```text
inspection_status = "inspected"
page_details = ()
page_details_truncated = False
inspection_error = ""
```

### Fully inspected document

When:

```text
page_count <= max_inspected_pages
```

and every inspected page succeeds:

```text
inspection_status = "inspected"
page_details_truncated = False
inspection_error = ""
```

### Successfully bounded document

When:

```text
page_count > max_inspected_pages
```

and every bounded page succeeds:

```text
inspection_status = "bounded"
page_details_truncated = True
inspection_error = ""
```

### Partial result

When the bounded prefix contains:

* at least one `inspected`
* at least one `page_error`

return:

```text
inspection_status = "partial"
inspection_error =
    "one or more pages could not be structurally inspected"
```

The truncation flag remains:

```text
page_count > max_inspected_pages
```

### All bounded pages fail

When:

* `detail_count > 0`
* every attempted page has `page_error`

the implementation must not return `partial`.

It must return the fatal result:

```text
inspection_status = "parser_error"
encrypted = False
page_count = 0
inspected_page_count = 0
page_details_truncated = False
page_details = ()
inspection_error = "pdf parser error"
```

Known page count and failed page items are intentionally omitted to satisfy the approved fatal-result contract.

## Parser-unavailable mapping

When the `pypdf` import is unavailable:

```text
inspection_status = "parser_unavailable"
inspection_error =
    "pdf parser dependency is unavailable"
```

The implementation must not:

* install `pypdf`
* change dependencies
* modify the virtual environment
* fall back to another parser

## Unreadable mapping

An `OSError` raised outside the bounded per-page loop must map to:

```text
inspection_status = "unreadable"
inspection_error = "pdf file is unreadable"
```

Raw operating-system messages must not be exposed.

## Generic parser-error mapping

Any other top-level parser exception must map to:

```text
inspection_status = "parser_error"
inspection_error = "pdf parser error"
```

Raw exception text, stack traces, parser dumps, and path diagnostics must not be returned.

## Exception ordering

The approved top-level handling order is:

```text
parser unavailable check
try:
    construct reader
    check encryption
    read page count
    inspect bounded page prefix
except OSError:
    unreadable
except Exception:
    parser_error
```

Per-page errors are caught inside the bounded loop before they can reach the top-level generic parser mapping.

## No parser retry

The implementation must not:

* reopen the PDF
* retry failed page access
* switch parser modes
* toggle strict mode
* retry with passwords
* repair the document
* invoke command-line utilities
* invoke another PDF library

One implementation request permits at most one `PdfReader` construction.

## No automatic fallback

No result may trigger:

* PDF text extraction
* page rendering
* image extraction
* OCR
* metadata inference
* Evidence
* Knowledge
* Prompt Candidate creation

This includes:

```text
partial
encrypted
unreadable
parser_unavailable
parser_error
blocked
```

## Output boundary

The implementation returns one in-memory immutable result only.

It must not write:

* JSON
* CSV
* text reports
* logs
* page images
* extracted assets
* temporary PDFs
* Evidence artifacts
* Knowledge artifacts

Test output may be saved outside the repository by the verification command only.

## Evidence boundary

Every implementation result must preserve:

```text
evidence_allowed = False
```

The implementation request must not contain an Evidence override.

The implementation must not import Evidence modules.

Structural metadata inspection output is not Evidence.

## Knowledge boundary

The implementation must not:

* classify the document
* infer product specifications
* infer brands or products
* normalize business values
* create Knowledge
* create Prompt Candidates
* make creative decisions

It returns factual structural PDF values only.

## Test isolation strategy

PR-021J tests must not create or open a PDF.

Parser behavior must be tested by monkeypatching the implementation module's:

```text
PdfReader
```

with controlled fake readers and fake pages.

The public implementation API must not add a reader-factory parameter solely for testing.

No unnecessary dependency-injection abstraction is approved.

## Fake reader boundary

Test doubles may provide only the parser values required by each test:

```text
is_encrypted
pages
page.mediabox.width
page.mediabox.height
page.rotation
```

Test doubles must not simulate:

* document text
* document metadata
* image extraction
* rendering
* OCR
* filesystem traversal

## Required PR-021J unit-test coverage

PR-021J tests must cover at least:

1. implementation request approval is required
2. invalid execution authority blocks before parser construction
3. parser unavailable result
4. encrypted result
5. zero-page inspected result
6. normal inspected result
7. bounded result
8. partial result with one page error
9. all bounded pages failing maps to parser error
10. reader-construction `OSError` maps to unreadable
11. reader-construction generic exception maps to parser error
12. page-count exception maps to parser error
13. `None` rotation normalizes to zero
14. `360` rotation normalizes to zero
15. `450` rotation normalizes to 90
16. negative 90 rotation normalizes to 270
17. invalid 45-degree rotation creates page error
18. invalid page width creates page error
19. invalid page height creates page error
20. non-finite dimension creates page error
21. bounded page access never exceeds maximum
22. `reader.metadata` is never accessed
23. text-extraction methods are never accessed
24. returned result always has `evidence_allowed=False`

The exact test count is not fixed.

## Existing contract tests

PR-021J must continue to pass:

```text
tests/ingestion/test_controlled_pdf_structural_metadata_contract.py
tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py
tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py
tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py
```

## Full-regression requirement

Before PR-021J may be committed:

* implementation tests must pass
* all structural metadata focused tests must pass
* full repository regression must pass
* only the two approved PR-021J files may change
* sandbox must remain empty
* Phase 20 PDF must remain absent
* cached files must remain empty

## PR-021J permitted files

PR-021J may introduce exactly:

```text
src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py
tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py
```

## PR-021J prohibited file changes

PR-021J must not modify:

```text
src/rie/ingestion/controlled_real_asset_fixture_contract.py
src/rie/ingestion/controlled_pdf_structural_metadata_contract.py
src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py
src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py
```

It must not modify existing tests.

Any required modification to an existing contract is a hard stop requiring separate review.

## Dependency boundary

PR-021J must not modify:

```text
pyproject.toml
requirements files
lock files
virtual environment files
```

The locally available `pypdf` dependency is sufficient.

## Recommended implementation constants

The implementation may reuse approved constants from the result contract:

```text
ENCRYPTED_ERROR
UNREADABLE_ERROR
PARSER_UNAVAILABLE_ERROR
PARSER_ERROR
SAFETY_CHECK_ERROR
REQUEST_REQUIRED_ERROR
PARTIAL_INSPECTION_ERROR
```

It must not duplicate these strings with divergent wording.

## Recommended commit

Recommended PR-021J commit subject:

```text
feat: add controlled pdf structural metadata implementation
```

This is a recommendation only.

Commit remains prohibited until:

* source content is reviewed
* implementation tests pass
* focused tests pass
* full regression passes
* parser boundaries are verified
* repository scope is verified
* sandbox remains empty

## Future step after PR-021J

After PR-021J, the next step should remain documentation-only:

```text
PR-021K - Controlled PDF Structural Metadata Synthetic Parser Verification Review
```

PR-021K should determine whether one generated synthetic PDF may be created and inspected in the controlled sandbox.

PR-021J itself must remain PDF-free.

## Allowed work in PR-021I

PR-021I may:

* record locally verified parser APIs
* define parser implementation boundaries
* define implementation request values
* define parser and page error mapping
* define test-double strategy
* recommend PR-021J

## Prohibited work in PR-021I

PR-021I must not:

* create implementation source
* create implementation tests
* create or open a PDF
* invoke `PdfReader` on a file
* inspect structural metadata
* install dependencies
* change parser versions
* modify the virtual environment
* render pages
* extract text or images
* run OCR
* create output files
* create Evidence or Knowledge
* modify locked or SSOT documents

## Git boundary

* Only the PR-021I documentation file may be introduced.
* PR-021A through PR-021H must remain unchanged.
* No source or test file may change.
* No real or synthetic asset may be staged or committed.
* Any unexpected tracked, staged, or untracked file is a hard stop.
* No merge or Phase 21 tag is authorized.

## Acceptance criteria

* PR-021I is documentation-only.
* Local `pypdf` public APIs are recorded.
* No top-level `RectangleObject` import is permitted.
* The implementation request is explicitly defined.
* Implementation execution requires separate approval.
* Only one `PdfReader` construction is permitted per request.
* Encryption is checked before page-count access.
* Page inspection is bounded to a zero-based prefix.
* Width and height are read from `page.mediabox`.
* Rotation normalization is explicitly defined.
* Page failures are bounded and contain no raw exception.
* Document statuses are deterministically selected.
* Parser errors are mapped to approved generic messages.
* All valid parser outcomes pass through the result contract.
* No PDF is created or opened in PR-021J tests.
* Parser behavior is verified with test doubles.
* Content extraction, rendering, OCR, Evidence, and Knowledge remain prohibited.
* Only two new files are approved for PR-021J.
