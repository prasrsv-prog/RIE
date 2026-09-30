# PR-135G — Minimum Generated Output to Creative Result Candidate Provenance Bridge Contract

## Status
Proposed post-v1 bounded contract. This document does not authorize implementation, candidate admission, provider execution, asset admission, approval, or publication.

## Proven basis
PR-135F established that:
- `CreativeResultCandidate` is the existing immutable Gate 18 candidate record and requires candidate identity, workflow/project/campaign/brief/instruction bindings, a lowercase SHA256 content checksum, admitting actor, deterministic provenance, exact `CANDIDATE` authority, and false accepted/approved authority claims.
- `ProviderExecutionResponse` represents successful provider execution and exposes non-empty `provider_output_refs` plus an optional `provider_execution_ref`.
- the concrete visual-generation execution adapter explicitly performs no candidate admission.
- the governed creative workflow already accepts a project/campaign-bound `creative_result_candidate_reference`.
No reviewed path established a bridge that constructs a provenance-bound `CreativeResultCandidate` from generated provider output.

## Smallest gap
`MINIMUM_GENERATED_OUTPUT_TO_CREATIVE_RESULT_CANDIDATE_PROVENANCE_BRIDGE`.

## Required bridge behavior
The bridge SHALL:
1. accept explicit governed workflow/context inputs rather than infer them from provider output;
2. accept exactly one successful `ProviderExecutionResponse`;
3. accept exactly one generated output's immutable bytes or an explicitly supplied lowercase SHA256 checksum bound to that output;
4. fail closed when provider execution is not successful, output cardinality is not exactly one, checksum is malformed, or required governed bindings are absent/inconsistent;
5. preserve the exact workflow request, project, campaign, creative brief, and instruction references supplied by governed inputs;
6. derive or validate `candidate_content_checksum` as the lowercase SHA256 of the generated output bytes;
7. preserve provider/model/execution/output lineage in deterministic provenance using explicit immutable ASCII references;
8. construct exactly one existing `CreativeResultCandidate` with authority state exactly `CANDIDATE`;
9. set all premature authority-claim flags to false;
10. perform no accepted-asset admission, approved-asset claim, official-source claim, workflow transition, provider retry, provider selection, persistence, or publication.

## Provenance minimum
Deterministic provenance SHALL include, in stable order, explicit references sufficient to bind:
- workflow request identity;
- generation provider identity;
- generation model identity;
- provider execution reference when non-empty;
- the selected provider output reference or an immutable digest-derived reference when the provider output reference itself is unsuitable as immutable provenance;
- generated content SHA256.

The bridge MUST NOT treat a mutable URL, transient data URI, secret, bearer token, or credential value as durable provenance.

## Identity and authority
Candidate identity and admitting actor/service identity MUST be explicit inputs or be derived only by a separately locked deterministic rule. This contract does not grant the bridge authority to invent operator approval, accepted-asset state, or governed-asset state.

## Expected implementation boundary
Expected new paths:
- `src/rie/application/generated_output_creative_result_candidate_bridge.py`
- `tests/application/test_generated_output_creative_result_candidate_bridge.py`

Existing domain contracts SHOULD be reused without modification unless a later exact review proves modification is unavoidable.

## Verification boundary
Targeted tests SHALL prove:
- one valid generated output constructs one immutable candidate;
- checksum is exact and deterministic;
- context/instruction bindings are preserved;
- provider/model/execution/output provenance is preserved without secrets;
- invalid execution/cardinality/checksum/context fails closed;
- authority remains `CANDIDATE`;
- accepted/approved/official-source claims remain false;
- no provider request, retry, persistence, workflow transition, or asset admission occurs.

## Out of scope
Multi-output admission, retry/iteration, autonomous evaluation, candidate persistence, evidence materialization, asset acceptance, approval, paid-provider routing, and human-pilot execution remain outside this boundary.
