# PR-020C - Controlled Real Asset PDF Fresh Placement Execution

## Status

- Controlled manual fresh-placement execution recorded.
- Placement complete.
- Extraction not authorized.

## Current checkpoint

- Branch: `phase-020-real-asset-pdf-extraction`
- Pre-placement HEAD: `85677ad`
- PR-020A and PR-020B are committed on the phase branch.
- `main` remains at `86c2a7f`.
- The phase branch is not merged.
- No official Phase 20 tag exists.

## Purpose

Record the already approved manual placement of one real PDF at the exact controlled sandbox target without opening, reading, parsing, or extracting PDF content.

PR-020C records placement only. It does not approve extraction.

## Execution scope

The placement scope was limited to:

- one approved manual placement
- one exact sandbox target
- manual action performed outside RIE
- no source discovery or scan
- no wildcard path
- no recursion
- no batch operation
- no production source path recorded

The exact sandbox target is:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

RIE did not search for, locate, or copy the source PDF.

## Metadata verification result

Metadata-only verification recorded:

- target directory exists: `True`
- target file exists: `True`
- sandbox item count: `1`
- filename: `real-asset-smoke-source.pdf`
- extension: `.pdf`
- byte size: `987120`
- SHA256: `E65168E219E41868D0DEB408F6D636BABDC7EC7DB8C8F6BCCA812B4EAF2079BF`
- Git state: untracked
- `git ls-files --stage` output for the PDF: empty
- PDF staged: `False`
- PDF committed: `False`

The production source path was not requested or recorded.

## Content-access boundary

Metadata verification did not authorize or perform:

- opening PDF content
- reading PDF text
- parsing PDF objects
- extracting text
- extracting images
- OCR
- AI inference
- Evidence creation
- Knowledge creation
- Product Knowledge creation
- Official Knowledge creation
- Prompt Candidate creation

No parser was invoked. No text or image extraction occurred.

## Repository boundary

PR-020C changes no source code, tests, dependencies, virtual environment, or locked documents.

The placement PDF is a local real-asset artifact and is not a repository change authorized for staging or commit.

## Git boundary

- The real PDF remains untracked.
- The real PDF must never be staged or committed.
- Only the PR-020C document may later be committed.
- Any accidental staging or tracking is a hard stop.
- Documentation commit preparation must select the PR-020C document explicitly and exclude the PDF.

## Extraction boundary

Fresh placement does not authorize extraction.

Any later extraction requires metadata verification and a separately approved extraction execution review. The result boundary remains unchanged:

- full `extracted_text` must not be exposed
- extracted PDF text is not Evidence
- bounded `text_preview` is not Knowledge
- no Prompt Candidate may be created

## Decision

PR-020C records successful controlled fresh placement only.

PR-020C does not approve extraction.

The recommended next PR is:

`PR-020D - Controlled Real Asset PDF Extraction Target Metadata Verification`

PR-020D must remain metadata-only and review-first.

## Acceptance criteria

- Exactly one real PDF exists at the exact sandbox target.
- The filename is `real-asset-smoke-source.pdf`.
- The extension is `.pdf`.
- The byte size is `987120`.
- The SHA256 is `E65168E219E41868D0DEB408F6D636BABDC7EC7DB8C8F6BCCA812B4EAF2079BF`.
- The PDF is untracked and unstaged.
- Only the PR-020C document is the intended repository change.
- No PDF content access or extraction occurred.
- No Evidence, Knowledge, Product Knowledge, Official Knowledge, or Prompt Candidate was created.
