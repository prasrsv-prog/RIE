# PR-066B Controlled Image Structural Parser Single Consumer Contract and Target Selection

Status: SELECTED FOR A LATER IMPLEMENTATION BOUNDARY

## 1. Accepted basis

This contract is based only on the independently accepted PR-066A-D5 final corrected inventory.

The immutable Phase 65 checkpoint is commit `33d38dcb35ece90468f289758a483294541e04df`.

The accepted gap is:

`CONTROLLED_IMAGE_STRUCTURAL_PARSER_GOVERNED_PACKAGE_REACHABILITY_PUBLISHED_WITH_ZERO_NON_TEST_RUNTIME_CONSUMERS_AND_NO_SELECTED_CONSUMER_CONTRACT`

The accepted inventory proves:

- `rie.extraction` exports exactly five controlled image structural parser symbols in one block.
- all 155 non-definition runtime Python paths were inspected, including six zero-byte package files;
- all 29 `rie.extraction` occurrences are unrelated dotted extraction-submodule namespace traffic;
- accepted-symbol package imports, direct image-parser module imports or references, parser-specific symbols, and parser calls are all zero;
- candidate surfaces contain three `official_source` paths, 36 `ingestion` paths, eight operator or CLI paths, and zero other image-named runtime paths;
- no tracked `docs/architecture/pr-066*.md` consumer contract existed at the accepted checkpoint.

## 2. Candidate surface decision

### 2.1 `official_source`

Not selected.

The recorded paths are one empty package file and two inspection-oriented paths. Selecting this surface would risk mixing the parser consumer boundary with official-source registry or inspection behavior before a dedicated contract proves that coupling is necessary.

### 2.2 operator or CLI

Excluded.

Phase 66 must not expose the parser through an operator command, CLI command, public command surface, or release-facing interface.

### 2.3 other image-named runtime surface

Unavailable.

The accepted inventory contains zero runtime paths in this category.

### 2.4 `ingestion`

Selected domain.

The ingestion inventory contains an existing internal header-inspection path whose path-level responsibility is the closest recorded fit for a bytes-only structural consumer without selecting a PDF-specific, filesystem-specific, real-asset, registry, or CLI surface.

## 3. Selected single consumer target

Selected source target:

`src/rie/ingestion/unknown_asset_header_inspector.py`

Selected future test target:

`tests/ingestion/test_unknown_asset_header_inspector_image_structure_consumer.py`

Selected future callable:

`inspect_controlled_image_structure_bytes(data: bytes) -> ImageStructureResult`

The callable must import `ImageStructureResult` and `inspect_image_structure_bytes` only from the governed package surface `rie.extraction` and must return the delegated result without translation, enrichment, mutation, persistence, or side effects.

The selected target is conditional on a later implementation-readiness review proving the exact baseline fingerprint, import safety, absence of conflicting behavior, and compatibility with this contract. This contract does not authorize implementation by itself.

## 4. Required future implementation behavior

A later implementation boundary may:

- modify only the selected source target;
- create only the selected future test target;
- add exactly one bytes-only delegation callable;
- import only the two selected governed package symbols;
- prove object and value equivalence with direct `rie.extraction.inspect_image_structure_bytes` behavior;
- use synthetic PNG, JPEG, WEBP, unsupported, truncated, oversized, repeated, and non-bytes inputs;
- preserve deterministic parser results and existing exception behavior.

The future implementation must not:

- read a path, directory, stream, file handle, or filesystem object;
- inspect or materialize a real asset;
- decode image pixels or extract EXIF or other metadata;
- alter the parser implementation or the Phase 65 package export block;
- add a CLI, operator command, registry mutation, source-admission side effect, persistence action, or network action;
- introduce multimodal interpretation, semantic expansion, inference, prompt execution, or model execution;
- add or change a runtime dependency.

## 5. Required readiness evidence

Before implementation, a separate read-only review must prove:

- the selected source target exists and its exact SHA-256, byte, LF, CR, BOM, ASCII, and final-LF properties;
- the selected future test target does not already exist;
- the selected source target has no current controlled image parser import, symbol, or call;
- adding the two governed package imports does not create an import cycle;
- existing tests associated with the selected source target are identified;
- the exact synthetic targeted-test count and invocation are fixed;
- repository, Phase 65 tag, Release, artifacts, and runtime dependency remain exact.

## 6. Success boundary

PR-066B succeeds only when this document is the sole committed path on a new Phase 66 branch whose parent is the immutable Phase 65 implementation commit, and local, origin, and live branch references resolve to the same new commit.

No source implementation, test implementation, parser execution, real-asset access, tag, Release, merge, or main-branch mutation is part of PR-066B.

## 7. Selected future boundary

`SYNTHETIC_BYTES_ONLY_UNKNOWN_ASSET_HEADER_INSPECTOR_IMAGE_STRUCTURE_DELEGATION`
