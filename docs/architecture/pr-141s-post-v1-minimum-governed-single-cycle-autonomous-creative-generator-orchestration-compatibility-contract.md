# PR-141S -- Post-v1 Minimum Governed Single-Cycle Autonomous Creative Generator Orchestration Compatibility Contract

## Status

Post-v1 bounded compatibility contract.

This contract resolves only the two concrete composition seams selected by PR-141R so that a later single-cycle autonomous creative generator orchestrator can compose already-published component boundaries without duplicate provider execution, synthetic shadow fields, monkey-patching, or broad domain redesign.

It does not implement the orchestrator itself.

## 1. Evidence basis

The accepted PR-141P orchestration contract requires compatibility reconciliation before runtime orchestration.

PR-141R confirmed two exact seams at published baseline `ba1fff3140f2cdf2325e01ffc8a462d37b89df0d`:

1. the concrete visual-generation adapter invokes one `ProviderTransport`, receives an exact `ProviderExecutionResponse`, but returns only `VisualGenerationResult`, while the candidate bridge requires an exact `ProviderExecutionResponse`; and
2. the canonical `GeneratedCandidateEvaluation` exposes `creative_result_candidate_id`, `candidate_content_checksum`, `campaign_context_reference`, and `instruction_reference`, while `decide_generated_candidate` currently expects synthetic attributes `candidate_id` and `candidate_checksum` and passes tuple-valued campaign/instruction references into downstream decision fields that are scalar strings.

PR-141R selected the following minimum resolutions:

- one new single-call provider-response capture helper plus one focused test file; and
- one minimal correction to `decide_generated_candidate.py` plus its focused application test file.

No other rewrite was selected.

## 2. Exact implementation path boundary

A future compatibility implementation, if separately authorized, must be limited to exactly these four paths:

1. `src/rie/application/execute_visual_generation_with_provider_response_capture.py` -- new;
2. `tests/application/test_execute_visual_generation_with_provider_response_capture.py` -- new;
3. `src/rie/application/decide_generated_candidate.py` -- modified;
4. `tests/application/test_decide_generated_candidate.py` -- modified.

The compatibility implementation must not modify:

- `src/rie/application/concrete_visual_generation_execution_adapter.py`;
- `src/rie/application/generated_output_creative_result_candidate_bridge.py`;
- `src/rie/domain/generated_candidate_evaluation.py`;
- `src/rie/domain/generated_candidate_decision.py`;
- `src/rie/domain/generated_candidate_decision_action_authorization.py`;
- `src/rie/application/authorize_generated_candidate_decision_action.py`;
- any action executor;
- provider transport implementations;
- workflow orchestration surfaces; or
- existing unrelated tests.

Any broader change requires a new separately governed boundary.

## 3. Provider-response capture compatibility purpose

The provider compatibility helper exists only to preserve the exact `ProviderExecutionResponse` already produced during the one accepted adapter invocation.

It must not create a second provider request.

It must not reconstruct a provider response from `VisualGenerationResult.message`, audit text, provider output references, or any lossy projection.

It must not bypass `ConcreteVisualGenerationExecutionAdapter`.

## 4. Provider-response capture input boundary

The helper must receive explicitly:

- one exact `VisualGenerationRequest`;
- one exact `VisualGenerationExecutionConfig`;
- one accepted `VisualReferenceResolver`;
- one explicit `ProviderTransport`.

It must construct and invoke exactly one `ConcreteVisualGenerationExecutionAdapter` using those exact inputs.

No provider, model, reference resolver, transport, request field, credential, or fallback may be inferred.

## 5. Exact single-call transport capture rule

The helper may wrap the caller-supplied `ProviderTransport` only to observe and retain the exact response object returned by that one transport invocation.

The wrapper must:

- call the caller-supplied transport at most once;
- preserve the provider request mapping exactly as supplied by the adapter;
- require the returned value to be an exact `ProviderExecutionResponse`;
- retain that exact immutable response object without mutation;
- return that same exact response object to the adapter;
- fail closed if invoked more than once;
- fail closed if no transport invocation occurs;
- fail closed if the transport returns an invalid object.

The wrapper must not perform retry, fallback, buffering, persistence, network discovery, credential lookup, logging of secrets, or response rewriting.

## 6. Captured generation result boundary

The helper should return one immutable compatibility result containing exactly:

- the exact `VisualGenerationResult` returned by the adapter; and
- the exact captured `ProviderExecutionResponse` returned by the caller-supplied transport.

A future implementation may use one frozen dataclass in the new helper module for this compatibility result.

The compatibility result must not:

- claim candidate authority;
- perform candidate admission;
- compute a decision;
- authorize an action;
- persist provider output;
- expose hidden credentials or transport configuration.

## 7. Provider result consistency checks

Before returning, the helper must verify at minimum:

- exactly one transport call occurred;
- `visual_generation_result.provider_output_refs == provider_execution_response.provider_output_refs`;
- the captured response remains successful under the existing `ProviderExecutionResponse` validation;
- the adapter result remains an exact `VisualGenerationResult`.

The helper must not parse the adapter audit string to reconstruct the response.

The helper may verify audit consistency only as a non-authoritative secondary check.

## 8. Candidate bridge consumption rule

The later orchestrator may pass the captured exact `ProviderExecutionResponse` directly to `bridge_generated_output_to_creative_result_candidate`.

The exact provider/model identities supplied to the generation configuration must also be supplied explicitly to the bridge.

The bridge remains authoritative for:

- output cardinality;
- generated-output checksum binding;
- immutable provider output reference normalization;
- candidate authority state;
- candidate provenance construction; and
- project/campaign binding.

This compatibility contract does not weaken or replace candidate-bridge validation.

## 9. No duplicate provider request

The single-cycle initial generation path must contain exactly one initial provider transport invocation.

The compatibility helper must not:

- invoke the transport directly and then invoke the adapter;
- invoke the adapter twice;
- call a second adapter;
- issue a verification request to the provider;
- retry on failure;
- fallback to another provider/model.

A later authorized `RETRY_REGENERATION` action remains a separate action-specific provider attempt and is not part of this initial compatibility helper.

## 10. Evaluation-to-decision correction purpose

The decision compatibility correction exists only to make `decide_generated_candidate` consume the canonical, validated fields of an exact `GeneratedCandidateEvaluation`.

It must eliminate reliance on synthetic shadow attributes created only in tests.

It must not modify the evaluation domain model.

## 11. Canonical evaluation field projection

For one exact `GeneratedCandidateEvaluation`, `decide_generated_candidate` must project:

- decision `candidate_id` from `evaluation.creative_result_candidate_id`;
- decision `candidate_checksum` from `evaluation.candidate_content_checksum`;
- decision `campaign_context_reference` from `evaluation.campaign_context_reference[1]`;
- decision `instruction_reference` from `evaluation.instruction_reference[0]`.

The function must continue to take:

- `evaluation_id` from `evaluation.evaluation_id`;
- workflow request reference from `evaluation.workflow_request_reference`;
- project context reference from `evaluation.project_context_reference`;
- creative brief reference from `evaluation.creative_brief_reference`;
- artifact type from `evaluation.artifact_type`;
- evaluation aggregate outcome from `evaluation.aggregate_outcome`;
- deterministic evaluation provenance from `evaluation.deterministic_provenance`.

No identity-bearing decision field may be invented.

## 12. Exact tuple compatibility validation

Before projecting campaign and instruction identifiers, the corrected decision application must fail closed unless:

- `campaign_context_reference` is an exact tuple of length two;
- its first value exactly equals `project_context_reference`;
- both campaign tuple values are valid nonempty ASCII text under the accepted evaluation model;
- `instruction_reference` is an exact tuple of length two;
- both instruction tuple values are valid nonempty ASCII text under the accepted evaluation model.

The decision projection uses only:

- campaign tuple element `[1]` as the scalar campaign identity; and
- instruction tuple element `[0]` as the scalar instruction identity.

The second instruction tuple value remains evaluation lineage context and must not be substituted as the instruction identity.

## 13. Decision identity preservation

The corrected `decide_generated_candidate` must continue to derive the decision SHA-256 deterministically from the same semantic identity projection, except that the projection now reads canonical evaluation fields instead of synthetic aliases.

For identical exact canonical evaluation and identical explicit decision inputs, the decision identity and deterministic provenance must be identical.

The correction must not introduce:

- random UUIDs;
- ambient current time;
- filesystem state;
- provider state;
- mutable object identity;
- hidden policy;
- secret material.

## 14. Existing downstream decision shape remains authoritative

The correction must continue to return the existing exact `GeneratedCandidateDecision`.

It must not change the decision domain field names or types.

The resulting decision must remain compatible with:

- `authorize_generated_candidate_decision_action`;
- `GeneratedCandidateDecisionActionAuthorization`;
- asset-admission execution;
- retry-regeneration execution;
- workflow-transition execution; and
- autonomous-iteration execution.

No authorization or action-executor rewrite is authorized by this contract.

## 15. Test correction boundary

`tests/application/test_decide_generated_candidate.py` must stop constructing a fake evaluation via `object.__new__(GeneratedCandidateEvaluation)` plus synthetic shadow attributes.

The corrected tests must use a real valid `GeneratedCandidateEvaluation` with canonical fields.

The tests must prove at minimum:

- exact canonical candidate identity projection;
- exact canonical candidate checksum projection;
- exact campaign ID projection from tuple element `[1]`;
- exact instruction ID projection from tuple element `[0]`;
- aggregate outcome does not implicitly determine decision outcome;
- identical exact inputs produce identical decision identity;
- identity-bearing decision inputs alter identity;
- wrong evaluation type fails closed;
- malformed compatibility tuple shape fails closed when independently constructible for the tested boundary; and
- timezone-naive decision timestamp fails closed.

Tests must not use monkey-patching or synthetic shadow fields to make incompatible shapes appear compatible.

## 16. Provider compatibility test boundary

The new provider-response capture helper tests must prove at minimum:

- exactly one transport invocation occurs;
- the adapter remains the generation execution path;
- the exact `ProviderExecutionResponse` object is captured;
- the adapter's `VisualGenerationResult` is returned unchanged;
- provider output references match between captured response and adapter result;
- a second transport invocation attempt fails closed;
- malformed transport response fails closed;
- provider/model auto-selection is absent;
- retry/fallback is absent;
- candidate admission is absent;
- no persistence or secret extraction is introduced.

The tests must use deterministic local fakes only and must not make a real provider/network request.

## 17. Compatibility implementation sequencing

A future exact implementation materialization must apply both compatibility resolutions as one bounded prerequisite slice before single-cycle orchestrator implementation.

The sequence is:

1. add the provider-response capture helper;
2. add its focused tests;
3. correct `decide_generated_candidate` canonical field projection;
4. correct its focused application tests;
5. run only the bounded compatibility tests first;
6. perform semantic review;
7. publish the compatibility slice only after all exact checks pass;
8. only then begin the orchestrator implementation boundary review.

The orchestrator must not be implemented against unresolved compatibility seams.

## 18. Fail-closed conditions

The compatibility slice must fail closed for at least:

- invalid generation request;
- invalid execution configuration;
- invalid resolver;
- invalid transport;
- transport called more than once;
- invalid provider response;
- missing captured provider response;
- adapter result type mismatch;
- provider output reference mismatch;
- non-exact `GeneratedCandidateEvaluation`;
- missing canonical evaluation fields;
- invalid campaign tuple shape or binding;
- invalid instruction tuple shape;
- invalid decision outcome;
- invalid decision timestamp;
- invalid deterministic evaluation provenance.

Failure must not trigger a second provider request, fabricate candidate evidence, fabricate decision fields, or invoke any downstream action.

## 19. No hidden policy or authority expansion

This compatibility slice must not infer or decide:

- provider or model;
- provider fallback;
- candidate evaluation criteria;
- decision outcome;
- requested action;
- authorization outcome;
- workflow transition;
- retry policy;
- autonomous next step;
- asset admission;
- production release.

It resolves data-shape compatibility only.

## 20. Side-effect boundary

The provider helper may cause only the single provider transport side effect already explicitly requested through the accepted adapter.

The decision correction is side-effect-free.

The compatibility slice must not add:

- persistence;
- databases;
- registries;
- queues;
- background jobs;
- scheduling;
- deployment;
- production publication;
- human pilot execution;
- repository mutation at runtime.

## 21. Explicitly out of scope

This contract does not authorize:

- the single-cycle orchestrator implementation itself;
- a multi-cycle autonomous loop;
- recursive orchestration;
- automated visual judging;
- automatic decision policy;
- automatic requested-action policy;
- automatic authorization policy;
- provider/model selection or fallback;
- candidate bridge rewrite;
- generation adapter rewrite;
- evaluation domain rewrite;
- decision domain rewrite;
- authorization rewrite;
- action-executor rewrite;
- persistence;
- production release;
- human pilot.

## 22. Definition of compatibility closure

This compatibility prerequisite may be considered closed only when:

- the new single-call capture helper exists and is tested;
- exactly one initial provider transport invocation is proven;
- the exact captured provider response can be supplied directly to the unchanged candidate bridge;
- `decide_generated_candidate` consumes a real canonical `GeneratedCandidateEvaluation`;
- synthetic decision-test shadow fields are removed;
- decision output remains compatible with unchanged downstream authorization;
- all bounded tests pass;
- no unrelated path changes are present; and
- the exact compatibility changes are published and post-publication-confirmed.

Only after that closure may the project proceed to the single-cycle orchestrator implementation boundary review.
