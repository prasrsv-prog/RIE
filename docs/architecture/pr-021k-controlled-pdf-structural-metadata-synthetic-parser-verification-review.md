# PR-021K - Controlled PDF Structural Metadata Synthetic Parser Verification Review

## Status

Documentation-only synthetic parser verification review.

No `PdfWriter` or `PdfReader` instance is created. No PDF is created, opened, read, parsed, or written in PR-021K.

## Current checkpoint

- Branch: `phase-021-controlled-pdf-post-extraction-review`
- HEAD: `44d3391`
- `main`: `fbb0c99`
- `origin/main`: `fbb0c99`
- Working tree before review: clean
- Sandbox directory exists and is empty
- Real PDF target is absent
- Synthetic PDF target is absent

## Read-only review outcome

The approved read-only source and local API review confirmed:

- `pypdf` version `6.14.2`
- `PdfWriter` is a public `pypdf` export
- required writer and page APIs are locally available by import and signature inspection
- the committed structural metadata implementation accesses only bounded reader/page geometry APIs
- prohibited content, document metadata, image, attachment, outline, and decryption APIs are not accessed
- repository and sandbox state remained clean

The review was import/introspection and source inspection only.

## Purpose

Define the exact creation, execution, assertion, failure, and cleanup boundaries for a future controlled synthetic parser verification of PDF structural metadata.

PR-021K does not implement or execute the recommendation.

## Verified local PdfWriter API

Locally verified as supported without instantiation:

- `PdfWriter()`
- `PdfWriter.add_blank_page(width, height)`
- `PageObject.rotate(degrees)`
- `PdfWriter.write(path)`
- `PdfWriter.close()`
- `PdfWriter.pages`
- `PageObject.rotation`
- `PageObject.mediabox`

The following APIs exist but are prohibited:

- `PdfWriter.encrypt`
- `PdfWriter.add_metadata`
- `PdfWriter.add_attachment`
- `PageObject.extract_text`
- `PageObject.images`

API availability does not grant execution authority.

## Synthetic fixture definition

The exact future synthetic target is:

```text
sandbox/real_asset_pdf_smoke/synthetic-structural-metadata.pdf
```

The future fixture must contain exactly four blank pages. It must contain no text, images, annotations, attachments, document metadata, encryption, or other semantic content.

The synthetic PDF is a temporary execution artifact. It must remain untracked and must never be committed.

## Page specification

| Page index | width_points | height_points | rotation_degrees |
| ---: | ---: | ---: | ---: |
| 0 | 612 | 792 | 0 |
| 1 | 595 | 842 | 90 |
| 2 | 420 | 595 | 180 |
| 3 | 792 | 612 | 270 |

Width and height assertions refer to media-box values. They are not swapped merely because a page rotation is `90` or `270` degrees.

## Creation boundary

A future explicitly approved execution must:

- construct `PdfWriter` exactly once
- add exactly four blank pages
- use the dimensions in the page specification
- rotate only pages `1`, `2`, and `3`
- apply rotations `90`, `180`, and `270` respectively
- write exactly one file to the literal synthetic target
- close the writer after writing

Creation must use:

- no encryption
- no metadata
- no attachments
- no text
- no images
- no annotations
- no alternate paths
- no persistent repository output
- no wildcard, recursion, scan, discovery, or batch behavior

## Contract authority chain

The only future controlled chain is:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfStructuralMetadataContract
-> ControlledPdfStructuralMetadataExecutionContract
-> ControlledPdfStructuralMetadataImplementation
-> ControlledPdfStructuralMetadataResultContract
```

Future authority values must be exactly:

- `fixture_type = product_spec_pdf`
- `allowed_for_metadata = True`
- `allowed_for_pdf_text_extraction = False`
- `allowed_for_image_metadata = False`
- `allowed_for_evidence = False`
- `inspection_mode = structural_metadata_only`
- `allow_execution = True`
- `max_inspected_pages = 4`
- `allow_content_extraction = False`
- `allow_output_file_creation = False`
- `allow_implementation_execution = True`
- `evidence_allowed` remains `False`

## Execution boundary

Before future execution:

- confirm the approved branch and HEAD
- confirm the repository state is clean
- confirm the sandbox exists and is empty
- confirm the real and synthetic PDF targets are absent
- confirm the local API and dependency version remain approved

Future execution may create only the exact synthetic fixture and pass only its literal path through the controlled chain.

No alternate extractor, CLI, API, dashboard, batch scanner, rendering path, or downstream workflow may be used.

## Result assertion boundary

Exact future assertions are:

- `allowed is True`
- `inspection_status is inspected`
- `encrypted is False`
- `page_count is 4`
- `inspected_page_count is 4`
- `page_details_truncated is False`
- `inspection_error` is empty
- `evidence_allowed is False`
- page indices are exactly `0`, `1`, `2`, `3`
- dimensions match the configured media boxes in order
- rotations are exactly `0`, `90`, `180`, `270`
- only approved structural metadata fields are inspected

No assertion may inspect or infer text, images, annotations, attachments, document metadata, outline, XMP data, content streams, or other semantic content.

## Failure and cleanup boundary

After success or failure, cleanup must target only:

```text
sandbox/real_asset_pdf_smoke/synthetic-structural-metadata.pdf
```

Cleanup rules:

- use the exact literal path only
- use no wildcard
- use no recursive deletion
- do not delete `sandbox/real_asset_pdf_smoke`
- verify the synthetic target is absent
- verify the sandbox item count returns to zero
- verify Git state remains clean

Cleanup must still be attempted for the exact synthetic target after an execution or assertion failure.

Raw parser errors must not be emitted into result values. There must be no fallback to text extraction, rendering, OCR, image extraction, Evidence, or Knowledge.

## Prohibited operations

- PDF creation or parser execution in PR-021K
- production asset access
- encryption
- document metadata addition
- attachment addition
- text extraction
- image access or extraction
- annotation access
- rendering
- OCR
- AI inference
- Evidence creation
- Knowledge creation
- Product Knowledge creation
- Official Knowledge creation
- Prompt Candidate creation
- wildcard, recursive, repository-wide, or current-directory scans
- alternate fixture paths
- generated repository output
- staging or committing a PDF
- dependency or virtual-environment changes

## Git and asset boundary

- PR-021K creates only this documentation file.
- No PDF exists in the sandbox during PR-021K.
- No real or synthetic asset is tracked, staged, or committed.
- Existing source and tests remain unchanged.
- The future synthetic PDF must remain an untracked temporary artifact.
- Only a later execution report document may be committed after cleanup and review.

## Recommended PR-021L

`PR-021L - Controlled PDF Structural Metadata Synthetic Parser Execution`

PR-021L must be execution-only and must not commit the synthetic PDF. It must use the exact fixture, authority, execution, assertion, failure, and cleanup boundaries defined here.

## Acceptance criteria

- Only the PR-021K document is added.
- `pypdf 6.14.2` API facts are recorded.
- The exact four-page fixture definition is recorded.
- Media-box dimensions remain independent of page rotation assertions.
- The exact controlled authority chain and values are recorded.
- Exact result assertions are recorded.
- Exact failure and cleanup behavior is recorded.
- PR-021K creates or opens no PDF.
- PR-021K instantiates no `PdfWriter` or `PdfReader`.
- No source code or test changes occur.
- No prohibited content or downstream workflow occurs.
- Repository state contains only this untracked document.
- Sandbox remains empty with both PDF targets absent.
- Nothing is staged, committed, pushed, merged, or tagged.
