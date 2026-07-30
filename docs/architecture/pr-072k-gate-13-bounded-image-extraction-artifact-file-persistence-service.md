# PR-072K Gate 13 Bounded Image Extraction Artifact File Persistence Service

## Status

Subordinate Gate 13 bounded filesystem-persistence service contract and implementation boundary.

This boundary closes only deterministic artifact filename derivation, controlled-root validation, atomic artifact publication, exact existing-file verification, strict read-back, and controlled filesystem failure results for accepted canonical Image Extraction Artifact bytes.

It does not implement Official Image Source lookup or revalidation, parser orchestration, real-asset execution, Gate 14, semantic interpretation, or repository publication.

## Accepted authority

- The canonical Gate 13 contract is accepted.
- The versioned factual Image Extraction Artifact model is accepted.
- Canonical full-artifact serialization, strict deserialization, serialized SHA-256 and byte length, and exact byte round-trip are accepted.
- PR-072J selected `GATE_13_IMAGE_EXTRACTION_ARTIFACT_FILE_PERSISTENCE_SERVICE_NOT_IMPLEMENTED` as the single next gap.
- Existing accepted artifact-model and canonical-persistence modules remain unchanged.

## Runtime surface

The additive runtime module is:

`rie.extraction.image_extraction_artifact_file_persistence`

The module exposes:

- `image_extraction_artifact_filename`
- `persist_image_extraction_artifact_file`
- `load_image_extraction_artifact_file`
- `ImageExtractionArtifactFileWriteResult`
- `ImageExtractionArtifactFileReadResult`
- controlled status and failure-code enums

## Deterministic filename

The artifact filename is exactly:

`<artifact_id>.image-extraction-artifact.json`

`artifact_id` must contain exactly 64 lowercase hexadecimal characters.

No clock, machine name, process identifier, random value, path input, execution order, or external state contributes to the filename.

The service also uses one deterministic temporary filename:

`<artifact filename>.tmp`

The temporary filename is internal and must not survive a successful write.

## Controlled root

The caller supplies one explicit `pathlib.Path` root.

The root must:

- be absolute;
- already exist;
- be a directory;
- not itself be a symbolic link.

The service does not create the root or nested directories.

The controlled filename is derived only from the accepted artifact identifier, so caller-controlled path segments cannot escape the root.

## Atomic publication

For a new artifact:

1. canonical bytes are created by the accepted canonical-persistence module;
2. a temporary file is created exclusively in the controlled root;
3. all bytes are written, flushed, and synchronized;
4. the temporary file is strictly deserialized and compared with the accepted artifact;
5. the temporary file is atomically published by a same-directory hard-link operation;
6. the temporary name is removed;
7. the published file is strictly read back and compared byte-for-byte and artifact-for-artifact.

The target is never intentionally overwritten.

A pre-existing temporary path fails closed.

## Existing target

When the deterministic target already exists:

- a directory or symbolic link is rejected;
- invalid canonical bytes are rejected;
- a valid but different artifact is rejected;
- an exact canonical byte and artifact match returns `already_present`;
- no existing target is overwritten.

## Strict read

Reading:

- derives the deterministic filename from one controlled artifact identifier;
- reads at most the accepted canonical serialized-byte boundary plus one byte;
- strictly deserializes the bytes;
- verifies the deserialized artifact identifier matches the requested identifier;
- returns exact serialized SHA-256 and byte length;
- returns controlled rejection for absence, invalid bytes, oversize content, non-regular targets, read failure, or identifier mismatch.

## Controlled results

Expected filesystem and content failures return immutable controlled result objects.

Programmer contract misuse, such as a non-`Path` root, non-artifact value, or malformed artifact identifier, raises a deterministic type or value error.

Successful results contain no failure code.

Rejected results contain exactly one failure code and no invented artifact.

## Exclusions

This boundary does not:

- create artifact storage directories;
- select a business storage location;
- scan a directory;
- delete or replace a pre-existing target;
- look up, create, update, or revalidate Official Image Source records;
- invoke the image parser;
- inspect image source bytes;
- open or decode pixels;
- use real assets;
- add dependencies;
- modify accepted artifact or canonical-persistence modules;
- modify existing PDF Extraction Artifact modules;
- create Evidence or Knowledge;
- perform OCR or semantic interpretation;
- execute a model;
- use network access;
- stage, commit, push, merge, tag, or publish repository history.

## Acceptance evidence

Synthetic-only targeted tests must prove:

- exact deterministic target and temporary filenames;
- invalid identifier rejection;
- exact canonical bytes written;
- exact serialized SHA-256 and byte length;
- immutable write and read results;
- successful and rejected artifact write/read round-trip;
- idempotent exact existing-file handling;
- no overwrite of valid mismatched or invalid existing targets;
- relative, missing, non-directory, and non-regular root or target rejection;
- occupied temporary-path rejection;
- successful temporary-path cleanup;
- controlled missing, invalid, oversized, and identifier-mismatch read results;
- no nested-directory creation;
- absence of network, clock, random, decoder, model, and random temporary-file dependencies;
- preservation of all accepted Gate 13 and PDF Extraction Artifact files.

## Continuation

After independent acceptance and exact commit publication, the next review must reconcile Official Image Source integration and parser orchestration as separate remaining Gate 13 gaps.
