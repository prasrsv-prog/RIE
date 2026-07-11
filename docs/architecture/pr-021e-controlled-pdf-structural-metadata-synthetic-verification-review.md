# PR-021E - Controlled PDF Structural Metadata Synthetic Verification Review

## Status

* Documentation-only synthetic verification review.
* PR-021D contract skeleton is committed and synchronized.
* The structural metadata base contract and execution contract now exist.
* Their focused unit tests passed.
* The full repository regression suite passed.
* No PDF parser implementation exists for this capability.
* No structural metadata result contract exists.
* No real or synthetic PDF is present.
* No parser, OCR, rendering, image extraction, Evidence, Knowledge, or Prompt Candidate execution is authorized.

## Current checkpoint

* Branch: `phase-021-controlled-pdf-post-extraction-review`
* Branch HEAD before PR-021E: `071245c`
* `main`: `fbb0c99`
* `origin/main`: `fbb0c99`
* Phase 21 branch is synchronized with its remote branch.
* Working-tree tracked diff: empty.
* Cached diff: empty.
* Controlled sandbox directory exists and remains empty.
* Phase 20 real PDF target remains absent.

## Previous PR outcome

PR-021D introduced:

* `ControlledPdfStructuralMetadataContract`
* `ControlledPdfStructuralMetadataExecutionContract`
* their immutable result objects
* isolated unit tests for both contracts

PR-021D did not introduce:

* `PdfReader`
* parser access
* file opening
* structural metadata implementation
* structural metadata result contract
* synthetic PDF creation
* real PDF placement
* persistent output
* Evidence or Knowledge integration

PR-021D verification produced:

* focused contract tests passing
* full repository regression passing
* no forbidden parser import
* no staged or remaining repository changes
* empty controlled sandbox

## Purpose

Define the boundary for a synthetic integration verification of the existing value-only structural metadata contracts.

PR-021E determines:

* what synthetic verification means at the current architecture level
* which contract chain may be exercised
* which values may be supplied
* which allowed and blocked states must be verified
* which files may be introduced
* which activities remain prohibited
* whether parser-level synthetic verification is appropriate

PR-021E does not create or execute tests.

## Synthetic verification definition

For PR-021E, synthetic verification means an in-memory contract-chain test using manually constructed immutable values.

It does not mean:

* creating a PDF
* opening a PDF
* parsing a PDF
* inspecting page count
* reading page dimensions
* reading page rotation
* creating parser output
* creating result-contract output
* rendering pages
* extracting text
* extracting images
* running OCR
* creating Evidence or Knowledge

The synthetic input is a fixture declaration value only.

## Approved verification chain

The only chain approved for synthetic verification is:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfStructuralMetadataContract
-> ControlledPdfStructuralMetadataExecutionContract
```

The verification ends at the execution-contract result.

It must not continue into:

* structural metadata implementation
* structural metadata result contract
* PDF parser access
* downstream workflows

## Why parser verification is deferred

The current Phase 21 implementation contains only:

* fixture authority
* structural metadata capability contract
* structural metadata execution contract

There is no approved:

* implementation request
* parser adapter
* page-detail value object
* result input
* result contract
* error mapping implementation

Creating a synthetic PDF or invoking `pypdf` now would skip required architecture layers.

Parser-level synthetic verification is therefore deferred until:

1. the structural metadata result-contract review is complete
2. the result contract exists
3. implementation boundaries are separately reviewed
4. the parser implementation exists
5. parser execution is explicitly approved

## Recommended PR-021F scope

PR-021F should introduce exactly one test file:

```text
tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py
```

No source file should be changed.

The test file should exercise the existing value-only contract chain only.

## Synthetic fixture declaration

The synthetic smoke flow may construct one:

```text
ControlledRealAssetFixtureItem
```

Approved fixture values:

```text
fixture_id = "synthetic-pdf-structural-metadata"
source_label = "synthetic structural metadata fixture"
fixture_path = "synthetic/controlled-structural-metadata.pdf"
fixture_type = "product_spec_pdf"
allowed_for_metadata = True
allowed_for_pdf_text_extraction = False
allowed_for_image_metadata = False
allowed_for_evidence = False
notes = "value-only synthetic contract verification"
```

The fixture path is a value only.

The test must not:

* create the directory
* create the file
* check file existence
* resolve the path
* open the path
* access a production path

## Approved success flow

The synthetic success flow should:

1. create one synthetic fixture item
2. evaluate `ControlledRealAssetFixtureContract`
3. verify the fixture contract is allowed
4. evaluate `ControlledPdfStructuralMetadataContract`
5. verify the metadata contract is allowed
6. evaluate `ControlledPdfStructuralMetadataExecutionContract`
7. explicitly set `allow_execution=True`
8. provide a bounded `max_inspected_pages`
9. verify the execution contract is allowed
10. verify all prohibition flags remain disabled

The approved execution boundary for the smoke flow is:

```text
max_inspected_pages = 3
```

This value is below:

```text
MAX_INSPECTED_PAGES_LIMIT = 10
```

The value does not authorize page inspection because no implementation is invoked.

## Required success assertions

The success test must verify:

* fixture contract `allowed=True`
* fixture count equals `1`
* metadata contract `allowed=True`
* execution contract `allowed=True`
* fixture identity remains unchanged
* fixture path remains unchanged
* fixture type remains `product_spec_pdf`
* inspection mode remains `structural_metadata_only`
* permitted fields match the approved immutable field set
* execution approval is `True`
* maximum inspected pages equals `3`
* content extraction remains `False`
* output-file creation remains `False`
* Evidence remains `False`

## Required permitted-field assertions

The smoke flow must verify that the approved field set is exactly:

```text
encrypted
page_count
page_width_points
page_height_points
page_rotation_degrees
```

The test must not add:

* text fields
* OCR fields
* image fields
* semantic metadata fields
* parser-specific fields
* arbitrary caller-defined fields

## Required blocked flow

PR-021F should include a blocked integrated flow demonstrating that fixture metadata authority alone is insufficient.

The blocked flow should:

1. produce an allowed fixture contract
2. produce an allowed structural metadata contract
3. evaluate the execution contract with `allow_execution=False`
4. verify the result is blocked
5. verify the reason is `execution approval is required`

This proves:

```text
allowed_for_metadata=True
```

does not automatically authorize inspection execution.

## Optional blocked flow

PR-021F may include one additional integrated prohibition test.

The preferred optional case is:

```text
allow_content_extraction=True
```

Expected result:

```text
allowed=False
reason="content extraction is not allowed by this contract"
```

This case verifies that an approved execution request cannot expand into text, image, OCR, or semantic content access.

No more than three synthetic smoke-flow tests should be introduced in PR-021F.

Existing unit tests already provide detailed validation of individual branches.

## Filesystem boundary

PR-021F must not use:

* `Path.exists`
* `Path.resolve`
* `open`
* `read_text`
* `read_bytes`
* `PdfReader`
* `pypdf`
* temporary-file APIs
* fixture directories
* sandbox file creation

The synthetic fixture path must remain an uninterpreted string value.

## Import boundary

The synthetic smoke-flow test may import only:

* `ControlledRealAssetFixtureContract`
* `ControlledRealAssetFixtureItem`
* `ControlledPdfStructuralMetadataContract`
* `ControlledPdfStructuralMetadataExecutionContract`
* approved constants from the two structural metadata contract modules

It must not import:

* `pypdf`
* text-extraction implementation
* text-extraction execution contract
* Evidence modules
* Knowledge modules
* OCR libraries
* image-processing libraries

## Source-code boundary

PR-021F must not modify:

```text
src/rie/ingestion/controlled_real_asset_fixture_contract.py
src/rie/ingestion/controlled_pdf_structural_metadata_contract.py
src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py
```

It must not create:

```text
controlled_pdf_structural_metadata_implementation.py
controlled_pdf_structural_metadata_result_contract.py
```

Any need to alter the current contracts is a hard stop requiring a separate review.

## Test boundary

PR-021F may introduce only:

```text
tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py
```

The test must remain:

* deterministic
* value-only
* filesystem-free
* parser-free
* network-free
* dependency-free beyond existing project imports
* isolated from Evidence and Knowledge

## Test count boundary

PR-021F may add:

* one required success-flow test
* one required execution-approval blocked test
* at most one content-extraction blocked test

Maximum new test count:

```text
3
```

A larger test matrix belongs in existing isolated unit-test files or a separately reviewed test expansion.

## Execution boundary

Executing pytest for PR-021F does not authorize structural metadata inspection.

Pytest may only evaluate contract values.

The test execution must not:

* access a PDF
* call parser APIs
* create output files
* create sandbox content
* invoke downstream workflows

## Regression boundary

PR-021F must run:

1. the synthetic smoke-flow test
2. the two structural metadata contract test files
3. the full repository test suite

Expected safeguards:

* all focused tests pass
* all full-suite tests pass
* only the new smoke-flow test file appears as a repository change
* sandbox remains empty
* Phase 20 PDF target remains absent

## Output boundary

Test output may be written to a text file outside the repository for review.

Recommended location:

```text
D:\PROJECT\pr-021f-structural-metadata-synthetic-output.txt
```

The external output file must not be staged or committed.

No repository output artifact is permitted.

## Real-asset boundary

PR-021F requires no real asset.

It must not:

* restore the Phase 20 PDF
* request a production source path
* copy a PDF into the sandbox
* inspect real metadata
* retain any asset

## Result-contract boundary

PR-021F does not create or simulate:

* document page count
* encryption state
* page dimensions
* page rotation
* page-detail items
* inspection statuses
* inspection errors
* parser result values

Those fields belong to the future structural metadata result-contract layer.

The synthetic smoke flow validates authority propagation only.

## Evidence and Knowledge boundary

All successful synthetic results must preserve:

```text
evidence_allowed = False
```

The smoke flow must not import or call:

* Evidence builders
* Evidence collectors
* Evidence repositories
* Knowledge builders
* Knowledge repositories
* Prompt Candidate workflows

Contract authorization is not Evidence.

## No automatic fallback

A blocked or allowed synthetic result must not trigger:

* PDF text extraction
* PDF structural inspection
* page rendering
* embedded-image extraction
* OCR
* Evidence
* Knowledge

The test ends after result assertions.

## Decision

A value-only synthetic smoke flow is approved for implementation review.

Parser-level synthetic verification is not approved.

PR-021F may introduce one isolated test file with no source changes and no PDF creation.

## Recommended PR-021F commit

Recommended commit subject:

```text
test: add controlled pdf structural metadata synthetic smoke flow
```

This is a recommendation only.

Commit remains prohibited until:

* test content is reviewed
* focused tests pass
* full regression passes
* repository scope is verified
* sandbox remains empty

## Future sequence after PR-021F

After PR-021F, Phase 21 should pause before parser implementation.

The next safest review should determine whether to introduce:

```text
ControlledPdfStructuralMetadataResultContract
```

before any parser implementation.

The roadmap may therefore be refined after PR-021F.

No parser or real-asset execution should begin merely because the contract smoke flow passes.

## Allowed work in PR-021E

PR-021E may:

* define synthetic contract-chain verification
* define approved synthetic fixture values
* define integrated success and blocked cases
* define the future test file
* preserve parser and filesystem prohibitions
* recommend PR-021F

## Prohibited work in PR-021E

PR-021E must not:

* create tests
* modify source code
* create a PDF
* open a PDF
* invoke `pypdf`
* inspect structural metadata
* create a result contract
* create an implementation
* render pages
* extract text
* extract images
* run OCR
* install dependencies
* modify the virtual environment
* create Evidence or Knowledge
* modify locked or SSOT documents

## Git boundary

* Only the PR-021E documentation file may be introduced.
* PR-021A through PR-021D must remain unchanged.
* No source or test file may change.
* No real or synthetic asset may be staged or committed.
* Any unexpected tracked, staged, or untracked file is a hard stop.
* No merge or Phase 21 tag is authorized.

## Acceptance criteria

* PR-021E is documentation-only.
* The current contract chain is reviewed without execution.
* Synthetic verification is defined as value-only.
* No PDF creation or parser access is authorized.
* The smoke flow ends at the execution-contract result.
* One success flow is required.
* One missing-execution-approval flow is required.
* At most one content-extraction blocked flow is permitted.
* Maximum new test count is three.
* Only one future test file is approved.
* Existing source files must remain unchanged.
* Result contract and parser implementation remain deferred.
* Evidence and Knowledge remain prohibited.
* The sandbox remains empty.
* The Phase 20 PDF target remains absent.
* PR-021F is identified as the next test-only step.
* Only the PR-021E document is the intended repository change.
