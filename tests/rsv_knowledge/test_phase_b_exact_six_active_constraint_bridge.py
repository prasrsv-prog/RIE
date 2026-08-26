from types import SimpleNamespace

import pytest

from rie.domain.governed_knowledge import GovernedKnowledge
from rie.rsv_knowledge.constraint_binding import bind_canonical_constraints
from rie.rsv_knowledge.governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
)
from rie.rsv_knowledge.ingestion_manifest import IngestionManifestRecord
from rie.rsv_knowledge.phase_b_exact_six_active_constraint_bridge import (
    EXACT_SIX_ACTIVE_CONSTRAINT_AUTHORITY,
    EXPECTED_PRODUCT_MANUAL_MAPPINGS,
    PhaseBExactSixActiveConstraintBridgeContractError,
    materialize_exact_six_active_product_constraints,
)
from rie.rsv_knowledge.product_catalog import (
    ProductCatalog,
    ProductRecord,
    VariantRecord,
)


def catalog():
    return ProductCatalog(
        products=[
            ProductRecord("ffs21", "FFS21", "RSV", "active"),
            ProductRecord("new-windtail", "New Windtail", "RSV", "active"),
            ProductRecord("sv300", "SV300", "RSV", "active"),
        ],
        variants=[
            VariantRecord("ffs21-v1", "ffs21", "FFS21 V1", "active"),
            VariantRecord(
                "new-windtail-v1",
                "new-windtail",
                "New Windtail V1",
                "active",
            ),
            VariantRecord("sv300-v1", "sv300", "SV300 V1", "active"),
        ],
    )


def governed(product_id, source_id=None):
    expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]
    value = object.__new__(GovernedKnowledge)
    object.__setattr__(
        value,
        "governed_knowledge_id",
        expected["governed_knowledge_id"],
    )
    object.__setattr__(value, "statement", f"synthetic manual for {product_id}")
    object.__setattr__(
        value,
        "support",
        (
            SimpleNamespace(
                source_id=source_id
                if source_id is not None
                else expected["source_id"]
            ),
        ),
    )
    return value


def mapping(product_id, *, variant_id=None, source_id=None):
    expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]
    return GovernedKnowledgePromptInputMappingRecord(
        governed_knowledge_id=expected["governed_knowledge_id"],
        knowledge_id=expected["knowledge_id"],
        product_id=product_id,
        variant_id=variant_id,
        source_id=source_id if source_id is not None else expected["source_id"],
        source_asset_id=expected["source_asset_id"],
        knowledge_type=expected["knowledge_type"],
        subject=expected["subject"],
        property=expected["property"],
    )


def manifest(product_id):
    expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]
    return IngestionManifestRecord(
        source_path=expected["source_path"],
        source_sha256=expected["source_sha256"],
        product_id=product_id,
        variant_id=None,
        knowledge_type="product_manual",
        asset_type="pdf",
        source=expected["source_id"],
        authority="RSV_INTERNAL_APPROVED_SOURCE",
        version="2026-08-09",
        status="active",
    )


def fixture_values():
    product_ids = ("ffs21", "new-windtail", "sv300")
    return (
        [governed(product_id) for product_id in product_ids],
        [manifest(product_id) for product_id in product_ids],
        [mapping(product_id) for product_id in product_ids],
    )


def materialized():
    governed_values, manifest_values, mapping_values = fixture_values()
    return materialize_exact_six_active_product_constraints(
        catalog=catalog(),
        governed_knowledge=governed_values,
        ingestion_manifest_records=manifest_values,
        knowledge_mappings=mapping_values,
    )


def test_exact_six_authority_is_exact_active_product_level_set():
    assert len(EXACT_SIX_ACTIVE_CONSTRAINT_AUTHORITY) == 6
    assert len(
        {record.constraint_id for record in EXACT_SIX_ACTIVE_CONSTRAINT_AUTHORITY}
    ) == 6
    assert {
        record.product_id for record in EXACT_SIX_ACTIVE_CONSTRAINT_AUTHORITY
    } == {"ffs21", "new-windtail", "sv300"}
    assert all(
        record.variant_id is None and record.status == "active"
        for record in EXACT_SIX_ACTIVE_CONSTRAINT_AUTHORITY
    )
    assert {
        record.constraint_type
        for record in EXACT_SIX_ACTIVE_CONSTRAINT_AUTHORITY
    } == {"helmet_body_material", "chinstrap_retention_system"}


def test_bridge_materializes_exact_six_active_constraints_with_manual_provenance():
    result = materialized()

    assert result.prompt_inputs.materialization_status == "PASSED"
    assert len(result.authority_records) == 6
    assert len(result.constraint_specs) == 6
    assert len(result.prompt_inputs.constraint_records) == 6
    assert len(result.prompt_inputs.knowledge_records) == 3
    assert len(result.prompt_inputs.asset_records) == 3
    assert all(
        record.variant_id is None and record.status == "active"
        for record in result.prompt_inputs.constraint_records
    )
    assert {
        record.source_knowledge_id_or_asset_id
        for record in result.prompt_inputs.constraint_records
    } == {
        "knowledge-ffs21-official-product-manual",
        "knowledge-new-windtail-official-product-manual",
        "knowledge-sv300-official-product-manual",
    }


def test_bridge_is_deterministic_for_reordered_explicit_inputs():
    governed_values, manifest_values, mapping_values = fixture_values()
    first = materialize_exact_six_active_product_constraints(
        catalog=catalog(),
        governed_knowledge=governed_values,
        ingestion_manifest_records=manifest_values,
        knowledge_mappings=mapping_values,
    )
    second = materialize_exact_six_active_product_constraints(
        catalog=catalog(),
        governed_knowledge=list(reversed(governed_values)),
        ingestion_manifest_records=list(reversed(manifest_values)),
        knowledge_mappings=list(reversed(mapping_values)),
    )

    assert second == first


def test_bridge_fails_closed_when_one_manual_mapping_is_missing():
    governed_values, manifest_values, mapping_values = fixture_values()

    with pytest.raises(
        PhaseBExactSixActiveConstraintBridgeContractError,
        match="exactly three product-manual knowledge mappings",
    ):
        materialize_exact_six_active_product_constraints(
            catalog=catalog(),
            governed_knowledge=governed_values,
            ingestion_manifest_records=manifest_values,
            knowledge_mappings=mapping_values[:-1],
        )


def test_bridge_fails_closed_on_variant_scoped_manual_mapping():
    governed_values, manifest_values, mapping_values = fixture_values()
    mapping_values[-1] = mapping("sv300", variant_id="sv300-v1")

    with pytest.raises(
        PhaseBExactSixActiveConstraintBridgeContractError,
        match="product-manual mapping identity drift: sv300",
    ):
        materialize_exact_six_active_product_constraints(
            catalog=catalog(),
            governed_knowledge=governed_values,
            ingestion_manifest_records=manifest_values,
            knowledge_mappings=mapping_values,
        )


def test_bridge_fails_closed_on_wrong_governed_support_source():
    governed_values, manifest_values, mapping_values = fixture_values()
    governed_values[-1] = governed("sv300", source_id="wrong-source")

    with pytest.raises(
        PhaseBExactSixActiveConstraintBridgeContractError,
        match="governed product-manual support source drift: sv300",
    ):
        materialize_exact_six_active_product_constraints(
            catalog=catalog(),
            governed_knowledge=governed_values,
            ingestion_manifest_records=manifest_values,
            knowledge_mappings=mapping_values,
        )


def test_exact_six_bind_as_two_product_level_constraints_per_product_without_projection():
    result = materialized()
    c = catalog()

    for product_id, variant_id in (
        ("ffs21", "ffs21-v1"),
        ("new-windtail", "new-windtail-v1"),
        ("sv300", "sv300-v1"),
    ):
        binding = bind_canonical_constraints(
            catalog=c,
            product_id=product_id,
            variant_id=variant_id,
            knowledge_records=result.prompt_inputs.knowledge_records,
            asset_records=result.prompt_inputs.asset_records,
            constraint_records=result.prompt_inputs.constraint_records,
        )
        assert binding.binding_status == "PASSED"
        assert len(binding.bound_constraints) == 2
        assert all(
            record.product_id == product_id and record.variant_id is None
            for record in binding.bound_constraints
        )
        assert binding.used_knowledge_ids == (
            EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]["knowledge_id"],
        )
