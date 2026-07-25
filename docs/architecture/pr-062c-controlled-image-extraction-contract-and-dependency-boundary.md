# PR-062C Controlled Image Extraction Contract and Dependency Boundary

## Status

Contract and dependency boundary only.

This document defines the smallest deterministic boundary required before any controlled image extraction implementation is proposed.

## Accepted baseline

- Phase 61 is officially closed at commit `abaa3b89f00373160898ba3b070b82eebc359aa0`.
- The official image source domain contract governs candidate identity, source reference, declared media type, extension, SHA-256, byte length, provenance, acceptance state, and rejection reason.
- The repository recognizes JPEG, PNG, and WEBP classifications.
- The repository contains negative image-metadata gates.
- The repository has no accepted image decoder dependency, decode API, controlled image extraction contract, runtime tests, operator command, acceptance evidence, or real-asset image fixture.

## Domain purpose

Controlled image extraction will produce deterministic structural facts from an accepted official image source candidate without semantic interpretation.

In this boundary, extraction means governed structural inspection only. It does not mean visual understanding.

## Minimum future input contract

A future controlled image extraction request must contain exactly one accepted official image source candidate with:

- stable source identifier;
- controlled source reference;
- declared media type;
- declared extension;
- exact SHA-256 fingerprint;
- exact byte length;
- explicit provenance;
- accepted source state.

The request must be rejected before extraction when any required field is missing, ambiguous, malformed, or inconsistent.

## Minimum future output contract

A future controlled image extraction artifact may contain only deterministic structural facts:

- deterministic artifact identifier;
- source identifier;
- input SHA-256 fingerprint;
- input byte length;
- detected supported format;
- pixel width;
- pixel height;
- parser or decoder identity;
- parser or decoder version;
- extraction status;
- explicit rejection reason when unsuccessful;
- exact output SHA-256 fingerprint;
- exact output byte length.

No output field may be inferred from visual meaning, filenames, surrounding folders, model output, or unstated assumptions.

## Initially bounded classifications

A later implementation proposal may address only:

- JPEG;
- PNG;
- WEBP.

Classification recognition does not by itself authorize opening, decoding, rendering, or interpreting an image.

## Dependency boundary

The current exact runtime dependency remains `pypdf==6.14.2`.

This document does not authorize adding Pillow, OpenCV, ImageIO, EXIF libraries, OCR libraries, or any other image-processing dependency.

Before any dependency addition, a separate review must prove:

- why the required structural facts cannot be obtained safely within the existing dependency boundary;
- the smallest single dependency that can satisfy the contract;
- an exact locked version;
- exact package and offline wheel fingerprints;
- deterministic behavior for JPEG, PNG, and WEBP;
- bounded memory, dimensions, and file-size handling;
- safe rejection of malformed, truncated, unsupported, or oversized inputs;
- compatibility with fresh external build and installation acceptance;
- absence of model execution, semantic interpretation, network calls, and hidden runtime downloads;
- preservation of the accepted PDF workflow.

Dependency selection and installation remain separate future boundaries.

## Required rejection behavior

A future implementation must reject or safe-stop when:

- the official image source candidate is not accepted;
- source identity or provenance is missing or ambiguous;
- the input fingerprint or byte length does not match;
- declared media type, extension, and detected format conflict;
- the format is unsupported;
- the file is malformed, truncated, or exceeds an accepted resource limit;
- width or height is missing, invalid, zero, or outside an accepted bound;
- parser or decoder identity does not match the accepted dependency contract;
- deterministic output cannot be proven;
- the requested operation requires metadata extraction, pixel interpretation, semantic analysis, or model execution.

## Explicit non-authority

This contract boundary does not authorize:

- adding or changing runtime dependencies;
- implementing image parsing or decoding;
- opening, decoding, rendering, resizing, or transforming an image;
- reading pixel values;
- extracting EXIF or other image metadata;
- generating thumbnails or previews;
- OCR or text recognition;
- object, product, person, logo, scene, color, or visual-attribute recognition;
- embeddings, vectors, semantic indexes, ontologies, knowledge graphs, or automated inference;
- local or remote model execution;
- real-asset inspection or execution;
- multimodal interpretation;
- operator CLI changes;
- registry changes;
- changes to the accepted PDF workflow.

## Synthetic-only implementation prerequisite

Any later implementation boundary must begin with generated synthetic JPEG, PNG, and WEBP fixtures whose exact bytes and expected structural facts are controlled.

Real assets remain unauthorized until a separate post-synthetic acceptance boundary is independently approved.

## Repository boundary

This document is the only repository materialization authorized by PR-062C.

PR-062C does not authorize implementation code, tests, dependency files, CLI changes, registry changes, image files, build execution, installation, package-network access, or real-asset execution.

## Follow-on boundary

After independent acceptance and commit publication of this document, the next proposal must be a separate implementation-readiness review that resolves the smallest parser or decoder dependency and synthetic execution contract.

## Closure condition

This boundary is complete only when this document is committed as the sole changed repository path and all Phase 61 publication evidence remains preserved.
