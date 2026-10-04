# PR-141F -- Post-v1 Minimum Governed Generated-Candidate Autonomous-Iteration Action Execution Contract

## Status

Post-v1 bounded contract.

This contract defines the smallest governed execution boundary for one exact generated-candidate decision-action authorization whose requested action is `AUTONOMOUS_ITERATION`.

It closes only the authorization-to-autonomous-iteration-execution gap selected by PR-141E.

This contract does not authorize an unbounded loop, hidden policy selection, provider/model execution, candidate ingestion, candidate evaluation, candidate decision, downstream action authorization, asset admission, workflow transition, persistence, publication, or human-pilot activity.

## 1. Evidence basis

The published baseline already contains:

- `GeneratedCandidateDecisionActionAuthorization` with exact requested-action vocabulary:
  - `ASSET_ADMISSION`;
  - `RETRY_REGENERATION`;
  - `WORKFLOW_TRANSITION`;
  - `AUTONOMOUS_ITERATION`;
- an asset-admission action execution consumer;
- a workflow-transition action execution consumer;
- a retry-regeneration action execution consumer;
- no external action-execution consumer for `AUTONOMOUS_ITERATION`.

PR-141E therefore selected `AUTONOMOUS_ITERATION` as the only remaining generated-candidate authorization action with zero external execution consumer.

## 2. Purpose

The purpose of this boundary is to consume one exact immutable `GeneratedCandidateDecisionActionAuthorization` for `AUTONOMOUS_ITERATION` and materialize one immutable, deterministic, bounded autonomous-iteration execution record.

The execution record represents permission consumed for exactly one iteration advance.

It MUST NOT by itself execute a provider request or any downstream action-specific executor.

It MUST NOT recursively authorize or execute another autonomous iteration.

## 3. Required authorization input

The execution boundary MUST receive exactly one valid immutable `GeneratedCandidateDecisionActionAuthorization`.

It MUST fail closed unless all of the following are true:

- the object is exactly the expected authorization type;
- `requested_action == "AUTONOMOUS_ITERATION"`;
- `authorization_outcome == "AUTHORIZED"`;
- `authorization_id` remains the exact valid lowercase SHA-256 identity;
- `decision_id`, `evaluation_id`, `candidate_id`, and `candidate_checksum` remain present and valid under the existing authorization model;
- workflow, project, campaign, creative-brief, and instruction references remain present;
- deterministic authorization provenance exactly matches the existing authorization provenance contract;
- the authorization remains bound to the exact upstream generated-candidate decision lineage.

`DENIED` or `DEFERRED` authorization MUST NOT produce autonomous-iteration execution evidence.

## 4. Explicit bounded iteration inputs

The caller MUST explicitly supply all iteration-control inputs.

The first implementation slice MUST require:

- `iteration_plan_reference`: one explicit immutable ASCII reference identifying the governed plan or policy input for this iteration advance;
- `current_iteration_index`: an exact non-negative integer representing the iteration being consumed;
- `maximum_iteration_count`: an exact positive integer representing the hard upper bound for the current bounded iteration plan;
- `next_step_reference`: one explicit immutable ASCII reference identifying the separately governed next-step instruction, request, plan, or handoff to be consumed by a later boundary;
- `execution_actor_reference`: one explicit immutable ASCII actor/service reference;
- `execution_timestamp`: one timezone-aware explicit timestamp.

The execution MUST fail closed when:

- `current_iteration_index < 0`;
- `maximum_iteration_count <= 0`;
- `current_iteration_index >= maximum_iteration_count`;
- any required reference is missing, blank, non-ASCII, mutable, secret-bearing, or malformed;
- the execution timestamp is naive.

The boundary MUST NOT invent, increment, decrement, or otherwise infer any iteration-control value.

## 5. No implicit next-step selection

The boundary MUST NOT infer `next_step_reference` from:

- candidate decision outcome;
- evaluation result;
- authorization outcome;
- retry-regeneration result;
- workflow state;
- provider diagnostics;
- previous generated output;
- asset-admission result;
- hidden ranking or policy;
- current or maximum iteration count.

A rejected candidate MUST NOT implicitly mean retry/regeneration.

An accepted candidate MUST NOT implicitly mean asset admission or workflow transition.

The next step remains explicit caller-supplied governed input.

## 6. Relationship to existing action executors

Existing action executors remain authoritative for their own action types.

This boundary MUST NOT bypass or weaken:

- `execute_generated_candidate_asset_admission`;
- `execute_generated_candidate_workflow_transition_action`;
- `execute_generated_candidate_retry_regeneration_action`.

An `AUTONOMOUS_ITERATION` authorization MUST NOT be passed to those action-specific executors as if it were an authorization for another requested action.

The autonomous-iteration execution record MUST NOT be treated as a replacement for a separate action-specific authorization.

Any later asset admission, workflow transition, retry regeneration, provider request, or candidate ingestion requires its own applicable governed boundary and required authorization evidence.

## 7. One authorization consumption equals one iteration advance

One `AUTONOMOUS_ITERATION` authorization consumption under this boundary permits exactly one bounded iteration-advance record.

The implementation MUST NOT:

- emit more than one autonomous-iteration execution record from one invocation;
- loop over multiple iteration indices;
- recursively call itself;
- schedule itself;
- automatically invoke a second iteration;
- automatically request or construct a new authorization;
- automatically invoke a provider;
- automatically invoke retry-regeneration;
- automatically invoke workflow transition;
- automatically invoke asset admission.

A later iteration advance requires new separately governed authorization evidence.

## 8. Required lineage preservation

The autonomous-iteration execution record MUST preserve at minimum:

- exact `authorization_id`;
- exact `decision_id`;
- exact `evaluation_id`;
- exact `candidate_id`;
- exact `candidate_checksum`;
- exact workflow request reference;
- exact project context reference;
- exact campaign context reference;
- exact creative brief reference;
- exact instruction reference;
- exact generated-candidate decision outcome;
- exact requested action `AUTONOMOUS_ITERATION`;
- exact authorization outcome `AUTHORIZED`;
- exact `iteration_plan_reference`;
- exact `current_iteration_index`;
- exact `maximum_iteration_count`;
- exact `next_step_reference`;
- exact execution actor/reference;
- exact execution timestamp;
- deterministic execution identity;
- deterministic provenance.

The original candidate, evaluation, decision, and authorization remain immutable inputs.

## 9. Deterministic execution identity

The execution record MUST have one deterministic lowercase SHA-256 identity.

For identical exact:

- authorization lineage;
- iteration plan reference;
- current iteration index;
- maximum iteration count;
- next-step reference;
- execution actor/reference;
- execution timestamp;

the execution identity and deterministic provenance MUST be identical.

The identity MUST NOT depend on:

- randomness;
- UUID generation;
- implicit current time;
- process-local identity;
- repository path;
- mutable filesystem location;
- hidden provider/model choice;
- credentials or secrets.

This determinism requirement applies to the execution evidence only.

It does not claim deterministic provider output or deterministic behavior of any later separately governed step.

## 10. Deterministic provenance

The execution record MUST include deterministic provenance that binds the exact authorization lineage to the exact bounded iteration advance.

At minimum the provenance MUST bind:

- `authorization_sha256`;
- `decision_id`;
- `candidate_sha256`;
- `requested_action:AUTONOMOUS_ITERATION`;
- a deterministic fingerprint of the exact iteration-control projection;
- the autonomous-iteration action execution SHA-256 identity.

The deterministic iteration-control fingerprint MUST cover:

- iteration plan reference;
- current iteration index;
- maximum iteration count;
- next-step reference.

No secret material may enter provenance.

## 11. Immutable reference and secret safety

The first implementation slice MUST reject iteration-plan and next-step references that:

- are empty;
- contain surrounding whitespace;
- contain non-ASCII text;
- use obviously mutable prefixes such as `memory:`, `mutable:`, `object:`, `session:`, or `temp:`;
- contain common secret markers such as `api_key`, `authorization:`, `credential`, `password`, `private_key`, `secret`, `session_token`, or `access_token`.

The implementation MUST NOT persist credentials, tokens, provider authorization material, or raw secrets.

## 12. No provider/model execution

This boundary MUST NOT invoke:

- `ConcreteVisualGenerationExecutionAdapter`;
- a provider transport;
- Cloudflare Workers AI;
- OpenAI Images;
- any other model/provider runtime.

It MUST NOT select, rank, fallback, or optimize providers or models.

Provider/model execution remains outside this first autonomous-iteration action execution slice.

## 13. No candidate or workflow mutation

This boundary MUST NOT:

- create a new `CreativeResultCandidate`;
- evaluate a candidate;
- decide a candidate;
- authorize a downstream candidate action;
- admit an asset;
- mutate workflow state;
- create a workflow transition evaluation;
- claim an accepted asset;
- claim production release;
- overwrite or supersede the original candidate lineage.

The output is iteration execution evidence only.

## 14. No persistence or external side effects

The first implementation slice MUST be side-effect-free other than returning the immutable in-memory execution record.

It MUST NOT:

- persist execution evidence;
- mutate registries;
- mutate databases;
- write workflow state;
- stage, commit, or publish repository content;
- invoke external network/provider operations;
- initiate human review;
- initiate a human pilot.

Persistence or orchestration requires a separately governed boundary.

## 15. Failure semantics

Malformed authorization, wrong requested action, non-`AUTHORIZED` outcome, provenance mismatch, invalid iteration control, exhausted iteration bound, malformed immutable reference, secret-bearing reference, invalid actor/reference, or naive timestamp MUST fail closed.

Failure MUST NOT:

- fabricate execution evidence;
- increment the iteration index;
- select a next step;
- invoke another action executor;
- invoke a provider;
- schedule another iteration;
- create downstream authorization;
- mutate workflow or candidate state.

## 16. Scope exclusions

This contract does not authorize or implement:

- autonomous loop orchestration;
- provider/model execution;
- provider/model auto-selection;
- provider fallback;
- retry-regeneration execution;
- workflow-transition execution;
- asset-admission execution;
- candidate ingestion;
- candidate evaluation;
- candidate decision;
- downstream action authorization;
- persistence;
- publication/release;
- human pilot.

These remain separate boundaries.

## 17. Minimum implementation boundary implied by this contract

A future implementation boundary, if separately accepted, SHOULD be limited to:

- one immutable domain result type for generated-candidate autonomous-iteration action execution;
- one application function consuming exact `GeneratedCandidateDecisionActionAuthorization`;
- explicit caller-supplied bounded iteration inputs;
- deterministic identity and provenance helpers;
- one focused domain test file;
- one focused application test file.

The first implementation SHOULD NOT require modification of the existing authorization domain/application, existing asset-admission executor, existing workflow-transition executor, existing retry-regeneration executor, provider boundary, generation adapter, candidate bridge, or existing tests.

No real provider request, no retry execution, no workflow transition, no asset admission, no candidate ingestion, no persistence, and no human-pilot activity are authorized by materializing this contract.
