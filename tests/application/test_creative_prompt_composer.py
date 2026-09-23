from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

import rie.application.creative_prompt_composer as composer_module
from rie.application.creative_prompt_composer import (
    CreativePromptBrief,
    CreativePromptComposer,
    CreativePromptComposerContractError,
)
from rie.application.grounded_prompt_application_service import (
    GroundedPromptApplicationService,
)
from rie.rsv_knowledge.grounded_prompt_compiler import (
    GroundedPromptCompileResult,
)
from rie.rsv_knowledge.phase_b_grounded_prompt_orchestration import (
    PhaseBGroundedPromptOrchestrationResult,
)


def _orchestration_result(
    *,
    product_id: str = "sv300",
    variant_id: str = "sv300-white-glossy",
    prompt_text: str = "compiled grounded prompt",
    grounding_status: str = "PASSED",
    used_asset_ids: tuple[str, ...] = ("asset-identity", "asset-manual"),
    missing_knowledge: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
) -> PhaseBGroundedPromptOrchestrationResult:
    return PhaseBGroundedPromptOrchestrationResult(
        bridge_result=object(),
        exact_six_bridge_result=object(),
        binding_result=object(),
        compile_result=GroundedPromptCompileResult(
            prompt_text=prompt_text,
            product_id=product_id,
            variant_id=variant_id,
            used_knowledge_ids=("knowledge-identity", "knowledge-manual"),
            used_asset_ids=used_asset_ids,
            missing_knowledge=missing_knowledge,
            conflicts=conflicts,
            grounding_status=grounding_status,
        ),
    )


def _service(calls: list[dict[str, object]], *, result=None):
    def orchestrator(
        *,
        product_id,
        variant_id,
        creative_variables,
        requested_output,
    ):
        calls.append(
            {
                "product_id": product_id,
                "variant_id": variant_id,
                "creative_variables": dict(creative_variables),
                "requested_output": requested_output,
            }
        )
        return result or _orchestration_result(
            product_id=product_id,
            variant_id=variant_id,
        )

    return GroundedPromptApplicationService(
        orchestrator=orchestrator,
        foundation_dependencies={},
    )


class _FakeVisualReferenceAssetQuery:
    def __init__(
        self,
        *,
        authorized_asset_ids: tuple[str, ...] = ("asset-photo-a", "asset-photo-b"),
    ) -> None:
        self.authorized_asset_ids = authorized_asset_ids
        self.calls: list[tuple[str, str]] = []

    def list_assets(self, *, product_id: str, variant_id: str):
        self.calls.append((product_id, variant_id))
        return tuple(
            type(
                "Asset",
                (),
                {
                    "asset_id": asset_id,
                    "product_id": product_id,
                    "variant_id": variant_id,
                    "available": True,
                },
            )()
            for asset_id in self.authorized_asset_ids
        )


def _brief(**overrides) -> CreativePromptBrief:
    values = {
        "objective": "ecommerce hero",
        "deliverable": "grounded product prompt",
        "environment": "dark studio",
        "camera_angle": "front three-quarter",
        "shot_type": "medium product shot",
        "lighting_style": "soft directional",
        "composition": "centered with negative space",
        "mood_style": "premium technical",
        "aspect_ratio": "4:5",
        "orientation": "portrait",
        "product_emphasis": "helmet dominant",
        "preserve_constraints": ("keep visor clear", "preserve logo placement"),
        "avoid_constraints": ("no floating product",),
        "selected_reference_asset_ids": (),
        "freeform_notes": "natural floor contact",
    }
    values.update(overrides)
    return CreativePromptBrief(**values)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("environment", "   "),
        ("camera_angle", ""),
        ("deliverable", "  "),
    ),
)
def test_required_brief_fields_fail_before_service_execution(
    field_name,
    value,
) -> None:
    calls = []
    composer = CreativePromptComposer(application_service=_service(calls))
    with pytest.raises(
        CreativePromptComposerContractError,
        match=field_name,
    ):
        composer.compose_grounded_prompt(
            product_id="sv300",
            variant_id="sv300-white-glossy",
            brief=_brief(**{field_name: value}),
        )
    assert calls == []


@pytest.mark.parametrize(
    ("field_name", "value"),
    (("product_id", ""), ("variant_id", "   ")),
)
def test_product_and_variant_fail_before_service_execution(
    field_name,
    value,
) -> None:
    calls = []
    composer = CreativePromptComposer(application_service=_service(calls))
    kwargs = {
        "product_id": "sv300",
        "variant_id": "sv300-white-glossy",
        "brief": _brief(),
    }
    kwargs[field_name] = value
    with pytest.raises(
        CreativePromptComposerContractError,
        match=field_name,
    ):
        composer.compose_grounded_prompt(**kwargs)
    assert calls == []


def test_rich_brief_maps_to_creative_only_variables_deterministically() -> None:
    calls = []
    composer = CreativePromptComposer(application_service=_service(calls))
    result = composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=_brief(),
    )

    assert result.is_grounded_success
    assert len(calls) == 1
    assert calls[0] == {
        "product_id": "sv300",
        "variant_id": "sv300-white-glossy",
        "creative_variables": {
            "background": "dark studio",
            "camera_angle": "front three-quarter",
            "objective": "ecommerce hero",
            "shot_type": "medium product shot",
            "lighting_style": "soft directional",
            "composition": "centered with negative space",
            "mood_style": "premium technical",
            "aspect_ratio": "4:5",
            "orientation": "portrait",
            "product_emphasis": "helmet dominant",
            "freeform_notes": "natural floor contact",
            "user_preserve_constraints": (
                "keep visor clear; preserve logo placement"
            ),
            "user_avoid_constraints": "no floating product",
        },
        "requested_output": "grounded product prompt",
    }


def test_blank_optional_fields_are_omitted_from_creative_variables() -> None:
    calls = []
    composer = CreativePromptComposer(application_service=_service(calls))
    composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=_brief(
            objective="  ",
            shot_type="",
            lighting_style=" ",
            composition="",
            mood_style="",
            aspect_ratio="",
            orientation="",
            product_emphasis="",
            preserve_constraints=(),
            avoid_constraints=(),
            freeform_notes="",
        ),
    )
    assert calls[0]["creative_variables"] == {
        "background": "dark studio",
        "camera_angle": "front three-quarter",
    }


def test_user_preserve_and_avoid_remain_distinct_from_canonical_constraints() -> None:
    calls = []
    composer = CreativePromptComposer(application_service=_service(calls))
    composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=_brief(),
    )
    variables = calls[0]["creative_variables"]
    assert "user_preserve_constraints" in variables
    assert "user_avoid_constraints" in variables
    assert "preservation_constraints" not in variables
    assert "product_variant_identity" not in variables
    assert "chinstrap_retention_system" not in variables
    assert "helmet_body_material" not in variables


def test_available_requested_outputs_are_suggestions_not_restrictions() -> None:
    calls = []
    composer = CreativePromptComposer(application_service=_service(calls))
    assert composer.available_requested_outputs() == (
        "grounded product prompt",
        "ecommerce hero prompt",
        "campaign visual prompt",
    )
    composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=_brief(deliverable="custom storyboard frame prompt"),
    )
    assert calls[0]["requested_output"] == "custom storyboard frame prompt"


def test_normalizes_compile_result_without_promoting_generated_output() -> None:
    calls = []
    visual_query = _FakeVisualReferenceAssetQuery(
        authorized_asset_ids=("asset-reference-1",)
    )
    composer = CreativePromptComposer(
        application_service=_service(calls),
        visual_reference_asset_query=visual_query,
    )
    result = composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=_brief(selected_reference_asset_ids=("asset-reference-1",)),
    )
    assert result.prompt_text == "compiled grounded prompt"
    assert result.grounding_status == "PASSED"
    assert result.used_knowledge_ids == (
        "knowledge-identity",
        "knowledge-manual",
    )
    assert result.used_asset_ids == ("asset-identity", "asset-manual")
    assert result.selected_reference_asset_ids == ("asset-reference-1",)
    assert result.missing_knowledge == ()
    assert result.conflicts == ()
    assert not hasattr(result, "official_product_truth")


def test_passed_result_preserves_empty_used_asset_ids_without_fabrication() -> None:
    calls = []
    knowledge_backed = _orchestration_result(
        used_asset_ids=(),
    )
    composer = CreativePromptComposer(
        application_service=_service(calls, result=knowledge_backed)
    )
    result = composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=_brief(),
    )

    assert result.is_grounded_success
    assert result.grounding_status == "PASSED"
    assert result.prompt_text
    assert result.used_knowledge_ids == (
        "knowledge-identity",
        "knowledge-manual",
    )
    assert result.used_asset_ids == ()
    assert result.missing_knowledge == ()
    assert result.conflicts == ()


def test_valid_failed_grounding_result_is_returned_as_not_successful() -> None:
    calls = []
    failed = _orchestration_result(
        prompt_text="",
        grounding_status="FAILED",
        conflicts=("creative_override:helmet_body_material",),
    )
    composer = CreativePromptComposer(
        application_service=_service(calls, result=failed)
    )
    result = composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=_brief(),
    )
    assert result.grounding_status == "FAILED"
    assert result.conflicts == ("creative_override:helmet_body_material",)
    assert not result.is_grounded_success


def test_selected_reference_assets_are_preserved_but_not_sent_as_creative_variables() -> None:
    calls = []
    visual_query = _FakeVisualReferenceAssetQuery()
    composer = CreativePromptComposer(
        application_service=_service(calls),
        visual_reference_asset_query=visual_query,
    )
    result = composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=_brief(
            selected_reference_asset_ids=("asset-photo-a", "asset-photo-b")
        ),
    )

    assert result.selected_reference_asset_ids == (
        "asset-photo-a",
        "asset-photo-b",
    )
    assert "selected_reference_asset_ids" not in calls[0]["creative_variables"]
    assert result.used_asset_ids == ("asset-identity", "asset-manual")
    assert visual_query.calls == [("sv300", "sv300-white-glossy")]


def test_selected_reference_assets_require_application_authorization_query() -> None:
    calls = []
    composer = CreativePromptComposer(application_service=_service(calls))
    with pytest.raises(
        CreativePromptComposerContractError,
        match="require visual-reference authorization",
    ):
        composer.compose_grounded_prompt(
            product_id="sv300",
            variant_id="sv300-white-glossy",
            brief=_brief(selected_reference_asset_ids=("asset-photo-a",)),
        )
    assert calls == []


def test_unauthorized_selected_reference_asset_fails_before_service_execution() -> None:
    calls = []
    visual_query = _FakeVisualReferenceAssetQuery(
        authorized_asset_ids=("asset-photo-a",)
    )
    composer = CreativePromptComposer(
        application_service=_service(calls),
        visual_reference_asset_query=visual_query,
    )
    with pytest.raises(
        CreativePromptComposerContractError,
        match="not authorized",
    ):
        composer.compose_grounded_prompt(
            product_id="sv300",
            variant_id="sv300-white-glossy",
            brief=_brief(selected_reference_asset_ids=("asset-other-product",)),
        )
    assert visual_query.calls == [("sv300", "sv300-white-glossy")]
    assert calls == []


def test_duplicate_selected_reference_asset_ids_fail_before_service_execution() -> None:
    calls = []
    composer = CreativePromptComposer(application_service=_service(calls))
    with pytest.raises(
        CreativePromptComposerContractError,
        match="must not contain duplicates",
    ):
        composer.compose_grounded_prompt(
            product_id="sv300",
            variant_id="sv300-white-glossy",
            brief=_brief(
                selected_reference_asset_ids=("asset-photo-a", "asset-photo-a")
            ),
        )
    assert calls == []


def test_invalid_service_result_fails_closed() -> None:
    def orchestrator(
        *, product_id, variant_id, creative_variables, requested_output
    ):
        return object()

    service = GroundedPromptApplicationService(
        orchestrator=orchestrator,
        foundation_dependencies={},
    )
    composer = CreativePromptComposer(application_service=service)
    with pytest.raises(
        CreativePromptComposerContractError,
        match="invalid orchestration result",
    ):
        composer.compose_grounded_prompt(
            product_id="sv300",
            variant_id="sv300-white-glossy",
            brief=_brief(),
        )


def test_from_intake_root_reuses_published_provider_and_composition_root(
    monkeypatch,
) -> None:
    foundation = type(
        "Foundation",
        (),
        {
            "collection_id": "collection-1",
            "catalog": object(),
            "governed_knowledge": (object(),),
            "knowledge_mappings": (object(),),
            "traceable_evidence_items": (object(),),
            "product_constraint_governed_knowledge": (object(),),
            "product_constraint_ingestion_manifest_records": (object(),),
            "product_constraint_knowledge_mappings": (object(),),
        },
    )()
    service = _service([])
    load_calls = []
    build_calls = []
    visual_query = _FakeVisualReferenceAssetQuery()
    visual_query_build_calls = []

    def fake_visual_query_from_intake_root(*, intake_root):
        visual_query_build_calls.append(Path(intake_root))
        return visual_query


    def fake_load(*, intake_root):
        load_calls.append(Path(intake_root))
        return foundation

    def fake_build(**kwargs):
        build_calls.append(kwargs)
        return service

    monkeypatch.setattr(
        composer_module,
        "load_frozen_pilot_grounded_prompt_application_foundation",
        fake_load,
    )
    monkeypatch.setattr(
        composer_module,
        "build_grounded_prompt_application_service",
        fake_build,
    )
    monkeypatch.setattr(
        composer_module.VisualReferenceAssetQuery,
        "from_intake_root",
        fake_visual_query_from_intake_root,
    )

    composer = CreativePromptComposer.from_intake_root(
        intake_root="C:/pilot-intake"
    )
    assert isinstance(composer, CreativePromptComposer)
    assert load_calls == [Path("C:/pilot-intake")]
    assert visual_query_build_calls == [Path("C:/pilot-intake")]
    assert composer._visual_reference_asset_query is visual_query
    assert build_calls == [
        {
            "collection_id": foundation.collection_id,
            "catalog": foundation.catalog,
            "governed_knowledge": foundation.governed_knowledge,
            "knowledge_mappings": foundation.knowledge_mappings,
            "traceable_evidence_items": foundation.traceable_evidence_items,
            "product_constraint_governed_knowledge": (
                foundation.product_constraint_governed_knowledge
            ),
            "product_constraint_ingestion_manifest_records": (
                foundation.product_constraint_ingestion_manifest_records
            ),
            "product_constraint_knowledge_mappings": (
                foundation.product_constraint_knowledge_mappings
            ),
        }
    ]


def test_from_intake_root_accepts_composition_supplied_visual_query(
    monkeypatch,
) -> None:
    foundation = type(
        "Foundation",
        (),
        {
            "collection_id": "collection-1",
            "catalog": object(),
            "governed_knowledge": (object(),),
            "knowledge_mappings": (object(),),
            "traceable_evidence_items": (object(),),
            "product_constraint_governed_knowledge": (object(),),
            "product_constraint_ingestion_manifest_records": (object(),),
            "product_constraint_knowledge_mappings": (object(),),
        },
    )()
    service = _service([])
    visual_query = _FakeVisualReferenceAssetQuery()

    monkeypatch.setattr(
        composer_module,
        "load_frozen_pilot_grounded_prompt_application_foundation",
        lambda *, intake_root: foundation,
    )
    monkeypatch.setattr(
        composer_module,
        "build_grounded_prompt_application_service",
        lambda **kwargs: service,
    )

    def fail_visual_query_build(*, intake_root):
        raise AssertionError("supplied visual-reference query must be reused")

    monkeypatch.setattr(
        composer_module.VisualReferenceAssetQuery,
        "from_intake_root",
        fail_visual_query_build,
    )

    composer = CreativePromptComposer.from_intake_root(
        intake_root="C:/pilot-intake",
        visual_reference_asset_query=visual_query,
    )
    assert composer._visual_reference_asset_query is visual_query


def test_composer_source_is_framework_neutral_and_has_no_direct_storage_imports() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "application"
        / "creative_prompt_composer.py"
    )
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    assert not any(name == "rie.ui" or name.startswith("rie.ui.") for name in imports)
    assert not any(name == "PySide6" or name.startswith("PySide6.") for name in imports)
    assert "tkinter" not in imports

    lowered = source.lower()
    for forbidden in (
        "evidence_repository",
        "knowledge_repository",
        "governed_asset_library_registry",
        "sqlite3",
        "database_connection",
    ):
        assert forbidden not in lowered


def test_real_frozen_foundation_composes_rich_brief_deterministically() -> None:
    raw_root = os.environ.get("RCIS_TEST_INTAKE_ROOT")
    intake_root = (
        Path(raw_root)
        if raw_root
        else Path.home()
        / "Downloads"
        / "RCIS-RSV-Real-Asset-Pilot-01-Intake"
    )
    assert intake_root.is_dir(), (
        "real frozen pilot intake root is required for PR-118B proof: "
        + str(intake_root)
    )

    composer = CreativePromptComposer.from_intake_root(
        intake_root=intake_root
    )
    brief = _brief(
        preserve_constraints=("keep visor visually clear",),
        avoid_constraints=("no floating product",),
    )
    first = composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=brief,
    )
    second = composer.compose_grounded_prompt(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        brief=brief,
    )

    assert first == second
    assert first.is_grounded_success
    assert first.grounding_status == "PASSED"
    assert first.prompt_text
    assert first.used_knowledge_ids
    assert first.used_asset_ids == ()
    assert first.missing_knowledge == ()
    assert first.conflicts == ()
    assert "PRODUCT LOCKS:" in first.prompt_text
    assert "CREATIVE VARIABLES:" in first.prompt_text
    assert "user_preserve_constraints" in first.prompt_text
    assert "user_avoid_constraints" in first.prompt_text
