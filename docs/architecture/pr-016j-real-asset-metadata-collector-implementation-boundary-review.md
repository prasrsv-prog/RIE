# PR-016J - Real Asset Metadata Collector Implementation Boundary Review

## Status

Docs-only implementation boundary review.

## Current Safe Checkpoint

```text
v0.16.8-rcis-real-asset-metadata-collector-architecture-review
af4a8e6 docs: review real asset metadata collector architecture
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
future RealAssetMetadataCollector
```

## Purpose

The purpose of PR-016J is to define the implementation boundary before any `RealAssetMetadataCollector` code is added.

PR-016J does not implement collector code.

PR-016J does not approve collector execution.

PR-016J does not approve filesystem metadata access yet.

PR-016J exists to decide the safe shape of PR-016K.

## Implementation Boundary Decisions

### Filesystem APIs in PR-016K

Decision:

```text
- no real filesystem APIs in PR-016K
- PR-016K should be synthetic-first collector skeleton only
- filesystem access must wait for a later controlled PR
```

PR-016K must not call `Path.exists`, `Path.stat`, `Path.iterdir`, `Path.rglob`, `os.stat`, `os.scandir`, `open`, or `read_bytes`.

### Pathlib Usage in PR-016K

Decision:

```text
- no pathlib.Path in collector skeleton input/output
- keep path and relative_path as strings
- avoid executing filesystem behavior
```

Strings are sufficient for the PR-016K skeleton because no real filesystem operation is approved.

### CreativeAssetBatchScanner Usage in PR-016K

Decision:

```text
- no
```

`CreativeAssetBatchScanner` routes into `CreativeAssetTypeDetector`.

It is not approved for the real asset metadata-only workflow.

### CreativeAssetTypeDetector Usage in PR-016K

Decision:

```text
- no
```

`CreativeAssetTypeDetector` performs content reads using `path.read_bytes()`.

It is outside metadata-only collector work.

### Evidence Creation in PR-016K

Decision:

```text
- no
```

Metadata collector output is not Evidence.

### Knowledge or Prompt Candidate Creation in PR-016K

Decision:

```text
- no
```

Metadata collector output is not Official Knowledge, Product Knowledge, Prompt Candidate, or Final Prompt.

### Recursive Collection in PR-016K

Decision:

```text
- no
```

Recursive collection remains unapproved.

### PDF or Image Parsing in PR-016K

Decision:

```text
- no
```

PR-016K must not parse PDF content, image content, OCR text, image pixels, captions, MIME/content type, or any product meaning.

## Allowed Future PR-016K Skeleton Shape

This section discusses future design only. PR-016J does not implement this.

PR-016K may add:

```text
- RealAssetMetadataCollector skeleton class
- RealAssetMetadataCollectionRequest frozen dataclass
- RealAssetMetadataCollectionResult frozen dataclass
- synthetic input only
- supplied metadata items only
- no filesystem access
- no Path usage
- no scanner/detector imports
- no extractor/evidence/knowledge/prompt imports
```

Potential PR-016K API shape:

```text
RealAssetMetadataCollector.collect(
    decision: RealAssetMetadataCollectionDecision,
    items: tuple[RealAssetMetadataDryRunItem, ...] = (),
) -> RealAssetMetadataCollectionResult
```

Because PR-016H currently blocks `allow_filesystem_metadata=True`, PR-016K must not use filesystem APIs.

PR-016K may only pass through supplied synthetic metadata items when `decision.allowed` is `True`.

If `decision.allowed` is `False`, the collector skeleton must return a blocked result.

## Future Real Filesystem Metadata Access

Real filesystem metadata access must be deferred to a later PR after PR-016K.

That later PR must explicitly review:

```text
- exact filesystem APIs
- exact non-recursive behavior
- explicit root handling
- permission error behavior
- symlink behavior
- file count limit
- error item representation
- no content reads
- no mutation
```

No future PR may assume filesystem metadata access is already approved by PR-016J.

## Forbidden Scope for PR-016J

PR-016J must not include:

```text
- production code changes
- test changes
- collector implementation
- filesystem calls
- Path.exists/stat/iterdir/rglob
- os.stat/os.scandir
- open/read_bytes
- real asset scans
- folder inspection
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

PR-016J approves an implementation boundary review only.

PR-016J does not approve collector code.

PR-016J does not approve collector execution.

PR-016J does not approve filesystem metadata access.

PR-016K should be a synthetic-first collector skeleton only, with supplied metadata items and no filesystem behavior.
