from __future__ import annotations

import ast
from pathlib import Path

import pytest

from rie.application.creative_product_profile import (
    CreativeProductProfileBuilder,
    CreativeProductProfileContractError,
    CreativeProductRule,
    RULE_KIND_IDENTITY_CRITICAL,
    RULE_KIND_MAY_VARY,
    RULE_KIND_PRESERVE,
    RULE_KIND_PROHIBIT,
    SCOPE_PRODUCT,
    SCOPE_VARIANT,
)
from rie.application.product_intelligence_query import (
    ProductIntelligenceConstraint,
    ProductIntelligenceContext,
    ProductIntelligenceFact,
    ProductIntelligenceUnknown,
)


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "rie"
    / "application"
    / "creative_product_profile.py"
)


def _context() -> ProductIntelligenceContext:
    return ProductIntelligenceContext(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        product_label="SV300",
        variant_label="White Glossy",
        summary="Grounded product context.",
        fact_groups=(
            ProductIntelligenceFact(
                fact_id="fact-product-material",
                category="material",
                label="Helmet body material",
                value="ABS",
                scope="product",
                provenance_refs=("ev-product",),
            ),
            ProductIntelligenceFact(
                fact_id="fact-variant-identity",
                category="identity",
                label="Variant identity",
                value="SV300 / White Glossy",
                scope="variant",
                provenance_refs=("ev-variant",),
            ),
            ProductIntelligenceFact(
                fact_id="fact-background-freedom",
                category="creative-boundary",
                label="Background treatment",
                value="May vary without changing product identity",
                scope="variant",
                provenance_refs=("ev-creative",),
            ),
        ),
        preservation_constraints=(
            ProductIntelligenceConstraint(
                constraint_id="constraint-material",
                label="Preserve material",
                rule_text="preserve ABS helmet body material",
                scope="product",
                source_fact_refs=("fact-product-material",),
            ),
            ProductIntelligenceConstraint(
                constraint_id="constraint-variant",
                label="Preserve variant identity",
                rule_text="preserve exact approved product and variant identity",
                scope="variant",
                source_fact_refs=("fact-variant-identity",),
            ),
        ),
        authorized_reference_asset_ids=("asset-a",),
        unknown_topics=(
            ProductIntelligenceUnknown(
                topic="spoiler-geometry",
                user_facing_label="Spoiler geometry is unresolved.",
            ),
        ),
        conflicts=("visor-finish-conflict",),
        provenance_summary="manufacturer-approved-source / approved / 2026.08",
    )


def _rule(
    *,
    rule_id: str,
    rule_kind: str,
    label: str,
    instruction: str,
    scope: str,
    facts: tuple[str, ...] = (),
    constraints: tuple[str, ...] = (),
    provenance: tuple[str, ...] = (),
) -> CreativeProductRule:
    return CreativeProductRule(
        rule_id=rule_id,
        rule_kind=rule_kind,
        label=label,
        instruction=instruction,
        scope=scope,
        supporting_fact_refs=facts,
        supporting_constraint_refs=constraints,
        provenance_refs=provenance,
    )


def test_supported_four_rule_kinds_build_one_profile() -> None:
    profile = CreativeProductProfileBuilder().build(
        context=_context(),
        profile_id="cpp-sv300-white-glossy",
        profile_version="1.0.0",
        rules=(
            _rule(
                rule_id="identity-variant",
                rule_kind=RULE_KIND_IDENTITY_CRITICAL,
                label="variant identity",
                instruction="preserve exact SV300 White Glossy identity",
                scope=SCOPE_VARIANT,
                facts=("fact-variant-identity",),
            ),
            _rule(
                rule_id="preserve-material",
                rule_kind=RULE_KIND_PRESERVE,
                label="helmet body material",
                instruction="preserve ABS helmet body material",
                scope=SCOPE_PRODUCT,
                constraints=("constraint-material",),
            ),
            _rule(
                rule_id="vary-background",
                rule_kind=RULE_KIND_MAY_VARY,
                label="background treatment",
                instruction="background treatment may vary",
                scope=SCOPE_VARIANT,
                facts=("fact-background-freedom",),
            ),
            _rule(
                rule_id="prohibit-variant-change",
                rule_kind=RULE_KIND_PROHIBIT,
                label="variant replacement",
                instruction="do not replace the approved variant identity",
                scope=SCOPE_VARIANT,
                facts=("fact-variant-identity",),
            ),
        ),
    )

    assert profile.product_id == "sv300"
    assert profile.variant_id == "sv300-white-glossy"
    assert tuple(rule.rule_id for rule in profile.identity_critical_rules) == (
        "identity-variant",
    )
    assert tuple(rule.rule_id for rule in profile.preserve_rules) == (
        "preserve-material",
    )
    assert tuple(rule.rule_id for rule in profile.variation_rules) == (
        "vary-background",
    )
    assert tuple(rule.rule_id for rule in profile.prohibit_rules) == (
        "prohibit-variant-change",
    )
    assert profile.provenance_refs == (
        "ev-variant",
        "ev-product",
        "ev-creative",
    )


def test_preservation_constraint_derives_provenance_from_source_fact() -> None:
    profile = CreativeProductProfileBuilder().build(
        context=_context(),
        profile_id="cpp",
        profile_version="1",
        rules=(
            _rule(
                rule_id="preserve-material",
                rule_kind=RULE_KIND_PRESERVE,
                label="material",
                instruction="preserve product material",
                scope=SCOPE_PRODUCT,
                constraints=("constraint-material",),
            ),
        ),
    )
    assert profile.preserve_rules[0].provenance_refs == ("ev-product",)


def test_declared_provenance_must_exactly_match_reachable_support() -> None:
    with pytest.raises(
        CreativeProductProfileContractError,
        match="provenance_refs must exactly match",
    ):
        CreativeProductProfileBuilder().build(
            context=_context(),
            profile_id="cpp",
            profile_version="1",
            rules=(
                _rule(
                    rule_id="identity",
                    rule_kind=RULE_KIND_IDENTITY_CRITICAL,
                    label="identity",
                    instruction="preserve identity",
                    scope=SCOPE_VARIANT,
                    facts=("fact-variant-identity",),
                    provenance=("fabricated",),
                ),
            ),
        )


def test_rule_without_grounded_support_fails_closed() -> None:
    with pytest.raises(
        CreativeProductProfileContractError,
        match="requires explicit grounded support",
    ):
        _rule(
            rule_id="unsupported",
            rule_kind=RULE_KIND_MAY_VARY,
            label="shell geometry",
            instruction="shell geometry may vary",
            scope=SCOPE_VARIANT,
        )


@pytest.mark.parametrize(
    ("facts", "constraints", "message"),
    (
        (("missing-fact",), (), "unknown supporting fact reference"),
        ((), ("missing-constraint",), "unknown supporting constraint reference"),
    ),
)
def test_unknown_support_reference_fails_closed(
    facts: tuple[str, ...],
    constraints: tuple[str, ...],
    message: str,
) -> None:
    with pytest.raises(CreativeProductProfileContractError, match=message):
        CreativeProductProfileBuilder().build(
            context=_context(),
            profile_id="cpp",
            profile_version="1",
            rules=(
                _rule(
                    rule_id="rule",
                    rule_kind=RULE_KIND_PRESERVE,
                    label="supported subject",
                    instruction="preserve supported subject",
                    scope=SCOPE_VARIANT,
                    facts=facts,
                    constraints=constraints,
                ),
            ),
        )


def test_product_scope_cannot_widen_variant_support() -> None:
    with pytest.raises(
        CreativeProductProfileContractError,
        match="must not widen variant-scoped support",
    ):
        CreativeProductProfileBuilder().build(
            context=_context(),
            profile_id="cpp",
            profile_version="1",
            rules=(
                _rule(
                    rule_id="widened",
                    rule_kind=RULE_KIND_IDENTITY_CRITICAL,
                    label="variant identity",
                    instruction="treat variant identity as product-wide",
                    scope=SCOPE_PRODUCT,
                    facts=("fact-variant-identity",),
                ),
            ),
        )


def test_variant_scope_may_preserve_product_scoped_support() -> None:
    profile = CreativeProductProfileBuilder().build(
        context=_context(),
        profile_id="cpp",
        profile_version="1",
        rules=(
            _rule(
                rule_id="material-in-variant-profile",
                rule_kind=RULE_KIND_PRESERVE,
                label="product material",
                instruction="preserve product material in this variant creative",
                scope=SCOPE_VARIANT,
                facts=("fact-product-material",),
            ),
        ),
    )
    assert profile.preserve_rules[0].provenance_refs == ("ev-product",)


def test_duplicate_rule_identity_fails_closed() -> None:
    rule = _rule(
        rule_id="same",
        rule_kind=RULE_KIND_PRESERVE,
        label="material",
        instruction="preserve material",
        scope=SCOPE_PRODUCT,
        facts=("fact-product-material",),
    )
    with pytest.raises(
        CreativeProductProfileContractError,
        match="duplicate rule_id",
    ):
        CreativeProductProfileBuilder().build(
            context=_context(),
            profile_id="cpp",
            profile_version="1",
            rules=(rule, rule),
        )


@pytest.mark.parametrize(
    "protected_kind",
    (
        RULE_KIND_IDENTITY_CRITICAL,
        RULE_KIND_PRESERVE,
        RULE_KIND_PROHIBIT,
    ),
)
def test_exact_may_vary_contradiction_fails_closed(
    protected_kind: str,
) -> None:
    with pytest.raises(
        CreativeProductProfileContractError,
        match="exact modeled contradiction",
    ):
        CreativeProductProfileBuilder().build(
            context=_context(),
            profile_id="cpp",
            profile_version="1",
            rules=(
                _rule(
                    rule_id="protected",
                    rule_kind=protected_kind,
                    label="variant identity",
                    instruction="protect variant identity",
                    scope=SCOPE_VARIANT,
                    facts=("fact-variant-identity",),
                ),
                _rule(
                    rule_id="vary",
                    rule_kind=RULE_KIND_MAY_VARY,
                    label="variant identity",
                    instruction="variant identity may vary",
                    scope=SCOPE_VARIANT,
                    facts=("fact-variant-identity",),
                ),
            ),
        )


def test_unknown_topics_and_conflicts_are_preserved_exactly() -> None:
    context = _context()
    profile = CreativeProductProfileBuilder().build(
        context=context,
        profile_id="cpp",
        profile_version="1",
        rules=(
            _rule(
                rule_id="identity",
                rule_kind=RULE_KIND_IDENTITY_CRITICAL,
                label="variant identity",
                instruction="preserve variant identity",
                scope=SCOPE_VARIANT,
                facts=("fact-variant-identity",),
            ),
        ),
    )
    assert profile.unknown_topics == context.unknown_topics
    assert profile.conflicts == context.conflicts


def test_equivalent_construction_is_deterministic() -> None:
    kwargs = dict(
        context=_context(),
        profile_id="cpp",
        profile_version="1",
        rules=(
            _rule(
                rule_id="identity",
                rule_kind=RULE_KIND_IDENTITY_CRITICAL,
                label="variant identity",
                instruction="preserve variant identity",
                scope=SCOPE_VARIANT,
                facts=("fact-variant-identity",),
            ),
            _rule(
                rule_id="background",
                rule_kind=RULE_KIND_MAY_VARY,
                label="background treatment",
                instruction="background may vary",
                scope=SCOPE_VARIANT,
                facts=("fact-background-freedom",),
            ),
        ),
    )
    builder = CreativeProductProfileBuilder()
    assert builder.build(**kwargs) == builder.build(**kwargs)


def test_first_slice_is_framework_neutral_model_free_and_non_persistent() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= {
        "__future__",
        "dataclasses",
        "typing",
        "rie",
    }

    lowered = source.lower()
    for forbidden in (
        "pyside6",
        "tkinter",
        "sqlite3",
        "requests",
        "httpx",
        "openai",
        "torch",
        "transformers",
        "visual_generation_provider",
        "visual_reference_asset_query",
        "creative_prompt_composer",
        "governed_asset_library_registry",
        "pathlib",
        "open(",
        "write_text",
        "write_bytes",
    ):
        assert forbidden not in lowered
