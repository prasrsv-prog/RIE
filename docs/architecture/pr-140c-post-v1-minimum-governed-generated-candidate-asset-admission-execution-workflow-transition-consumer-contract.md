# PR-140C — Post-v1 Minimum Governed Generated-Candidate Asset-Admission Execution Workflow-Transition Consumer Contract

## Status

Proposed bounded contract for the smallest governed downstream consumer of an exact
`GeneratedCandidateAssetAdmissionExecution` record.

This contract is intentionally narrower than retry/regeneration execution,
autonomous iteration, persistence, publication, or any generic workflow mutation.

## 1. Purpose

The purpose of this boundary is to allow the already-published governed creative
workflow machinery to consume exact successful generated-candidate asset-admission
execution evidence without treating admission evidence itself as an implicit
workflow transition.

The boundary closes only the demonstrated zero-consumer gap for
`GeneratedCandidateAssetAdmissionExecution`.

## 2. Required inputs

A conforming consumer must receive all of the following explicitly:

1. one exact immutable `GeneratedCandidateAssetAdmissionExecution`;
2. the exact current governed creative-workflow context required by the existing
   workflow-transition evaluator;
3. one explicit caller-supplied requested workflow transition or target state;
4. one explicit actor/reference identifying who or what requested the consumption;
5. one timezone-aware consumption timestamp.

The consumer must not synthesize any missing workflow transition request from the
admission record.

## 3. Admission-evidence preconditions

The consumer must fail closed unless all of the following are true:

1. the supplied admission object is exactly the governed
   `GeneratedCandidateAssetAdmissionExecution` type expected by this boundary;
2. its execution outcome is exactly `ADMITTED`;
3. its admitted governed asset reference is non-empty and exact;
4. its generated-candidate identity and candidate checksum are present and
   internally consistent with the admission record;
5. its authorization, decision, and evaluation lineage references remain present
   exactly as recorded by the admission execution boundary;
6. the admission record is not mutated, rewritten, re-keyed, or replaced.

`ADMITTED` is necessary evidence for this boundary, but `ADMITTED` alone does not
authorize any workflow transition.

## 4. Workflow-context preconditions

The consumer must fail closed unless the supplied workflow context is one that the
existing governed creative-workflow transition machinery can evaluate.

For a workflow currently using the existing `ASSET_ADMISSION_PENDING`,
`accepted_governed_asset_reference`, or `asset_admission_execution_requested`
semantics, the consumer must preserve those semantics exactly and must not invent a
parallel workflow state model.

If an accepted governed asset reference is already present in the supplied workflow
context, that reference must equal the exact admitted governed asset reference from
the admission execution record. Any mismatch is a hard failure.

## 5. Explicit transition request

The transition request or target state must be supplied explicitly by the caller.

The consumer must not infer a next state from any of the following:

- `ADMITTED`;
- an accepted generated-candidate decision;
- an `AUTHORIZED` action-authorization outcome;
- `ASSET_ADMISSION_PENDING`;
- the presence of an admitted governed asset reference;
- any provider/model result;
- any retry or autonomous-iteration vocabulary.

Whether the requested transition is valid remains the responsibility of the
existing governed workflow-transition rules.

## 6. Permitted consumption behavior

A conforming implementation may perform only the minimum deterministic bridge
required to present the exact admission evidence to the existing governed
workflow-transition evaluator.

It may:

1. validate the exact admission record and exact workflow context;
2. bind the exact admitted governed asset reference into the workflow-transition
   evaluation inputs where the existing evaluator already exposes the corresponding
   governed field;
3. bind the existing asset-admission execution-request signal only according to the
   existing evaluator contract;
4. invoke the existing pure/deterministic workflow-transition evaluator at most once;
5. return an immutable consumer result containing:
   - the exact admission execution identity;
   - the exact admitted governed asset reference;
   - the exact explicit requested transition;
   - the exact workflow-transition evaluation result;
   - the actor/reference;
   - the timezone-aware timestamp;
   - deterministic provenance sufficient to reproduce the consumer identity.

## 7. Consumer result semantics

The consumer result is evidence that an exact admission execution record was
consumed by the governed workflow-transition evaluation boundary.

It is not, by itself:

- persistence;
- a database or registry mutation;
- a committed workflow state change;
- publication;
- external asset-registry admission;
- a retry/regeneration request;
- retry/regeneration execution;
- autonomous-iteration authorization;
- autonomous-iteration execution;
- provider/model invocation;
- a human-pilot action.

A successful workflow-transition evaluation does not silently materialize or persist
the resulting workflow state.

Any actual workflow-state mutation or persistence, if required later, must remain a
separately governed downstream boundary.

## 8. Determinism and immutability

For identical exact inputs, a conforming consumer must produce the same semantic
result and deterministic consumer identity.

The consumer must not mutate:

- `GeneratedCandidateAssetAdmissionExecution`;
- its upstream authorization;
- its upstream decision;
- its upstream evaluation;
- the generated candidate;
- the supplied workflow context;
- the existing workflow-transition evaluator result.

## 9. Fail-closed requirements

The boundary must reject, without partial success, at least the following:

- wrong admission object type;
- admission outcome other than `ADMITTED`;
- missing or malformed admitted governed asset reference;
- admission/workflow asset-reference mismatch;
- missing explicit transition request;
- unsupported or invalid workflow context;
- missing required lineage evidence;
- attempts to infer a workflow target implicitly;
- attempts to perform retry/regeneration;
- attempts to perform autonomous iteration;
- attempts to mutate or persist workflow state;
- attempts to invoke a generation provider/model.

## 10. Explicitly out of scope

This contract does not authorize:

- retry/regeneration action execution;
- generation-provider invocation;
- model selection;
- candidate generation;
- candidate re-ingestion;
- autonomous iteration;
- autonomous retry loops;
- workflow persistence;
- generic registry mutation;
- publication;
- usage-right expansion;
- human pilot activity.

## 11. Closure condition

This gap is closed only when a separately reviewed implementation can prove that an
exact `GeneratedCandidateAssetAdmissionExecution` is consumed by the existing
governed workflow-transition machinery under the fail-closed rules above, with no
hidden state mutation and no widening into retry/regeneration or autonomous
iteration.

Until that implementation is separately reviewed, tested, and published, this
document is contract evidence only.
