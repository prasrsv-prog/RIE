# PR-127B — Post-v1 Minimum Governed Creative Asset Role Contract

## 1. Status and purpose

This document defines the minimum post-v1 **Asset Intelligence Foundation** contract for RCIS/RIE.

The contract introduces explicit creative-use semantics for already-governed visual reference assets. It does not create a new asset authority, does not interpret pixels, does not widen usage rights, and does not authorize generation.

The smallest gap selected by PR-127A is:

`MINIMUM_GOVERNED_CREATIVE_ASSET_ROLE_CONTRACT`

The purpose of this contract is to bridge:

`already-governed approved visual reference asset`

to:

`explicit creative role + explicit view semantics + explicit reference strength`

without changing the existing product-truth, asset-rights, eligibility, approval, prompt, workflow, or generator authorities.

This is an architecture contract only.

---

## 2. Controlling post-v1 context

The Creative Product Profile slice is already closed and independently published.

Current post-v1 development head at contract initiation:

`93cd240c287407fbf3e448689598202ac2370076`

Historical RCIS v1 release identity remains unchanged:

- release tag: `v0.1.0`
- tag object: `b07d821434bffa6a8adde4cf0944ea227be2c6ce`
- peeled release target: `33cad5777dfc61aefe44db1bcc779c49b1490fd0`

PR-127A established that the repository already has:

- an application-facing visual-reference capability;
- approved visual-reference asset reads;
- governed asset records;
- governed usage-rights representation;
- governed use-eligibility evaluation;
- a governed visual-reference read bridge.

PR-127A also established that the repository does **not** yet have governed creative asset-role semantics.

Therefore this contract must reuse existing governed asset truth instead of replacing it.

---

## 3. Authority model

### 3.1 Product truth authority

Product Intelligence remains authoritative for factual product and variant truth.

This contract MUST NOT:

- invent product facts;
- infer product facts from an image;
- override Product Intelligence;
- reinterpret an asset as evidence for a product fact;
- widen a variant fact into a product-wide fact.

### 3.2 Creative Product Profile authority

The published Creative Product Profile remains authoritative for:

- identity-critical requirements;
- preserve requirements;
- allowed variation;
- prohibited transformation.

Asset Intelligence MUST NOT override or weaken any Creative Product Profile rule.

A creative asset directive is descriptive of **how an approved asset may be used as a reference**, not permission to violate a product-preservation rule.

### 3.3 Asset rights and eligibility authority

Existing governed asset rights and use-eligibility mechanisms remain authoritative.

A creative asset directive:

- MUST reference an already-governed asset;
- MUST NOT create or widen rights;
- MUST NOT convert an ineligible asset into an eligible asset;
- MUST NOT change approval status;
- MUST NOT change source authority;
- MUST NOT change the asset's product or variant association;
- MUST NOT persist a new asset-library lifecycle state.

Creative role semantics are subordinate to existing rights and eligibility.

### 3.4 Human / explicit metadata authority for semantics

Creative role, view semantics, and reference strength MUST be explicitly supplied through an authorized application input or already-governed metadata source.

They MUST NOT be inferred from:

- image pixels;
- OCR;
- filename alone;
- directory name alone;
- EXIF alone;
- visual resemblance;
- model output;
- embedding similarity;
- prompt text;
- absence of other metadata.

A filename such as `front.png` is not, by itself, authority to assign `FRONT`.

---

## 4. First-slice application boundary

The first implementation belongs in the **application layer**.

Candidate implementation path:

`src/rie/application/creative_asset_role_profile.py`

Candidate focused test path:

`tests/application/test_creative_asset_role_profile.py`

The first implementation MUST be:

- framework-neutral;
- deterministic;
- side-effect free;
- model-free;
- generator-agnostic;
- non-persistent;
- repository-write free;
- UI independent;
- prompt-composer independent.

The implementation may consume application-facing governed visual-reference values and explicit semantic assignments, but it MUST NOT directly open storage, image files, databases, or external services.

---

## 5. Minimum domain vocabulary

The first slice defines three independent semantic dimensions:

1. **creative role**
2. **view semantics**
3. **reference strength**

These dimensions MUST remain explicit and must not be silently derived from each other.

---

## 6. Creative role kinds

The exact first-slice creative role kinds are:

### 6.1 `IDENTITY_ANCHOR`

The asset is an explicit visual reference for preserving recognizable product or variant identity.

This role may support faithful identity retention, but it does not create product truth.

### 6.2 `FORM_REFERENCE`

The asset is an explicit reference for product form, silhouette, geometry, or proportions.

This role does not authorize transformation outside Creative Product Profile constraints.

### 6.3 `SURFACE_DETAIL_REFERENCE`

The asset is an explicit reference for visible surface characteristics such as finish, material appearance, texture, print, label, marking, or local product detail.

The assignment MUST be explicit. The implementation MUST NOT inspect pixels to determine that the asset contains such detail.

### 6.4 `PACKAGING_REFERENCE`

The asset is an explicit reference for packaging, container, retail presentation, or included presentation elements.

Packaging reference authority MUST NOT be treated as product-body identity authority unless a separate explicit role assignment supports that use.

### 6.5 `CONTEXT_REFERENCE`

The asset is an explicit reference for environment, usage context, placement, staging, or non-product scene cues.

`CONTEXT_REFERENCE` MUST NOT be promoted into product identity, form, surface-detail, or packaging authority without another explicit assignment.

---

## 7. View semantics

The exact first-slice view kinds are:

- `UNSPECIFIED`
- `FRONT`
- `BACK`
- `LEFT`
- `RIGHT`
- `TOP`
- `BOTTOM`
- `THREE_QUARTER`
- `DETAIL`
- `PACKAGING`
- `CONTEXT`

`UNSPECIFIED` is valid and is preferable to unsupported inference.

A view kind is a semantic annotation only. It does not modify asset identity, rights, approval, or eligibility.

No view may be inferred from a filename, directory path, or pixel content in the first slice.

---

## 8. Reference strength

The exact first-slice reference strengths are:

### 8.1 `PRIMARY`

The asset is an explicitly designated primary reference for its assigned role in the profile.

`PRIMARY` means priority among references for the same creative use. It does not mean stronger legal rights, stronger approval, stronger product truth, or authority to override preservation constraints.

### 8.2 `SUPPORTING`

The asset is an explicitly designated supporting reference for its assigned role.

### 8.3 `CONTEXT_ONLY`

The asset may influence only contextual or scene-level reference use.

`CONTEXT_ONLY` MUST NOT be used with `IDENTITY_ANCHOR`, `FORM_REFERENCE`, `SURFACE_DETAIL_REFERENCE`, or `PACKAGING_REFERENCE`.

It is valid only with `CONTEXT_REFERENCE`.

---

## 9. `CreativeAssetRoleDirective`

The first implementation should expose an immutable value equivalent to:

```python
@dataclass(frozen=True, slots=True)
class CreativeAssetRoleDirective:
    directive_id: str
    asset_id: str
    asset_version_identity: str
    product_id: str
    variant_id: str
    role_kind: str
    view_kind: str
    reference_strength: str
    support_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
```

The exact Python representation may vary only if the observable contract remains equivalent.

### 9.1 Required identity fields

The following fields are required, non-empty, deterministic ASCII text:

- `directive_id`
- `asset_id`
- `asset_version_identity`
- `product_id`
- `variant_id`

`asset_version_identity` MUST identify the exact governed visual-reference version. Where the existing governed bridge exposes SHA256-based visual-reference version identity, that exact identity SHOULD be preserved.

### 9.2 Explicit role support

`support_refs` MUST contain at least one explicit support reference.

A directive with no explicit support MUST fail closed.

Support may identify, for example:

- an authorized human annotation record;
- an already-governed metadata record;
- an explicit operator assignment record;
- another deterministic application input whose authority is independently established.

Support MUST NOT be synthesized from the asset filename or image content.

### 9.3 Provenance

`provenance_refs` MUST remain attributable to the supplied explicit support.

A first-slice builder MUST NOT fabricate provenance.

If a caller declares provenance that is not reachable from the supplied support, construction MUST fail closed.

---

## 10. `CreativeAssetRoleProfile`

The first implementation should expose an immutable aggregate equivalent to:

```python
@dataclass(frozen=True, slots=True)
class CreativeAssetRoleProfile:
    profile_id: str
    profile_version: str
    product_id: str
    variant_id: str
    directives: tuple[CreativeAssetRoleDirective, ...]
    unknown_topics: tuple[str, ...]
    conflicts: tuple[str, ...]
    provenance_refs: tuple[str, ...]
```

The profile is an application-layer derived value.

It is not:

- a persisted asset registry;
- a replacement asset record;
- a rights decision;
- an approval decision;
- a prompt;
- a workflow request;
- a generator request.

---

## 11. Builder input contract

A future first-slice builder should conceptually accept:

1. a product/variant selection;
2. governed visual-reference assets already returned through the existing application-facing read boundary;
3. existing governed use-eligibility results where required by that boundary;
4. explicit creative-role directives;
5. optional explicit unknown/conflict inputs.

The builder MUST NOT scan directories or load arbitrary assets directly.

The builder MUST NOT inspect preview bytes.

The builder MUST NOT invoke a visual model.

---

## 12. Asset existence and version binding

Every directive MUST bind to an exact governed asset that exists in the supplied governed visual-reference set.

The builder MUST fail closed if:

- `asset_id` is unknown;
- `asset_version_identity` does not match the supplied governed asset version;
- product identity does not match;
- variant identity does not match;
- the asset is outside the supplied governed selection;
- the asset is not eligible under the existing governed eligibility boundary where eligibility is required.

Creative semantics MUST bind to an exact asset version, not merely an asset label.

A changed asset version requires a new explicit semantic binding.

---

## 13. Product and variant scope

The first slice is variant-specific.

A role profile is built for one explicit `(product_id, variant_id)` pair.

A directive for one variant MUST NOT be silently reused for another variant.

A product-level visual reference may only be reused across variants if an existing governed boundary explicitly exposes it for the selected variant or a later contract authorizes product-level role scope.

The first slice does not introduce scope widening.

---

## 14. Determinism and duplicate handling

For equivalent input, the builder MUST produce equivalent output.

The builder MUST reject:

- duplicate `directive_id`;
- exact duplicate semantic assignment with conflicting strength;
- incompatible role/strength combinations;
- multiple `PRIMARY` directives for the same exact role and view unless a later contract explicitly permits multi-primary semantics.

Input ordering MUST NOT change semantic output.

Canonical ordering SHOULD be deterministic by a stable tuple such as:

`(role_kind, view_kind, reference_strength, asset_id, directive_id)`

---

## 15. First-slice conflict rules

The minimum contract models only explicit structural conflicts.

The following MUST fail closed:

1. `CONTEXT_ONLY` with a non-`CONTEXT_REFERENCE` role.
2. `CONTEXT_REFERENCE` assigned `PRIMARY` for product identity authority through any implicit conversion.
3. Same directive identity with differing content.
4. Same exact `(asset_id, role_kind, view_kind)` assigned contradictory strengths.
5. More than one `PRIMARY` asset for the same exact `(role_kind, view_kind)` in one profile.
6. Asset version mismatch.
7. Product or variant mismatch.
8. Missing explicit support.

The first slice MUST NOT invent semantic conflicts from image analysis.

---

## 16. Unknown preservation

Unknowns are valid first-class output.

Examples include:

- view not explicitly known;
- no explicit identity anchor designated;
- no explicit surface-detail reference designated;
- role support unavailable;
- semantic assignment intentionally deferred.

Unknown information MUST remain unknown.

Absence of a role assignment MUST NOT be interpreted as permission to vary the corresponding product characteristic.

That authority belongs to the Creative Product Profile, not Asset Intelligence.

---

## 17. Relationship to Creative Product Profile

The Creative Product Profile and Creative Asset Role Profile are complementary.

A future instruction layer may use them together:

- Creative Product Profile says **what must be preserved, may vary, or is prohibited**.
- Creative Asset Role Profile says **which exact governed visual references are explicitly designated for which creative reference purposes**.

Asset role semantics MUST NOT override product rules.

Example:

- a `CONTEXT_REFERENCE` cannot authorize changing an identity-critical product attribute;
- a `FORM_REFERENCE` cannot authorize geometry variation prohibited by the product profile;
- an `IDENTITY_ANCHOR` does not create identity facts absent from Product Intelligence.

---

## 18. Relationship to existing visual-reference capability

The existing visual-reference query/read capability remains the source of available approved reference assets.

This contract MUST NOT duplicate:

- product/variant option lookup;
- approved visual-reference enumeration;
- preview loading;
- governed visual-reference version identity;
- rights/use eligibility evaluation;
- asset registry persistence.

A future builder should accept those existing read values rather than bypassing them.

---

## 19. Relationship to rights and use eligibility

Creative role assignment is meaningful only after the asset remains allowed by the existing governance boundary.

If an asset becomes ineligible, expired, revoked, replaced, or otherwise unavailable under existing asset governance, its creative role assignment MUST NOT make it usable.

Role semantics have zero authority to widen rights.

---

## 20. Relationship to Prompt Intelligence

Prompt Intelligence remains deferred.

This contract does not:

- modify `creative_prompt_composer.py`;
- produce a prompt;
- produce generator-specific syntax;
- select a generation provider;
- decide image weight parameters;
- inject image bytes into a generator request.

A future Prompt/Instruction Intelligence layer may consume a verified Creative Asset Role Profile.

That later layer must map role/view/strength semantics to provider-neutral instruction semantics before any provider-specific adapter is considered.

---

## 21. Relationship to Gate17

Gate17 remains deferred.

This contract does not authorize:

- generator integration;
- API calls;
- model execution;
- image generation;
- image editing;
- provider credential use;
- provider-specific reference weighting.

Gate17 should consume Asset Intelligence later; it should not define Asset Intelligence.

---

## 22. Relationship to real RSV assets

Real RSV asset processing remains unauthorized by this contract.

No real pilot directory, frozen intake, or production asset needs to be opened or processed to define or implement the first-slice application contract.

Synthetic or minimal application values are sufficient for focused tests.

A real RSV pilot remains later in the sequence after:

1. Creative Product Profile;
2. Asset Intelligence;
3. Prompt/Instruction Intelligence;
4. real product + asset preparation;
5. Gate17 vertical slice.

---

## 23. Persistence boundary

The first implementation MUST NOT persist `CreativeAssetRoleProfile`.

It MUST NOT mutate:

- `GovernedAssetRecord`;
- asset-library registry state;
- usage rights;
- eligibility results;
- approval records;
- creative workflow state.

Persistence, if ever required, needs a separate explicit contract.

---

## 24. UI boundary

No UI mutation is required for the first slice.

The existing Assets workspace may continue displaying approved reference metadata as it does today.

A future UI may expose explicit role annotation or inspection, but that is outside this contract.

---

## 25. Security and trust posture

The implementation must fail closed on malformed or unsupported semantic assignments.

It must not trust arbitrary strings as governed asset authority.

Exact asset identity and version binding are mandatory.

No hidden fallback may convert:

- unknown role → inferred role;
- unknown view → guessed view;
- missing support → filename-based support;
- ineligible asset → usable asset;
- missing primary reference → arbitrary first asset.

---

## 26. Candidate public API

A minimal future API may be equivalent to:

```python
class CreativeAssetRoleProfileBuilder:
    def build(
        self,
        *,
        product_id: str,
        variant_id: str,
        governed_assets: tuple[object, ...],
        directives: tuple[CreativeAssetRoleDirective, ...],
        unknown_topics: tuple[str, ...] = (),
        conflicts: tuple[str, ...] = (),
        profile_id: str,
        profile_version: str,
    ) -> CreativeAssetRoleProfile:
        ...
```

Exact argument ordering is not controlling.

The controlling requirements are:

- exact governed asset binding;
- explicit support;
- no unsupported inference;
- deterministic construction;
- fail-closed validation;
- non-persistence;
- no model execution.

---

## 27. Minimum focused tests

The first implementation test file should prove at least:

1. all five creative role kinds are accepted when explicitly supported;
2. all allowed view kinds are accepted;
3. all three reference strengths are accepted in valid combinations;
4. `CONTEXT_ONLY` is rejected for non-context roles;
5. missing support fails closed;
6. unknown asset ID fails closed;
7. asset version mismatch fails closed;
8. product mismatch fails closed;
9. variant mismatch fails closed;
10. duplicate directive ID fails closed;
11. contradictory strength assignment fails closed;
12. multiple primary references for the same role/view fail closed;
13. unknown view may remain `UNSPECIFIED`;
14. unknown topics and conflicts are preserved;
15. equivalent construction is deterministic;
16. source remains framework-neutral, model-free, and non-persistent;
17. no filename or image-content inference path exists.

Focused tests do not need real RSV assets.

---

## 28. Upstream compatibility tests

The implementation slice should also run bounded existing tests for:

- visual reference asset query/read behavior; and/or
- governed visual reference read bridge behavior; and/or
- governed asset use-eligibility behavior,

provided those tests are environment-independent.

Environment-dependent real frozen pilot tests must remain explicitly disclosed rather than silently treated as passed.

---

## 29. Out of scope

PR-127B does not authorize:

- source implementation;
- test implementation;
- source modification;
- UI modification;
- database/storage modification;
- asset registry mutation;
- rights mutation;
- eligibility mutation;
- prompt composer mutation;
- workflow mutation;
- generator integration;
- model execution;
- Gate17 implementation;
- real RSV asset processing;
- automatic image understanding;
- automatic view classification;
- automatic creative-role classification;
- embedding similarity;
- semantic search over pixels.

---

## 30. Definition of done for the contract

This contract is complete when it unambiguously establishes:

- the existing visual-reference and rights boundaries remain authoritative;
- creative semantics are explicit and support-backed;
- no pixel or filename inference is allowed;
- role/view/strength dimensions are modeled independently;
- exact governed asset version binding is mandatory;
- product/variant mismatch fails closed;
- rights/eligibility cannot be widened;
- unknowns remain unknown;
- implementation belongs in the application layer;
- first implementation is deterministic, model-free, non-persistent;
- Prompt Intelligence remains deferred;
- Gate17 remains deferred;
- real RSV asset processing remains unauthorized.

---

## 31. Next decision after contract materialization

After exact one-path materialization and read-only review, the expected next decision is:

`PREPARE_EXACT_TWO_PATH_CREATIVE_ASSET_ROLE_IMPLEMENTATION_PROPOSAL`

Candidate implementation paths:

- `src/rie/application/creative_asset_role_profile.py`
- `tests/application/test_creative_asset_role_profile.py`

No implementation authority is granted by this architecture document.
