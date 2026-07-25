# PR-061D Official Image Source Domain Contract

## Status

Contract boundary only.

This document records the smallest remaining RCIS Core boundary after the accepted RIE Core v1 operator workflow and the Phase 61 read-only image capability reviews.

## Accepted baseline

- Phase 60 is officially closed at commit `b7e64ac0e98e1a72bf8fadfa8fbc2e4497b72726`.
- The repository can classify selected image file extensions and creative asset types.
- Existing image-related geometry checks are not image decoding.
- Existing `allowed_for_image_metadata` references are negative gates, not an image artifact runtime contract.
- No accepted image runtime capability currently exists.

## Domain purpose

The official image source domain will govern whether an image file may be recognized as an official source candidate before any image decoding, inspection, extraction, or interpretation occurs.

## Minimum contract

An official image source candidate must have:

- one stable source identifier;
- one controlled source path or controlled source reference;
- one declared media type;
- one declared file extension;
- one exact SHA-256 fingerprint;
- one exact byte length;
- one explicit provenance reference;
- one explicit acceptance state;
- one explicit reason when rejected.

Candidate recognition must remain deterministic and must not infer content from pixels, metadata, filenames, surrounding folders, or model output.

## Initially recognized classifications

The contract may recognize the existing classified types:

- JPEG;
- PNG;
- WEBP.

Recognition of a classification does not authorize decoding, rendering, metadata extraction, OCR, computer vision, semantic interpretation, or runtime ingestion.

## Required rejection behavior

The contract must reject or safe-stop when:

- the source identifier is missing or ambiguous;
- the controlled source reference is missing or ambiguous;
- the declared media type and extension conflict;
- the SHA-256 fingerprint is missing or malformed;
- the byte length is missing, invalid, or inconsistent;
- provenance is missing;
- acceptance state is missing or unsupported;
- more than one candidate is presented where exactly one is required;
- any operation would require image decoding or image interpretation.

## Explicit non-authority

This contract does not authorize:

- adding Pillow, OpenCV, ImageIO, EXIF, OCR, or other image decoder dependencies;
- opening or decoding JPEG, PNG, WEBP, or any other image;
- reading pixel data;
- extracting image metadata or EXIF;
- generating thumbnails or previews;
- rendering images;
- recognizing objects, products, people, text, scenes, colors, logos, or visual attributes;
- creating embeddings, vectors, semantic indexes, ontologies, or knowledge graphs;
- invoking local or remote models;
- inspecting a real asset;
- changing the accepted PDF operator workflow;
- changing existing negative image-metadata gates.

## Repository boundary

This document is the only repository materialization authorized by PR-061D.

PR-061D does not authorize implementation code, tests, dependency changes, CLI changes, registry changes, real-asset fixtures, image files, build execution, installation, or package-network access.

## Follow-on boundary

After independent acceptance and commit publication of this document, any implementation proposal must begin with a separate review that defines the smallest deterministic official-image-source candidate contract without image decoding or semantic capability expansion.

## Closure condition

This contract boundary is complete only when this document is committed without any additional repository path and all prior Phase 60 and Phase 61 evidence remains preserved.
