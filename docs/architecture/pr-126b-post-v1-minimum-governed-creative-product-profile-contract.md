# PR-126B - Post-v1 Minimum Governed Creative Product Profile Contract

## 1. Status and scope

This document defines the first bounded architecture contract in the post-v1
RCIS Creative Intelligence Foundation track.

It is intentionally narrower than Gate 17, generator integration, semantic
multimodal reasoning, asset-role intelligence, prompt-provider optimization,
or a real RSV creative-productivity pilot.

Materializing this document does not implement runtime code, tests, UI,
persistence, model execution, image analysis, generator execution, asset
mutation, approval, or product release.

The selected smallest gap is:

`MINIMUM_GOVERNED_CREATIVE_PRODUCT_PROFILE_CONTRACT`

Its responsibility is to bridge already-grounded product truth into explicit,
auditable creative semantics without inventing unsupported product facts.

## 2. Governing release baseline

This post-v1 track begins only after the independently closed RCIS v1 release
chain.

The release baseline is:

- product: `RCIS v1`;
- package version: `0.1.0`;
- final release commit:
  `33cad5777dfc61aefe44db1bcc779c49b1490fd0`;
- final annotated product tag: `v0.1.0`;
- final tag object:
  `b07d821434bffa6a8adde4cf0944ea227be2c6ce`;
- release mode: `SOURCE_AND_GOVERNANCE_WITHOUT_BINARY_ATTACHMENT`.

PR-126A independently reconciled this release state and selected the Creative
Intelligence Foundation as the first post-v1 track.

## 3. Problem statement

RCIS v1 already exposes grounded Product Intelligence, approved visual
references, creative-brief fields, grounded prompt composition, governed
approval boundaries, governed creative workflow, and a generator-provider
protocol.

Those surfaces are not sufficient by themselves to answer an important
creative-production question:

> Which aspects of one exact product and variant must remain visually faithful,
> which aspects may vary creatively, and which transformations are explicitly
> prohibited?

A grounded fact is not automatically a creative rule.

An approved product photo is not automatically identified as a geometry,
graphic, color, detail, or hero reference.

A creative brief is not automatically evidence that a requested transformation
is safe for the represented product.

A prompt is not automatically a complete product-fidelity instruction.

The Creative Product Profile establishes the smallest governed structure needed
to make those distinctions explicit before later asset intelligence, prompt
intelligence, generator integration, and real-product pilot work.

## 4. Preserved authority separations

This contract preserves all existing RCIS separations, including:

- Source Material is not Evidence.
- Evidence is not Knowledge.
- Knowledge is not a business decision.
- Product Intelligence is not creative authorization.
- A product fact is not automatically an identity-critical creative rule.
- A preservation constraint is not an executed generator instruction.
- An approved product photo is not automatically a creative-reference role.
- A Creative Product Profile is not an approved prompt.
- A Creative Product Profile is not a generator request.
- A grounded prompt is not generator execution.
- Generated Output is not an Official Source.
- Generated Output is not an Accepted Asset.
- Generated Output is not an Approved Creative Asset.
- Workflow completion is not production publication.

No automatic promotion may collapse these distinctions.

## 5. Existing upstream inputs

A future Creative Product Profile implementation may consume only explicit,
already-accepted application-layer product intelligence.

The minimum upstream context is the existing
`ProductIntelligenceContext`, including exact values for:

- `product_id`;
- `variant_id`;
- product label;
- variant label;
- grounded fact groups;
- preservation constraints;
- authorized reference-asset identifiers;
- unknown topics;
- conflicts; and
- provenance summary.

A profile implementation must not bypass Product Intelligence to discover
product truth directly from folders, arbitrary files, databases, network
services, image pixels, generated output, or model inference.

## 6. Minimum profile vocabulary

The minimum architecture introduces two logical immutable values:

1. `CreativeProductRule`
2. `CreativeProductProfile`

These names define the intended contract vocabulary. This document does not
authorize their source implementation.

## 7. CreativeProductRule

One `CreativeProductRule` represents one explicit creative semantic statement.

A minimum rule contains exactly these fields:

1. `rule_id`
2. `rule_kind`
3. `label`
4. `instruction`
5. `scope`
6. `supporting_fact_refs`
7. `supporting_constraint_refs`
8. `provenance_refs`

All fields are immutable after construction.

### 7.1 rule_id

`rule_id` is one caller-supplied stable non-empty ASCII identity.

It must not be generated from the ambient clock, randomness, a model response,
filesystem order, database sequence, or hidden global state.

The same `rule_id` must not be reused for different canonical rule content.

### 7.2 rule_kind

`rule_kind` may be exactly one of:

- `IDENTITY_CRITICAL`
- `PRESERVE`
- `MAY_VARY`
- `PROHIBIT`

No synonym, inferred type, wildcard, provider-specific value, or free-form kind
is part of the minimum contract.

### 7.3 label

`label` is concise non-empty human-readable ASCII text identifying the creative
subject of the rule.

Examples of future labels might include a shell silhouette, visor geometry,
logo placement, graphic layout, colorway, background, lighting, or camera
treatment.

An example label is not evidence that the corresponding product fact exists.

### 7.4 instruction

`instruction` is the exact non-empty governed creative statement represented by
the rule.

It must not contain unsupported product truth.

The instruction is not provider syntax and must remain generator-agnostic.

### 7.5 scope

`scope` may be exactly:

- `PRODUCT`
- `VARIANT`

A product-scoped rule may apply to all represented variants only when its
supporting references are themselves valid for product scope.

A variant-scoped rule must remain bound to the exact profile variant.

No rule may silently widen from variant scope to product scope.

### 7.6 supporting_fact_refs

`supporting_fact_refs` is an immutable tuple of zero or more exact
`ProductIntelligenceFact.fact_id` values from the supplied product context.

Every referenced fact must exist in that exact context.

Cross-product or cross-variant fact references must fail closed.

### 7.7 supporting_constraint_refs

`supporting_constraint_refs` is an immutable tuple of zero or more exact
`ProductIntelligenceConstraint.constraint_id` values from the supplied product
context.

Every referenced constraint must exist in that exact context.

Cross-product, cross-variant, or absent references must fail closed.

### 7.8 provenance_refs

`provenance_refs` is an immutable tuple of exact upstream provenance references
supporting the rule.

A profile implementation may only preserve provenance references that are
already reachable from the exact supporting Product Intelligence facts,
constraints, or an explicitly accepted upstream provenance mapping.

It must not invent, normalize, shorten, broaden, or semantically substitute
provenance.

## 8. Rule support requirement

Every rule must have explicit support.

At least one of the following must be non-empty:

- `supporting_fact_refs`;
- `supporting_constraint_refs`.

A rule with no explicit grounded support is invalid.

The implementation must not treat operator confidence, a filename, a folder
name, a generated output, a visual impression, a common product-category
assumption, or model reasoning as substitute support.

## 9. IDENTITY_CRITICAL semantics

`IDENTITY_CRITICAL` means the represented feature is part of the explicit
creative identity that downstream work must preserve for this exact product or
variant.

An identity-critical rule may be created only when the supplied Product
Intelligence context explicitly supports the statement.

The system must not infer identity-critical status merely because a feature is
visually prominent, common for the product category, repeated in many photos,
or judged important by a model.

A later operator-reviewed process may introduce new identity-critical rules,
but that later process must supply explicit grounded references and separate
authorization.

## 10. PRESERVE semantics

`PRESERVE` means a downstream creative instruction must retain the represented
supported property.

Existing Product Intelligence preservation constraints are the primary
candidate upstream support for minimum `PRESERVE` rules.

A future deterministic constructor may carry an accepted preservation
constraint forward without semantic rewriting when the exact rule statement
and scope remain traceably bound to that constraint.

The profile must not weaken an accepted preservation constraint.

## 11. MAY_VARY semantics

`MAY_VARY` means the represented creative dimension is explicitly permitted to
change within the stated governed instruction.

Absence of a preservation rule does not mean variation is permitted.

Absence of a known product fact does not mean variation is permitted.

An unknown topic does not mean variation is permitted.

A `MAY_VARY` rule therefore requires explicit supporting Product Intelligence
references just like every other rule.

If no explicit support establishes a safe variation boundary, the profile must
leave that variation undeclared rather than infer freedom.

This rule is essential to prevent a generator from treating every unspecified
product property as creative latitude.

## 12. PROHIBIT semantics

`PROHIBIT` means the represented transformation must not be requested or
represented as acceptable by downstream creative instruction.

A prohibition must have explicit supporting facts or constraints.

A future profile may express prohibitions such as changing an exact supported
identity feature, but it must not fabricate a prohibition that is unsupported
by the accepted product context.

A prohibition is a creative boundary. It is not an approval decision, asset
lifecycle mutation, provider safety policy, or legal conclusion.

## 13. CreativeProductProfile

One `CreativeProductProfile` represents the minimum governed creative semantic
profile for one exact product and variant context.

It contains exactly these fields:

1. `profile_id`
2. `profile_version`
3. `product_id`
4. `variant_id`
5. `identity_critical_rules`
6. `preserve_rules`
7. `variation_rules`
8. `prohibit_rules`
9. `unknown_topics`
10. `conflicts`
11. `provenance_refs`

### 13.1 profile_id

`profile_id` is caller-supplied stable non-empty ASCII text.

It is not a product ID, variant ID, asset ID, prompt ID, workflow ID, or
approval ID.

### 13.2 profile_version

`profile_version` is explicit non-empty ASCII text identifying the represented
profile revision.

A changed canonical profile requires a changed version or a separately governed
new profile identity according to a later versioning contract.

This contract does not implement persistence or supersession.

### 13.3 product_id and variant_id

The profile is bound to exactly one existing Product Intelligence product and
variant.

Cross-product or cross-variant reuse is prohibited.

A profile must not apply itself to a "similar" product, renamed variant, newer
model, replacement SKU, or visually similar shell without explicit governed
identity reconciliation.

### 13.4 categorized rules

The four rule collections contain only their matching exact `rule_kind`.

Each collection is immutable and deterministically ordered by the caller or a
later explicitly defined canonical ordering contract.

A rule ID must be unique within the whole profile, not merely within one rule
collection.

### 13.5 unknown_topics

`unknown_topics` preserves exact unresolved topics from the supplied Product
Intelligence context.

The profile may not silently delete an upstream unknown because a creative
operator, prompt author, provider, or model can guess the answer.

This contract does not define semantic matching between unknown topics and
creative brief fields.

### 13.6 conflicts

`conflicts` preserves exact Product Intelligence conflicts relevant to the
supplied context without resolving them.

A profile constructor must not resolve conflicting product truth.

A later prompt or generation-readiness assessment must fail closed whenever its
required instruction depends on unresolved conflicting truth.

### 13.7 profile provenance_refs

The profile-level provenance references are the deterministic union of the
accepted provenance references carried by its rules and exact upstream context
references selected by a later implementation contract.

No new provenance authority is created by profile construction.

## 14. Minimum deterministic construction boundary

A later implementation may define a framework-neutral
`CreativeProductProfileBuilder`.

The minimum builder responsibility may only:

1. accept one exact Product Intelligence context;
2. accept one explicit caller-supplied profile identity and version;
3. accept explicit requested rule declarations;
4. validate product and variant identity;
5. resolve every rule's exact supporting fact references;
6. resolve every rule's exact supporting constraint references;
7. verify scope agreement;
8. preserve reachable provenance references;
9. preserve upstream unknown topics;
10. preserve upstream conflicts;
11. reject duplicate or contradictory rule identity;
12. return one immutable `CreativeProductProfile`.

The builder must not:

- inspect images;
- infer visual features;
- invent creative rules;
- rewrite product facts;
- summarize evidence with a model;
- infer which product feature is important;
- rank rules by visual salience;
- select reference assets;
- generate prompts;
- call a generator;
- approve output;
- mutate an asset;
- persist the profile; or
- publish anything.

## 15. Exact-declaration boundary

The first implementation should prefer explicit declarations over hidden
intelligence.

This is deliberate.

RCIS must first prove that product-fidelity semantics can be represented,
validated, traced, and consumed without losing authority boundaries.

Later AI-assisted systems may propose candidate rules, but any proposed rule
must remain a candidate until the same exact support and governance checks are
satisfied.

Model confidence alone must never turn a proposed creative rule into governed
product truth.

## 16. Conflict and contradiction behavior

The minimum profile contract must fail closed for structural contradictions,
including:

- the same `rule_id` carrying different canonical content;
- one exact rule appearing in incompatible categories;
- a `MAY_VARY` declaration that directly contradicts an exact accepted
  `PRESERVE` or `PROHIBIT` rule for the same governed subject;
- a rule whose scope exceeds the scope of its supporting references;
- a supporting reference absent from the supplied context;
- provenance that cannot be traced to accepted support.

The first implementation does not need semantic natural-language contradiction
detection.

Only exact or explicitly modeled contradictions may be evaluated
deterministically.

Semantic contradiction analysis remains a later intelligence capability.

## 17. Relationship to Product Intelligence

Product Intelligence remains authoritative for grounded product facts,
constraints, unknowns, conflicts, and provenance.

Creative Product Profile does not replace Product Intelligence.

It projects selected accepted truth into a creative-fidelity vocabulary.

When upstream Product Intelligence changes, the profile does not silently
update itself.

A later reconciliation operation must determine whether the profile remains
valid for the new upstream identity/version.

## 18. Relationship to Asset Intelligence

This contract does not assign creative roles to assets.

It does not classify an approved product image as:

- hero;
- front;
- left profile;
- right profile;
- geometry reference;
- graphic reference;
- color reference;
- logo reference;
- detail reference; or
- any other creative-reference role.

Those semantics belong to the next separately reviewed Asset Intelligence
boundary.

The current approved visual-reference query remains unchanged.

## 19. Relationship to Prompt Intelligence

The current grounded prompt composer remains unchanged by this contract.

A future Prompt Intelligence boundary may consume a valid
`CreativeProductProfile` to construct a richer governed creative instruction
package.

That later boundary may translate profile rules into structured creative
instruction sections, but it must preserve exact rule identity and provenance.

This contract does not define provider-specific prompt syntax.

## 20. Relationship to Gate 17

Gate 17 remains deferred while this foundation is built.

A generator provider must not become the source of product identity or creative
product truth.

A future Gate 17 implementation should consume an already-governed instruction
package plus explicitly selected governed reference assets.

It must not be asked to infer missing product-fidelity rules from general model
knowledge.

## 21. Relationship to real RSV asset processing

No real RSV asset processing is authorized by this contract.

The eventual real RSV creative-productivity pilot should begin only after the
minimum chain can represent:

1. grounded product truth;
2. one governed Creative Product Profile;
3. governed creative roles for selected reference assets;
4. one governed creative instruction package;
5. one concrete generator provider;
6. candidate output admission; and
7. human product-fidelity review.

This contract implements only item 2 at the architecture level.

## 22. Fail-closed conditions

A future implementation must fail closed for at least:

- invalid profile identity or version;
- unknown product identity;
- unknown or cross-product variant identity;
- invalid rule kind;
- duplicate rule identity;
- blank rule label or instruction;
- invalid scope;
- rule with no grounded support;
- unknown supporting fact reference;
- unknown supporting constraint reference;
- scope mismatch;
- unreachable or fabricated provenance;
- exact modeled rule contradiction;
- malformed upstream Product Intelligence context;
- attempted automatic inference;
- attempted model or generator execution;
- attempted asset mutation;
- attempted approval or lifecycle mutation.

No partial profile may be represented as fully valid when any required rule
fails validation.

## 23. Determinism and side-effect boundary

Equivalent explicit inputs must produce equivalent canonical profile values.

Minimum construction must be free of:

- filesystem discovery;
- arbitrary file reads;
- image decoding;
- network access;
- ambient clock use;
- randomness;
- model execution;
- OCR;
- embeddings;
- vector search;
- semantic search;
- knowledge-graph traversal;
- database mutation;
- repository mutation;
- background jobs;
- generator execution; and
- approval execution.

All required identity, support, scope, and provenance values must be supplied
through accepted caller inputs or accepted upstream application boundaries.

## 24. Security and secret boundary

A Creative Product Profile must not contain:

- credentials;
- API keys;
- passwords;
- cookies;
- session tokens;
- model-provider secrets;
- absolute local filesystem paths;
- hidden prompts;
- mutable runtime handles.

The profile is governed product-fidelity metadata, not a transport or secret
container.

## 25. Explicit non-goals

PR-126B does not authorize or define:

- runtime source implementation;
- test implementation;
- product-profile persistence;
- database schema;
- profile UI;
- automatic profile generation;
- semantic image understanding;
- image classification;
- object recognition;
- logo detection;
- geometry comparison;
- OCR;
- embeddings;
- vector database;
- semantic search;
- knowledge graph;
- automated inference;
- asset-role intelligence;
- automatic reference-asset selection;
- prompt-provider optimization;
- provider-specific prompt syntax;
- Gate 17 implementation;
- local or cloud generator connection;
- model execution;
- real RSV asset processing;
- generated-output evaluation;
- automatic product-fidelity scoring;
- asset lifecycle mutation;
- approval execution;
- packaging or deployment;
- source staging, commit, push, or tagging.

## 26. Candidate implementation surface

After this architecture contract is independently materialized, reviewed, and
published, a later boundary review may consider the smallest implementation.

The preferred candidate is one framework-neutral application-layer path:

`src/rie/application/creative_product_profile.py`

with one focused test path:

`tests/application/test_creative_product_profile.py`

This is a candidate only.

PR-126B does not authorize creating either path.

A later review may choose a narrower or different exact implementation surface
if repository reconciliation shows that to be safer.

## 27. Minimum future test matrix

A later implementation should prove at least:

1. one supported identity-critical rule is accepted;
2. one accepted preservation constraint can be carried forward with traceable
   support;
3. one explicitly supported variation rule is accepted;
4. one explicitly supported prohibition rule is accepted;
5. a rule with no support is rejected;
6. an unknown fact reference is rejected;
7. an unknown constraint reference is rejected;
8. cross-product and cross-variant references fail closed;
9. scope widening fails closed;
10. duplicate rule IDs fail closed;
11. exact modeled contradictions fail closed;
12. upstream unknown topics are preserved;
13. upstream conflicts are preserved;
14. provenance is preserved and not invented;
15. repeated equivalent construction is deterministic;
16. no UI, storage, network, model, generator, or asset mutation dependency is
    introduced.

## 28. Acceptance predicates for this architecture contract

PR-126B architecture materialization is acceptable only when independent
evidence confirms:

1. RCIS v1 release checkpoint and tag remain unchanged;
2. the accepted PR-126A initiation evidence is exact;
3. this architecture document is the only worktree path created or modified;
4. the document is UTF-8 without BOM, LF-only, and has exactly one final LF;
5. the four exact rule kinds are present;
6. the explicit grounded-support requirement is present;
7. unsupported `MAY_VARY` inference is explicitly prohibited;
8. Product Intelligence remains authoritative;
9. asset-role intelligence remains deferred;
10. Prompt Intelligence remains deferred;
11. Gate 17 remains deferred;
12. real RSV asset processing remains unauthorized;
13. no source, test, configuration, asset, branch, index, commit, tag, or remote
    mutation occurs except creation of this one unstaged architecture path.

Failure of any predicate must fail closed.

## 29. Controlled continuation

The next operation after an accepted PR-126B materialization must be a separate
read-only review.

That review must determine whether the contract is internally consistent and
whether the candidate implementation surface is still the smallest safe next
step.

No runtime implementation is authorized until that separate review is accepted.

## 30. Decision

The minimum first post-v1 Creative Intelligence gap is a governed Creative
Product Profile.

This profile exists to convert already-grounded product truth into explicit,
traceable creative fidelity rules while preserving uncertainty and preventing
unsupported variation.

It is intentionally generator-agnostic and model-free.

Asset Intelligence, Prompt Intelligence, Gate 17, and the first real RSV
creative-productivity pilot remain downstream of this boundary.
