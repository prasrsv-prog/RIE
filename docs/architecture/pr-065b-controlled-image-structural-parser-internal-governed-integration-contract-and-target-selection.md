# PR-065B Controlled Image Structural Parser Internal Governed Integration Contract and Target Selection

## Status

`CONTROLLED_IMAGE_STRUCTURAL_PARSER_INTERNAL_GOVERNED_INTEGRATION_CONTRACT_ACCEPTED`

## Purpose

This contract selects the smallest existing internal runtime surface through which the Phase 64 controlled image structural parser may become governedly reachable without expanding into operator, CLI, registry, file-I/O, real-asset, decoder, metadata, multimodal, semantic, or model-execution scope.

## Accepted baseline

The accepted Phase 64 implementation is:

- source: `src/rie/extraction/image_structure_parser.py`;
- tests: `tests/extraction/test_image_structure_parser.py`;
- function: `inspect_image_structure_bytes`;
- result type: `ImageStructureResult`;
- parser ID: `rie.image-structure.stdlib`;
- parser version: `1`;
- input boundary: immutable `bytes`;
- maximum input size: `1_048_576` bytes;
- supported structural formats: JPEG, PNG, and WEBP;
- accepted output fields: status, image format, width, height, parser identity, parser version, input SHA-256, input byte length, and rejection reason;
- runtime dependency baseline: exactly `pypdf==6.14.2`;
- verified targeted synthetic tests: `21`.

## Selected governed integration target

The first accepted governed integration target is:

`src/rie/extraction/__init__.py`

This existing package boundary is selected because it is:

- internal to the extraction domain;
- already tracked and stable;
- independent from operator and CLI surfaces;
- independent from registry publication;
- independent from official-source admission;
- independent from ingestion file discovery;
- compatible with bytes-only synthetic invocation;
- sufficient to make the accepted parser contract reachable through one governed package surface without introducing a new service abstraction.

## Authorized future implementation shape

A later separately reviewed implementation boundary may modify only:

1. `src/rie/extraction/__init__.py`;
2. a dedicated synthetic test path selected by that implementation review.

The package surface may export only these existing Phase 64 symbols:

- `ImageStructureResult`;
- `MAX_INPUT_BYTES`;
- `PARSER_ID`;
- `PARSER_VERSION`;
- `inspect_image_structure_bytes`.

The implementation must not duplicate parser logic, create a second parser, add a service layer, change the parser result schema, or alter Phase 64 rejection behavior.

## Synthetic governed invocation contract

The later implementation review must prove that:

- the parser is imported through `rie.extraction`;
- invocation accepts `bytes` only;
- accepted and rejected results are deterministic;
- package-export invocation produces the same result as direct module invocation;
- no filesystem path, stream, file handle, or real image asset is used;
- no cache or Python bytecode artifact is created by the controlled test execution;
- repository state remains limited to the accepted implementation paths.

## Dependency decision

`NO_NEW_RUNTIME_DEPENDENCY_REQUIRED`

No dependency addition, replacement, or upgrade is authorized.

## Explicit exclusions

This contract does not authorize:

- file-I/O parser execution;
- path-based or stream-based parser input;
- real image fixtures or real-asset inspection;
- image decoding or pixel reads;
- EXIF or metadata extraction;
- official-source integration;
- ingestion orchestration integration;
- operator or CLI exposure;
- registry publication;
- artifact serialization or persistence;
- network execution;
- multimodal interpretation;
- semantic extraction or inference;
- model or prompt execution;
- generalized adapters, plugin systems, or future-facing abstractions.

## Phase 65 boundary

The accepted implementation sequence is:

1. publish this contract and target selection;
2. independently review the committed contract;
3. implement the exact extraction-package export with synthetic equivalence tests;
4. review the implementation and targeted tests;
5. publish and close Phase 65 only after all exact checks pass.

## Exact gap classification

`CONTROLLED_IMAGE_STRUCTURAL_PARSER_INTERNAL_PACKAGE_EXPORT_GOVERNED_REACHABILITY_GAP`

## Final decision

The smallest safe remaining RCIS Core integration step is an internal extraction-package export of the existing bytes-only structural parser, verified through synthetic equivalence tests. CLI, registry, file-I/O, real assets, image decoding, metadata extraction, multimodal interpretation, semantic expansion, and model execution remain outside the authorized boundary.
