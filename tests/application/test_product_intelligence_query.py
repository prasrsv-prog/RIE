from __future__ import annotations

import ast
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import rie.application.product_intelligence_query as query_module
from rie.application.product_intelligence_query import (
    ProductIntelligenceQuery,
    ProductIntelligenceQueryContractError,
)


def _catalog():
    return SimpleNamespace(
        products=(
            SimpleNamespace(
                product_id="sv300",
                canonical_name="SV300",
                status="active",
            ),
            SimpleNamespace(
                product_id="inactive",
                canonical_name="Inactive",
                status="inactive",
            ),
        ),
        variants=(
            SimpleNamespace(
                variant_id="sv300-white-glossy",
                product_id="sv300",
                canonical_name="White Glossy",
                status="active",
            ),
            SimpleNamespace(
                variant_id="sv300-old",
                product_id="sv300",
                canonical_name="Old",
                status="inactive",
            ),
        ),
    )


def _foundation():
    return SimpleNamespace(
        collection_id="collection-1",
        catalog=_catalog(),
        governed_knowledge=("identity-governed",),
        knowledge_mappings=("identity-mapping",),
        traceable_evidence_items=("traceable-evidence",),
        product_constraint_governed_knowledge=("manual-governed",),
        product_constraint_ingestion_manifest_records=("manual-manifest",),
        product_constraint_knowledge_mappings=("manual-mapping",),
    )


def _identity_bridge_result():
    knowledge = SimpleNamespace(
        knowledge_id="knowledge-sv300-white-glossy-variant-identity",
        product_id="sv300",
        variant_id="sv300-white-glossy",
        knowledge_type="product_variant_identity",
        subject="sv300-white-glossy",
        property="variant_identity",
        value="SV300 / White Glossy",
        source_asset_id="asset-bridge-1",
        authority="manufacturer-approved-source",
        version="2026.08",
        status="active",
    )
    asset = SimpleNamespace(
        asset_id="asset-bridge-1",
        product_id="sv300",
        variant_id="sv300-white-glossy",
        asset_type="structured_evidence",
        canonical_path="evidence://collection-1/evidence/ev-1",
        sha256="a" * 64,
        source="pilot-evidence-repository-v2",
        authority="manufacturer-approved-source",
        version="2026.08",
        status="approved",
    )
    identity_constraint = SimpleNamespace(
        constraint_id=(
            "constraint-sv300-white-glossy-product-variant-identity"
        ),
        product_id="sv300",
        variant_id="sv300-white-glossy",
        constraint_type="product_variant_identity",
        rule="preserve exact approved product and variant identity",
        source_knowledge_id_or_asset_id=knowledge.knowledge_id,
        status="active",
    )
    bridge_record = SimpleNamespace(
        original_source_asset_id="asset-original-1",
        bridged_source_asset_id="asset-bridge-1",
        product_id="sv300",
        variant_id="sv300-white-glossy",
        knowledge_id=knowledge.knowledge_id,
        traceable_evidence_id="ev-1",
        traceable_evidence_content_digest="b" * 64,
        source_relative_paths=(
            "SV300/sv300manual book.pdf",
            "SV300/White Glossy/front.png",
        ),
    )
    prompt_inputs = SimpleNamespace(
        knowledge_records=(knowledge,),
        asset_records=(asset,),
        constraint_records=(identity_constraint,),
        missing_mappings=(),
        conflicts=(),
        materialization_status="PASSED",
    )
    return SimpleNamespace(
        bridge_records=(bridge_record,),
        ingestion_manifest_records=(),
        bridged_knowledge_mappings=(),
        constraint_specs=(),
        prompt_inputs=prompt_inputs,
    )


def _exact_six_result():
    product_manual_knowledge = SimpleNamespace(
        knowledge_id="knowledge-sv300-official-product-manual",
        product_id="sv300",
        variant_id=None,
        knowledge_type="product_manual",
        subject="sv300",
        property="official_manual_content",
        value="Manual content",
        source_asset_id="asset-manual-1",
        authority="official_manual",
        version="1",
        status="active",
    )
    product_constraints = (
        SimpleNamespace(
            constraint_id="constraint-sv300-chinstrap-retention-d-ring",
            product_id="sv300",
            variant_id=None,
            constraint_type="chinstrap_retention_system",
            rule="preserve D-ring chinstrap retention system",
            source_knowledge_id_or_asset_id=(
                "knowledge-sv300-official-product-manual"
            ),
            status="active",
        ),
        SimpleNamespace(
            constraint_id="constraint-sv300-helmet-body-material-abs",
            product_id="sv300",
            variant_id=None,
            constraint_type="helmet_body_material",
            rule="preserve ABS helmet body material",
            source_knowledge_id_or_asset_id=(
                "knowledge-sv300-official-product-manual"
            ),
            status="active",
        ),
        SimpleNamespace(
            constraint_id="constraint-other-1",
            product_id="other",
            variant_id=None,
            constraint_type="other",
            rule="other",
            source_knowledge_id_or_asset_id="knowledge-other",
            status="active",
        ),
        SimpleNamespace(
            constraint_id="constraint-other-2",
            product_id="other",
            variant_id=None,
            constraint_type="other",
            rule="other",
            source_knowledge_id_or_asset_id="knowledge-other",
            status="active",
        ),
        SimpleNamespace(
            constraint_id="constraint-third-1",
            product_id="third",
            variant_id=None,
            constraint_type="other",
            rule="other",
            source_knowledge_id_or_asset_id="knowledge-third",
            status="active",
        ),
        SimpleNamespace(
            constraint_id="constraint-third-2",
            product_id="third",
            variant_id=None,
            constraint_type="other",
            rule="other",
            source_knowledge_id_or_asset_id="knowledge-third",
            status="active",
        ),
    )
    prompt_inputs = SimpleNamespace(
        knowledge_records=(product_manual_knowledge,),
        asset_records=(),
        constraint_records=product_constraints,
        missing_mappings=(),
        conflicts=(),
        materialization_status="PASSED",
    )
    return SimpleNamespace(
        authority_records=(),
        constraint_specs=(),
        prompt_inputs=prompt_inputs,
    )


@pytest.fixture
def patched_materializers(monkeypatch):
    calls = {
        "identity": [],
        "exact_six": [],
    }

    def fake_identity(**kwargs):
        calls["identity"].append(kwargs)
        return _identity_bridge_result()

    def fake_exact_six(**kwargs):
        calls["exact_six"].append(kwargs)
        return _exact_six_result()

    monkeypatch.setattr(
        query_module,
        "materialize_traceable_evidence_backed_product_variant_prompt_inputs",
        fake_identity,
    )
    monkeypatch.setattr(
        query_module,
        "materialize_exact_six_active_product_constraints",
        fake_exact_six,
    )
    return calls


def test_list_products_and_variants_preserve_canonical_active_identity(
    patched_materializers,
) -> None:
    query = ProductIntelligenceQuery(foundation=_foundation())
    assert query.list_products() == (
        query_module.ProductIntelligenceProduct(
            product_id="sv300",
            label="SV300",
        ),
    )
    assert query.list_variants("sv300") == (
        query_module.ProductIntelligenceVariant(
            variant_id="sv300-white-glossy",
            product_id="sv300",
            label="White Glossy",
        ),
    )


def test_query_uses_published_materializers_with_exact_foundation_inputs(
    patched_materializers,
) -> None:
    foundation = _foundation()
    ProductIntelligenceQuery(foundation=foundation)

    assert patched_materializers["identity"] == [
        {
            "collection_id": foundation.collection_id,
            "catalog": foundation.catalog,
            "governed_knowledge": foundation.governed_knowledge,
            "knowledge_mappings": foundation.knowledge_mappings,
            "traceable_evidence_items": foundation.traceable_evidence_items,
        }
    ]
    assert patched_materializers["exact_six"] == [
        {
            "catalog": foundation.catalog,
            "governed_knowledge": (
                foundation.product_constraint_governed_knowledge
            ),
            "ingestion_manifest_records": (
                foundation.product_constraint_ingestion_manifest_records
            ),
            "knowledge_mappings": (
                foundation.product_constraint_knowledge_mappings
            ),
        }
    ]


def test_unknown_product_and_cross_product_variant_fail_closed(
    patched_materializers,
) -> None:
    query = ProductIntelligenceQuery(foundation=_foundation())
    with pytest.raises(
        ProductIntelligenceQueryContractError,
        match="unknown active product_id",
    ):
        query.list_variants("missing")
    with pytest.raises(
        ProductIntelligenceQueryContractError,
        match="unknown active variant_id",
    ):
        query.get_product_context("sv300", "missing")


def test_context_projects_materialized_fact_and_exact_three_constraints(
    patched_materializers,
) -> None:
    query = ProductIntelligenceQuery(foundation=_foundation())
    context = query.get_product_context(
        "sv300",
        "sv300-white-glossy",
    )

    assert context.product_label == "SV300"
    assert context.variant_label == "White Glossy"
    assert len(context.fact_groups) == 1
    fact = context.fact_groups[0]
    assert fact.fact_id == "knowledge-sv300-white-glossy-variant-identity"
    assert fact.value == "SV300 / White Glossy"
    assert fact.scope == "variant"
    assert fact.provenance_refs == ("ev-1",)

    assert len(context.preservation_constraints) == 3
    assert {
        item.scope for item in context.preservation_constraints
    } == {"product", "variant"}
    rules = {item.rule_text for item in context.preservation_constraints}
    assert "preserve exact approved product and variant identity" in rules
    assert "preserve D-ring chinstrap retention system" in rules
    assert "preserve ABS helmet body material" in rules
    assert context.authorized_reference_asset_ids == ()
    assert context.conflicts == ()


def test_provenance_uses_bridge_lineage_and_materialized_authority_version(
    patched_materializers,
) -> None:
    query = ProductIntelligenceQuery(foundation=_foundation())
    provenance = query.get_provenance("ev-1")

    assert provenance.reference_id == "ev-1"
    assert provenance.source_type == "structured_evidence"
    assert provenance.authority == "manufacturer-approved-source"
    assert provenance.status == "approved"
    assert provenance.version == "2026.08"
    assert provenance.source_paths == (
        "SV300/sv300manual book.pdf",
        "SV300/White Glossy/front.png",
    )
    assert "manufacturer-approved-source" in provenance.summary
    assert "2026.08" in provenance.summary


def test_search_product_facts_searches_normalized_read_model_only(
    patched_materializers,
) -> None:
    query = ProductIntelligenceQuery(foundation=_foundation())
    result = query.search_product_facts(
        "white glossy",
        product_id="sv300",
        variant_id="sv300-white-glossy",
    )
    assert len(result) == 1
    assert result[0].value == "SV300 / White Glossy"


def test_get_provenance_rejects_unknown_reference(
    patched_materializers,
) -> None:
    query = ProductIntelligenceQuery(foundation=_foundation())
    with pytest.raises(
        ProductIntelligenceQueryContractError,
        match="unknown provenance reference",
    ):
        query.get_provenance("missing")


def test_materialization_conflict_or_count_drift_fails_closed(
    monkeypatch,
) -> None:
    bad_identity = _identity_bridge_result()
    bad_identity.prompt_inputs.materialization_status = "FAILED"

    monkeypatch.setattr(
        query_module,
        "materialize_traceable_evidence_backed_product_variant_prompt_inputs",
        lambda **kwargs: bad_identity,
    )
    monkeypatch.setattr(
        query_module,
        "materialize_exact_six_active_product_constraints",
        lambda **kwargs: _exact_six_result(),
    )

    with pytest.raises(
        ProductIntelligenceQueryContractError,
        match="identity materialization did not pass",
    ):
        ProductIntelligenceQuery(foundation=_foundation())


def test_repeat_is_deterministic(patched_materializers) -> None:
    query = ProductIntelligenceQuery(foundation=_foundation())
    first = query.get_product_context("sv300", "sv300-white-glossy")
    second = query.get_product_context("sv300", "sv300-white-glossy")
    assert first == second
    assert query.get_provenance("ev-1") == query.get_provenance("ev-1")


def test_from_intake_root_uses_frozen_application_foundation_loader(
    monkeypatch,
    patched_materializers,
) -> None:
    foundation = _foundation()
    calls = []

    def fake_loader(*, intake_root):
        calls.append(Path(intake_root))
        return foundation

    monkeypatch.setattr(
        query_module,
        "load_frozen_pilot_grounded_prompt_application_foundation",
        fake_loader,
    )
    query = ProductIntelligenceQuery.from_intake_root(
        intake_root="C:/example/intake"
    )
    assert calls == [Path("C:/example/intake")]
    assert query.list_products()[0].product_id == "sv300"


def test_application_query_is_framework_neutral_and_has_no_direct_storage_imports() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "application"
        / "product_intelligence_query.py"
    )
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    assert not any(
        name == "rie.ui" or name.startswith("rie.ui.")
        for name in imports
    )
    assert not any(
        name == "PySide6" or name.startswith("PySide6.")
        for name in imports
    )
    assert "tkinter" not in imports

    lowered = source.lower()
    for forbidden in (
        "evidence_repository",
        "governed_asset_library_registry",
        "sqlite3",
        "database_connection",
    ):
        assert forbidden not in lowered


def test_real_frozen_foundation_product_intelligence_and_provenance() -> None:
    raw_root = os.environ.get("RCIS_TEST_INTAKE_ROOT")
    intake_root = (
        Path(raw_root)
        if raw_root
        else Path.home()
        / "Downloads"
        / "RCIS-RSV-Real-Asset-Pilot-01-Intake"
    )
    assert intake_root.is_dir(), (
        "real frozen pilot intake root is required for PR-116C proof: "
        + str(intake_root)
    )

    query = ProductIntelligenceQuery.from_intake_root(
        intake_root=intake_root
    )

    products = query.list_products()
    assert len(products) == 3
    assert {item.product_id for item in products} == {
        "ffs21",
        "new-windtail",
        "sv300",
    }
    all_variants = tuple(
        variant
        for product in products
        for variant in query.list_variants(product.product_id)
    )
    assert len(all_variants) == 18
    assert len({item.variant_id for item in all_variants}) == 18

    context = query.get_product_context(
        "sv300",
        "sv300-white-glossy",
    )
    assert context.fact_groups
    assert context.preservation_constraints
    assert any(
        item.scope == "variant"
        for item in context.preservation_constraints
    )
    assert any(
        item.scope == "product"
        for item in context.preservation_constraints
    )

    provenance = tuple(
        query.get_provenance(reference_id)
        for fact in context.fact_groups
        for reference_id in fact.provenance_refs
    )
    assert provenance
    assert all(item.reference_id for item in provenance)
    assert any(
        item.authority
        and item.version
        and item.source_paths
        for item in provenance
    )

    repeated = query.get_product_context(
        "sv300",
        "sv300-white-glossy",
    )
    assert repeated == context
