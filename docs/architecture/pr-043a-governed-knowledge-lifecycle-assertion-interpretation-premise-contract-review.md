# PR-043A - Governed Knowledge Lifecycle Assertion Interpretation Premise Contract Review

## 1. Review identity

PR-043A is an architecture-only exact-contract review on branch `phase-043-governed-knowledge-lifecycle-assertion-interpretation-premise-contract-review` at official Phase 42 checkpoint `a17021d80ed3e3fe526c6fca8e21075f716a7e5f`.

It defines the minimum exact immutable contract for one explicit caller-supplied finite governed-Knowledge lifecycle assertion collection premise with declared scope and completeness.

PR-043A does not implement the contract, define an interpretation result, execute transitions, project current state, create repository behavior, persist premises, or authorize business, creative, Prompt, AI, or runtime behavior.

## 2. Official predecessor checkpoint

The official predecessor is annotated tag:

```text
v0.42.0-rcis-governed-knowledge-lifecycle-assertion-interpretation-premise-phase
```

Its local and remote tag object is:

```text
43718ad4e5fe4c8ee0e87674cbdab8c1e13a1109
```

Its peeled target is:

```text
a17021d80ed3e3fe526c6fca8e21075f716a7e5f
```

Phase 42 selected exactly one premise:

```text
explicit_caller_supplied_finite_assertion_collection_with_declared_scope_and_completeness
```

Phase 42 selected no exact premise contract and authorized no implementation.

## 3. Preserved architecture direction

PR-043A preserves exactly:

```text
interpretation_premise_before_transition_current_state_repository_or_persistence
```

Interpretation prerequisites remain ahead of transition execution, current-state projection, repository admission, and persistence.

## 4. Review mode

This review is architecture-only.

It creates one architecture document and one fresh external evidence report.

It changes no production file, test file, package initializer, configuration file, dependency declaration, repository interface, serializer, persistence adapter, schema, migration, CLI, API, or runtime integration.

No tests and no project interpreter are run.

No Git mutation command is performed by this review task.

## 5. Current implemented endpoint

The implemented endpoint remains:

```text
GovernedKnowledge
-> GovernedKnowledgeAcceptanceDecision
-> GovernedKnowledgeAcceptanceHistoryInterpretation
-> GovernedKnowledgeLifecycleAssertion
-> no lifecycle assertion interpretation premise contract
-> no lifecycle assertion interpretation
-> no transition execution
-> no current-state projection
-> no lifecycle assertion repository
-> no persistence
```

The existing lifecycle assertion record remains immutable, deterministic, caller-supplied, provenance-bearing, and non-interpreting.

## 6. Exact contract question

PR-043A answers:

```text
What minimum exact immutable contract can represent one caller-supplied finite collection of governed-Knowledge lifecycle assertions, one declared consideration scope, and one explicit completeness declaration without defining interpretation behavior?
```

The answer must preserve every structurally valid supplied assertion and must create no semantic priority, authority, transition, current state, repository truth, or persistence truth.

## 7. Contract candidates

PR-043A evaluates:

1. `minimum_provenance_bearing_immutable_assertion_collection_premise_contract`;
2. `assertion_id_collection_only_premise_contract`;
3. `repository_query_backed_premise_contract`;
4. `interpretation_shaped_premise_contract`;
5. `none`.

## 8. Candidate comparison

### 8.1 Minimum provenance-bearing immutable assertion collection premise contract

This candidate stores one exact governed-Knowledge subject, one exact tuple of validated lifecycle assertion records, one declared consideration scope, one explicit completeness declaration, caller provenance, explicit caller-supplied time, policy provenance, and ordered reason codes.

Its deterministic identity uses the exact ordered assertion IDs because every lifecycle assertion ID already binds the full immutable assertion material.

Disposition: eligible and selected.

### 8.2 Assertion-ID collection only premise contract

This candidate would store assertion IDs without carrying the exact assertion records.

A future interpreter would require repository lookup or another external resolution mechanism to recover the supplied material. That would weaken the explicit caller-supplied premise boundary.

Disposition: insufficient and not selected.

### 8.3 Repository-query-backed premise contract

This candidate would treat repository query output, query exhaustion, or storage contents as the premise.

Repository contents cannot prove semantic completeness, and storage behavior cannot replace explicit caller-supplied scope or completeness.

Disposition: prohibited and not selected.

### 8.4 Interpretation-shaped premise contract

This candidate would add contradiction classification, selected assertion, sufficiency, current state, transition meaning, or interpretation outcome.

Those fields belong to a future interpretation contract, not to premise material.

Disposition: prohibited and not selected.

### 8.5 None

`none` remains valid if no exact contract can be defined without unsupported semantics.

It is not selected because one immutable caller-supplied premise contract can be stated while preserving every Phase 42 exclusion.

Disposition: eligible but not selected.

## 9. Selected contract

Selected contract:

```text
minimum_provenance_bearing_immutable_assertion_collection_premise_contract
```

Selection count: one.

## 10. Future record names

The future premise record name is:

```text
GovernedKnowledgeLifecycleAssertionInterpretationPremise
```

The future identity-input record name is:

```text
GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput
```

These are architecture decisions only. PR-043A implements no Python class.

## 11. Exact contract version

Exact premise contract version:

```text
governed-knowledge-lifecycle-assertion-interpretation-premise-v1
```

No alternate version, fallback, compatibility alias, migration, or implicit upgrade behavior is approved.

## 12. Exact final-record field order

The future final record must contain exactly these thirteen fields in this order:

```text
governed_knowledge_lifecycle_assertion_interpretation_premise_id: str
contract_version: str
governed_knowledge_id: str
governed_knowledge_contract_version: str
premise_scope: str
premise_scope_reference: str
completeness_declaration: str
assertions: tuple[GovernedKnowledgeLifecycleAssertion, ...]
declared_by: str
declared_at: datetime
declaration_policy_id: str
declaration_policy_version: str
reason_codes: tuple[str, ...]
```

No field has a default.

No interpretation result, diagnostic, transition, current-state, repository, persistence, serialization, or runtime field is included.

## 13. Exact identity-input field order

The future identity-input record must contain exactly these twelve fields in this order:

```text
contract_version: str
governed_knowledge_id: str
governed_knowledge_contract_version: str
premise_scope: str
premise_scope_reference: str
completeness_declaration: str
assertions: tuple[GovernedKnowledgeLifecycleAssertion, ...]
declared_by: str
declared_at: datetime
declaration_policy_id: str
declaration_policy_version: str
reason_codes: tuple[str, ...]
```

The final premise ID remains outside its own identity.

## 14. Exact governed-Knowledge subject boundary

`governed_knowledge_id` must identify one exact governed-Knowledge record and must conform to the existing `gk1_` identity format.

`governed_knowledge_contract_version` must equal the exact governed-Knowledge contract version:

```text
governed-knowledge-v1
```

Every supplied lifecycle assertion must identify the same exact governed-Knowledge subject and the same exact governed-Knowledge contract version.

Cross-subject premise material must fail closed.

## 15. Exact premise scope

Exact premise scope constant:

```text
governed_knowledge_lifecycle_assertion_interpretation_for_declared_subject
```

`premise_scope_reference` must be an exact non-empty caller-supplied string.

The scope and reference identify the caller-declared consideration boundary only. They create no authority, repository ownership, persistence location, current state, transition meaning, or business approval.

## 16. Exact completeness declarations

The future contract permits exactly two completeness declaration values:

```text
complete_for_declared_scope
incomplete_for_declared_scope
```

The declaration must be supplied explicitly by the caller.

`complete_for_declared_scope` does not prove truth, authority, global completeness, repository completeness, historical completeness, transition occurrence, current state, or business fitness.

`incomplete_for_declared_scope` remains valid premise material. A future interpretation contract may fail closed or produce a non-authoritative result, but PR-043A defines no such behavior.

## 17. Exact assertion collection boundary

`assertions` must be an exact immutable tuple.

Each item must be an exact `GovernedKnowledgeLifecycleAssertion` record. Subclasses and alternate record types are not accepted.

The tuple may be empty. An empty tuple has no interpretation meaning by itself and does not imply that no lifecycle assertion exists outside the caller-declared premise.

Every non-empty tuple must preserve each supplied structurally valid assertion record exactly.

## 18. Cross-subject validation

Each supplied assertion must satisfy all of the following:

- its exact type is `GovernedKnowledgeLifecycleAssertion`;
- its own record validation succeeds;
- its `governed_knowledge_id` equals the premise `governed_knowledge_id`;
- its `governed_knowledge_contract_version` equals the premise `governed_knowledge_contract_version`;
- its lifecycle assertion contract version is the supported exact assertion contract version.

A mismatch is malformed premise material rather than a contradiction.

## 19. Duplicate assertion identity rule

A premise must reject repeated lifecycle assertion IDs.

Duplicate-ID rejection is a premise-membership rule only.

It creates no repository uniqueness rule, duplicate-storage rule, idempotency rule, replacement rule, or persistence behavior.

## 20. Exact canonical collection ordering

The assertion tuple must be lexicographically ordered by exact lifecycle assertion ID.

Canonical ordering creates deterministic premise identity only.

It creates no semantic priority, authority, chronology, winner selection, supersession, withdrawal, invalidation, or current effectiveness.

## 21. Contradiction preservation

Different structurally valid assertions about the same governed-Knowledge subject may coexist in one premise even when their assertion values conflict.

Contradiction is not malformed premise material.

The contract does not classify, rank, merge, resolve, select, supersede, withdraw, invalidate, or normalize contradictory assertions.

## 22. Caller provenance

`declared_by` must be an exact non-empty caller-supplied string.

Its presence records premise provenance only.

It creates no role hierarchy, trust hierarchy, approval hierarchy, permission, authority, or winner selection.

## 23. Explicit caller-supplied time

`declared_at` must be an exact timezone-aware datetime supplied by the caller.

Canonical identity must normalize it to UTC with microsecond precision and terminal `Z`.

The future contract may not acquire a system clock or substitute current time.

Time remains descriptive identity material only.

## 24. Policy provenance

`declaration_policy_id` and `declaration_policy_version` must be exact non-empty caller-supplied strings.

They identify the caller-declared policy context only.

Their presence does not prove authority, validity, applicability, precedence, or business approval.

## 25. Reason codes

`reason_codes` must be a non-empty immutable tuple of exact non-empty strings.

Values must be unique and lexicographically ordered.

Reason codes are identity and provenance material only. They create no interpretation result, authority, transition, current state, repository action, persistence action, or business action.

## 26. Deterministic premise identity

Exact premise ID prefix:

```text
gklaip1_
```

Exact identity policy ID:

```text
rcis-governed-knowledge-lifecycle-assertion-interpretation-premise-identity
```

Exact identity policy version:

```text
1.0.0
```

Exact canonicalization contract:

```text
rcis-governed-knowledge-lifecycle-assertion-interpretation-premise-canonical-json-v1
```

Exact digest algorithm:

```text
sha256
```

The final premise ID must be `gklaip1_` followed by 64 lowercase hexadecimal characters.

## 27. Exact material identity projection

The future identity projection must contain exactly these thirteen keys:

```text
contract_version
governed_knowledge_id
governed_knowledge_contract_version
premise_scope
premise_scope_reference
completeness_declaration
assertion_ids
declared_by
declared_at
declaration_policy_id
declaration_policy_version
reason_codes
identity_canonicalization_contract
```

`assertion_ids` must contain the exact lexicographically ordered lifecycle assertion IDs from `assertions`.

The final premise ID remains outside its own identity.

No assertion is resolved through repository lookup. No repository metadata, persistence metadata, insertion order, mutable status, current time, environment value, filesystem value, database value, network value, or external lookup participates.

## 28. Canonicalization

All string values and mapping keys must use Unicode NFC normalization.

Canonical JSON must use:

```text
ensure_ascii=False
sort_keys=True
separators=(",", ":")
allow_nan=False
```

`declared_at` must be represented in UTC with microsecond precision and terminal `Z`.

Tuple values must project as JSON arrays.

No locale, platform newline, mapping insertion order, process state, clock, randomness, filesystem, database, or network input may affect identity.

## 29. Immutability

The future premise identity-input record and final premise record must be frozen exact-type records.

Mutation, correction-in-place, replacement, collection extension, collection reduction, completeness update, scope update, or provenance update is prohibited.

A changed premise must be represented by a new immutable record with a new deterministic identity when material differs.

## 30. Exact validation order

The future identity-input record must validate in this order:

1. `contract_version`;
2. `governed_knowledge_id`;
3. `governed_knowledge_contract_version`;
4. `premise_scope`;
5. `premise_scope_reference`;
6. `completeness_declaration`;
7. `assertions` exact tuple type;
8. each assertion exact type and record validity;
9. each assertion subject and contract-version match;
10. duplicate lifecycle assertion IDs;
11. lexicographic assertion-ID order;
12. `declared_by`;
13. `declared_at`;
14. `declaration_policy_id`;
15. `declaration_policy_version`;
16. `reason_codes`.

Validation must stop at the first failure.

The future final record must validate its premise-ID exact type and format first, then derive and validate the exact identity input, then compare the declared ID with the deterministic computed ID.

## 31. Exact validation boundary

A future implementation must reject:

- unsupported premise contract version;
- malformed `gklaip1_` premise ID;
- malformed `gk1_` governed-Knowledge ID;
- unsupported governed-Knowledge contract version;
- unsupported premise scope;
- blank premise scope reference;
- unsupported completeness declaration;
- non-tuple assertion collection;
- assertion item of the wrong exact type;
- invalid lifecycle assertion record;
- cross-subject assertion;
- unsupported lifecycle assertion contract version;
- duplicate lifecycle assertion ID;
- non-lexicographic assertion-ID order;
- blank declared-by value;
- naive or non-datetime declared-at value;
- blank declaration policy ID;
- blank declaration policy version;
- empty reason-code tuple;
- invalid reason-code item;
- duplicate reason codes;
- non-lexicographic reason-code order;
- unsupported canonical value;
- declared premise ID that differs from computed identity.

Exact exception messages remain implementation-boundary decisions for a future dedicated review.

## 32. Acceptance and lifecycle-assertion separation

Acceptance decisions and acceptance-history interpretations may not synthesize premise fields.

Lifecycle assertion actor, policy, time, reason codes, lexical identity, or assertion count may not synthesize premise scope, completeness, declaration provenance, or premise identity.

The premise is separate caller-supplied material.

## 33. Interpretation-output separation

PR-043A defines no interpretation result.

It creates no composition status, contradiction classification, completeness judgment, sufficiency result, selected assertion, current state, transition event, recommendation, diagnostic, or authority outcome.

The presence of a valid premise does not guarantee that interpretation will succeed.

## 34. Transition separation

No premise or assertion collection proves that a lifecycle transition occurred.

The contract contains no prior state, resulting state, transition name, transition authority, completion status, execution record, or side effect.

Transition execution remains ineligible.

## 35. Current-state separation

No current lifecycle state or current-effective assertion is selected.

Completeness, assertion time, actor, policy, reason codes, lexical identity, tuple order, repository order, or persistence order creates no current-state authority.

## 36. Repository separation

PR-043A creates no premise repository, lifecycle assertion repository, repository protocol, admission request, duplicate-storage policy, uniqueness rule, idempotency rule, transaction boundary, lock, concurrency behavior, or failure-atomicity contract.

Deterministic premise identity is not repository authorization.

## 37. Persistence separation

PR-043A creates no serializer, storage schema, database mapping, migration, wire format, compatibility rule, recovery behavior, or persistence adapter.

The canonical identity projection is not a storage schema.

## 38. Business, creative, Prompt, AI, and runtime exclusions

The selected contract grants no business, creative, legal, compliance, publication, campaign, marketing, Prompt Candidate, Prompt generation, AI inference, embedding, recommendation, or external-action authority.

It performs no filesystem, database, network, clock, randomness, callback, dispatch, retry, or external action.

## 39. Future architecture subject

The selected exact premise contract makes exactly one future architecture subject eligible:

```text
governed_knowledge_lifecycle_assertion_interpretation_premise_implementation_boundary_review
```

That review is not started by PR-043A.

It must determine whether the exact immutable premise contract, nested assertion validation, deterministic identity, validation order, file placement, and test boundary are ready for one minimum standalone implementation slice.

## 40. Implementation status

Implementation authorized: no.

Production files approved: zero.

Test files approved: zero.

Existing-file modifications approved: zero.

No premise dataclass, identity-input dataclass, constant, canonicalizer, identity function, constructor, package export, interpreter, interpretation result, transition service, current-state projector, repository, serializer, schema, migration, CLI, API, or runtime integration is approved.

## 41. Risks deferred

Deferred risks include implementation file placement, package exports, exact exception messages, diagnostics, exhaustive test cases, nested-record revalidation mechanics, performance, interpretation-result contract, contradiction classification, transition execution, current-state projection, repository admission, persistence, serialization, migration, recovery, business use, creative use, Prompt use, AI use, and runtime integration.

## 42. Definition of Done

PR-043A is complete when:

- the official Phase 42 checkpoint and annotated tag are verified locally and remotely;
- the Phase 43 branch is synchronized and clean before document creation;
- accepted Phase 42 evidence reports are verified exactly;
- committed Phase 39 through Phase 42 architecture and lifecycle assertion fingerprints are verified;
- every premise-contract candidate is evaluated consistently;
- exactly one premise contract is selected;
- exact record names, field order, field counts, scope, completeness declarations, collection membership, duplicate behavior, canonical ordering, provenance, identity projection, canonicalization, immutability, and validation order are defined;
- contradiction visibility remains preserved;
- assertion ordering creates no semantic priority;
- interpretation output, transition, current state, repository, and persistence remain separate;
- exactly one future implementation-boundary review becomes eligible;
- exactly one architecture document is added;
- no production or test file changes;
- no tests or project interpreter run;
- no Git mutation command runs;
- the external report contains the exact executed script, complete relevant snapshots, actual fingerprints, and one unique final marker block;
- no future review begins automatically.

## 43. Final decision

# SELECTED PREMISE CONTRACT: MINIMUM PROVENANCE-BEARING IMMUTABLE ASSERTION COLLECTION PREMISE CONTRACT

PR-043A approves one exact architecture contract only.

It does not approve implementation, interpretation output, transition execution, current-state projection, repository admission, persistence, serialization, business action, creative action, Prompt behavior, AI behavior, or runtime behavior.

The future implementation-boundary review remains eligible but is not started.
