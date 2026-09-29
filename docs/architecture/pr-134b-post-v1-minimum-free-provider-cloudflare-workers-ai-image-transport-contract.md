# PR-134B — Minimum Free-Provider Cloudflare Workers AI Image Transport Contract

## Status
Proposed governed post-v1 contract. This contract does not authorize live provider execution.

## Purpose
Define the smallest explicit free-first transport boundary from the existing provider-neutral visual generation adapter to Cloudflare Workers AI using `@cf/black-forest-labs/flux-1-schnell`.

## Provider and model lock
- Provider identity: `cloudflare-workers-ai`.
- Initial model identity: `@cf/black-forest-labs/flux-1-schnell`.
- Model selection is explicit; the transport must not silently substitute another model.
- This track is intended for Workers Free-plan validation before any paid-provider planning.

## REST boundary
- Endpoint form: `POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell`.
- Authentication uses a runtime-injected Cloudflare API token.
- Account ID is runtime-injected explicitly.
- Token and Account ID must never be hard-coded in source/tests or emitted into governance evidence.
- Missing/blank credentials fail before network execution.
- At most one provider request per transport invocation.
- No retry, fallback, polling, second provider call, or hidden provider/model selection.

## Input translation
The transport accepts only the existing adapter mapping:
- `provider_id`
- `model_id`
- `grounded_prompt`
- `reference_media_refs`

Rules:
- `provider_id` must exactly identify the Cloudflare Workers AI transport.
- `model_id` must exactly match the locked model.
- `grounded_prompt` is authoritative and must be forwarded without adding creative claims.
- Initial FLUX schnell transport supports text-to-image only; non-empty `reference_media_refs` fail closed before network execution.
- The transport must not reinterpret product truth, infer creative asset roles, widen rights, or substitute references.
- Request construction must be deterministic. Any optional generation parameters must be explicitly governed before use.

## Output translation
- Successful provider output must contain the expected generated image field.
- Provider image data may be represented as a provider-local data reference/output reference suitable for the existing `ProviderExecutionResponse`.
- Empty, malformed, rejected, unauthorized, quota-exhausted, or transport-error responses fail closed.
- Provider success remains non-governed output. It is not automatically a `CreativeResultCandidate`, accepted asset, official product truth, or released creative.
- Credential material must never appear in output refs, diagnostics, provenance, logs, or governance evidence.

## Free-first guard
- Live proof is authorized only while the selected Cloudflare account remains on a no-paid-usage path for Workers AI.
- Free allocation exhaustion must fail closed; the implementation must not auto-upgrade, purchase credits, or route to a paid third-party provider.
- Paid-provider execution remains separately governed and deferred.

## Implementation boundary
Expected smallest implementation:
1. `src/rie/application/cloudflare_workers_ai_image_transport.py`
2. `tests/application/test_cloudflare_workers_ai_image_transport.py`

No dependency change is expected: Python standard-library networking may be injected behind a callable boundary and focused tests must use fakes/stubs only.
Existing provider-neutral boundaries and the published OpenAI transport remain unchanged unless a later review proves modification unavoidable.

## Required focused tests
Tests must prove:
- exact provider/model validation;
- deterministic endpoint and request translation;
- prompt preservation;
- non-empty reference rejection before network;
- missing Account ID/token rejection before network;
- exactly one injected HTTP invocation on success;
- successful image-output translation;
- malformed/error/quota response failure;
- no retry/fallback;
- no environment credential lookup inside the transport;
- no candidate admission or autonomous iteration.

## Explicitly deferred
- live Cloudflare execution proof;
- reference-image generation/editing;
- automatic provider selection;
- multi-provider routing;
- retry/fallback/autonomous iteration;
- candidate ingestion and provenance bridge;
- governed evaluation and accept/reject;
- release/admission;
- paid-provider planning;
- human pilot.
