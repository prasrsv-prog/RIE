# PR-017B - Controlled Real Asset Fixture Policy Review

Status:
Docs-only fixture policy review.

Current checkpoint:
v0.17.0-rcis-controlled-real-asset-smoke-test-architecture-review
940b182 docs: review controlled real asset smoke test architecture

## Context

PR-016 is phase complete and established the metadata-only dry-run foundation for controlled real asset work.

PR-017A is complete and reviewed the architecture boundary for the controlled real asset smoke test phase.

PR-017B defines the fixture policy before any controlled real asset sample is copied, referenced, scanned, or read.

PR-017B must not implement fixture loading.

PR-017B must not create fixture files.

PR-017B must not touch real assets.

## Fixture Boundary

A controlled fixture means an intentionally selected sandbox copy.

A controlled fixture does not mean a production RSV asset folder.

A controlled fixture does not mean repository-wide sample discovery.

A controlled fixture does not mean recursive asset discovery.

A controlled fixture does not authorize content extraction.

A controlled fixture does not authorize Evidence creation.

A controlled fixture does not authorize Knowledge creation.

A controlled fixture does not authorize Prompt Candidate generation.

## Allowed Future Fixture Scope

The following scope may be discussed for future PR-017 work only. PR-017B does not implement it.

Future controlled fixture set may contain:

- exactly 1 product specification PDF
- 1 to 3 product photos JPEG/PNG
- all files must be sandbox copies
- all files must be read-only from the RIE perspective
- fixture folder must be explicit
- fixture files must be intentionally selected
- max item count must be explicit and small

## Forbidden Fixture Sources

Future controlled fixtures must not come from:

- production RSV asset folders directly
- locked or SSOT documents as mutable fixtures
- broad product asset directories
- user desktop or downloads folders
- repository root
- current working directory
- auto-discovered folders
- recursive folder trees

## Required Future Fixture Metadata

A future fixture manifest or contract should record:

- fixture_id
- source_label
- fixture_path as string
- fixture_type
- allowed_for_metadata
- allowed_for_pdf_text_extraction
- allowed_for_image_metadata
- allowed_for_evidence
- notes

These are policy fields only for future review.

Do not implement them in PR-017B.

## Fixture Type Policy

Allowed future fixture types:

- product_spec_pdf
- product_photo_jpeg
- product_photo_png

Forbidden future fixture types unless later reviewed:

- official_knowledge_base
- master_asset_library
- locked_governance_doc
- prompt_template
- generated_prompt
- unknown_directory
- recursive_folder

## Evidence Boundary

Metadata fixture inspection is not Evidence.

Fixture policy is not Evidence.

PDF text extraction from a fixture may become Evidence only after a later controlled review.

Image metadata is not image understanding.

Image pixels must not be interpreted by this policy.

No product claims, benefits, persona, or prompt should be inferred from fixture presence.

## Relationship To PR-016 Foundation

The PR-016 metadata-only chain remains the entry gate.

RealFilesystemMetadataAdapter can only operate on an explicit fixture folder in later PRs.

RealFilesystemMetadataAdapterSafetyContract remains required.

CreativeAssetBatchScanner remains outside this workflow.

CreativeAssetTypeDetector remains outside this workflow.

## Recommended Next PR

PR-017C - Controlled Real Asset Fixture Contract

PR-017C should add a contract skeleton only.

PR-017C should not load fixture files.

PR-017C should not read filesystem.

PR-017C should use synthetic tests only.

## Forbidden Scope For PR-017B

PR-017B forbids:

- production code changes
- test changes
- fixture creation
- fixture loading
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
