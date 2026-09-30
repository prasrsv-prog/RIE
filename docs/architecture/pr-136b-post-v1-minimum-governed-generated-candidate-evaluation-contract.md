# PR-136B — Post-v1 Minimum Governed Generated-Candidate Evaluation Contract

## Boundary
Evaluate exactly one immutable `CreativeResultCandidate` and emit exactly one immutable governed evaluation record. Evaluation is evidence only: it does not accept, approve, publish, persist, retry, regenerate, select among candidates, transition workflow state, or create a governed asset.

## Candidate authority and lineage
The exact candidate type is required. Preserve its candidate ID, workflow/project/campaign/brief/instruction references, content checksum, artifact type, and deterministic provenance. The candidate remains `CANDIDATE`; `official_source_claimed`, `accepted_asset_claimed`, and `approved_asset_claimed` remain false.

## Explicit criteria
Evaluation uses only explicit caller-supplied governed criterion results. Each criterion has a unique stable ASCII identifier, one controlled outcome, and a non-empty ASCII reason/evidence reference. At least one criterion is required.

Controlled criterion outcomes are exactly `passed`, `failed`, and `deferred`. Provider success, filename, URL, candidate order, or mutable transport metadata must not imply a criterion result.

## Deterministic aggregate
Aggregate outcome is exactly:
1. any `failed` -> `failed`;
2. otherwise any `deferred` -> `deferred`;
3. otherwise -> `passed`.

`passed` means only that the supplied governed criteria passed for this exact candidate. It is not acceptance, approval, publication, governed-asset admission, or workflow-transition authorization.
`failed` does not itself authorize retry/regeneration.
`deferred` does not itself trigger human review or external action.

## Immutable evaluation record
The record contains at minimum a deterministic evaluation identity; exact candidate ID/checksum and workflow/project/campaign/brief/instruction lineage; exact ordered criterion results; aggregate outcome; evaluator actor; timezone-aware evaluation timestamp; and deterministic provenance.

Identity is deterministic from stable governed inputs and excludes mutable paths, transient URLs/data URIs, credentials, secrets, implicit current time, randomness, generated UUIDs, diagnostics, and repository location.

## Fail closed
Fail before producing a record if the input is not the exact candidate type; candidate authority/premature-claim invariants are invalid; lineage is blank/malformed/inconsistent; checksum is not lowercase SHA256; criteria are empty/malformed/duplicated/uncontrolled; evaluator actor is blank/non-ASCII; timestamp is not timezone-aware; or aggregate outcome differs from the deterministic rule. No partial record is allowed.

## Side-effect boundary
No network/provider request, credential read, candidate mutation, acceptance/approval, governed-asset creation/admission, retry/regeneration/fallback/autonomous iteration, ranking/winner/latest-wins selection, workflow transition, persistence/repository mutation, paid-provider routing, human-pilot execution, or evaluation-time Git staging/commit/push is authorized.

## Expected later implementation slice
A separately authorized implementation may introduce exactly:
- `src/rie/domain/generated_candidate_evaluation.py`
- `src/rie/application/evaluate_generated_candidate.py`
- `tests/domain/test_generated_candidate_evaluation.py`
- `tests/application/test_evaluate_generated_candidate.py`

This materialization gate authorizes no implementation.

## Downstream separation
The handoff is:
`CreativeResultCandidate -> governed evaluation evidence -> future decision/action boundary`.

Candidate acceptance/rejection handling, retry, and bounded autonomous iteration remain separate later boundaries.

## Scope lock
This contract is limited to `MINIMUM_GOVERNED_GENERATED_CANDIDATE_EVALUATION_CONTRACT`, the exact smallest gap selected by PR-136A. It must not expand into retry, autonomous iteration, human pilot, paid-provider planning, persistence, or asset acceptance.
