# RCIS v1 / RIE 0.1.0 - Source and Governance Handoff

## Handoff state

- Handoff type: `FINAL_RELEASE_HANDOFF_CANDIDATE`
- Product label: `RCIS v1`
- Package: `rie`
- Package version: `0.1.0`
- Release title: `RCIS v1 - Governed Creative Knowledge, Asset, Approval, and Workflow`
- Release mode: `SOURCE_AND_GOVERNANCE_WITHOUT_BINARY_ATTACHMENT`
- Final required-gate checkpoint before release-document finalization: `3a8cb5c0f34c26c86d2c1a68b77b983bc9f1f511`
- Candidate annotated product release tag: `v0.1.0`
- Binary attachment inventory: empty
- Release authorized: `False`
- Release published: `False`

## Repository and gate handoff

At the accepted final required-gate checkpoint:

- branch: `main`;
- HEAD, local `main`, origin tracking `main`, and live remote `main` all resolve to `3a8cb5c0f34c26c86d2c1a68b77b983bc9f1f511`;
- worktree is clean;
- index is empty;
- Gate 14 is closed;
- Gate 15 is closed;
- Gate 16 is closed;
- Gate 17 is deferred optional post-v1;
- Gate 18 is closed;
- all required RCIS v1 gates are closed.

The controlling final Gate 18 closure evidence is PR-125H.

## Current capability handoff

The source-and-governance handoff represents the accepted RCIS v1 capability boundary:

1. governed official-source, ingestion, evidence, knowledge, and prompt foundations;
2. Gate 14 multimodal evidence and knowledge;
3. Gate 15 governed master asset-library runtime;
4. Gate 16 operator dashboard and approval workflow;
5. Gate 18 governed creative-workflow assessment and operator-facing Workflow workspace;
6. explicit authority boundaries between evidence, knowledge, assets, approvals, workflow assessment, and any later production-release action;
7. fail-closed evidence preservation and forward-only repository governance.

Gate 17 local generator integration is not required for this release.

## Gate 18 implementation identity

The final required-gate checkpoint is:

`3a8cb5c0f34c26c86d2c1a68b77b983bc9f1f511`

Its subject is:

`Add Gate 18 governed workflow workspace`

Its parent is:

`c0ddc4ad7cca662e3679cd2ef63d01fd07c9e42f`

The Gate 18 publication changed exactly:

- `src/rie/ui/pyside_product_shell.py`;
- `tests/ui/test_pyside_product_shell.py`.

PR-125H independently verified the published tree/blob identities, remote `main`, clean repository state, 867 targeted tests, and packaging smoke.

## Validation handoff

PR-125F remains the controlling full-validation evidence:

- `3 failed, 5813 passed`;
- residual failed-node set exactly matches the accepted Gate 16 baseline residual set;
- no new Gate 18 regression observed;
- clean acceptance reaches `ingest pdf`;
- clean acceptance residual class is `parser_failure`, exit `7`;
- packaging smoke passes.

The three disclosed residual nodes are:

- `tests/acceptance/test_rie_core_v1_fresh_environment.py::test_fresh_environment_installed_end_to_end_workflow`;
- `tests/evidence_materialization/test_evidence_materialization_boundary.py::test_package_contains_exact_reviewed_python_files`;
- `tests/test_persisted_evidence_knowledge_construction_public_api.py::test_package_contains_exact_four_python_files`.

These are release disclosures, not hidden or silently reclassified as passing.

## Release document provenance

The final product release operation must preserve and verify the committed Git blob identities of:

- `docs/release/rie-core-v1-release-notes.md`;
- `docs/release/rie-core-v1-source-and-governance-handoff.md`.

The exact commit produced by publishing these finalized documents becomes the release commit only after an independent post-publication verification accepts it.

## Product tag boundary

The proposed product release tag is:

`v0.1.0`

It corresponds to the package version declared in `pyproject.toml`.

The final checkpoint currently has no tag pointing at it.

The `v0.1.0` product release tag is separate from phase tags. Existing phase tag `v0.76.0-rcis-creative-workflow-and-production-release-gate-18-phase` must not be moved, deleted, or repurposed.

The product tag remains unauthorized until a later exact proposal is approved.

## Binary and installation boundary

The release attachment inventory is empty.

The release does not attach:

- `rie-0.1.0-py3-none-any.whl`;
- dependency wheels;
- source-distribution archives;
- virtual environments;
- wheelhouses or caches;
- acceptance sandboxes;
- real RSV PDFs, JPEGs, PNGs, extracted content, or pilot outputs.

Historical binary fingerprints remain provenance only.

No binary-installation-bundle or offline-installation claim is made by this release mode.

## Operator verification boundary

After final release publication, the handoff evidence must record and verify:

- final release commit;
- local `main`;
- origin tracking `main`;
- live remote `main`;
- annotated product tag name;
- annotated tag object;
- peeled tag target;
- release-note Git blob identity;
- handoff Git blob identity;
- clean worktree;
- empty index;
- disclosed baseline validation debt.

Repository verification must not mutate source, history, tags, or real assets.

## Support boundary

This release supports the accepted source-and-governance state for RCIS v1.

It does not claim or authorize:

- Gate 17 local generator integration;
- automatic model orchestration;
- new production-release semantics;
- binary attachment delivery;
- offline installation support;
- real RSV asset processing without separate authority;
- force-push or history rewriting.

## Rollback and withdrawal

Corrections must use a separately reviewed forward commit or revert commit.

Published tags are immutable.

A withdrawal must preserve:

- final release commit identity;
- product tag object and peeled target;
- release documents;
- governance evidence;
- validation-debt disclosure;
- withdrawal reason;
- corrective next step.

## Finalization requirements

This handoff becomes final only after:

1. this exact handoff and release notes are committed and published;
2. that publication is independently verified;
3. an exact annotated `v0.1.0` tag proposal is separately approved;
4. the tag is created on the verified release commit and pushed non-force;
5. post-tag verification records the exact tag object, peeled target, remote identities, release-document blobs, and clean repository state.

Until then:

- `RCIS_V1_RELEASE_AUTHORIZED=False`;
- `RCIS_V1_RELEASED=False`.
