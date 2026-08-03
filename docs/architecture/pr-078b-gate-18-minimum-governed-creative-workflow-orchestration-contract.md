# PR-078B Gate 18 Minimum Governed Creative Workflow Orchestration Contract

Version: 1.0
Status: Selected-gap architecture contract
Gate: 18
Phase candidate: 76

## 1. Purpose

This contract defines the minimum fail-closed orchestration boundary required
to move one governed creative request from an explicit brief context to an
approved creative asset reference without treating generation, external tool
output, operator review, or asset admission as the same authority.

The contract coordinates references and accepted service results. It does not
implement a generator, execute inference, persist workflow state, mutate an
asset lifecycle, create a user interface, deploy a service, or release RCIS v1.

## 2. Governing authority

This contract is governed by:

- the accepted Gate 14 Evidence and Knowledge boundaries;
- the accepted Gate 15 governed asset library, identity, rights, eligibility,
  exact-reference registry, and registry-backed evaluation boundaries;
- the accepted Gate 16 operator decision, role authority, application service,
  permission reconciliation, audit history, and safe dashboard boundaries;
- the accepted PR-078A Gate 18 initiation and reconciliation review;
- `RCIS_RIE_Roadmap_Alignment_v5_Gate13_Closure_and_Narrowed_RCIS_v1_Scope`;
  and
- the narrowed RCIS v1 requirement that automated generator execution is not a
  production-release dependency.

No lower-level implementation may broaden these authorities.

## 3. Mandatory authority separations

The following separations are mandatory:

- Source Material is not Extraction Result.
- Extraction Result is not Evidence.
- Evidence is not Knowledge.
- Knowledge is not a business decision.
- Prompt Candidate is not an approved instruction.
- Generated Output is not an Official Source.
- Generated Output is not an Accepted Asset.
- Generated Output is not an Approved Creative Asset.
- OperatorApprovalDecision is not lifecycle mutation.
- Role-authority evaluation is not executed approval.
- Application-service assessment is not persisted approval history.
- Audit-history record is not executed approval.
- Dashboard projection is not approval authorization.
- Dashboard projection is not target lifecycle mutation.
- Governed asset eligibility is not governed asset admission.
- Orchestration completion is not production release.

No automatic promotion is permitted across any of these boundaries.

## 4. Contract vocabulary

A future implementation may use the following contract-level concepts:

- `GovernedCreativeWorkflowRequest`: one immutable request envelope.
- `CreativeProjectContextReference`: one exact project boundary reference.
- `CreativeCampaignContextReference`: one exact campaign boundary reference.
- `CreativeBriefReference`: one exact brief or requirement reference.
- `ApprovedKnowledgeReference`: one accepted Knowledge reference.
- `GovernedAssetReference`: one exact Gate 15 governed asset reference.
- `InstructionReference`: either one Prompt Candidate reference or one approved
  instruction reference, with the authority state explicit.
- `ManualExternalToolHandoffRecord`: an optional immutable handoff record.
- `CreativeResultCandidate`: one generated or externally created result
  admitted only as a candidate.
- `CreativeWorkflowEvent`: one deterministic audit event envelope.
- `GovernedCreativeWorkflowResult`: one immutable orchestration result.

These names define architecture vocabulary only. They do not authorize source
code, persistence, transport, or user-interface implementation.

## 5. Exact request boundary

A conforming request must supply all required values explicitly:

1. one workflow request identity;
2. one idempotency key;
3. one project context reference;
4. one campaign context reference bound to that project;
5. one creative brief reference;
6. zero or more approved Knowledge references;
7. zero or more exact governed Asset references;
8. exactly one instruction reference;
9. one requesting actor reference;
10. one caller-supplied timezone-aware request timestamp;
11. one workflow contract name and version;
12. one requested output-purpose code;
13. one requested review-policy reference; and
14. an optional manual external-tool handoff declaration.

The orchestrator must not derive missing authority, context, timestamps,
identity values, approval state, rights state, or lifecycle state from ambient
process, filesystem, network, clock, random, model, or user-interface state.

## 6. Project and campaign isolation

Every request, event, candidate, review reference, and final result must carry
the same exact project and campaign context references.

A campaign context must be explicitly bound to its project context. References
from another project or campaign must fail closed even when their identifiers,
checksums, filenames, or human-readable labels appear similar.

No cross-project search, fallback, substitution, asset borrowing, Knowledge
borrowing, review reuse, or implicit campaign inheritance is permitted.

Project and campaign isolation must be verified before any instruction,
handoff, candidate, review, or asset-admission step is accepted.

## 7. Approved Knowledge and governed Asset inputs

Knowledge inputs may be used only through accepted Knowledge references. The
orchestrator must not reconstruct Knowledge from Source Material, extraction,
Evidence, free text, or generated output.

Asset inputs may be used only through exact Gate 15 governed Asset references.
For each referenced asset, the future implementation must require the accepted
identity, lifecycle, usage-rights, and use-eligibility evidence required by the
Gate 15 contracts.

The orchestrator must not:

- bypass the governed asset registry;
- read asset storage directly;
- infer rights or eligibility;
- silently replace an unavailable asset;
- promote an ineligible asset;
- mutate an asset record; or
- treat an asset reference as approval for a new creative result.

## 8. Instruction reference boundary

Exactly one instruction reference is required.

A Prompt Candidate reference must remain explicitly marked as a candidate. It
may not be treated as an approved instruction unless an accepted authority
surface separately proves the approved state.

An approved instruction reference must preserve:

- its exact identity;
- its exact version or revision;
- its approval authority reference;
- its project and campaign context;
- its permitted output purpose; and
- its immutable content checksum or equivalent exact-content binding.

The orchestrator may coordinate an instruction reference but must not author,
rewrite, approve, infer, expand, or optimize instruction content.

## 9. Optional manual external-tool handoff

Manual external-tool handoff is optional. RCIS v1 completion must not depend on
an automated generator connector or local model runtime.

When a handoff is included, the handoff record must contain:

- one exact handoff identity;
- the workflow, project, campaign, brief, and instruction references;
- the exporting actor;
- a caller-supplied timezone-aware export timestamp;
- the declared external tool or tool-family label;
- the exact exported package checksum or equivalent content binding;
- the permitted output-purpose code;
- an explicit statement that execution occurs outside RCIS; and
- no credentials, session tokens, hidden prompts, model runtime controls, or
  automatic callback instructions.

The handoff record is evidence of a manual boundary only. It is not evidence
that the external tool executed correctly, that an output is safe, that an
output is approved, or that an output may enter the governed asset library.

## 10. Creative result candidate admission

Every generated or externally created result must enter RCIS only as one
`CreativeResultCandidate`.

Candidate admission must require:

- one exact candidate identity;
- the workflow, project, campaign, brief, and instruction references;
- the originating handoff reference when a manual handoff was used;
- an exact candidate content checksum or equivalent immutable binding;
- a declared media or artifact type;
- a caller-supplied timezone-aware admission timestamp;
- the admitting actor reference;
- deterministic provenance fields;
- an explicit `CANDIDATE` authority state; and
- confirmation that no official-source, accepted-asset, or approved-asset state
  has been assigned.

Candidate admission must fail closed for missing provenance, cross-context
references, unsupported artifact type, checksum mismatch, ambiguous authority,
or attempted automatic promotion.

## 11. Operator review through Gate 16

Operator review must occur only through accepted Gate 16 authority and
application-service surfaces.

The orchestration boundary may consume an accepted Gate 16 assessment and
decision reference. It must not:

- execute approval directly;
- bypass role-authority evaluation;
- bypass permission-reference reconciliation;
- treat dashboard projection as authorization;
- synthesize an OperatorApprovalDecision;
- alter persisted approval history;
- mutate the candidate or asset lifecycle; or
- reinterpret a rejected or safe-stop decision.

An accepted operator decision remains a business decision record. It is not by
itself a governed asset admission or lifecycle transition.

## 12. Governed asset admission through Gate 15

A reviewed candidate may be presented for governed asset admission only
through accepted Gate 15 boundaries.

The orchestration boundary may consume the resulting accepted governed asset
reference only when all required identity, rights, lifecycle, exact-reference,
and registry-backed eligibility conditions are satisfied.

The orchestrator must not create a parallel asset registry, write directly to
storage, assign rights, infer eligibility, bypass exact references, or perform
automatic lifecycle mutation.

An orchestration result may state that an accepted governed asset reference was
returned. It must not claim that orchestration itself admitted or approved the
asset.

## 13. Deterministic workflow states

The minimum workflow-state vocabulary is:

- `REQUESTED`
- `INPUTS_VALIDATED`
- `INSTRUCTION_READY`
- `EXTERNAL_HANDOFF_RECORDED`
- `CANDIDATE_PENDING`
- `CANDIDATE_ADMITTED`
- `OPERATOR_REVIEW_PENDING`
- `OPERATOR_DECISION_RECORDED`
- `ASSET_ADMISSION_PENDING`
- `GOVERNED_ASSET_REFERENCE_RECORDED`
- `COMPLETED`
- `REJECTED`
- `SAFE_STOP`

`EXTERNAL_HANDOFF_RECORDED` is optional and may be skipped when no manual
handoff is included.

A transition is valid only when its exact predecessor state, required evidence
references, project and campaign context, idempotency key, and authority
preconditions are present.

`COMPLETED` means that the orchestration result contains the accepted references
required by this contract. It does not mean production release, target
promotion, deployment, publication, or storage mutation.

## 14. Idempotency and replay

The idempotency key must be unique within one exact project and campaign
context.

Repeated requests with the same idempotency key and identical canonical inputs
must return the same workflow identity and deterministic result references.

The same idempotency key with different canonical inputs must fail closed with
`IDEMPOTENCY_CONFLICT`.

Replay must not duplicate:

- external handoff records;
- candidate admission records;
- operator decision references;
- audit events;
- governed asset admission requests; or
- final result references.

The contract defines idempotency behavior only. It does not authorize a
database, repository adapter, cache, queue, or background job.

## 15. Audit event boundary

Each accepted transition must define one immutable `CreativeWorkflowEvent`
containing:

- one deterministic event identity;
- the workflow identity and idempotency key;
- the exact prior and resulting workflow states;
- project, campaign, brief, and instruction references;
- the actor or accepted service reference responsible for the transition;
- a caller-supplied timezone-aware event timestamp;
- the exact evidence references required by the transition;
- deterministic reason codes;
- the contract name and version; and
- no secret, credential, binary asset content, or mutable object reference.

An audit event records that a transition was accepted by the orchestration
contract. It is not an executed approval, asset admission, lifecycle mutation,
or production-release event.

## 16. Recovery boundary

Recovery must be explicit, deterministic, and evidence-backed.

A recovery request must supply:

- the workflow identity;
- the idempotency key;
- the last accepted workflow state;
- the exact last accepted audit event reference;
- all required context and evidence references; and
- one recovery reason code.

Recovery may resume only from the last independently verifiable accepted state.
It must not skip operator review, asset eligibility, asset admission, audit, or
context validation.

Any ambiguous, conflicting, missing, or future-state recovery evidence must
produce `SAFE_STOP`.

This contract does not execute backup, restore, disaster recovery, deployment,
or production-environment recovery.

## 17. Result contract

A future implementation may return only one immutable
`GovernedCreativeWorkflowResult` containing:

- the workflow identity;
- the idempotency key;
- project, campaign, brief, and instruction references;
- the final workflow state;
- the last accepted audit event reference;
- the manual handoff reference or `None`;
- the creative result candidate reference or `None`;
- the accepted operator decision reference or `None`;
- the accepted governed asset reference or `None`;
- deterministic reason codes; and
- deterministic diagnostics.

`COMPLETED` requires an accepted operator decision reference and an accepted
governed asset reference that both preserve the exact workflow context.

`REJECTED` and `SAFE_STOP` must not fabricate missing downstream references.

## 18. Deterministic error vocabulary

The minimum error and safe-stop vocabulary is:

- `INVALID_REQUEST`
- `PROJECT_CONTEXT_MISMATCH`
- `CAMPAIGN_CONTEXT_MISMATCH`
- `BRIEF_REFERENCE_INVALID`
- `KNOWLEDGE_REFERENCE_INVALID`
- `ASSET_REFERENCE_INVALID`
- `ASSET_RIGHTS_OR_ELIGIBILITY_INVALID`
- `INSTRUCTION_REFERENCE_INVALID`
- `HANDOFF_RECORD_INVALID`
- `CANDIDATE_PROVENANCE_INVALID`
- `CANDIDATE_AUTHORITY_INVALID`
- `OPERATOR_REVIEW_REQUIRED`
- `OPERATOR_DECISION_REJECTED`
- `OPERATOR_AUTHORITY_INVALID`
- `ASSET_ADMISSION_REQUIRED`
- `ASSET_ADMISSION_REJECTED`
- `IDEMPOTENCY_CONFLICT`
- `INVALID_STATE_TRANSITION`
- `AUDIT_EVENT_INVALID`
- `RECOVERY_EVIDENCE_INVALID`
- `AUTHORITY_BYPASS_ATTEMPT`
- `PROHIBITED_AUTOMATION_ATTEMPT`
- `SAFE_STOP_REQUIRED`

Reason-code ordering must be deterministic. Unknown conditions must fail closed
as `SAFE_STOP_REQUIRED`.

## 19. Fail-closed conditions

The future implementation must reject or safe-stop for at least:

1. missing or invalid request identity or idempotency key;
2. project or campaign mismatch;
3. invalid brief, Knowledge, Asset, or instruction reference;
4. missing or invalid asset rights or eligibility evidence;
5. unsupported instruction authority state;
6. malformed manual handoff evidence;
7. candidate checksum or provenance mismatch;
8. candidate represented as official, accepted, or approved before acceptance;
9. missing Gate 16 review or authority evidence;
10. rejected, conflicting, or ambiguous Gate 16 decision evidence;
11. missing Gate 15 admission evidence;
12. rejected, conflicting, or ambiguous Gate 15 evidence;
13. invalid state transition;
14. idempotency conflict or duplicate side-effect attempt;
15. invalid audit or recovery evidence;
16. cross-project or cross-campaign reference reuse;
17. direct storage, persistence, lifecycle, or approval bypass attempt;
18. automatic generator, inference, model, or callback attempt;
19. automatic promotion or target lifecycle mutation attempt; and
20. partial downstream result represented as completed.

No partial result may be promoted to `COMPLETED`.

## 20. Determinism and side-effect boundary

A future minimum orchestration implementation must be deterministic for
identical explicit inputs and accepted service results.

The orchestration domain calculation must be free of:

- filesystem discovery;
- direct asset-file access;
- network discovery;
- ambient clock access;
- randomness;
- model or generator execution;
- OCR, embeddings, semantic search, ontology, or knowledge-graph inference;
- database or persistence side effects;
- background jobs;
- automatic approval;
- automatic promotion;
- direct lifecycle mutation;
- deployment; and
- production release.

Any required timestamps, identities, references, and external results must be
supplied explicitly by callers or accepted service boundaries.

## 21. Existing accepted surfaces protected from modification

This contract protects the following accepted Gate 15 and Gate 16 surfaces
from modification by its initial materialization:

- `src/rie/domain/governed_asset_record.py`
- `src/rie/domain/governed_asset_usage_rights.py`
- `src/rie/domain/governed_asset_use_eligibility.py`
- `src/rie/domain/governed_asset_library_registry.py`
- `src/rie/domain/evaluate_governed_asset_library_use_eligibility.py`
- `src/rie/domain/operator_approval_decision.py`
- `src/rie/domain/operator_role_authority.py`
- `src/rie/domain/operator_approval_audit_history.py`
- `src/rie/application/operator_approval_application_service.py`
- `src/rie/application/safe_operator_dashboard_adapter.py`

Their matching tests and accepted architecture contracts are also protected.
A later exact review must authorize any compatibility change.

## 22. Explicitly out of scope

This contract does not authorize:

- an automated local or cloud generator connector;
- model runtime, inference, GPU management, or generalized orchestration;
- prompt generation, prompt rewriting, or automatic prompt approval;
- OCR, embeddings, vector database, semantic search, ontology, knowledge graph,
  or automated inference;
- a web, desktop, mobile, dashboard, or operator user interface;
- authentication provider, session runtime, identity directory, or multi-user
  runtime;
- database, persistence, repository adapter, cache, queue, or background job;
- direct storage access;
- target lifecycle mutation or automatic promotion;
- real-asset scanning or external-tool execution;
- backup or restore execution;
- deployment or monitoring configuration;
- production release;
- Gate 17 implementation;
- Phase 76 branch or tag creation;
- source, test, configuration, or migration implementation; or
- modification of any existing repository path.

Only the single canonical architecture contract path selected by PR-078A may
be created by PR-078B.

## 23. Future implementation boundary review

This architecture contract does not authorize runtime implementation.

A later read-only boundary review must independently determine:

- the minimum new source path or paths;
- the minimum new test path or paths;
- whether one implementation document is necessary;
- the exact request, event, candidate, and result types;
- the exact existing Gate 15 and Gate 16 imports permitted;
- the canonical identity and idempotency inputs;
- the exact pure transition function boundary;
- the exact optional manual-handoff record boundary;
- the synthetic test matrix;
- the targeted test command;
- the protected-path list;
- the no-persistence and no-generator proofs; and
- the exact next operation.

Until that review is independently accepted, only this one architecture
contract may be materialized.
