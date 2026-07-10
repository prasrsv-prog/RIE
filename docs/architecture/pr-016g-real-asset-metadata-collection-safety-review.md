# PR-016G - Real Asset Metadata Collection Safety Review

## Status

Docs-only architecture review.

## Current Safe Checkpoint

```text
v0.16.5-rcis-real-asset-metadata-only-dry-run-boundary-skeleton
be886fe merge: pr-016f real asset metadata-only dry-run boundary skeleton
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
```

Current architecture:

```text
RealAssetSandboxPolicy
    ->
RealAssetDryRunContract
    ->
RealAssetMetadataDryRunBoundary
    ->
future metadata collection safety review
    ->
future metadata collection contract skeleton
```

## Purpose

The purpose of PR-016G is to review the safety boundary before any real filesystem metadata collection exists.

PR-016G does not implement metadata collection.

PR-016G does not approve real asset content reads.

## Metadata Collection Boundary

Metadata collection is not scanning.

Metadata collection is not content detection.

Metadata collection is not extraction.

Metadata collection is not evidence creation.

Metadata collection is not knowledge creation.

Metadata collection is not prompt generation.

The metadata collection boundary must remain separate from content-derived classification, downstream artifact creation, and prompt generation.

## Allowed Filesystem Operations

For PR-016G itself:

```text
- none
```

For a future reviewed collector only:

```text
- possible narrow metadata-only operations may be discussed
- no filesystem operation is approved for implementation in PR-016G
```

Future approval must be explicit before any real filesystem metadata collection exists.

## Forbidden Operations

PR-016G does not approve:

```text
- open
- read_bytes
- content reads
- PDF parsing
- image parsing
- OCR
- MIME/content detection
- recursive unrestricted scans
- writes or mutation
- CreativeAssetTypeDetector
- CreativeAssetBatchScanner
- extractors
- evidence builders
- knowledge builders
- prompt builders
```

## Relationship to Existing Layers

`RealAssetSandboxPolicy` remains gate 1.

`RealAssetDryRunContract` remains gate 2.

`RealAssetMetadataDryRunBoundary` remains gate 3.

A future metadata collector must run only after all approved gates allow it.

PR-016G must not weaken blocked upstream decisions.

If any upstream gate blocks the flow, future metadata collection must remain blocked.

## Relationship to CreativeAssetBatchScanner

`CreativeAssetBatchScanner` is not approved for real asset metadata collection yet.

It routes into `CreativeAssetTypeDetector`.

Therefore it is not metadata-only safe for real assets.

## Relationship to CreativeAssetTypeDetector

`CreativeAssetTypeDetector` is not approved for real asset metadata collection.

It uses `path.read_bytes()`.

Therefore it performs content reads and must remain outside metadata-only work.

Content-derived type detection is not metadata-only collection.

## Proposed Future Architecture

```text
RealAssetSandboxPolicy
    ->
RealAssetDryRunContract
    ->
RealAssetMetadataDryRunBoundary
    ->
RealAssetMetadataCollectionContract
    ->
future metadata collector
```

## Proposed Next PR

Recommended next step:

```text
PR-016H - Real Asset Metadata Collection Contract Skeleton
```

PR-016H must still be synthetic-test-only and must not call filesystem APIs.

PR-016H must remain a contract skeleton only unless a later review explicitly approves real metadata collection.

## Forbidden Scope for PR-016G

PR-016G must not include:

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

PR-016G approves a safety review boundary only.

It does not approve real filesystem metadata collection.

It does not approve content reads, scanner/detector use, extraction, evidence creation, knowledge creation, or prompt generation.

Only after PR-016G is reviewed, merged, and tagged should PR-016H be considered.
