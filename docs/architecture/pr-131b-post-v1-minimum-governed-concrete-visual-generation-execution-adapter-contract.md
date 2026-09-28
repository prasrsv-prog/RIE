# PR-131B â€” Minimum Governed Concrete Visual Generation Execution Adapter Contract

## Status
Proposed post-v1 autonomous-generation contract. This contract does not itself authorize provider/model execution.

## Evidence basis
PR-131A established that the published repository already contains:
- a deterministic governed Real Asset / Product creative-intelligence assembly;
- a `VisualGenerationRequest`, `VisualGenerationResult`, and `VisualGenerationProvider` protocol;
- UI wiring that can invoke an injected provider;
- a governed `CreativeResultCandidate` domain record;
- no concrete model/network/generator runtime in the visual-generation provider boundary;
- no bounded autonomous iteration surface.

The smallest missing boundary is therefore a concrete visual-generation execution adapter contract between the existing provider-neutral request boundary and one explicitly configured external generation capability.

## Objective
Define the minimum fail-closed adapter contract required to execute exactly one visual-generation request while preserving RCIS product truth, governed reference identity, authority boundaries, and auditable provenance.

## Authority boundary
The adapter MUST NOT:
1. create, modify, reinterpret, or widen product truth;
2. infer asset roles from pixels, embeddings, filenames, directories, MIME type, EXIF, UI order, or asset order;
3. widen asset rights or use eligibility;
4. convert provider success into governed candidate acceptance, asset acceptance, approval, or production release;
5. mutate Gate 17, Gate 18, operator approval, governed asset admission, or upstream evidence;
6. perform autonomous retry/iteration;
7. select among providers/models using hidden heuristics;
8. persist provider credentials, secrets, or raw authorization material in RCIS evidence.

## Required input
A concrete adapter may receive only an already-valid `VisualGenerationRequest` plus explicit immutable execution configuration sufficient for one provider/model invocation. The request's grounded prompt and selected governed reference IDs MUST be preserved exactly at the RCIS boundary.

Any translation into provider-specific request fields MUST be deterministic, inspectable, and covered by focused tests.

## Explicit provider/model configuration
Provider identity and model identity MUST be explicit configuration. Missing, blank, unsupported, or ambiguous provider/model identity MUST fail closed before network/model execution.

The first implementation slice MUST target exactly one concrete provider adapter. Multi-provider routing, fallback, ranking, model selection, and cost optimization are out of scope.

## Reference handling
Selected reference asset IDs are identifiers, not permission to bypass governed asset access. A concrete adapter MUST use an explicit authorized reference-resolution dependency if provider bytes/URLs are required.

Reference resolution MUST preserve exact identity and MUST fail closed if:
- a selected reference cannot be resolved;
- the resolved identity does not match the requested governed reference;
- rights/use eligibility is absent or no longer valid;
- provider-required media cannot be constructed without widening authority.

## Execution result
One invocation returns provider-local execution metadata only. At minimum, the adapter result must permit deterministic audit of:
- provider identity;
- model identity;
- provider request/execution reference when available;
- returned output references;
- execution status;
- non-secret diagnostic information.

Provider output MUST remain non-governed until a separate candidate-ingestion/provenance bridge validates and materializes a `CreativeResultCandidate`.

## Failure semantics
Configuration, request construction, reference resolution, transport, provider rejection, timeout, malformed response, and unsupported output MUST fail closed with bounded diagnostics.

No failure may fabricate output references, candidate identity, approval, asset admission, or success.

## Secrets
Credentials MUST enter through an injected runtime/configuration mechanism and MUST NOT be written into source, tests, reports, provenance, diagnostics, or committed configuration.

Tests MUST use fakes/stubs and MUST NOT call a real provider.

## Determinism and auditability
Given the same governed request and same explicit non-secret execution configuration, provider-specific request construction MUST be deterministic.

The adapter must expose enough non-secret metadata to bind a later candidate-ingestion record to the exact execution without claiming that provider-local metadata is governed provenance by itself.

## Initial implementation boundary
The first implementation proposal after this contract is accepted SHOULD be limited to the smallest source/test path set proven necessary by a read-only boundary review.

Expected conceptual surfaces:
- one concrete adapter implementation;
- focused tests for exact request translation, explicit provider/model identity, fail-closed behavior, reference-resolution boundary, secret exclusion, and provider-result normalization.

Existing `visual_generation_provider.py` remains the provider-neutral protocol authority unless a subsequent read-only review proves a minimal compatible extension is required.

## Explicitly deferred
- real provider/model execution proof;
- provider/model auto-selection;
- multi-provider routing/fallback;
- autonomous retry/iteration;
- generated-candidate ingestion;
- governed candidate evaluation;
- automatic accept/reject;
- asset admission;
- UI expansion beyond wiring already present;
- production release.

## Acceptance condition
This contract is ready for implementation-boundary review only when:
- it introduces no runtime execution;
- it does not weaken existing authority boundaries;
- it selects one smallest concrete execution gap;
- subsequent implementation can remain testable without real network/model calls.