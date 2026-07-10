# PR-016L - Real Filesystem Metadata Access Review

## Status

Docs-only architecture and implementation safety review.

## Current Safe Checkpoint

```text
v0.16.10-rcis-real-asset-metadata-collector-skeleton
45379e0 feat: add real asset metadata collector skeleton
```

## Context

PR-016 prepares the Real Asset Sandbox / Dry-Run Foundation.

Completed steps:

```text
PR-016A completed Real Asset Sandbox Architecture Review.
PR-016B completed Real Asset Sandbox Policy Skeleton.
PR-016C completed Real Asset Dry-Run Contract Review.
PR-016D completed Real Asset Dry-Run Contract Skeleton.
PR-016E completed Real Asset Metadata-Only Dry-Run Planning Review.
PR-016F completed Real Asset Metadata-Only Dry-Run Boundary Skeleton.
PR-016G completed Real Asset Metadata Collection Safety Review.
PR-016H completed Real Asset Metadata Collection Contract Skeleton.
PR-016I completed Real Asset Metadata Collector Architecture Review.
PR-016J completed Real Asset Metadata Collector Implementation Boundary Review.
PR-016K completed Real Asset Metadata Collector Skeleton.
```

Current architecture:

```text
RealAssetSandboxPolicy
    ->
RealAssetDryRunContract
    ->
RealAssetMetadataDryRunBoundary
    ->
RealAssetMetadataCollectionContract
    ->
RealAssetMetadataCollector
    ->
future filesystem metadata access layer
```

## Purpose

The purpose of PR-016L is to review whether and how real filesystem metadata access may be introduced in a future PR.

PR-016L does not implement filesystem access.

PR-016L does not approve unrestricted scanning.

PR-016L does not approve content reads.

PR-016L does not approve recursive scans.

PR-016L does not approve scanner or detector usage.

PR-016L does not create evidence, knowledge, or prompt candidates.

## Key Decision

The next implementation PR after PR-016L may introduce a tightly constrained filesystem metadata adapter only if it follows the approved rules in this review.

PR-016L itself does not implement that adapter.

## Approved Future Filesystem Metadata Access Shape

This section discusses future design only. PR-016L does not implement filesystem metadata access.

A future adapter may be allowed to:

```text
- accept an explicit root path
- inspect only immediate children of root by default
- be non-recursive
- be read-only
- collect only metadata fields already represented by RealAssetMetadataDryRunItem
- represent permission or stat errors as metadata items with error text
- return a collection result without raising for individual item failures
```

Approved future metadata fields remain limited to:

```text
- path as string
- relative_path as string
- exists
- is_file
- size
- suffix
- error
```

These fields must not become content-derived asset classification or downstream artifact data.

## Filesystem APIs to Review

Allowed in a future controlled PR only:

```text
- Path.iterdir only for immediate children of an explicit root
- Path.stat only for metadata size and file status
- Path.is_file only if needed for metadata
- Path.exists only for explicit root validation
```

Still forbidden:

```text
- Path.rglob
- recursive globbing
- os.walk
- open
- read_bytes
- read_text
- PDF parsing
- image parsing
- OCR
- MIME/content detection
- reading file headers
- CreativeAssetTypeDetector
- CreativeAssetBatchScanner
- extractor modules
- evidence modules
- knowledge modules
- prompt modules
- AI calls
- mutation, write, rename, move, delete
```

## Safety Rules for Future Implementation

A future filesystem metadata adapter must preserve these rules:

```text
- explicit root only
- no default repository scan
- no current working directory scan by accident
- no automatic registry loading
- no locked/SSOT document modification
- no mutation
- no content read
- no product inference
- no evidence creation
- no knowledge creation
- no prompt generation
- small item count limit should be considered before implementation
- permission errors must become safe metadata errors
- symlink behavior must be explicitly defined before implementation
- recursive behavior remains blocked
```

## Relationship to Current RealAssetMetadataCollector

The existing `RealAssetMetadataCollector` is synthetic pass-through only.

It must not be modified to directly scan the filesystem in PR-016L.

A future filesystem adapter should be separate from the collector skeleton unless a later review approves integration.

The collector should continue to accept supplied `RealAssetMetadataDryRunItem` values.

## Recommended Next PR

Recommended next step:

```text
PR-016M - Real Filesystem Metadata Adapter Skeleton
```

PR-016M must still be conservative:

```text
- no real project-wide scan
- no recursive behavior
- no content reads
- no scanner/detector
- no evidence/knowledge/prompt
- likely tests should use temporary synthetic directories only if explicitly approved
- otherwise add another contract-only step first
```

## Forbidden Scope for PR-016L

PR-016L must not include:

```text
- production code changes
- test changes
- filesystem calls
- real asset scans
- folder inspection
- content reads
- scanner/detector usage
- PDF/image parsing
- evidence creation
- knowledge creation
- prompt creation
- AI calls
- API/CLI/dashboard work
- locked/SSOT document changes
- master asset library changes
- registry autoloading
```

## Acceptance Criteria

```text
- only one docs file added
- full tests pass
- no non-ASCII or garbled characters remain
- no commit
```

## Decision

PR-016L approves a filesystem metadata access review only.

It does not implement filesystem metadata access.

It does not approve unrestricted scans, recursive behavior, content reads, scanner/detector usage, evidence creation, knowledge creation, prompt generation, or AI calls.

Future filesystem metadata access must be introduced only through a later controlled PR with explicit API, root, error, symlink, count-limit, and non-recursive behavior rules.
