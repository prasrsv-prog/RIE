from __future__ import annotations

import inspect
import tkinter as tk

import pytest

from rie.ui.grounded_prompt_ui_controller import (
    GroundedPromptUiContractError,
    GroundedPromptUiResult,
)
from rie.ui.tkinter_grounded_prompt_app import GroundedPromptTkApplication


class _FakeController:
    def __init__(self):
        self.product_ids = ("alpha", "beta")
        self.submit_calls = []

    def variant_ids_for_product(self, product_id):
        if product_id == "alpha":
            return ("alpha-a", "alpha-b")
        if product_id == "beta":
            return ("beta-a",)
        raise GroundedPromptUiContractError("unknown active product_id")

    def submit(
        self,
        *,
        product_id,
        variant_id,
        background,
        camera_angle,
        requested_output,
    ):
        if not product_id:
            raise GroundedPromptUiContractError("product_id must not be empty")
        if not variant_id:
            raise GroundedPromptUiContractError("variant_id must not be empty")
        if not background.strip():
            raise GroundedPromptUiContractError("background must not be empty")
        if not camera_angle.strip():
            raise GroundedPromptUiContractError("camera_angle must not be empty")
        if not requested_output.strip():
            raise GroundedPromptUiContractError(
                "requested_output must not be empty"
            )
        self.submit_calls.append(
            {
                "product_id": product_id,
                "variant_id": variant_id,
                "background": background,
                "camera_angle": camera_angle,
                "requested_output": requested_output,
            }
        )
        return GroundedPromptUiResult(
            product_id=product_id,
            variant_id=variant_id,
            prompt_text="compiled grounded prompt",
            bridge_materialization_status="PASSED",
            exact_six_materialization_status="PASSED",
            binding_status="PASSED",
            grounding_status="PASSED",
        )


@pytest.fixture(scope="session")
def _tk_session_root():
    value = tk.Tk()
    value.withdraw()
    value.update_idletasks()
    yield value
    value.destroy()


@pytest.fixture
def root(_tk_session_root):
    value = tk.Toplevel(_tk_session_root)
    value.withdraw()
    value.update_idletasks()
    yield value
    value.destroy()


def _app(root, *, directory_picker=lambda: ""):
    controller = _FakeController()
    calls = []

    def factory(*, intake_root):
        calls.append(intake_root)
        return controller

    app = GroundedPromptTkApplication(
        root,
        controller_factory=factory,
        directory_picker=directory_picker,
    )
    root.update_idletasks()
    return app, controller, calls


def test_app_initial_state_has_empty_intake_product_and_variant_controls(root) -> None:
    app, _, _ = _app(root)

    assert app.intake_root_var.get() == ""
    assert app.product_var.get() == ""
    assert app.variant_var.get() == ""
    assert tuple(app.product_combo["values"]) == ()
    assert tuple(app.variant_combo["values"]) == ()


def test_load_foundation_uses_exact_visible_intake_root_and_populates_products_without_auto_selection(root) -> None:
    app, _, calls = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")

    app.load_foundation()

    assert calls == [r"C:\pilot\intake"]
    assert tuple(app.product_combo["values"]) == ("alpha", "beta")
    assert app.product_var.get() == ""
    assert app.variant_var.get() == ""


def test_product_selection_populates_variants_and_keeps_variant_unselected(root) -> None:
    app, _, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")

    app.refresh_variants()

    assert tuple(app.variant_combo["values"]) == ("alpha-a", "alpha-b")
    assert app.variant_var.get() == ""


def test_submit_validation_requires_explicit_product_variant_and_text_inputs(root) -> None:
    app, controller, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()

    app.submit()

    assert "product_id" in app.error_var.get()
    assert controller.submit_calls == []


def test_submit_passes_exact_visible_values_to_controller(root) -> None:
    app, controller, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "grounded product prompt")

    app.submit()

    assert controller.submit_calls == [
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "dark studio",
            "camera_angle": "front",
            "requested_output": "grounded product prompt",
        }
    ]


def test_success_renders_four_statuses_and_read_only_prompt_text(root) -> None:
    app, _, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "grounded product prompt")

    app.submit()

    assert app.bridge_status_var.get() == "PASSED"
    assert app.exact_six_status_var.get() == "PASSED"
    assert app.binding_status_var.get() == "PASSED"
    assert app.grounding_status_var.get() == "PASSED"
    assert app.prompt_output.get("1.0", "end-1c") == "compiled grounded prompt"
    assert str(app.prompt_output.cget("state")) == "disabled"


def test_failure_renders_error_without_clearing_operator_inputs(root) -> None:
    app, _, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "   ")

    app.submit()

    assert "requested_output" in app.error_var.get()
    assert app.product_var.get() == "alpha"
    assert app.variant_var.get() == "alpha-a"
    assert app.background_var.get() == "dark studio"
    assert app.camera_angle_var.get() == "front"
    assert app.requested_output_text.get("1.0", "end-1c") == "   "



def test_browse_intake_root_sets_exact_selected_directory_without_loading_foundation(root) -> None:
    selected_directory = "C:/Pilot Root/Selected Intake"
    app, _, calls = _app(root, directory_picker=lambda: selected_directory)

    app.browse_intake_root()

    assert app.intake_root_var.get() == selected_directory
    assert calls == []
    assert tuple(app.product_combo["values"]) == ()
    assert tuple(app.variant_combo["values"]) == ()


def test_browse_intake_root_cancel_preserves_existing_visible_value(root) -> None:
    app, _, calls = _app(root, directory_picker=lambda: "")
    app.intake_root_var.set(r"C:\pilot\existing-intake")

    app.browse_intake_root()

    assert app.intake_root_var.get() == r"C:\pilot\existing-intake"
    assert calls == []


def test_browse_intake_root_does_not_auto_select_product_or_variant(root) -> None:
    selected_directory = r"C:\pilot\browsed-intake"
    app, _, calls = _app(root, directory_picker=lambda: selected_directory)

    app.browse_intake_root()

    assert app.intake_root_var.get() == selected_directory
    assert app.product_var.get() == ""
    assert app.variant_var.get() == ""
    assert calls == []


def test_tkinter_module_does_not_import_frozen_runtime_database_or_construct_phase_e_service_directly() -> None:
    source = inspect.getsource(
        __import__(
            "rie.ui.tkinter_grounded_prompt_app",
            fromlist=["GroundedPromptTkApplication"],
        )
    )

    assert "sqlite" not in source.lower()
    assert "rie.rsv_knowledge" not in source
    assert "evidence_repository" not in source
    assert "knowledge_repository" not in source
    assert "grounded_prompt_application_service" not in source
    assert "grounded_prompt_application_composition_root" not in source
    assert "grounded_prompt_application_foundation_provider" not in source
