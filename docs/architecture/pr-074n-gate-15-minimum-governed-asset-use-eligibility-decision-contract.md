# PR-074N Gate 15 Minimum Governed Asset Use-Eligibility Decision Contract

## Status

This document defines the minimum governed asset use-eligibility decision
contract for Gate 15.

It is a bounded architecture contract. It does not implement a runtime
evaluator, persistence, search, importer behavior, filtering, user interface
behavior, real-asset execution, legal inference, or semantic interpretation.

## Purpose

`GovernedAssetRecord` records asset identity, provenance, usage-rights
reference, version identity, lifecycle state, and stored use eligibility.

`GovernedAssetUsageRights` records rights identity, rights holder reference,
permitted use scope, restriction scope, validity state, and use authorization.

Neither record alone is sufficient to authorize one requested use.

This contract defines the deterministic fail-closed decision that joins exactly
one asset record to exactly one matching usage-rights record for one explicit
requested use.

## Decision inputs

A use-eligibility decision requires exactly these six inputs:

1. `asset_record`
2. `usage_rights_record`
3. `requested_use_scope`
4. `asset_record_reference`
5. `usage_rights_record_reference`
6. `decision_context_reference`

No input has an implicit default.

Every input must be present before a decision can be evaluated.

## `asset_record`

`asset_record` must be one accepted immutable `GovernedAssetRecord`.

The record must retain its original six field values.

The decision must not rewrite the asset record.

## `usage_rights_record`

`usage_rights_record` must be one accepted immutable
`GovernedAssetUsageRights`.

The record must retain its original six field values.

The decision must not rewrite the usage-rights record.

## `requested_use_scope`

`requested_use_scope` identifies the exact proposed use being evaluated.

It must be non-empty ASCII text.

A generic, missing, or inferred requested use is invalid.

Possession of an asset file is not a requested use scope.

## Record references

`asset_record_reference` must identify the exact asset record being evaluated.

`usage_rights_record_reference` must identify the exact rights record being
evaluated.

Both references must be non-empty ASCII text.

The asset record's `usage_rights_reference` must resolve to exactly the supplied
`usage_rights_record_reference`.

Zero matches, multiple matches, or a mismatched reference must fail closed.

## `decision_context_reference`

`decision_context_reference` identifies the governed context in which the
decision was requested.

It must be non-empty ASCII text.

It is an audit reference. It must not be interpreted as permission.

## Decision output

The decision output has exactly one of these values:

- `ELIGIBLE`
- `INELIGIBLE`

No other decision value is part of this minimum contract.

`INELIGIBLE` is the fail-closed result.

## Eligibility rule

The output may be `ELIGIBLE` only when all of these predicates are true:

1. `asset_record_reference` resolves to exactly the supplied asset record;
2. `usage_rights_record_reference` resolves to exactly the supplied
   usage-rights record;
3. `asset_record.usage_rights_reference` equals
   `usage_rights_record_reference`;
4. `asset_record.lifecycle_state` is `ACTIVE`;
5. `asset_record.use_eligibility` is `ELIGIBLE`;
6. `usage_rights_record.validity_state` is `ACTIVE`;
7. `usage_rights_record.use_authorization` is `AUTHORIZED`;
8. `requested_use_scope` is explicitly included within
   `usage_rights_record.permitted_use_scope`;
9. `requested_use_scope` is not blocked by
   `usage_rights_record.restriction_scope`;
10. all required references and scope values are present, non-empty, and
    ASCII;
11. no source evidence required by either record is unresolved;
12. no contradictory governed fact is present.

If any predicate is false or unresolved, the output must be `INELIGIBLE`.

## Deterministic evaluation order

An implementation derived from this contract must evaluate in this order:

1. validate all required decision inputs;
2. validate exact asset-record reference resolution;
3. validate exact usage-rights-record reference resolution;
4. validate the asset-to-rights reference match;
5. validate asset lifecycle and stored eligibility;
6. validate rights validity and authorization;
7. validate permitted scope inclusion;
8. validate restriction exclusion;
9. return `ELIGIBLE` only when every prior step succeeds;
10. otherwise return `INELIGIBLE`.

The evaluator must not skip a failed predicate because a later predicate
appears favorable.

## Scope comparison boundary

This contract requires an explicit deterministic scope comparison.

It does not authorize semantic similarity, embeddings, language-model
interpretation, fuzzy matching, ontology reasoning, or inferred equivalence.

Until a later bounded contract defines a richer representation, scope inclusion
and restriction checks must use exact governed values supplied by the caller.

An empty permitted scope must not mean unrestricted use.

An empty restriction scope must not mean no restrictions.

## Relationship to stored asset eligibility

The asset record's stored `use_eligibility` is necessary but not sufficient.

`asset_record.use_eligibility=ELIGIBLE` does not override rights validity,
authorization, permitted scope, restrictions, or reference mismatch.

`asset_record.use_eligibility=INELIGIBLE` always produces an
`INELIGIBLE` decision.

The decision output does not automatically mutate the asset record.

## Relationship to rights authorization

`usage_rights_record.use_authorization=AUTHORIZED` is necessary but not
sufficient.

Authorization does not override an inactive asset, an ineligible asset, a
reference mismatch, a scope mismatch, or a restriction.

`usage_rights_record.use_authorization=NOT_AUTHORIZED` always produces an
`INELIGIBLE` decision.

## Generated assets

Generated or transformed assets use the same decision rules.

Generation does not erase provenance, rights references, restrictions, or
Official Source linkage.

Locally generated output does not receive automatic eligibility.

## Fail-closed reasons

The following conditions must produce `INELIGIBLE`:

- missing decision input;
- empty or non-ASCII reference or requested scope;
- unresolved asset record;
- unresolved usage-rights record;
- more than one matching asset or rights record;
- asset-to-rights reference mismatch;
- asset lifecycle other than `ACTIVE`;
- stored asset eligibility other than `ELIGIBLE`;
- rights validity other than `ACTIVE`;
- rights authorization other than `AUTHORIZED`;
- requested use outside the permitted scope;
- requested use blocked by a restriction;
- unresolved source evidence;
- contradictory governed facts;
- attempted semantic, fuzzy, or inferred scope matching.

## Audit boundary

A future runtime decision may record its inputs and output for audit.

This contract does not define persistence, timestamps, storage format,
supersession, history traversal, or database schema.

The immutable source records must remain independently auditable.

## Explicit non-goals

This contract does not authorize:

- a runtime decision evaluator;
- a decision domain model;
- source code or tests;
- persistence or database schema;
- deterministic search infrastructure;
- semantic search;
- filtering runtime;
- batch importers or crawlers;
- dashboards or user interfaces;
- real-asset scans;
- automated legal interpretation;
- OCR;
- embeddings or vector databases;
- AI connectors;
- Local AI Generator Integration;
- Gate 16, Gate 17, or Gate 18 implementation.

## Smallest continuation boundary

After independent acceptance and publication of this contract, the next review
may determine whether a minimum deterministic use-eligibility decision domain
model is the next smallest Gate 15 dependency.

That later review must separately authorize any source code, targeted tests,
stage, commit, push, persistence, or runtime behavior.

Whole Gate 15 implementation remains unauthorized.
