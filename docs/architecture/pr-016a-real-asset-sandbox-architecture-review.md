# PR-016A — Real Asset Sandbox Architecture Review

## Status

Architecture Review Only

## Current Safe Checkpoint

```text
v0.15.2-rcis-evidence-workflow-preflight-skeleton
9bc113f merge: pr-015c evidence workflow preflight skeleton
```

## Context

PR-016 begins the Real Asset Sandbox / Dry-Run Foundation.

This phase is part of Jalur B:

```text
PR-015 — Evidence Workflow Gate / Preflight Foundation
PR-016 — Real Asset Sandbox / Dry-Run Foundation
PR-017 — Controlled Real Asset Evidence Smoke Test
```

The purpose of PR-016 is to prepare the engine for controlled real asset testing with assets such as:

```text
- one product specification PDF
- one to three product photos
- sandbox copy only
- read-only mode
```

PR-016A does not implement real asset testing. It reviews the safest architecture boundary first.

## Current Ingestion Structure

Current ingestion files are under:

```text
src/rie/ingestion
```

Relevant current files:

```text
src/rie/ingestion/creative_asset_batch_scanner.py
src/rie/ingestion/creative_asset_type_detector.py
src/rie/ingestion/creative_asset_scan_report_serializer.py
src/rie/ingestion/creative_asset_scan_item.py
src/rie/ingestion/creative_asset_scan_report.py
src/rie/ingestion/creative_asset_type.py
src/rie/ingestion/scan_assets.py
src/rie/ingestion/inspect_scan_report.py
src/rie/ingestion/inspect_unknown_assets.py
src/rie/ingestion/unknown_asset_header_inspector.py
```

Current tests are under:

```text
tests/ingestion
```

## Current Behavior

The current `CreativeAssetBatchScanner`:

```text
- iterates files from a folder
- optionally scans recursively
- checks whether paths are files
- detects asset type
- reads file size with stat
- records scan errors
- returns CreativeAssetScanReport
```

The current `CreativeAssetTypeDetector`:

```text
- reads file bytes
- detects PNG
- detects JPEG
- detects PDF
- detects WEBP
- detects TIFF
- detects MP4
- detects ZIP container
- detects UTF-8 text
- returns UNKNOWN when content cannot be classified
```

The current scan report serializer:

```text
- serializes root
- serializes total file count
- serializes counts by asset type
- serializes failed count
- serializes item path
- serializes asset type
- serializes size
- serializes error
```

## Key Risk

The current type detector uses full file reads for detection.

For real assets, especially PDF specification documents, photos, videos, or large product files, this is not ideal for a first sandbox dry-run.

The first real asset sandbox must not perform full-content parsing or extraction.

## Required Boundary Distinction

PR-016 must distinguish these levels:

```text
Level 1 — Metadata-only dry-run
Level 2 — Header-only type detection
Level 3 — Text/image/PDF extraction
Level 4 — Evidence creation
Level 5 — Knowledge creation
Level 6 — Prompt/brief generation
```

PR-016A approves only Level 1 and reviews Level 2.

It does not approve Levels 3–6.

## Real Asset Sandbox Definition

A real asset sandbox is a controlled folder used for safe dry-run testing.

It must use:

```text
- copied sample files
- small sample size
- read-only behavior
- explicit input path
- explicit output path when needed
- no default production folder
- no recursive scan unless explicitly requested
```

The sandbox must not use:

```text
- master production asset library directly
- locked / SSOT documents directly
- uncontrolled asset folders
- automatic registry discovery
- hidden default paths
```

## Approved Future Test Asset Types

After PR-016 and PR-017 are ready, controlled tests may use:

```text
- one PDF product specification
- one to three product photos
- small copied sample folder
```

Allowed file types for sandbox discovery may include:

```text
PDF
PNG
JPEG
WEBP
TIFF
UTF8_TEXT
UNKNOWN
```

But detection must not imply evidence eligibility, official status, product knowledge, or prompt readiness.

## Sandbox Rules

The sandbox must be:

```text
read-only
explicit
small
inspectable
repeatable
safe to delete
separate from production assets
```

The sandbox must never:

```text
modify files
move files
rename files
delete files
write metadata to source files
change file timestamps intentionally
write sidecar metadata next to source assets
infer product knowledge
create official knowledge
create prompt candidates
call AI
```

## Dry-Run Rules

Dry-run mode may produce a report.

The report may include:

```text
- sandbox root
- total discovered files
- relative or string path references
- file size
- detected asset type
- scan error
- dry-run mode name
```

The report must not include:

```text
- extracted PDF text
- OCR text
- image captions
- product names inferred from image
- marketing claims
- product knowledge
- prompt candidates
- final prompts
- AI-generated descriptions
- Official Knowledge items
```

## Header-Only Detection Direction

Future PR-016 implementation should prefer header-only detection for binary assets.

The detector should not need to read entire files to classify:

```text
PDF
PNG
JPEG
WEBP
TIFF
MP4
ZIP container
```

A future implementation may introduce a limited read size, for example only the first N bytes.

This review does not implement that change.

## Relationship to Evidence Workflow

PR-015 established:

```text
EvidenceWorkflowGate
EvidenceWorkflowPreflight
```

PR-016 should not bypass that work.

However, PR-016A does not integrate sandbox scanning with evidence workflow yet.

Real asset sandbox discovery is not the same as evidence creation.

```text
Sandbox scan report ≠ Evidence
Sandbox scan report ≠ Official Knowledge
Sandbox scan report ≠ Product Knowledge
Sandbox scan report ≠ Prompt Candidate
```

## Relationship to PDF Specification Products

PDF product specification testing is an important future target.

But PR-016A does not approve PDF content extraction.

Approved future sequence:

```text
sandbox copy of one product PDF
    ↓
metadata/header dry-run
    ↓
scan report inspection
    ↓
later controlled extraction review
    ↓
later evidence smoke test
```

Not approved:

```text
PDF specification
    ↓
automatic Official Knowledge
```

## Relationship to Product Photos

Product photo testing is also a future target.

But PR-016A does not approve image interpretation.

Approved future sequence:

```text
sandbox copy of one to three product photos
    ↓
metadata/header dry-run
    ↓
scan report inspection
    ↓
later visual evidence review
```

Not approved:

```text
product photo
    ↓
automatic product knowledge
```

## Proposed PR-016B Direction

PR-016B may implement a minimal sandbox policy or dry-run contract.

Possible files:

```text
src/rie/ingestion/real_asset_sandbox_policy.py
tests/ingestion/test_real_asset_sandbox_policy.py
```

Possible concepts:

```text
RealAssetSandboxPolicy
RealAssetSandboxDecision
```

The first implementation should remain small and must not scan real assets automatically.

Alternative possible files:

```text
src/rie/ingestion/real_asset_dry_run_mode.py
tests/ingestion/test_real_asset_dry_run_mode.py
```

## Forbidden Scope for PR-016A

PR-016A must not:

```text
modify production code
modify tests
parse PDFs
parse images
read real product assets
create evidence
create Official Knowledge
create Product Knowledge
create Prompt Candidate
create Final Prompt
call AI
add dashboard work
add API work
modify locked / SSOT documents
modify master asset library
add default folder discovery
add automatic registry loading
```

## Decision

PR-016A approves the architecture direction for a real asset sandbox.

The first safe implementation should support a small, explicit, read-only dry-run boundary.

The recommended next step is:

```text
PR-016B — Real Asset Sandbox Policy Skeleton
```

PR-016B should remain small, synthetic-test-only, and should not scan real assets yet.
