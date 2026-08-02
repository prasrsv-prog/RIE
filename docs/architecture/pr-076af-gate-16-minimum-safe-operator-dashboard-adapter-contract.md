# PR-076AF Gate 16 Minimum Safe Operator Dashboard Adapter Contract

Status: bounded Gate 16 architecture contract
Gate: 16 - Operator Dashboard and Approval Workflow
Upstream accepted review: PR-076AE Correction 1
Selected gap: MINIMUM_SAFE_OPERATOR_DASHBOARD_ADAPTER_BOUNDARY

## 1. Purpose

This contract defines the smallest safe operator dashboard-adapter boundary
required after the accepted and published operator approval decision,
role-authority, approval application-service, and approval audit-history
boundaries.

The adapter is an application-layer read-only projection boundary. It may
validate one explicit request, delegate to already accepted domain and
application services, and return one immutable projection suitable for a later
operator-facing interface.

This contract does not implement a web interface. It does not authenticate a
person, open a session, read or write storage, execute an approval, mutate a
target, or promote any object.

## 2. Accepted upstream authority

The following accepted identities remain authoritative:

- PR-076AE Correction 1 raw report SHA256:
  `e8f077bb917907165880fe37100aa52bdee4cbb822d3270605ccdd5ef6168ee7`
- Accepted main commit:
  `038a971519c37de815d0dd8cee6ef225d31f340c`
- Operator approval decision model:
  `src/rie/domain/operator_approval_decision.py`
- Operator role-authority model:
  `src/rie/domain/operator_role_authority.py`
- Operator approval application-service contract:
  `docs/architecture/pr-076n-gate-16-minimum-operator-approval-application-service-contract.md`
- Operator approval application service:
  `src/rie/application/operator_approval_application_service.py`
- Operator approval audit-history contract:
  `docs/architecture/pr-076z-gate-16-minimum-operator-approval-audit-history-contract.md`
- Operator approval audit-history model:
  `src/rie/domain/operator_approval_audit_history.py`

The accepted services remain non-persistent and non-self-executing.

## 3. Fixed authority separations

The dashboard-adapter boundary must preserve all of the following:

- Source Material != Extraction Result
- Extraction Result != Evidence
- Evidence != Knowledge
- Knowledge != business decision
- Prompt Candidate != final approved instruction
- OperatorApprovalDecision != executed lifecycle mutation
- Role-authority evaluation != executed approval
- Application-service assessment != persisted approval history
- Audit-history record != executed approval
- Dashboard projection != approval authorization
- Dashboard projection != target lifecycle mutation
- Generated Output != Official Source
- Generated Output != Accepted Asset
- Generated Output != Approved Creative Asset

No automatic promotion is allowed between any layers.

## 4. Exact adapter responsibility

A later separately authorized implementation may only:

1. accept one explicit immutable SafeOperatorDashboardRequest;
2. validate the request fail closed;
3. delegate role and permission evaluation to the accepted role-authority
   boundary;
4. delegate approval execution assessment to the accepted approval
   application-service boundary;
5. read a bounded projection from one supplied immutable
   OperatorApprovalAuditHistory value;
6. map accepted results into one immutable SafeOperatorDashboardProjection;
7. return one immutable SafeOperatorDashboardResult; and
8. expose deterministic status and error vocabulary.

The adapter must not discover identities, infer missing facts, repair
references, load storage, write storage, execute approval, or mutate a governed
target.

## 5. Immutable SafeOperatorDashboardRequest

A future request value must contain exactly these fields:

- `request_id`
- `operator_reference`
- `role_reference`
- `target_type`
- `target_reference`
- `action`
- `reason_reference`
- `audit_context_reference`
- `audit_limit`

Every text field must be non-empty ASCII text without leading or trailing
whitespace or control characters.

`audit_limit` must be an integer from 1 through 100 inclusive.

The request must not contain credentials, tokens, passwords, cookies, session
identifiers, database identifiers, storage locations, URLs, or transport
metadata.

`request_id` is caller supplied. The adapter must not generate it from a clock,
random value, hash, network service, database sequence, or hidden global state.

## 6. Explicit dependency inputs

A future adapter operation must receive all dependencies explicitly.

The minimum dependency inputs are:

- one accepted role-authority evaluator;
- one accepted approval application-service assessor;
- one immutable OperatorApprovalAuditHistory value; and
- one explicit SafeOperatorDashboardRequest.

The adapter must not instantiate storage, discover plugins, resolve network
services, inspect environment credentials, or use global mutable registries.

Dependency failure, malformed dependency output, or unexpected exception must
map to a deterministic fail-closed result.

## 7. Role-authority delegation

The adapter must delegate role and permission evaluation to the accepted
role-authority boundary.

The adapter must not duplicate permission rules, invent a permission
reference, weaken a denied evaluation, or convert an unknown result into an
allow result.

Only the exact accepted allow result with its exact permission reference may
be represented as allowed in the dashboard projection.

Any deny, malformed result, missing permission reference, identity mismatch,
target mismatch, or action mismatch must fail closed.

## 8. Approval assessment delegation

The adapter must delegate approval execution assessment to:

`assess_operator_approval_execution`

The adapter must supply the explicit request facts required by the accepted
application-service boundary.

The adapter must preserve exactly:

- decision identity;
- operator reference;
- role reference;
- permission reference;
- target type;
- target reference;
- action;
- assessment outcome;
- assessment reason code;
- reason reference;
- audit-context reference;
- lifecycle reason reference;
- provenance reference;
- rights reference;
- idempotency reference; and
- conflict reference.

The adapter must not convert `DENIED` into `ELIGIBLE`, execute an eligible
assessment, or treat eligibility as completed approval.

## 9. Bounded audit-history visibility

The adapter may read only from the immutable audit-history value supplied by
the caller.

The read must be bounded by `audit_limit`, from 1 through 100 inclusive.

The minimum projection may expose only the newest matching records up to the
limit while preserving their original append order.

A matching record must have exact equality for:

- `operator_reference`;
- `role_reference`;
- `target_type`;
- `target_reference`; and
- `action`.

The adapter must not query a repository, database, filesystem, network service,
cache, event stream, or hidden global state.

The adapter must not append, replace, update, delete, reorder, or repair audit
records.

## 10. Immutable SafeOperatorDashboardProjection

A future projection value must contain exactly these fields:

- `request_id`
- `operator_reference`
- `role_reference`
- `permission_reference`
- `target_type`
- `target_reference`
- `action`
- `assessment_outcome`
- `assessment_reason_code`
- `reason_reference`
- `audit_context_reference`
- `matching_audit_records`

`matching_audit_records` must be an immutable tuple of accepted
OperatorApprovalAuditRecord values.

The projection must copy facts exactly from accepted dependency outputs. It
must not normalize, enrich, summarize, rank, infer, or generate facts.

An `ELIGIBLE` projection requires an exact accepted allow evaluation and the
exact application-service assessment references.

A `DENIED` projection must not invent a permission reference or any optional
reference absent from the accepted assessment.

## 11. Immutable SafeOperatorDashboardResult

A future result value must contain exactly these fields:

- `status`
- `projection`
- `error_code`

`status` may be only:

- `READY`
- `DENIED`
- `INVALID`

`READY` requires a valid request, exact accepted allow evaluation, and an
`ELIGIBLE` application-service assessment.

`DENIED` requires a valid request and an accepted denied authority or approval
assessment.

`INVALID` covers malformed requests, identity disagreement, malformed
dependency output, unsupported vocabulary, dependency failure, and unexpected
exceptions.

`projection` is required for `READY` and may be present for `DENIED` only when
all represented facts are accepted and internally consistent.

`projection` must be absent for `INVALID`.

`error_code` must be absent for `READY` and must use the exact bounded
vocabulary defined below for all other statuses.

## 12. Exact deterministic error vocabulary

A future adapter may emit only these error codes:

- `REQUEST_INVALID`
- `ROLE_AUTHORITY_DENIED`
- `ROLE_AUTHORITY_RESULT_INVALID`
- `APPROVAL_ASSESSMENT_DENIED`
- `APPROVAL_ASSESSMENT_RESULT_INVALID`
- `AUDIT_HISTORY_INVALID`
- `DEPENDENCY_FAILURE`
- `INTERNAL_FAILURE`

No raw exception text, stack trace, filesystem path, credential, token,
network location, or storage detail may appear in the result.

Equivalent inputs and equivalent dependency outputs must produce equal result
values.

## 13. Fail-closed agreement checks

Before returning a projection, the adapter must verify exact agreement for:

- operator reference;
- role reference;
- target type;
- target reference;
- action;
- reason reference; and
- audit-context reference.

The exact permission reference returned by the accepted role-authority
evaluation must equal the permission reference represented by an eligible
approval assessment.

Any disagreement must return `INVALID` and no projection.

The adapter must not select the most permissive value, repair one side, or
silently discard a conflicting fact.

## 14. Purity and determinism

The future adapter implementation must be pure with respect to supplied
values.

It must not:

- read or write files;
- read or write environment variables;
- access a database;
- access a repository adapter or storage port;
- access the network;
- use a clock;
- use randomness;
- use process-global mutable state;
- spawn a process or background job;
- mutate an input object;
- mutate a target;
- execute an approval; or
- automatically promote any object.

The same valid inputs and dependency outputs must produce equal immutable
results.

## 15. Exact future implementation paths

This contract authorizes no implementation by itself.

A later separately reviewed materialization may use only:

- `src/rie/application/safe_operator_dashboard_adapter.py`
- `tests/application/test_safe_operator_dashboard_adapter.py`

No additional source, test, configuration, migration, frontend, persistence,
or infrastructure path is authorized by this contract.

## 16. Minimum future tests

A later separately authorized implementation must include focused tests for at
least:

1. valid request construction;
2. invalid text and audit-limit rejection;
3. exact role-authority allow delegation;
4. role-authority deny mapping;
5. malformed role-authority result rejection;
6. exact approval-assessment delegation;
7. eligible projection construction;
8. denied assessment mapping;
9. malformed approval-assessment result rejection;
10. exact permission-reference agreement;
11. exact operator, role, target, action, reason, and audit-context agreement;
12. bounded audit-history reads at limits 1 and 100;
13. invalid audit limits 0 and 101;
14. exact matching-record filtering;
15. append-order preservation;
16. no audit-history mutation;
17. deterministic dependency-failure mapping;
18. deterministic unexpected-exception mapping;
19. immutable request, projection, and result values;
20. no I/O, network, clock, randomness, persistence, or direct storage access;
21. no target lifecycle mutation;
22. no automatic promotion; and
23. no duplicate implementation outside the two exact future paths.

## 17. Acceptance boundary

This contract is accepted only when the materialized document proves all of
the following:

- one immutable request boundary;
- explicit accepted dependency delegation;
- one immutable projection boundary;
- one immutable result boundary;
- deterministic fail-closed status and error mapping;
- exact role, permission, target, action, reason, and audit-context agreement;
- bounded immutable audit-history visibility;
- no direct target mutation;
- no direct storage access;
- no persistence;
- no network, clock, randomness, or hidden global state;
- exact future source and test paths; and
- no implementation authorization from contract materialization alone.

## 18. Non-expansion boundary

This contract does not authorize:

- web frameworks;
- HTTP handlers or APIs;
- HTML, CSS, or JavaScript;
- desktop GUI frameworks;
- generalized UI abstractions;
- authentication providers;
- identity directories;
- credentials, tokens, cookies, or sessions;
- multi-user runtime;
- persistence or database work;
- repository adapters or storage ports;
- direct storage access;
- background jobs or event buses;
- network access;
- clocks or randomness;
- target lifecycle mutation;
- automatic promotion;
- semantic search, embeddings, vector databases, ontologies, knowledge graphs,
  OCR, inference, or generalized AI/model abstractions;
- Gate 17 generator integration; or
- Gate 18 production implementation.

## 19. Publication and implementation ordering

After independent acceptance, the only candidate next operation is publication
of this exact contract.

A later implementation gap review is required after publication.

Contract publication does not authorize implementation. Implementation does
not authorize a web interface, persistence, authentication, or production
deployment.

## 20. Closure statement

This contract closes only the minimum safe operator dashboard-adapter contract
gap selected by PR-076AE Correction 1.

Gate 16 remains active and is not closed. The next operation after independent
acceptance is limited to publishing this exact contract.
