# PR-020G - Controlled Real Asset PDF Cleanup and Retention Decision

## Status

* Documentation-only cleanup and retention decision review.
* Controlled extraction execution is complete.
* The local real PDF has not yet been deleted.
* No additional extraction is authorized.

## Current checkpoint

* Branch: `phase-020-real-asset-pdf-extraction`
* Pre-decision HEAD: `a0631b0`
* PR-020A through PR-020F are committed on the phase branch.
* `main` remains at `86c2a7f`.
* The phase branch is not merged.
* No official Phase 20 tag exists.
* The real PDF remains local, untracked, and unstaged.

## Purpose

Decide whether the controlled real PDF should be retained temporarily or removed after the completed PR-020F extraction execution.

PR-020G records the decision only. It does not delete, move, rename, stage, commit, open, parse, or extract the PDF.

## Current real asset state

The exact local target is:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

Verified state:

* target directory exists: `True`
* target exists: `True`
* sandbox item count: `1`
* filename: `real-asset-smoke-source.pdf`
* extension: `.pdf`
* byte size: `987120`
* SHA256: `E65168E219E41868D0DEB408F6D636BABDC7EC7DB8C8F6BCCA812B4EAF2079BF`
* Git state: untracked
* PDF staged or tracked: `False`
* tracked diff: empty
* cached diff: empty

The metadata remains consistent with PR-020C, PR-020D, and PR-020F.

## Completed execution context

PR-020F performed exactly one approved bounded parser execution.

The bounded result was:

* extraction status: `empty`
* text length: `0`
* bounded text preview: empty
* extracted text included: `False`
* truncated: `False`
* extraction error: empty
* Evidence allowed: `False`

The execution did not authorize a second extraction attempt.

The `empty` result does not authorize OCR, image extraction, image understanding, page inspection, layout analysis, or AI inference.

## Retention options reviewed

### Option A - Temporary retention

Temporary retention would keep the untracked PDF in the sandbox for a later approved action.

This option is not selected because:

* the approved PR-020F execution is complete
* no additional parser execution is authorized
* no immediate reviewed phase requires the PDF
* retaining the real asset increases the risk of accidental staging, commit, access, or repeated extraction
* phase closure requires a controlled and reviewable real-asset state

### Option B - Controlled removal

Controlled removal deletes only the exact local sandbox target after a separately approved cleanup execution gate.

This option:

* reduces accidental real-asset exposure
* prevents unauthorized repeated extraction
* restores the sandbox to an empty local preparation state
* preserves all committed architecture and audit documentation
* does not delete or mutate any production source
* does not affect locked or SSOT documents

## Decision

Select **Option B - Controlled removal**.

The real PDF should be removed in:

`PR-020H - Controlled Real Asset PDF Cleanup Execution`

PR-020G does not itself authorize immediate deletion outside that gate.

PR-020H may delete only:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

The sandbox directory may remain as an empty local preparation artifact.

## Cleanup execution boundary

A later approved PR-020H execution may:

* verify the exact branch and expected HEAD
* verify the exact target path
* verify the filename, extension, byte size, and SHA256
* verify the sandbox contains exactly one item
* verify the PDF is untracked and unstaged
* delete only the exact sandbox target
* verify the target is absent afterward
* verify the sandbox item count is zero
* record the cleanup result in documentation

PR-020H must not:

* use wildcard deletion
* recursively delete directories
* delete the sandbox directory
* scan or access a production source path
* open or inspect PDF content
* execute the parser again
* extract text or images
* use OCR
* invoke AI
* create Evidence, Knowledge, Product Knowledge, Official Knowledge, or Prompt Candidate
* stage or commit the PDF
* modify source code, tests, dependencies, virtual environment, or locked documents

## Git boundary

* The real PDF must remain untracked and unstaged until controlled deletion.
* The real PDF must never be committed.
* Only the PR-020G decision document may be committed in this PR.
* Any accidental PDF staging or tracking is a hard stop.
* The deletion of an untracked local PDF must not create a tracked repository diff.

## Audit preservation

Cleanup must preserve the committed documentation records for:

* fresh placement
* metadata verification
* extraction execution review
* bounded extraction execution
* exact byte size and SHA256
* empty extraction result
* downstream prohibitions

Deleting the local PDF does not delete the audit trail.

## Downstream boundary

The cleanup decision does not authorize:

* another extraction execution
* OCR
* image extraction
* image understanding
* Evidence or Evidence Candidate creation
* Knowledge creation
* Product Knowledge creation
* Official Knowledge creation
* Prompt Candidate creation
* Final Prompt creation
* knowledge repository updates

## Recommended next PR

`PR-020H - Controlled Real Asset PDF Cleanup Execution`

PR-020H must begin with a pre-cleanup verification and explicit approval before deletion.

After PR-020H, the recommended next step is:

`PR-020I - Controlled Real Asset PDF Extraction Phase Closure Review`

## Acceptance criteria

* PR-020G is documentation-only.
* The cleanup decision selects controlled removal.
* The PDF still exists during PR-020G review and commit.
* The PDF remains untracked and unstaged.
* No parser execution or content access occurs.
* No real asset deletion occurs in PR-020G.
* Only the PR-020G document is the intended repository change.
* Cleanup is deferred to separately approved PR-020H.
