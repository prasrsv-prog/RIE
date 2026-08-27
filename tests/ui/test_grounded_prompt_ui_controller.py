from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest

from rie.rsv_knowledge.product_catalog import (
    ProductCatalog,
    ProductRecord,
    VariantRecord,
)
from rie.ui.grounded_prompt_ui_controller import (
    GroundedPromptUiContractError,
    GroundedPromptUiController,
)


INTAKE_ROOT = Path(
    r"C:\Users\Kreatif Kris\Downloads\RCIS-RSV-Real-Asset-Pilot-01-Intake"
)


def _catalog() -> ProductCatalog:
    return ProductCatalog(
        products=(
            ProductRecord("alpha", "Alpha", "RSV", "active"),
            ProductRecord("beta", "Beta", "RSV", "active"),
        ),
        variants=(
            VariantRecord("alpha-a", "alpha", "Alpha A", "active"),
            VariantRecord("alpha-b", "alpha", "Alpha B", "active"),
            VariantRecord("beta-a", "beta", "Beta A", "active"),
        ),
    )


def _passed_orchestration(
    *,
    product_id: str = "alpha",
    variant_id: str = "alpha-a",
    prompt_text: str = "compiled prompt",
):
    return SimpleNamespace(
        bridge_result=SimpleNamespace(
            prompt_inputs=SimpleNamespace(materialization_status="PASSED")
        ),
        exact_six_bridge_result=SimpleNamespace(
            prompt_inputs=SimpleNamespace(materialization_status="PASSED")
        ),
        binding_result=SimpleNamespace(binding_status="PASSED"),
        compile_result=SimpleNamespace(
            product_id=product_id,
            variant_id=variant_id,
            prompt_text=prompt_text,
            grounding_status="PASSED",
        ),
    )


class _FakeService:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or _passed_orchestration()

    def execute(self, request):
        self.calls.append(request)
        return self.result


def test_from_intake_root_loads_exact_three_products_and_eighteen_variants() -> None:
    controller = GroundedPromptUiController.from_intake_root(
        intake_root=INTAKE_ROOT
    )

    assert len(controller.product_ids) == 3
    assert sum(
        len(controller.variant_ids_for_product(product_id))
        for product_id in controller.product_ids
    ) == 18


def test_product_ids_are_deterministic_and_controller_has_no_selected_product() -> None:
    controller = GroundedPromptUiController(
        catalog=_catalog(),
        service=_FakeService(),
    )

    assert controller.product_ids == ("alpha", "beta")
    assert not hasattr(controller, "selected_product_id")
    assert not hasattr(controller, "selected_variant_id")


def test_variant_ids_are_filtered_by_explicit_product_and_no_variant_is_auto_selected() -> None:
    controller = GroundedPromptUiController(
        catalog=_catalog(),
        service=_FakeService(),
    )

    assert controller.variant_ids_for_product("alpha") == (
        "alpha-a",
        "alpha-b",
    )
    assert controller.variant_ids_for_product("beta") == ("beta-a",)
    assert not hasattr(controller, "selected_variant_id")


def test_submit_known_explicit_request_returns_passed_statuses_and_prompt_text() -> None:
    controller = GroundedPromptUiController.from_intake_root(
        intake_root=INTAKE_ROOT
    )

    result = controller.submit(
        product_id="sv300",
        variant_id="sv300-white-glossy",
        background="dark studio",
        camera_angle="front",
        requested_output="grounded product prompt",
    )

    assert result.product_id == "sv300"
    assert result.variant_id == "sv300-white-glossy"
    assert result.prompt_text
    assert result.bridge_materialization_status == "PASSED"
    assert result.exact_six_materialization_status == "PASSED"
    assert result.binding_status == "PASSED"
    assert result.grounding_status == "PASSED"


def test_submit_preserves_exact_operator_request_values() -> None:
    service = _FakeService()
    controller = GroundedPromptUiController(
        catalog=_catalog(),
        service=service,
    )

    controller.submit(
        product_id="alpha",
        variant_id="alpha-a",
        background="dark studio",
        camera_angle="front",
        requested_output="grounded product prompt",
    )

    request = service.calls[0]
    assert request.product_id == "alpha"
    assert request.variant_id == "alpha-a"
    assert request.creative_variables == {
        "background": "dark studio",
        "camera_angle": "front",
    }
    assert request.requested_output == "grounded product prompt"


def test_submit_blank_required_field_fails_before_service_execution() -> None:
    service = _FakeService()
    controller = GroundedPromptUiController(
        catalog=_catalog(),
        service=service,
    )

    with pytest.raises(GroundedPromptUiContractError, match="background"):
        controller.submit(
            product_id="alpha",
            variant_id="alpha-a",
            background="   ",
            camera_angle="front",
            requested_output="grounded product prompt",
        )

    assert service.calls == []


def test_submit_cross_product_variant_fails_before_service_execution() -> None:
    service = _FakeService()
    controller = GroundedPromptUiController(
        catalog=_catalog(),
        service=service,
    )

    with pytest.raises(
        GroundedPromptUiContractError,
        match="does not belong",
    ):
        controller.submit(
            product_id="beta",
            variant_id="alpha-a",
            background="dark studio",
            camera_angle="front",
            requested_output="grounded product prompt",
        )

    assert service.calls == []


def test_controller_has_no_tkinter_or_direct_frozen_database_dependency() -> None:
    source = inspect.getsource(
        __import__(
            "rie.ui.grounded_prompt_ui_controller",
            fromlist=["GroundedPromptUiController"],
        )
    )

    assert "tkinter" not in source
    assert "sqlite" not in source.lower()
    assert "rie.rsv_knowledge" not in source
    assert "evidence_repository" not in source
    assert "knowledge_repository" not in source
