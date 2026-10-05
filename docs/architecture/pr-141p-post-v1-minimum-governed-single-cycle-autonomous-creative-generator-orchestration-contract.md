# PR-141P -- Post-v1 Minimum Governed Single-Cycle Autonomous Creative Generator Orchestration Contract

## Status

Post-v1 bounded architecture contract.

This contract defines the smallest governed application-orchestration boundary that can compose the already-published visual generation, generated-output candidate bridge, candidate evaluation, candidate decision, decision-action authorization, and authorized action-execution surfaces into one explicit creative-generation cycle.

It closes only the system-composition gap selected by PR-141O.

It does not authorize a multi-cycle autonomous loop, hidden policy selection, provider/model auto-selection, automated visual judging, persistence, publication/release, or human-pilot activity.

## 1. Evidence basis

The published baseline at PR-141O contains independent component-level surfaces for:

- explicit concrete visual generation through `ConcreteVisualGenerationExecutionAdapter`;
- generated-output to `CreativeResultCandidate` provenance bridging;
- generated-candidate evaluation;
- generated-candidate decision;
- generated-candidate decision-action authorization;
- authorized asset-admission action execution;
- authorized retry-regeneration action execution;
- authorized workflow-transition action execution; and
- authorized autonomous-iteration action execution.

PR-141O also confirmed:

- the governed creative workflow application service remains an assessment-only boundary;
- no existing application module composes the full generation-to-action core;
- no existing orchestration-named autonomous generator surface is present; and
- the smallest selected system gap is one governed single-cycle autonomous creative generator orchestration contract.

## 2. Purpose

A conforming future implementation may coordinate exactly one bounded creative-generation cycle:

1. consume one explicit visual generation request and one explicit provider/model execution configuration;
2. execute one initial provider generation through the accepted concrete visual-generation adapter;
3. materialize exactly one generated output as one `CreativeResultCandidate`;
4. evaluate that exact candidate from explicit governed criterion results;
5. create one decision from the exact evaluation;
6. create one decision-action authorization from the exact decision;
7. when and only when authorization outcome is `AUTHORIZED`, execute at most one exact action-specific executor selected by the explicit requested action; and
8. return one immutable orchestration result that binds the exact lineage of the cycle.

The orchestration boundary coordinates accepted components. It does not replace their authority or validation rules.

## 3. Meaning of autonomous at this boundary

For this first system-composition slice, `autonomous` means that one application invocation may execute the already-governed component chain without requiring a human to manually call each internal application function.

It does not mean the system may invent policy.

The caller must still explicitly supply all values that existing accepted component boundaries require, including evaluation criterion results, decision outcome, requested action, authorization outcome, action-specific control inputs, actors, references, timestamps, provider/model configuration, and transport dependencies.

A later separately governed boundary may automate policy derivation or evaluation. This contract does not.

## 4. Exact cycle input boundary

A future orchestrator must receive explicit inputs sufficient for every component it invokes.

At minimum, the initial generation portion must receive:

- one exact `VisualGenerationRequest`;
- one exact `VisualGenerationExecutionConfig`;
- one explicit `VisualReferenceResolver`;
- one explicit provider `transport`;
- one exact creative-result candidate identity;
- workflow, project, campaign, creative-brief, and instruction references;
- one caller-supplied candidate admission timestamp;
- one admitting actor reference;
- exact generated-output bytes or exact generated-output checksum when required by the candidate bridge.

The evaluation portion must receive:

- one nonempty exact tuple of `GeneratedCandidateCriterionResult`;
- one evaluator actor reference; and
- one timezone-aware evaluation timestamp.

The decision portion must receive:

- one explicit controlled decision outcome;
- one decision-reason evidence reference;
- one decision actor reference; and
- one timezone-aware decision timestamp.

The authorization portion must receive:

- one explicit requested action from the published action vocabulary;
- one explicit authorization outcome;
- one authorization-reason evidence reference;
- one authorization actor reference; and
- one timezone-aware authorization timestamp.

Any action-specific executor inputs must also be explicit.

No missing value may be inferred from ambient clock, filesystem, process state, network discovery, model output labels, prior action type, evaluation aggregate, or hidden policy.

## 5. One initial provider execution

The initial generation step must use the accepted `ConcreteVisualGenerationExecutionAdapter`.

The orchestrator must not:

- auto-select a provider or model;
- fallback to another provider or model;
- retry the initial provider call;
- call the provider directly in parallel with the adapter;
- duplicate the same initial request;
- infer provider credentials or transport configuration;
- persist provider secrets.

Exactly one initial adapter `generate` invocation is permitted per single-cycle orchestration invocation.

A later `RETRY_REGENERATION` action executor may perform its own separately authorized provider attempt. That retry output remains retry-execution evidence and must not be ingested into a second candidate inside the same cycle.

## 6. Provider-response to candidate-bridge compatibility precondition

The published generation adapter returns `VisualGenerationResult`, while the published candidate bridge currently requires an exact `ProviderExecutionResponse`.

This is a real composition seam.

A future orchestration implementation must not fabricate a `ProviderExecutionResponse`, reconstruct one from lossy audit text, or perform a duplicate provider request merely to satisfy the candidate bridge.

Before runtime orchestration is implemented, one separately reviewed compatibility mechanism must be selected, such as:

- an exact non-lossy capture/projection of the single provider transport response already used by the adapter; or
- a narrowly scoped candidate-bridge compatibility change that accepts the exact accepted generation result while preserving provider execution provenance.

The compatibility mechanism must prove that:

- there remains exactly one initial provider request;
- provider output references are unchanged;
- provider/model identity is preserved;
- provider execution reference is preserved when present;
- generated-output checksum binding remains exact;
- no secret material is introduced; and
- candidate authority remains `CANDIDATE`.

This contract does not itself choose or implement that compatibility mechanism.

## 7. Candidate materialization

Exactly one initial generated output may be bridged into exactly one `CreativeResultCandidate`.

The orchestrator must preserve:

- exact workflow request reference;
- exact project and campaign context;
- exact creative brief and instruction references;
- exact provider and model identity;
- exact provider execution evidence;
- exact generated-output reference;
- exact content SHA-256;
- exact admission actor and timestamp;
- deterministic candidate provenance; and
- candidate-only authority state.

The candidate must not claim official-source, accepted-asset, approved-asset, or production-release authority.

## 8. Evaluation boundary

The orchestrator may invoke `evaluate_generated_candidate` only with the exact candidate created in the same cycle and explicit governed criterion results.

Criterion results remain explicit inputs for this first orchestration slice.

The orchestrator must not:

- use the provider/model to judge its own output;
- infer criterion outcomes from provider diagnostics;
- invent missing criterion results;
- convert a missing criterion into `passed`;
- override aggregate outcome derivation; or
- mutate the candidate during evaluation.

Automated visual-quality or policy evaluation is outside this contract.

## 9. Evaluation-to-decision compatibility precondition

The published `GeneratedCandidateEvaluation` currently carries candidate identity and checksum as:

- `creative_result_candidate_id`; and
- `candidate_content_checksum`.

The published `decide_generated_candidate` consumer currently requires evaluation attributes named:

- `candidate_id`; and
- `candidate_checksum`.

This is a second real composition seam.

The orchestration implementation must not use dynamic monkey-patching, mutable shadow attributes, unchecked dictionaries, or silent field-name substitution to bypass this mismatch.

Before runtime orchestration is implemented, a separately reviewed compatibility correction or exact projection boundary must reconcile these names while preserving:

- the exact evaluation type or an explicitly governed compatible type;
- exact candidate identity;
- exact candidate checksum;
- workflow, project, campaign, brief, and instruction lineage;
- evaluation aggregate outcome;
- evaluation deterministic provenance; and
- decision deterministic identity.

This contract does not silently treat the current evaluation and decision surfaces as directly composable.

## 10. Decision boundary

After the evaluation-to-decision compatibility precondition is satisfied, the orchestrator may invoke `decide_generated_candidate` exactly once.

The decision outcome remains explicit caller-supplied governed input for this first slice.

The orchestrator must not automatically map:

- `passed` to `ACCEPTED`;
- `failed` to `REJECTED`;
- `deferred` to `DEFERRED`; or
- any provider or candidate diagnostic to a decision outcome.

Such policy automation requires a later separately governed contract.

## 11. Authorization boundary

The exact generated-candidate decision may be passed to `authorize_generated_candidate_decision_action` exactly once.

The requested action and authorization outcome remain explicit inputs.

The orchestrator must not infer requested action from decision or evaluation outcome.

In particular:

- `ACCEPTED` does not implicitly mean `ASSET_ADMISSION`;
- `REJECTED` does not implicitly mean `RETRY_REGENERATION`;
- `DEFERRED` does not implicitly mean `WORKFLOW_TRANSITION`;
- any decision outcome does not implicitly mean `AUTONOMOUS_ITERATION`.

The authorization function remains the sole authority for materializing the decision-action authorization record.

## 12. Action dispatch boundary

If authorization outcome is `DENIED` or `DEFERRED`, no action executor may be called.

If authorization outcome is `AUTHORIZED`, the orchestrator may dispatch to exactly one action-specific executor according to the exact explicit `requested_action`:

- `ASSET_ADMISSION` -> `execute_generated_candidate_asset_admission`;
- `RETRY_REGENERATION` -> `execute_generated_candidate_retry_regeneration_action`;
- `WORKFLOW_TRANSITION` -> `execute_generated_candidate_workflow_transition_action`;
- `AUTONOMOUS_ITERATION` -> `execute_generated_candidate_autonomous_iteration_action`.

No authorization may execute more than one branch.

No action executor may be substituted for another.

Every branch must receive only its explicitly required action-specific inputs.

## 13. Asset-admission branch

The asset-admission branch must reuse the exact candidate from the cycle and the exact authorization for that candidate.

It must preserve the accepted asset-admission executor's existing requirements, including exact candidate identity/checksum binding, candidate authority invariants, explicit admitted asset reference, actor/reference, and timezone-aware timestamp.

The orchestrator must not itself elevate candidate authority, mutate an asset registry, or claim production release.

## 14. Retry-regeneration branch

The retry-regeneration branch may invoke the accepted retry-regeneration executor exactly once.

The branch may therefore perform one separately authorized retry provider attempt.

The resulting provider output remains retry-regeneration execution evidence only.

Within the same single-cycle orchestration invocation, the orchestrator must not:

- bridge the retry output into a new candidate;
- evaluate the retry output;
- decide the retry output;
- authorize another action for the retry output;
- recurse into another orchestration cycle.

A later cycle requires a new separately governed invocation and new applicable authorization lineage.

## 15. Workflow-transition branch

The workflow-transition branch must preserve the accepted executor's existing campaign, instruction, actor, workflow-state, evidence, reason-code, contract, idempotency, and transition-evaluation requirements.

The orchestrator must not bypass the accepted workflow transition evaluator or synthesize a transition result.

Workflow transition execution remains bounded by its own contract and is not equivalent to production release.

## 16. Autonomous-iteration branch

The autonomous-iteration branch may materialize exactly one bounded autonomous-iteration action execution record.

The orchestrator must preserve explicit:

- iteration plan reference;
- current iteration index;
- maximum iteration count;
- next-step reference;
- execution actor/reference; and
- execution timestamp.

The orchestrator must not increment the iteration index, infer the next step, recursively invoke itself, or initiate another cycle.

The autonomous-iteration action remains evidence of one bounded iteration advance, not a loop engine.

## 17. Single-cycle orchestration result

A future implementation should return one immutable result containing at minimum:

- one deterministic orchestration-cycle identity;
- exact initial generation request fingerprint or exact request projection;
- exact provider/model configuration references;
- exact initial generation result reference/evidence;
- exact candidate identity and content checksum;
- exact evaluation identity and aggregate outcome;
- exact decision identity and decision outcome;
- exact authorization identity, requested action, and authorization outcome;
- zero or one exact action-execution result;
- one explicit branch outcome;
- exact cycle actor/reference;
- exact cycle timestamp or explicit component timestamps;
- deterministic provenance.

When authorization is not `AUTHORIZED`, the action-execution result must be absent.

When authorization is `AUTHORIZED`, exactly one action-execution result must be present and its type must match the requested action.

## 18. Deterministic cycle identity

The orchestration cycle identity must be a deterministic lowercase SHA-256 derived from exact explicit inputs and exact accepted component results.

For identical exact:

- generation request;
- provider/model configuration;
- provider execution evidence;
- generated-output checksum;
- candidate lineage;
- criterion results;
- evaluation result;
- decision inputs/result;
- authorization inputs/result;
- selected action-specific inputs/result;
- explicit actors/references;
- explicit timestamps;

the orchestration identity and deterministic provenance must be identical.

The identity must not depend on randomness, implicit current time, process-local object identity, mutable filesystem paths, hidden environment state, or secrets.

This requirement does not claim deterministic model output. It governs evidence identity after exact provider output is known.

## 19. Fail-closed sequencing

The orchestration must fail closed immediately when any component or compatibility precondition fails.

A failed step must not cause downstream steps to run.

At minimum:

- failed initial generation -> no candidate;
- failed candidate bridge -> no evaluation;
- failed evaluation -> no decision;
- unresolved evaluation-to-decision compatibility -> no decision;
- failed decision -> no authorization;
- failed authorization -> no action execution;
- non-`AUTHORIZED` authorization -> no action execution;
- failed action execution -> no second branch and no recursive cycle.

Partial results must not be represented as a completed cycle.

## 20. No hidden policy or inferred control

This first orchestration slice must not infer or select:

- provider;
- model;
- reference assets;
- grounded prompt;
- generated-output checksum;
- evaluation criterion results;
- decision outcome;
- requested action;
- authorization outcome;
- admitted asset reference;
- retry request;
- workflow next state;
- autonomous iteration plan/index/max/next-step;
- actor identity;
- timestamps.

All such values must be explicit accepted inputs or exact outputs of already-governed component boundaries.

## 21. Side-effect boundary

The orchestration may cause only the external effects already explicitly authorized by the selected accepted component:

- one initial provider generation;
- optionally one retry provider attempt if the exact authorized action is `RETRY_REGENERATION`;
- workflow transition evaluation/execution as defined by the accepted workflow-transition executor.

The orchestration itself must not add persistence, database writes, registry mutation, queueing, scheduling, background jobs, deployment, publication, release, or human-pilot activity.

It must not stage, commit, or push repository content at runtime.

## 22. Existing surfaces remain authoritative

The first orchestration implementation must treat the published component contracts and public application functions as authoritative.

It must not weaken validation in:

- `ConcreteVisualGenerationExecutionAdapter`;
- `bridge_generated_output_to_creative_result_candidate`;
- `evaluate_generated_candidate`;
- `decide_generated_candidate`;
- `authorize_generated_candidate_decision_action`;
- `execute_generated_candidate_asset_admission`;
- `execute_generated_candidate_retry_regeneration_action`;
- `execute_generated_candidate_workflow_transition_action`;
- `execute_generated_candidate_autonomous_iteration_action`.

Any compatibility change required by Sections 6 or 9 must be separately identified, minimally scoped, tested, and reviewed before the orchestrator relies on it.

## 23. Explicitly out of scope

This contract does not authorize:

- a multi-cycle autonomous loop;
- recursive orchestration;
- automatic next-cycle scheduling;
- provider/model auto-selection;
- provider fallback;
- hidden decision policy;
- automatic requested-action policy;
- automatic authorization policy;
- model-based candidate judging;
- OCR, embeddings, semantic search, ontology, or knowledge-graph inference;
- persistence or repository adapters;
- queue or background-job execution;
- production release;
- deployment;
- human pilot;
- modification of existing accepted components without separate compatibility review.

## 24. Minimum implementation boundary implied by this contract

A later read-only implementation-boundary review must determine the smallest exact runtime change set.

The preferred end-state is:

- one immutable domain result type for one single-cycle orchestration result;
- one application orchestration function;
- deterministic cycle identity/provenance helpers;
- one focused domain test file;
- one focused application test file.

However, runtime orchestration must not be materialized until the two published composition seams are explicitly resolved:

1. generation adapter result / candidate-bridge provider-response compatibility; and
2. evaluation candidate-field naming / decision-consumer compatibility.

The implementation-boundary review must decide whether those seams require:

- narrow compatibility adapters/projections in new files;
- minimal corrections to existing files; or
- another smaller prerequisite contract.

No broader redesign is authorized.

## 25. Required verification before implementation

Before implementation is authorized, a later exact review must prove:

- all published component surfaces still exist at the accepted baseline;
- the contract remains exact and unmodified;
- the provider-response/candidate-bridge composition seam is resolved without duplicate provider execution;
- the evaluation/decision composition seam is resolved without silent field invention;
- single-cycle sequencing remains fail-closed;
- all control values remain explicit;
- at most one action executor can run;
- retry output cannot recurse into a second candidate in the same invocation;
- autonomous-iteration execution cannot recurse into another cycle;
- persistence and human pilot remain out of scope.

Only after those conditions are satisfied may source implementation proceed.
