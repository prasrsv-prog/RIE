# PR-074B - Gate 15 Minimum Governed Asset Record Identity and Lifecycle Contract

## 1. Authority and scope

This contract is the first bounded Gate 15 materialization after the accepted PR-074A Correction 2 initiation and reconciliation review.

Gate 15 remains limited to the Master Asset Library Runtime. This document defines only the minimum governed asset-record identity and lifecycle boundary selected by PR-074A. It does not implement runtime behavior.

The governing boundaries remain:

- an asset library is not a folder dump;
- no governed asset record exists without explicit provenance and usage-rights references;
- generated output does not replace an Official Source;
- deprecated or superseded assets are not eligible for automatic use;
- Source Material, Evidence, Knowledge, business decisions, generated output, and accepted assets remain distinct authority layers;
- no automatic promotion is allowed.

## 2. Selected smallest gap

The selected smallest remaining Gate 15 gap is:

`MINIMUM_GOVERNED_ASSET_RECORD_IDENTITY_AND_LIFECYCLE_CONTRACT`

This gap is narrower than persistence, search, import, classification, product-variant mapping, Official Source linkage, Knowledge linkage, UI, approval workflow, or real-asset execution.

## 3. Minimum governed asset record

A minimum governed asset record contains exactly the following contract fields:

1. `asset_record_id`
   - Required stable identity for the governed record.
   - Non-empty ASCII text.
   - Immutable after record creation.
   - It identifies the governed metadata record, not a folder path and not an Official Source.

2. `provenance_reference`
   - Required explicit reference to the accepted provenance material supporting the record.
   - Non-empty ASCII text.
   - The reference remains an identifier only in this contract; reference resolution is deferred.
   - Presence of this reference does not automatically promote Source Material to Evidence, Evidence to Knowledge, or generated output to an accepted asset.

3. `usage_rights_reference`
   - Required explicit reference to the applicable usage-rights record or controlled rights assertion.
   - Non-empty ASCII text.
   - Rights interpretation, external license services, and policy engines are outside this contract.

4. `version_identity`
   - Required immutable identity for the represented asset version.
   - Non-empty ASCII text.
   - It is distinct from `asset_record_id`.
   - Version relationships, migration, replacement, and persistence are deferred.

5. `lifecycle_state`
   - Required explicit state.
   - Allowed values are exactly `CANDIDATE`, `ACTIVE`, `DEPRECATED`, or `SUPERSEDED`.
   - State transition services and approval workflow are outside this contract.

6. `use_eligibility`
   - Required explicit eligibility state.
   - Allowed values are exactly `ELIGIBLE` or `INELIGIBLE`.
   - Eligibility is never inferred from a file location, filename, generated-output status, lifecycle state, model output, or search result.

No optional field is introduced by this contract.

## 4. Deterministic invariants

A governed asset record conforms to this contract only when all of the following are true:

1. All six fields are present.
2. All identity and reference fields are non-empty ASCII text.
3. `asset_record_id` and `version_identity` are treated as immutable identities.
4. `lifecycle_state` is one of the four exact allowed values.
5. `use_eligibility` is one of the two exact allowed values.
6. `ELIGIBLE` is valid only when `lifecycle_state` is `ACTIVE`.
7. `CANDIDATE`, `DEPRECATED`, and `SUPERSEDED` records must be `INELIGIBLE`.
8. A missing provenance reference makes the record invalid.
9. A missing usage-rights reference makes the record invalid.
10. A generated asset record remains distinct from and cannot replace an Official Source.
11. The record does not become Evidence or Knowledge merely by existing.
12. No directory scan, filename convention, duplicate heuristic, semantic inference, model reasoning, or external tool output may create or promote the record automatically.

## 5. Authority behavior

This contract establishes metadata identity only.

- `asset_record_id` identifies a governed asset record.
- `provenance_reference` preserves the explicit upstream provenance boundary.
- `usage_rights_reference` preserves the explicit rights boundary.
- `version_identity` distinguishes the represented version without defining storage or migration.
- `lifecycle_state` records the explicit lifecycle classification.
- `use_eligibility` records the explicit use boundary.

The record is not itself:

- an Official Source;
- Evidence;
- Knowledge;
- a business approval;
- a generated file;
- a persisted binary asset;
- a search result;
- an instruction to automatically use the asset.

## 6. Explicit non-expansion boundary

PR-074B does not authorize or define:

- persistence, database schema, filesystem storage, or migration;
- deterministic or semantic search;
- embeddings, vector databases, ontologies, knowledge graphs, or inference;
- folder crawling, batch import, real-asset scanning, or duplicate resolution;
- product-variant mapping;
- campaign or event classification;
- persona or OOTD references;
- Official Source relationship implementation;
- Knowledge relationship implementation;
- evidence materialization for assets;
- dashboard, UI, roles, approval workflow, or multi-user behavior;
- generator connectors, model orchestration, inference queues, or GPU management;
- tests, runtime code, configuration, packaging, or deployment.

## 7. Contract acceptance evidence

PR-074B is complete only when independent evidence confirms:

- this exact document is the only repository path created or modified;
- the document is ASCII-only, LF-only, has no BOM or null bytes, and has exactly one final LF;
- all six required fields and all deterministic invariants are present;
- all non-expansion boundaries are present;
- no test execution occurred;
- no branch, index, commit, tag, remote, source, test, configuration, migration, or real-asset mutation occurred;
- Gate 15 implementation remains unauthorized.

## 8. Controlled continuation

After independent acceptance of PR-074B, the only candidate continuation is:

`PR_074C_GATE_15_MINIMUM_GOVERNED_ASSET_RECORD_CONTRACT_STAGE_COMMIT_PUSH`

That separate bounded operation may place this contract under Git governance through exact-path staging, commit, push, and post-publication verification. It must not implement the domain model, persistence, search, importer, UI, or real-asset behavior. It remains unauthorized until PR-074B is independently accepted.
