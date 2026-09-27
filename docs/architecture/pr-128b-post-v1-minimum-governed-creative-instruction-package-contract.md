# PR-128B — Post-v1 Minimum Governed Creative Instruction Package Contract

## 1. Status and purpose

This document defines the minimum post-v1 **Prompt / Instruction Intelligence Foundation** contract for RCIS/RIE.

The smallest gap selected by PR-128A is:

`MINIMUM_GOVERNED_CREATIVE_INSTRUCTION_PACKAGE_CONTRACT`

The contract introduces one deterministic, provider-neutral, application-layer package that combines:

- the already-published `CreativeProductProfile`;
- the already-published `CreativeAssetRoleProfile`;
- the existing operator-authored `CreativePromptBrief`;
- provenance;
- unknown state;
- conflict state.

The package is a structured **instruction candidate**, not an approved instruction, not a generated image request, and not a replacement for existing authorities.

This is an architecture contract only.

---

## 2. Controlling post-v1 context

At contract initiation, the current post-v1 development head is:

`78697cb297333474f1f035935d1e02596bc67c93`

The historical RCIS v1 release identity remains unchanged:

- release tag: `v0.1.0`
- tag object: `b07d821434bffa6a8adde4cf0944ea227be2c6ce`
- peeled release target: `33cad5777dfc61aefe44db1bcc779c49b1490fd0`

The following post-v1 foundations are already closed and independently published:

1. Creative Product Profile Foundation.
2. Creative Asset Role Foundation.

PR-128A also verified that RCIS already contains:

- a grounded prompt composer;
- prompt-candidate capability;
- workflow instruction-authority semantics;
- a visual-generation-provider seam;
- `PROMPT_CANDIDATE` / `APPROVED_INSTRUCTION` workflow vocabulary.

PR-128A verified that RCIS does **not** yet contain one governed integrated creative instruction package that combines the two new post-v1 intelligence foundations with operator creative intent.

This contract fills only that gap.

---

## 3. Authority model

### 3.1 Product Intelligence remains product-truth authority

Product Intelligence remains authoritative for factual product and variant truth.

The instruction package MUST NOT:

- invent product facts;
- infer product facts from creative intent;
- infer product facts from asset pixels;
- reinterpret freeform notes as product truth;
- widen variant facts into product-wide facts;
- override Product Intelligence.

### 3.2 Creative Product Profile remains preserve / vary / prohibit authority

The published `CreativeProductProfile` remains authoritative for:

- `IDENTITY_CRITICAL`;
- `PRESERVE`;
- `MAY_VARY`;
- `PROHIBIT`.

The instruction package may deterministically carry these rules forward into structured instruction sections.

It MUST NOT:

- weaken a preservation rule;
- turn an unknown into `MAY_VARY`;
- turn operator preference into product authority;
- suppress a prohibition;
- promote a creative preference over an identity-critical requirement.

### 3.3 Creative Asset Role Profile remains visual-reference-use authority

The published `CreativeAssetRoleProfile` remains authoritative for explicit creative-use semantics of governed reference assets.

The instruction package may carry forward:

- exact asset identity;
- exact asset version identity;
- creative role;
- view semantics;
- reference strength;
- support/provenance references.

The instruction package MUST NOT:

- invent an asset role;
- infer a view from pixels or filenames;
- widen asset rights;
- make an ineligible asset eligible;
- change asset approval status;
- substitute another asset version;
- promote `CONTEXT_REFERENCE` into product-identity authority.

### 3.4 Existing rights and use eligibility remain authoritative

Existing governed asset rights and use-eligibility mechanisms remain authoritative.

The instruction package has zero authority to widen rights or eligibility.

If an asset is unavailable under the existing governed boundary, package construction MUST NOT make it usable.

### 3.5 Operator creative brief remains intent, not truth authority

The existing `CreativePromptBrief` remains an operator creative-intent input.

Its fields may include:

- objective;
- deliverable;
- environment;
- camera angle;
- shot type;
- lighting style;
- composition;
- mood/style;
- aspect ratio;
- orientation;
- product emphasis;
- operator preserve constraints;
- operator avoid constraints;
- selected reference asset IDs;
- freeform notes.

These fields express creative intent.

They MUST NOT be treated as product truth or asset-rights authority.

---

## 4. Instruction authority is fixed to `PROMPT_CANDIDATE`

The exact first-slice instruction authority is:

`PROMPT_CANDIDATE`

Every first-slice package MUST identify itself as a prompt/instruction candidate.

The package MUST NOT claim:

`APPROVED_INSTRUCTION`

Construction of a valid package does not constitute approval.

The package does not perform an approval transition.

A later workflow or approval boundary may decide whether an instruction becomes approved. That later authority is outside this contract.

---

## 5. Provider-neutral boundary

The package MUST be provider-neutral.

It MUST NOT contain required semantics that depend on:

- OpenAI;
- Adobe;
- Midjourney;
- Stable Diffusion;
- Flux;
- ComfyUI;
- any provider-specific parameter;
- any provider-specific image-weight syntax;
- any provider-specific negative-prompt syntax;
- any provider-specific seed/sampler/scheduler;
- any API credential;
- any model name.

Provider-specific adaptation belongs after this package and requires a separate authorized boundary.

---

## 6. First-slice application boundary

The first implementation belongs in the application layer.

Candidate implementation path:

`src/rie/application/creative_instruction_package.py`

Candidate focused test path:

`tests/application/test_creative_instruction_package.py`

The first implementation MUST be:

- framework-neutral;
- deterministic;
- model-free;
- provider-neutral;
- non-persistent;
- side-effect free;
- repository-write free;
- UI independent;
- Gate17 independent.

It MAY import and consume existing application-layer immutable values, including:

- `CreativeProductProfile`;
- `CreativeAssetRoleProfile`;
- `CreativePromptBrief`.

It MUST NOT mutate those values.

---

## 7. Minimum structured package sections

A first-slice package must expose distinct structured sections for:

1. product preservation / identity requirements;
2. product variation permissions;
3. product prohibitions;
4. visual reference-use directives;
5. operator creative intent;
6. unknown topics;
7. conflicts;
8. provenance;
9. instruction readiness;
10. instruction authority.

These sections MUST remain distinguishable.

The first implementation MUST NOT collapse all authority into one untyped prompt string.

---

## 8. Product instruction directives

A normalized product directive should preserve the controlling Creative Product Profile rule identity and kind.

A representation equivalent to the following is appropriate:

```python
@dataclass(frozen=True, slots=True)
class CreativeInstructionProductDirective:
    rule_id: str
    rule_kind: str
    subject: str
    instruction_value: str
    support_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
```

The exact Python field names may vary only if the observable contract remains equivalent.

### 8.1 Allowed source kinds

The directive MUST derive only from these Creative Product Profile rule kinds:

- `IDENTITY_CRITICAL`;
- `PRESERVE`;
- `MAY_VARY`;
- `PROHIBIT`.

No additional authority kind may be invented in the first slice.

### 8.2 Deterministic carry-forward

The instruction layer may normalize wording or ordering only when the semantic authority is unchanged.

It MUST NOT reinterpret:

- `PRESERVE` as optional;
- `PROHIBIT` as preference;
- `MAY_VARY` as required variation;
- `IDENTITY_CRITICAL` as stylistic suggestion.

---

## 9. Visual reference instruction directives

A normalized asset instruction directive should preserve the exact Creative Asset Role directive identity.

A representation equivalent to the following is appropriate:

```python
@dataclass(frozen=True, slots=True)
class CreativeInstructionAssetDirective:
    directive_id: str
    asset_id: str
    asset_version_identity: str
    role_kind: str
    view_kind: str
    reference_strength: str
    support_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
```

No field in this derived directive may widen authority relative to the input Asset Role Profile.

The package MUST preserve exact asset-version binding.

---

## 10. Operator creative intent section

The package should expose an immutable snapshot equivalent to the existing `CreativePromptBrief`.

The first slice SHOULD reuse `CreativePromptBrief` directly rather than creating a competing brief authority.

Operator intent may add creative preferences, including:

- scene/environment;
- shot/camera;
- lighting;
- composition;
- mood/style;
- output framing;
- operator preserve requests;
- operator avoid requests;
- selected governed reference assets;
- freeform notes.

Operator intent MUST NOT remove, weaken, or contradict authoritative product rules silently.

---

## 11. Relationship between operator preserve/avoid constraints and product rules

Operator constraints are additive creative restrictions.

They are not Product Intelligence facts.

### 11.1 Operator preserve constraints

An operator preserve constraint may strengthen caution.

It MUST NOT be treated as evidence that the corresponding property is a grounded product fact unless Product Intelligence / Creative Product Profile already supports that authority.

### 11.2 Operator avoid constraints

An operator avoid constraint may add a creative exclusion.

It MUST NOT convert that exclusion into product truth.

### 11.3 Conflict handling

If operator intent explicitly conflicts with an authoritative product rule, the package MUST be `BLOCKED`.

Examples:

- operator asks to change an `IDENTITY_CRITICAL` subject;
- operator asks to vary something explicitly `PRESERVE`;
- operator requests something explicitly `PROHIBIT`.

The first slice MUST NOT silently prefer operator intent.

---

## 12. Selected reference assets

`CreativePromptBrief.selected_reference_asset_ids` may be used only as a selection over the supplied Creative Asset Role Profile.

For every selected asset ID:

- at least one explicit Asset Role directive MUST exist;
- the asset identity MUST match the package product/variant context;
- exact asset-version binding MUST remain available;
- the role assignment MUST remain explicit.

A selected asset with no Asset Role directive MUST fail closed.

An unselected Asset Role directive may remain present in the source profile without becoming an active instruction reference.

The package MUST distinguish:

- available governed role directives;
- actively selected instruction references.

---

## 13. No implicit reference promotion

The package MUST NOT infer reference priority from:

- selected-list ordering;
- filename;
- UI list order;
- filesystem order;
- preview content;
- image similarity.

Only explicit `reference_strength` from Asset Role Intelligence controls reference strength.

---

## 14. Package readiness

The exact first-slice readiness values are:

- `READY`;
- `BLOCKED`.

Readiness is not approval.

`READY` means the structured candidate is internally consistent enough to be handed to a later authorized boundary.

`BLOCKED` means the candidate preserves unresolved state and MUST NOT be presented as ready for generation.

---

## 15. Structural failures versus semantic blocking

The builder MUST distinguish malformed construction from valid-but-blocked semantic state.

### 15.1 Structural construction errors

Construction MUST fail closed with a contract error for conditions such as:

- missing package identity;
- malformed product or variant identity;
- product-profile identity mismatch;
- asset-role-profile identity mismatch;
- duplicate directive identity;
- selected asset absent from the Asset Role Profile;
- corrupted exact asset-version identity;
- unsupported rule/role/view/strength kind;
- unsupported instruction authority;
- caller attempts `APPROVED_INSTRUCTION`.

### 15.2 Semantic blocking

A package may be constructed with `readiness=BLOCKED` when the supplied governed inputs are structurally valid but contain unresolved semantic state, including:

- product profile conflicts;
- asset role profile conflicts;
- explicit operator intent conflict with authoritative product rules;
- required instruction context explicitly marked unknown;
- selected references whose governed semantic support is incomplete but structurally represented as unknown.

Blocked state MUST preserve the reasons.

---

## 16. Unknown preservation

Unknowns are first-class output.

Unknown topics from:

- Creative Product Profile;
- Creative Asset Role Profile;
- explicit instruction-layer validation;

MUST be preserved.

The instruction layer MUST NOT convert unknowns into creative permissions.

In particular:

absence of a product rule MUST NOT be interpreted as `MAY_VARY`.

Absence of an asset role MUST NOT be interpreted as a usable generic reference.

---

## 17. Conflict preservation

Conflicts from the two source profiles MUST remain visible in the package.

Instruction-layer conflicts MUST also be explicit.

The package MUST NOT:

- drop conflicts;
- hide them inside freeform text;
- report `READY` while a blocking conflict exists.

---

## 18. Provenance preservation

The package MUST expose provenance sufficient to trace its authoritative sections back to their supplied governed inputs.

At minimum:

- product directives preserve product-rule support/provenance;
- asset directives preserve asset-role support/provenance;
- package-level provenance is the deterministic union of reachable source provenance plus explicit instruction-layer support.

The package MUST NOT fabricate provenance.

A caller-supplied declared provenance set that is not reachable from the supplied governed inputs MUST fail closed.

---

## 19. `CreativeInstructionPackage`

The first implementation should expose an immutable aggregate equivalent to:

```python
@dataclass(frozen=True, slots=True)
class CreativeInstructionPackage:
    package_id: str
    package_version: str
    product_id: str
    variant_id: str
    instruction_authority: str
    readiness: str
    product_directives: tuple[CreativeInstructionProductDirective, ...]
    active_asset_directives: tuple[CreativeInstructionAssetDirective, ...]
    creative_brief: CreativePromptBrief
    unknown_topics: tuple[str, ...]
    conflicts: tuple[str, ...]
    provenance_refs: tuple[str, ...]
```

The exact Python representation may vary only if the observable contract remains equivalent.

The package is a derived application value.

It is not:

- an approval record;
- a persisted prompt record;
- a workflow transition;
- a provider request;
- a generated-result record;
- a release decision.

---

## 20. Builder contract

A future first-slice builder should be equivalent to:

```python
class CreativeInstructionPackageBuilder:
    def build(
        self,
        *,
        package_id: str,
        package_version: str,
        product_id: str,
        variant_id: str,
        product_profile: CreativeProductProfile,
        asset_role_profile: CreativeAssetRoleProfile,
        creative_brief: CreativePromptBrief,
    ) -> CreativeInstructionPackage:
        ...
```

The exact argument ordering is not controlling.

The controlling requirements are:

- exact product/variant alignment;
- deterministic product-rule carry-forward;
- deterministic asset-role carry-forward;
- explicit selected-reference resolution;
- unknown/conflict preservation;
- provenance preservation;
- fixed `PROMPT_CANDIDATE` authority;
- deterministic readiness;
- no provider execution;
- no persistence.

---

## 21. Product / variant alignment

The builder MUST require one exact `(product_id, variant_id)` context.

The following must match:

- requested package context;
- Creative Product Profile context;
- Creative Asset Role Profile context.

Mismatch MUST fail closed.

No cross-variant scope widening is allowed.

---

## 22. Deterministic ordering

Equivalent input MUST produce equivalent output.

Canonical ordering SHOULD be deterministic.

Recommended ordering:

### 22.1 Product directives

`(rule_kind, subject, rule_id)`

### 22.2 Active asset directives

`(role_kind, view_kind, reference_strength, asset_id, directive_id)`

### 22.3 Unknowns, conflicts, provenance

Stable deduplicated lexical ordering is acceptable when source ordering is not itself authoritative.

The builder MUST NOT depend on set iteration, filesystem order, or UI ordering.

---

## 23. Instruction package versus prompt text

This package is not required to emit one rendered prompt string.

A later deterministic renderer may transform the provider-neutral package into:

- a textual prompt candidate;
- a provider-neutral instruction document;
- a provider-adapter request.

That later renderer MUST preserve this package's authority and conflict/readiness state.

The existing `CreativePromptComposer` remains unchanged by this contract.

No migration of existing prompt-composer behavior is authorized here.

---

## 24. Relationship to existing grounded prompt composer

The existing grounded prompt composer is a valuable compatibility and product capability.

This contract does not replace or mutate it.

The new package is a narrower governance layer that explicitly integrates the post-v1 Creative Product Profile and Creative Asset Role Profile.

A later integration may:

- have the existing composer consume a verified package;
- add a new deterministic renderer;
- preserve the existing UI while changing the internal source of prompt text.

That choice requires a later explicit boundary review.

---

## 25. Relationship to existing prompt-candidate capability

Existing prompt-candidate records remain separate.

Construction of `CreativeInstructionPackage` does not persist or publish a prompt candidate.

A later adapter may create or reference a prompt candidate using the package.

That adapter is outside this contract.

---

## 26. Relationship to workflow instruction authority

The existing creative workflow distinguishes:

- `PROMPT_CANDIDATE`;
- `APPROVED_INSTRUCTION`.

This contract intentionally aligns first-slice package authority with:

`PROMPT_CANDIDATE`

The package MUST NOT create an `APPROVED_INSTRUCTION`.

Approval remains a separate governed decision.

---

## 27. Relationship to visual generation provider

The existing visual-generation-provider seam remains untouched.

This package MUST NOT call `generate`.

The package MUST NOT construct a provider-specific request.

A later provider adapter may consume only a `READY` package or an authorized downstream derivative.

Gate17 remains the later vertical integration boundary.

---

## 28. Relationship to Gate17

Gate17 remains deferred.

PR-128B does not authorize:

- provider integration;
- generator execution;
- credential use;
- image generation;
- image editing;
- automatic generation retries;
- provider-specific prompt conversion;
- provider-specific asset weighting.

Gate17 should consume the completed intelligence foundation later.

It should not define the intelligence foundation.

---

## 29. Relationship to real RSV assets

Real RSV asset/product integration remains later.

This contract does not require a real RSV intake.

The first implementation and focused tests MUST be executable with synthetic/minimal immutable values.

No real RSV asset processing is authorized by this contract.

---

## 30. Persistence boundary

The first implementation MUST NOT persist `CreativeInstructionPackage`.

It MUST NOT mutate:

- Product Intelligence;
- Creative Product Profile;
- Creative Asset Role Profile;
- governed asset records;
- rights;
- eligibility;
- approval records;
- prompt-candidate storage;
- creative workflow state.

Any persistence requires a separate explicit contract.

---

## 31. UI boundary

No UI change is required by the first slice.

The current Create workspace may remain unchanged.

A future integration may expose package readiness, conflicts, structured directives, or rendered output, but that is outside this contract.

---

## 32. Security and fail-closed posture

The implementation must fail closed on unsupported authority or malformed identity.

No hidden fallback may convert:

- unknown → permission;
- conflict → ready;
- prompt candidate → approved instruction;
- filename → asset role;
- asset selection → reference strength;
- freeform note → product truth;
- ineligible asset → usable reference;
- missing exact version → latest version.

---

## 33. Minimum focused tests

The first implementation test file should prove at least:

1. a valid package combines Product Profile + Asset Role Profile + CreativePromptBrief;
2. package authority is exactly `PROMPT_CANDIDATE`;
3. caller cannot request `APPROVED_INSTRUCTION`;
4. product directives preserve all four Product Profile rule kinds;
5. selected asset references preserve exact asset version identity;
6. selected asset without Asset Role directive fails closed;
7. product-profile product mismatch fails closed;
8. product-profile variant mismatch fails closed;
9. asset-role-profile product mismatch fails closed;
10. asset-role-profile variant mismatch fails closed;
11. unknown topics from both profiles are preserved;
12. conflicts from both profiles cause `BLOCKED`;
13. explicit operator/product-rule conflict causes `BLOCKED`;
14. no blocking conflict yields `READY`;
15. operator preserve constraints do not become product facts;
16. operator avoid constraints do not become product facts;
17. asset role/view/strength semantics are preserved exactly;
18. active asset ordering is deterministic;
19. product directive ordering is deterministic;
20. provenance is the deterministic reachable union;
21. unreachable declared provenance fails closed if declared provenance is supported;
22. empty selected reference list is valid;
23. unselected governed asset-role directives do not become active references;
24. package construction is deterministic;
25. source is framework-neutral, provider-neutral, model-free, and non-persistent;
26. source does not call the visual-generation provider;
27. source does not mutate the existing creative prompt composer;
28. package readiness is not treated as approval.

Focused tests do not require real RSV assets.

---

## 34. Bounded upstream compatibility tests

A future implementation slice should run environment-independent bounded tests for the nearest existing boundaries, such as:

- Creative Product Profile;
- Creative Asset Role Profile;
- Creative Prompt Composer;
- visual generation provider protocol/value contract;
- governed creative workflow request instruction-authority semantics.

Environment-dependent tests must remain explicitly disclosed rather than silently treated as passed.

No full-suite-green claim is implied by bounded compatibility tests.

---

## 35. Out of scope

PR-128B does not authorize:

- source implementation;
- test implementation;
- existing path modification;
- Creative Prompt Composer mutation;
- prompt-candidate persistence;
- workflow mutation;
- UI mutation;
- asset registry mutation;
- rights mutation;
- eligibility mutation;
- approval mutation;
- provider request construction;
- provider integration;
- model execution;
- Gate17 implementation;
- real RSV asset processing;
- automatic prompt optimization;
- automatic semantic image understanding;
- AI-assisted fidelity evaluation.

---

## 36. Definition of done for this contract

This contract is complete when it unambiguously establishes:

- one provider-neutral structured package integrates the two post-v1 intelligence foundations with operator creative intent;
- Product Intelligence remains product-truth authority;
- Creative Product Profile remains preserve/vary/prohibit authority;
- Creative Asset Role Profile remains visual-reference-use authority;
- operator brief remains intent rather than truth authority;
- instruction authority is always `PROMPT_CANDIDATE` in the first slice;
- `APPROVED_INSTRUCTION` cannot be constructed by this builder;
- unknowns and conflicts remain explicit;
- blocking conflicts cannot report `READY`;
- selected reference assets require explicit Asset Role semantics;
- exact asset-version binding is preserved;
- provenance remains reachable and non-fabricated;
- construction is deterministic and non-persistent;
- existing prompt composer remains unchanged;
- provider execution remains deferred;
- Gate17 remains deferred;
- real RSV asset processing remains unauthorized.

---

## 37. Next decision after contract materialization

After exact one-path materialization and read-only boundary review, the expected next decision is:

`PREPARE_EXACT_TWO_PATH_CREATIVE_INSTRUCTION_PACKAGE_IMPLEMENTATION_PROPOSAL`

Candidate implementation paths:

- `src/rie/application/creative_instruction_package.py`
- `tests/application/test_creative_instruction_package.py`

No implementation authority is granted by this architecture document.
