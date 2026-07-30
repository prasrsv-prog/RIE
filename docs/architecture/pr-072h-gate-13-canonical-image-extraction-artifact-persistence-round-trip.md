# PR-072H Gate 13 Canonical Image Extraction Artifact Persistence Round-Trip

## Status

Subordinate Gate 13 canonical persistence-bytes contract and implementation boundary.

This boundary closes only canonical full-artifact serialization, strict deserialization, stable serialized SHA-256 and byte length, and exact byte round-trip for the accepted versioned factual Image Extraction Artifact model.

It does not implement filesystem persistence, Official Image Source lookup or revalidation, parser orchestration, real-asset execution, or Gate 14.

## Accepted authority

- The canonical Gate 13 contract is committed on the Phase 72 branch.
- The accepted artifact-model commit is `faec3f1e604bdceb9c0e8047093bb9b792d6cf5b`.
- PR-072G selected `GATE_13_CANONICAL_IMAGE_EXTRACTION_ARTIFACT_PERSISTENCE_ROUND_TRIP_NOT_IMPLEMENTED` as the single next gap.
- The accepted artifact model remains authoritative and unchanged.
- The artifact identity payload remains distinct from full-artifact persistence serialization.

## Runtime surface

The additive runtime module is:

`rie.extraction.image_extraction_artifact_persistence`

The canonical format identifier is:

`image_extraction_artifact_canonical_json_v1`

The module exposes:

- `serialize_image_extraction_artifact`
- `deserialize_image_extraction_artifact`
- `canonical_image_extraction_artifact_payload`
- `CanonicalImageExtractionArtifactPayload`
- `ImageExtractionArtifactPersistenceError`

## Canonical serialization

Serialization:

- accepts only an exact `ImageExtractionArtifact`;
- emits one compact JSON object;
- preserves the accepted 14-field artifact order;
- encodes enum values as their controlled string values;
- uses ASCII only;
- uses no insignificant whitespace;
- contains no CR;
- ends with exactly one LF;
- has a maximum serialized length of 65,536 bytes;
- is deterministic for the same accepted artifact.

The full serialized bytes include `artifact_id`.

The serialized bytes are not the identity payload and do not redefine artifact identity.

## Serialized payload metadata

`CanonicalImageExtractionArtifactPayload` is immutable and carries:

1. `payload`
2. `serialized_sha256`
3. `serialized_byte_length`

The SHA-256 and byte length must exactly match `payload`.

## Strict deserialization

Deserialization fails closed when any of these conditions occurs:

- input is not exact bytes;
- input is empty or larger than 65,536 bytes;
- BOM is present;
- non-ASCII bytes are present;
- CR or CRLF is present;
- exactly one final LF is absent;
- JSON is malformed;
- the top-level value is not one object;
- duplicate fields exist;
- any field is missing;
- any unknown field exists;
- field order differs from the accepted order;
- enum values are invalid;
- exact integer fields use booleans or non-integer values;
- artifact-model invariants fail;
- `artifact_id` does not match canonical identity fields;
- input bytes are valid JSON but not canonical serialization.

## Exact round-trip

For every accepted successful or rejected artifact:

`deserialize_image_extraction_artifact(serialize_image_extraction_artifact(artifact)) == artifact`

and:

`serialize_image_extraction_artifact(deserialize_image_extraction_artifact(payload)) == payload`

The second equality is required before deserialization succeeds.

## Exclusions

This boundary does not:

- read or write artifact files;
- create directories;
- choose filenames or storage paths;
- perform atomic replacement;
- look up, create, update, or revalidate Official Image Source records;
- invoke the image parser;
- inspect real assets;
- open or decode image pixels;
- add dependencies;
- modify the accepted artifact model;
- modify existing PDF Extraction Artifact modules;
- create Evidence or Knowledge;
- perform OCR or semantic interpretation;
- execute a model;
- stage, commit, push, merge, tag, or publish repository history.

## Acceptance evidence

Targeted tests must prove:

- exact format identifier and size boundary;
- deterministic serialization;
- exact accepted field order;
- ASCII, compact JSON, LF-only, and one-final-LF rules;
- immutable serialized payload metadata;
- exact serialized SHA-256 and byte length;
- successful and rejected artifact round-trip;
- duplicate, missing, unknown, and reordered field rejection;
- BOM, CRLF, missing LF, extra LF, non-ASCII, empty, and oversized input rejection;
- non-object JSON rejection;
- invalid schema, identity, integer, status, and rejection-code rejection;
- non-canonical whitespace rejection;
- absence of filesystem, network, clock, random, decoder, and model dependencies;
- preservation of all accepted Gate 13 files.

## Continuation

After independent acceptance and exact commit publication, the next review must reconcile the bounded artifact file-persistence service and Official Image Source integration as separate remaining Gate 13 gaps.
