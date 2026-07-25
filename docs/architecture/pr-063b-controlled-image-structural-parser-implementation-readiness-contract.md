# PR-063B Controlled Image Structural Parser Implementation Readiness Contract

Status: proposed Phase 63 implementation-readiness contract
Phase baseline: Phase 62 controlled image extraction boundary
Parent commit: 2e2e59335c18dcbfce00e99e850f207c726953db

## 1. Purpose

This contract records the smallest accepted implementation-readiness boundary for a future controlled image structural parser.

The boundary is limited to deterministic format and dimension inspection for accepted JPEG, PNG, and WEBP source candidates. It does not implement the parser, authorize runtime execution, or declare a completed image extraction capability.

## 2. Proven repository baseline

The accepted repository baseline proves:

- existing PNG, JPEG, and WEBP tests are synthetic magic-byte format-classification tests only;
- each existing classification test writes synthetic bytes to a temporary `.dat` path;
- those tests do not assert image dimensions;
- no image-specific structural extraction test exists;
- no image-specific structural parser implementation exists;
- no image structural artifact implementation or test exists;
- no image decoder API is used;
- no image decoder dependency is installed;
- no tracked JPEG, JPG, PNG, or WEBP fixture exists;
- the exact runtime dependency remains `pypdf==6.14.2`.

The existing format-classification tests are prior capability evidence and must not be reclassified as structural extraction.

## 3. Minimum future parser boundary

A later implementation boundary may use only the Python standard library to inspect bounded binary headers.

The minimum supported formats are:

- JPEG;
- PNG;
- WEBP.

The future parser may return only deterministic structural fields required by the accepted Phase 62 contract, including:

- detected format;
- width;
- height;
- parser identity;
- parser version;
- inspection status;
- bounded rejection reason;
- source fingerprint and byte length;
- output fingerprint and output byte length.

## 4. Format-specific readiness boundary

### JPEG

A later parser may validate the JPEG SOI signature and perform a bounded marker scan to locate an accepted SOF marker carrying width and height.

The scan must reject malformed, truncated, unsupported, oversized, or ambiguous marker layouts without decoding pixels.

### PNG

A later parser may validate the PNG signature and read width and height only from a structurally valid IHDR boundary.

It must reject malformed, truncated, unsupported, oversized, or ambiguous input without reading image pixels.

### WEBP

A later parser may validate the RIFF and WEBP signatures and inspect only bounded VP8, VP8L, or VP8X structural headers for width and height.

It must reject malformed, truncated, unsupported, oversized, or ambiguous input without decoding image content.

## 5. Dependency decision

No new runtime dependency is required for this readiness boundary.

The accepted dependency decision is:

`NO_NEW_RUNTIME_DEPENDENCY_REQUIRED`

Pillow, PIL, OpenCV, cv2, imageio, Wand, ExifRead, piexif, rawpy, and equivalent decoder or metadata libraries remain outside this boundary.

Any later proposal to add or change a runtime dependency requires a separate boundary review and explicit acceptance.

## 6. Test-first execution boundary

A later implementation must begin with synthetic fixtures created in tests.

Synthetic tests must cover at minimum:

- one accepted JPEG structural header;
- one accepted PNG structural header;
- accepted WEBP VP8, VP8L, and VP8X structural headers where supported by the implementation boundary;
- truncated input;
- malformed signatures;
- invalid or zero dimensions;
- unsupported structural variants;
- bounded input-size rejection;
- deterministic repeated output.

No real asset may be introduced, inspected, decoded, or executed until a later explicit real-asset boundary is independently accepted.

## 7. Explicit exclusions

This contract does not authorize:

- parser implementation;
- changes to source code or tests;
- changes to CLI, operator commands, registry, or accepted PDF workflows;
- new or changed runtime dependencies;
- image decoding;
- pixel reads;
- EXIF or other metadata extraction;
- thumbnails, resizing, rendering, or transformation;
- OCR;
- real-asset execution;
- multimodal interpretation;
- semantic indexing, embeddings, vectors, ontologies, knowledge graphs, or automated inference;
- local or remote model execution;
- declaration of full RCIS Core completion.

## 8. Next controlled boundary

After this readiness contract is independently accepted, the next separately reviewed boundary may authorize a test-first synthetic implementation of the bounded standard-library structural header parser.

That later boundary must define exact source paths, test paths, result contracts, rejection behavior, and acceptance commands before any implementation mutation occurs.

## 9. Acceptance statement

The implementation-readiness classification is:

`CONTROLLED_IMAGE_STRUCTURAL_HEADER_PARSER_IMPLEMENTATION_READINESS_NO_NEW_RUNTIME_DEPENDENCY_SYNTHETIC_ONLY`

The accepted readiness statement is:

`CONTROLLED_IMAGE_STRUCTURAL_PARSER_IMPLEMENTATION_READINESS_CONTRACT_ACCEPTED`
