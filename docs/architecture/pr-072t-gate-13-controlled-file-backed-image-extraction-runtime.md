# PR-072T Gate 13 Controlled File-Backed Image Extraction Runtime

## Status

Subordinate Gate 13 runtime boundary for one controlled synthetic image file.

This boundary connects an explicit controlled source root and normalized relative file path to the accepted bytes-in controlled image extraction orchestration. It closes only bounded file reading, source-path containment, file-read failure control, exact input fingerprint publication, and one orchestration invocation.

It does not implement registry scanning, recursive discovery, batch execution, a command-line interface, real-asset execution, pixel decoding, semantic interpretation, or Gate 14.

## Accepted authority

The following accepted Gate 13 boundaries remain unchanged:

- canonical contract and Definition of Done;
- versioned factual Image Extraction Artifact model;
- canonical artifact persistence round trip;
- bounded artifact file-persistence service;
- Official Image Source extraction integration;
- deterministic image structure parser;
- bytes-in controlled image extraction orchestration.

PR-072S selected `GATE_13_CONTROLLED_FILE_BACKED_IMAGE_EXTRACTION_RUNTIME_NOT_IMPLEMENTED` as the single next gap.

## Runtime surface

The additive runtime module is:

`rie.extraction.controlled_image_file_extraction_runtime`

The public API is:

`run_controlled_image_file_extraction`

The immutable result has exactly eight fields:

1. `runtime_version`
2. `status`
3. `source_relative_path`
4. `source_file_opened`
5. `input_sha256`
6. `input_byte_length`
7. `failure_code`
8. `orchestration_result`

The version is exactly:

`controlled_image_file_extraction_runtime_v1`

## Controlled source path

The caller supplies:

- one absolute existing `pathlib.Path` source root;
- one normalized non-empty POSIX relative path;
- one explicit artifact root;
- one canonical Official Image Source payload or `None`;
- the governed source identifier and source locator;
- one coherent JPEG, PNG, or WEBP declaration pair.

The relative path:

- must not be absolute;
- must not contain `.` or `..` segments;
- must not contain backslashes, control characters, or surrounding whitespace;
- may contain nested forward-slash-separated segments;
- must resolve to a regular file inside the resolved source root.

The source root and every source-path component must not be a symbolic link. Resolution must remain beneath the controlled root.

## Bounded file read

The runtime opens exactly one source file once and performs one bounded read of:

`MAX_INPUT_BYTES + 1`

The extra byte is a deterministic oversize sentinel.

An empty file or a read longer than `MAX_INPUT_BYTES` is rejected before orchestration. No partial bytes are presented as an accepted input fingerprint.

For a non-empty in-boundary file, the runtime computes exact SHA-256 and byte length from the bytes read and invokes the accepted bytes-in orchestration exactly once.

## Governed proof

The downstream accepted orchestration:

1. resolves and revalidates exactly one canonical Official Image Source payload;
2. proves source identity, locator, admission, authority, rights, lifecycle, SHA-256, byte length, declaration, and provenance;
3. executes the structural parser only after accepted source validation;
4. constructs a successful or rejected Image Extraction Artifact;
5. persists the artifact through the accepted bounded service.

The file runtime result verifies that the persisted artifact input SHA-256 and byte length equal the bytes read from the controlled file.

## Controlled file failures

Expected file-boundary failures return `file_rejected` with exactly one controlled failure code and no orchestration result:

- source root is relative;
- source root is missing;
- source root is not a directory;
- source root is a symbolic link;
- source path escapes the root;
- a source-path component is a symbolic link;
- source file is missing;
- source target is not a regular file;
- source file is empty;
- source file exceeds the accepted byte boundary;
- source file cannot be read.

Programmer contract misuse, including non-`Path` roots, malformed relative paths, or incoherent media declarations, raises a deterministic type or value error before file opening.

## Result status

`orchestrated` means one in-boundary non-empty file was read and the accepted bytes-in orchestration returned a controlled result. The nested orchestration may be successful, rejected, or persistence-failed.

`file_rejected` means the runtime stopped before orchestration because the controlled file boundary was not satisfied.

## Exclusions

This boundary does not:

- scan a source root;
- discover files recursively;
- accept an absolute source-file argument;
- follow a symbolic link;
- create a source directory;
- modify a source file;
- decode image pixels;
- extract EXIF or other semantic metadata;
- perform OCR;
- classify or interpret image content;
- create Evidence or Knowledge;
- execute a model;
- use network access;
- implement a CLI;
- execute a real asset;
- enter Gate 14;
- modify an accepted Gate 12 or earlier Gate 13 module;
- stage, commit, push, merge, tag, or publish repository history.

## Acceptance evidence

Synthetic-only tests must prove:

- exact version and eight-field result order;
- successful nested-path PNG file execution;
- exact input SHA-256 and byte length;
- exactly one file open and one `MAX_INPUT_BYTES + 1` read;
- exact bytes passed once to the accepted orchestration;
- governed source rejection without parser execution;
- parser rejection persistence;
- persistence-failure propagation;
- idempotent repeated execution;
- controlled empty, oversized, missing, directory, root, and read failures;
- no orchestration invocation for oversized input;
- malformed relative-path rejection before file opening;
- immutable result objects;
- absence of network, decoder, model, random, clock, temporary-file, and CLI dependencies;
- preservation of all accepted Gate 12 and Gate 13 paths.

## Continuation

After independent acceptance and exact commit publication, a post-file-runtime reconciliation review must determine whether the Gate 13 Definition of Done is complete or whether one additional non-semantic closure gap remains.
