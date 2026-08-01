# PR-074T Gate 15 Minimum Governed Asset Library Exact-Reference Registry Contract

## Status

This document defines the minimum governed asset library exact-reference
registry contract for Gate 15.

It is a bounded architecture contract. It does not implement persistence, a
database, search, filtering, importing, a user interface, real-asset
processing, legal inference, semantic interpretation, or a generalized
repository abstraction.

## Purpose

Gate 15 now has immutable domain models for:

- `GovernedAssetRecord`;
- `GovernedAssetUsageRights`;
- `GovernedAssetUseEligibilityDecision`.

Those models define individual governed facts and one deterministic eligibility
decision. They do not yet define the minimum library container that can retain
multiple records while preserving unique identities and exact references.

This contract defines that minimum container boundary.

## Registry snapshot

A governed asset library registry is one immutable snapshot constructed from
exactly these two collections:

1. `asset_records`
2. `usage_rights_records`

Both collections are required inputs.

Either collection may be empty.

No implicit default collection is part of this contract.

The registry snapshot must not mutate, replace, normalize, merge, or infer
values in any supplied record.

## Accepted record types

Every member of `asset_records` must be one accepted immutable
`GovernedAssetRecord`.

Every member of `usage_rights_records` must be one accepted immutable
`GovernedAssetUsageRights`.

Any other object type must cause registry construction to fail closed.

The registry must retain the supplied record values exactly.

## Exact asset identity

`asset_record_id` is the exact registry key for an asset record.

Within one registry snapshot:

- each `asset_record_id` must be non-empty ASCII text;
- each `asset_record_id` must occur exactly once;
- matching is case-sensitive;
- leading or trailing characters must not be normalized;
- two records with the same `asset_record_id` must be rejected even when their
  remaining fields are identical.

The registry must not deduplicate asset records by content, provenance,
filename, version identity, or source reference.

## Exact rights identity

`rights_record_id` is the exact registry key for a usage-rights record.

Within one registry snapshot:

- each `rights_record_id` must be non-empty ASCII text;
- each `rights_record_id` must occur exactly once;
- matching is case-sensitive;
- leading or trailing characters must not be normalized;
- two records with the same `rights_record_id` must be rejected even when their
  remaining fields are identical.

The registry must not deduplicate usage-rights records by holder, scope,
restriction, validity, or authorization.

## Referential integrity

Every asset record contains one `usage_rights_reference`.

For every asset record in the registry:

1. `usage_rights_reference` must be non-empty ASCII text;
2. it must exactly equal one registered `rights_record_id`;
3. zero matching rights records must fail closed;
4. more than one matching rights record must fail closed;
5. case folding, trimming, aliases, semantic similarity, and inferred
   equivalence are prohibited.

A rights record may exist without being referenced by an asset record.

An asset record may not exist in an accepted registry snapshot when its
rights reference is unresolved.

## Deterministic construction order

Registry construction must validate in this order:

1. validate both required collections;
2. validate every asset record type;
3. validate every usage-rights record type;
4. validate all asset IDs;
5. reject duplicate asset IDs;
6. validate all rights IDs;
7. reject duplicate rights IDs;
8. validate every asset `usage_rights_reference`;
9. resolve every reference by exact rights ID;
10. reject every missing or ambiguous reference;
11. accept the immutable registry snapshot only when all prior checks pass.

A later successful check must not override an earlier failure.

## Exact retrieval

The minimum registry supports deterministic exact retrieval only.

Exact asset retrieval accepts one `asset_record_id`.

Exact rights retrieval accepts one `rights_record_id`.

Retrieval behavior must satisfy all of these rules:

- comparison is exact and case-sensitive;
- no trimming or normalization is performed;
- a registered exact ID returns exactly one immutable record;
- an unregistered ID fails closed as `NOT_FOUND`;
- multiple results are impossible in an accepted registry;
- retrieval does not mutate the registry or returned record;
- retrieval order does not affect the result.

`NOT_FOUND` is not permission to create, infer, substitute, or import a record.

## Exact reference resolution

Exact reference resolution accepts one asset record or one exact
`asset_record_id`.

It returns the single immutable usage-rights record whose `rights_record_id`
exactly matches the asset record's `usage_rights_reference`.

Missing asset identity, missing rights identity, mismatched identity, or
unresolved reference must fail closed.

Exact reference resolution does not evaluate use eligibility.

Eligibility remains the responsibility of the separately governed
`GovernedAssetUseEligibilityDecision`.

## Immutability boundary

An accepted registry snapshot is immutable.

This minimum contract does not permit:

- adding a record after construction;
- replacing a record;
- deleting a record;
- changing an ID;
- changing a rights reference;
- mutating a retained record;
- automatically promoting a candidate asset;
- automatically changing lifecycle, validity, authorization, or eligibility.

A changed collection requires construction of a separate new snapshot under a
later authorized contract.

This contract does not define snapshot identity, history, supersession, or
persistence.

## Ordering boundary

Input ordering must not change:

- uniqueness validation;
- referential-integrity validation;
- exact retrieval results;
- exact reference-resolution results.

This contract does not require sorting or define a presentation order.

## Version and lifecycle boundary

Multiple asset records may have different IDs while sharing a
`version_identity`.

The registry does not infer which version is current.

It does not automatically suppress `DEPRECATED` or `SUPERSEDED` records.

It does not automatically select an `ACTIVE` record.

Lifecycle and version interpretation remain governed by the individual asset
records and later explicitly authorized behavior.

## Rights-state boundary

The registry retains rights records regardless of whether their
`validity_state` is `UNVERIFIED`, `ACTIVE`, `EXPIRED`, or `REVOKED`.

The registry does not convert rights validity into authorization.

It does not remove or hide a `NOT_AUTHORIZED` rights record.

Eligibility evaluation remains separate.

## Generated assets

Generated or transformed assets follow the same registration and reference
rules.

Generation does not create an implicit asset ID, rights ID, or rights
reference.

Generated output does not receive automatic registration, authorization, or
eligibility.

Official Source linkage and provenance remain independently governed.

## Fail-closed conditions

Registry construction must fail closed for:

- a missing required collection;
- a member with the wrong record type;
- an empty or non-ASCII asset ID;
- an empty or non-ASCII rights ID;
- a duplicate asset ID;
- a duplicate rights ID;
- an empty or non-ASCII usage-rights reference;
- a missing exact rights target;
- an ambiguous rights target;
- attempted case folding or normalization;
- attempted semantic or fuzzy identity matching;
- attempted automatic record mutation;
- contradictory governed facts required for construction.

Exact retrieval or reference resolution must fail closed for:

- an empty or non-ASCII requested ID;
- an unregistered ID;
- an identity mismatch;
- an unresolved reference.

## Explicit non-goals

This contract does not authorize:

- a registry runtime domain model;
- source code or tests;
- persistence or serialization;
- a database or schema;
- filesystem storage;
- search or semantic search;
- filtering, ranking, or pagination;
- filename, path, tag, metadata, or content queries;
- batch importers, crawlers, or folder scans;
- update, delete, or merge operations;
- dashboards or user interfaces;
- real-asset execution;
- automated legal interpretation;
- OCR;
- embeddings or vector databases;
- AI connectors;
- Local AI Generator Integration;
- Gate 16, Gate 17, or Gate 18 implementation.

## Smallest continuation boundary

After independent acceptance and publication of this contract, the next review
may determine whether one immutable in-memory exact-reference registry domain
model and one targeted test are the next smallest Gate 15 dependency.

That later review must separately authorize source code, tests, stage, commit,
push, or any other mutation.

Persistence, database behavior, search, filtering, importer behavior, and whole
Gate 15 implementation remain unauthorized.
