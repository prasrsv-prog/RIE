"""Phase B production orchestration for grounded RSV prompt requests."""

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Tuple

from rie.domain.governed_knowledge import GovernedKnowledge
from rie.evidence_materialization.evidence_materialization_contract import (
    TraceableEvidence,
)

from .constraint_binding import (
    ConstraintBindingResult,
    bind_canonical_constraints,
)
from .governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
)
from .grounded_prompt_compiler import (
    GroundedPromptCompileResult,
    compile_grounded_prompt,
)
from .ingestion_manifest import IngestionManifestRecord
from .phase_b_exact_six_active_constraint_bridge import (
    PhaseBExactSixActiveConstraintBridgeResult,
    materialize_exact_six_active_product_constraints,
)
from .phase_b_prompt_input_bridge import (
    PhaseBPromptInputBridgeResult,
    materialize_traceable_evidence_backed_product_variant_prompt_inputs,
)
from .product_catalog import ProductCatalog


@dataclass(frozen=True)
class PhaseBGroundedPromptOrchestrationResult:
    bridge_result: PhaseBPromptInputBridgeResult
    exact_six_bridge_result: PhaseBExactSixActiveConstraintBridgeResult
    binding_result: ConstraintBindingResult
    compile_result: GroundedPromptCompileResult


def _merge_records_by_id(
    first: Iterable[object],
    second: Iterable[object],
    id_field: str,
) -> Tuple[object, ...]:
    values = tuple(first) + tuple(second)
    identifiers = [getattr(value, id_field) for value in values]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError(f"duplicate merged {id_field}")
    return tuple(sorted(values, key=lambda value: getattr(value, id_field)))


def orchestrate_exact18_grounded_prompt_request(
    *,
    collection_id: str,
    catalog: ProductCatalog,
    governed_knowledge: Iterable[GovernedKnowledge],
    knowledge_mappings: Iterable[GovernedKnowledgePromptInputMappingRecord],
    traceable_evidence_items: Iterable[TraceableEvidence],
    product_constraint_governed_knowledge: Iterable[GovernedKnowledge],
    product_constraint_ingestion_manifest_records: Iterable[IngestionManifestRecord],
    product_constraint_knowledge_mappings: Iterable[
        GovernedKnowledgePromptInputMappingRecord
    ],
    product_id: str,
    variant_id: Optional[str],
    creative_variables: Mapping[str, str],
    requested_output: str,
) -> PhaseBGroundedPromptOrchestrationResult:
    """Compose exact18 identity and approved exact-six product constraints."""

    bridge_result = (
        materialize_traceable_evidence_backed_product_variant_prompt_inputs(
            collection_id=collection_id,
            catalog=catalog,
            governed_knowledge=governed_knowledge,
            knowledge_mappings=knowledge_mappings,
            traceable_evidence_items=traceable_evidence_items,
        )
    )
    exact_six_bridge_result = materialize_exact_six_active_product_constraints(
        catalog=catalog,
        governed_knowledge=product_constraint_governed_knowledge,
        ingestion_manifest_records=(
            product_constraint_ingestion_manifest_records
        ),
        knowledge_mappings=product_constraint_knowledge_mappings,
    )

    knowledge_records = _merge_records_by_id(
        bridge_result.prompt_inputs.knowledge_records,
        exact_six_bridge_result.prompt_inputs.knowledge_records,
        "knowledge_id",
    )
    asset_records = _merge_records_by_id(
        bridge_result.prompt_inputs.asset_records,
        exact_six_bridge_result.prompt_inputs.asset_records,
        "asset_id",
    )
    constraint_records = _merge_records_by_id(
        bridge_result.prompt_inputs.constraint_records,
        exact_six_bridge_result.prompt_inputs.constraint_records,
        "constraint_id",
    )

    binding_result = bind_canonical_constraints(
        catalog=catalog,
        product_id=product_id,
        variant_id=variant_id,
        knowledge_records=knowledge_records,
        asset_records=asset_records,
        constraint_records=constraint_records,
    )
    compile_result = compile_grounded_prompt(
        binding_result=binding_result,
        creative_variables=creative_variables,
        requested_output=requested_output,
    )
    return PhaseBGroundedPromptOrchestrationResult(
        bridge_result=bridge_result,
        exact_six_bridge_result=exact_six_bridge_result,
        binding_result=binding_result,
        compile_result=compile_result,
    )
