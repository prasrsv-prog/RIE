# PR-038A - Governed Knowledge Lifecycle Fact-Model Boundary Review

## 1. Review identity

PR-038A is an architecture-only fact-model boundary review on branch `phase-038-governed-knowledge-lifecycle-fact-model-boundary-review` at official Phase 37 checkpoint `de2fe3a18b49e2f84cdb0938c8d2f3f9a5104c9b`.

It evaluates which single minimum fact representation can satisfy the Phase 37 premise without deriving lifecycle from acceptance history, creating current state, executing a transition, introducing repository admission, defining persistence, or authorizing implementation.

## 2. Official predecessor checkpoint

The official predecessor is annotated tag `v0.37.0-rcis-governed-knowledge-lifecycle-premise-phase`.

Its tag object is `ad6881d6bf5300e0d40ca8e291acae30589b866a` and its peeled target is `de2fe3a18b49e2f84cdb0938c8d2f3f9a5104c9b`.

Phase 37 selected exactly one premise:

```text
explicit_caller_supplied_governed_knowledge_lifecycle_facts
```

Phase 37 authorized no lifecycle fact model and no implementation.

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
-> no governed-Knowledge lifecycle fact
-> no lifecycle interpretation
-> no transition execution
-> no repository admission
-> no persistence
```

Existing acceptance-history interpretation preserves exact bounded composition and contradiction but does not establish lifecycle.

Existing `KnowledgeCandidate.lifecycle_status` belongs to the earlier KnowledgeCandidate contract. It is not a governed-Knowledge lifecycle fact and cannot be reused as one.

## 5. Problem statement

Phase 37 established the source rule for future lifecycle material but deliberately left the fact representation unresolved.

A future contract cannot be reviewed safely until the architecture distinguishes a lifecycle assertion from a transition event and from mutable current state.

## 6. Fact-model candidates

PR-038A considers four candidates:

1. `immutable_caller_supplied_governed_knowledge_lifecycle_assertion_fact`;
2. `immutable_governed_knowledge_lifecycle_transition_event`;
3. `mutable_governed_knowledge_current_lifecycle_state_record`;
4. `none`.

## 7. Selection criteria

Each candidate is evaluated against the same criteria:

1. satisfies the Phase 37 explicit-fact premise;
2. identifies one exact governed-Knowledge subject;
3. records caller-supplied lifecycle material directly;
4. does not derive lifecycle from acceptance;
5. does not create current-effective acceptance;
6. does not imply that a transition occurred;
7. does not execute a transition;
8. does not create mutable current state;
9. preserves contradictory facts;
10. permits coexistence of independently supplied facts;
11. does not rank actor, policy, time, or lexical identity;
12. does not use latest-wins;
13. remains deterministic at the fact boundary;
14. remains separate from lifecycle interpretation;
15. remains separate from transition execution;
16. remains separate from repository admission;
17. remains separate from persistence and serialization;
18. introduces no clock acquisition;
19. introduces no business, creative, Prompt, AI, or runtime authority;
20. can support a later exact contract review without deciding unrelated responsibilities;
21. authorizes no implementation automatically.

## 8. Candidate comparison

### 8.1 Immutable caller-supplied governed-Knowledge lifecycle assertion fact

This candidate records one explicit lifecycle assertion supplied for one exact governed-Knowledge identity.

An assertion records what the caller asserts. It does not prove that a transition occurred, does not project current state, and does not select among contradictory assertions.

Independent assertion facts can coexist immutably. Their actor, policy, time, source, reason, and identity material cannot create priority unless a later interpretation policy explicitly authorizes such semantics.

Disposition: eligible and selected.

### 8.2 Immutable governed-Knowledge lifecycle transition event

A transition event would claim that a lifecycle change occurred. That requires approved prior and resulting states, transition vocabulary, transition authority, occurrence semantics, and validation of whether the transition was authorized and completed.

Those premises do not exist. Selecting this model would collapse fact recording into transition semantics.

Disposition: premature and not selected.

### 8.3 Mutable governed-Knowledge current lifecycle state record

A mutable current-state record would require an owner, replacement policy, concurrency rules, transaction boundaries, locking, persistence, and a current-effective selection rule.

It would also risk hiding latest-wins, supersession, or invalidation semantics.

Disposition: prohibited and not selected.

### 8.4 None

`none` remains valid if no fact representation can satisfy Phase 37 without inventing unsupported meaning.

It is not selected because an immutable caller-supplied assertion fact can be bounded without claiming transition occurrence or current state.

Disposition: eligible but not selected.

## 9. Selected fact model

Selected fact model:

```text
immutable_caller_supplied_governed_knowledge_lifecycle_assertion_fact
```

Selection count: one.

## 10. Single responsibility

The selected model has one responsibility:

```text
Record one immutable caller-supplied lifecycle assertion about one exact governed-Knowledge identity.
```

It does not interpret, rank, apply, transition, activate, retire, supersede, invalidate, admit, persist, publish, dispatch, or execute anything.

## 11. Exact subject boundary

Each future assertion fact must identify one exact governed-Knowledge subject by exact governed-Knowledge identity and governed-Knowledge contract version.

No aggregate, alias, mutable business object, product, campaign, Prompt, repository row, or external resource becomes the subject.

## 12. Explicit assertion boundary

The lifecycle assertion must be explicit caller-supplied material.

A later exact contract review must define the assertion vocabulary and representation. PR-038A does not approve lifecycle states, status values, transition names, from-state or to-state fields, current-state fields, or a lifecycle policy result.

## 13. Immutability boundary

Each assertion fact must be immutable after construction.

Correction, contradiction, withdrawal, supersession, and invalidation may only be represented by separately approved facts or policies in later reviews. PR-038A approves none of those mechanisms.

## 14. Coexistence boundary

Multiple assertion facts about the same governed-Knowledge identity may coexist.

Coexistence does not imply agreement, ordering, precedence, current effectiveness, or a winner.

## 15. Contradiction boundary

Contradictory lifecycle assertions are not automatically malformed.

They must remain preserved as separate facts unless a future dedicated interpretation policy explicitly defines a controlled classification. PR-038A defines no conflict resolution.

## 16. Acceptance separation

Acceptance decisions and acceptance-history interpretations remain distinct evidence.

`accepted_only`, mixed acceptance compositions, acceptance timestamps, acceptance actors, acceptance policies, and lexical acceptance IDs cannot create lifecycle assertions.

## 17. Transition separation

An assertion fact is not a transition event.

It does not establish that a prior state existed, that a resulting state exists, that a transition was authorized, or that any transition completed.

No transition service or execution record is approved.

## 18. Current-state separation

An assertion fact is not current lifecycle state.

No assertion is current-effective by default. Actor, policy, time, source, reason, lexical ID, repository order, and persistence order do not create current state or latest-wins behavior.

## 19. Interpretation separation

Fact recording remains separate from lifecycle interpretation.

A future interpreter may only be considered after the exact assertion contract exists. It must consume an explicit bounded fact set and must not mutate or supplement facts.

## 20. Identity boundary

A deterministic content identity may be considered in a later exact contract review.

PR-038A approves no field names, field order, ID prefix, canonical JSON projection, normalization rule, digest contract, or validation implementation.

Existing `gk1_`, `gka1_`, and `gkai1_` identity contracts grant no lifecycle assertion identity.

## 21. Provenance and authority boundary

A later exact contract review must decide whether actor, policy, source reference, reason, and explicit time are material fields.

None of those values may create authority or priority merely by being present. PR-038A defines no authority hierarchy.

## 22. Time boundary

PR-038A introduces no clock acquisition and no implicit current time.

Any future explicit caller-supplied time material must remain descriptive unless a later architecture review separately authorizes time semantics. Time cannot establish current state or latest-wins.

## 23. Completeness boundary

One assertion fact makes no completeness claim about all lifecycle material for its subject.

Any later lifecycle interpretation completeness assertion must be separate, explicit, bounded, and must not be inferred from repository lookup, persistence contents, or current time.

## 24. Repository separation

PR-038A creates no governed-Knowledge lifecycle repository, repository interface, admission rule, uniqueness rule, duplicate replacement, transaction boundary, lock, concurrency behavior, or failure-atomicity contract.

Fact coexistence is a domain possibility, not repository authorization.

## 25. Persistence separation

PR-038A creates no serializer, schema, database mapping, migration, wire format, storage order, compatibility rule, recovery behavior, or persistence adapter.

Content identity is not a storage schema.

## 26. Malformed-input boundary

A later exact contract review must distinguish malformed assertion material from valid contradictory assertions.

PR-038A does not define exact validation rules, exception types, diagnostics, or rejection precedence.

## 27. Business and runtime exclusions

The selected fact model grants no business, creative, legal, compliance, publication, campaign, marketing, Prompt Candidate, Prompt generation, AI inference, embedding, recommendation, or runtime authority.

It performs no filesystem, database, network, clock, randomness, callback, dispatch, retry, or external action.

## 28. Future dedicated review subject

The selected model makes exactly one future architecture subject eligible for consideration:

```text
governed_knowledge_lifecycle_assertion_contract_review
```

That review is not automatically started by PR-038A.

It must define the exact immutable assertion contract without adding interpretation, transition execution, current-state projection, repository admission, or persistence.

## 29. Implementation authorization

Implementation authorized: no.

Production files approved: zero.

Test files approved: zero.

No lifecycle dataclass, enum, constant, ID prefix, canonical projection, constructor, interpreter, transition service, repository, serializer, schema, migration, or test matrix is approved.

## 30. Risks deferred

Deferred risks include assertion vocabulary, exact fields, field types, contract version, identity prefix, canonicalization, provenance, authority material, time material, reason material, source reference, diagnostics, malformed input, contradiction classification, completeness, interpretation policy, transition execution, repository ownership, persistence, compatibility, migration, and recovery.

## 31. Definition of Done

PR-038A is complete when:

- the official Phase 37 checkpoint and annotated tag are verified locally and remotely;
- the Phase 38 branch is synchronized and clean;
- the accepted PR-037B evidence report is verified;
- relevant committed architecture and domain contracts are inspected;
- no governed-Knowledge lifecycle production file exists;
- every fact-model candidate is evaluated consistently;
- exactly one fact model is selected;
- assertion remains separate from transition event and current state;
- acceptance remains separate from lifecycle;
- interpretation, transition execution, repository admission, and persistence remain separate;
- exactly this architecture document is added;
- no production or test file changes;
- no tests or project interpreter run;
- no Git mutation command runs;
- the external report contains complete exact snapshots and fingerprints;
- implementation remains explicitly unauthorized.

## 32. Final decision

# SELECTED FACT MODEL: IMMUTABLE CALLER-SUPPLIED GOVERNED-KNOWLEDGE LIFECYCLE ASSERTION FACT

PR-038A approves one architecture fact-model boundary only.

It does not approve an exact assertion contract, lifecycle vocabulary, lifecycle identity, interpretation, transition execution, current state, repository admission, persistence, serialization, business action, creative action, Prompt behavior, AI behavior, or runtime behavior.

The next step is not implementation.
