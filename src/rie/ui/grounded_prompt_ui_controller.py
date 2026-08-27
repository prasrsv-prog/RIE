"""Toolkit-independent controller for the Phase F grounded prompt UI MVP."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rie.application.grounded_prompt_application_composition_root import (
    build_grounded_prompt_application_service,
)
from rie.application.grounded_prompt_application_foundation_provider import (
    load_frozen_pilot_grounded_prompt_application_foundation,
)
from rie.application.grounded_prompt_application_service import (
    GroundedPromptApplicationRequest,
)


class GroundedPromptUiContractError(ValueError):
    """Raised when explicit operator UI input violates the Phase F contract."""


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise GroundedPromptUiContractError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise GroundedPromptUiContractError(f"{field_name} must not be empty")
    return normalized


@dataclass(frozen=True)
class GroundedPromptUiResult:
    product_id: str
    variant_id: str
    prompt_text: str
    bridge_materialization_status: str
    exact_six_materialization_status: str
    binding_status: str
    grounding_status: str


class GroundedPromptUiController:
    """Thin UI-independent adapter over the published Phase E application surface."""

    def __init__(self, *, catalog: Any, service: Any) -> None:
        self._catalog = catalog
        self._service = service

    @classmethod
    def from_intake_root(
        cls,
        *,
        intake_root: str | Path,
    ) -> "GroundedPromptUiController":
        foundation = load_frozen_pilot_grounded_prompt_application_foundation(
            intake_root=intake_root
        )
        service = build_grounded_prompt_application_service(
            collection_id=foundation.collection_id,
            catalog=foundation.catalog,
            governed_knowledge=foundation.governed_knowledge,
            knowledge_mappings=foundation.knowledge_mappings,
            traceable_evidence_items=foundation.traceable_evidence_items,
            product_constraint_governed_knowledge=(
                foundation.product_constraint_governed_knowledge
            ),
            product_constraint_ingestion_manifest_records=(
                foundation.product_constraint_ingestion_manifest_records
            ),
            product_constraint_knowledge_mappings=(
                foundation.product_constraint_knowledge_mappings
            ),
        )
        return cls(catalog=foundation.catalog, service=service)

    @property
    def product_ids(self) -> tuple[str, ...]:
        return tuple(
            product.product_id
            for product in self._catalog.products
            if product.status == "active"
        )

    def variant_ids_for_product(self, product_id: str) -> tuple[str, ...]:
        product_id = _required_text(product_id, "product_id")
        if product_id not in self.product_ids:
            raise GroundedPromptUiContractError(
                f"unknown active product_id: {product_id}"
            )
        return tuple(
            variant.variant_id
            for variant in self._catalog.variants
            if variant.status == "active" and variant.product_id == product_id
        )

    def submit(
        self,
        *,
        product_id: str,
        variant_id: str,
        background: str,
        camera_angle: str,
        requested_output: str,
    ) -> GroundedPromptUiResult:
        product_id = _required_text(product_id, "product_id")
        variant_id = _required_text(variant_id, "variant_id")
        background = _required_text(background, "background")
        camera_angle = _required_text(camera_angle, "camera_angle")
        requested_output = _required_text(requested_output, "requested_output")

        allowed_variants = self.variant_ids_for_product(product_id)
        if variant_id not in allowed_variants:
            raise GroundedPromptUiContractError(
                "variant_id does not belong to requested product_id"
            )

        request = GroundedPromptApplicationRequest(
            product_id=product_id,
            variant_id=variant_id,
            creative_variables={
                "background": background,
                "camera_angle": camera_angle,
            },
            requested_output=requested_output,
        )
        orchestration = self._service.execute(request)
        compile_result = orchestration.compile_result

        return GroundedPromptUiResult(
            product_id=compile_result.product_id,
            variant_id=compile_result.variant_id,
            prompt_text=compile_result.prompt_text,
            bridge_materialization_status=(
                orchestration.bridge_result.prompt_inputs.materialization_status
            ),
            exact_six_materialization_status=(
                orchestration.exact_six_bridge_result.prompt_inputs.materialization_status
            ),
            binding_status=orchestration.binding_result.binding_status,
            grounding_status=compile_result.grounding_status,
        )
