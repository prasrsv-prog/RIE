# PR-040A - Governed Knowledge Lifecycle Assertion Implementation Boundary Review

## 1. Review identity

PR-040A is an architecture-only implementation-boundary review on branch `phase-040-governed-knowledge-lifecycle-assertion-implementation-boundary-review` at official Phase 39 checkpoint `c5800fc75996e94e09c38deb0cbb4b9d04af69bf`.

It determines whether the exact Phase 39 governed-Knowledge lifecycle assertion contract is ready for one minimum standalone implementation slice without implementing lifecycle interpretation, transition execution, current-state projection, repository admission, persistence, serialization, diagnostics, business behavior, creative behavior, Prompt behavior, AI behavior, or runtime integration.

## 2. Official predecessor checkpoint

The official predecessor is annotated tag `v0.39.0-rcis-governed-knowledge-lifecycle-assertion-contract-phase`.

Its local and remote tag object is `c13388f5b84fb0317610bc1eabe1f298f94497b9`, and its peeled target is `c5800fc75996e94e09c38deb0cbb4b9d04af69bf`.

Phase 39 selected exactly one contract:

```text
minimum_provenance_bearing_immutable_assertion_contract
```

Phase 39 implemented nothing and authorized no implementation automatically.

## 3. Review mode

This review is architecture-only.

It creates one architecture document and one external evidence report. It changes no production file, test file, package initializer, configuration file, dependency declaration, repository interface, serializer, schema, migration, CLI, API, or runtime integration.

No tests and no project interpreter are run.

## 4. Current implemented endpoint

The implemented production chain remains:

```text
GovernedKnowledge
-> GovernedKnowledgeAcceptanceDecision
-> GovernedKnowledgeAcceptanceHistoryInterpretation
-> no governed-Knowledge lifecycle assertion implementation
-> no lifecycle assertion interpretation
-> no transition execution
-> no current-state projection
-> no repository admission
-> no persistence
```

The exact Phase 39 contract exists only as committed architecture documentation.

## 5. Boundary question

The review question is:

```text
Can the exact Phase 39 immutable lifecycle assertion contract be implemented as one standalone domain module with one dedicated test module while preserving every excluded responsibility?
```

The implementation boundary must be exact enough to prevent field drift, identity drift, validation drift, package-surface drift, diagnostics expansion, interpretation coupling, repository coupling, and persistence coupling.

## 6. Implementation candidates

PR-040A considers four candidates:

1. `minimum_standalone_immutable_assertion_domain_slice`;
2. `assertion_contract_plus_diagnostics_and_package_exports`;
3. `assertion_contract_plus_interpretation_or_repository_integration`;
4. `none`.

## 7. Selection criteria

Each candidate is evaluated against the same criteria:

1. implements exactly the Phase 39 contract;
2. preserves final-record field count 12;
3. preserves identity-input field count 11;
4. preserves identity projection key count 12;
5. keeps the assertion ID outside its own identity;
6. preserves exact contract and subject versions;
7. preserves exact assertion scope;
8. preserves caller-supplied provenance and time;
9. preserves UTC microsecond terminal-`Z` canonicalization;
10. preserves Unicode NFC normalization;
11. preserves canonical JSON settings;
12. remains deterministic and immutable;
13. distinguishes malformed material from valid contradiction;
14. introduces no diagnostics field;
15. introduces no lifecycle vocabulary or interpretation;
16. introduces no transition execution;
17. introduces no current-state projection;
18. introduces no repository admission;
19. introduces no persistence or serialization;
20. introduces no clock acquisition, randomness, filesystem, database, or network dependency;
21. requires no package initializer change;
22. uses one production file and one dedicated test file;
23. follows existing governed-Knowledge domain identity patterns where compatible;
24. defines exact validation and test boundaries;
25. authorizes no unrelated implementation;
26. supports independent evidence review before implementation;
27. permits a smallest future implementation commit;
28. keeps implementation separate from phase closure;
29. creates no business, creative, Prompt, AI, or runtime authority;
30. may be rejected as `none` if any required behavior remains ambiguous.

## 8. Candidate comparison

### 8.1 Minimum standalone immutable assertion domain slice

This candidate adds one standalone domain module implementing only the exact constants, immutable records, deterministic identity projection, canonical bytes, ID computation, record-to-identity-input conversion, and validation required by Phase 39.

It adds one dedicated test module and does not modify the package initializer.

Disposition: eligible and selected.

### 8.2 Assertion contract plus diagnostics and package exports

This candidate would add a diagnostic record, diagnostics field, package initializer exports, or convenience API surface.

Phase 39 explicitly excluded diagnostics from the minimum record and deferred public exposure. These additions are unnecessary for the exact contract.

Disposition: scope expansion and not selected.

### 8.3 Assertion contract plus interpretation or repository integration

This candidate would connect lifecycle assertions to acceptance interpretation, transition processing, current-state projection, repository admission, persistence, serialization, or runtime behavior.

Those responsibilities remain separately governed and are not implementation prerequisites for the assertion fact.

Disposition: prohibited and not selected.

### 8.4 None

`none` remains valid if exact implementation behavior cannot be bounded.

It is not selected because the Phase 39 contract, existing governed-Knowledge identity patterns, and the exact boundaries below are sufficient for one minimum standalone implementation slice.

Disposition: eligible but not selected.

## 9. Selected implementation boundary

Selected boundary:

```text
minimum_standalone_immutable_assertion_domain_slice
```

Selection count: one.

## 10. Exact approved production scope

Exactly one future production file is approved:

```text
src/rie/domain/governed_knowledge_lifecycle_assertion.py
```

The file must be added as a new module.

No existing production file may be modified.

## 11. Exact approved test scope

Exactly one future test file is approved:

```text
tests/domain/test_governed_knowledge_lifecycle_assertion.py
```

The file must be added as a new test module.

No existing test file may be modified.

## 12. Package initializer decision

`src/rie/domain/__init__.py` must not change.

The lifecycle assertion module remains directly importable by its module path. Public package aggregation, re-export, convenience imports, and compatibility aliases are not approved.

## 13. Exact production symbols

The approved production module contains exactly these public contract symbols:

```text
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_ID
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_VERSION
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_CANONICALIZATION_CONTRACT
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_DIGEST_ALGORITHM
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED
GovernedKnowledgeLifecycleAssertionIdentityInput
GovernedKnowledgeLifecycleAssertion
canonical_governed_knowledge_lifecycle_assertion_identity_projection
canonical_governed_knowledge_lifecycle_assertion_identity_bytes
compute_governed_knowledge_lifecycle_assertion_id
governed_knowledge_lifecycle_assertion_identity_input_from_record
```

No diagnostic symbol, constructor service, interpreter, transition service, repository, serializer, persistence adapter, CLI, API, or compatibility alias is approved.

## 14. Exact constant values

The future module must define:

```text
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION =
    "governed-knowledge-lifecycle-assertion-v1"

GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX =
    "gkla1_"

GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_ID =
    "rcis-governed-knowledge-lifecycle-assertion-identity"

GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_VERSION =
    "1.0.0"

GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_CANONICALIZATION_CONTRACT =
    "rcis-governed-knowledge-lifecycle-assertion-canonical-json-v1"

GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_DIGEST_ALGORITHM =
    "sha256"

GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED =
    "governed_knowledge_lifecycle_assertion_for_declared_subject"
```

The governed-Knowledge subject contract version must be imported under this exact private alias:

```text
from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION as _GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
)
```

All subject-version comparisons must use `_GOVERNED_KNOWLEDGE_CONTRACT_VERSION`.

The literal `governed-knowledge-v1` must not be duplicated as a second source, and the upstream import must not create an additional public module symbol.

## 15. Exact identity-input record

`GovernedKnowledgeLifecycleAssertionIdentityInput` must be a frozen dataclass with exactly these eleven fields in this order:

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

No default value is approved.

No optional field is approved.

No diagnostics field is approved.

## 16. Exact final record

`GovernedKnowledgeLifecycleAssertion` must be a frozen dataclass with exactly these twelve fields in this order:

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

No default value is approved.

No diagnostics field is approved.

## 17. Exact identity projection

The identity projection must contain exactly these twelve keys:

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

The first eleven keys correspond exactly to the identity-input field order.

`identity_canonicalization_contract` is supplied from the exact canonicalization constant.

`governed_knowledge_lifecycle_assertion_id` remains outside its own identity.

## 18. Exact canonicalization behavior

All string values and mapping keys must use Unicode NFC normalization.

The timestamp must be represented in UTC with microsecond precision and terminal `Z`.

Tuples and lists project as JSON arrays.

Mappings must use normalized string keys and reject normalized-key collisions.

Canonical JSON must use:

```text
ensure_ascii=False
sort_keys=True
separators=(",", ":")
allow_nan=False
```

The output bytes must be UTF-8.

The ID must be `gkla1_` plus the lowercase SHA-256 hex digest of the canonical bytes.

## 19. Exact supported canonical values

The internal canonicalizer may support only:

```text
None
exact bool
exact int
finite exact float
exact str
exact tuple
exact list
exact dict with exact str keys
```

An exact float that is not finite must raise:

```text
ValueError("canonical values must be finite")
```

Any value of an unsupported exact type must raise:

```text
ValueError("unsupported canonical value")
```

A non-string mapping key must raise:

```text
ValueError("canonical mapping keys must be strings")
```

A Unicode-normalized duplicate mapping key must raise:

```text
ValueError("canonical mapping keys must remain unique")
```

## 20. Exact validation order for identity input

`GovernedKnowledgeLifecycleAssertionIdentityInput.__post_init__` must validate in this order:

1. `contract_version`;
2. `governed_knowledge_id`;
3. `governed_knowledge_contract_version`;
4. `assertion_scope`;
5. `assertion_scope_reference`;
6. `assertion_value`;
7. `asserted_by`;
8. `asserted_at`;
9. `assertion_policy_id`;
10. `assertion_policy_version`;
11. `reason_codes`.

Validation must stop at the first failure.

## 21. Exact validation messages

The future implementation must use these exact messages where applicable:

```text
unsupported contract_version
governed_knowledge_lifecycle_assertion_id must be an exact non-empty string
governed_knowledge_lifecycle_assertion_id has an invalid format
governed_knowledge_id must be an exact non-empty string
governed_knowledge_id has an invalid format
unsupported governed_knowledge_contract_version
unsupported assertion_scope
assertion_scope_reference must be an exact non-empty string
assertion_value must be an exact non-empty string
asserted_by must be an exact non-empty string
asserted_at must be an exact datetime
asserted_at must be timezone-aware
assertion_policy_id must be an exact non-empty string
assertion_policy_version must be an exact non-empty string
reason_codes must be a non-empty tuple
reason_codes must be an exact non-empty string
reason_codes must contain unique values
reason_codes must be lexicographically ordered
canonical values must be finite
```

All validation failures use `ValueError`.

## 22. Exact identifier validation

The governed-Knowledge ID pattern is:

```text
^gk1_[0-9a-f]{64}$
```

The lifecycle assertion ID pattern is:

```text
^gkla1_[0-9a-f]{64}$
```

The final record must first validate its lifecycle assertion ID format, then derive and validate an exact identity input, then compare the declared ID to the computed ID.

A mismatched declared ID must raise:

```text
ValueError(
    "governed_knowledge_lifecycle_assertion_id does not match identity"
)
```

## 23. Exact type guards

The canonical projection, canonical bytes, and ID computation functions must require the exact `GovernedKnowledgeLifecycleAssertionIdentityInput` type.

A wrong type must raise:

```text
ValueError(
    "identity_input must be an exact "
    "GovernedKnowledgeLifecycleAssertionIdentityInput"
)
```

The record-to-input function must require the exact `GovernedKnowledgeLifecycleAssertion` type.

A wrong type must raise:

```text
ValueError(
    "record must be an exact GovernedKnowledgeLifecycleAssertion"
)
```

Subclasses do not satisfy exact-type guards.

## 24. Validation invocation boundary

The canonical projection function must invoke `identity_input.__post_init__()` before projection.

The canonical bytes and ID computation functions must delegate through the validated projection path.

The final record must validate through the record-to-input function and deterministic ID computation.

No separate constructor factory is approved.

## 25. Contradiction boundary

Different exact assertion values about the same governed-Knowledge identity remain valid independently supplied facts.

They must produce different deterministic IDs when any material identity field differs.

No contradiction classification, winner selection, latest-wins behavior, supersession, withdrawal, invalidation, current-state projection, or transition behavior is approved.

## 26. Duplicate identity boundary

Exactly identical identity-input material must produce exactly the same deterministic ID.

This property authorizes no repository deduplication, duplicate rejection, uniqueness rule, replacement, idempotent write, persistence behavior, or admission policy.

## 27. Time boundary

The implementation accepts only exact timezone-aware `datetime` values.

It must acquire no clock and substitute no current time.

Equivalent instants with different offsets must canonicalize to the same UTC microsecond representation.

Different microseconds remain distinct identity material.

## 28. Immutability boundary

Both approved dataclasses must use `frozen=True`.

Tests must verify mutation rejection.

No correction-in-place, withdrawal, supersession, invalidation, current-state update, or repository overwrite behavior is approved.

## 29. Exact minimum test matrix

The dedicated test module must cover at least:

1. exact public contract symbol set with no unapproved public symbol or public import leakage;
2. exact constant values;
3. exact private upstream governed-Knowledge contract-version alias and no duplicated subject-version literal;
4. exact identity-input field order and count;
5. exact final-record field order and count;
6. exact identity projection keys and count;
7. deterministic canonical bytes;
8. deterministic ID prefix and digest shape;
9. malformed declared assertion-ID type and format rejection with exact messages;
10. declared assertion-ID mismatch rejection;
11. record-to-input exact field transfer;
12. frozen identity-input record;
13. frozen final record;
14. exact-type guards and subclass rejection;
15. identity-input first-failure validation precedence using combined invalid material;
16. final-record validation precedence: assertion-ID format, identity-input validation, then identity mismatch;
17. contract-version rejection;
18. governed-Knowledge ID type and format rejection;
19. governed-Knowledge contract-version rejection;
20. assertion-scope rejection;
21. blank string rejection for every required string field;
22. non-datetime and naive-datetime rejection;
23. UTC equivalence across offsets;
24. microsecond distinction;
25. Unicode NFC equivalence;
26. non-empty reason-code tuple;
27. exact reason-code item type and non-blank requirement;
28. duplicate reason-code rejection;
29. lexicographic reason-code ordering;
30. unsupported canonical exact-type rejection;
31. non-finite exact-float rejection with exact message;
32. non-string canonical mapping-key rejection;
33. normalized canonical mapping-key collision rejection;
34. identical identity material gives identical ID;
35. changed material field gives different ID;
36. contradictory assertion values can coexist as distinct valid records;
37. no diagnostics field;
38. no package initializer change;
39. no filesystem, database, network, clock, or randomness dependency.

The test count is not locked. Coverage of every boundary is locked.

## 30. Test execution boundary

The future implementation task must run:

```text
targeted lifecycle assertion tests
full committed-state regression suite
```

The implementation task must report actual counts.

PR-040A itself runs no tests.

## 31. Exact implementation commit scope

The future implementation commit may contain only:

```text
A	src/rie/domain/governed_knowledge_lifecycle_assertion.py
A	tests/domain/test_governed_knowledge_lifecycle_assertion.py
A	docs/architecture/<future implementation review document>.md
```

The future implementation review document path must be separately declared by that task.

No existing file modification is approved.

## 32. Evidence boundary for implementation

The future implementation task must produce a fresh external TXT report outside the repository.

It must include the exact executed script, complete snapshots of both new code files, the new implementation review document, the committed Phase 39 contract documents, relevant governed-Knowledge analog modules and tests, actual SHA-256 fingerprints, actual test commands, actual test counts, exact Git scope, and one final marker block.

The report must be strict UTF-8 without BOM, LF-only, and final-LF terminated.

## 33. Failure boundary

Any implementation deviation from the exact fields, order, symbols, constants, validation messages, validation order, identity projection, canonicalization, file scope, initializer decision, or test boundary requires correction before commit.

A failed targeted test or regression test blocks commit.

No automatic fallback, broad refactor, compatibility shim, or scope expansion is approved.

## 34. Repository, persistence, and runtime exclusions

The approved implementation slice creates no repository, repository protocol, admission operation, duplicate policy, idempotency rule, transaction boundary, lock, concurrency behavior, persistence adapter, serializer, schema, migration, wire format, CLI, API, callback, dispatch, retry, filesystem action, database action, network action, or runtime integration.

## 35. Acceptance, interpretation, transition, and current-state exclusions

The approved slice does not derive lifecycle from acceptance decisions or acceptance-history interpretation.

It creates no lifecycle interpreter, completeness declaration, contradiction classification, transition event, transition execution, prior state, resulting state, current state, current-effective flag, supersession, withdrawal, invalidation, or winner selection.

## 36. Business, creative, Prompt, and AI exclusions

The approved slice grants no business, creative, legal, compliance, publication, campaign, marketing, Prompt Candidate, Prompt generation, AI inference, embedding, recommendation, or external-action authority.

## 37. Implementation authorization

Exactly one future minimum implementation slice is authorized after PR-040A passes independent evidence review and is committed and pushed.

Approved production files: one.

Approved test files: one.

Approved existing-file modifications: zero.

Implementation executed by PR-040A: no.

## 38. Future implementation subject

The selected boundary makes exactly one future implementation subject eligible:

```text
governed_knowledge_lifecycle_assertion_minimum_implementation
```

That implementation is not started automatically by PR-040A.

## 39. Risks deferred

Deferred risks include package-level public exports, diagnostics, compatibility aliases, lifecycle vocabulary, lifecycle interpretation, completeness, contradiction classification, transition execution, current-state projection, repository admission, persistence, serialization, migration, recovery, business use, creative use, Prompt use, AI use, and runtime integration.

## 40. Definition of Done

PR-040A is complete when:

- the official Phase 39 checkpoint and tag are verified locally and remotely;
- the Phase 40 branch is synchronized and clean;
- accepted PR-039B evidence is verified exactly;
- committed PR-039A and PR-039B fingerprints are verified;
- no lifecycle assertion implementation or test file exists;
- relevant governed-Knowledge analog modules and tests are inspected;
- every implementation candidate is evaluated consistently;
- exactly one minimum implementation boundary is selected;
- exact production path, test path, public symbol set, private upstream-version alias, constants, fields, order, projection, canonicalization, validation messages, validation precedence, and test matrix are locked;
- non-finite exact-float rejection is locked separately from unsupported exact-type rejection;
- package initializer modification is explicitly prohibited;
- exactly one architecture document is added;
- no production or test file changes;
- no tests or project interpreter run;
- no Git mutation command runs;
- the external report provides complete exact evidence;
- the future implementation subject is eligible but not automatically started.

## 41. Final decision

# SELECTED IMPLEMENTATION BOUNDARY: MINIMUM STANDALONE IMMUTABLE GOVERNED-KNOWLEDGE LIFECYCLE ASSERTION DOMAIN SLICE

PR-040A authorizes exactly one future implementation slice after independent acceptance and commit of this architecture review.

PR-040A does not implement the slice and does not authorize diagnostics, package initializer changes, interpretation, transition execution, current-state projection, repository admission, persistence, serialization, business behavior, creative behavior, Prompt behavior, AI behavior, or runtime integration.
