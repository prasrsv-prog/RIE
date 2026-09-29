# PR-132B — Minimum Explicit Single-Provider Visual Generation Transport Contract

## Status
Corrected after PR-132C endpoint-compatibility review. No live provider call is authorized.

## Provider
The only supported provider identity is exactly `openai`. Model identity remains explicit existing configuration; no model may be silently selected or replaced.

## Deterministic endpoint rule
One transport invocation selects exactly one endpoint:
- empty `reference_media_refs` -> `POST /v1/images/generations`;
- non-empty `reference_media_refs` -> `POST /v1/images/edits`.

This is deterministic endpoint translation, not provider/model selection, fallback, retry, or autonomous iteration.

## Input and authority
The transport accepts only the published adapter mapping: `provider_id`, `model_id`, `grounded_prompt`, and `reference_media_refs`.
It must reject unsupported/ambiguous fields and must not reinterpret product truth, infer asset roles, widen rights, substitute references, or add creative claims.

Reference-media order and identity must be preserved. Translation to provider-required image inputs must be explicit, deterministic, and tested.

## Credentials
Credentials are runtime-injected. Secrets must never be committed, embedded in tests, written to governance evidence, returned in diagnostics, or copied into provenance/output references. Missing credentials fail closed before network execution.

## Execution
At most one OpenAI Images request may occur per transport invocation. No retry, fallback, polling-based creative iteration, or second creative attempt is authorized.

The grounded prompt remains the RCIS prompt authority. No hidden prompt rewrite is authorized at the RCIS boundary.

## Response
Success normalizes into existing `ProviderExecutionResponse` with `execution_status="SUCCEEDED"`, non-empty unique provider output references, execution reference when available, and bounded non-secret diagnostics.
Malformed, rejected, empty, timeout, authentication, authorization, transport, or provider errors fail closed.

Provider success remains non-governed and must not imply candidate admission, asset acceptance, approval, or release.

## Implementation boundary
Before implementation, a read-only review must determine the smallest exact path set.
Expected conceptual surfaces are one OpenAI Images transport source, one focused test path, and only if proven necessary one minimal dependency/configuration path.
Existing provider-neutral and concrete execution-adapter authorities remain unchanged unless review proves a minimal compatible extension unavoidable.

Focused tests use fakes/stubs only and cover exact provider/model identity, deterministic generations-vs-edits selection, reference preservation, credential failure without secret exposure, exactly-one-call behavior, response normalization, malformed/rejected response failure, and absence of retry/fallback/candidate admission.

## Deferred
Live provider execution proof, provider/model auto-selection, multi-provider routing, autonomous retry/iteration, candidate ingestion/provenance, governed evaluation, automatic accept/reject, asset admission, production release, and human pilot remain deferred.
