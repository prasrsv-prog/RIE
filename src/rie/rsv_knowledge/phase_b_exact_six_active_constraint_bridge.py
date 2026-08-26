"""Exact-six active product-level constraint bridge for Phase B."""

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from rie.domain.governed_knowledge import GovernedKnowledge

from .governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
    GovernedPromptInputMaterializationResult,
    PromptConstraintMaterializationSpec,
    materialize_governed_prompt_inputs,
)
from .ingestion_manifest import IngestionManifestRecord
from .product_catalog import ProductCatalog


class PhaseBExactSixActiveConstraintBridgeContractError(ValueError):
    """Raised when exact-six runtime authority inputs drift from approval."""


@dataclass(frozen=True)
class ExactSixActiveConstraintAuthorityRecord:
    constraint_id: str
    product_id: str
    variant_id: Optional[str]
    constraint_type: str
    rule: str
    source_knowledge_id: str
    source_governed_knowledge_id: str
    source_statement_sha256: str
    source_span_start: int
    source_span_end: int
    source_excerpt_verbatim: str
    status: str


@dataclass(frozen=True)
class PhaseBExactSixActiveConstraintBridgeResult:
    authority_records: Tuple[ExactSixActiveConstraintAuthorityRecord, ...]
    constraint_specs: Tuple[PromptConstraintMaterializationSpec, ...]
    prompt_inputs: GovernedPromptInputMaterializationResult


EXPECTED_PRODUCT_MANUAL_MAPPINGS = {
    "ffs21": {
        "governed_knowledge_id": (
            "gk1_6d6c116762e8c0bd3076ecd94a717297498da8f33d6030e34d150a672ad6500b"
        ),
        "knowledge_id": "knowledge-ffs21-official-product-manual",
        "source_id": "pilot-rsv-ffs21-product-manual",
        "source_asset_id": (
            "asset-67e7d5f723fd84180bcfcf091dfc16801b3498d95b5caefe8be351aebfc40a82"
        ),
        "source_path": "FFS21/MANUAL BOOK FFS21 fix rev.pdf",
        "source_sha256": (
            "67e7d5f723fd84180bcfcf091dfc16801b3498d95b5caefe8be351aebfc40a82"
        ),
        "knowledge_type": "product_manual",
        "subject": "ffs21",
        "property": "official_manual_content",
    },
    "new-windtail": {
        "governed_knowledge_id": (
            "gk1_876998a75a6b6cd44ff8655341fefe36f2949745bb1c2eaca48b4e36108f2ab5"
        ),
        "knowledge_id": "knowledge-new-windtail-official-product-manual",
        "source_id": "pilot-rsv-new-windtail-product-manual",
        "source_asset_id": (
            "asset-073eeb18651d5219b2e4e24c7e0df872a8199407be3e4291da4e26b3af0f1960"
        ),
        "source_path": "New-Windtail/NWT.pdf",
        "source_sha256": (
            "073eeb18651d5219b2e4e24c7e0df872a8199407be3e4291da4e26b3af0f1960"
        ),
        "knowledge_type": "product_manual",
        "subject": "new-windtail",
        "property": "official_manual_content",
    },
    "sv300": {
        "governed_knowledge_id": (
            "gk1_d712f4136ee3fdb0f06ddb810dd7e258759f40b50f606bc09eb4dd825c39c67f"
        ),
        "knowledge_id": "knowledge-sv300-official-product-manual",
        "source_id": "pilot-rsv-sv300-product-manual",
        "source_asset_id": (
            "asset-42407924c4c1781685607bb6dd2325fe5cba63924d6ed626df2c5cff699bcaa3"
        ),
        "source_path": "SV300/sv300manual book.pdf",
        "source_sha256": (
            "42407924c4c1781685607bb6dd2325fe5cba63924d6ed626df2c5cff699bcaa3"
        ),
        "knowledge_type": "product_manual",
        "subject": "sv300",
        "property": "official_manual_content",
    },
}


EXACT_SIX_ACTIVE_CONSTRAINT_AUTHORITY = (
    ExactSixActiveConstraintAuthorityRecord(
        constraint_id="constraint-ffs21-chinstrap-retention-d-ring",
        product_id="ffs21",
        variant_id=None,
        constraint_type="chinstrap_retention_system",
        rule="preserve D-ring chinstrap retention system",
        source_knowledge_id="knowledge-ffs21-official-product-manual",
        source_governed_knowledge_id=(
            "gk1_6d6c116762e8c0bd3076ecd94a717297498da8f33d6030e34d150a672ad6500b"
        ),
        source_statement_sha256=(
            "b044cd92773ff4b066cf7505165c47284f55c24e4ff53f5a4e748c0747b98243"
        ),
        source_span_start=2329,
        source_span_end=2407,
        source_excerpt_verbatim=(
            "the end of the strap through the D-rings. "
            "Make sure to fimly fasten the straps"
        ),
        status="active",
    ),
    ExactSixActiveConstraintAuthorityRecord(
        constraint_id="constraint-ffs21-helmet-body-material-abs",
        product_id="ffs21",
        variant_id=None,
        constraint_type="helmet_body_material",
        rule=(
            "preserve ABS (Acrylonitrile butadiene styrene) "
            "helmet shell material"
        ),
        source_knowledge_id="knowledge-ffs21-official-product-manual",
        source_governed_knowledge_id=(
            "gk1_6d6c116762e8c0bd3076ecd94a717297498da8f33d6030e34d150a672ad6500b"
        ),
        source_statement_sha256=(
            "b044cd92773ff4b066cf7505165c47284f55c24e4ff53f5a4e748c0747b98243"
        ),
        source_span_start=971,
        source_span_end=1021,
        source_excerpt_verbatim=(
            "of ABS (Acrylonitrile butadiene styrene) materials"
        ),
        status="active",
    ),
    ExactSixActiveConstraintAuthorityRecord(
        constraint_id="constraint-new-windtail-chinstrap-retention-microlock",
        product_id="new-windtail",
        variant_id=None,
        constraint_type="chinstrap_retention_system",
        rule="preserve Microlock chinstrap retention system",
        source_knowledge_id="knowledge-new-windtail-official-product-manual",
        source_governed_knowledge_id=(
            "gk1_876998a75a6b6cd44ff8655341fefe36f2949745bb1c2eaca48b4e36108f2ab5"
        ),
        source_statement_sha256=(
            "f75b81fead5d7bdfba1d49e3b49fa36be9dfe18be954ba1e992193f7432ec891"
        ),
        source_span_start=354,
        source_span_end=425,
        source_excerpt_verbatim=(
            "the end of the strap throught the Microlock . "
            "Make sure to fimly fasten"
        ),
        status="active",
    ),
    ExactSixActiveConstraintAuthorityRecord(
        constraint_id="constraint-new-windtail-helmet-body-material-abs",
        product_id="new-windtail",
        variant_id=None,
        constraint_type="helmet_body_material",
        rule="preserve ABS helmet body material",
        source_knowledge_id="knowledge-new-windtail-official-product-manual",
        source_governed_knowledge_id=(
            "gk1_876998a75a6b6cd44ff8655341fefe36f2949745bb1c2eaca48b4e36108f2ab5"
        ),
        source_statement_sha256=(
            "f75b81fead5d7bdfba1d49e3b49fa36be9dfe18be954ba1e992193f7432ec891"
        ),
        source_span_start=426,
        source_span_end=450,
        source_excerpt_verbatim="bodymade of ABS material",
        status="active",
    ),
    ExactSixActiveConstraintAuthorityRecord(
        constraint_id="constraint-sv300-chinstrap-retention-d-ring",
        product_id="sv300",
        variant_id=None,
        constraint_type="chinstrap_retention_system",
        rule="preserve D-ring chinstrap retention system",
        source_knowledge_id="knowledge-sv300-official-product-manual",
        source_governed_knowledge_id=(
            "gk1_d712f4136ee3fdb0f06ddb810dd7e258759f40b50f606bc09eb4dd825c39c67f"
        ),
        source_statement_sha256=(
            "a2ed98744e1e19da3c297996d6abfaba61cff543ab3d1c1c1a69b3730cf04323"
        ),
        source_span_start=250,
        source_span_end=329,
        source_excerpt_verbatim=(
            "the end of the strap throught the D-rings. "
            "Make sure to fimly fasten the straps"
        ),
        status="active",
    ),
    ExactSixActiveConstraintAuthorityRecord(
        constraint_id="constraint-sv300-helmet-body-material-abs",
        product_id="sv300",
        variant_id=None,
        constraint_type="helmet_body_material",
        rule="preserve ABS helmet body material",
        source_knowledge_id="knowledge-sv300-official-product-manual",
        source_governed_knowledge_id=(
            "gk1_d712f4136ee3fdb0f06ddb810dd7e258759f40b50f606bc09eb4dd825c39c67f"
        ),
        source_statement_sha256=(
            "a2ed98744e1e19da3c297996d6abfaba61cff543ab3d1c1c1a69b3730cf04323"
        ),
        source_span_start=330,
        source_span_end=354,
        source_excerpt_verbatim="bodymade of ABS material",
        status="active",
    ),
)


def _mapping_key(
    mapping: GovernedKnowledgePromptInputMappingRecord,
) -> tuple[object, ...]:
    return (
        mapping.governed_knowledge_id,
        mapping.knowledge_id,
        mapping.product_id,
        mapping.variant_id,
        mapping.source_id,
        mapping.source_asset_id,
        mapping.knowledge_type,
        mapping.subject,
        mapping.property,
    )


def _expected_mapping_key(product_id: str) -> tuple[object, ...]:
    expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]
    return (
        expected["governed_knowledge_id"],
        expected["knowledge_id"],
        product_id,
        None,
        expected["source_id"],
        expected["source_asset_id"],
        expected["knowledge_type"],
        expected["subject"],
        expected["property"],
    )


def _validate_explicit_manual_inputs(
    *,
    governed_knowledge: Tuple[GovernedKnowledge, ...],
    ingestion_manifest_records: Tuple[IngestionManifestRecord, ...],
    knowledge_mappings: Tuple[GovernedKnowledgePromptInputMappingRecord, ...],
) -> None:
    if len(governed_knowledge) != 3:
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "exactly three governed product manuals are required"
        )
    if len(ingestion_manifest_records) != 3:
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "exactly three product-manual manifest records are required"
        )
    if len(knowledge_mappings) != 3:
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "exactly three product-manual knowledge mappings are required"
        )

    mappings_by_product = {}
    for mapping in knowledge_mappings:
        if type(mapping) is not GovernedKnowledgePromptInputMappingRecord:
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                "knowledge_mappings must contain exact mapping records"
            )
        if mapping.product_id in mappings_by_product:
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                f"duplicate product-manual mapping: {mapping.product_id}"
            )
        mappings_by_product[mapping.product_id] = mapping

    if set(mappings_by_product) != set(EXPECTED_PRODUCT_MANUAL_MAPPINGS):
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "product-manual mapping product set drift"
        )
    for product_id, mapping in mappings_by_product.items():
        if _mapping_key(mapping) != _expected_mapping_key(product_id):
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                f"product-manual mapping identity drift: {product_id}"
            )

    governed_by_id = {}
    for value in governed_knowledge:
        if type(value) is not GovernedKnowledge:
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                "governed_knowledge must contain exact GovernedKnowledge values"
            )
        if value.governed_knowledge_id in governed_by_id:
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                f"duplicate governed product manual: {value.governed_knowledge_id}"
            )
        governed_by_id[value.governed_knowledge_id] = value

    expected_governed_ids = {
        item["governed_knowledge_id"]
        for item in EXPECTED_PRODUCT_MANUAL_MAPPINGS.values()
    }
    if set(governed_by_id) != expected_governed_ids:
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "governed product-manual identity set drift"
        )
    for product_id, expected in EXPECTED_PRODUCT_MANUAL_MAPPINGS.items():
        support_source_ids = {
            support.source_id
            for support in governed_by_id[expected["governed_knowledge_id"]].support
        }
        if expected["source_id"] not in support_source_ids:
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                f"governed product-manual support source drift: {product_id}"
            )

    manifests_by_product = {}
    for record in ingestion_manifest_records:
        if type(record) is not IngestionManifestRecord:
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                "ingestion_manifest_records must contain exact manifest records"
            )
        if record.product_id in manifests_by_product:
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                f"duplicate product-manual manifest: {record.product_id}"
            )
        manifests_by_product[record.product_id] = record

    if set(manifests_by_product) != set(EXPECTED_PRODUCT_MANUAL_MAPPINGS):
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "product-manual manifest product set drift"
        )
    for product_id, record in manifests_by_product.items():
        expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]
        if (
            record.variant_id is not None
            or record.source_sha256 != expected["source_sha256"]
            or record.status != "active"
        ):
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                f"product-manual manifest identity drift: {product_id}"
            )
        if "asset-" + record.source_sha256 != expected["source_asset_id"]:
            raise PhaseBExactSixActiveConstraintBridgeContractError(
                f"product-manual source asset drift: {product_id}"
            )


def materialize_exact_six_active_product_constraints(
    *,
    catalog: ProductCatalog,
    governed_knowledge: Iterable[GovernedKnowledge],
    ingestion_manifest_records: Iterable[IngestionManifestRecord],
    knowledge_mappings: Iterable[GovernedKnowledgePromptInputMappingRecord],
) -> PhaseBExactSixActiveConstraintBridgeResult:
    """Materialize exactly six approved active product-level constraints."""

    governed_values = tuple(governed_knowledge)
    manifest_values = tuple(ingestion_manifest_records)
    mapping_values = tuple(knowledge_mappings)

    _validate_explicit_manual_inputs(
        governed_knowledge=governed_values,
        ingestion_manifest_records=manifest_values,
        knowledge_mappings=mapping_values,
    )

    authority_records = tuple(
        sorted(
            EXACT_SIX_ACTIVE_CONSTRAINT_AUTHORITY,
            key=lambda record: (record.constraint_type, record.constraint_id),
        )
    )
    constraint_specs = tuple(
        PromptConstraintMaterializationSpec(
            constraint_id=record.constraint_id,
            product_id=record.product_id,
            variant_id=record.variant_id,
            constraint_type=record.constraint_type,
            rule=record.rule,
            source_knowledge_id_or_asset_id=record.source_knowledge_id,
            status=record.status,
        )
        for record in authority_records
    )

    prompt_inputs = materialize_governed_prompt_inputs(
        catalog=catalog,
        governed_knowledge=governed_values,
        ingestion_manifest_records=manifest_values,
        knowledge_mappings=mapping_values,
        constraint_specs=constraint_specs,
    )
    if prompt_inputs.materialization_status != "PASSED":
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "exact-six governed prompt-input materialization failed: "
            + "|".join(prompt_inputs.missing_mappings + prompt_inputs.conflicts)
        )

    expected_constraint_ids = tuple(
        record.constraint_id for record in authority_records
    )
    actual_constraint_ids = tuple(
        record.constraint_id for record in prompt_inputs.constraint_records
    )
    if len(prompt_inputs.constraint_records) != 6:
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "exact-six materialized constraint count drift"
        )
    if actual_constraint_ids != expected_constraint_ids:
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "exact-six materialized constraint identity drift"
        )
    if not all(
        record.variant_id is None and record.status == "active"
        for record in prompt_inputs.constraint_records
    ):
        raise PhaseBExactSixActiveConstraintBridgeContractError(
            "exact-six active product-level scope drift"
        )

    return PhaseBExactSixActiveConstraintBridgeResult(
        authority_records=authority_records,
        constraint_specs=constraint_specs,
        prompt_inputs=prompt_inputs,
    )
