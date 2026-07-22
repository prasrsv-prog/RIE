# PR-055C - Prompt Candidate Implementation Boundary Review

## 1. Review identity

Gate: `Gate 10 - Prompt Candidate`

Phase: `Phase 55 - Prompt Candidate`

Repository checkpoint: `6640db29b49cab770e1851f564c3aab3e2634064`

Branch: `phase-055-prompt-candidate`

Selected minimum closure boundary: `caller_supplied_exact_governed_knowledge_revision_and_explicit_prompt_intent_to_deterministic_provenance_bearing_immutable_structural_prompt_candidate`

Selected runtime contract: `caller_supplied_exact_gate_9_revision_lookup_result_and_explicit_prompt_intent_to_deterministic_immutable_provenance_bearing_structural_prompt_candidate_construction_runtime_contract`

This is an architecture-only and documentation-only implementation-boundary review.

It creates no production code, test code, package export, configuration, CLI, model integration, prompt execution, repository mutation, merge, tag, publication, gate closure, or Gate 11 work.

## 2. Selected implementation boundary

Selected implementation boundary: `eight_file_isolated_prompt_candidate_contract_canonicalization_service_public_api_and_boundary_test_implementation`

The future implementation is restricted to one new isolated `rie.prompt_candidate` namespace with four production files and four directly corresponding test files.

No existing source, test, initializer, configuration, documentation, or dependency declaration may be modified by the implementation.

The selection contains no repository protocol, storage backend, renderer, tokenizer, model provider, CLI adapter, or compatibility facade.

## 3. Exact production path scope

Production path count: `4`.

1. `src/rie/prompt_candidate/__init__.py`
2. `src/rie/prompt_candidate/prompt_candidate_contract.py`
3. `src/rie/prompt_candidate/prompt_candidate_canonicalization.py`
4. `src/rie/prompt_candidate/prompt_candidate_service.py`

All four production paths are new.

### Module responsibilities

- `__init__.py` re-exports exactly the selected public package API and performs no work.
- `prompt_candidate_contract.py` owns the six immutable dataclasses, contract constants, status constants, issue vocabulary, fixed issue messages, and strict object invariants.
- `prompt_candidate_canonicalization.py` owns deterministic canonical JSON projections, SHA-256 digests, prompt-intent identity, provenance identity, candidate payload identity, and candidate identity.
- `prompt_candidate_service.py` owns the single runtime workflow callable `construct_prompt_candidate` and the exact first-failure validation order.

## 4. Exact test path scope

Test path count: `4`.

1. `tests/test_prompt_candidate_contract.py`
2. `tests/test_prompt_candidate_canonicalization.py`
3. `tests/test_prompt_candidate_service.py`
4. `tests/test_prompt_candidate_public_api.py`

All four test paths are new.

Total implementation path count: `8`.

Any implementation path outside these eight paths is unauthorized.

## 5. Exact public package API

Public class count: `6`.

- class `PromptCandidateConstructionRequest`
- class `PromptIntent`
- class `PromptCandidateProvenance`
- class `PromptCandidate`
- class `PromptCandidateConstructionResult`
- class `PromptCandidateIssue`

Public function count: `10`.

- function `canonicalize_prompt_intent_identity`
- function `derive_prompt_intent_digest`
- function `derive_prompt_intent_id`
- function `canonicalize_prompt_candidate_provenance_identity`
- function `derive_prompt_candidate_provenance_id`
- function `canonicalize_prompt_candidate_payload`
- function `derive_prompt_candidate_payload_digest`
- function `canonicalize_prompt_candidate_identity`
- function `derive_prompt_candidate_id`
- function `construct_prompt_candidate`

Public constant count: `21`.

- constant `PROMPT_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION`
- constant `PROMPT_INTENT_CONTRACT_VERSION`
- constant `PROMPT_CANDIDATE_PROVENANCE_CONTRACT_VERSION`
- constant `PROMPT_CANDIDATE_CONTRACT_VERSION`
- constant `PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION`
- constant `PROMPT_CANDIDATE_ISSUE_CONTRACT_VERSION`
- constant `PROMPT_CANDIDATE_SCHEMA_ID`
- constant `PROMPT_CANDIDATE_SCHEMA_VERSION`
- constant `PROMPT_CANDIDATE_CONSTRUCTION_POLICY_ID`
- constant `PROMPT_CANDIDATE_CONSTRUCTION_POLICY_VERSION`
- constant `PROMPT_CANDIDATE_DIGEST_ALGORITHM`
- constant `PROMPT_INTENT_IDENTITY_CANONICALIZATION_VERSION`
- constant `PROMPT_CANDIDATE_PROVENANCE_IDENTITY_CANONICALIZATION_VERSION`
- constant `PROMPT_CANDIDATE_PAYLOAD_CANONICALIZATION_VERSION`
- constant `PROMPT_CANDIDATE_IDENTITY_CANONICALIZATION_VERSION`
- constant `PROMPT_INTENT_ID_PREFIX`
- constant `PROMPT_CANDIDATE_PROVENANCE_ID_PREFIX`
- constant `PROMPT_CANDIDATE_ID_PREFIX`
- constant `PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED`
- constant `PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED`
- constant `PROMPT_CANDIDATE_ISSUE_CODES`

Total exact public package symbol count: `37`.

No other public symbol may be exported by `rie.prompt_candidate`.

The nine canonicalization and identity helpers are deterministic value utilities. The only public workflow entrypoint remains `construct_prompt_candidate`.

## 6. Exact callable boundary

`construct_prompt_candidate(request: PromptCandidateConstructionRequest) -> PromptCandidateConstructionResult`

The callable accepts one already-resolved exact Gate 9 `KnowledgeRepositoryLookupResult` and one explicit immutable `PromptIntent` inside the reviewed request.

The callable does not receive a repository, database connection, provider, model, tokenizer, renderer, filesystem path, clock, random source, conversation object, or callback.

## 7. Upstream dependency boundary

Allowed production dependencies are Python standard-library value-processing modules plus the exact committed Gate 9 public immutable contracts and pure identity or payload-verification helpers needed to verify the supplied lookup result.

The implementation may consume `KnowledgeRepositoryLookupResult`, `KnowledgeRepositoryRevision`, `KnowledgeRepositoryLineageRecord`, `KnowledgeRepositoryAuditRecord`, and the pure governed-knowledge repository payload-digest helper.

Nested `GovernedKnowledge` and structural lifecycle interpretation-result values retain their existing public immutable semantics. Existing pure identity helpers may be imported only to verify those exact values.

No application workflow entrypoint may be called. No Gate 9 repository protocol or concrete backend may be imported or instantiated.

Forbidden production import or call names include:

- `GovernedKnowledgeRepository`
- `SqliteGovernedKnowledgeRepository`
- `persist_initial`
- `append_lifecycle_transition`
- `get_by_revision_id`
- `get_by_governed_knowledge_revision`
- `list_governed_knowledge_history`
- `construct_knowledge_from_persisted_evidence`
- `construct_knowledge_candidate`
- `construct_governed_knowledge`
- `decide_governed_knowledge_acceptance`
- `govern_knowledge_candidate`
- `assess_knowledge_candidate_conflict`
- `decide_knowledge_authority`
- `evaluate_knowledge_promotion_prerequisite`
- `decide_knowledge_promotion`
- `record_knowledge_promotion_execution`
- `interpret_governed_knowledge_lifecycle_assertion_premise_structurally`
- `sqlite3`
- `requests`
- `urllib`
- `socket`
- `subprocess`
- `pathlib`
- `os`
- `time`
- `random`
- `uuid`
- `logging`

No new third-party dependency and no `pyproject.toml` modification are permitted.

## 8. Canonicalization and identity implementation boundary

The implementation must preserve the four PR-055B canonicalization contracts:

- `prompt_intent_identity_json_v1`
- `prompt_candidate_provenance_identity_json_v1`
- `prompt_candidate_payload_json_v1`
- `prompt_candidate_identity_json_v1`

Canonicalization uses compact deterministic JSON, sorted object keys, preserved caller tuple order, exact strings, lowercase non-ASCII escapes, surrogate pairs when required, UTF-8 bytes, and SHA-256.

The implementation must reject floating-point values, NaN, infinity, bytes, sets, unordered caller mappings, duplicate decoded keys, and unsupported value shapes.

Identity derivation remains non-cyclic: prompt intent, provenance, candidate payload, then candidate identity.

No canonical representation includes current time, environment text, filesystem paths, database state, network output, model output, or process state.

## 9. Contract and validation boundary

The implementation must realize exactly the six PR-055B immutable contracts and all thirty issue codes without adding an alternate status, compatibility fallback, partial candidate, warning-only success, or exception-based public failure path.

Validation order remains exactly:
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

Only the first deterministic issue is returned.

## 10. Immutability, determinism, and replay

All six public records are frozen immutable values.

The same valid immutable request must return equal result, candidate, provenance, digests, IDs, and byte-identical canonical representations.

The same invalid immutable request must return the same `rejected` status and first issue code.

No persistence occurs, so there is no `unchanged_exact_replay` status and no replay mutation.

The service must not mutate the supplied lookup result, revision, lineage, audit, governed knowledge, lifecycle interpretation result, PromptIntent, or constraint tuples.

## 11. Exact test boundary

The four selected test modules must cover:

- frozen dataclass shape, exact contract versions, exact statuses, issue-code order, fixed messages, strict type checks, tuple preservation, and immutability;
- canonical JSON fixed vectors, lowercase Unicode escapes, surrogate pairs, caller-order preservation, rejected float and unordered values, SHA-256 digests, non-cyclic identities, and byte-identical replay;
- successful exact Gate 9 lookup construction, exact nested-value copying, all fourteen validation stages, first-issue precedence, malformed and mismatched source values, exact provenance, exact candidate identity, and deterministic rejection;
- exact package __all__, exact public symbol set, no existing-module re-export, no repository/backend/model/provider/CLI dependency, no filesystem/network/clock/random side effect, and no Gate 11 surface;

Implementation execution must use one targeted pytest process covering the four new test modules and the existing Gate 9 public-boundary test that forbids upstream imports of the new namespace.

After targeted success, one full regression pytest process is required.

No automatic retry is permitted. Any failure must stop and produce a fresh correction report.

## 12. Static layer boundary

Static checks must prove:

- all eight selected implementation paths and no others are changed;
- no existing module imports or re-exports `rie.prompt_candidate`;
- `prompt_candidate_service.py` has no repository backend, SQLite, filesystem, network, subprocess, clock, random, UUID, logging, model, provider, tokenizer, renderer, or CLI dependency;
- the package does not invoke Gate 8 governance or Gate 9 mutation workflows;
- package `__all__` exactly equals the selected public symbol set;
- no real RSV production data is embedded in production or test fixtures.

## 13. Exact future implementation scope

Only after this review is accepted, committed, pushed, and post-commit verified may a future PR implement exactly the eight selected paths.

The future implementation commit may contain the four production files and four test files together. Its implementation-review document, if required by the controlled execution script, must be separately selected before commit and must not silently broaden this path boundary.

No existing source, test, architecture document, README, configuration, script, migration, package metadata, or dependency declaration may be changed.

## 14. Explicit exclusions

- no Gate 9 repository access, mutation, lifecycle append, implicit latest lookup, history query, or persistence;
- no model invocation, prompt execution, provider selection, provider fallback, rendering, tokenization, or provider-specific token budgeting;
- no hidden conversation context, automatic intent inference, automatic style selection, prompt optimization, quality scoring, or creative generation;
- no Gate 8 reconstruction, governance, conflict, authority, promotion, GovernedKnowledge construction, acceptance, or lifecycle interpretation execution;
- no filesystem, network, subprocess, current clock, randomness, UUID generation, mutable global cache, or environment-dependent normalization;
- no CLI, API transport, packaging, release behavior, Gate 11 invocation, or real RSV production-data admission;

## 15. Decision

Gate 10 minimum closure boundary committed: `True`.

Gate 10 runtime contract committed: `True`.

Gate 10 implementation boundary selected: `True`.

Gate 10 implementation boundary committed: `False`.

Gate 10 implementation authorized: `False`.

Gate 10 implementation started: `False`.

Gate 10 closed: `False`.

Gate 11 invoked: `False`.

## 16. Next safe operation

After independent acceptance of this review report, the next safe operation is manual commit and push of this one architecture document, followed by separate PR-055C post-commit verification.

Implementation remains unauthorized until that post-commit verification is independently accepted.
