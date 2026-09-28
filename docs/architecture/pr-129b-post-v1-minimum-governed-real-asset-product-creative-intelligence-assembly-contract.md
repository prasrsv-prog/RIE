# PR-129B — Post-v1 Minimum Governed Real Asset / Product Creative Intelligence Assembly Contract

## 1. Status and purpose

This document defines the minimum application-layer contract for assembling already-governed real product intelligence, governed visual-reference assets, explicit creative asset-role semantics, the governed Creative Product Profile, and the governed Creative Instruction Package into one deterministic creative-intelligence result.

This contract is intentionally narrow. It closes the smallest gap selected by PR-129A-C1:

`MINIMUM_GOVERNED_REAL_ASSET_PRODUCT_CREATIVE_INTELLIGENCE_ASSEMBLY_CONTRACT`

It does not authorize a generator, provider request, provider execution, workflow mutation, UI mutation, persistence mutation, model inference, Gate17 implementation, or real RSV production processing.

## 2. Controlling published foundations

The implementation governed by this contract must reuse, not replace, the published foundations already present at post-v1 head `aca7db1a9fff74562a3df4b6593b8d901b1e3691`:

1. `ProductIntelligenceQuery` remains the product-truth read authority.
2. `VisualReferenceAssetQuery` and the existing governed visual-reference / rights / use-eligibility boundaries remain the visual-reference read authority.
3. `CreativeProductProfileBuilder` remains the authority for the IDENTITY_CRITICAL / PRESERVE / MAY_VARY / PROHIBIT creative-product constraint profile.
4. `CreativeAssetRoleProfileBuilder` remains the authority for explicit creative asset role, view, and reference-strength semantics.
5. `CreativeInstructionPackageBuilder` remains the authority for a provider-neutral instruction package whose authority is exactly `PROMPT_CANDIDATE`.
6. Existing `CreativePromptBrief` is reused directly. This contract does not define a replacement brief type.

No assembly implementation may promote itself above these authorities.

## 3. Application-layer location

The intended first implementation layer is:

`src/rie/application/real_asset_product_creative_intelligence_assembly.py`

The intended focused test path is:

`tests/application/test_real_asset_product_creative_intelligence_assembly.py`

The first implementation must be framework-neutral, deterministic, model-free, non-persistent, provider-neutral, side-effect-free except for reads performed by existing query boundaries, and independent of the UI and Gate17.

This PR-129B contract does not authorize those implementation paths to be created yet.

## 4. Required assembly inputs

The assembly request must identify exactly one product / variant creative-intelligence task and must contain or receive:

- `product_id`;
- `variant_id`;
- one existing `CreativePromptBrief`;
- zero or more selected governed visual-reference asset identifiers;
- explicit creative asset-role directives for every selected asset that will participate in the instruction package;
- the existing query / builder dependencies, either injected directly or constructed by a narrowly-scoped factory that delegates to the existing public boundaries.

The request must not contain raw image bytes as semantic authority.

The request must not use filenames as semantic authority.

The request must not permit implicit role, view, strength, product-identity, or preserve/vary/prohibit inference.

## 5. Explicit asset-role directive rule

Creative asset-role semantics are never inferred by this assembly.

For every selected visual-reference asset used by the assembly, the caller must provide an explicit semantic directive that binds the intended role semantics to the exact selected governed asset identity and version.

The directive must reuse the semantic vocabulary and validation already enforced by `CreativeAssetRoleProfileBuilder`, including the existing role, view, reference-strength, grounded-support, exact-asset-version, and product/variant-alignment rules.

The assembly must not create a competing role taxonomy.

The assembly must not widen or reinterpret existing role semantics.

The assembly must not derive role, view, or reference strength from:

- pixels;
- image embeddings;
- model inference;
- filenames;
- directory names;
- extension or MIME type;
- aspect ratio;
- preview bytes;
- EXIF or other media metadata;
- UI selection order;
- asset ordering alone.

A selected asset without an explicit compatible directive is blocking and cannot become a READY instruction candidate.

An explicit directive that does not bind to the exact governed selected asset version is blocking.

An explicit directive whose product or variant does not match the assembly request is blocking.

Unknown semantics remain unknown and are not converted into permission.

## 6. Product truth resolution

Product truth must be obtained only through the existing `ProductIntelligenceQuery` boundary.

The assembly must not read product truth directly from:

- evidence storage;
- SQLite;
- persisted JSON files;
- source documents;
- raw intake folders;
- filesystem naming conventions;
- the UI.

The assembly must request the exact product / variant selected by the caller.

If the product or variant cannot be resolved by the existing Product Intelligence boundary, the assembly fails closed or returns a BLOCKED result according to the existing builder contract. It must not fabricate missing product facts.

The resulting Creative Product Profile must be built by the existing `CreativeProductProfileBuilder`. The assembly must preserve the existing four rule kinds and their provenance, unknown, and conflict semantics.

## 7. Governed visual-reference resolution

Visual-reference assets must be obtained only through `VisualReferenceAssetQuery` and the existing governed bridge / rights / use-eligibility boundaries on which that query depends.

For a requested product / variant, the assembly may only consider assets returned as governed visual references for that same product / variant.

The assembly must preserve the exact governed asset identity and exact asset version.

An asset not returned by the governed visual-reference boundary is not eligible merely because its path, filename, pixels, metadata, or UI state resembles an eligible asset.

The assembly must not widen rights or use eligibility.

The assembly must not mutate asset records, rights, eligibility, or registry state.

## 8. Selected asset resolution

For each requested selected reference identifier:

1. resolve it against the governed visual-reference result for the exact product / variant;
2. require an exact unique match;
3. preserve the governed asset identity and version;
4. require the existing rights / use-eligibility decision to remain valid;
5. require one explicit compatible asset-role directive;
6. construct the Creative Asset Role Profile only through `CreativeAssetRoleProfileBuilder`.

Missing selected assets, duplicate ambiguous matches, mismatched versions, ineligible assets, missing directives, conflicting directives, or product / variant mismatches are blocking.

The assembly may return diagnostic unknowns / conflicts, but it must not silently drop a caller-selected asset and still claim READY unless the existing Instruction Package contract explicitly treats that selection as non-required. The default contract interpretation is fail closed for explicitly selected references.

## 9. Creative Product Profile construction

The assembly must construct or receive exactly one Creative Product Profile for the requested product / variant.

When constructed by the assembly, it must use the existing `CreativeProductProfileBuilder` against Product Intelligence-derived governed inputs.

The assembly must not mutate the resulting profile.

The profile remains the only assembly input that authoritatively expresses:

- identity-critical constraints;
- preserve constraints;
- may-vary constraints;
- prohibited transformations.

The assembly must not infer MAY_VARY from absence of a prohibition.

## 10. Creative Asset Role Profile construction

For each selected asset, the assembly constructs exactly one compatible Creative Asset Role Profile through the existing `CreativeAssetRoleProfileBuilder`, using:

- the exact governed selected asset facts already available from the existing visual-reference boundary;
- the explicit caller-provided role directive;
- the exact requested product / variant identity;
- the existing grounded-support / provenance inputs required by that builder.

If the existing builder rejects the input, the assembly must preserve that failure as blocking. The assembly must not bypass or duplicate builder validation.

## 11. Creative Instruction Package construction

After successful product-profile and selected-asset-role construction, the assembly invokes the existing `CreativeInstructionPackageBuilder`.

The instruction package receives:

- the Creative Product Profile;
- the applicable Creative Asset Role Profiles;
- the existing `CreativePromptBrief`;
- selected reference identity information required by the published Instruction Package contract;
- provenance, unknowns, and conflicts as required by that contract.

The resulting authority remains exactly:

`PROMPT_CANDIDATE`

The assembly is not authorized to construct `APPROVED_INSTRUCTION`.

The assembly is not authorized to construct a provider request.

The assembly is not authorized to invoke a provider.

## 12. Assembly result

The first implementation should expose an immutable result representing the whole assembly attempt.

The result must make the following observable without requiring UI or persistence:

- requested product ID;
- requested variant ID;
- resolved product identity;
- exact selected governed asset identities / versions;
- Creative Product Profile;
- Creative Asset Role Profiles;
- Creative Instruction Package when construction succeeds;
- readiness state;
- blocking reasons;
- unknowns;
- conflicts;
- reachable provenance.

The result may use the existing READY / BLOCKED semantics from the Instruction Package foundation. It must not introduce an approval state.

A READY assembly means only that the governed inputs are sufficiently resolved to form a `PROMPT_CANDIDATE`.

READY does not mean approved, published, persisted, executable, or provider-ready.

## 13. Determinism and ordering

For semantically identical governed inputs, the assembly result must be deterministic.

Ordering must not depend on filesystem enumeration order, hash-table iteration, UI selection order unless selection order is explicitly part of the caller request, or provider behavior.

The implementation must define deterministic ordering for multiple selected asset role profiles and preserve the ordering semantics required by the existing Instruction Package builder.

The assembly must not mutate its input objects.

## 14. Provenance, unknowns, and conflicts

Provenance remains first-class.

Every product constraint and asset-role semantic that contributes to the assembly must remain traceable through the existing profile / package provenance surfaces.

The assembly must not fabricate provenance.

Unknowns remain first-class and never become permissions.

Conflicts remain first-class. A blocking conflict prevents READY.

If existing foundations distinguish blocking from non-blocking conflicts, the assembly must preserve that distinction rather than invent a new one.

## 15. Real intake construction boundary

A later implementation may provide a convenience constructor or factory that accepts an intake root and composes existing real-data read boundaries, for example:

- `ProductIntelligenceQuery.from_intake_root(...)`;
- `VisualReferenceAssetQuery(...)` using that product query.

Such a factory is only composition.

It does not authorize the assembly module to enumerate the intake directory itself, open arbitrary media, inspect pixels, hash real assets for semantic inference, derive roles from filenames, or bypass the existing governed read boundaries.

Any real-frozen integration proof must be separately authorized and bounded.

This PR-129B contract materialization itself performs no real intake content read.

## 16. Fail-closed structural rules

The first implementation must fail closed for malformed or incompatible authority-bearing inputs, including at minimum:

- missing product ID;
- missing variant ID;
- unresolved product or variant;
- mismatched product / variant identities across profiles, assets, or directives;
- malformed Creative Product Profile authority;
- malformed Creative Asset Role Profile authority;
- malformed Creative Instruction Package authority;
- selected asset not present in governed visual references;
- selected asset version mismatch;
- ineligible governed asset;
- missing explicit asset-role directive;
- ambiguous or duplicate directive for the same exact asset version;
- unsupported role / view / reference-strength semantics;
- missing grounded support required by existing builders.

Structural failure must not be downgraded into a permissive unknown.

## 17. No duplicate authority

The assembly is an orchestrator, not a new truth engine.

It must not duplicate:

- Product Intelligence truth evaluation;
- governed rights evaluation;
- governed use-eligibility evaluation;
- Creative Product Profile classification;
- Creative Asset Role Profile semantic validation;
- Creative Instruction Package readiness / authority validation.

The implementation should delegate to existing public boundaries and keep adapter logic minimal.

## 18. No direct storage or media inspection

The assembly module must not import or access direct governed-storage implementations merely to reconstruct data already exposed through application boundaries.

The implementation must not require:

- direct repository persistence access;
- SQLite access;
- raw asset byte reads;
- image decoders;
- EXIF readers;
- OCR;
- computer vision;
- embeddings;
- generative or classification models.

These are outside the minimum integration foundation.

## 19. No mutation scope

The assembly is read-only with respect to existing governed project state.

It must not:

- modify Product Intelligence;
- modify governed asset records;
- modify rights;
- modify use eligibility;
- persist Creative Product Profiles;
- persist Creative Asset Role Profiles;
- persist Creative Instruction Packages;
- mutate workflow state;
- apply operator approval;
- mutate UI state;
- stage Git changes;
- publish releases.

Persistence and workflow integration require separate contracts.

## 20. Provider and Gate17 separation

The assembly contract ends at the governed `PROMPT_CANDIDATE` package.

Visual generation provider request construction is separate.

Provider execution is separate.

Gate17 vertical-slice implementation is separate and remains deferred until this Real Asset / Product Integration Foundation is closed and independently verified.

The real RSV pilot remains deferred until the integration foundation and Gate17 vertical slice are separately closed.

## 21. First implementation verification expectations

A later implementation proposal should be limited to the candidate source and focused test paths selected by PR-129A-C1 unless a read-only boundary review proves an additional path is strictly necessary.

Focused tests should cover at minimum:

- deterministic assembly for a valid product / variant;
- exact Product Intelligence delegation;
- exact governed visual-reference delegation;
- exact selected asset version preservation;
- explicit asset-role directive requirement;
- missing directive fail-closed behavior;
- product / variant mismatch fail-closed behavior;
- asset version mismatch fail-closed behavior;
- rights / eligibility non-widening;
- Product Profile builder delegation;
- Asset Role Profile builder delegation;
- Instruction Package builder delegation;
- final authority remains `PROMPT_CANDIDATE`;
- no approved instruction construction;
- no provider request or execution;
- no UI / workflow / persistence mutation;
- no pixel / filename / model inference;
- provenance / unknown / conflict preservation;
- deterministic multi-asset ordering.

Bounded upstream regression tests should include the published Product Profile, Asset Role Profile, Instruction Package, Product Intelligence query, visual-reference query / bridge, and use-eligibility boundaries selected by the later read-only implementation review.

No full-suite-green claim is implied.

## 22. PR-129B materialization boundary

PR-129B is authorized, after exact proposal approval, to materialize only this architecture contract at:

`docs/architecture/pr-129b-post-v1-minimum-governed-real-asset-product-creative-intelligence-assembly-contract.md`

PR-129B does not authorize:

- source implementation;
- tests;
- modification of tracked files;
- staging;
- commit;
- push;
- tag mutation;
- UI work;
- persistence work;
- workflow work;
- provider work;
- model execution;
- Gate17 implementation;
- real RSV asset processing.

After successful materialization, the next step is a separate read-only PR-129C contract / implementation-boundary review.
