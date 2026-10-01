# PR-138C — Post-v1 Minimum Governed Generated-Candidate Decision Action Authorization Contract

## Status

Post-v1 bounded contract. This contract defines the smallest governed authorization-evidence boundary immediately downstream of `GeneratedCandidateDecision`.

This contract does **not** execute any downstream action.

## 1. Purpose

The purpose of this boundary is to bind one exact immutable `GeneratedCandidateDecision` to one explicit caller-supplied downstream action authorization decision.

The resulting record is authorization evidence only.

The boundary exists because PR-137C requires any action downstream of a generated-candidate decision to have a separate governed boundary and separate authorization. A generated-candidate decision alone MUST NOT execute or implicitly authorize a downstream action.

## 2. Required input

The authorization constructor MUST receive exactly one valid immutable `GeneratedCandidateDecision`.

It MUST also receive explicit caller-supplied values for:

- `requested_action`
- `authorization_outcome`
- `authorization_reason_evidence_reference`
- `authorization_actor_reference`
- `authorization_timestamp`

No value in the input `GeneratedCandidateDecision` may silently or automatically determine any of these caller-supplied authorization values.

## 3. Requested action vocabulary

`requested_action` MUST be exactly one of:

- `ASSET_ADMISSION`
- `RETRY_REGENERATION`
- `WORKFLOW_TRANSITION`
- `AUTONOMOUS_ITERATION`

The requested action identifies only the class of downstream action being considered.

It does not execute that action and does not select a provider, model, asset, workflow destination, retry plan, or iteration plan.

## 4. Authorization outcome vocabulary

`authorization_outcome` MUST be exactly one of:

- `AUTHORIZED`
- `DENIED`
- `DEFERRED`

The outcome MUST be supplied explicitly by the caller.

There is no implicit mapping from `GeneratedCandidateDecision.decision_outcome` to `authorization_outcome`.

In particular:

- `ACCEPTED` MUST NOT silently become authorization for `ASSET_ADMISSION` or any other action.
- `REJECTED` MUST NOT silently become authorization for `RETRY_REGENERATION`, provider fallback, or autonomous iteration.
- `DEFERRED` MUST NOT silently become authorization for human review, workflow transition, retry, provider execution, or any other action.

## 5. Meaning of authorization outcomes

`AUTHORIZED` means only that an immutable governed authorization record exists for the exact `requested_action` bound to the exact input decision.

`AUTHORIZED` does **not** execute the requested action.

`DENIED` means only that the exact requested action is not authorized by this authorization record.

`DENIED` does not mutate the candidate or decision and does not trigger any alternate action.

`DEFERRED` means only that authorization for the exact requested action is deferred.

`DEFERRED` does not trigger review, escalation, retry, provider execution, workflow transition, persistence, or any other action.

## 6. Required identity binding

A governed decision-action authorization record MUST preserve and bind:

- deterministic authorization identity
- exact `decision_id`
- exact `evaluation_id`
- exact `candidate_id`
- exact `candidate_checksum`
- exact workflow request reference
- exact project context reference
- exact campaign context reference
- exact creative brief reference
- exact instruction reference
- exact artifact type
- exact generated-candidate decision outcome
- exact `requested_action`
- exact `authorization_outcome`
- nonempty ASCII `authorization_reason_evidence_reference`
- nonempty ASCII `authorization_actor_reference`
- timezone-aware `authorization_timestamp`
- deterministic provenance sufficient to bind the authorization record to the exact upstream decision

The authorization identity MUST be deterministic over the immutable governed identity inputs above.

The identity MUST NOT depend on mutable filesystem paths, transient URLs, data URIs, secrets, implicit current time, randomness, generated UUIDs, diagnostics, repository location, or process-local state.

## 7. Immutability and validation

The authorization record MUST be immutable after construction.

The constructor MUST fail closed for invalid or unsupported input.

At minimum it MUST reject:

- an object that is not exactly the expected `GeneratedCandidateDecision` type
- unsupported `requested_action`
- unsupported `authorization_outcome`
- empty, non-ASCII, or surrounding-whitespace reason/evidence reference
- empty, non-ASCII, or surrounding-whitespace actor reference
- a timestamp without timezone information
- malformed deterministic provenance
- missing required lineage or identity data

## 8. No action execution

This contract authorizes no action execution.

Creating an `AUTHORIZED` record MUST NOT itself:

- admit or approve an asset
- create or mutate a governed asset
- mutate candidate authority state
- set accepted/approved asset claims
- execute retry or regeneration
- select or invoke a provider or model
- perform provider fallback
- perform autonomous iteration
- transition workflow state
- choose a workflow destination
- persist a decision or authorization record
- publish content
- initiate human pilot activity

Execution of any authorized action requires a separate downstream governed execution boundary that explicitly consumes and validates the relevant authorization evidence.

## 9. No hidden policy or routing

This contract MUST NOT introduce hidden decision policy, ranking, provider routing, retry policy, workflow policy, asset-admission policy, or autonomous-iteration policy.

The existence of generic asset-admission and workflow-transition mechanisms elsewhere in the repository does not make them authorized consumers of this record by implication.

Any consumer of this authorization record must be introduced through a separately governed exact boundary.

## 10. Deterministic provenance

Deterministic provenance MUST include, at minimum, stable bindings sufficient to identify:

- the exact candidate
- the exact evaluation
- the exact generated-candidate decision
- the exact requested action
- the exact authorization record

The provenance representation MUST be deterministic, immutable, nonempty, and free of duplicate entries.

## 11. Scope exclusions

This contract does not authorize:

- implementation outside the exact future implementation boundary
- action execution
- asset admission or approval
- retry or regeneration
- provider/model selection or invocation
- fallback
- autonomous iteration
- workflow transition
- persistence
- paid-provider routing
- human pilot activity
- Git staging, commit, or push

## 12. Governed sequence

The bounded sequence is:

`CreativeResultCandidate`
→ `GeneratedCandidateEvaluation` evidence
→ `GeneratedCandidateDecision`
→ governed decision-action authorization evidence
→ future separately governed action execution boundary

This contract closes only the authorization-evidence gap.

It does not close any downstream action-execution gap.
