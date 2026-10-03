# PR-140L — Post-v1 Minimum Governed Generated-Candidate Workflow-Transition Action Execution Contract

## Status

Post-v1 bounded contract.

This contract defines the smallest governed execution-evidence boundary for one exact generated-candidate decision-action authorization whose requested action is `WORKFLOW_TRANSITION`.

It closes only the authorization-to-workflow-transition execution gap selected by PR-140K.

This contract does not persist or commit workflow state.

## 1. Purpose

The purpose of this boundary is to consume one exact immutable `GeneratedCandidateDecisionActionAuthorization` for `WORKFLOW_TRANSITION`, bind that authorization to one explicit caller-supplied workflow transition request, invoke the existing governed workflow-transition evaluator at most once, and return immutable deterministic execution evidence.

An authorization record alone MUST NOT execute a transition.

A generated-candidate decision alone MUST NOT execute or imply a transition.

The boundary MUST NOT create a parallel workflow-state model or bypass the existing governed workflow-transition evaluator.

## 2. Required authorization input

The execution boundary MUST receive exactly one valid immutable `GeneratedCandidateDecisionActionAuthorization`.

It MUST fail closed unless all of the following are true:

- the object is exactly the expected authorization type
- `requested_action == "WORKFLOW_TRANSITION"`
- `authorization_outcome == "AUTHORIZED"`
- `authorization_id` is a valid exact lowercase SHA-256 identity
- `decision_id`, `evaluation_id`, `candidate_id`, and `candidate_checksum` are present and valid according to the existing authorization model
- workflow, project, campaign, creative-brief, and instruction references are present
- deterministic authorization provenance is present, nonempty, and exactly consistent with the authorization record
- the authorization remains bound to the exact upstream generated-candidate decision lineage

`DENIED` or `DEFERRED` authorization MUST NOT execute or evaluate a workflow transition through this boundary.

## 3. Explicit transition request

The caller MUST supply an explicit `requested_next_workflow_state`.

The requested target state MUST NOT be inferred from:

- the generated-candidate decision outcome
- `authorization_outcome`
- `requested_action`
- candidate evaluation outcome
- asset-admission evidence
- current workflow state
- accepted governed asset reference
- retry/regeneration vocabulary
- autonomous-iteration vocabulary
- provider/model output
- prior transition result

The caller MUST also supply the exact current governed workflow context required by the existing workflow-transition evaluator.

The existing evaluator remains authoritative for whether the requested transition is valid.

## 4. Existing workflow machinery remains authoritative

The implementation MUST use the existing governed workflow-transition evaluator.

It MUST NOT:

- introduce a second transition table
- silently reinterpret existing workflow states
- synthesize missing workflow references
- bypass existing transition guards
- convert authorization into implicit workflow-state mutation
- treat an evaluator result as persisted or committed state

The evaluator MAY be invoked at most once for one execution request.

If the existing evaluator rejects, safely stops, or otherwise does not authorize the requested transition according to its own result contract, this execution boundary MUST preserve that outcome without overriding it.

## 5. Candidate and authorization lineage binding

The execution result MUST preserve and bind at minimum:

- exact `authorization_id`
- exact `decision_id`
- exact `evaluation_id`
- exact `candidate_id`
- exact `candidate_checksum`
- exact workflow request reference
- exact project context reference
- exact campaign context reference
- exact creative brief reference
- exact instruction reference
- exact generated-candidate decision outcome
- exact requested action `WORKFLOW_TRANSITION`
- exact authorization outcome `AUTHORIZED`
- exact requested next workflow state
- exact existing evaluator result identity or deterministic projection
- execution actor/reference
- timezone-aware execution timestamp
- deterministic execution identity
- deterministic provenance

The execution identity MUST be deterministic over immutable governed inputs.

It MUST NOT depend on randomness, generated UUIDs, implicit current time, mutable filesystem paths, transient URLs, secrets, repository location, diagnostics, or process-local state.

## 6. Asset-reference handling

This boundary MUST NOT invent, admit, or select an asset reference.

If the requested workflow transition requires an existing governed asset reference under the existing evaluator contract, the caller MUST supply that reference explicitly.

Any supplied governed asset reference MUST already satisfy the existing workflow evaluator's contract.

If an accepted or governed asset reference is already bound in the supplied workflow context, this boundary MUST preserve it exactly.

This contract does not replace PR-139 asset-admission execution or PR-140 asset-admission-execution workflow-transition consumption.

## 7. Execution semantics

A valid execution implementation MAY only:

1. validate the exact authorization and its deterministic provenance
2. validate the explicit caller-supplied workflow transition inputs
3. bind exact authorization lineage into one deterministic execution request
4. invoke the existing pure/deterministic workflow-transition evaluator at most once
5. return one immutable deterministic workflow-transition action execution record

The result is execution evidence that the authorized transition request was evaluated through the governed transition machinery.

The result is not evidence that durable workflow state was persisted or committed.

## 8. Prohibited side effects

This boundary MUST NOT itself:

- persist or mutate workflow state
- mutate a workflow registry
- mutate a candidate
- mutate a decision
- mutate an authorization
- admit or approve an asset
- execute asset admission
- select or invoke a provider or model
- execute retry or regeneration
- perform provider fallback
- perform autonomous iteration
- publish content
- mutate external storage
- perform network provider requests
- read credentials
- create hidden human-review or human-pilot activity

No filesystem, database, registry, queue, external API, or provider side effect is authorized by this contract.

## 9. Authorization does not imply policy

`AUTHORIZED` for `WORKFLOW_TRANSITION` means only that the exact transition action class is authorized for the exact bound generated-candidate decision.

It does not select:

- a workflow destination
- a transition reason
- an asset
- a retry plan
- a provider or model
- an autonomous-iteration plan

All transition-specific inputs remain explicit caller-supplied governed inputs.

## 10. Determinism and immutability

The workflow-transition action execution record MUST be immutable after construction.

For identical exact governed inputs, the deterministic execution identity and deterministic provenance MUST be identical.

The implementation MUST fail closed for malformed types, unsupported authorization state, inconsistent lineage, inconsistent deterministic provenance, naive timestamps, missing explicit transition target, or invalid workflow context.

## 11. Scope exclusions

This contract does not authorize or implement:

- durable workflow-state persistence
- workflow-state repository mutation
- asset registry mutation
- retry/regeneration execution
- provider fallback
- autonomous iteration
- provider/model invocation
- publication
- release
- human pilot

Each excluded behavior requires its own separately governed boundary if pursued later.

## 12. Minimum implementation boundary implied by this contract

A future implementation boundary, if separately approved, SHOULD be limited to:

- one immutable domain result type for generated-candidate workflow-transition action execution
- one application function that consumes exact `GeneratedCandidateDecisionActionAuthorization`
- explicit workflow-transition inputs compatible with the existing evaluator
- one call maximum to the existing governed workflow-transition evaluator
- targeted domain and application tests

No implementation, tests, persistence, provider call, retry/regeneration, autonomous iteration, publication, or human-pilot activity is authorized by materializing this contract.
