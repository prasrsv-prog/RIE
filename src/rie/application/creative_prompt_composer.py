"""Framework-neutral PC3 Creative Brief and grounded prompt composition facade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rie.application.grounded_prompt_application_composition_root import (
    build_grounded_prompt_application_service,
)
from rie.application.grounded_prompt_application_foundation_provider import (
    load_frozen_pilot_grounded_prompt_application_foundation,
)
from rie.application.grounded_prompt_application_service import (
    GroundedPromptApplicationRequest,
    GroundedPromptApplicationService,
)
from rie.application.visual_reference_asset_query import VisualReferenceAssetQuery
from rie.rsv_knowledge.grounded_prompt_compiler import (
    GroundedPromptCompileResult,
)
from rie.rsv_knowledge.phase_b_grounded_prompt_orchestration import (
    PhaseBGroundedPromptOrchestrationResult,
)


class CreativePromptComposerContractError(ValueError):
    """Fail-closed contract error for PC3 creative prompt composition."""


@dataclass(frozen=True)
class CreativePromptBrief:
    objective: str = ""
    deliverable: str = ""
    environment: str = ""
    camera_angle: str = ""
    shot_type: str = ""
    lighting_style: str = ""
    composition: str = ""
    mood_style: str = ""
    aspect_ratio: str = ""
    orientation: str = ""
    product_emphasis: str = ""
    preserve_constraints: tuple[str, ...] = ()
    avoid_constraints: tuple[str, ...] = ()
    freeform_notes: str = ""
    selected_reference_asset_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class CreativePromptCompositionResult:
    prompt_text: str
    product_id: str
    variant_id: str
    requested_output: str
    grounding_status: str
    used_knowledge_ids: tuple[str, ...] = ()
    used_asset_ids: tuple[str, ...] = ()
    missing_knowledge: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    selected_reference_asset_ids: tuple[str, ...] = ()

    @property
    def is_grounded_success(self) -> bool:
        return (
            self.grounding_status == "PASSED"
            and bool(self.prompt_text.strip())
            and not self.missing_knowledge
            and not self.conflicts
        )


_REQUESTED_OUTPUT_SUGGESTIONS = (
    "grounded product prompt",
    "ecommerce hero prompt",
    "campaign visual prompt",
)

_REQUIRED_BRIEF_FIELDS = (
    "environment",
    "camera_angle",
    "deliverable",
)

_OPTIONAL_CREATIVE_FIELD_KEYS = (
    ("objective", "objective"),
    ("shot_type", "shot_type"),
    ("lighting_style", "lighting_style"),
    ("composition", "composition"),
    ("mood_style", "mood_style"),
    ("aspect_ratio", "aspect_ratio"),
    ("orientation", "orientation"),
    ("product_emphasis", "product_emphasis"),
    ("freeform_notes", "freeform_notes"),
)


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CreativePromptComposerContractError(
            f"{field_name} must be a nonempty string"
        )
    return value.strip()


def _optional_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise CreativePromptComposerContractError(
            f"{field_name} must be a string"
        )
    return value.strip()


def _normalized_instruction_tuple(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise CreativePromptComposerContractError(
            f"{field_name} must be a tuple of strings"
        )
    normalized: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise CreativePromptComposerContractError(
                f"{field_name}[{index}] must be a nonempty string"
            )
        normalized.append(item.strip())
    return tuple(normalized)


def _id_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise CreativePromptComposerContractError(
            f"{field_name} must be a tuple"
        )
    output: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise CreativePromptComposerContractError(
                f"{field_name}[{index}] must be a nonempty string"
            )
        output.append(item.strip())
    return tuple(output)


class CreativePromptComposer:
    """Validate a creative brief and delegate to the published grounded runtime."""

    def __init__(
        self,
        *,
        application_service: GroundedPromptApplicationService,
        visual_reference_asset_query: object | None = None,
    ) -> None:
        if not isinstance(
            application_service,
            GroundedPromptApplicationService,
        ):
            raise CreativePromptComposerContractError(
                "application_service must be GroundedPromptApplicationService"
            )
        if (
            visual_reference_asset_query is not None
            and not callable(
                getattr(visual_reference_asset_query, "list_assets", None)
            )
        ):
            raise CreativePromptComposerContractError(
                "visual_reference_asset_query must expose list_assets"
            )
        self._application_service = application_service
        self._visual_reference_asset_query = visual_reference_asset_query

    @classmethod
    def from_intake_root(
        cls,
        *,
        intake_root: str | Path,
        visual_reference_asset_query: object | None = None,
    ) -> "CreativePromptComposer":
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
        if visual_reference_asset_query is None:
            visual_reference_asset_query = (
                VisualReferenceAssetQuery.from_intake_root(
                    intake_root=intake_root
                )
            )
        return cls(
            application_service=service,
            visual_reference_asset_query=visual_reference_asset_query,
        )

    def available_requested_outputs(self) -> tuple[str, ...]:
        return _REQUESTED_OUTPUT_SUGGESTIONS

    def validate_creative_brief(
        self,
        brief: CreativePromptBrief,
    ) -> CreativePromptBrief:
        if not isinstance(brief, CreativePromptBrief):
            raise CreativePromptComposerContractError(
                "brief must be CreativePromptBrief"
            )

        values: dict[str, object] = {}
        for field_name in (
            "objective",
            "deliverable",
            "environment",
            "camera_angle",
            "shot_type",
            "lighting_style",
            "composition",
            "mood_style",
            "aspect_ratio",
            "orientation",
            "product_emphasis",
            "freeform_notes",
        ):
            raw_value = getattr(brief, field_name)
            if field_name in _REQUIRED_BRIEF_FIELDS:
                values[field_name] = _required_text(
                    raw_value,
                    field_name,
                )
            else:
                values[field_name] = _optional_text(
                    raw_value,
                    field_name,
                )

        values["preserve_constraints"] = _normalized_instruction_tuple(
            brief.preserve_constraints,
            "preserve_constraints",
        )
        values["avoid_constraints"] = _normalized_instruction_tuple(
            brief.avoid_constraints,
            "avoid_constraints",
        )
        selected_reference_asset_ids = _id_tuple(
            brief.selected_reference_asset_ids,
            "selected_reference_asset_ids",
        )
        if len(selected_reference_asset_ids) != len(
            set(selected_reference_asset_ids)
        ):
            raise CreativePromptComposerContractError(
                "selected_reference_asset_ids must not contain duplicates"
            )
        values["selected_reference_asset_ids"] = selected_reference_asset_ids
        return CreativePromptBrief(**values)

    def compose_grounded_prompt(
        self,
        *,
        product_id: str,
        variant_id: str,
        brief: CreativePromptBrief,
    ) -> CreativePromptCompositionResult:
        product_id = _required_text(product_id, "product_id")
        variant_id = _required_text(variant_id, "variant_id")
        brief = self.validate_creative_brief(brief)
        self._validate_selected_reference_assets(
            product_id=product_id,
            variant_id=variant_id,
            selected_reference_asset_ids=brief.selected_reference_asset_ids,
        )

        creative_variables = self._creative_variables(brief)
        request = GroundedPromptApplicationRequest(
            product_id=product_id,
            variant_id=variant_id,
            creative_variables=creative_variables,
            requested_output=brief.deliverable,
        )
        orchestration_result = self._application_service.execute(request)
        return self._normalize_result(
            orchestration_result,
            product_id=product_id,
            variant_id=variant_id,
            requested_output=brief.deliverable,
            selected_reference_asset_ids=brief.selected_reference_asset_ids,
        )

    def _validate_selected_reference_assets(
        self,
        *,
        product_id: str,
        variant_id: str,
        selected_reference_asset_ids: tuple[str, ...],
    ) -> None:
        if not selected_reference_asset_ids:
            return
        if self._visual_reference_asset_query is None:
            raise CreativePromptComposerContractError(
                "selected_reference_asset_ids require visual-reference authorization"
            )

        try:
            authorized_assets = tuple(
                self._visual_reference_asset_query.list_assets(
                    product_id=product_id,
                    variant_id=variant_id,
                )
            )
        except Exception as exc:
            raise CreativePromptComposerContractError(
                "visual-reference authorization query failed"
            ) from exc

        authorized_ids: set[str] = set()
        for asset in authorized_assets:
            asset_product_id = getattr(asset, "product_id", None)
            asset_variant_id = getattr(asset, "variant_id", None)
            asset_id = getattr(asset, "asset_id", None)
            available = getattr(asset, "available", False)

            if asset_product_id != product_id:
                raise CreativePromptComposerContractError(
                    "visual-reference authorization query returned cross-product asset"
                )
            if asset_variant_id not in (None, variant_id):
                raise CreativePromptComposerContractError(
                    "visual-reference authorization query returned cross-variant asset"
                )
            if (
                isinstance(asset_id, str)
                and asset_id.strip()
                and available is True
            ):
                authorized_ids.add(asset_id.strip())

        unauthorized = tuple(
            asset_id
            for asset_id in selected_reference_asset_ids
            if asset_id not in authorized_ids
        )
        if unauthorized:
            raise CreativePromptComposerContractError(
                "selected_reference_asset_ids are not authorized for "
                f"{product_id}/{variant_id}: "
                + ", ".join(unauthorized)
            )

    def _creative_variables(
        self,
        brief: CreativePromptBrief,
    ) -> dict[str, str]:
        creative: dict[str, str] = {
            "background": brief.environment,
            "camera_angle": brief.camera_angle,
        }
        for field_name, key in _OPTIONAL_CREATIVE_FIELD_KEYS:
            value = getattr(brief, field_name)
            if value:
                creative[key] = value
        if brief.preserve_constraints:
            creative["user_preserve_constraints"] = "; ".join(
                brief.preserve_constraints
            )
        if brief.avoid_constraints:
            creative["user_avoid_constraints"] = "; ".join(
                brief.avoid_constraints
            )
        return creative

    def _normalize_result(
        self,
        result: object,
        *,
        product_id: str,
        variant_id: str,
        requested_output: str,
        selected_reference_asset_ids: tuple[str, ...],
    ) -> CreativePromptCompositionResult:
        if not isinstance(result, PhaseBGroundedPromptOrchestrationResult):
            raise CreativePromptComposerContractError(
                "application service returned invalid orchestration result"
            )
        compile_result = result.compile_result
        if not isinstance(compile_result, GroundedPromptCompileResult):
            raise CreativePromptComposerContractError(
                "application service returned invalid compile result"
            )
        if compile_result.product_id != product_id:
            raise CreativePromptComposerContractError(
                "compile result product_id mismatch"
            )
        if compile_result.variant_id != variant_id:
            raise CreativePromptComposerContractError(
                "compile result variant_id mismatch"
            )
        if compile_result.grounding_status not in ("PASSED", "FAILED"):
            raise CreativePromptComposerContractError(
                "unsupported grounding_status: "
                + str(compile_result.grounding_status)
            )

        used_knowledge_ids = _id_tuple(
            compile_result.used_knowledge_ids,
            "used_knowledge_ids",
        )
        used_asset_ids = _id_tuple(
            compile_result.used_asset_ids,
            "used_asset_ids",
        )
        missing_knowledge = _id_tuple(
            compile_result.missing_knowledge,
            "missing_knowledge",
        )
        conflicts = _id_tuple(
            compile_result.conflicts,
            "conflicts",
        )

        prompt_text = compile_result.prompt_text
        if not isinstance(prompt_text, str):
            raise CreativePromptComposerContractError(
                "compile result prompt_text must be a string"
            )

        if compile_result.grounding_status == "PASSED":
            if not prompt_text.strip():
                raise CreativePromptComposerContractError(
                    "PASSED compile result must contain prompt_text"
                )
            if missing_knowledge or conflicts:
                raise CreativePromptComposerContractError(
                    "PASSED compile result must not contain missing knowledge or conflicts"
                )

        return CreativePromptCompositionResult(
            prompt_text=prompt_text,
            product_id=product_id,
            variant_id=variant_id,
            requested_output=requested_output,
            grounding_status=compile_result.grounding_status,
            used_knowledge_ids=used_knowledge_ids,
            used_asset_ids=used_asset_ids,
            selected_reference_asset_ids=selected_reference_asset_ids,
            missing_knowledge=missing_knowledge,
            conflicts=conflicts,
        )
