# PR-017A - Controlled Real Asset Smoke Test Architecture Review

Status:
Docs-only architecture review.

Current checkpoint:
v0.16.14-rcis-controlled-metadata-only-dry-run-smoke-flow
cf9ac10 test: add controlled metadata-only dry-run smoke flow

## Context

PR-016 is phase complete and established the metadata-only dry-run foundation for real asset work. Completed PR-016 capabilities include:

- RealAssetSandboxPolicy
- RealAssetDryRunContract
- RealAssetMetadataDryRunBoundary
- RealAssetMetadataCollectionContract
- RealAssetMetadataCollector
- RealFilesystemMetadataAdapter
- RealFilesystemMetadataAdapterSafetyContract
- Controlled metadata-only dry-run smoke flow using tmp_path only

Current approved PR-016 architecture:

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
RealFilesystemMetadataAdapterSafetyContract
    ->
RealFilesystemMetadataAdapter
```

PR-017A defines the architecture and safety boundary for the next phase:
PR-017 - Controlled Real Asset Evidence Smoke Test.

PR-017A must not implement anything. It defines the safe boundary before any real asset sample is touched.

## Boundary Statements

PR-017 is not a general real asset scan.

PR-017 is not a repository-wide scan.

PR-017 is not a recursive scan.

PR-017 is not automatic knowledge creation.

PR-017 is not prompt generation.

PR-017 is not AI inference.

PR-017 is not mutation of files or locked documents.

## Controlled Sample Scope

Future PR-017 work may use only:

- 1 product specification PDF
- 1 to 3 product photos JPEG/PNG
- sandbox copy only
- read-only
- explicit test fixture folder only
- no recursive scan
- no mutation

PR-017A does not approve using production RSV asset folders directly.

PR-017A does not approve modifying source assets.

PR-017A does not approve using locked or SSOT documents as mutable fixtures.

## Sample Handling Rules

Future controlled samples must follow these rules:

- use sandbox copies only
- never mutate original files
- fixture location must be explicit
- no default root
- no current working directory scan
- no project-wide scan
- no recursive scan
- max item count must be small and explicit
- sample files must be intentionally selected
- sample files must not be auto-discovered from a broad folder

## Evidence Boundary

Metadata-only results are not Evidence.

PDF text extraction may become Evidence only in a later controlled PR after explicit approval.

Image metadata is not image understanding.

Image pixels must not be interpreted in PR-017A.

Product name, claim, benefit, persona, and prompt must not be inferred.

Official Knowledge must not be created automatically.

Product Knowledge must not be created automatically.

Prompt Candidate must not be created automatically.

## Relationship To PR-016 Foundation

The PR-016 metadata-only chain remains the entry gate for controlled real asset work.

RealFilesystemMetadataAdapter may be used only under an explicit fixture root and safety contract.

No scanner or detector should be used for the PR-017 real asset workflow.

Existing CreativeAssetBatchScanner remains outside the controlled real asset workflow.

Existing CreativeAssetTypeDetector remains outside the controlled real asset workflow because it performs content reads.

The metadata-only smoke flow does not authorize content extraction.

## Future PR-017 Stages

Recommended staged PRs:

- PR-017B - Controlled Real Asset Fixture Policy Review
- PR-017C - Controlled Real Asset Fixture Contract
- PR-017D - Controlled Real Asset Metadata Smoke Test
- PR-017E - Controlled PDF Text Evidence Review
- PR-017F - Controlled PDF Text Evidence Smoke Test
- PR-017G - Controlled Image Metadata Review
- PR-017H - Controlled Image Metadata Smoke Test

The exact stages may be adjusted after review.

## Allowed Future Work

The following work may be discussed for later PR-017 stages, but is not implemented or approved by PR-017A:

- fixture policy
- fixture contract
- metadata-only smoke over selected sandbox fixture files
- later controlled PDF text extraction review
- later controlled image metadata review

## Forbidden Scope For PR-017A

PR-017A forbids:

- production code changes
- test changes
- filesystem calls
- real asset scans
- folder inspection
- content reads
- PDF parsing
- image parsing
- OCR
- scanner or detector usage
- evidence creation
- knowledge creation
- prompt creation
- AI calls
- API, CLI, or dashboard work
- locked or SSOT document changes
- master asset library changes
- registry autoloading

## Acceptance Criteria

- Only one docs file added.
- Full tests pass.
- No non-ASCII or garbled characters remain.
- No commit.
