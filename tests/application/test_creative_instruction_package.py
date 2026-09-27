from __future__ import annotations

import ast
from pathlib import Path

import pytest

from rie.application.creative_asset_role_profile import (
    CreativeAssetRoleDirective,
    CreativeAssetRoleProfile,
    REFERENCE_CONTEXT_ONLY,
    REFERENCE_PRIMARY,
    REFERENCE_SUPPORTING,
    ROLE_CONTEXT_REFERENCE,
    ROLE_FORM_REFERENCE,
    ROLE_IDENTITY_ANCHOR,
    VIEW_CONTEXT,
    VIEW_FRONT,
    VIEW_THREE_QUARTER,
)
from rie.application.creative_instruction_package import (
    CreativeInstructionPackageBuilder,
    CreativeInstructionPackageContractError,
    INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
    READINESS_BLOCKED,
    READINESS_READY,
)
from rie.application.creative_product_profile import (
    CreativeProductProfile,
    CreativeProductRule,
    RULE_KIND_IDENTITY_CRITICAL,
    RULE_KIND_MAY_VARY,
    RULE_KIND_PRESERVE,
    RULE_KIND_PROHIBIT,
    SCOPE_PRODUCT,
    SCOPE_VARIANT,
)
from rie.application.creative_prompt_composer import CreativePromptBrief
from rie.application.product_intelligence_query import ProductIntelligenceUnknown


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "rie"
    / "application"
    / "creative_instruction_package.py"
)

SHA_A = "1" * 64
SHA_B = "2" * 64


def _rule(
    *,
    rule_id: str,
    rule_kind: str,
    label: str,
    instruction: str,
    facts: tuple[str, ...] = ("fact:1",),
    constraints: tuple[str, ...] = (),
    provenance: tuple[str, ...] = ("prov:product:1",),
    scope: str = SCOPE_VARIANT,
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


def _product_profile(
    *,
    product_id: str = "sv300",
    variant_id: str = "white-glossy",
    unknowns: tuple[ProductIntelligenceUnknown, ...] = (),
    conflicts: tuple[str, ...] = (),
) -> CreativeProductProfile:
    return CreativeProductProfile(
        profile_id="cpp:sv300:white-glossy",
        profile_version="1.0.0",
        product_id=product_id,
        variant_id=variant_id,
        identity_critical_rules=(
            _rule(
                rule_id="identity:variant",
                rule_kind=RULE_KIND_IDENTITY_CRITICAL,
                label="variant identity",
                instruction="preserve exact approved SV300 White Glossy identity",
            ),
        ),
        preserve_rules=(
            _rule(
                rule_id="preserve:material",
                rule_kind=RULE_KIND_PRESERVE,
                label="helmet body material",
                instruction="preserve ABS helmet body material",
                facts=(),
                constraints=("constraint:material",),
                provenance=("prov:product:2",),
                scope=SCOPE_PRODUCT,
            ),
        ),
        variation_rules=(
            _rule(
                rule_id="vary:background",
                rule_kind=RULE_KIND_MAY_VARY,
                label="background treatment",
                instruction="background treatment may vary",
                provenance=("prov:product:3",),
            ),
        ),
        prohibit_rules=(
            _rule(
                rule_id="prohibit:identity-change",
                rule_kind=RULE_KIND_PROHIBIT,
                label="variant replacement",
                instruction="do not replace the approved variant identity",
                provenance=("prov:product:4",),
            ),
        ),
        unknown_topics=unknowns,
        conflicts=conflicts,
        provenance_refs=(
            "prov:product:1",
            "prov:product:2",
            "prov:product:3",
            "prov:product:4",
        ),
    )


def _asset_directive(
    *,
    directive_id: str = "asset-role:front",
    asset_id: str = "asset-front",
    asset_version_identity: str = "sha256:" + SHA_A,
    product_id: str = "sv300",
    variant_id: str = "white-glossy",
    role_kind: str = ROLE_IDENTITY_ANCHOR,
    view_kind: str = VIEW_FRONT,
    reference_strength: str = REFERENCE_PRIMARY,
    support_refs: tuple[str, ...] = ("support:asset:1",),
    provenance_refs: tuple[str, ...] = ("prov:asset:1",),
) -> CreativeAssetRoleDirective:
    return CreativeAssetRoleDirective(
        directive_id=directive_id,
        asset_id=asset_id,
        asset_version_identity=asset_version_identity,
        product_id=product_id,
        variant_id=variant_id,
        role_kind=role_kind,
        view_kind=view_kind,
        reference_strength=reference_strength,
        support_refs=support_refs,
        provenance_refs=provenance_refs,
    )


def _asset_profile(
    *,
    product_id: str = "sv300",
    variant_id: str = "white-glossy",
    directives: tuple[CreativeAssetRoleDirective, ...] | None = None,
    unknowns: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
) -> CreativeAssetRoleProfile:
    if directives is None:
        directives = (
            _asset_directive(),
            _asset_directive(
                directive_id="asset-role:context",
                asset_id="asset-context",
                asset_version_identity="sha256:" + SHA_B,
                role_kind=ROLE_CONTEXT_REFERENCE,
                view_kind=VIEW_CONTEXT,
                reference_strength=REFERENCE_CONTEXT_ONLY,
                support_refs=("support:asset:2",),
                provenance_refs=("prov:asset:2",),
            ),
        )
    return CreativeAssetRoleProfile(
        profile_id="carp:sv300:white-glossy",
        profile_version="1.0.0",
        product_id=product_id,
        variant_id=variant_id,
        directives=directives,
        unknown_topics=unknowns,
        conflicts=conflicts,
        provenance_refs=("prov:asset:1", "prov:asset:2"),
    )


def _brief(
    *,
    selected: tuple[str, ...] = ("asset-front",),
    preserve: tuple[str, ...] = ("keep visor clear",),
    avoid: tuple[str, ...] = ("no floating product",),
) -> CreativePromptBrief:
    return CreativePromptBrief(
        objective="ecommerce hero",
        deliverable="grounded product prompt",
        environment="dark studio",
        camera_angle="front three-quarter",
        shot_type="medium product shot",
        lighting_style="soft directional",
        composition="centered with negative space",
        mood_style="premium technical",
        aspect_ratio="4:5",
        orientation="portrait",
        product_emphasis="helmet dominant",
        preserve_constraints=preserve,
        avoid_constraints=avoid,
        freeform_notes="natural floor contact",
        selected_reference_asset_ids=selected,
    )


def _build(**overrides):
    values = {
        "package_id": "instruction:sv300:white-glossy:001",
        "package_version": "1.0.0",
        "product_id": "sv300",
        "variant_id": "white-glossy",
        "product_profile": _product_profile(),
        "asset_role_profile": _asset_profile(),
        "creative_brief": _brief(),
    }
    values.update(overrides)
    return CreativeInstructionPackageBuilder().build(**values)


def test_valid_package_combines_three_existing_foundation_values() -> None:
    product = _product_profile()
    asset = _asset_profile()
    brief = _brief()
    package = _build(
        product_profile=product,
        asset_role_profile=asset,
        creative_brief=brief,
    )
    assert package.creative_brief is brief
    assert package.product_id == product.product_id == asset.product_id
    assert package.variant_id == product.variant_id == asset.variant_id
    assert package.is_ready


def test_instruction_authority_is_exactly_prompt_candidate() -> None:
    package = _build()
    assert package.instruction_authority == INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE
    assert package.instruction_authority == "PROMPT_CANDIDATE"


def test_approved_instruction_authority_fails_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="PROMPT_CANDIDATE",
    ):
        _build(instruction_authority="APPROVED_INSTRUCTION")


@pytest.mark.parametrize(
    "rule_kind",
    (
        RULE_KIND_IDENTITY_CRITICAL,
        RULE_KIND_PRESERVE,
        RULE_KIND_MAY_VARY,
        RULE_KIND_PROHIBIT,
    ),
)
def test_all_four_product_rule_kinds_are_preserved(rule_kind: str) -> None:
    package = _build()
    assert rule_kind in {value.rule_kind for value in package.product_directives}


def test_product_directives_preserve_rule_identity_subject_and_instruction() -> None:
    package = _build()
    by_id = {value.rule_id: value for value in package.product_directives}
    directive = by_id["identity:variant"]
    assert directive.subject == "variant identity"
    assert directive.instruction_value == (
        "preserve exact approved SV300 White Glossy identity"
    )
    assert directive.support_refs == ("fact:1",)
    assert directive.provenance_refs == ("prov:product:1",)


def test_product_directive_ordering_is_deterministic() -> None:
    first = _build().product_directives
    second = _build().product_directives
    assert first == second
    assert first == tuple(
        sorted(
            first,
            key=lambda value: (value.rule_kind, value.subject, value.rule_id),
        )
    )


def test_selected_asset_preserves_exact_version_role_view_and_strength() -> None:
    package = _build()
    assert len(package.active_asset_directives) == 1
    directive = package.active_asset_directives[0]
    assert directive.asset_id == "asset-front"
    assert directive.asset_version_identity == "sha256:" + SHA_A
    assert directive.role_kind == ROLE_IDENTITY_ANCHOR
    assert directive.view_kind == VIEW_FRONT
    assert directive.reference_strength == REFERENCE_PRIMARY


def test_selected_asset_without_explicit_role_semantics_fails_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="lacks explicit Asset Role semantics",
    ):
        _build(creative_brief=_brief(selected=("asset-missing",)))


def test_unselected_asset_role_directive_does_not_become_active() -> None:
    package = _build(creative_brief=_brief(selected=("asset-front",)))
    assert {value.asset_id for value in package.active_asset_directives} == {
        "asset-front"
    }


def test_empty_selected_reference_list_is_valid() -> None:
    package = _build(creative_brief=_brief(selected=()))
    assert package.active_asset_directives == ()
    assert package.is_ready


def test_asset_directive_ordering_is_deterministic() -> None:
    asset_profile = _asset_profile(
        directives=(
            _asset_directive(
                directive_id="asset-role:form",
                asset_id="asset-front",
                role_kind=ROLE_FORM_REFERENCE,
                view_kind=VIEW_THREE_QUARTER,
                reference_strength=REFERENCE_SUPPORTING,
                support_refs=("support:asset:3",),
                provenance_refs=("prov:asset:3",),
            ),
            _asset_directive(),
        )
    )
    package = _build(asset_role_profile=asset_profile)
    assert package.active_asset_directives == tuple(
        sorted(
            package.active_asset_directives,
            key=lambda value: (
                value.role_kind,
                value.view_kind,
                value.reference_strength,
                value.asset_id,
                value.directive_id,
            ),
        )
    )


def test_product_profile_product_mismatch_fails_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="product_profile product mismatch",
    ):
        _build(product_profile=_product_profile(product_id="other-product"))


def test_product_profile_variant_mismatch_fails_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="product_profile variant mismatch",
    ):
        _build(product_profile=_product_profile(variant_id="other-variant"))


def test_asset_role_profile_product_mismatch_fails_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="asset_role_profile product mismatch",
    ):
        _build(asset_role_profile=_asset_profile(product_id="other-product"))


def test_asset_role_profile_variant_mismatch_fails_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="asset_role_profile variant mismatch",
    ):
        _build(asset_role_profile=_asset_profile(variant_id="other-variant"))


def test_product_unknown_topics_are_preserved_and_block_readiness() -> None:
    profile = _product_profile(
        unknowns=(
            ProductIntelligenceUnknown(
                topic="spoiler-geometry",
                user_facing_label="Spoiler geometry unresolved.",
            ),
        )
    )
    package = _build(product_profile=profile)
    assert package.unknown_topics == ("spoiler-geometry",)
    assert package.readiness == READINESS_BLOCKED
    assert not package.is_ready


def test_asset_unknown_topics_are_preserved_and_block_readiness() -> None:
    package = _build(asset_role_profile=_asset_profile(unknowns=("rear-view",)))
    assert package.unknown_topics == ("rear-view",)
    assert package.readiness == READINESS_BLOCKED


def test_declared_instruction_unknowns_are_explicit_and_block_readiness() -> None:
    package = _build(declared_unknown_topics=("required-output-size",))
    assert package.unknown_topics == ("required-output-size",)
    assert package.readiness == READINESS_BLOCKED


def test_product_and_asset_profile_conflicts_are_preserved_and_blocked() -> None:
    package = _build(
        product_profile=_product_profile(conflicts=("product-conflict",)),
        asset_role_profile=_asset_profile(conflicts=("asset-conflict",)),
    )
    assert package.conflicts == ("asset-conflict", "product-conflict")
    assert package.readiness == READINESS_BLOCKED


def test_explicit_operator_conflict_is_preserved_and_blocks() -> None:
    package = _build(
        declared_operator_conflicts=(
            "operator intent conflicts with IDENTITY_CRITICAL:variant identity",
        )
    )
    assert package.conflicts == (
        "operator intent conflicts with IDENTITY_CRITICAL:variant identity",
    )
    assert package.readiness == READINESS_BLOCKED


def test_no_unknown_or_conflict_yields_ready() -> None:
    package = _build()
    assert package.unknown_topics == ()
    assert package.conflicts == ()
    assert package.readiness == READINESS_READY


def test_operator_preserve_and_avoid_constraints_remain_only_creative_intent() -> None:
    package = _build(
        creative_brief=_brief(
            preserve=("preserve dramatic shadow",),
            avoid=("avoid warm background",),
        )
    )
    assert package.creative_brief.preserve_constraints == (
        "preserve dramatic shadow",
    )
    assert package.creative_brief.avoid_constraints == (
        "avoid warm background",
    )
    rendered_product_values = {
        value.instruction_value for value in package.product_directives
    }
    assert "preserve dramatic shadow" not in rendered_product_values
    assert "avoid warm background" not in rendered_product_values


def test_provenance_is_deterministic_union_of_product_and_active_asset_sources() -> None:
    package = _build()
    assert package.provenance_refs == (
        "prov:asset:1",
        "prov:product:1",
        "prov:product:2",
        "prov:product:3",
        "prov:product:4",
    )


def test_unselected_asset_provenance_does_not_enter_active_package_provenance() -> None:
    package = _build(creative_brief=_brief(selected=("asset-front",)))
    assert "prov:asset:2" not in package.provenance_refs


def test_reachable_declared_provenance_is_accepted_without_fabrication() -> None:
    package = _build(
        declared_provenance_refs=("prov:product:1", "prov:asset:1")
    )
    assert "prov:product:1" in package.provenance_refs
    assert "prov:asset:1" in package.provenance_refs


def test_unreachable_declared_provenance_fails_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="not reachable",
    ):
        _build(declared_provenance_refs=("fabricated:provenance",))


def test_equivalent_construction_is_deterministic() -> None:
    first = _build()
    second = _build()
    assert first == second


def test_package_readiness_is_not_approval() -> None:
    package = _build()
    assert package.readiness == READINESS_READY
    assert package.instruction_authority == "PROMPT_CANDIDATE"
    assert package.instruction_authority != "APPROVED_INSTRUCTION"


def test_duplicate_selected_reference_asset_ids_fail_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="duplicates",
    ):
        _build(
            creative_brief=_brief(
                selected=("asset-front", "asset-front"),
            )
        )


def test_invalid_package_identity_fails_closed() -> None:
    with pytest.raises(CreativeInstructionPackageContractError, match="package_id"):
        _build(package_id=" ")


def test_invalid_package_version_fails_closed() -> None:
    with pytest.raises(
        CreativeInstructionPackageContractError,
        match="package_version",
    ):
        _build(package_version="")


def test_source_is_framework_provider_model_and_persistence_neutral() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    lowered = source.lower()
    for forbidden in (
        "pyside6",
        "sqlite3",
        "requests",
        "httpx",
        "openai",
        "adobe",
        "midjourney",
        "stable diffusion",
        "comfyui",
        "torch",
        "transformers",
        "visualgenerationrequest",
        ".generate(",
        "prompt_candidate_service",
        "governed_creative_workflow_application_service",
    ):
        assert forbidden not in lowered


def test_source_does_not_mutate_existing_creative_prompt_composer() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_from_composer = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == (
            "rie.application.creative_prompt_composer"
        ):
            imported_from_composer.extend(alias.name for alias in node.names)
    assert imported_from_composer == ["CreativePromptBrief"]
    assert "CreativePromptComposer" not in source


def test_source_has_no_provider_execution_or_workflow_approval_path() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "APPROVED_INSTRUCTION" not in source
    assert "VisualGenerationRequest" not in source
    assert "VisualGenerationResult" not in source
    assert "governed_creative_workflow_request" not in source
    assert ".generate(" not in source


def test_public_surface_exposes_only_first_slice_instruction_values() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "CreativeInstructionPackageBuilder" in source
    assert "CreativeInstructionPackage" in source
    assert "CreativeInstructionProductDirective" in source
    assert "CreativeInstructionAssetDirective" in source
    assert 'INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE: Final[str] = "PROMPT_CANDIDATE"' in source
    assert 'READINESS_READY: Final[str] = "READY"' in source
    assert 'READINESS_BLOCKED: Final[str] = "BLOCKED"' in source
