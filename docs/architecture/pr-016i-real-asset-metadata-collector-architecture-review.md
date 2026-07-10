# PR-016I - Real Asset Metadata Collector Architecture Review

## Status

Docs-only architecture review.

## Current Safe Checkpoint

```text
v0.16.7-rcis-real-asset-metadata-collection-contract-skeleton
ae57e1b feat: add real asset metadata collection contract skeleton
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
future metadata collector
```

## Purpose

The purpose of PR-016I is to review the architecture and safety boundary before any real filesystem metadata collector is implemented.

PR-016I does not implement a collector.

PR-016I does not approve running a collector.

PR-016I does not approve real asset content reads.

## Collector Boundary

Metadata collector is not scanner.

Metadata collector is not content detector.

Metadata collector is not extractor.

Metadata collector is not evidence builder.

Metadata collector is not knowledge builder.

Metadata collector is not prompt builder.

Metadata collector must not call AI.

A future collector must remain metadata-only and must not infer product meaning, claims, benefits, personas, prompts, evidence, or knowledge from assets.

## Allowed Future Collector Behavior

The following behavior is discussed only as future design. It is not approved for implementation in PR-016I.

A future collector may eventually be allowed to read limited filesystem metadata only after all gates approve:

```text
- root path supplied explicitly
- non-recursive only by default
- read-only only
- no mutation
- no file content reads
- no content-derived type detection
- no automatic evidence creation
- no automatic knowledge creation
```

Potential future metadata fields:

```text
- path as string
- relative_path as string
- exists
- is_file
- size
- suffix
- error
```

These fields are already represented by `RealAssetMetadataDryRunItem`, but PR-016I must not implement collection.

## Forbidden Future Collector Behavior

A future metadata collector must not perform:

```text
- recursive unrestricted scanning
- open
- read_bytes
- reading PDF text
- reading image pixels
- OCR
- MIME/content detection
- calling CreativeAssetTypeDetector
- calling CreativeAssetBatchScanner
- using extractor modules
- using evidence modules
- using knowledge modules
- using prompt modules
- calling AI
- mutating, moving, renaming, deleting, or writing files
- deriving product name, claim, benefit, persona, prompt, or knowledge from assets
```

## Relationship to RealAssetMetadataCollectionContract

Future collector must run only if `RealAssetMetadataCollectionDecision.allowed` is `True`.

Future collector must refuse to run if `allow_filesystem_metadata` is not explicitly approved in a later PR.

PR-016H currently blocks `allow_filesystem_metadata=True`.

Therefore PR-016I must not claim the collector is currently allowed to run.

Blocked upstream decisions must remain blocked.

## Important Design Decision

PR-016I recommends one more explicit implementation review before any real metadata collector is allowed to touch filesystem metadata.

PR-016J may be considered as a collector skeleton only if it remains safe:

```text
- synthetic tests only
- no real folders
- no real asset scanning
- no file content reads
- no scanner/detector usage
- no evidence or knowledge artifacts
```

If PR-016J cannot preserve that boundary, another contract-only step should happen first.

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
RealAssetMetadataCollector
    ->
RealAssetMetadataDryRunBoundaryResult or future collection result
```

PR-016I does not implement this.

PR-016I does not approve running this.

Future collector output must remain metadata-only and must not become Evidence.

## Relationship to Existing Scanner and Detector

`CreativeAssetBatchScanner` remains outside this workflow.

`CreativeAssetTypeDetector` remains outside this workflow.

Existing scanner and detector code may continue to exist for synthetic or existing ingestion tests, but they are not approved for the real asset metadata-only workflow.

The reason is architectural and safety-related: this workflow must not route through content-derived type detection.

## Forbidden Scope for PR-016I

PR-016I must not include:

```text
- production code changes
- test changes
- real asset scans
- folder inspection
- file reads
- filesystem metadata API calls
- Path.exists
- Path.stat
- Path.iterdir
- Path.rglob
- open
- read_bytes
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

PR-016I approves architecture review only.

It does not approve collector implementation.

It does not approve collector execution.

It does not approve filesystem metadata APIs.

It does not approve content reads, scanner/detector use, extraction, evidence creation, knowledge creation, prompt generation, or AI calls.
