# RCIS v1 / RIE 0.1.0 - Release Notes

## Release state

- Document type: `FINAL_RELEASE_DOCUMENT_CANDIDATE`
- Product label: `RCIS v1`
- Package: `rie`
- Package version represented by source: `0.1.0`
- Release title: `RCIS v1 - Governed Creative Knowledge, Asset, Approval, and Workflow`
- Release mode: `SOURCE_AND_GOVERNANCE_WITHOUT_BINARY_ATTACHMENT`
- Final required-gate checkpoint before release-document finalization: `3a8cb5c0f34c26c86d2c1a68b77b983bc9f1f511`
- Candidate annotated product release tag: `v0.1.0`
- Release authorized: `False`
- Release published: `False`

## Required-gate status

The mandatory RCIS v1 gate path is complete at the checkpoint above:

- Gate 14 - Multimodal Evidence and Knowledge: closed and published.
- Gate 15 - Master Asset Library Runtime: closed and published.
- Gate 16 - Operator Dashboard and Approval Workflow: closed and published.
- Gate 17 - Optional Generator Integration: deferred optional post-v1 and non-blocking.
- Gate 18 - Governed Creative Workflow: closed and published.

Gate 18 closure is recorded by the accepted PR-125H post-publication verification.

## Product scope represented by this release candidate

RCIS v1 is a governed creative knowledge, asset, approval, and workflow system.

The represented source state includes:

- governed official-source and evidence foundations;
- multimodal evidence and knowledge capabilities accepted through Gate 14;
- governed master asset-library runtime capabilities accepted through Gate 15;
- operator dashboard and approval-workflow capabilities accepted through Gate 16;
- governed creative-workflow assessment and operator-facing Workflow workspace accepted through Gate 18;
- explicit separation between workflow assessment and production-release authority;
- audit-oriented, fail-closed operation and evidence preservation.

The release does not require Gate 17 local generator integration.

## Gate 18 release boundary

Gate 18 workflow completion does not itself claim production release.

The published PySide Workflow workspace reuses the existing governed creative-workflow application service and does not create new domain, approval, asset, persistence, network, Gate 17, or production-release semantics.

Normal product-shell launch does not invent Gate 18 authority.

## Validation evidence

The controlling Gate 18 full validation is PR-125F:

- full suite: `3 failed, 5813 passed`;
- failed-node set exactly matched the accepted Gate 16 baseline residual set;
- no new Gate 18 regression was observed;
- clean fresh-environment acceptance reached `ingest pdf` and failed with exit code `7`, issue class `parser_failure`;
- clean acceptance did not fail because `rie.exe` was missing;
- packaging smoke passed;
- repository diff check passed.

PR-125H then verified the published Gate 18 checkpoint with:

- exact two-path published tree and blob identities;
- unchanged Gate 18 backend contracts and local runtime;
- verified remote `main`;
- clean worktree and empty index;
- targeted Gate 18 suite: `867 passed`;
- packaging smoke passed.

## Disclosed baseline validation debt

Three known baseline validation debts remain and are not represented as fixed:

1. `tests/acceptance/test_rie_core_v1_fresh_environment.py::test_fresh_environment_installed_end_to_end_workflow`
   - clean isolated reproduction reaches `ingest pdf`;
   - operator result: exit `7`, `issue_code=parser_failure`, `PDF parser execution failed`;
   - cause beyond the parser-failure boundary is not established by the accepted evidence.

2. `tests/evidence_materialization/test_evidence_materialization_boundary.py::test_package_contains_exact_reviewed_python_files`
   - stale exact-package assertion;
   - observed extra module: `atomic_text_evidence_derivation.py`.

3. `tests/test_persisted_evidence_knowledge_construction_public_api.py::test_package_contains_exact_four_python_files`
   - stale exact-package assertion;
   - observed extra module: `persisted_traceable_evidence_acceptance_bridge.py`.

The release must preserve this disclosure.

## Release mode and binary attachment boundary

The selected release mode remains:

`SOURCE_AND_GOVERNANCE_WITHOUT_BINARY_ATTACHMENT`

No wheel, source-distribution archive, dependency bundle, virtual environment, cache, wheelhouse, acceptance sandbox, or real RSV asset is a release attachment.

Historical wheel fingerprints remain provenance evidence only and must not be represented as current release attachments.

This release candidate does not make a binary-installation-bundle or offline-installation claim.

## Product release tag boundary

The candidate final product release tag is:

`v0.1.0`

This tag is distinct from historical phase tags such as:

`v0.76.0-rcis-creative-workflow-and-production-release-gate-18-phase`

The phase tag records a historical phase identity. It is not the final RCIS v1 product release tag.

The `v0.1.0` tag must:

- remain absent until a separate exact release authorization is approved;
- be annotated;
- target the exact verified release commit after these release documents are finalized and published;
- be pushed non-force;
- never be moved, recreated, or silently repointed after publication.

## Excluded release actions

This document does not authorize:

- source mutation beyond separately approved release-document finalization;
- Gate 17 implementation;
- new domain or workflow semantics;
- new production-release semantics;
- binary attachment publication;
- dependency installation;
- real RSV asset processing;
- tag creation;
- GitHub release creation;
- force push;
- history rewriting.

## Rollback and withdrawal

Published repository history must remain forward-only.

A correction must use a separately reviewed forward commit or revert commit.

A published product release tag must remain immutable.

Any withdrawal must preserve the release identity, tag identity, governance evidence, known-debt disclosure, withdrawal reason, and corrective next step.

## Finalization sequence

This release-note candidate becomes final only after:

1. this exact release note and the source/governance handoff are committed and published;
2. the resulting release-document commit is independently verified;
3. the exact `v0.1.0` annotated-tag proposal is separately approved;
4. the tag is created on the verified release commit, pushed non-force, and independently verified;
5. final release evidence records the resolved commit, tag object, peeled target, remote identity, and disclosed validation debt.

Until that sequence completes:

- `RCIS_V1_RELEASE_AUTHORIZED=False`;
- `RCIS_V1_RELEASED=False`.
