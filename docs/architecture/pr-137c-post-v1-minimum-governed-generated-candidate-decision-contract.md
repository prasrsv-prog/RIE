# PR-137C â€” Post-v1 Minimum Governed Generated-Candidate Decision Contract

## 1. Purpose

This contract defines the minimum governed decision boundary immediately downstream of one immutable `GeneratedCandidateEvaluation`.

The boundary converts explicit caller-authorized decision input plus exact evaluation evidence into one immutable governed decision record. It does not perform the action that may later follow from that decision.

## 2. Exact input boundary

The decision operation accepts exactly one valid immutable `GeneratedCandidateEvaluation` and explicit decision inputs supplied by the caller.

The evaluation record remains evidence. Its aggregate outcome MUST NOT silently or automatically become a decision.

The decision operation MUST fail closed when the evaluation is malformed, candidate/evaluation lineage is inconsistent, decision vocabulary is unsupported, required decision evidence is absent, actor identity is invalid, or the decision timestamp is not timezone-aware.

## 3. Controlled decision vocabulary

The only governed decision outcomes are:

- `ACCEPTED`
- `REJECTED`
- `DEFERRED`

The caller MUST explicitly supply the decision outcome.

`ACCEPTED` means only that the exact evaluated candidate has an immutable governed acceptance decision record.

`REJECTED` means only that the exact evaluated candidate has an immutable governed rejection decision record.

`DEFERRED` means only that the exact evaluated candidate has an immutable governed deferred decision record.

No evaluation aggregate maps implicitly to any of these decision outcomes.

## 4. Required lineage and evidence

The immutable decision record MUST preserve or bind:

- deterministic decision identity;
- exact evaluation identity;
- exact creative-result-candidate identity;
- candidate content SHA-256;
- workflow request reference;
- project context reference;
- campaign context reference;
- creative brief reference;
- instruction reference;
- evaluation aggregate outcome;
- explicit governed decision outcome;
- nonempty ASCII decision reason/evidence reference;
- decision actor reference;
- timezone-aware decision timestamp;
- deterministic provenance linking candidate, evaluation, and decision.

Identity construction MUST exclude mutable filesystem paths, transient URLs or data URIs, secrets or credentials, implicit current time, randomness, generated UUIDs, diagnostics, and repository location.

## 5. Authority separation

A governed decision record is not a governed asset and is not an asset-admission record.

`ACCEPTED` MUST NOT itself:

- mutate the `CreativeResultCandidate`;
- change candidate authority state;
- set accepted/approved asset claims;
- create or admit a governed asset;
- approve an asset;
- publish content;
- transition the governed creative workflow;
- invoke a provider;
- authorize retry or regeneration.

`REJECTED` MUST NOT itself authorize or execute retry, regeneration, fallback, provider selection, or autonomous iteration.

`DEFERRED` MUST NOT itself trigger human review, workflow transition, retry, provider execution, or any other action.

Any action downstream of a decision requires a separate governed boundary and separate authorization.

## 6. Determinism and immutability

The decision record MUST be immutable.

For identical explicit inputs, deterministic identity MUST be identical. Any identity-bearing change to candidate/evaluation lineage, decision outcome, decision reason/evidence reference, decision actor, or explicit decision timestamp MUST affect deterministic identity.

Ordered/canonical serialization used for identity MUST be explicit and stable.

## 7. Side-effect prohibition

Decision evaluation and record construction MUST perform no:

- network or provider request;
- credential read;
- candidate mutation;
- governed-asset creation/admission/approval;
- retry, regeneration, fallback, or autonomous iteration;
- ranking, winner selection, or latest-wins selection;
- workflow transition;
- repository persistence or other durable persistence;
- paid-provider routing;
- human-pilot execution;
- Git staging, commit, or push.

## 8. Expected later implementation boundary

A later explicitly authorized implementation may introduce the smallest additive domain/application/test paths required for this contract.

No implementation path is authorized by PR-137C itself.

## 9. Downstream separation

The required sequence remains:

`CreativeResultCandidate -> GeneratedCandidateEvaluation evidence -> governed generated-candidate decision -> future separately governed action boundary`

Retry/regeneration and bounded autonomous iteration remain later boundaries. Asset admission/approval, workflow transition, persistence, paid-provider planning, and human pilot also remain outside this contract.

## 10. Scope lock

PR-137C is limited to `MINIMUM_GOVERNED_GENERATED_CANDIDATE_DECISION_CONTRACT`.

It authorizes only materialization and review of this architecture contract. It does not authorize implementation, tests, publication, retry, autonomous iteration, asset admission, workflow transition, persistence, provider activity, paid routing, or human pilot.