# PR-140V -- Post-v1 Minimum Governed Generated-Candidate Retry-Regeneration Action Execution Contract

## Status

Post-v1 bounded contract.

This contract defines the smallest governed execution boundary for one exact generated-candidate decision-action authorization whose requested action is `RETRY_REGENERATION`.

It closes only the authorization-to-single-retry-execution gap selected by PR-140U.

This contract does not authorize autonomous iteration, provider fallback, candidate admission, workflow-state mutation, asset admission, persistence, publication, or human-pilot activity.

## 1. Evidence basis

The published baseline already contains:

- `GeneratedCandidateDecisionActionAuthorization` with exact requested-action vocabulary including `RETRY_REGENERATION`;
- `ConcreteVisualGenerationExecutionAdapter` for one explicitly configured provider/model invocation;
- `VisualGenerationRequest` and `VisualGenerationResult`;
- generated-output-to-`CreativeResultCandidate` bridge machinery;
- governed candidate evaluation, decision, authorization, asset-admission execution, and workflow-transition action execution;
- no external source consumer of `RETRY_REGENERATION` authorization;
- no external source consumer of `AUTONOMOUS_ITERATION` authorization.

PR-140U therefore selected `RETRY_REGENERATION` as the smallest adjacent authorization-to-execution gap before autonomous iteration.

## 2. Purpose

The purpose of this boundary is to consume one exact immutable `GeneratedCandidateDecisionActionAuthorization` for `RETRY_REGENERATION`, bind it to one explicit caller-supplied retry generation request and one explicit provider/model execution configuration, invoke the existing concrete visual-generation execution machinery at most once, and return immutable execution evidence.

An authorization record alone MUST NOT execute a retry.

A rejected generated candidate alone MUST NOT implicitly trigger retry/regeneration.

A retry execution MUST NOT create an autonomous loop.

## 3. Required authorization input

The execution boundary MUST receive exactly one valid immutable `GeneratedCandidateDecisionActionAuthorization`.

It MUST fail closed unless all of the following are true:

- the object is exactly the expected authorization type;
- `requested_action == "RETRY_REGENERATION"`;
- `authorization_outcome == "AUTHORIZED"`;
- `authorization_id` is a valid exact lowercase SHA-256 identity;
- `decision_id`, `evaluation_id`, `candidate_id`, and `candidate_checksum` remain present and valid under the existing authorization model;
- workflow, project, campaign, creative-brief, and instruction references remain present;
- deterministic authorization provenance is present, nonempty, and exactly consistent with the authorization record;
- the authorization remains bound to the exact upstream generated-candidate decision lineage.

`DENIED` or `DEFERRED` authorization MUST NOT execute regeneration through this boundary.

## 4. Explicit retry-generation request

The caller MUST supply one exact valid `VisualGenerationRequest` for the retry attempt.

The retry request MUST be explicit. It MUST NOT be inferred from:

- `decision_outcome`;
- `authorization_outcome`;
- candidate evaluation outcome;
- provider diagnostics;
- previous provider output references;
- workflow state;
- asset-admission result;
- prior retry history;
- autonomous-iteration policy.

The caller remains responsible for supplying the governed grounded prompt and selected governed reference asset IDs appropriate for the retry attempt.

This boundary MUST NOT silently rewrite the grounded prompt, add or remove reference asset IDs, or synthesize a new retry request.

## 5. Explicit provider/model execution configuration

The caller MUST supply one exact explicit `VisualGenerationExecutionConfig`.

Provider identity and model identity MUST remain explicit.

This boundary MUST NOT:

- select a provider or model using hidden policy;
- rank providers or models;
- perform provider fallback;
- switch provider or model after failure;
- widen provider credentials or permissions;
- fabricate configuration values.

The first execution slice is limited to exactly one configured provider/model attempt.

## 6. Existing concrete visual-generation machinery remains authoritative

The implementation MUST use the existing `ConcreteVisualGenerationExecutionAdapter` and the existing `VisualGenerationRequest` contract.

It MUST NOT create a parallel provider request model or bypass the adapter's governed reference-resolution checks.

For one retry-regeneration execution request, the adapter's `generate` operation MAY be invoked at most once.

Reference resolution MUST preserve exact requested governed asset identity and use eligibility under the existing adapter contract.

Transport/provider failure MUST fail closed. A failed provider attempt MUST NOT be converted into fabricated success, fabricated output references, or automatic fallback.

## 7. Required authorization and request lineage binding

The retry-regeneration execution evidence MUST preserve and bind at minimum:

- exact `authorization_id`;
- exact `decision_id`;
- exact `evaluation_id`;
- exact original `candidate_id`;
- exact original `candidate_checksum`;
- exact workflow request reference;
- exact project context reference;
- exact campaign context reference;
- exact creative brief reference;
- exact instruction reference;
- exact generated-candidate decision outcome;
- exact requested action `RETRY_REGENERATION`;
- exact authorization outcome `AUTHORIZED`;
- exact retry-generation grounded prompt or a canonical deterministic fingerprint of that exact prompt;
- exact ordered selected reference asset IDs;
- exact explicit provider identity;
- exact explicit model identity;
- exact provider-local output references returned by the existing adapter;
- non-secret provider-local audit metadata returned by the existing adapter;
- execution actor/reference;
- timezone-aware execution timestamp;
- deterministic execution-evidence identity;
- deterministic provenance.

The execution-evidence identity MUST be deterministic over the exact immutable authorization lineage, explicit retry request, explicit provider/model configuration, exact returned provider-local result metadata, execution actor/reference, and explicit execution timestamp.

This determinism requirement applies to evidence identity for identical exact evidence. It does NOT claim that an external generative model will produce identical outputs for identical inputs.

## 8. Provider output authority

Provider output returned by this boundary remains provider-local and non-governed.

Successful retry execution MUST NOT itself:

- create a `CreativeResultCandidate`;
- claim candidate authority;
- evaluate or decide the generated output;
- authorize any downstream action;
- admit or approve an asset;
- transition workflow state;
- persist generated output.

Existing generated-output-to-candidate bridge machinery remains a separate downstream boundary.

Invocation of that bridge is outside this contract.

## 9. Original candidate immutability

The original candidate, evaluation, decision, and authorization are immutable inputs.

Retry-regeneration execution MUST NOT mutate, replace, delete, supersede, or relabel any of them.

A successful retry attempt does not retroactively change the original candidate decision.

Any future candidate created from retry output requires its own candidate identity and normal downstream governed evaluation/decision/authorization lineage.

## 10. Single-attempt semantics

One authorization consumption under this boundary permits at most one retry-regeneration provider invocation.

It MUST NOT:

- loop until success;
- recursively retry;
- schedule another retry;
- invoke a second provider/model;
- perform autonomous iteration;
- create a new authorization;
- infer whether another retry should occur.

A further retry attempt requires separately governed authorization evidence.

## 11. Secrets and diagnostics

Credentials and secrets MUST enter only through the existing injected runtime/transport mechanism.

This boundary MUST NOT write credentials, authorization headers, tokens, secrets, or raw private provider material into:

- deterministic provenance;
- execution identity input;
- execution evidence;
- diagnostics;
- reports;
- committed source or test fixtures.

Only non-secret provider-local audit metadata may be preserved.

## 12. Failure semantics

The boundary MUST fail closed before provider invocation for malformed authorization, wrong requested action, non-`AUTHORIZED` outcome, inconsistent authorization provenance, invalid retry request, invalid explicit execution configuration, or invalid execution metadata.

Reference-resolution failure, transport failure, provider rejection, malformed provider response, or unsupported output MUST remain failure.

Failure MUST NOT trigger provider fallback, automatic retry, autonomous iteration, candidate admission, workflow transition, or asset admission.

## 13. Determinism and immutability

The retry-regeneration action execution record MUST be immutable after construction.

For identical exact authorization lineage, retry request, explicit provider/model configuration, returned provider-local result metadata, execution actor/reference, and execution timestamp, deterministic execution identity and deterministic provenance MUST be identical.

No deterministic identity may depend on repository location, process-local identity, randomness, generated UUIDs, implicit current time, hidden provider selection, secrets, or mutable filesystem paths.

## 14. Prohibited side effects

Except for the one explicitly authorized provider/model invocation through the existing adapter, this boundary MUST NOT itself:

- mutate workflow state;
- mutate an asset registry;
- mutate candidate/evaluation/decision/authorization state;
- admit or approve an asset;
- create a governed candidate;
- execute provider fallback;
- execute a second retry;
- perform autonomous iteration;
- publish content;
- mutate external storage unrelated to the single provider invocation;
- persist execution evidence;
- initiate human review or human-pilot activity.

## 15. Scope exclusions

This contract does not authorize or implement:

- autonomous iteration orchestration;
- provider/model auto-selection;
- multi-provider routing;
- provider fallback;
- retry loops or retry scheduling;
- generated-output candidate ingestion;
- generated-candidate evaluation;
- generated-candidate decision;
- downstream action authorization;
- asset admission;
- workflow transition;
- durable persistence;
- publication or release;
- human pilot.

Each excluded behavior requires its own separately governed boundary if pursued later.

## 16. Minimum implementation boundary implied by this contract

A future implementation boundary, if separately approved, SHOULD be limited to:

- one immutable domain result type for generated-candidate retry-regeneration action execution;
- one application function that consumes exact `GeneratedCandidateDecisionActionAuthorization`;
- one exact caller-supplied `VisualGenerationRequest`;
- one exact explicit `VisualGenerationExecutionConfig`;
- injected existing reference-resolution and transport dependencies;
- at most one invocation of existing `ConcreteVisualGenerationExecutionAdapter.generate`;
- deterministic, non-secret execution evidence;
- focused domain and application tests using fakes/stubs only.

No real provider proof, candidate ingestion, evaluation, decision, downstream authorization, asset admission, workflow transition, autonomous iteration, persistence, publication, or human-pilot activity is authorized by materializing this contract.
