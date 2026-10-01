# PR-139C — Post-v1 Minimum Governed Authorized Generated-Candidate Asset-Admission Execution Contract

## Status

Proposed exact contract for the smallest governed downstream action-execution boundary selected by PR-139B.

This contract defines one bounded execution step for `ASSET_ADMISSION` after an exact
`GeneratedCandidateDecisionActionAuthorization` record has already been created.

It does not define retry/regeneration, workflow-transition execution, autonomous iteration,
provider/model invocation, persistence, publication, or a human pilot.

## 1. Purpose

The purpose of this boundary is to close only the smallest gap between:

1. an exact immutable generated-candidate decision;
2. an exact immutable decision-action authorization whose `requested_action` is
   `ASSET_ADMISSION` and whose `authorization_outcome` is `AUTHORIZED`; and
3. one immutable governed asset-admission execution record for the exact generated candidate.

The successful immutable execution record is the governed execution effect of this boundary.
No hidden mutable state change is required or permitted.

## 2. Required upstream evidence

The execution constructor must consume, directly and explicitly:

- exactly one immutable `GeneratedCandidateDecisionActionAuthorization`;
- exactly one immutable generated `CreativeResultCandidate` that is the candidate bound by the
  authorization lineage;
- one explicit caller-supplied governed asset reference identifying the admitted asset identity;
- one explicit caller-supplied execution actor reference; and
- one explicit caller-supplied timezone-aware execution timestamp.

The constructor must not obtain any required value from mutable global state, repository state,
environment variables, current time, random values, UUID generation, network responses, provider
responses, UI state, or hidden defaults.

## 3. Exact authorization preconditions

Execution must fail closed unless all of the following are true:

1. the supplied authorization is exactly a
   `GeneratedCandidateDecisionActionAuthorization`;
2. `requested_action == "ASSET_ADMISSION"`;
3. `authorization_outcome == "AUTHORIZED"`;
4. the authorization lineage binds the exact supplied candidate identity and candidate-content
   checksum;
5. the authorization lineage binds an exact generated-candidate decision;
6. the bound decision outcome is `ACCEPTED`; and
7. the supplied candidate remains a generated candidate and does not already claim accepted or
   approved asset authority.

`ACCEPTED` alone does not authorize admission. `AUTHORIZED` alone does not bypass candidate,
decision, or lineage validation. Both the accepted decision evidence and the exact authorized
`ASSET_ADMISSION` evidence are required.

## 4. Explicit execution inputs

The execution boundary must require the caller to provide all execution-specific inputs
explicitly:

- `admitted_asset_reference`;
- `execution_actor_reference`; and
- `execution_timestamp`.

The boundary must not select an asset destination, storage location, workflow state, provider,
model, retry policy, iteration policy, publication target, or persistence mechanism.

The execution timestamp must be timezone-aware.

All caller-supplied reference values must satisfy the same strict non-empty, deterministic,
serializable reference discipline used by adjacent governed boundaries.

## 5. Immutable execution result

A successful call must return one immutable
`GeneratedCandidateAssetAdmissionExecution` record.

The record must bind, at minimum:

- deterministic `asset_admission_execution_id`;
- exact authorization identity;
- exact generated-candidate decision identity;
- exact generated-candidate evaluation identity;
- exact generated candidate identity;
- exact candidate-content checksum;
- exact admitted asset reference;
- exact execution actor reference;
- exact execution timestamp;
- execution outcome `ADMITTED`; and
- deterministic provenance sufficient to reconstruct the binding above.

The execution identity must be derived deterministically from canonical serializable content.

The identity must not include:

- local filesystem paths;
- URLs or data URIs;
- secrets or credentials;
- implicit current time;
- random values or UUIDs;
- diagnostics;
- process state;
- repository location; or
- mutable storage identifiers not explicitly supplied as governed references.

## 6. Meaning of `ADMITTED`

Within this boundary, `ADMITTED` means:

- the exact candidate passed all execution preconditions;
- the exact authorization explicitly authorized `ASSET_ADMISSION`;
- the exact admitted asset reference was explicitly supplied;
- the immutable execution record was successfully constructed; and
- downstream consumers may use this execution record as the exact governed evidence that the
  candidate was admitted as the referenced asset.

`ADMITTED` does not mean:

- persisted to a database or object store;
- published or distributed;
- approved for every future use;
- selected for a campaign;
- moved to a workflow state;
- retried or regenerated;
- used to invoke a provider/model;
- admitted into an unrelated asset registry;
- granted new usage rights beyond separately governed rights evidence; or
- accepted by a human pilot.

## 7. No implicit side effects

Construction of `GeneratedCandidateAssetAdmissionExecution` must not:

- mutate the supplied candidate;
- mutate the supplied authorization, decision, or evaluation;
- mutate a generic governed asset registry;
- write to a database, filesystem asset store, or remote service;
- create or modify workflow state;
- set `asset_admission_execution_requested` in another object;
- invoke `evaluate_governed_creative_workflow_transition`;
- select or invoke any visual-generation provider or model;
- perform retry, fallback, or regeneration;
- begin or continue autonomous iteration;
- stage, commit, or push Git state;
- read credentials; or
- initiate a human pilot.

## 8. Relationship to existing workflow support

Existing repository concepts such as `ASSET_ADMISSION_PENDING`,
`accepted_governed_asset_reference`, and `asset_admission_execution_requested` are adjacent
workflow mechanisms only.

This contract does not silently connect itself to those mechanisms.

A future separately governed boundary may consume the exact
`GeneratedCandidateAssetAdmissionExecution` record and explicitly integrate it with an allowed
workflow transition. That future boundary must define and authorize its own exact behavior.

## 9. Determinism and fail-closed behavior

For identical validated inputs, the execution result and deterministic identity must be
identical.

Any missing, malformed, inconsistent, unauthorized, mismatched, or non-timezone-aware required
input must fail closed before an `ADMITTED` execution record is returned.

No fallback result is permitted.

## 10. Scope exclusions

This contract does not authorize implementation beyond this exact boundary and does not authorize:

- retry/regeneration execution;
- workflow-transition execution;
- autonomous-iteration execution;
- provider/model selection or invocation;
- credential access;
- network access;
- hidden routing;
- persistence;
- publication;
- asset-store mutation;
- generic asset-registry mutation;
- workflow mutation;
- human-pilot execution; or
- any unrelated product or creative capability.

## 11. Governed sequence after this contract

The bounded sequence is:

`CreativeResultCandidate`
→ generated-candidate evaluation evidence
→ generated-candidate decision
→ decision-action authorization evidence
→ governed generated-candidate asset-admission execution record
→ future separately governed consumer/workflow boundary.

This contract closes only the minimum governed authorized generated-candidate
`ASSET_ADMISSION` execution-record gap.
