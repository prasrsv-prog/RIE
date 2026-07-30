# PR-072N Gate 13 Official Image Source Extraction Integration

## Status

Subordinate Gate 13 governed Official Image Source integration contract and implementation boundary.

This boundary closes only resolution of exactly one canonical persisted Official Image Source record and deterministic revalidation of its governed extraction authority before any structural parser call.

It does not implement parser orchestration, artifact construction, artifact file persistence invocation, registry scanning, real-asset execution, or Gate 14.

## Accepted authority

- The canonical Gate 13 contract is accepted.
- The Gate 12 Official Image Source domain, record model, lifecycle rules, admission audit, and canonical persistence codec are accepted.
- The versioned factual Image Extraction Artifact model is accepted.
- Canonical artifact serialization and exact byte round-trip are accepted.
- The bounded artifact file-persistence service is accepted.
- PR-072M selected `GATE_13_OFFICIAL_IMAGE_SOURCE_INTEGRATION_NOT_IMPLEMENTED` as the single next gap.
- Existing accepted Gate 12, Gate 13, parser, PDF workflow, and persistence modules remain unchanged.

## Runtime surface

The additive runtime module is:

`rie.extraction.official_image_source_extraction_integration`

The integration format identifier is:

`official_image_source_extraction_integration_v1`

The public resolution API is:

`resolve_and_validate_official_image_source_for_extraction`

The immutable result is:

`OfficialImageSourceExtractionValidationResult`

## Exactly one governed record

The caller provides either:

- exactly one canonical Official Image Source persistence payload; or
- `None`, which deterministically represents a missing record.

The integration decodes only that one canonical payload through the accepted Gate 12 codec.

The integration does not enumerate, search, mutate, or persist a registry. It does not select between multiple records and does not accept an untyped mapping as a record substitute.

Malformed, non-canonical, or otherwise invalid record bytes are rejected as `official_image_source_not_accepted`.

## Governed request inputs

Every validation call requires:

1. presented source identifier;
2. presented controlled source locator;
3. exact input bytes;
4. declared media type;
5. declared extension;
6. exactly one canonical Official Image Source payload or `None`.

The integration computes the input SHA-256 and byte length directly from the exact input bytes.

Presented source identifiers must also be compatible with the accepted Image Extraction Artifact identifier-token boundary.

## Deterministic revalidation order

Before any parser call, the integration validates:

1. declared media type and extension consistency;
2. record presence;
3. canonical record decoding;
4. source identifier equality;
5. controlled source locator equality;
6. admission status;
7. authority class and source-kind compatibility;
8. rights status;
9. lifecycle state;
10. input SHA-256 equality;
11. input byte-length equality;
12. one unambiguous provenance reference.

The same inputs produce the same result.

## Authority and source-kind policy

The accepted combinations are:

- `FILE` with `OFFICIAL_INTERNAL` or `OFFICIAL_PARTNER`;
- `REPOSITORY_ASSET` with `OFFICIAL_INTERNAL` or `OFFICIAL_PARTNER`;
- `CONTROLLED_EXTERNAL_REFERENCE` with `OFFICIAL_PARTNER` or `CONTROLLED_EXTERNAL`.

Every other source-kind and authority combination is rejected as `authority_rejected`.

## Rights policy

The extraction-permitting rights states are:

- `OWNED`;
- `LICENSED`;
- `APPROVED_INTERNAL_USE`.

`RESTRICTED` is rejected as `rights_rejected`.

## Admission and lifecycle policy

The record must have:

- `admission_status == ACCEPTED`; and
- `lifecycle_state == ACTIVE`.

Every other admission state is rejected as `official_image_source_not_accepted`.

Every other lifecycle state is rejected as `lifecycle_rejected`.

## Provenance rule

The result carries exactly one `provenance_reference_id`.

For a root source, the provenance reference is the source identifier itself.

For a non-root source, the provenance reference is the accepted `provenance_parent_id`.

The Gate 12 model remains authoritative for the validity and non-self-reference of the parent identifier.

This integration does not traverse a provenance graph.

## Declared classification

The accepted declared pairs are exactly:

- `image/jpeg` with `.jpg`;
- `image/jpeg` with `.jpeg`;
- `image/png` with `.png`;
- `image/webp` with `.webp`.

Unsupported or conflicting pairs return `declared_media_type_extension_conflict`.

No classification is inferred from the locator or bytes in this integration boundary.

## Controlled result

The result contains exactly these eleven fields:

1. integration version;
2. validation status;
3. presented source identifier;
4. presented source locator;
5. computed input SHA-256;
6. computed input byte length;
7. declared media type;
8. declared extension;
9. accepted Official Image Source or null;
10. provenance reference identifier or null;
11. controlled Image Extraction Artifact rejection code or null.

An accepted result contains one exact Official Image Source and no rejection code.

A rejected result contains no Official Image Source, no provenance reference, and exactly one existing controlled Image Extraction Artifact rejection code.

Programmer contract misuse remains a deterministic type or value error.

## Explicit exclusions

This boundary does not:

- invoke the image structure parser;
- inspect or derive image dimensions;
- construct a successful or rejected Image Extraction Artifact;
- invoke canonical artifact serialization;
- invoke the artifact file-persistence service;
- read or write a source registry;
- scan a directory or repository;
- open an image file;
- decode pixels;
- extract EXIF;
- perform OCR or semantic interpretation;
- use a real asset;
- add dependencies;
- modify accepted Official Image Source types or codecs;
- modify accepted artifact, canonical-persistence, or file-persistence modules;
- modify the accepted PDF workflow;
- use network access;
- execute a model;
- enter Gate 14;
- stage, commit, push, merge, tag, or publish repository history.

## Acceptance evidence

Synthetic-only targeted tests must prove:

- exact integration version and eleven-field result order;
- successful internal, partner, and controlled-external policies;
- deterministic input SHA-256 and byte length;
- immutable result behavior;
- missing and invalid source-payload rejection;
- admission rejection;
- source identifier and locator mismatch rejection;
- checksum and byte-length mismatch rejection;
- authority/source-kind policy rejection;
- restricted-rights rejection;
- non-active lifecycle rejection;
- declared classification conflict rejection;
- artifact-compatible source identifier enforcement;
- root and non-root provenance-reference behavior;
- accepted and rejected result invariants;
- absence of parser, filesystem, network, clock, random, decoder, and model dependencies;
- compatibility with accepted Gate 12 Official Image Source and persistence tests;
- preservation of every accepted Gate 13, parser-foundation, Official Image Source, and PDF Extraction Artifact path.

## Continuation

After independent acceptance and exact commit publication, the next review must reconcile controlled parser orchestration into factual artifacts and bounded artifact persistence as the remaining implementation gap.

Real-asset execution and Gate 14 remain unauthorized.
