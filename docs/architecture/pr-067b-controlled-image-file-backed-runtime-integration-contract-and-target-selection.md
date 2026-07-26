# PR-067B Controlled Image File-Backed Runtime Integration Contract and Target Selection

Status: SELECTED FOR IMPLEMENTATION READINESS REVIEW

## 1. Accepted basis

This contract is based on the independently accepted PR-067A-D1 direct parser path-role and classification diagnostic.

The immutable Phase 66 implementation checkpoint is commit `dbb4d2d4fff6bc2e5d349f49f7f401a666ab0d12`.

The accepted gap classification is:

`PHASE_66_PUBLISHED_BYTES_ONLY_SINGLE_RUNTIME_CONSUMER_WITH_ZERO_PRODUCTION_CALL_SITES_AND_EXISTING_FILE_BACKED_UNKNOWN_ASSET_FLOW_REQUIRING_A_SEPARATE_SYNTHETIC_FILE_IO_INTEGRATION_CONTRACT`

The accepted diagnostic proves:

- `inspect_controlled_image_structure_bytes` is defined exactly once;
- that selected callable has zero production invocation sites and zero other runtime paths;
- `inspect_image_structure_bytes` appears only in the accepted Phase 66 delegation consumer, its callable-definition source, and its governed package re-export;
- no unexpected runtime path imports or invokes the direct parser;
- `inspect_unknown_assets` and `_inspect_unknown_item` already form an established file-backed unknown-asset flow;
- the existing flow opens a caller-provided path in binary mode and performs a bounded header read;
- `UnknownAssetHeaderInspection` currently has no image-structure field;
- the PR-067A failure was an exact raw reference-path predicate defect, not a repository, publication, parser, runtime, or scope defect.

## 2. Selected Phase 67 boundary

Selected branch:

`phase-067-controlled-image-file-backed-runtime-integration`

Selected source target:

`src/rie/ingestion/unknown_asset_header_inspector.py`

Selected future integration test:

`tests/ingestion/test_unknown_asset_header_inspector_controlled_image_file_integration.py`

Selected integration boundary:

`SYNTHETIC_TEMP_FILE_BOUNDED_READ_TO_EXISTING_BYTES_ONLY_IMAGE_STRUCTURE_CONSUMER`

The selected outcome is one minimal governed file-backed bridge from a caller-provided synthetic temporary file to the already accepted bytes-only callable `inspect_controlled_image_structure_bytes`.

## 3. Required future behavior

A later implementation boundary may:

- modify only the selected source target;
- create only the selected future integration test;
- add one narrowly named file-backed integration callable whose exact signature is fixed by PR-067C;
- accept a caller-provided filesystem path under the exact path-like contract fixed by PR-067C;
- open that path in binary mode;
- perform one explicit bounded read whose exact bound is derived from the governed image parser input limit and fixed by PR-067C;
- delegate the resulting bytes to `inspect_controlled_image_structure_bytes`;
- return the existing deterministic `ImageStructureResult` without translation, enrichment, persistence, or semantic interpretation;
- preserve existing behavior of `inspect_unknown_assets`, `_inspect_unknown_item`, and `UnknownAssetHeaderInspection` unless PR-067C proves one exact minimal compatibility change is necessary;
- use synthetic temporary files only.

## 4. Required readiness decisions

Before implementation, PR-067C must fix:

- the exact future callable name and type signature;
- the exact accepted path-like input type;
- the exact bounded-read size and its relationship to `MAX_INPUT_BYTES`;
- whether the read must request exactly the parser limit or one additional sentinel byte;
- exact behavior for missing paths, directories, permission failures, non-path input, oversized content, empty content, unsupported content, truncated content, and repeated calls;
- exact synthetic fixture bytes for PNG, JPEG, WEBP, unsupported, truncated, oversized, and empty files;
- the exact targeted test paths, test-function count, and pytest invocation;
- import-cycle safety and preservation of the accepted Phase 66 consumer contract.

PR-067B does not authorize implementation before that readiness review passes.

## 5. Prohibited expansion

Phase 67 must not:

- read or inspect a real image asset;
- redesign general filesystem ingestion or recursive discovery;
- alter the controlled image structural parser or its governed package export;
- decode images, inspect pixels, or extract EXIF or other metadata;
- add image persistence, asset cataloging, source admission, registry mutation, or network behavior;
- add CLI, operator, command, or public release-surface integration;
- add a runtime dependency;
- introduce multimodal interpretation, semantic search, embeddings, vectors, ontology, knowledge graph, inference, prompt execution, model execution, or generalized future abstraction;
- broadly refactor `unknown_asset_header_inspector.py`;
- modify the existing result dataclass merely to widen the phase.

## 6. Error and determinism contract

The future file-backed integration must preserve deterministic parser output for identical bytes.

Filesystem exceptions must not be silently converted, retried, suppressed, or generalized. PR-067C must select the exact governed exception behavior before implementation.

No automatic retry, fallback decoder, alternate parser, real-asset substitution, cleanup of accepted evidence, or hidden state mutation is authorized.

## 7. PR-067B success boundary

PR-067B succeeds only when this document is the sole committed path on a new Phase 67 branch whose parent is the immutable Phase 66 implementation commit, and local, origin, and live Phase 67 branch references resolve to the same new contract commit.

Main, the Phase 66 branch, the Phase 66 annotated tag, and the Phase 66 GitHub Release must remain unchanged.

No source implementation, test implementation, Python execution, pytest execution, parser execution, real-asset access, merge, tag, or Release is part of PR-067B.

## 8. Immediate next operation

After independent acceptance of the PR-067B operation report, continue directly to PR-067C: a read-only implementation-readiness and exact-test-plan review.
