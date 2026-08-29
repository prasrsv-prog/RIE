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


def _app(
    root,
    *,
    directory_picker=lambda: "",
    settings_loader=lambda: None,
    settings_saver=lambda _intake_root: None,
):
    controller = _FakeController()
    calls = []

    def factory(*, intake_root):
        calls.append(intake_root)
        return controller

    app = GroundedPromptTkApplication(
        root,
        controller_factory=factory,
        directory_picker=directory_picker,
        settings_loader=settings_loader,
        settings_saver=settings_saver,
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



def test_browse_intake_root_sets_selected_directory_and_loads_foundation(root) -> None:
    selected_directory = "C:/Pilot Root/Selected Intake"
    app, _, calls = _app(root, directory_picker=lambda: selected_directory)

    app.browse_intake_root()

    assert app.intake_root_var.get() == selected_directory
    assert calls == [selected_directory]
    assert tuple(app.product_combo["values"]) == ("alpha", "beta")
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
    assert calls == [selected_directory]


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

def _prime_success_for_invalidation(root):
    app, controller, calls = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "grounded product prompt")
    app.submit()
    root.update()
    assert app.bridge_status_var.get() == "PASSED"
    assert app.exact_six_status_var.get() == "PASSED"
    assert app.binding_status_var.get() == "PASSED"
    assert app.grounding_status_var.get() == "PASSED"
    assert app.prompt_output.get("1.0", "end-1c") == "compiled grounded prompt"
    return app, controller, calls


def _assert_rendered_success_is_clear(app) -> None:
    assert app.bridge_status_var.get() == ""
    assert app.exact_six_status_var.get() == ""
    assert app.binding_status_var.get() == ""
    assert app.grounding_status_var.get() == ""
    assert app.prompt_output.get("1.0", "end-1c") == ""


def test_background_change_after_success_clears_rendered_success_without_submit(root) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    app.background_var.set("bright studio")
    _assert_rendered_success_is_clear(app)
    assert app.background_var.get() == "bright studio"
    assert len(controller.submit_calls) == 1
    assert calls == [r"C:\pilot\intake"]


def test_camera_angle_change_after_success_clears_rendered_success_without_submit(root) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    app.camera_angle_var.set("three-quarter")
    _assert_rendered_success_is_clear(app)
    assert app.camera_angle_var.get() == "three-quarter"
    assert len(controller.submit_calls) == 1
    assert calls == [r"C:\pilot\intake"]


def test_requested_output_change_after_success_clears_rendered_success_without_submit(root) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    app.requested_output_text.delete("1.0", "end")
    app.requested_output_text.insert("1.0", "revised grounded product prompt")
    root.update()
    _assert_rendered_success_is_clear(app)
    assert app.requested_output_text.get("1.0", "end-1c") == "revised grounded product prompt"
    assert len(controller.submit_calls) == 1
    assert calls == [r"C:\pilot\intake"]


def test_product_change_after_success_clears_rendered_success_and_keeps_variant_clear_behavior(root) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    app.product_var.set("beta")
    app.refresh_variants()
    _assert_rendered_success_is_clear(app)
    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == ""
    assert tuple(app.variant_combo["values"]) == ("beta-a",)
    assert len(controller.submit_calls) == 1
    assert calls == [r"C:\pilot\intake"]


def test_variant_change_after_success_clears_rendered_success_without_submit(root) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    app.variant_var.set("alpha-b")
    _assert_rendered_success_is_clear(app)
    assert app.variant_var.get() == "alpha-b"
    assert len(controller.submit_calls) == 1
    assert calls == [r"C:\pilot\intake"]


def test_intake_root_change_after_success_clears_rendered_success_without_auto_load(root) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    app.intake_root_var.set(r"C:\pilot\other-intake")
    _assert_rendered_success_is_clear(app)
    assert app.intake_root_var.get() == r"C:\pilot\other-intake"
    assert app._controller is controller
    assert len(controller.submit_calls) == 1
    assert calls == [r"C:\pilot\intake"]

def test_phase_h_no_remembered_setting_leaves_manual_first_run_mode(root) -> None:
    app, _, calls = _app(root, settings_loader=lambda: None)
    assert calls == []
    assert app.intake_root_var.get() == ""
    assert app._controller is None
    assert tuple(app.product_combo["values"]) == ()


def test_phase_h_valid_remembered_setting_auto_loads_foundation_at_startup(root) -> None:
    remembered = r"C:\pilot\remembered-intake"
    app, _, calls = _app(
        root,
        settings_loader=lambda: remembered,
    )
    assert calls == [remembered]
    assert app.intake_root_var.get() == remembered
    assert app._controller is not None
    assert tuple(app.product_combo["values"]) == ("alpha", "beta")
    assert app.product_var.get() == ""
    assert app.variant_var.get() == ""


def test_phase_h_rejected_remembered_setting_falls_back_without_crashing(root) -> None:
    remembered = r"C:\pilot\rejected-intake"
    calls = []

    def factory(*, intake_root):
        calls.append(intake_root)
        raise GroundedPromptUiContractError("remembered intake rejected")

    app = GroundedPromptTkApplication(
        root,
        controller_factory=factory,
        directory_picker=lambda: "",
        settings_loader=lambda: remembered,
        settings_saver=lambda _value: None,
    )
    root.update_idletasks()

    assert calls == [remembered]
    assert app.intake_root_var.get() == remembered
    assert app._controller is None
    assert tuple(app.product_combo["values"]) == ()
    assert "remembered intake rejected" in app.error_var.get()


def test_phase_h_browse_attempts_load_and_persists_only_on_success(root) -> None:
    selected = r"C:\pilot\browsed-and-remembered"
    saved = []
    app, _, calls = _app(
        root,
        directory_picker=lambda: selected,
        settings_saver=saved.append,
    )

    app.browse_intake_root()

    assert calls == [selected]
    assert saved == [selected]
    assert app.intake_root_var.get() == selected
    assert app._controller is not None
    assert tuple(app.product_combo["values"]) == ("alpha", "beta")


def test_phase_h_failed_manual_load_does_not_replace_last_known_good_setting(root) -> None:
    good = r"C:\pilot\good-intake"
    bad = r"C:\pilot\bad-intake"
    controller = _FakeController()
    saved = []
    calls = []

    def factory(*, intake_root):
        calls.append(intake_root)
        if intake_root == bad:
            raise GroundedPromptUiContractError("bad intake")
        return controller

    app = GroundedPromptTkApplication(
        root,
        controller_factory=factory,
        directory_picker=lambda: "",
        settings_loader=lambda: None,
        settings_saver=saved.append,
    )
    root.update_idletasks()

    app.intake_root_var.set(good)
    app.load_foundation()
    app.intake_root_var.set(bad)
    app.load_foundation()

    assert calls == [good, bad]
    assert saved == [good]
    assert "bad intake" in app.error_var.get()


def test_phase_h_repeat_launch_uses_remembered_intake_without_browse_or_load(root) -> None:
    selected = r"C:\pilot\repeat-intake"
    saved = []

    first, _, first_calls = _app(
        root,
        directory_picker=lambda: selected,
        settings_saver=saved.append,
    )
    first.browse_intake_root()
    assert first_calls == [selected]
    assert saved == [selected]

    def forbidden_picker():
        raise AssertionError("repeat launch must not require Browse")

    second, _, second_calls = _app(
        root,
        directory_picker=forbidden_picker,
        settings_loader=lambda: saved[-1],
    )

    assert second_calls == [selected]
    assert second.intake_root_var.get() == selected
    assert second._controller is not None
    assert tuple(second.product_combo["values"]) == ("alpha", "beta")
    assert second.product_var.get() == ""
    assert second.variant_var.get() == ""
