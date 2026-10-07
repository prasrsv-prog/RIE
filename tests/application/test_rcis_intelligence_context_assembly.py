from dataclasses import FrozenInstanceError
import inspect
from types import SimpleNamespace

import pytest

from rie.application.product_intelligence_query import ProductIntelligenceQuery
from rie.application.visual_reference_asset_query import VisualReferenceAssetQuery
from rie.application.rcis_intelligence_context_assembly import (
    RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
    RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    RCISIntelligenceContextAssembler,
)


class _ProductIntelligenceQuery:
    def __init__(self) -> None:
        self.calls = []
        self.context = SimpleNamespace(
            fact_groups=("grounded-fact",),
            preservation_constraints=("preserve-identity",),
            unknown_topics=("unknown-mass",),
            provenance_summary="governed product intelligence",
        )

    def get_product_context(self, *, product_id: str, variant_id: str):
        self.calls.append((product_id, variant_id))
        return self.context


class _VisualReferenceAssetQuery:
    def __init__(self) -> None:
        self.calls = []
        self.assets = (
            SimpleNamespace(
                asset_id="asset-front",
                product_id="sv300",
                variant_id="sv300-white-glossy",
                status="APPROVED",
            ),
        )

    def list_assets(self, *, product_id: str, variant_id: str):
        self.calls.append((product_id, variant_id))
        return self.assets



def test_existing_read_boundaries_accept_named_product_variant_identity() -> None:
    for method in (
        ProductIntelligenceQuery.get_product_context,
        VisualReferenceAssetQuery.list_assets,
    ):
        parameters = inspect.signature(method).parameters
        for name in ("product_id", "variant_id"):
            assert name in parameters
            assert parameters[name].kind is not inspect.Parameter.POSITIONAL_ONLY


def test_assemble_preserves_existing_governed_read_models() -> None:
    product_query = _ProductIntelligenceQuery()
    visual_query = _VisualReferenceAssetQuery()
    assembler = RCISIntelligenceContextAssembler(
        product_intelligence_query=product_query,
        visual_reference_asset_query=visual_query,
    )

    result = assembler.assemble(
        product_id="sv300",
        variant_id="sv300-white-glossy",
    )

    assert product_query.calls == [("sv300", "sv300-white-glossy")]
    assert visual_query.calls == [("sv300", "sv300-white-glossy")]
    assert result.contract_version == RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION
    assert result.product_id == "sv300"
    assert result.variant_id == "sv300-white-glossy"
    assert result.product_context is product_query.context
    assert result.visual_reference_assets == visual_query.assets
    assert result.source_boundaries == RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES
    assert result.product_context.fact_groups == ("grounded-fact",)
    assert result.product_context.preservation_constraints == ("preserve-identity",)
    assert result.product_context.unknown_topics == ("unknown-mass",)
    assert result.product_context.provenance_summary == "governed product intelligence"


def test_context_contract_is_frozen() -> None:
    result = RCISIntelligenceContextAssembler(
        product_intelligence_query=_ProductIntelligenceQuery(),
        visual_reference_asset_query=_VisualReferenceAssetQuery(),
    ).assemble(product_id="sv300", variant_id="sv300-white-glossy")

    with pytest.raises(FrozenInstanceError):
        result.product_id = "other"


@pytest.mark.parametrize("product_id,variant_id", [("", "v"), ("p", ""), ("   ", "v")])
def test_assemble_rejects_empty_identity(product_id: str, variant_id: str) -> None:
    assembler = RCISIntelligenceContextAssembler(
        product_intelligence_query=_ProductIntelligenceQuery(),
        visual_reference_asset_query=_VisualReferenceAssetQuery(),
    )

    with pytest.raises(ValueError):
        assembler.assemble(product_id=product_id, variant_id=variant_id)


def test_constructor_requires_existing_read_boundaries() -> None:
    with pytest.raises(TypeError, match="get_product_context"):
        RCISIntelligenceContextAssembler(
            product_intelligence_query=object(),
            visual_reference_asset_query=_VisualReferenceAssetQuery(),
        )

    with pytest.raises(TypeError, match="list_assets"):
        RCISIntelligenceContextAssembler(
            product_intelligence_query=_ProductIntelligenceQuery(),
            visual_reference_asset_query=object(),
        )


def test_assemble_rejects_missing_product_context() -> None:
    product_query = _ProductIntelligenceQuery()
    product_query.context = None
    assembler = RCISIntelligenceContextAssembler(
        product_intelligence_query=product_query,
        visual_reference_asset_query=_VisualReferenceAssetQuery(),
    )

    with pytest.raises(TypeError, match="no product context"):
        assembler.assemble(product_id="sv300", variant_id="sv300-white-glossy")


def test_assemble_rejects_invalid_asset_values() -> None:
    visual_query = _VisualReferenceAssetQuery()
    visual_query.assets = (None,)
    assembler = RCISIntelligenceContextAssembler(
        product_intelligence_query=_ProductIntelligenceQuery(),
        visual_reference_asset_query=visual_query,
    )

    with pytest.raises(TypeError, match="invalid asset value"):
        assembler.assemble(product_id="sv300", variant_id="sv300-white-glossy")
