from __future__ import annotations

from rie.application.grounded_prompt_application_service import (
    FROZEN_GROUNDED_PROMPT_ORCHESTRATOR,
    GroundedPromptApplicationService,
)


FOUNDATION_DEPENDENCY_NAMES = (
    "collection_id",
    "catalog",
    "governed_knowledge",
    "knowledge_mappings",
    "traceable_evidence_items",
    "product_constraint_governed_knowledge",
    "product_constraint_ingestion_manifest_records",
    "product_constraint_knowledge_mappings",
)


def build_grounded_prompt_application_service(
    *,
    collection_id: object,
    catalog: object,
    governed_knowledge: object,
    knowledge_mappings: object,
    traceable_evidence_items: object,
    product_constraint_governed_knowledge: object,
    product_constraint_ingestion_manifest_records: object,
    product_constraint_knowledge_mappings: object,
) -> GroundedPromptApplicationService:
    foundation_dependencies = {
        "collection_id": collection_id,
        "catalog": catalog,
        "governed_knowledge": governed_knowledge,
        "knowledge_mappings": knowledge_mappings,
        "traceable_evidence_items": traceable_evidence_items,
        "product_constraint_governed_knowledge": product_constraint_governed_knowledge,
        "product_constraint_ingestion_manifest_records": (
            product_constraint_ingestion_manifest_records
        ),
        "product_constraint_knowledge_mappings": (
            product_constraint_knowledge_mappings
        ),
    }

    return GroundedPromptApplicationService(
        orchestrator=FROZEN_GROUNDED_PROMPT_ORCHESTRATOR,
        foundation_dependencies=foundation_dependencies,
    )
