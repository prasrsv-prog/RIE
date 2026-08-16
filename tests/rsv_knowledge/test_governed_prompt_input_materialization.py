from datetime import datetime, timezone

import pytest

from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
    REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,
    GovernedKnowledge,
    GovernedKnowledgeIdentityInput,
    compute_governed_knowledge_id,
)
from rie.domain.knowledge_candidate import KnowledgeEvidenceSupport
from rie.rsv_knowledge import (
    IngestionManifestRecord,
    ProductCatalog,
    ProductRecord,
    VariantRecord,
)
from rie.rsv_knowledge.constraint_binding import bind_canonical_constraints
from rie.rsv_knowledge.governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
    GovernedPromptInputMaterializationContractError,
    PromptConstraintMaterializationSpec,
    materialize_governed_prompt_inputs,
)


NOW = datetime(2026, 8, 16, 3, 0, 0, tzinfo=timezone.utc)


def build_catalog():
    return ProductCatalog(
        products=[
            ProductRecord("new-windtail", "New Windtail", "RSV", "active"),
            ProductRecord("sv300", "SV300", "RSV", "active"),
        ],
        variants=[
            VariantRecord(
                "new-windtail-black-glossy",
                "new-windtail",
                "Black Glossy",
                "active",
            )
        ],
    )


def manifest(
    *,
    source_path="New-Windtail/NWT.pdf",
    source_sha="a" * 64,
    product_id="new-windtail",
    variant_id=None,
    asset_type="pdf",
):
    return IngestionManifestRecord(
        source_path=source_path,
        source_sha256=source_sha,
        product_id=product_id,
        variant_id=variant_id,
        knowledge_type=(
            "official_product_document"
            if asset_type == "pdf"
            else "visual_reference"
        ),
        asset_type=asset_type,
        source="RSV_INTERNAL",
        authority="RSV_INTERNAL_APPROVED_SOURCE",
        version="2026-08-09",
        status="active",
    )


def governed(
    *,
    statement="Exact governed shell geometry statement.",
    source_id="pilot-rsv-new-windtail-product-manual",
):
    support = KnowledgeEvidenceSupport(
        evidence_id="ev1_" + "1" * 64,
        acceptance_record_ids=("ar1_" + "2" * 64,),
        acceptance_review_record_ids=("review-1",),
        source_id=source_id,
        source_content_digest="3" * 64,
        source_authority_status="authoritative",
        source_lifecycle_status="active",
        payload_digest="4" * 64,
        locator_type="text-span",
        locator_value="page-1",
        locator_schema_version="1.0.0",
    )
    identity = GovernedKnowledgeIdentityInput(
        contract_version=GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
        knowledge_candidate_id="kc1_" + "5" * 64,
        knowledge_candidate_contract_version="knowledge-candidate-v1",
        knowledge_candidate_snapshot_digest="6" * 64,
        statement_type="fact",
        statement=statement,
        support=(support,),
        knowledge_promotion_prerequisite_evaluation_id="kpe1_" + "7" * 64,
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            "knowledge-promotion-prerequisite-evaluation-v1"
        ),
        knowledge_promotion_decision_id="kpd1_" + "8" * 64,
        knowledge_promotion_decision_contract_version=(
            "knowledge-promotion-decision-v1"
        ),
        promotion_decision_outcome=(
            "promotion_authorized_for_future_execution"
        ),
        authorization_scope=(
            "eligible_for_future_promotion_execution_for_declared_scope"
        ),
        knowledge_promotion_execution_id="kpx1_" + "9" * 64,
        knowledge_promotion_execution_contract_version=(
            "knowledge-promotion-execution-v1"
        ),
        promotion_execution_scope="promotion_execution_for_declared_scope",
        promotion_execution_outcome=(
            "promotion_execution_completed_for_declared_scope"
        ),
        construction_scope=GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
        construction_reference="pilot-construction",
        reason_codes=(REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,),
        constructed_by="rcis-rsv-real-asset-pilot-primary-operator",
        constructed_at=NOW,
        construction_policy_id="rcis-governed-knowledge-construction",
        construction_policy_version="1.0.0",
    )
    return GovernedKnowledge(
        governed_knowledge_id=compute_governed_knowledge_id(identity),
        contract_version=identity.contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            identity.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            identity.knowledge_candidate_snapshot_digest
        ),
        statement_type=identity.statement_type,
        statement=identity.statement,
        support=identity.support,
        knowledge_promotion_prerequisite_evaluation_id=(
            identity.knowledge_promotion_prerequisite_evaluation_id
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            identity.knowledge_promotion_prerequisite_evaluation_contract_version
        ),
        knowledge_promotion_decision_id=identity.knowledge_promotion_decision_id,
        knowledge_promotion_decision_contract_version=(
            identity.knowledge_promotion_decision_contract_version
        ),
        promotion_decision_outcome=identity.promotion_decision_outcome,
        authorization_scope=identity.authorization_scope,
        knowledge_promotion_execution_id=identity.knowledge_promotion_execution_id,
        knowledge_promotion_execution_contract_version=(
            identity.knowledge_promotion_execution_contract_version
        ),
        promotion_execution_scope=identity.promotion_execution_scope,
        promotion_execution_outcome=identity.promotion_execution_outcome,
        construction_scope=identity.construction_scope,
        construction_reference=identity.construction_reference,
        reason_codes=identity.reason_codes,
        constructed_by=identity.constructed_by,
        constructed_at=identity.constructed_at,
        construction_policy_id=identity.construction_policy_id,
        construction_policy_version=identity.construction_policy_version,
        diagnostics=(),
    )


def mapping(value, *, product_id="new-windtail", variant_id=None):
    return GovernedKnowledgePromptInputMappingRecord(
        governed_knowledge_id=value.governed_knowledge_id,
        knowledge_id="knowledge-new-windtail-shell",
        product_id=product_id,
        variant_id=variant_id,
        source_id="pilot-rsv-new-windtail-product-manual",
        source_asset_id="asset-" + "a" * 64,
        knowledge_type="product_detail",
        subject="helmet",
        property="shell_geometry",
    )


def constraint(*, product_id="new-windtail", variant_id=None):
    return PromptConstraintMaterializationSpec(
        constraint_id="constraint-new-windtail-shell",
        product_id=product_id,
        variant_id=variant_id,
        constraint_type="shell_geometry",
        rule="preserve exact shell geometry",
        source_knowledge_id_or_asset_id="knowledge-new-windtail-shell",
    )


def test_materialization_preserves_exact_statement_provenance_and_existing_types():
    value = governed()
    result = materialize_governed_prompt_inputs(
        catalog=build_catalog(),
        governed_knowledge=[value],
        ingestion_manifest_records=[manifest()],
        knowledge_mappings=[mapping(value)],
        constraint_specs=[constraint()],
    )

    assert result.materialization_status == "PASSED"
    assert result.missing_mappings == ()
    assert result.conflicts == ()
    assert len(result.knowledge_records) == 1
    assert len(result.asset_records) == 1
    assert len(result.constraint_records) == 1

    knowledge = result.knowledge_records[0]
    asset = result.asset_records[0]
    materialized_constraint = result.constraint_records[0]

    assert knowledge.value == value.statement
    assert knowledge.knowledge_type == "product_detail"
    assert knowledge.subject == "helmet"
    assert knowledge.property == "shell_geometry"
    assert knowledge.source_asset_id == asset.asset_id
    assert knowledge.authority == asset.authority
    assert knowledge.version == asset.version
    assert asset.asset_id == "asset-" + "a" * 64
    assert materialized_constraint.rule == "preserve exact shell geometry"

    bound = bind_canonical_constraints(
        catalog=build_catalog(),
        product_id="new-windtail",
        variant_id=None,
        knowledge_records=result.knowledge_records,
        asset_records=result.asset_records,
        constraint_records=result.constraint_records,
    )
    assert bound.binding_status == "PASSED"
    assert bound.used_knowledge_ids == ("knowledge-new-windtail-shell",)


def test_materialization_fails_closed_when_governed_mapping_is_missing():
    value = governed()
    result = materialize_governed_prompt_inputs(
        catalog=build_catalog(),
        governed_knowledge=[value],
        ingestion_manifest_records=[manifest()],
        knowledge_mappings=[],
        constraint_specs=[],
    )

    assert result.materialization_status == "FAILED"
    assert result.missing_mappings == (value.governed_knowledge_id,)
    assert result.knowledge_records == ()
    assert result.asset_records == ()
    assert result.constraint_records == ()


def test_materialization_fails_closed_when_explicit_source_id_is_not_in_support():
    value = governed()
    bad = GovernedKnowledgePromptInputMappingRecord(
        governed_knowledge_id=value.governed_knowledge_id,
        knowledge_id="knowledge-new-windtail-shell",
        product_id="new-windtail",
        variant_id=None,
        source_id="wrong-source",
        source_asset_id="asset-" + "a" * 64,
        knowledge_type="product_detail",
        subject="helmet",
        property="shell_geometry",
    )
    result = materialize_governed_prompt_inputs(
        catalog=build_catalog(),
        governed_knowledge=[value],
        ingestion_manifest_records=[manifest()],
        knowledge_mappings=[bad],
        constraint_specs=[],
    )

    assert result.materialization_status == "FAILED"
    assert result.knowledge_records == ()
    assert result.conflicts == (
        "governed_support_source_mismatch:"
        "knowledge-new-windtail-shell:wrong-source",
    )


def test_materialization_rejects_cross_product_source_asset_scope():
    value = governed()
    with pytest.raises(
        GovernedPromptInputMaterializationContractError,
        match="unknown variant_id|does not belong|unknown product_id",
    ):
        materialize_governed_prompt_inputs(
            catalog=build_catalog(),
            governed_knowledge=[value],
            ingestion_manifest_records=[manifest(product_id="new-windtail")],
            knowledge_mappings=[
                mapping(
                    value,
                    product_id="sv300",
                    variant_id="new-windtail-black-glossy",
                )
            ],
            constraint_specs=[],
        )


def test_materialization_fails_closed_when_constraint_source_is_missing():
    value = governed()
    result = materialize_governed_prompt_inputs(
        catalog=build_catalog(),
        governed_knowledge=[value],
        ingestion_manifest_records=[manifest()],
        knowledge_mappings=[mapping(value)],
        constraint_specs=[
            PromptConstraintMaterializationSpec(
                constraint_id="constraint-missing",
                product_id="new-windtail",
                variant_id=None,
                constraint_type="visor",
                rule="preserve visor",
                source_knowledge_id_or_asset_id="missing-source",
            )
        ],
    )

    assert result.materialization_status == "FAILED"
    assert result.constraint_records == ()
    assert result.conflicts == (
        "constraint_source_missing:constraint-missing:missing-source",
    )


def test_materialization_is_deterministic_for_reordered_explicit_inputs():
    value = governed()
    second_manifest = manifest(
        source_path="New-Windtail/left.jpg",
        source_sha="b" * 64,
        variant_id="new-windtail-black-glossy",
        asset_type="image",
    )
    first = materialize_governed_prompt_inputs(
        catalog=build_catalog(),
        governed_knowledge=[value],
        ingestion_manifest_records=[manifest(), second_manifest],
        knowledge_mappings=[mapping(value)],
        constraint_specs=[constraint()],
    )
    second = materialize_governed_prompt_inputs(
        catalog=build_catalog(),
        governed_knowledge=[value],
        ingestion_manifest_records=[second_manifest, manifest()],
        knowledge_mappings=[mapping(value)],
        constraint_specs=[constraint()],
    )

    assert first == second


def test_mapping_taxonomy_fields_are_required_and_never_inferred():
    value = governed()
    with pytest.raises(
        GovernedPromptInputMaterializationContractError,
        match="knowledge_type must not be empty",
    ):
        GovernedKnowledgePromptInputMappingRecord(
            governed_knowledge_id=value.governed_knowledge_id,
            knowledge_id="knowledge-new-windtail-shell",
            product_id="new-windtail",
            variant_id=None,
            source_id="pilot-rsv-new-windtail-product-manual",
            source_asset_id="asset-" + "a" * 64,
            knowledge_type="",
            subject="helmet",
            property="shell_geometry",
        )
