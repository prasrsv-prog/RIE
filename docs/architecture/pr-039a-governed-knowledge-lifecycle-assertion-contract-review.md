# PR-039A - Governed Knowledge Lifecycle Assertion Contract Review

## 1. Review identity

PR-039A is an architecture-only exact-contract review on branch `phase-039-governed-knowledge-lifecycle-assertion-contract-review` at official Phase 38 checkpoint `d3d07f9f26c141799088da1d38caa980be5dd068`.

It defines the minimum exact immutable contract for one caller-supplied governed-Knowledge lifecycle assertion without implementing the contract, interpreting assertions, executing transitions, projecting current state, introducing repository admission, defining persistence, or authorizing runtime behavior.

## 2. Official predecessor checkpoint

The official predecessor is annotated tag `v0.38.0-rcis-governed-knowledge-lifecycle-fact-model-boundary-phase`.

Its tag object is `7958cd18a4ed86dd8668a30e5bf0250b9333938c` and its peeled target is `d3d07f9f26c141799088da1d38caa980be5dd068`.

Phase 38 selected exactly one fact model:

```text
immutable_caller_supplied_governed_knowledge_lifecycle_assertion_fact
```

Phase 38 authorized no exact assertion contract and no implementation.

## 3. Review mode

This review is architecture-only.

It creates one architecture document and one external evidence report. It changes no production file, test file, package initializer, configuration file, dependency declaration, schema, migration, repository interface, serializer, CLI, API, or runtime integration.

No tests and no project interpreter are run.

## 4. Current implemented endpoint

The implemented production chain remains:

```text
GovernedKnowledge
-> GovernedKnowledgeAcceptanceDecision
-> GovernedKnowledgeAcceptanceHistoryInterpretation
-> no governed-Knowledge lifecycle assertion contract
-> no lifecycle assertion identity
-> no lifecycle assertion interpretation
-> no transition execution
-> no current-state projection
-> no repository admission
-> no persistence
```

Existing `KnowledgeCandidate.lifecycle_status` remains part of the earlier KnowledgeCandidate contract and does not satisfy the selected governed-Knowledge lifecycle assertion model.

## 5. Problem statement

Phase 38 chose an immutable caller-supplied assertion fact but deliberately deferred the exact contract.

The missing contract must define one exact subject, one exact assertion value, explicit caller provenance, explicit descriptive time, deterministic identity material, and validation boundaries without assigning authority, ordering, current effectiveness, or transition meaning.

## 6. Contract candidates

PR-039A considers four candidates:

1. `minimum_provenance_bearing_immutable_assertion_contract`;
2. `subject_and_assertion_value_only_contract`;
3. `transition_shaped_assertion_contract`;
4. `none`.

## 7. Selection criteria

Each candidate is evaluated against the same criteria:

1. conforms to the Phase 38 immutable assertion-fact model;
2. identifies one exact governed-Knowledge subject;
3. records one explicit caller-supplied assertion value;
4. provides enough provenance to distinguish independently supplied assertions;
5. uses explicit caller-supplied time without acquiring a clock;
6. supports deterministic content identity;
7. remains immutable;
8. permits contradictory assertions to coexist;
9. creates no actor, policy, source, reason, or time priority;
10. creates no latest-wins behavior;
11. does not imply that a transition occurred;
12. creates no current lifecycle state;
13. remains separate from lifecycle interpretation;
14. remains separate from transition execution;
15. remains separate from repository admission;
16. remains separate from persistence and serialization;
17. defines exact validation boundaries;
18. introduces no business, creative, Prompt, AI, or runtime authority;
19. can support a later implementation-boundary review;
20. authorizes no implementation automatically.

## 8. Candidate comparison

### 8.1 Minimum provenance-bearing immutable assertion contract

This candidate records one exact governed-Knowledge subject, one opaque caller-supplied assertion value, one exact caller-supplied assertion reference, caller identity, explicit descriptive time, policy identity, policy version, and ordered reason codes.

All eleven identity-input fields participate in deterministic identity. The final assertion ID is derived from those fields and remains outside its own identity projection. The contract remains non-interpreting and non-selecting.

Disposition: eligible and selected.

### 8.2 Subject and assertion value only contract

This candidate would record only the governed-Knowledge subject and assertion value.

It cannot distinguish independently supplied assertions that have the same value but different provenance, policy, reason, or explicit occurrence context. It also creates ambiguity about whether duplicate values represent one fact or several facts.

Disposition: insufficient and not selected.

### 8.3 Transition-shaped assertion contract

This candidate would include prior state, resulting state, transition name, completion status, or transition authority.

Those fields would claim transition semantics that Phase 38 explicitly excluded.

Disposition: prohibited and not selected.

### 8.4 None

`none` remains valid if no exact contract can be stated without inventing unsupported semantics.

It is not selected because one minimum provenance-bearing immutable assertion contract can be defined while preserving all Phase 38 exclusions.

Disposition: eligible but not selected.

## 9. Selected contract

Selected contract:

```text
minimum_provenance_bearing_immutable_assertion_contract
```

Selection count: one.

## 10. Contract name

The future domain record name is:

```text
GovernedKnowledgeLifecycleAssertion
```

The future identity-input record name is:

```text
GovernedKnowledgeLifecycleAssertionIdentityInput
```

These names are architecture decisions only. No Python class is implemented by PR-039A.

## 11. Contract version

Exact contract version:

```text
governed-knowledge-lifecycle-assertion-v1
```

A future record must carry this exact version.

No compatibility, migration, fallback, or alternate version behavior is approved.

## 12. Exact record and identity-input fields

The exact `GovernedKnowledgeLifecycleAssertion` field order is:

```text
governed_knowledge_lifecycle_assertion_id: str
contract_version: str
governed_knowledge_id: str
governed_knowledge_contract_version: str
assertion_scope: str
assertion_scope_reference: str
assertion_value: str
asserted_by: str
asserted_at: datetime
assertion_policy_id: str
assertion_policy_version: str
reason_codes: tuple[str, ...]
```

The final record field count is 12.

The exact `GovernedKnowledgeLifecycleAssertionIdentityInput` field order is:

```text
contract_version: str
governed_knowledge_id: str
governed_knowledge_contract_version: str
assertion_scope: str
assertion_scope_reference: str
assertion_value: str
asserted_by: str
asserted_at: datetime
assertion_policy_id: str
assertion_policy_version: str
reason_codes: tuple[str, ...]
```

The identity-input field count is 11. Identity contains final-record fields 2 through 12. `governed_knowledge_lifecycle_assertion_id` is derived from the identity input and remains outside its own identity.

No diagnostics field, transition field, current-state field, repository field, persistence field, or runtime field is part of the minimum contract.

## 13. Exact subject boundary

`governed_knowledge_id` must identify one exact governed-Knowledge record and must conform to the existing `gk1_` identity format.

`governed_knowledge_contract_version` must equal the exact existing governed-Knowledge contract version:

```text
governed-knowledge-v1
```

The assertion subject is not a KnowledgeCandidate, acceptance decision, acceptance-history interpretation, repository row, product, campaign, Prompt, or external resource.

## 14. Assertion scope

Exact assertion scope constant:

```text
governed_knowledge_lifecycle_assertion_for_declared_subject
```

`assertion_scope_reference` must be an exact non-empty caller-supplied string.

The reference is descriptive identity material. It does not create authority, completeness, current state, repository ownership, or persistence location.

## 15. Assertion value

`assertion_value` must be an exact non-empty caller-supplied string.

The value is opaque at the fact boundary. PR-039A approves no lifecycle enum, state vocabulary, transition vocabulary, semantic alias, normalization to a business status, or current-effective interpretation.

Two different exact assertion strings are different identity material. Equivalent business meaning is not inferred.

## 16. Caller provenance

`asserted_by` must be an exact non-empty caller-supplied string.

Its presence identifies provenance only. It creates no authority hierarchy, priority, permission, approval, trust, or winner selection.

## 17. Explicit time

`asserted_at` must be an exact timezone-aware datetime supplied by the caller.

A future implementation must normalize it to UTC with microsecond precision for canonical identity. It may not acquire the system clock or substitute current time.

Time is descriptive identity material only. It creates no ordering rule, latest-wins behavior, current effectiveness, supersession, or invalidation.

## 18. Policy provenance

`assertion_policy_id` and `assertion_policy_version` must be exact non-empty caller-supplied strings.

They identify the declared policy context only. Their presence does not prove authority, validity, applicability, or precedence.

## 19. Reason codes

`reason_codes` must be a non-empty immutable tuple of exact non-empty strings.

Values must be unique and lexicographically ordered.

Reason codes are identity material. They create no interpretation, authority, transition, current state, or business action.

## 20. Deterministic identity

Exact ID prefix:

```text
gkla1_
```

Exact identity policy ID:

```text
rcis-governed-knowledge-lifecycle-assertion-identity
```

Exact identity policy version:

```text
1.0.0
```

Exact canonicalization contract:

```text
rcis-governed-knowledge-lifecycle-assertion-canonical-json-v1
```

Exact digest algorithm:

```text
sha256
```

The final identity must be `gkla1_` followed by 64 lowercase hexadecimal characters.

## 21. Material identity projection

The future identity projection must contain exactly these 12 keys:

```text
contract_version
governed_knowledge_id
governed_knowledge_contract_version
assertion_scope
assertion_scope_reference
assertion_value
asserted_by
asserted_at
assertion_policy_id
assertion_policy_version
reason_codes
identity_canonicalization_contract
```

The first 11 projection keys correspond exactly to the identity-input field order. `identity_canonicalization_contract` is the twelfth projection key and is supplied by the exact canonicalization constant rather than by a caller field.

`governed_knowledge_lifecycle_assertion_id` is computed from the projection and is not embedded inside its own projection.

No repository metadata, persistence metadata, insertion order, mutable status, diagnostic, current time, environment value, or external lookup may participate.

## 22. Canonicalization

All string values and mapping keys must use Unicode NFC normalization.

The projection must use canonical JSON with:

```text
ensure_ascii=False
sort_keys=True
separators=(",", ":")
allow_nan=False
```

`asserted_at` must be represented in UTC with microsecond precision and a terminal `Z`.

Tuple values must project as JSON arrays.

No whitespace, locale, platform newline, dictionary insertion order, or process state may affect identity.

## 23. Immutability

The future identity-input record and lifecycle assertion record must be immutable exact-type records.

The final record must validate that its declared ID equals the deterministic ID computed from its exact material fields.

Mutation, correction-in-place, replacement, or current-state updates are prohibited.

## 24. Exact validation boundary

A future implementation must reject:

- unsupported contract version;
- malformed `gkla1_` assertion ID;
- malformed `gk1_` governed-Knowledge ID;
- unsupported governed-Knowledge contract version;
- unsupported assertion scope;
- blank assertion scope reference;
- blank assertion value;
- blank asserted-by value;
- naive or non-datetime asserted-at value;
- blank policy ID;
- blank policy version;
- empty reason-code tuple;
- duplicate reason codes;
- non-lexicographic reason-code order;
- unsupported canonical value;
- declared assertion ID that differs from computed identity.

Exact exception messages and diagnostic types remain implementation details for a later review.

## 25. Contradiction and coexistence

Two or more valid assertions about the same governed-Knowledge identity may coexist even when their assertion values conflict.

A contradiction is not a malformed fact.

This contract does not classify, rank, merge, resolve, supersede, invalidate, withdraw, or select among assertions.

## 26. Duplicate meaning

Two assertion records with exactly the same material identity fields compute the same deterministic assertion ID.

Identity equality does not authorize repository deduplication, duplicate rejection, idempotent write behavior, replacement, or uniqueness enforcement.

Those remain repository-admission questions.

## 27. Acceptance separation

Acceptance decisions and acceptance-history interpretations do not provide default values for any assertion-contract field.

Acceptance outcome, actor, policy, timestamp, lexical ID, and composition result cannot synthesize `assertion_value`, `asserted_by`, `asserted_at`, policy fields, reason codes, or assertion identity.

## 28. Transition separation

The assertion contract contains no prior state, resulting state, transition name, transition authority, transition outcome, completion flag, or execution reference.

An assertion record does not prove that a transition occurred.

## 29. Current-state separation

The assertion contract contains no current-state field and no current-effective indicator.

No assertion is current merely because of time, actor, policy, source, reason, lexical ID, repository order, persistence order, or later insertion.

## 30. Interpretation separation

The assertion contract records facts only.

No lifecycle interpreter, completeness declaration, composition classification, contradiction policy, current-state projection, or selection result is approved.

## 31. Repository separation

PR-039A creates no lifecycle assertion repository, repository protocol, admission request, uniqueness key, duplicate rule, idempotency rule, transaction boundary, lock, concurrency behavior, or failure-atomicity contract.

The deterministic ID is not repository authorization.

## 32. Persistence separation

PR-039A creates no serializer, storage schema, database mapping, migration, wire format, compatibility rule, recovery behavior, or persistence adapter.

The canonical identity projection is not a storage schema.

## 33. Runtime exclusions

The selected contract grants no business, creative, legal, compliance, publication, campaign, marketing, Prompt Candidate, Prompt generation, AI inference, embedding, recommendation, or runtime authority.

It performs no filesystem, database, network, clock, randomness, callback, dispatch, retry, or external action.

## 34. Future dedicated review subject

The selected exact contract makes exactly one future architecture subject eligible for consideration:

```text
governed_knowledge_lifecycle_assertion_implementation_boundary_review
```

That review is not automatically started by PR-039A.

It must determine whether the exact immutable contract, identity, validation, and test boundary are implementation-ready without adding interpretation, transition execution, repository admission, or persistence.

## 35. Implementation authorization

Implementation authorized: no.

Production files approved: zero.

Test files approved: zero.

No dataclass, constant, regex, canonical projection function, ID computation function, constructor, export, interpreter, transition service, repository, serializer, schema, migration, or test matrix is approved.

## 36. Risks deferred

Deferred risks include implementation file placement, package export, exact exception wording, diagnostic policy, exhaustive validation precedence, test cases, public API exposure, compatibility, lifecycle interpretation, contradiction classification, completeness, transition execution, repository ownership, persistence, migration, and recovery.

## 37. Definition of Done

PR-039A is complete when:

- the official Phase 38 checkpoint and annotated tag are verified locally and remotely;
- the Phase 39 branch is synchronized and clean;
- the accepted PR-038B evidence report is verified;
- relevant committed architecture and domain contracts are inspected;
- no lifecycle assertion production file exists;
- every exact-contract candidate is evaluated consistently;
- exactly one contract is selected;
- exact final-record field order, identity-input field order, identity projection, canonicalization, and validation boundary are defined;
- assertion remains separate from transition event and current state;
- acceptance remains separate from lifecycle assertion material;
- interpretation, repository admission, and persistence remain separate;
- exactly this architecture document is added;
- no production or test file changes;
- no tests or project interpreter run;
- no Git mutation command runs;
- the external report contains complete exact snapshots and fingerprints;
- implementation remains explicitly unauthorized.

## 38. Final decision

# SELECTED CONTRACT: MINIMUM PROVENANCE-BEARING IMMUTABLE GOVERNED-KNOWLEDGE LIFECYCLE ASSERTION CONTRACT

PR-039A approves one exact architecture contract only.

It does not approve implementation, lifecycle interpretation, transition execution, current-state projection, repository admission, persistence, serialization, business action, creative action, Prompt behavior, AI behavior, or runtime behavior.

The next step is not implementation.
