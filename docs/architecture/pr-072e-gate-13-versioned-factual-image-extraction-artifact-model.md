# PR-072E Gate 13 Versioned Factual Image Extraction Artifact Model

## Status

Subordinate Gate 13 artifact-model contract and implementation boundary.

This document implements only the strict in-memory versioned factual Image Extraction Artifact model selected by PR-072D. It does not implement persistence, file writing, serializer/deserializer round-trip, Official Image Source lookup, parser orchestration, real-asset execution, or Gate 14.

## Accepted authority

- The canonical Gate 13 contract is committed at `08496b6920fc42158ad32e4f9d64498ec8e279b7`.
- PR-072D selected `GATE_13_VERSIONED_FACTUAL_IMAGE_EXTRACTION_ARTIFACT_MODEL_NOT_IMPLEMENTED` as the single next gap.
- The accepted JPEG, PNG, and WEBP parser and bounded file-runtime foundations remain unchanged.
- Existing Gate 5 PDF Extraction Artifact modules remain authoritative for the PDF workflow and must not be repurposed or modified by this boundary.

## Selected runtime surface

The additive runtime module is:

`rie.extraction.image_extraction_artifact`

The public model is:

`ImageExtractionArtifact`

The model is immutable and carries exactly these fields:

1. `artifact_schema_version`
2. `artifact_id`
3. `official_image_source_id`
4. `input_sha256`
5. `input_byte_length`
6. `declared_media_type`
7. `declared_extension`
8. `detected_format`
9. `pixel_width`
10. `pixel_height`
11. `parser_id`
12. `parser_version`
13. `extraction_status`
14. `rejection_code`

The only accepted schema version in this boundary is:

`image_extraction_artifact_v1`

Unknown versions fail closed.

## Deterministic identity boundary

`artifact_id` is exactly 64 lowercase hexadecimal characters.

It is the SHA-256 of a canonical ASCII identity payload containing all artifact fields except `artifact_id`, in the frozen identity-field order, encoded as compact JSON with exactly one final LF.

This identity payload is only the artifact identity contract. It is not the Gate 13 persistence serialization contract and does not close canonical persistence round-trip.

Clock time, machine identity, user identity, absolute path, process identity, random values, network state, and execution order are excluded from identity.

## Successful state

A successful artifact:

- uses status `succeeded`;
- has no rejection code;
- has one detected format from `jpeg`, `png`, or `webp`;
- has exact positive integer pixel width and height;
- has declared media type and extension consistent with the detected format.

## Rejected state

A rejected artifact:

- uses status `rejected`;
- has exactly one controlled rejection code;
- contains no detected format, pixel width, or pixel height;
- preserves source checksum, byte length, declared classification, parser identity, and parser version;
- never invents a structural fact.

## Classification boundary

The accepted media types are:

- `image/jpeg`
- `image/png`
- `image/webp`

The accepted extensions are:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`

No normalization or best-effort fallback is performed.

## Exclusions

This boundary does not:

- read or write files;
- open, decode, render, or inspect image pixels;
- call the image parser;
- look up or mutate Official Image Source records;
- serialize or persist the full artifact;
- add dependencies;
- alter existing PDF Extraction Artifact modules;
- create Evidence or Knowledge;
- perform OCR or semantic interpretation;
- execute a model;
- use real assets;
- stage, commit, push, merge, tag, or publish repository history.

## Acceptance evidence

Targeted tests must prove:

- frozen field order and immutable values;
- exact schema-version rejection;
- deterministic artifact identity;
- supported JPEG, PNG, and WEBP classifications;
- declared classification consistency;
- strict SHA-256, byte-length, identifier, status, and dimension validation;
- successful and rejected state invariants;
- no filesystem, network, clock, random, decoder, or model dependency;
- preservation of all accepted foundation files.

## Continuation

After independent acceptance, the next review must reconcile the remaining Gate 13 gaps. Canonical persistence round-trip and Official Image Source integration remain open and must be handled as separate bounded operations.
