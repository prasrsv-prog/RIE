# PR-074Z Gate 15 Minimum Governed Asset Library Registry-Backed Use-Eligibility Evaluation Contract

## Status

This document defines the minimum governed asset library registry-backed
use-eligibility evaluation contract for Gate 15.

It is a bounded architecture contract. It does not implement source code,
tests, persistence, a database, search, filtering, importing, a user
interface, real-asset processing, legal inference, semantic matching, or a
generalized orchestration abstraction.

## Purpose

Gate 15 now has accepted immutable domain models for:

- `GovernedAssetRecord`;
- `GovernedAssetUsageRights`;
- `GovernedAssetUseEligibilityDecision`;
- `GovernedAssetLibraryRegistry`.

The registry provides deterministic exact retrieval and exact rights-reference
resolution. The decision model provides deterministic fail-closed
use-eligibility evaluation.

This contract defines the smallest integration boundary between those two
accepted models.

## Evaluation operation

The minimum operation is named
`evaluate_governed_asset_library_use_eligibility`.

It accepts exactly four required inputs:

1. `registry`
2. `asset_record_id`
3. `requested_use_scope`
4. `decision_context_reference`

No implicit input, default registry, default scope, default context, or
environment-derived value is part of this contract.

## Registry input

`registry` must be one accepted immutable
`GovernedAssetLibraryRegistry`.

Any other value must fail closed.

The evaluation operation must not:

- construct a substitute registry;
- add, replace, remove, or mutate registry records;
- normalize registry identities;
- infer a missing asset or rights record;
- load records from storage;
- import records from a folder or external source.

## Exact asset identity input

`asset_record_id` must be non-empty ASCII text.

It must be passed unchanged to the registry's exact asset retrieval behavior.

Comparison is exact and case-sensitive.

The operation must not trim, normalize, case-fold, alias, tokenize, rank,
search, or semantically match the requested asset identity.

A missing exact asset identity must fail closed with the registry's governed
`NOT_FOUND` behavior.

## Requested use-scope input

`requested_use_scope` must be non-empty ASCII text.

The value must be passed unchanged to
`GovernedAssetUseEligibilityDecision`.

The operation must not:

- split or merge scopes;
- expand a broad scope;
- narrow a scope;
- infer an equivalent scope;
- translate a scope;
- compare scopes semantically or fuzzily;
- substitute a permitted scope for the requested scope.

Scope equality and restriction behavior remain exactly as governed by the
decision model.

## Decision-context input

`decision_context_reference` must be non-empty ASCII text.

The value identifies the bounded context of one evaluation request.

It must be passed unchanged to
`GovernedAssetUseEligibilityDecision`.

The operation must not interpret the context reference as legal evidence,
authorization, provenance, a user identity, a policy override, or permission
to mutate any record.

## Deterministic evaluation sequence

The operation must execute in exactly this order:

1. validate the `registry` input;
2. validate `asset_record_id`;
3. validate `requested_use_scope`;
4. validate `decision_context_reference`;
5. retrieve the exact asset record from the registry;
6. resolve the exact usage-rights record through the registry;
7. construct one `GovernedAssetUseEligibilityDecision`;
8. return that immutable decision.

A later successful step must not override an earlier failure.

No fallback branch is permitted.

## Exact asset retrieval

The operation must use the registry's deterministic exact asset retrieval.

The returned asset record must be the same immutable record retained by the
registry for the exact `asset_record_id`.

The operation must not copy values into a different asset-record type, select
another version, prefer an `ACTIVE` version, or suppress a deprecated or
superseded record.

Lifecycle interpretation remains inside the governed decision inputs and
decision rules.

## Exact rights resolution

The operation must use the registry's deterministic exact reference
resolution for the retrieved asset record.

The returned usage-rights record must be the same immutable record whose
`rights_record_id` exactly equals the asset record's
`usage_rights_reference`.

The operation must not select rights by holder, scope, validity,
authorization, similarity, ordering, or recency.

Missing or mismatched rights references must fail closed through the registry
boundary.

## Decision construction

The operation must construct exactly one
`GovernedAssetUseEligibilityDecision` with these exact values:

- `asset_record` is the exact retrieved asset record;
- `usage_rights_record` is the exact resolved usage-rights record;
- `requested_use_scope` is the unchanged requested scope;
- `asset_record_reference` is the exact retrieved `asset_record_id`;
- `usage_rights_record_reference` is the exact resolved
  `rights_record_id`;
- `decision_context_reference` is the unchanged context reference.

No field may be omitted, replaced, inferred, normalized, or populated from a
different record.

## Returned value

The operation returns the single immutable
`GovernedAssetUseEligibilityDecision` instance it constructs.

The operation does not return:

- a mutable result wrapper;
- a list of candidate decisions;
- a ranked result;
- a filtered record set;
- a persisted decision identifier;
- a legal conclusion;
- a user-interface response;
- an automatically executed asset use.

The governed result remains available through the decision model's exact
`decision_value`, which is either `ELIGIBLE` or `INELIGIBLE`.

## Fail-closed behavior

The operation must fail closed for:

- a non-registry `registry` input;
- an empty or non-ASCII `asset_record_id`;
- an empty or non-ASCII `requested_use_scope`;
- an empty or non-ASCII `decision_context_reference`;
- registry `NOT_FOUND`;
- unresolved or mismatched usage-rights references;
- an invalid asset or rights record encountered through a contradictory
  registry state;
- any rejected `GovernedAssetUseEligibilityDecision` construction;
- attempted normalization, fuzzy matching, semantic matching, or substitution;
- attempted mutation of the registry or retained records.

The operation must not convert an integration failure into `ELIGIBLE`.

It must not create a synthetic `INELIGIBLE` decision when the governed
decision object cannot be validly constructed.

Construction failure and a valid decision whose `decision_value` is
`INELIGIBLE` are distinct outcomes.

## Immutability boundary

The registry, retrieved asset record, resolved rights record, and returned
decision remain immutable.

The operation must not maintain hidden mutable state, a cache, a session, an
index, or a decision history.

Repeated evaluation with the same immutable inputs must produce an equivalent
decision without changing any input.

## Ordering boundary

Registry collection ordering must not affect:

- exact asset retrieval;
- exact rights resolution;
- decision input values;
- the final `decision_value`.

The operation does not define sorting, ranking, pagination, or presentation
order.

## Version and lifecycle boundary

The operation evaluates the exact asset record selected by exact
`asset_record_id`.

It does not:

- find another record with the same `version_identity`;
- select the newest record;
- select the first `ACTIVE` record;
- follow supersession links;
- rewrite lifecycle state;
- automatically migrate an asset reference.

The decision model remains responsible for its exact lifecycle checks.

## Rights-state boundary

The operation does not alter or reinterpret:

- `validity_state`;
- `use_authorization`;
- `permitted_use_scope`;
- `restriction_scope`.

It does not treat registration as authorization.

It does not treat exact resolution as eligibility.

The decision model remains the sole bounded evaluator of those governed
fields.

## Generated assets

Generated or transformed assets use the same exact operation.

Generation does not permit:

- implicit registration;
- inferred rights;
- automatic eligibility;
- a substituted source asset;
- an AI-generated legal conclusion;
- a bypass of Official Source or provenance governance.

Local AI Generator Integration remains optional and deferred post-v1. It is
not required by this contract.

## Explicit non-goals

This contract does not authorize:

- the evaluation runtime source file;
- the targeted test file;
- any source-code mutation;
- test execution;
- stage, commit, or push;
- persistence or serialization;
- a database or schema;
- filesystem storage;
- search or semantic search;
- filtering, ranking, or pagination;
- batch evaluation;
- importers, crawlers, or folder scans;
- update, delete, or merge operations;
- dashboards or user interfaces;
- real-asset execution;
- automated legal interpretation;
- OCR;
- embeddings or vector databases;
- AI connectors;
- Local AI Generator Integration implementation;
- Gate 16, Gate 17, or Gate 18 implementation.

## Smallest continuation boundary

After independent acceptance and publication of this contract, a later
read-only review may determine whether one deterministic registry-backed
evaluation function and one targeted test are the next smallest Gate 15
dependency.

That later review must separately authorize source code, tests, test
execution, stage, commit, push, or any other mutation.

Persistence, database behavior, search, filtering, importing, user-interface
behavior, real-asset execution, and whole Gate 15 implementation remain
unauthorized.
