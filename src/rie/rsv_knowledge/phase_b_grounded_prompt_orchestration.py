"""Deterministic Phase B grounded-prompt request orchestration.

This module composes the already-governed B1 prompt-input bridge, canonical
constraint binding, and grounded prompt compiler. It introduces no new
constraint, provenance, filesystem, database, network, model, or UI semantics.
"""

from dataclasses import dataclass
from typing import Iterable, Mapping

from rie.domain.governed_knowledge import GovernedKnowledge
from rie.evidence_materialization.evidence_materialization_contract import (
    TraceableEvidence,
)

from .constraint_binding import ConstraintBindingResult, bind_canonical_constraints
from .governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
)
from .grounded_prompt_compiler import (
    GroundedPromptCompileResult,
    compile_grounded_prompt,
)
from .phase_b_prompt_input_bridge import (
    PhaseBPromptInputBridgeResult,
    materialize_traceable_evidence_backed_product_variant_prompt_inputs,
)
from .product_catalog import ProductCatalog


@dataclass(frozen=True)
class PhaseBGroundedPromptOrchestrationResult:
    """Audit-preserving result of the existing Phase B composition chain."""

    bridge_result: PhaseBPromptInputBridgeResult
    binding_result: ConstraintBindingResult
    compile_result: GroundedPromptCompileResult


def orchestrate_exact18_grounded_prompt_request(
    *,
    collection_id: str,
    catalog: ProductCatalog,
    governed_knowledge: Iterable[GovernedKnowledge],
    knowledge_mappings: Iterable[GovernedKnowledgePromptInputMappingRecord],
    traceable_evidence_items: Iterable[TraceableEvidence],
    product_id: str,
    variant_id: str,
    creative_variables: Mapping[str, str],
    requested_output: str,
) -> PhaseBGroundedPromptOrchestrationResult:
    """Compose the approved B1 bridge, binder, and grounded prompt compiler."""

    bridge_result = (
        materialize_traceable_evidence_backed_product_variant_prompt_inputs(
            collection_id=collection_id,
            catalog=catalog,
            governed_knowledge=governed_knowledge,
            knowledge_mappings=knowledge_mappings,
            traceable_evidence_items=traceable_evidence_items,
        )
    )

    binding_result = bind_canonical_constraints(
        catalog=catalog,
        product_id=product_id,
        variant_id=variant_id,
        knowledge_records=bridge_result.prompt_inputs.knowledge_records,
        asset_records=bridge_result.prompt_inputs.asset_records,
        constraint_records=bridge_result.prompt_inputs.constraint_records,
    )

    compile_result = compile_grounded_prompt(
        binding_result=binding_result,
        creative_variables=creative_variables,
        requested_output=requested_output,
    )

    return PhaseBGroundedPromptOrchestrationResult(
        bridge_result=bridge_result,
        binding_result=binding_result,
        compile_result=compile_result,
    )
