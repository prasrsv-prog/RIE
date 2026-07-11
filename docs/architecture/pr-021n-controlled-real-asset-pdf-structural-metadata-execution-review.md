# PR-021N - Controlled Real Asset PDF Structural Metadata Execution Review

## Status

Documentation-only review of whether one explicitly user-approved real PDF may later be manually placed and inspected once for bounded structural metadata.

PR-021N does not select, place, open, parse, inspect, hash, or delete a PDF. It does not authorize immediate placement or execution.

## Current checkpoint

- Branch: `phase-021-controlled-pdf-post-extraction-review`
- HEAD: `3e893ef`
- Remote phase HEAD: `3e893ef`
- `main`: `fbb0c99`
- `origin/main`: `fbb0c99`
- Local/remote phase divergence: `0 0`
- Working tree before PR-021N: clean
- Index before PR-021N: clean
- Sandbox directory exists and is empty
- Real PDF target is absent
- Synthetic PDF target is absent

## Prior synthetic verification outcome

PR-021L successfully verified the committed structural metadata chain exactly once:

- `PdfWriter` construction count: `1`
- synthetic PDF write count: `1`
- structural metadata implementation execution count: `1`
- pages inspected: `4`
- page count: `4`
- media-box dimensions were preserved
- rotations `0`, `90`, `180`, and `270` were preserved
- result status: `inspected`
- Evidence allowed remained `False`
- exact cleanup succeeded
- the final repository and sandbox returned clean

The successful synthetic execution must not be repeated without a new explicit review. It establishes a bounded synthetic capability only; it does not authorize real-asset execution.

## Purpose

This review defines the decision and safety boundaries for whether one explicitly user-approved real PDF may later be:

- manually copied into the controlled sandbox
- inspected exactly once
- limited to structural metadata only
- deleted through exact-path cleanup
- excluded from Git staging and commits

PR-021N itself does not authorize immediate placement or execution. Separate approval and controlled later steps remain mandatory.

## Real-asset selection boundary

- No real asset is currently selected.
- No source path is currently approved.
- No source filename is currently approved.
- No production asset may be discovered automatically.
- No repository document may be assumed to be the real asset.
- No Phase 20 asset may be restored automatically.
- The user must explicitly identify and approve one local source PDF in a later step.
- The source PDF must remain outside the repository before manual placement.
- Source approval is specific to one file and one execution cycle.
- Approval does not extend to neighboring files or directories.

No production folder, user folder, repository, drive, or asset library may be scanned. Source-path inference, directory discovery, wildcard selection, and recursive discovery are prohibited.

## Controlled sandbox target

The only proposed future repository-local target is:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

- The target is a temporary execution asset.
- It must never be staged or committed.
- The sandbox directory must remain present.
- The target must be absent before placement.
- The sandbox must contain zero items before placement.
- No alternate target path is allowed.
- The source filename must not be preserved or inferred in the repository target.

## Manual placement boundary

A separately approved future placement step may:

- copy exactly one explicitly approved source PDF
- copy it only to the exact literal sandbox target
- perform no content inspection during placement
- verify only target existence and bounded file identity information required for placement control
- verify exactly one sandbox item exists
- allow exactly one untracked repository file while placed: `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`

A future placement step must not:

- open the PDF
- call `PdfReader`
- extract text
- inspect metadata
- render pages
- access images
- rename or modify the source file
- scan directories
- use wildcard copying
- use recursive copying
- copy multiple assets
- stage or commit the PDF
- leave the PDF after the approved execution and cleanup sequence

Manual placement is not authorized by PR-021N.

## Source integrity boundary

A later explicitly approved manual-placement step should record:

- the explicit approved source path
- source file size in bytes
- source SHA-256 hash
- copied target file size in bytes
- copied target SHA-256 hash
- equality of source and target hashes

Hashing is permitted only for placement integrity. A hash is not content extraction, Evidence, or Knowledge.

PR-021N does not calculate a source or target hash.

## Execution authority chain

Any future real-asset execution must use only:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfStructuralMetadataContract
-> ControlledPdfStructuralMetadataExecutionContract
-> ControlledPdfStructuralMetadataImplementation
-> ControlledPdfStructuralMetadataResultContract
```

Required future fixture values are:

- `fixture_id`: `controlled-real-asset-pdf-structural-metadata`
- `source_label`: `controlled real asset PDF structural metadata verification`
- `fixture_path`: `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- `fixture_type`: `product_spec_pdf`
- `allowed_for_metadata`: `True`
- `allowed_for_pdf_text_extraction`: `False`
- `allowed_for_image_metadata`: `False`
- `allowed_for_evidence`: `False`

Required future execution values are:

- `inspection_mode`: `structural_metadata_only`
- `allow_execution`: `True`
- `max_inspected_pages`: `10`
- `allow_content_extraction`: `False`
- `allow_output_file_creation`: `False`
- `allow_evidence_creation`: `False`
- `allow_implementation_execution`: `True`
- `evidence_allowed`: `False`

These values describe a potential future execution boundary. They do not grant execution authority in PR-021N.

## Maximum inspection boundary

- The document page count may be read.
- Detailed page inspection is limited to the first `10` pages.
- Page indices must remain a contiguous zero-based prefix.
- Pages beyond the limit must not be accessed.
- `page_details_truncated` must reflect whether `page_count` exceeds `10`.
- Arbitrary page selection and sampling are prohibited.

## Permitted structural output

Only these structural fields may be produced:

- `encrypted`
- `page_count`
- `page_width_points`
- `page_height_points`
- `page_rotation_degrees`

Permitted result states remain:

- `inspected`
- `bounded`
- `partial`
- `encrypted`
- `unreadable`
- `parser_unavailable`
- `parser_error`
- `blocked`

No raw parser exception may be exposed.

## Prohibited content access

The future placement and execution sequence must not access or use:

- `reader.metadata`
- `page.extract_text`
- `page.images`
- annotations
- attachments
- outlines
- XMP
- form values
- links
- raw content streams
- embedded files
- rendering
- OCR
- AI interpretation
- product specification extraction
- semantic classification
- Evidence
- Knowledge
- Prompt Candidates

Text, images, document metadata, and semantic content remain outside the authorized structural boundary.

## One-time execution boundary

A separately authorized future real-asset execution must:

- occur exactly once
- construct `PdfReader` only through the committed implementation
- call the implementation `execute` method exactly once
- prohibit retry
- prohibit fallback
- prohibit switching parsers
- prohibit strict-mode experimentation
- prohibit password attempts
- prohibit decryption
- prohibit repairing the PDF

Failure must still proceed to exact cleanup. PR-021N does not execute this sequence.

## Transient Git boundary

Before placement:

- no tracked changes
- no staged files
- no untracked files
- sandbox item count `0`

During placement and execution:

- no tracked changes
- no staged files
- exactly one untracked file: `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- sandbox item count `1`

After cleanup:

- no tracked changes
- no staged files
- no untracked files
- exact target absent
- sandbox item count `0`

The temporary PDF must never enter the index or repository history.

## Cleanup boundary

A future cleanup must:

- delete only `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- use the exact literal target path
- run even after execution or assertion failure
- retain the sandbox directory
- verify target absence
- verify the sandbox item count returns to zero
- verify Git state returns clean

Cleanup must not use wildcard deletion, recursive deletion, sandbox-directory deletion, deletion of the original source PDF, or cleanup of unrelated files.

## Result assertion boundary

For a successful non-encrypted asset, a future execution may assert:

- result `allowed` is `True`
- fixture identity matches
- fixture path matches the exact sandbox target
- fixture type is `product_spec_pdf`
- inspection mode is `structural_metadata_only`
- encrypted is `False`
- `page_count` is a non-negative integer
- `inspected_page_count` equals the bounded page-detail count
- `inspected_page_count` is at most `10`
- page indices form a contiguous zero-based prefix
- inspected page dimensions are finite positive PDF-point values
- rotations are `0`, `90`, `180`, or `270`
- Evidence is `False`
- no content fields are returned

The review does not predetermine page count, dimensions, rotations, encryption status, or inspected/bounded/partial status. Those values must come from the explicitly approved real PDF and remain factual parser output.

## Encrypted and error-result boundary

Encrypted, unreadable, parser-unavailable, parser-error, partial, or blocked results are valid controlled outcomes when consistent with the contracts.

Such outcomes:

- do not authorize retries
- do not authorize password attempts
- do not authorize fallback extraction
- do not authorize raw exceptions
- must still be followed by exact cleanup

An error or bounded result does not expand authority.

## Evidence and Knowledge boundary

- Structural metadata output is not Evidence.
- A successful real-asset inspection does not authorize Evidence creation.
- It does not authorize Knowledge creation.
- It does not authorize Product Knowledge.
- It does not authorize Official Knowledge.
- It does not authorize Prompt Candidate generation.
- No automatic promotion or conversion is permitted.

## Next-step sequence

The recommended safe sequence is:

1. **PR-021N - Controlled Real Asset PDF Structural Metadata Execution Review**
   Documentation-only.
2. **PR-021O - Controlled Real Asset PDF Manual Placement**
   One explicitly approved external source PDF; exact copy and integrity verification only; no parser execution; no commit.
3. **PR-021P - Controlled Real Asset PDF Structural Metadata Execution**
   Exactly one implementation execution; terminal output only; exact cleanup; no commit.
4. **PR-021Q - Controlled Real Asset PDF Structural Metadata Execution Review**
   Documentation-only record of the outcome.

PR-021O is not authorized until:

- PR-021N is committed and synchronized
- the user explicitly identifies and approves one source PDF
- the source path and source file are reviewed without directory discovery

## Recommended PR-021O

The recommended next PR is:

**PR-021O - Controlled Real Asset PDF Manual Placement**

PR-021O must remain placement-only. It must not execute `PdfReader` or the structural metadata implementation. It requires a separately identified and explicitly approved external source PDF before any placement activity.

## Git boundary

- Only the PR-021N document may be introduced.
- No source or test file may change.
- No existing document, dependency, configuration, or virtual-environment file may change.
- No real asset may be created, copied, opened, staged, or committed.
- No synthetic PDF may be created or opened.
- No merge or Phase 21 tag is authorized.

The document must remain untracked and unstaged during review. PR-021N does not authorize staging, commit, push, merge, or tag operations.

## Acceptance criteria

- The current checkpoint remains branch `phase-021-controlled-pdf-post-extraction-review` at `3e893ef` locally and remotely.
- `main` and `origin/main` remain at `fbb0c99`.
- Local/remote phase divergence remains `0 0`.
- The prior synthetic result and repeat-execution prohibition are recorded.
- No real asset, source path, or source filename is selected or inferred.
- The exact proposed sandbox target and manual-placement boundary are explicit.
- Source integrity verification is limited to a separately authorized placement step.
- The exact contract chain and required future values are recorded.
- Detailed inspection is bounded to the first `10` pages.
- Permitted structural fields and prohibited content APIs are explicit.
- Execution is one-time, without retry, fallback, password attempt, decryption, repair, or parser switching.
- The transient Git and exact-cleanup boundaries are explicit.
- Assertions remain factual and do not predetermine real-asset results.
- Encrypted and error outcomes do not expand authority.
- Structural metadata is not Evidence or Knowledge.
- PR-021O remains unauthorized until PR-021N is committed and synchronized and one source PDF is explicitly approved.
- Only this PR-021N document is the intended repository change.
- The document remains untracked and unstaged.
- The sandbox remains present and empty, with both named PDF targets absent.
