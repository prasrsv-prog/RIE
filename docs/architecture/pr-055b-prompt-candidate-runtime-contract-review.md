# PR-055B - Prompt Candidate Runtime Contract Review

## 1. Review identity

Gate: `Gate 10 - Prompt Candidate`

Phase: `Phase 55 - Prompt Candidate`

Repository checkpoint: `b15e24f8728232dffafbb7214c45295b82857124`

Branch: `phase-055-prompt-candidate`

Selected minimum closure boundary:

`caller_supplied_exact_governed_knowledge_revision_and_explicit_prompt_intent_to_deterministic_provenance_bearing_immutable_structural_prompt_candidate`

This is an architecture-only and documentation-only runtime contract review.

This review creates no production code, test code, package export, configuration,
CLI, provider integration, prompt execution path, repository mutation, merge,
tag, publication, gate closure, or Gate 11 work.

## 2. Selected runtime contract

Selected runtime contract:

`caller_supplied_exact_gate_9_revision_lookup_result_and_explicit_prompt_intent_to_deterministic_immutable_provenance_bearing_structural_prompt_candidate_construction_runtime_contract`

The runtime accepts one caller-supplied exact Gate 9 revision lookup result,
one caller-supplied explicit immutable prompt intent, one supported prompt
candidate schema identity and version, and one supported construction policy
identity and version.

The runtime returns one deterministic construction result containing either one
immutable structural prompt candidate or one deterministic issue.

The runtime does not access the Gate 9 repository. The caller must perform an
exact revision lookup before invoking Gate 10.

## 3. Public callable boundary

The exact public callable boundary is:

`construct_prompt_candidate(request: PromptCandidateConstructionRequest) -> PromptCandidateConstructionResult`

No repository protocol, provider protocol, model protocol, tokenizer protocol,
renderer protocol, filesystem protocol, clock protocol, or network protocol is
part of this runtime contract.

## 4. Contract identities and versions

- request contract: `prompt_candidate_construction_request_contract_v1`
- prompt intent contract: `prompt_intent_contract_v1`
- provenance contract: `prompt_candidate_provenance_contract_v1`
- prompt candidate contract: `prompt_candidate_contract_v1`
- construction result contract: `prompt_candidate_construction_result_contract_v1`
- issue contract: `prompt_candidate_issue_contract_v1`
- supported candidate schema ID: `rcis.prompt_candidate.structural`
- supported candidate schema version: `1.0.0`
- construction policy ID: `rcis-prompt-candidate-construction`
- construction policy version: `1.0.0`
- digest algorithm: `sha256`
- prompt intent ID prefix: `pi1_`
- provenance ID prefix: `pcp1_`
- prompt candidate ID prefix: `pc1_`

Unsupported contract versions, schema identities, schema versions, policy
identities, and policy versions are rejected. There is no compatibility
fallback and no implicit upgrade.

## 5. Immutable request contract

### PromptCandidateConstructionRequest

Field count: `7`.

- `contract_version`
- `source_revision_lookup_result`
- `prompt_intent`
- `prompt_candidate_schema_id`
- `prompt_candidate_schema_version`
- `construction_policy_id`
- `construction_policy_version`

The request is immutable.

`source_revision_lookup_result` must be one exact Gate 9
`KnowledgeRepositoryLookupResult` using
`knowledge_repository_lookup_result_contract_v1`.

The accepted lookup result must have status `found`. It must have been obtained
by the caller through either an exact `revision_id` lookup or an exact
`governed_knowledge_id` plus `revision_number` lookup.

Gate 10 does not receive, request, infer, or resolve an implicit latest or
current revision.

## 6. Explicit prompt intent contract

### PromptIntent

Field count: `8`.

- `contract_version`
- `intent_id`
- `objective`
- `audience`
- `language`
- `output_format`
- `required_constraints`
- `forbidden_constraints`

`objective` is required and must contain at least one non-whitespace code point.

`audience`, `language`, and `output_format` are nullable. When present, each
must contain at least one non-whitespace code point.

`required_constraints` and `forbidden_constraints` are immutable ordered
tuples of exact strings. Every item must contain at least one non-whitespace
code point. Exact duplicate items within one tuple are rejected. An exact item
must not occur in both tuples.

Tuple order is caller authority and is preserved. The runtime performs no
sorting, trimming, case folding, Unicode normalization, paraphrasing,
summarization, expansion, intent inference, or hidden conversation lookup.

The prompt intent identity projection contains all PromptIntent fields except
`intent_id`.

`intent_id` is:

`pi1_` plus the lowercase SHA-256 hex digest of the canonical prompt intent
identity projection.

## 7. Exact Gate 9 source revision contract

The runtime reuses these committed Gate 9 public contracts without changing
their semantics:

- `knowledge_repository_lookup_result_contract_v1`
- `knowledge_repository_revision_contract_v1`
- `knowledge_repository_lineage_record_contract_v1`
- `knowledge_repository_audit_record_contract_v1`

The exact source lookup result must contain:

- status `found`;
- one non-null revision;
- one non-null lineage record;
- one non-null audit record;
- one non-null GovernedKnowledge value;
- one non-null lifecycle interpretation result;
- no issue.

The runtime validates that:

1. the revision ID is internally valid;
2. the revision governed-knowledge ID equals the GovernedKnowledge ID;
3. the revision number is a positive exact integer;
4. the revision governed-knowledge payload digest matches the exact
   GovernedKnowledge value;
5. the revision lineage-record ID equals the supplied lineage-record ID;
6. the lineage record is for the same GovernedKnowledge;
7. the revision audit ID equals the supplied audit-record ID;
8. the audit record is for the same revision and GovernedKnowledge;
9. the revision lifecycle interpretation result ID equals the supplied
   lifecycle interpretation result ID;
10. all nested Gate 9 values satisfy their own committed contracts.

Gate 10 does not repair, reinterpret, transition, append, persist, or select the
source revision.

## 8. Provenance contract

### PromptCandidateProvenance

Field count: `16`.

- `contract_version`
- `provenance_id`
- `source_lookup_result_contract_version`
- `source_revision_id`
- `source_governed_knowledge_id`
- `source_revision_number`
- `source_governed_knowledge_payload_digest`
- `source_lineage_record_id`
- `source_audit_id`
- `source_lifecycle_interpretation_result_id`
- `prompt_intent_id`
- `prompt_intent_digest`
- `prompt_candidate_schema_id`
- `prompt_candidate_schema_version`
- `construction_policy_id`
- `construction_policy_version`

Every source field is copied from the validated exact Gate 9 lookup result.
Every prompt intent field is copied from the validated PromptIntent.

The provenance identity projection contains all provenance fields except
`provenance_id`.

`provenance_id` is:

`pcp1_` plus the lowercase SHA-256 hex digest of the canonical provenance
identity projection.

## 9. Structural prompt candidate contract

### PromptCandidate

Field count: `12`.

- `contract_version`
- `candidate_id`
- `prompt_candidate_schema_id`
- `prompt_candidate_schema_version`
- `construction_policy_id`
- `construction_policy_version`
- `prompt_intent`
- `source_revision`
- `governed_knowledge`
- `lifecycle_interpretation_result`
- `provenance`
- `candidate_payload_digest`

The candidate is an immutable typed structural envelope. It is not provider
prompt text, a chat message list, a rendered template, a token sequence, a
model request, or final creative output.

The candidate preserves the exact PromptIntent, the exact Gate 9 revision
record, the exact GovernedKnowledge value, the exact lifecycle interpretation
result, and the derived provenance record.

No field is populated from current time, environment variables, process state,
filesystem state, network state, model output, hidden memory, or an implicit
repository lookup.

## 10. Construction result and status vocabulary

### PromptCandidateConstructionResult

Field count: `4`.

- `contract_version`
- `status`
- `prompt_candidate`
- `issue`

Supported status count: `2`.

- `constructed`
- `rejected`

For `constructed`, `prompt_candidate` is non-null and `issue` is null.

For `rejected`, `prompt_candidate` is null and `issue` is non-null.

No partial prompt candidate is returned.

There is no `unchanged_exact_replay` status because this runtime performs no
persistence or mutation.

## 11. Issue contract and vocabulary

### PromptCandidateIssue

Field count: `2`.

- `code`
- `message`

Supported issue code count: `30`.

1. `invalid_request`
2. `unsupported_request_contract_version`
3. `unsupported_prompt_candidate_schema`
4. `unsupported_prompt_candidate_schema_version`
5. `unsupported_construction_policy`
6. `unsupported_construction_policy_version`
7. `invalid_prompt_intent`
8. `unsupported_prompt_intent_contract_version`
9. `invalid_prompt_intent_field`
10. `prompt_intent_id_mismatch`
11. `invalid_source_revision_lookup_result`
12. `unsupported_source_lookup_result_contract_version`
13. `source_revision_not_found`
14. `source_revision_lookup_rejected`
15. `missing_source_revision`
16. `invalid_source_revision`
17. `source_revision_identity_mismatch`
18. `missing_source_governed_knowledge`
19. `source_governed_knowledge_identity_mismatch`
20. `source_revision_payload_digest_mismatch`
21. `missing_source_lifecycle_interpretation_result`
22. `source_lifecycle_interpretation_result_mismatch`
23. `missing_source_lineage_record`
24. `source_lineage_mismatch`
25. `missing_source_audit_record`
26. `source_audit_mismatch`
27. `provenance_identity_mismatch`
28. `candidate_payload_digest_mismatch`
29. `candidate_identity_mismatch`
30. `internal_contract_violation`

Only the first deterministic validation failure is exposed.

Issue codes are stable public semantics. Issue messages are deterministic
human-readable explanations and must not contain environment-dependent data.

## 12. Canonicalization rules

Canonicalization contracts:

- prompt intent identity: `prompt_intent_identity_json_v1`
- provenance identity: `prompt_candidate_provenance_identity_json_v1`
- candidate payload: `prompt_candidate_payload_json_v1`
- candidate identity: `prompt_candidate_identity_json_v1`

Each canonical representation uses these exact rules:

1. JSON object keys are sorted by ordinal code-point order;
2. no insignificant whitespace is emitted;
3. arrays preserve caller-supplied order;
4. strings preserve exact code points and are not normalized;
5. all non-ASCII code points are emitted as lowercase `\uXXXX` JSON escapes,
   using surrogate pairs when required;
6. solidus characters are not escaped;
7. control characters use the shortest required JSON escape;
8. integers use base-10 form without leading zeros;
9. floating-point values, NaN, infinity, bytes, sets, and unordered mappings are
   rejected;
10. booleans are `true` or `false`, and null is `null`;
11. duplicate object keys are impossible in the typed contracts and rejected
    during any boundary decoding;
12. canonical text is encoded as UTF-8 and hashed with SHA-256.

Gate 9 nested values retain their committed field semantics. Gate 10
canonicalization serializes their public immutable value projections and does
not inspect private implementation state.

## 13. Deterministic identity derivation

`prompt_intent_digest` is the SHA-256 digest of the canonical PromptIntent
identity projection.

`candidate_payload_digest` is the SHA-256 digest of a canonical projection
containing:

- prompt candidate contract version;
- schema ID and version;
- construction policy ID and version;
- exact PromptIntent;
- exact source revision;
- exact GovernedKnowledge;
- exact lifecycle interpretation result;
- exact provenance.

The candidate payload projection excludes `candidate_id` and
`candidate_payload_digest`.

The prompt candidate identity projection contains:

- prompt candidate contract version;
- schema ID and version;
- construction policy ID and version;
- source revision ID;
- prompt intent ID;
- provenance ID;
- candidate payload digest.

`candidate_id` is:

`pc1_` plus the lowercase SHA-256 hex digest of the canonical candidate
identity projection.

The derivation graph is non-cyclic:

1. validate source revision and PromptIntent values;
2. derive prompt intent digest and ID;
3. derive provenance and provenance ID;
4. derive candidate payload digest;
5. derive candidate ID;
6. construct the result wrapper.

## 14. Validation ordering

Validation order is fixed:

1. request type and request contract version;
2. candidate schema ID and version;
3. construction policy ID and version;
4. PromptIntent type, contract version, fields, and identity;
5. source lookup-result type, contract version, and status;
6. source revision presence and revision invariants;
7. GovernedKnowledge presence, identity, and payload digest;
8. lifecycle interpretation result presence and revision linkage;
9. lineage record presence and linkage;
10. audit record presence and linkage;
11. provenance projection and identity;
12. candidate payload canonicalization and digest;
13. candidate identity;
14. construction-result invariant.

Validation stops at the first failure. Later validation stages do not run after
an earlier failure.

## 15. Determinism and replay

The same valid immutable request under the same supported contract versions
produces an equal PromptCandidateConstructionResult, equal PromptCandidate,
equal provenance, equal digests, equal IDs, and byte-identical canonical
representations.

The same invalid immutable request produces the same `rejected` status and the
same first issue code.

The runtime uses no clock, random source, filesystem, database, repository
call, network call, retry loop, global mutable state, environment-dependent
normalization, model invocation, provider service, tokenizer, or hidden
conversation context.

## 16. Forbidden dependencies and side effects

The runtime contract forbids:

- Gate 9 repository reads or writes;
- implicit latest or current revision selection;
- lifecycle transition creation or persistence;
- Gate 8 KnowledgeCandidate reconstruction;
- authority, conflict, promotion, or acceptance re-evaluation;
- hidden intent inference or conversation-memory access;
- prompt execution, model invocation, provider selection, or provider fallback;
- provider-specific message rendering or token budgeting;
- filesystem reads or writes;
- network access;
- current-clock or random input;
- mutable global caches;
- logging that changes result semantics;
- CLI command construction;
- package or release behavior;
- real RSV production data admission;
- Gate 11 invocation.

## 17. Success and failure semantics

A successful construction means only that one exact Gate 9 revision and one
explicit PromptIntent were validated and bound into one deterministic,
immutable, provenance-bearing structural PromptCandidate.

Success does not mean the prompt candidate is executed, optimized, approved,
published, or suitable for a specific model provider.

A rejected result performs no side effect and returns no partial candidate.

Programming defects that violate an already-validated internal invariant map
to `internal_contract_violation`; they do not authorize fallback behavior.

## 18. Scope decision

Gate 10 minimum closure boundary selected: `True`.

Gate 10 minimum closure boundary committed: `True`.

Gate 10 runtime contract selected: `True`.

Gate 10 runtime contract committed: `False`.

Gate 10 implementation boundary selected: `False`.

Gate 10 implementation authorized: `False`.

Gate 10 implementation started: `False`.

Gate 10 closed: `False`.

Gate 11 invoked: `False`.

No semantic blocker requiring work outside this Gate 10 contract is proven.

The next eligible architecture subject after accepted PR-055B commit and
post-commit verification is:

`prompt_candidate_implementation_boundary_review`

This review does not assign implementation paths, create tests, implement the
callable, stage, commit, push, merge, tag, publish, close Gate 10, or invoke
Gate 11.
