# PR-016C - Real Asset Dry-Run Contract Review

## Status

Architecture Review Only

## Current Safe Checkpoint

```text
v0.16.1-rcis-real-asset-sandbox-policy-skeleton
40d7967 merge: pr-016b real asset sandbox policy skeleton
```

## Context

PR-016 prepares the Real Asset Sandbox / Dry-Run Foundation.

Completed steps:

```text
PR-016A - Real Asset Sandbox Architecture Review
PR-016B - Real Asset Sandbox Policy Skeleton
```

PR-016C reviews the dry-run contract before any implementation touches real asset folders.

## Purpose

The purpose of a real asset dry-run is to inspect whether a sandbox configuration and asset discovery flow can run safely without creating downstream artifacts.

A dry-run may describe what would be scanned or reported, but it must not perform content extraction or knowledge generation.

## Approved Scope

PR-016C approves only a contract review.

It may define future concepts such as:

```text
RealAssetDryRunContract
RealAssetDryRunResult
RealAssetDryRunItem
```

This PR does not implement them.

## Dry-Run Position in Architecture

The dry-run contract sits after sandbox policy and before any real scan or extraction.

```text
RealAssetSandboxPolicy
    ->
RealAssetSandboxDecision
    ->
RealAssetDryRunContract
    ->
future dry-run execution
```

The dry-run contract is not evidence workflow.

```text
Dry-run result != Evidence
Dry-run result != Official Knowledge
Dry-run result != Product Knowledge
Dry-run result != Prompt Candidate
Dry-run result != Final Prompt
```

## Required Contract Boundary

The dry-run contract must separate these stages:

```text
1. sandbox policy validation
2. dry-run contract validation
3. future metadata-only discovery
4. future header-only type detection
5. future extraction
6. future evidence creation
7. future knowledge creation
```

PR-016C approves only stages 1-2 at the architecture level.

## Future Dry-Run Result Shape

A future dry-run result may include:

```text
- allowed
- reason
- root
- recursive
- read_only
- mode
- planned_scan_allowed
- planned_real_asset_reads_allowed
- planned_mutation_allowed
- item_count
- items
```

For PR-016C, this is only a contract direction.

## Future Dry-Run Item Shape

A future dry-run item may include:

```text
- path
- relative_path
- exists
- is_file
- size
- detected_asset_type
- error
```

But PR-016C does not approve real file inspection yet.

## Approved Dry-Run Modes

The architecture should recognize separate dry-run modes:

```text
metadata_only
header_only
extraction_preview
```

Only `metadata_only` may be considered for the first implementation.

`header_only` must require additional review.

`extraction_preview` is explicitly not approved in PR-016C.

## Forbidden Dry-Run Output

A dry-run report must not include:

```text
- extracted PDF text
- OCR text
- image captions
- product descriptions inferred from images
- marketing claims
- product benefits
- product knowledge
- Official Knowledge
- Evidence objects
- Prompt Candidates
- Final Prompts
- AI-generated descriptions
```

## Relationship to PR-016B Policy

PR-016B introduced sandbox policy validation.

The dry-run contract must respect policy decisions.

If the sandbox policy blocks execution, the dry-run contract must not allow downstream scanning.

```text
blocked sandbox policy
    ->
blocked dry-run
    ->
no scan
```

## Relationship to Current Ingestion Scanner

Current ingestion scanner already exists and can scan files.

However, PR-016C does not approve direct use of the existing scanner for real assets yet.

Reason:

```text
The current asset type detector reads full file bytes for type detection.
```

Before using it for real product assets, the engine needs a safer metadata/header boundary.

## Relationship to Product Specification PDF

A product specification PDF may be used in a future controlled smoke test.

PR-016C does not approve PDF extraction.

Approved future direction:

```text
sandbox policy
    ->
dry-run contract
    ->
metadata-only dry-run
    ->
manual review
    ->
later header-only detection
    ->
later extraction review
```

Forbidden direction:

```text
PDF product specification
    ->
automatic Evidence
    ->
automatic Official Knowledge
```

## Relationship to Product Photos

Product photos may be used in a future controlled smoke test.

PR-016C does not approve image interpretation.

Approved future direction:

```text
sandbox policy
    ->
dry-run contract
    ->
metadata-only dry-run
    ->
manual review
    ->
later header-only detection
    ->
later visual evidence review
```

Forbidden direction:

```text
product photo
    ->
automatic Product Knowledge
    ->
automatic Prompt Candidate
```

## Proposed PR-016D Direction

Recommended next step:

```text
PR-016D - Real Asset Dry-Run Contract Skeleton
```

Possible files:

```text
src/rie/ingestion/real_asset_dry_run_contract.py
tests/ingestion/test_real_asset_dry_run_contract.py
```

The first skeleton should:

```text
- use synthetic tests only
- not touch filesystem
- not scan folders
- not parse files
- not create evidence
- not create knowledge
```

## Forbidden Scope for PR-016C

PR-016C must not:

```text
modify production code
modify tests
scan real assets
read files
parse PDFs
parse images
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
add automatic registry loading
```

## Decision

PR-016C approves the architecture direction for a dry-run contract layer.

The dry-run contract must remain separate from extraction, evidence creation, knowledge creation, and prompt generation.

The recommended next step is PR-016D - Real Asset Dry-Run Contract Skeleton.
