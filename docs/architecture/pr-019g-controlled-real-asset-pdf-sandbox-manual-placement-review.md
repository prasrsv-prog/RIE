# PR-019G - Controlled Real Asset PDF Sandbox Manual Placement Review

## Status

Docs-only manual placement review.

## Current checkpoint

- Tag: `v0.19.5-rcis-controlled-real-asset-pdf-sandbox-directory-creation-execution`
- Commit: `faa92d2 docs: record controlled real asset pdf sandbox directory creation`

## Purpose

Review the readiness criteria, user-facing manual placement instruction, and stop conditions for a future manual placement of exactly one real RSV PDF into the approved sandbox path without placing, copying, parsing, or processing any real asset in PR-019G.

PR-019G documents a future instruction boundary only. It does not instruct the user to place a file now.

## PR-019G boundary

PR-019G:

- does not modify production code
- does not modify tests
- does not modify `pyproject.toml`
- does not modify lock files
- does not install dependencies
- does not change the virtual environment
- does not parse PDFs
- does not create PDF fixtures
- does not extract PDF text
- does not copy real RSV assets
- does not touch real RSV assets
- does not place any PDF in the sandbox directory
- does not inspect the sandbox directory
- does not create Evidence, Knowledge, or Prompt Candidate
- does not authorize AI inference

## PR-019F context

PR-019F created only the approved empty local sandbox directory:

```text
sandbox/real_asset_pdf_smoke/
```

PR-019F committed only the execution report document. Git does not track the empty sandbox directory, and PR-019F added no `.gitkeep`, `.gitignore`, or placeholder file.

PR-019F did not copy a real RSV PDF, parse a PDF, or create Evidence, Knowledge, or Prompt Candidate. Directory creation is not placement and is not extraction.

PR-019G does not inspect or reverify the local directory.

## Manual placement review objective

PR-019G defines readiness requirements and the exact future instruction boundary for a later manual placement execution PR.

Future manual placement may be considered only if:

- the user explicitly approves moving from review to manual placement
- the branch is approved
- the working tree is clean
- the approved sandbox directory remains `sandbox/real_asset_pdf_smoke/`
- the approved target file remains `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- the user manually selects exactly one real RSV PDF
- the selected file is a PDF
- the selected file is not a folder
- the selected file is not an archive
- the selected file is not an image
- the production source path is not passed to RIE
- no production folder is scanned
- no wildcard path is used
- no recursive command is used
- no batch copy is used
- no PDF parsing occurs
- no PDF text extraction occurs
- no Evidence, Knowledge, or Prompt Candidate path is enabled

Failure of any readiness requirement stops future placement.

## Approved future placement target

The only approved future placement target remains:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

Placement rules:

- exactly one PDF only
- manual copy by the user only
- target filename must be `real-asset-smoke-source.pdf`
- target directory must be `sandbox/real_asset_pdf_smoke/`
- no product name in the filename
- no customer data in the filename
- no campaign name in the filename
- no production folder path in the filename
- no automatic script copy
- no RIE-driven copy
- no wildcard source path
- no folder source path
- no recursive copy
- no batch copy
- no overwrite without review

## Future user-facing placement instruction

A later approved placement execution PR may instruct the user within this exact boundary:

1. Manually select exactly one real RSV PDF.
2. Copy it manually outside RIE execution.
3. Rename the copied file to:
   `real-asset-smoke-source.pdf`
4. Place it only at:
   `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
5. Do not provide the production source path to RIE.
6. Do not run recursive commands.
7. Do not run wildcard commands.
8. Do not parse or inspect PDF text.
9. Do not stage or commit the real PDF.

These steps are future-only wording. PR-019G must not and does not give an execution instruction to place the file now.

## Future verification after placement

A later approved placement execution PR may verify only:

- the target directory exists
- the target file exists
- exactly one file exists in the target directory
- the target file extension is `.pdf` or `.PDF`
- the target file size is greater than zero
- an optional SHA256 hash is recorded
- an optional byte size is recorded
- the sandbox PDF is not tracked or staged by Git
- no extra sidecar files exist
- no nested folders exist
- no `.gitkeep`, `.gitignore`, or placeholder file exists in the sandbox directory

Future verification must not:

- parse PDF content
- read PDF text
- expose `extracted_text`
- call AI
- run OCR
- extract images
- infer product claims
- infer product benefits
- create Evidence
- create Knowledge
- create Prompt Candidate

## Stop conditions

Future manual placement must stop if:

- the working tree is not clean
- the sandbox directory is missing
- more than one file is selected
- the selected source is not a PDF
- the selected source is a folder
- the selected source is an archive
- a wildcard is needed
- a recursive command is needed
- a batch copy is attempted
- the target file already exists and overwrite is not explicitly reviewed
- the production source path is about to be used as RIE input
- the sandbox PDF would be staged or committed
- any command would parse PDF content
- any command would expose `extracted_text`
- any command would create Evidence, Knowledge, or Prompt Candidate

## Production asset protection

The original production RSV PDF must:

- not be opened by RIE
- not be parsed by RIE
- not be renamed
- not be moved
- not be modified
- not be deleted
- not be used as program input
- not be used as a fixture path
- not be included in logs
- not be committed
- remain outside the repository unless the user manually creates a sandbox copy at the approved target path

The production source path must never become RIE input.

## Future execution boundary

Manual placement is not extraction.

Even after a future placement succeeds:

- no PDF parsing is automatically allowed
- no extraction is automatically allowed
- no Evidence is automatically allowed
- no Knowledge is automatically allowed
- no Prompt Candidate is automatically allowed
- a later extraction execution PR must explicitly approve any parser run

If a later extraction execution PR is approved, it may process only the approved sandbox-copy PDF through this chain:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfTextExtractionContract
-> ControlledPdfTextExtractionExecutionContract
-> ControlledPdfTextExtractionImplementation
-> ControlledPdfTextExtractionResultContractResult
```

The future result must:

- not expose `extracted_text`
- keep `extracted_text_included` as `False`
- keep `evidence_allowed` as `False`
- keep `allow_full_text_storage` as `False`
- keep `allow_evidence_creation` as `False`
- report only status, `text_length`, bounded `text_preview`, and errors
- treat extracted PDF text as extraction output only, not Evidence
- treat `text_preview` as bounded parser output only, not Knowledge

## Cleanup boundary

A later placement or smoke-test PR must decide whether the sandbox copy is:

- deleted after verification, or
- temporarily retained for a later approved extraction execution PR

The default policy is to delete the sandbox copy after its approved review window unless temporary retention is explicitly approved.

Cleanup must:

- target only `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- not delete production files
- not recursively delete broader paths
- verify Git status afterward

PR-019G itself must not delete any sandbox file or directory.

## Forbidden scope

The following remain forbidden:

- placing any PDF in the sandbox directory in PR-019G
- copying any real asset in PR-019G
- parsing any real PDF in PR-019G
- inspecting the sandbox directory in PR-019G
- adding `.gitkeep`
- adding placeholder files
- adding `.gitignore` in the sandbox directory
- production RSV folder scan
- direct production asset processing
- multiple real assets
- recursive scan
- current working directory scan
- repository-wide scan
- automatic copy from production folders
- batch processing
- full `extracted_text` exposure
- Evidence creation
- Official Knowledge creation
- Product Knowledge creation
- Prompt Candidate creation
- AI inference
- OCR
- image extraction
- layout interpretation
- product claim extraction
- product benefit extraction
- persona inference
- prompt inference
- CLI, API, or dashboard execution
- locked or SSOT document mutation

## Risk review

### Review mistaken for placement execution

Future-only wording could be interpreted as authorization to place a file now. Placement requires a separate approved execution PR and explicit user approval.

### More than one PDF is copied

Multi-select, batch, wildcard, or folder copy behavior could exceed the single-file boundary. Future placement must be one manual user action for exactly one PDF.

### Wrong file type is placed

An image, archive, folder, or other file could be selected instead of a PDF. The later placement gate must stop unless the selected source is one PDF.

### Target overwrite without review

An existing sandbox file could be replaced without confirming its identity or review state. Future placement must stop before any unreviewed overwrite.

### Production source path becomes program input

The original path could be passed to RIE instead of the sandbox copy path. The production path must never be RIE input, a fixture path, or log content.

### Sandbox PDF becomes tracked or staged

The real PDF could be staged or committed accidentally. Future verification must confirm that the sandbox PDF remains untracked and unstaged.

### Verification drifts into parsing

Metadata verification could expand into opening or parsing PDF content. Verification must remain limited to path, count, extension, size, and optional hash.

### Retained PDF is forgotten

A temporarily retained real PDF could remain after its approved window. Retention must be explicit, and the default policy remains deletion of the exact sandbox copy.

### Placement mistaken for extraction approval

Successful placement does not authorize parser execution. Extraction requires a later separately approved execution PR.

### Extraction output becomes Evidence or Knowledge

Future extraction output could be promoted prematurely. Any preview must remain bounded parser output and must not enter Evidence, Official Knowledge, Product Knowledge, or Prompt Candidate paths.

## Recommended next PR

`PR-019H - Controlled Real Asset PDF Sandbox Manual Placement Execution`

PR-019H may be a small execution step if approved. It may allow the user to manually place exactly one real RSV PDF at:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

It must not parse any PDF or create Evidence, Knowledge, or Prompt Candidate.

## Acceptance Criteria

- Only one docs file is added.
- Empty sandbox directory remains a local preparation artifact.
- No PDF is placed in the sandbox directory by PR-019G.
- No .gitkeep, .gitignore, or placeholder file is added to the sandbox directory.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed.
- No virtual environment changes are made.
- No PDF parsing is performed.
- No PDF fixture is created.
- No real RSV asset is touched, copied, or scanned.
- No sandbox directory inspection is performed by PR-019G.
- Full tests pass.
- pypdf imports successfully and version 6.14.2 is recorded.
- No non-ASCII or garbled characters remain.
- No commit is created by PR-019G preparation.
