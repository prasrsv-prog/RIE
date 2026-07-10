# PR-016E - Real Asset Metadata-Only Dry-Run Planning Review

## Status

Docs-only architecture planning.

## Current Safe Checkpoint

```text
v0.16.3-rcis-real-asset-dry-run-contract-skeleton
d50735f merge: pr-016d real asset dry-run contract skeleton
```

## Context

PR-016 prepares the Real Asset Sandbox / Dry-Run Foundation.

Completed steps:

```text
PR-016A completed Real Asset Sandbox Architecture Review.
PR-016B completed Real Asset Sandbox Policy Skeleton.
PR-016C completed Real Asset Dry-Run Contract Review.
PR-016D completed Real Asset Dry-Run Contract Skeleton.
```

PR-016E defines the next safe boundary before any real asset metadata-only dry-run implementation.

## Purpose

The purpose of this review is to define what metadata-only means for future real asset dry-run work.

PR-016E does not implement a scanner, does not inspect folders, does not read files, and does not parse content.

## Metadata-Only Boundary

A future metadata-only dry-run may include only:

```text
- path
- relative_path
- exists
- is_file
- size
- suffix
- error
```

These fields describe file location and basic file-system metadata only.

Metadata-only dry-run must not include:

```text
- extracted PDF text
- OCR text
- image captions
- image interpretation
- content-derived asset type
- product names inferred from files/images
- marketing claims
- product benefits
- Evidence
- Official Knowledge
- Product Knowledge
- Prompt Candidate
- Final Prompt
- AI-generated descriptions
```

## Current Repo Risk

The current `CreativeAssetTypeDetector` uses `path.read_bytes()`.

Therefore, `CreativeAssetTypeDetector` is not approved for real asset metadata-only dry-run.

`CreativeAssetBatchScanner` is not approved for real asset metadata-only dry-run yet because it routes into `CreativeAssetTypeDetector`.

This distinction matters because content-derived type detection is not metadata-only.

## Approved Future Sequence

```text
RealAssetSandboxPolicy
    ->
RealAssetDryRunContract
    ->
future metadata-only dry-run boundary
    ->
manual review
    ->
later header-only detection review
    ->
later extraction review
```

## Forbidden Direction

```text
real product PDF/photo
    ->
CreativeAssetBatchScanner
    ->
CreativeAssetTypeDetector.read_bytes()
    ->
automatic evidence/knowledge
```

The current scanner and detector are useful for controlled synthetic and non-real-asset workflows, but PR-016E does not approve their direct use on real product assets.

## Relationship to PR-016B and PR-016D

`RealAssetSandboxPolicy` remains the first safety gate.

`RealAssetDryRunContract` remains the second safety gate.

A future metadata-only dry-run boundary must run only after both gates allow the configuration.

The metadata-only boundary must not weaken PR-016B or PR-016D. It must not convert a blocked sandbox policy or blocked dry-run contract into an allowed scan.

## Proposed Next PR

Recommended next step:

```text
PR-016F - Real Asset Metadata-Only Dry-Run Boundary Skeleton
```

Proposed future files for PR-016F:

```text
src/rie/ingestion/real_asset_metadata_dry_run_boundary.py
tests/ingestion/test_real_asset_metadata_dry_run_boundary.py
```

PR-016F should still use synthetic tests only and should not touch the filesystem yet.

The first skeleton should evaluate supplied metadata-like values only. It should not discover paths, scan folders, call `stat`, call `exists`, call `iterdir`, call `read_bytes`, use `CreativeAssetTypeDetector`, use `CreativeAssetBatchScanner`, call extractors, or create downstream artifacts.

## Forbidden Scope for PR-016E

PR-016E must not include:

```text
- production code changes
- test changes
- real asset scanning
- filesystem reads
- content reads
- header detection
- PDF parsing
- image parsing
- evidence creation
- knowledge creation
- prompt creation
- AI calls
- CLI work
- API work
- dashboard work
- locked / SSOT document changes
- master asset library changes
- automatic registry loading
```

## Decision

PR-016E approves a metadata-only planning boundary only.

Metadata-only does not mean content-derived type detection.

The current `CreativeAssetTypeDetector` and `CreativeAssetBatchScanner` must remain outside any real asset metadata-only dry-run until a later review approves a safer boundary.

The recommended next step is PR-016F - Real Asset Metadata-Only Dry-Run Boundary Skeleton.
