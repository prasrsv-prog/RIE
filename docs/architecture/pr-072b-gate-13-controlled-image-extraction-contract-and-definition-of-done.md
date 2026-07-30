# PR-072B Gate 13 Controlled Image Extraction Contract and Definition of Done

## Status

Canonical Gate 13 contract and Definition of Done.

This document authorizes only the bounded Gate 13 program described below. It does not by itself implement, execute, or close Gate 13.

## Accepted authority

- Gate 12 is closed and published at commit `991c98d22c0e58e2d5075685cfeebdbcd1e3112e`.
- The official Gate 12 annotated tag is `v0.68.0-rcis-official-image-source-domain-phase`.
- The accepted Official Image Source domain governs source identity, authority, rights, lifecycle, checksum, byte length, provenance, admission state, admission audit, and persistence round-trip.
- The accepted structural parser foundation recognizes JPEG, PNG, and WEBP and can return bounded structural facts.
- The accepted file-backed foundation can inspect a controlled image file without changing the accepted PDF workflow.
- Historical targeted acceptance contains 60 passing tests for the structural and file-backed foundation.
- Gate 14 and every downstream semantic capability remain unauthorized.

## Gate purpose

Gate 13 converts exactly one accepted Official Image Source and its exact governed input bytes into exactly one versioned factual Image Extraction Artifact.

The artifact contains structural facts only. It is not Evidence, Knowledge, a business decision, a prompt, or a semantic interpretation.

Extraction Result must not be promoted automatically to Evidence or Knowledge.

## Required input authority

Every Gate 13 extraction request must reference exactly one accepted Official Image Source record.

Before structural extraction begins, the implementation must prove all of the following:

- the Official Image Source record exists;
- its admission state is accepted;
- its authority and rights state permit the governed operation;
- its lifecycle state permits the governed operation;
- the presented source identifier matches the accepted record;
- the controlled source reference matches the accepted record;
- the exact input SHA-256 matches the accepted record;
- the exact input byte length matches the accepted record;
- declared media type and extension are present;
- provenance is present and unambiguous.

No file path, byte sequence, parser call, or convenience API may bypass the accepted Official Image Source record.

## Supported factual extraction boundary

Gate 13 may produce only deterministic structural facts for:

- JPEG;
- PNG;
- WEBP.

The initial factual field boundary is:

- artifact schema version;
- deterministic artifact identifier;
- Official Image Source identifier;
- input SHA-256;
- input byte length;
- declared media type;
- declared extension;
- detected structural format;
- pixel width;
- pixel height;
- parser identity;
- parser version;
- extraction status;
- controlled rejection code when unsuccessful.

A successful artifact must not contain a rejection code.

An unsuccessful artifact must not invent width, height, format, or any other fact that was not deterministically proven.

## Deterministic artifact identity

Artifact identity must be derived only from canonical contract fields.

Ambient time, machine name, user name, absolute local path, process identifier, random value, network state, and execution order must not affect the artifact identifier or canonical serialized bytes.

The same accepted Official Image Source record, exact input bytes, parser identity, parser version, and artifact schema version must produce the same factual artifact and the same canonical serialized representation.

## Versioned artifact contract

The Image Extraction Artifact must have an explicit schema version.

Schema version changes must be reviewed as a separate compatibility boundary.

Unknown schema versions must be rejected. Silent field addition, field removal, field reinterpretation, or fallback to a different schema version is forbidden.

The artifact model must reject:

- missing required fields;
- unknown fields;
- duplicate fields;
- malformed identifiers;
- malformed SHA-256 values;
- invalid byte lengths;
- unsupported formats;
- invalid dimensions;
- contradictory success and rejection states.

## Canonical serialization and round-trip

Gate 13 closure requires a deterministic canonical serialization contract.

The canonical representation must define:

- exact encoding;
- exact field names;
- exact field order or canonical ordering rule;
- exact boolean, integer, null, and string representation;
- exact newline and final-byte behavior;
- rejection of unknown or duplicate fields;
- stable SHA-256 and byte length for serialized artifacts.

For every accepted artifact:

`deserialize(serialize(artifact)) == artifact`

For every accepted canonical serialized artifact:

`serialize(deserialize(bytes)) == bytes`

Non-canonical but otherwise parseable input must be rejected unless a separate normalization contract is explicitly approved.

## Required controlled failures

The runtime must safe-stop with a stable controlled rejection code when any of the following occurs:

- Official Image Source record missing;
- Official Image Source not accepted;
- authority, rights, or lifecycle state disallows extraction;
- source identifier mismatch;
- controlled source reference mismatch;
- input SHA-256 mismatch;
- input byte-length mismatch;
- missing or ambiguous provenance;
- declared media type and extension conflict;
- declared classification and detected format conflict;
- unsupported format;
- malformed or truncated structural data;
- zero, invalid, or out-of-bound dimensions;
- explicit resource limit exceeded;
- parser identity or version mismatch;
- unsupported artifact schema version;
- artifact serialization or deserialization contract failure;
- deterministic output cannot be proven.

Native filesystem failures may remain native only when the accepted file boundary already requires that behavior and tests preserve it explicitly.

## Resource-boundary requirement

Before any new runtime implementation is accepted, exact byte, dimension, allocation, and read limits must be stated and tested.

Implicit library defaults are not an accepted resource contract.

The implementation must not perform hidden network access, hidden downloads, background model execution, or unbounded file reads.

## Synthetic-first evidence boundary

Implementation and acceptance must use controlled synthetic JPEG, PNG, and WEBP fixtures with exact bytes and expected structural facts.

Malformed, truncated, conflicting, unsupported, and resource-limit fixtures must also be synthetic and deterministic.

Real-asset execution remains unauthorized until a separate post-synthetic boundary is approved.

Tracked historical image assets must not be opened, decoded, rendered, inspected, or used as Gate 13 acceptance evidence under this contract.

## Definition of Done

Gate 13 is complete only when all criteria below are independently proven.

### Criterion 1 - Canonical contract

This document is committed and accepted as the canonical Gate 13 contract and Definition of Done.

### Criterion 2 - Official Image Source integration

Every extraction path requires one accepted Official Image Source record and revalidates exact source identity, checksum, byte length, declared classification, provenance, authority, rights, and lifecycle before extraction.

### Criterion 3 - Deterministic structural extraction

JPEG, PNG, and WEBP structural extraction produces only the accepted factual fields and is deterministic for identical governed inputs.

### Criterion 4 - Bounded file runtime

The file-backed runtime enforces explicit accepted resource limits, preserves native filesystem behavior where contracted, and does not change the accepted PDF workflow.

### Criterion 5 - Versioned Image Extraction Artifact

A strict versioned artifact model enforces required fields, exact types, state consistency, supported schema versions, and rejection of unknown or contradictory data.

### Criterion 6 - Canonical persistence round-trip

Canonical serialization, deserialization, SHA-256, byte length, and exact byte round-trip are proven for successful and rejected artifacts.

### Criterion 7 - Controlled failures

All required rejection conditions produce stable controlled outcomes without semantic inference, silent normalization, partial success, or fabricated facts.

### Criterion 8 - Acceptance evidence

Targeted synthetic tests prove positive, negative, determinism, integration, resource-boundary, and round-trip behavior. Fresh external build and installation acceptance must remain preserved when dependency or packaging scope changes.

### Criterion 9 - Scope preservation

No test or implementation reads pixels, extracts EXIF, performs OCR, generates previews, recognizes visual meaning, executes a model, or enters Gate 14.

### Criterion 10 - Publication closure

The exact Gate 13 implementation and evidence are independently reviewed, fast-forward published to main, and protected by the official annotated Phase 72 tag.

## Explicit non-authority

Gate 13 does not authorize:

- Gate 14 multimodal evidence or knowledge work;
- semantic image interpretation;
- OCR or text recognition;
- object, product, person, face, logo, scene, color, style, or attribute recognition;
- pixel reading or pixel-derived analysis;
- EXIF or other non-required metadata extraction;
- image rendering, previews, thumbnails, resizing, conversion, or transformation;
- embeddings, vectors, semantic indexes, ontologies, knowledge graphs, or automated inference;
- local or remote model execution;
- master asset library implementation;
- dashboard implementation;
- local AI connectors;
- creative workflow orchestration;
- automatic promotion from Extraction Result to Evidence or Knowledge;
- changes to the accepted PDF workflow;
- real-asset execution;
- dependency additions without a separate exact dependency boundary;
- CLI, registry, release, or downstream gate work unless separately authorized.

## Phase 72 repository boundary

PR-072B authorizes only:

- creation of branch `phase-072-controlled-image-extraction-gate-13` from accepted main commit `991c98d22c0e58e2d5075685cfeebdbcd1e3112e`;
- materialization of this document at `docs/architecture/pr-072b-gate-13-controlled-image-extraction-contract-and-definition-of-done.md`.

PR-072B does not authorize staging, commit, push, tag, implementation code, test changes, dependency changes, image execution, Python execution, pytest execution, or real-asset inspection.

## Next bounded operation

After independent acceptance of PR-072B materialization, the next operation is a separate docs-only stage, commit, push, and verification boundary for this exact document.

Implementation begins only after the canonical document is committed, published on the Phase 72 branch, and independently reviewed.

## Closure condition for PR-072B

PR-072B materialization is complete only when:

- the Phase 72 branch is created from the exact accepted checkpoint;
- this document is the only working-tree path;
- the document matches its exact approved SHA-256, byte length, LF count, ASCII-only representation, no-BOM state, and single-final-LF contract;
- no staging, commit, push, tag, implementation, test, dependency, image, model, or real-asset operation occurs.
