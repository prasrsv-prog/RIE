# PR-072Q Gate 13 Controlled Image Extraction Parser Orchestration

## Status

Subordinate Gate 13 synthetic-only orchestration contract and implementation boundary.

This boundary closes only one fail-closed bytes-in workflow that invokes accepted Official Image Source validation, accepted structural parsing, deterministic Image Extraction Artifact construction, and accepted bounded artifact-file persistence.

It does not introduce a file-backed image-source loader, registry scan, CLI, real-asset execution, pixel decoding, semantic interpretation, Gate 14, or repository publication.

## Accepted authority

- The canonical Gate 13 contract is accepted.
- The versioned factual Image Extraction Artifact model is accepted.
- Canonical artifact serialization and exact byte round-trip are accepted.
- The bounded artifact file-persistence service is accepted.
- Official Image Source extraction integration is accepted.
- The structural image parser foundation is accepted.
- PR-072P Correction 2 selected `GATE_13_CONTROLLED_IMAGE_EXTRACTION_PARSER_ORCHESTRATION_NOT_IMPLEMENTED` as the single next gap.

## Runtime surface

The additive runtime module is:

`rie.extraction.controlled_image_extraction_orchestrator`

The public entry point is:

`run_controlled_image_extraction`

The module exposes:

- `CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_VERSION`
- `CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_RESULT_FIELD_ORDER`
- `ControlledImageExtractionOrchestrationStatus`
- `ControlledImageExtractionOrchestrationResult`
- `run_controlled_image_extraction`

## Request boundary

The caller supplies:

1. exactly one canonical Official Image Source payload or `None`;
2. presented source identifier;
3. presented source locator;
4. exact non-empty synthetic image bytes;
5. one coherent supported declared media type;
6. one coherent supported declared extension;
7. one explicit existing artifact-root `pathlib.Path`.

The supported declaration pairs are exactly:

- `image/jpeg` with `.jpg` or `.jpeg`;
- `image/png` with `.png`;
- `image/webp` with `.webp`.

A malformed request type or incoherent declaration pair is programmer contract misuse and raises a deterministic type or value error before orchestration.

## Fixed stage order

The orchestration stage order is exact:

1. validate the request declaration boundary;
2. resolve and revalidate one Official Image Source;
3. when source validation is accepted, invoke the accepted structural parser once;
4. construct exactly one successful or rejected Image Extraction Artifact;
5. invoke the accepted artifact file-persistence service once;
6. return one immutable orchestration result.

The structural parser must not execute when Official Image Source validation is rejected.

## Source-validation rejection

A controlled source-validation rejection:

- does not invoke the structural parser;
- constructs one rejected Image Extraction Artifact using the source-validation rejection code;
- uses the accepted parser identity and version as governed parser contract context;
- persists the rejected artifact through the accepted file-persistence service;
- returns orchestration status `rejected` when persistence succeeds;
- returns orchestration status `persistence_failed` when persistence rejects the artifact.

## Parser-result revalidation

After accepted source validation, the orchestrator revalidates the parser result:

- exact result type;
- accepted parser identity;
- accepted parser version;
- exact input SHA-256;
- exact input byte length;
- supported status;
- accepted-result dimensions and format;
- rejected-result absence of structural dimensions.

A parser identity mismatch maps to `parser_identity_mismatch`.

A parser fingerprint, byte-length, status, or structural-contract mismatch maps to `deterministic_output_unproven`.

## Parser rejection mapping

The exact controlled mapping is:

- `OVERSIZED_INPUT` to `resource_limit_exceeded`;
- `UNSUPPORTED_SIGNATURE` or `UNSUPPORTED_WEBP_CHUNK` to `unsupported_format`;
- `ZERO_DIMENSION` to `invalid_dimensions`;
- accepted malformed, truncated, or missing-structure reasons to `malformed_structure`;
- any unknown rejection reason to `deterministic_output_unproven`.

No parser rejection carries width or height into a rejected artifact.

## Successful parsing

A successful parser result must:

- report `JPEG`, `PNG`, or `WEBP`;
- match the declared classification;
- contain positive exact integer width and height;
- contain the accepted parser identity and version;
- match the exact input fingerprint and byte length.

The orchestrator then constructs one successful versioned artifact.

A detected-format conflict constructs one rejected artifact with `declared_format_conflict`.

## Persistence outcome

The accepted file-persistence result remains authoritative.

When persistence returns `written` or `already_present`:

- a successful artifact produces orchestration status `succeeded`;
- a rejected artifact produces orchestration status `rejected`.

When persistence returns `rejected`, orchestration status is `persistence_failed`.

The orchestrator does not retry, replace, delete, or independently read the artifact file.

## Immutable result

The orchestration result has exactly seven ordered fields:

1. `orchestration_version`
2. `status`
3. `source_validation`
4. `parser_executed`
5. `parser_result`
6. `artifact`
7. `persistence_result`

The result is immutable.

The artifact and persistence result are always present.

The parser result is present exactly when `parser_executed` is true.

## Exclusions

This boundary does not:

- discover or scan Official Image Source records;
- read an image source file;
- resolve a source locator through network or filesystem access;
- create the artifact root;
- invoke a CLI;
- process a real asset;
- decode pixels;
- read EXIF or other image metadata;
- perform OCR;
- perform semantic or multimodal interpretation;
- execute a model;
- create Evidence or Knowledge;
- enter Gate 14;
- change existing accepted Gate 13 or PDF Extraction Artifact modules;
- stage, commit, push, merge, tag, or publish repository history.

## Acceptance evidence

Synthetic-only targeted tests must prove:

- exact version and seven-field result order;
- immutable result;
- successful PNG, JPEG, and WEBP workflows;
- exact artifact structural facts;
- exact artifact-file persistence and load-back;
- idempotent repeated orchestration;
- source rejection prevents parser invocation;
- source rejection artifact construction and persistence;
- parser malformed, unsupported, zero-dimension, and oversized mapping;
- detected-format conflict mapping;
- parser identity mismatch handling;
- parser fingerprint and byte-length mismatch handling;
- unknown parser status and rejection-reason handling;
- persistence failure propagation;
- no retry or second parser invocation;
- deterministic repeated results;
- absence of registry scan, CLI, network, pixel decoder, OCR, semantic, model, and real-asset dependencies;
- preservation of all accepted Gate 13, Official Image Source, parser, ingestion-consumer, and PDF Extraction Artifact paths.

## Continuation

After independent acceptance and exact commit publication, the next review must reconcile the remaining Gate 13 closure criteria without authorizing real assets or Gate 14.
