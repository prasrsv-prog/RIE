# PR-058A - Phase 57 Operational Activation Scope and Minimum Closure Boundary Review

## Status

PROPOSED

## Identity

- Phase: 57
- PR boundary: PR-058A
- Phase branch: `phase-057-operational-activation-readiness`
- Parent branch: `main`
- Required parent commit: `eeb1e2108b4dada892f360edba1450ba01d25b92`
- Previous phase: Phase 56, formally closed
- Previous annotated tag: `v0.56.0-rcis-end-to-end-cli-audit-packaging-release-phase`
- Previous tag object: `2621bb49d361cd8149a0d059235030d797edc95a`
- Release mode: `SOURCE_AND_GOVERNANCE_WITHOUT_BINARY_ATTACHMENT`

## Decision

Phase 57 is authorized to begin only as an operational-activation readiness phase.

PR-058A freezes scope and minimum closure criteria. It does not authorize dependency installation, fresh-environment acceptance execution, sample workflow execution, a real RSV PDF pilot, source-code implementation, official-source registry mutation, hosted-release mutation, or tag mutation.

## Objective

Prove in later reviewed steps that the formally released RIE Core v1 source-and-governance package can be prepared and used by an operator in a controlled fresh local environment.

Phase 57 targets:

1. reproducible repository-local environment preparation;
2. bounded dependency installation;
3. public CLI invocation without source-code editing;
4. committed sample workflow execution;
5. audit and recovery verification;
6. rerun and idempotency verification;
7. operator instructions and rollback evidence;
8. zero use of real RSV assets;
9. zero mutation of the closed Phase 56 release identity.

## In scope after separate authorization

- released source and tag identity verification;
- installation and configuration contract review;
- repository-local `.venv`;
- exact committed dependency boundary;
- public `python -m rie` operator entry point;
- committed sample registry;
- committed sample PDF;
- controlled sample output;
- audit and recovery inspection;
- sample rerun and idempotency verification;
- operator command and rollback documentation.

## Out of scope

- real RSV PDF or image selection;
- real RSV asset reading, inspection, registration, or processing;
- mutation of a real official-source registry;
- OCR or image extraction;
- visual or multimodal knowledge;
- dashboard or graphical user interface;
- multi-user approval;
- Master Asset Library;
- ComfyUI, Stable Diffusion, Ollama, or generator integration;
- feature expansion beyond released RIE Core v1;
- modification of the Phase 56 release commit;
- tag replacement, deletion, movement, or recreation;
- hosted-release modification, deletion, retargeting, or asset upload;
- wheel or binary release attachment;
- global or system-wide dependency installation;
- reset, clean, amend, rebase, squash, force-push, or destructive recovery;
- automatic retry after a failed acceptance.

## Frozen Phase 56 inputs

- release commit: `eeb1e2108b4dada892f360edba1450ba01d25b92`;
- release parent: `22f981a5a0c2aebfcdffb1a5a700a165f3122d33`;
- release subject: `docs: authorize RIE Core v1 source-and-governance release`;
- annotated tag: `v0.56.0-rcis-end-to-end-cli-audit-packaging-release-phase`;
- tag object: `2621bb49d361cd8149a0d059235030d797edc95a`;
- tag target: `eeb1e2108b4dada892f360edba1450ba01d25b92`;
- hosted release ID: `358581550`;
- release title: `RIE Core v1 - Governed PDF Operator Workflow`;
- uploaded release assets: `0`.

These identities are immutable released inputs. Phase 57 must not be treated as a continuation or mutation of Phase 56.

## Proposed PR sequence

### PR-058A

Operational-activation scope and minimum-closure-boundary review.

### PR-058B

Fresh-environment installation and configuration contract review.

### PR-058C

Committed sample workflow and operator CLI execution authorization review.

### PR-058D

Fresh-environment installation and committed sample workflow execution.

### PR-058E

Fresh-environment and sample-workflow evidence review.

### PR-058F

Operator usability, audit, recovery, rerun, and idempotency acceptance review.

### PR-058G

Phase 57 closure authorization review.

### PR-058H

Phase 57 closure execution and closure record.

Additional PRs require separate evidence and must not silently expand scope.

## Installation boundary

PR-058A performs no installation.

A later authorization must require:

- repository-local `.venv`;
- no global package installation;
- exact dependency input from the repository;
- no dependency upgrade;
- no replacement of the committed lock boundary;
- explicit interpreter and package-version evidence;
- no source-code changes during acceptance.

## Sample-only boundary

Later execution may use only:

- `samples/rie-core-v1/sample-source.pdf`;
- `samples/rie-core-v1/official-source-registry.json`;
- committed operator documentation;
- a separately authorized controlled output location.

The committed sample PDF is not a real RSV production asset. Its presence does not authorize any other PDF.

## Real-asset boundary

Phase 57 does not authorize a real RSV PDF pilot.

A controlled real-asset pilot must be proposed in a separate later phase after Phase 57 is formally closed and independently accepted.

## Defect handling

If activation reveals a defect:

1. preserve failed evidence;
2. do not retry automatically;
3. do not patch source during execution;
4. classify the defect;
5. open a separate reviewed correction boundary;
6. keep Phase 56 release identities unchanged;
7. produce new evidence after correction.

## Minimum closure criteria

Phase 57 may close only after independent acceptance that:

- the installation contract is frozen;
- installation succeeds inside the authorized local environment;
- the public CLI starts successfully;
- the committed sample workflow completes;
- expected output, audit, and recovery artifacts are produced;
- rerun and idempotency behavior are verified;
- operator instructions work without source-code editing;
- rollback and failure preservation are proven;
- no real RSV asset was used;
- no real production registry was mutated;
- no Phase 56 release, tag, or hosted release mutation occurred;
- repository refs remain controlled;
- all execution and review evidence is preserved.

## PR-058A acceptance boundary

PR-058A is accepted only when:

- the phase branch is created from the exact Phase 56 release commit;
- this document is the only new working-tree path;
- its raw-byte contract is verified;
- nothing is staged;
- no commit or push is performed by the materialization step;
- no dependency is installed;
- no sample workflow is executed;
- no real asset is selected;
- no tag, release, or remote branch is mutated;
- the report ends with exactly one `FINAL_RESULT=PASSED`.

## Next operation after independent acceptance

After acceptance:

1. manually stage only this document;
2. manually commit with:
   `docs: define Phase 57 operational activation boundary`;
3. manually push the Phase 57 branch;
4. verify the commit and remote branch;
5. begin PR-058B.
