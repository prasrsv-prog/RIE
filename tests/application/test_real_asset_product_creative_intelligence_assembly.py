from dataclasses import dataclass

import pytest

from rie.application.creative_prompt_composer import CreativePromptBrief
from rie.application.real_asset_product_creative_intelligence_assembly import (
    READINESS_READY,
    RealAssetProductCreativeIntelligenceAssembler,
    RealAssetProductCreativeIntelligenceAssemblyContractError,
)


@dataclass(frozen=True)
class _Asset:
    reference_id: str
    asset_id: str
    product_id: str = "product-1"
    variant_id: str = "variant-1"
    sha256: str = "a" * 64


@dataclass(frozen=True)
class _Directive:
    asset_id: str


@dataclass(frozen=True)
class _Unknown:
    topic: str


@dataclass(frozen=True)
class _Profile:
    unknown_topics: tuple = ()
    conflicts: tuple = ()
    provenance_refs: tuple = ()


@dataclass(frozen=True)
class _Package:
    readiness: str = READINESS_READY
    unknown_topics: tuple = ()
    conflicts: tuple = ()
    provenance_refs: tuple = ("package-prov",)
    instruction_authority: str = "PROMPT_CANDIDATE"


class _ProductQuery:
    def __init__(self):
        self.calls = []

    def get_product_context(self, product_id, variant_id):
        self.calls.append((product_id, variant_id))
        return object()


class _VisualQuery:
    def __init__(self, assets):
        self.assets = tuple(assets)
        self.calls = []

    def list_assets(self, *, product_id, variant_id):
        self.calls.append((product_id, variant_id))
        return self.assets


class _ProductBuilder:
    def __init__(self):
        self.kwargs = None

    def build(self, **kwargs):
        self.kwargs = kwargs
        return _Profile(provenance_refs=("product-prov",))


class _RoleBuilder:
    def __init__(self):
        self.kwargs = None

    def build(self, **kwargs):
        self.kwargs = kwargs
        return _Profile(provenance_refs=("role-prov",))


class _InstructionBuilder:
    def __init__(self):
        self.kwargs = None

    def build(self, **kwargs):
        self.kwargs = kwargs
        return _Package()


def _assembler(assets):
    product_query = _ProductQuery()
    visual_query = _VisualQuery(assets)
    product_builder = _ProductBuilder()
    role_builder = _RoleBuilder()
    instruction_builder = _InstructionBuilder()
    assembler = RealAssetProductCreativeIntelligenceAssembler(
        product_intelligence_query=product_query,
        visual_reference_asset_query=visual_query,
        product_profile_builder=product_builder,
        asset_role_profile_builder=role_builder,
        instruction_package_builder=instruction_builder,
    )
    return (
        assembler,
        product_query,
        visual_query,
        product_builder,
        role_builder,
        instruction_builder,
    )


def _assemble(assembler, *, selected=("ref-1",), directives=(_Directive("asset-1"),)):
    return assembler.assemble(
        product_id="product-1",
        variant_id="variant-1",
        product_profile_id="cpp-1",
        product_profile_version="1",
        product_rules=(),
        asset_role_profile_id="carp-1",
        asset_role_profile_version="1",
        asset_role_directives=directives,
        instruction_package_id="cip-1",
        instruction_package_version="1",
        creative_brief=CreativePromptBrief(selected_reference_asset_ids=selected),
    )


def test_valid_assembly_delegates_exact_boundaries_and_preserves_order():
    assets = (_Asset("ref-1", "asset-1"), _Asset("ref-2", "asset-2"))
    assembler, product_query, visual_query, product_builder, role_builder, instruction_builder = _assembler(assets)

    result = _assemble(
        assembler,
        selected=("ref-2", "ref-1"),
        directives=(_Directive("asset-1"), _Directive("asset-2")),
    )

    assert product_query.calls == [("product-1", "variant-1")]
    assert visual_query.calls == [("product-1", "variant-1")]
    assert tuple(asset.reference_id for asset in result.selected_reference_assets) == ("ref-2", "ref-1")
    assert tuple(asset.reference_id for asset in role_builder.kwargs["governed_assets"]) == ("ref-2", "ref-1")
    assert product_builder.kwargs["context"] is not None
    assert instruction_builder.kwargs["product_profile"] is result.product_profile
    assert instruction_builder.kwargs["asset_role_profile"] is result.asset_role_profile
    assert result.instruction_package.instruction_authority == "PROMPT_CANDIDATE"
    assert result.readiness == "READY"
    assert result.provenance_refs == ("product-prov", "role-prov", "package-prov")


def test_missing_explicit_role_directive_fails_closed_before_role_or_instruction_build():
    assembler, _, _, _, role_builder, instruction_builder = _assembler(
        (_Asset("ref-1", "asset-1"),)
    )

    with pytest.raises(
        RealAssetProductCreativeIntelligenceAssemblyContractError,
        match="explicit asset-role directive",
    ):
        _assemble(assembler, directives=())

    assert role_builder.kwargs is None
    assert instruction_builder.kwargs is None


def test_ungoverned_selected_reference_fails_closed():
    assembler, _, _, _, role_builder, instruction_builder = _assembler(
        (_Asset("ref-1", "asset-1"),)
    )

    with pytest.raises(
        RealAssetProductCreativeIntelligenceAssemblyContractError,
        match="not governed",
    ):
        _assemble(
            assembler,
            selected=("ref-missing",),
            directives=(_Directive("asset-missing"),),
        )

    assert role_builder.kwargs is None
    assert instruction_builder.kwargs is None


def test_duplicate_selected_reference_fails_closed():
    assembler, *_ = _assembler((_Asset("ref-1", "asset-1"),))

    with pytest.raises(
        RealAssetProductCreativeIntelligenceAssemblyContractError,
        match="must not contain duplicates",
    ):
        _assemble(
            assembler,
            selected=("ref-1", "ref-1"),
            directives=(_Directive("asset-1"),),
        )


def test_product_variant_identity_is_forwarded_without_substitution():
    assembler, product_query, visual_query, *_ = _assembler(
        (_Asset("ref-1", "asset-1"),)
    )
    _assemble(assembler)
    assert product_query.calls == [("product-1", "variant-1")]
    assert visual_query.calls == [("product-1", "variant-1")]
