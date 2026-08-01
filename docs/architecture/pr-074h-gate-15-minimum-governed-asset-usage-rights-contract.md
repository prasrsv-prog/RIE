# PR-074H Gate 15 Minimum Governed Asset Usage-Rights Contract

## Status

This document defines the minimum governed asset usage-rights contract for
Gate 15.

It is a bounded architecture contract. It does not implement a runtime model,
persistence, search, importer behavior, user interface behavior, real-asset
execution, or legal inference.

## Dependency

The governed asset record stores a required `usage_rights_reference`.

That reference must resolve to a separately governed usage-rights record before
an asset can be considered eligible for operational use.

A string reference alone is not proof of rights.

## Minimum record

A governed asset usage-rights record has exactly these six required fields:

1. `rights_record_id`
2. `rights_holder_reference`
3. `permitted_use_scope`
4. `restriction_scope`
5. `validity_state`
6. `use_authorization`

No field has an implicit default.

Every field must be present before the record can be accepted.

## `rights_record_id`

`rights_record_id` is the stable identity of one usage-rights record.

It must be non-empty ASCII text.

It is immutable after record creation.

It must not be reused for a different rights statement.

## `rights_holder_reference`

`rights_holder_reference` identifies the governed source that names the person,
organization, agreement, license, or other authority associated with the
recorded rights.

It must be non-empty ASCII text.

It is a reference, not an inferred legal conclusion.

The system must not manufacture a rights holder from filenames, folders,
metadata, generated content, or operator assumptions.

## `permitted_use_scope`

`permitted_use_scope` records the bounded use scope explicitly supported by the
governed source.

It must be non-empty ASCII text.

It must not silently expand beyond the source statement.

An empty value must not be interpreted as unrestricted permission.

## `restriction_scope`

`restriction_scope` records restrictions, exclusions, or unresolved limits
that apply to the permitted use scope.

It must be non-empty ASCII text.

When the source does not establish the restriction scope, the record must state
that the scope is unresolved rather than inventing a restriction or declaring
that no restriction exists.

## `validity_state`

`validity_state` has exactly one of these values:

- `UNVERIFIED`
- `ACTIVE`
- `EXPIRED`
- `REVOKED`

`UNVERIFIED` means the available governed source is insufficient to establish
current validity.

`ACTIVE` means the governed source explicitly supports current validity within
the recorded scope.

`EXPIRED` means the governed source establishes that the rights are no longer
current because their validity period ended.

`REVOKED` means the governed source establishes that the rights were withdrawn
or cancelled.

No other validity value is part of this minimum contract.

## `use_authorization`

`use_authorization` has exactly one of these values:

- `AUTHORIZED`
- `NOT_AUTHORIZED`

`AUTHORIZED` is permitted only when `validity_state` is `ACTIVE`.

A record with `UNVERIFIED`, `EXPIRED`, or `REVOKED` validity must have
`use_authorization=NOT_AUTHORIZED`.

An `ACTIVE` record may still be `NOT_AUTHORIZED` when its permitted use scope
does not cover the requested operation or when a restriction blocks that use.

Authorization is an explicit governed decision. It must not be inferred from
the absence of a restriction, from possession of a file, or from the existence
of an asset record.

## Relationship to asset eligibility

A governed asset record may be eligible only when all of these conditions are
true:

1. its `usage_rights_reference` resolves to exactly one governed usage-rights
   record;
2. that rights record has `validity_state=ACTIVE`;
3. that rights record has `use_authorization=AUTHORIZED`;
4. the requested use falls within `permitted_use_scope`;
5. the requested use is not blocked by `restriction_scope`;
6. the asset record independently satisfies its provenance, lifecycle, and
   eligibility rules.

A rights record does not replace provenance.

A rights record does not replace Official Source linkage.

A rights record does not promote an asset automatically.

## Generated assets

Generated assets do not receive broader rights merely because they were
generated locally or transformed from another asset.

A generated asset must retain governed provenance and an explicit rights
reference.

Generated output must not replace the Official Source or erase restrictions
inherited from its source material.

## Immutability and supersession

The six recorded field values are immutable.

A changed rights statement requires a new `rights_record_id`.

A newer record may supersede an older record through a future explicit
relationship, but supersession behavior is not implemented by this contract.

The older record must remain auditable.

## Fail-closed rules

The following conditions are invalid:

- missing or empty required fields;
- non-ASCII field values;
- an unknown validity state;
- an unknown authorization decision;
- `AUTHORIZED` with any validity state other than `ACTIVE`;
- an unresolved rights reference treated as permission;
- an empty permitted scope treated as unrestricted use;
- an empty restriction scope treated as no restriction;
- inferred legal authority without governed source evidence;
- automatic authorization based on file possession or asset existence.

Invalid or unresolved rights must fail closed as `NOT_AUTHORIZED`.

## Explicit non-goals

This contract does not authorize:

- a usage-rights runtime domain model;
- persistence or database schema;
- deterministic or semantic search;
- filtering runtime;
- batch importers or crawlers;
- dashboards or user interfaces;
- real-asset scans;
- automated legal interpretation;
- license classification by inference;
- OCR;
- embeddings or vector databases;
- AI connectors;
- Local AI Generator Integration;
- Gate 16, Gate 17, or Gate 18 implementation.

## Smallest continuation boundary

After independent acceptance and publication of this contract, the next review
may determine whether a minimum immutable usage-rights domain model is the next
smallest Gate 15 dependency.

That later review must separately authorize any source code, tests, branch
mutation, persistence, or runtime behavior.

Whole Gate 15 implementation remains unauthorized.
