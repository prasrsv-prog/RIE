from __future__ import annotations

import inspect
import tkinter as tk
from pathlib import Path
from types import SimpleNamespace

import pytest

from rie.ui.grounded_prompt_ui_controller import (
    GroundedPromptUiContractError,
    GroundedPromptUiResult,
)
from rie.ui.tkinter_grounded_prompt_app import GroundedPromptTkApplication
from rie.ui.local_operator_workspace import (
    clone_workspace,
    empty_workspace,
    record_recent_prompt,
    save_preset,
    set_default_product_variant,
    set_last_request,
    toggle_product_favorite,
)


class _FakeController:
    def __init__(self):
        self.product_ids = ("alpha", "beta")
        self.submit_calls = []

    @property
    def product_options(self):
        return (
            SimpleNamespace(product_id="alpha", label="Alpha"),
            SimpleNamespace(product_id="beta", label="Beta"),
        )

    def variant_ids_for_product(self, product_id):
        if product_id == "alpha":
            return ("alpha-a", "alpha-b")
        if product_id == "beta":
            return ("beta-a",)
        raise GroundedPromptUiContractError("unknown active product_id")

    def variant_options_for_product(self, product_id):
        if product_id == "alpha":
            return (
                SimpleNamespace(
                    variant_id="alpha-a",
                    product_id="alpha",
                    label="Alpha A",
                ),
                SimpleNamespace(
                    variant_id="alpha-b",
                    product_id="alpha",
                    label="Alpha B",
                ),
            )
        if product_id == "beta":
            return (
                SimpleNamespace(
                    variant_id="beta-a",
                    product_id="beta",
                    label="Beta A",
                ),
            )
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
    assert tuple(app.product_combo["values"]) == ("Alpha", "Beta")
    assert app.product_var.get() == ""
    assert app.variant_var.get() == ""


def test_product_selection_populates_variants_and_keeps_variant_unselected(root) -> None:
    app, _, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")

    app.refresh_variants()

    assert tuple(app.variant_combo["values"]) == ("Alpha A", "Alpha B")
    assert app.variant_var.get() == ""


def test_submit_validation_requires_explicit_product_variant_and_text_inputs(root) -> None:
    app, controller, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()

    app.submit()

    assert app.error_var.get() == "Choose a Product before generating the prompt."
    assert "product_id must not be empty" in app.technical_error_var.get()
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

    assert app.error_var.get() == "Describe the Requested Output before generating the prompt."
    assert "requested_output must not be empty" in app.technical_error_var.get()
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
    assert tuple(app.product_combo["values"]) == ("Alpha", "Beta")
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
    assert tuple(app.variant_combo["values"]) == ("Beta A",)
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
    assert tuple(app.product_combo["values"]) == ("Alpha", "Beta")
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
    assert app.error_var.get() == "RCIS couldn\'t load this data source. Check the folder and try again."
    assert "remembered intake rejected" in app.technical_error_var.get()


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
    assert tuple(app.product_combo["values"]) == ("Alpha", "Beta")


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
    assert app.error_var.get() == "RCIS couldn\'t load this data source. Check the folder and try again."
    assert "bad intake" in app.technical_error_var.get()


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
    assert tuple(second.product_combo["values"]) == ("Alpha", "Beta")
    assert second.product_var.get() == ""
    assert second.variant_var.get() == ""

def test_phase_i_product_facing_title_and_heading_have_no_mvp(root) -> None:
    app, _, _ = _app(root)
    assert app.root.winfo_toplevel().title() == "RCIS Grounded Prompt"
    assert app.primary_heading.cget("text") == "Create a Grounded Product Prompt"
    assert "MVP" not in app.root.winfo_toplevel().title()
    assert "MVP" not in app.primary_heading.cget("text")


def test_phase_i_remembered_foundation_collapses_data_source(root) -> None:
    app, _, calls = _app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
    )
    assert calls == [r"C:\pilot\remembered-intake"]
    assert app._controller is not None
    assert app._data_source_visible is False


def test_phase_i_first_run_without_foundation_shows_data_source(root) -> None:
    app, _, calls = _app(root, settings_loader=lambda: None)
    assert calls == []
    assert app._controller is None
    assert app._data_source_visible is True


def test_phase_i_data_source_toggle_reveals_and_hides_recovery_controls(root) -> None:
    app, _, _ = _app(root)
    assert app._data_source_visible is True
    app.toggle_data_source()
    assert app._data_source_visible is False
    app.toggle_data_source()
    assert app._data_source_visible is True
    assert app.browse_button.cget("text") == "Browse..."
    assert app.load_button.cget("text") == "Load Foundation"


def test_phase_i_generate_prompt_is_primary_alias_of_submit(root) -> None:
    app, controller, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "grounded product prompt")

    assert app.generate_button.cget("text") == "Generate Prompt"
    assert app.submit_button is app.generate_button

    app.generate_button.invoke()

    assert len(controller.submit_calls) == 1
    assert app.result_state_var.get() == "Prompt ready"


def test_phase_i_success_uses_prompt_ready_and_details_are_collapsed(root) -> None:
    app, _, _ = _prime_success_for_invalidation(root)
    assert app.result_state_var.get() == "Prompt ready"
    assert app._details_visible is False
    assert app.details_toggle_button.cget("text") == "View Details"

    app.toggle_details()

    assert app._details_visible is True
    assert app.details_toggle_button.cget("text") == "Hide Details"
    assert app.bridge_status_var.get() == "PASSED"
    assert app.exact_six_status_var.get() == "PASSED"
    assert app.binding_status_var.get() == "PASSED"
    assert app.grounding_status_var.get() == "PASSED"


def test_phase_i_copy_prompt_copies_exact_prompt_without_mutating_request(root, monkeypatch) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    clipboard = []

    monkeypatch.setattr(root, "clipboard_clear", lambda: clipboard.clear())
    monkeypatch.setattr(root, "clipboard_append", clipboard.append)

    before = {
        "product": app.product_var.get(),
        "variant": app.variant_var.get(),
        "background": app.background_var.get(),
        "camera": app.camera_angle_var.get(),
        "requested": app.requested_output_text.get("1.0", "end-1c"),
        "submit_count": len(controller.submit_calls),
        "load_calls": list(calls),
    }

    app.copy_prompt()

    assert clipboard == ["compiled grounded prompt"]
    assert app.product_var.get() == before["product"]
    assert app.variant_var.get() == before["variant"]
    assert app.background_var.get() == before["background"]
    assert app.camera_angle_var.get() == before["camera"]
    assert app.requested_output_text.get("1.0", "end-1c") == before["requested"]
    assert len(controller.submit_calls) == before["submit_count"]
    assert calls == before["load_calls"]


def test_phase_i_new_request_clears_request_and_result_but_keeps_foundation(root, monkeypatch) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    focus_calls = []
    monkeypatch.setattr(
        app.product_combo,
        "focus_set",
        lambda: focus_calls.append("product"),
    )

    app.new_request()

    assert app._controller is controller
    assert calls == [r"C:\pilot\intake"]
    assert len(controller.submit_calls) == 1
    assert app.product_var.get() == ""
    assert app.variant_var.get() == ""
    assert app.background_var.get() == ""
    assert app.camera_angle_var.get() == ""
    assert app.requested_output_text.get("1.0", "end-1c") == ""
    assert app.prompt_output.get("1.0", "end-1c") == ""
    assert app.result_state_var.get() == ""
    assert app.bridge_status_var.get() == ""
    assert app.exact_six_status_var.get() == ""
    assert app.binding_status_var.get() == ""
    assert app.grounding_status_var.get() == ""
    assert tuple(app.product_combo["values"]) == ("Alpha", "Beta")
    assert tuple(app.variant_combo["values"]) == ()
    assert focus_calls == ["product"]

@pytest.fixture(autouse=True)
def _phase_j_isolate_local_workspace(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))


def _phase_j_app(
    root,
    *,
    directory_picker=lambda: "",
    settings_loader=lambda: None,
    settings_saver=lambda _intake_root: None,
    workspace_loader=lambda: empty_workspace(),
    workspace_saver=lambda _workspace: None,
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
        workspace_loader=workspace_loader,
        workspace_saver=workspace_saver,
    )
    root.update_idletasks()
    return app, controller, calls

def test_phase_j_navigation_exposes_new_prompt_recent_presets_products_settings(root) -> None:
    app, _, _ = _phase_j_app(root)
    assert tuple(app.navigation_buttons) == (
        "New Prompt",
        "Recent",
        "Presets",
        "Products",
        "Settings",
    )
    assert [
        app.navigation_buttons[name].cget("text")
        for name in app.navigation_buttons
    ] == [
        "New Prompt",
        "Recent",
        "Presets",
        "Products",
        "Settings",
    ]


def test_phase_j_valid_last_request_restores_after_foundation_without_submit_and_edits_persist(root) -> None:
    workspace = set_last_request(
        empty_workspace(),
        {
            "product_id": "alpha",
            "variant_id": "alpha-b",
            "background": "remembered background",
            "camera_angle": "three-quarter",
            "requested_output": "remembered output",
        },
    )
    app, controller, calls = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )

    assert calls == [r"C:\pilot\remembered-intake"]
    assert controller.submit_calls == []
    assert app.product_var.get() == "alpha"
    assert app.variant_var.get() == "alpha-b"
    assert app.background_var.get() == "remembered background"
    assert app.camera_angle_var.get() == "three-quarter"
    assert app.requested_output_text.get("1.0", "end-1c") == "remembered output"

    app.background_var.set("edited background")
    assert app._workspace["last_request"]["background"] == "edited background"
    assert controller.submit_calls == []


def test_phase_j_stale_invalid_last_request_is_ignored_without_submit(root) -> None:
    workspace = set_last_request(
        empty_workspace(),
        {
            "product_id": "missing-product",
            "variant_id": "missing-variant",
            "background": "should not restore",
            "camera_angle": "front",
            "requested_output": "should not restore",
        },
    )
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )

    assert controller.submit_calls == []
    assert app.product_var.get() == ""
    assert app.variant_var.get() == ""
    assert app.background_var.get() == ""
    assert app.camera_angle_var.get() == ""
    assert app.requested_output_text.get("1.0", "end-1c") == ""


def test_phase_j_success_records_recent_and_last_request_once(root) -> None:
    saved = []
    app, controller, _ = _phase_j_app(
        root,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "grounded product prompt")

    before_recent = len(app._workspace["recent_prompts"])
    app.submit()

    assert len(controller.submit_calls) == 1
    assert len(app._workspace["recent_prompts"]) == before_recent + 1
    assert app._workspace["recent_prompts"][0]["prompt_text"] == "compiled grounded prompt"
    assert app._workspace["last_request"]["product_id"] == "alpha"
    assert app._workspace["last_request"]["variant_id"] == "alpha-a"
    assert saved


def test_phase_j_recent_duplicate_hydrates_request_without_submit(root) -> None:
    workspace = record_recent_prompt(
        empty_workspace(),
        {
            "product_id": "beta",
            "variant_id": "beta-a",
            "background": "recent background",
            "camera_angle": "side",
            "requested_output": "recent output",
        },
        "stored prompt",
    )
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )
    app.recent_listbox.selection_set(0)

    app.duplicate_recent()

    assert controller.submit_calls == []
    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == "beta-a"
    assert app.background_var.get() == "recent background"
    assert app.camera_angle_var.get() == "side"
    assert app.requested_output_text.get("1.0", "end-1c") == "recent output"
    assert app.prompt_output.get("1.0", "end-1c") == ""


def test_phase_j_recent_copy_uses_exact_stored_prompt_without_request_mutation(root, monkeypatch) -> None:
    workspace = record_recent_prompt(
        empty_workspace(),
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "history background",
            "camera_angle": "front",
            "requested_output": "history output",
        },
        "exact stored history prompt",
    )
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )
    clipboard = []
    monkeypatch.setattr(root, "clipboard_clear", lambda: clipboard.clear())
    monkeypatch.setattr(root, "clipboard_append", clipboard.append)
    before = (
        app.product_var.get(),
        app.variant_var.get(),
        app.background_var.get(),
        app.camera_angle_var.get(),
        app.requested_output_text.get("1.0", "end-1c"),
    )
    app.recent_listbox.selection_set(0)

    app.copy_recent_prompt()

    assert clipboard == ["exact stored history prompt"]
    assert (
        app.product_var.get(),
        app.variant_var.get(),
        app.background_var.get(),
        app.camera_angle_var.get(),
        app.requested_output_text.get("1.0", "end-1c"),
    ) == before
    assert controller.submit_calls == []


def test_phase_j_recent_favorite_toggle_persists_local_workspace_only(root) -> None:
    workspace = record_recent_prompt(
        empty_workspace(),
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "",
            "camera_angle": "",
            "requested_output": "",
        },
        "stored prompt",
    )
    saved = []
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    app.recent_listbox.selection_set(0)

    app.toggle_recent_selected_favorite()

    assert app._workspace["recent_prompts"][0]["favorite"] is True
    assert saved[-1]["recent_prompts"][0]["favorite"] is True
    assert controller.submit_calls == []


def test_phase_j_preset_save_load_delete_is_local_and_never_submits(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
    )
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-b")
    app.background_var.set("preset background")
    app.camera_angle_var.set("top")
    app.requested_output_text.insert("1.0", "preset output")
    app.preset_name_var.set("My Preset")

    app.save_current_preset()
    assert app._workspace["presets"][0]["name"] == "My Preset"
    assert controller.submit_calls == []

    app.new_request()
    app.show_workspace_view("Presets")
    app.preset_listbox.selection_set(0)
    app.load_selected_preset()
    assert app.product_var.get() == "alpha"
    assert app.variant_var.get() == "alpha-b"
    assert app.background_var.get() == "preset background"
    assert app.camera_angle_var.get() == "top"
    assert app.requested_output_text.get("1.0", "end-1c") == "preset output"
    assert controller.submit_calls == []

    app.show_workspace_view("Presets")
    app.preset_listbox.selection_set(0)
    app.delete_selected_preset()
    assert app._workspace["presets"] == []
    assert controller.submit_calls == []


def test_phase_j_products_render_labels_and_set_explicit_id_default_without_catalog_change(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
    )
    before_products = controller.product_ids
    app.show_workspace_view("Products")

    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "Alpha / Alpha A",
        "Alpha / Alpha B",
        "Beta / Beta A",
    )
    app.product_variant_listbox.selection_set(1)
    app.set_selected_product_variant_default()

    assert app._workspace["default_product_variant"] == {
        "product_id": "alpha",
        "variant_id": "alpha-b",
    }
    assert controller.product_ids == before_products
    assert controller.submit_calls == []


def test_phase_j_settings_retains_data_source_recovery_and_can_clear_default(root) -> None:
    workspace = set_default_product_variant(
        empty_workspace(),
        "alpha",
        "alpha-a",
    )
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )
    assert app._data_source_visible is False

    app.show_workspace_view("Settings")

    assert app._data_source_visible is True
    assert app.settings_data_source_button.cget("text") == "Data Source"
    assert app.default_status_var.get() == "Alpha / Alpha A"

    app.clear_default_product_variant()

    assert app._workspace["default_product_variant"] is None
    assert app.default_status_var.get() == "No default"
    assert controller.submit_calls == []


def test_phase_j_new_request_preserves_workspace_and_applies_only_explicit_valid_default(root) -> None:
    workspace = record_recent_prompt(
        empty_workspace(),
        {
            "product_id": "beta",
            "variant_id": "beta-a",
            "background": "history",
            "camera_angle": "front",
            "requested_output": "history",
        },
        "history prompt",
    )
    workspace = save_preset(
        workspace,
        "Keep Me",
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "preset",
            "camera_angle": "front",
            "requested_output": "preset",
        },
    )
    workspace = toggle_product_favorite(
        workspace,
        "beta",
        "beta-a",
    )
    workspace = set_default_product_variant(
        workspace,
        "alpha",
        "alpha-b",
    )
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )

    app.new_request()

    assert app._controller is controller
    assert len(app._workspace["recent_prompts"]) == 1
    assert len(app._workspace["presets"]) == 1
    assert app._workspace["product_favorites"] == [
        {"product_id": "beta", "variant_id": "beta-a"}
    ]
    assert app.product_var.get() == "alpha"
    assert app.variant_var.get() == "alpha-b"
    assert app.background_var.get() == ""
    assert app.camera_angle_var.get() == ""
    assert app.requested_output_text.get("1.0", "end-1c") == ""
    assert controller.submit_calls == []


def test_phase_j_workspace_save_failure_does_not_invalidate_successful_prompt(root) -> None:
    def fail_save(_state):
        raise OSError("workspace disk unavailable")

    app, controller, _ = _phase_j_app(
        root,
        workspace_saver=fail_save,
    )
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "grounded product prompt")

    app.submit()

    assert len(controller.submit_calls) == 1
    assert app.result_state_var.get() == "Prompt ready"
    assert app.prompt_output.get("1.0", "end-1c") == "compiled grounded prompt"
    assert app.workspace_feedback_var.get() == (
        "Local workspace could not be saved. Your current prompt is still available."
    )
    assert "workspace disk unavailable" in app.technical_error_var.get()

def test_phase_k_empty_data_source_uses_friendly_primary_error_and_technical_detail(root) -> None:
    app, controller, calls = _phase_j_app(root)
    app.load_foundation()
    assert app.error_var.get() == "Choose a data source before loading RCIS."
    assert app.technical_error_var.get() == "intake_root must not be empty"
    assert controller.submit_calls == []
    assert calls == []

def test_phase_k_settings_loader_failure_is_visible_without_crash(root) -> None:
    def fail_load():
        raise OSError("settings file unavailable")
    app = GroundedPromptTkApplication(
        root,
        controller_factory=lambda **_kwargs: _FakeController(),
        directory_picker=lambda: "",
        settings_loader=fail_load,
        settings_saver=lambda _value: None,
        workspace_loader=lambda: empty_workspace(),
        workspace_saver=lambda _workspace: None,
    )
    assert app.error_var.get() == "Saved data source could not be restored. Open Settings to choose it again."
    assert "settings file unavailable" in app.technical_error_var.get()
    assert app._data_source_visible is True

def test_phase_k_manual_load_failure_exposes_try_again_and_one_retry_only(root) -> None:
    controller = _FakeController()
    calls = []
    def factory(*, intake_root):
        calls.append(intake_root)
        if len(calls) == 1:
            raise OSError("temporary intake read failure")
        return controller
    app = GroundedPromptTkApplication(
        root,
        controller_factory=factory,
        directory_picker=lambda: "",
        settings_loader=lambda: None,
        settings_saver=lambda _value: None,
        workspace_loader=lambda: empty_workspace(),
        workspace_saver=lambda _workspace: None,
    )
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    assert calls == [r"C:\pilot\intake"]
    assert app.error_var.get() == "RCIS couldn't load this data source. Check the folder and try again."
    assert "temporary intake read failure" in app.technical_error_var.get()
    app.retry_button.invoke()
    assert calls == [r"C:\pilot\intake", r"C:\pilot\intake"]
    assert app._controller is controller
    assert controller.submit_calls == []

def test_phase_k_settings_save_failure_is_nonfatal_and_visible(root) -> None:
    def fail_save(_value):
        raise OSError("settings write blocked")
    controller = _FakeController()
    app = GroundedPromptTkApplication(
        root,
        controller_factory=lambda **_kwargs: controller,
        directory_picker=lambda: "",
        settings_loader=lambda: None,
        settings_saver=fail_save,
        workspace_loader=lambda: empty_workspace(),
        workspace_saver=lambda _workspace: None,
    )
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    assert app._controller is controller
    assert app.workspace_feedback_var.get() == (
        "Foundation loaded, but RCIS couldn't remember this data source for next time."
    )
    assert "settings write blocked" in app.technical_error_var.get()
    assert app.error_var.get() == ""

def test_phase_k_submit_without_foundation_is_friendly_and_open_settings_never_submits(root) -> None:
    app, controller, calls = _phase_j_app(root)
    app.submit()
    assert app.error_var.get() == "RCIS needs a data source before it can generate a prompt."
    assert app.technical_error_var.get() == "foundation must be loaded before submit"
    app.open_settings_button.invoke()
    assert app._workspace_view == "Settings"
    assert app._data_source_visible is True
    assert controller.submit_calls == []
    assert calls == []

def test_phase_k_validation_failure_try_again_submits_once_after_fix(root) -> None:
    app, controller, _ = _phase_j_app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "   ")
    app.submit()
    assert controller.submit_calls == []
    assert app.error_var.get() == "Describe the Requested Output before generating the prompt."
    assert "requested_output must not be empty" in app.technical_error_var.get()
    app.requested_output_text.delete("1.0", "end")
    app.requested_output_text.insert("1.0", "grounded product prompt")
    app.retry_button.invoke()
    assert len(controller.submit_calls) == 1
    assert app.result_state_var.get() == "Prompt ready"

def test_phase_k_success_after_retry_clears_error_and_technical_detail(root) -> None:
    app, controller, _ = _phase_j_app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_var.set("alpha")
    app.refresh_variants()
    app.variant_var.set("alpha-a")
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.submit()
    assert app.error_var.get() == "Describe the Requested Output before generating the prompt."
    app.requested_output_text.insert("1.0", "grounded product prompt")
    app.retry_button.invoke()
    assert len(controller.submit_calls) == 1
    assert app.error_var.get() == ""
    assert app.technical_error_var.get() == ""

def test_phase_k_copy_prompt_success_has_feedback_without_request_mutation(root, monkeypatch) -> None:
    app, controller, calls = _prime_success_for_invalidation(root)
    copied = []
    monkeypatch.setattr(root, "clipboard_clear", lambda: copied.clear())
    monkeypatch.setattr(root, "clipboard_append", copied.append)
    before = app._visible_request()
    app.copy_prompt()
    assert copied == ["compiled grounded prompt"]
    assert app.copy_feedback_var.get() == "Copied to clipboard."
    assert app._visible_request() == before
    assert len(controller.submit_calls) == 1
    assert calls == [r"C:\pilot\intake"]

def test_phase_k_copy_prompt_failure_is_caught_and_retry_uses_same_text(root, monkeypatch) -> None:
    app, controller, _ = _prime_success_for_invalidation(root)
    failures = []
    def fail_append(value):
        failures.append(value)
        raise OSError("clipboard unavailable")
    monkeypatch.setattr(root, "clipboard_clear", lambda: None)
    monkeypatch.setattr(root, "clipboard_append", fail_append)
    app.copy_prompt()
    assert failures == ["compiled grounded prompt"]
    assert app.error_var.get() == "RCIS couldn't copy to the clipboard. Try again."
    assert "clipboard unavailable" in app.technical_error_var.get()
    copied = []
    monkeypatch.setattr(root, "clipboard_append", copied.append)
    app.retry_button.invoke()
    assert copied == ["compiled grounded prompt"]
    assert app.copy_feedback_var.get() == "Copied to clipboard."
    assert len(controller.submit_calls) == 1

def test_phase_k_recent_copy_failure_is_caught_without_request_or_submit_mutation(root, monkeypatch) -> None:
    workspace = record_recent_prompt(
        empty_workspace(),
        {"product_id":"alpha","variant_id":"alpha-a","background":"bg","camera_angle":"front","requested_output":"out"},
        "stored history prompt",
    )
    app, controller, _ = _phase_j_app(root, workspace_loader=lambda: workspace)
    before = app._visible_request()
    app.recent_listbox.selection_set(0)
    monkeypatch.setattr(root, "clipboard_clear", lambda: None)
    def fail_append(_value):
        raise OSError("recent clipboard blocked")
    monkeypatch.setattr(root, "clipboard_append", fail_append)
    app.copy_recent_prompt()
    assert app.error_var.get() == "RCIS couldn't copy to the clipboard. Try again."
    assert "recent clipboard blocked" in app.technical_error_var.get()
    assert app._visible_request() == before
    assert controller.submit_calls == []

def test_phase_k_workspace_save_failure_stays_nonfatal_and_friendly(root) -> None:
    def fail_save(_state):
        raise OSError("workspace persistence denied")
    app = GroundedPromptTkApplication(
        root,
        controller_factory=lambda **_kwargs: _FakeController(),
        directory_picker=lambda: "",
        settings_loader=lambda: None,
        settings_saver=lambda _value: None,
        workspace_loader=lambda: empty_workspace(),
        workspace_saver=fail_save,
    )
    app.intake_root_var.set(r"C:\\pilot\\intake")
    app.load_foundation()
    app.background_var.set("changed")
    assert app.workspace_feedback_var.get() == (
        "Local workspace could not be saved. Your current prompt is still available."
    )
    assert "workspace persistence denied" in app.technical_error_var.get()

def test_phase_k_recovery_controls_and_technical_detail_are_available(root) -> None:
    app, _, _ = _phase_j_app(root)
    assert app.retry_button.cget("text") == "Try Again"
    assert app.open_settings_button.cget("text") == "Open Settings"
    assert app.technical_error_var.get() == ""
    app.load_foundation()
    assert app.error_var.get() == "Choose a data source before loading RCIS."
    assert app.technical_error_var.get() == "intake_root must not be empty"


def test_phase_m_product_combobox_displays_labels_but_keeps_internal_id_empty_until_selection(root) -> None:
    app, _, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    assert tuple(app.product_combo["values"]) == ("Alpha", "Beta")
    assert app.product_label_var.get() == ""
    assert app.product_var.get() == ""


def test_phase_m_exact_product_label_selection_resolves_loaded_id_without_inference(root) -> None:
    app, _, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_label_var.set("Alpha")
    app._on_product_label_selected()
    assert app.product_var.get() == "alpha"
    assert tuple(app.variant_combo["values"]) == ("Alpha A", "Alpha B")
    assert app.variant_var.get() == ""


def test_phase_m_variant_combobox_displays_labels_and_exact_selection_resolves_id(root) -> None:
    app, _, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_label_var.set("Alpha")
    app._on_product_label_selected()
    app.variant_label_var.set("Alpha B")
    app._on_variant_label_selected()
    assert app.product_var.get() == "alpha"
    assert app.variant_var.get() == "alpha-b"


def test_phase_m_submit_from_visible_labels_forwards_exact_original_ids(root) -> None:
    app, controller, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_label_var.set("Alpha")
    app._on_product_label_selected()
    app.variant_label_var.set("Alpha A")
    app._on_variant_label_selected()
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "grounded product prompt")
    app.submit()
    assert controller.submit_calls[-1]["product_id"] == "alpha"
    assert controller.submit_calls[-1]["variant_id"] == "alpha-a"


def test_phase_m_workspace_persistence_remains_id_based_while_hydration_renders_labels(root) -> None:
    workspace = set_last_request(
        empty_workspace(),
        {
            "product_id": "beta",
            "variant_id": "beta-a",
            "background": "workspace background",
            "camera_angle": "side",
            "requested_output": "workspace output",
        },
    )
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )
    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == "beta-a"
    assert app.product_label_var.get() == "Beta"
    assert app.variant_label_var.get() == "Beta A"
    assert app._visible_request()["product_id"] == "beta"
    assert app._visible_request()["variant_id"] == "beta-a"


def test_phase_m_products_and_default_views_render_labels_but_store_ids(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
    )
    app.show_workspace_view("Products")
    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "Alpha / Alpha A",
        "Alpha / Alpha B",
        "Beta / Beta A",
    )
    app.product_variant_listbox.selection_set(1)
    app.set_selected_product_variant_default()
    assert app._workspace["default_product_variant"] == {
        "product_id": "alpha",
        "variant_id": "alpha-b",
    }
    assert app.default_status_var.get() == "Alpha / Alpha B"


def test_phase_m_unknown_visible_product_label_fails_closed_without_id_derivation(root) -> None:
    app, _, _ = _app(root)
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_label_var.set("alpha")
    app._on_product_label_selected()
    assert app.product_var.get() == ""
    assert app.variant_var.get() == ""
    assert "couldn't resolve the selected product" in app.error_var.get()


def test_phase_m_source_has_no_label_slugification_or_direct_governed_data_access() -> None:
    source = inspect.getsource(
        __import__(
            "rie.ui.tkinter_grounded_prompt_app",
            fromlist=["GroundedPromptTkApplication"],
        )
    )
    lowered = source.lower()
    assert "slugify" not in lowered
    assert "label.lower(" not in lowered
    assert "label.casefold(" not in lowered
    assert "label.replace(" not in lowered
    assert "label.split(" not in lowered
    assert "sqlite" not in lowered
    assert "pilot-product-variant-exact18" not in lowered
    assert "pilot-source-intake-manifest" not in lowered


def _phase_n_app(
    root,
    *,
    workspace=None,
    save_dialog=lambda **_kwargs: "",
    file_writer=lambda _path, _payload: None,
):
    state = empty_workspace() if workspace is None else workspace
    return GroundedPromptTkApplication(
        root,
        controller_factory=lambda **_kwargs: _FakeController(),
        directory_picker=lambda: "",
        settings_loader=lambda: None,
        settings_saver=lambda _value: None,
        workspace_loader=lambda: state,
        workspace_saver=lambda _workspace: None,
        save_dialog=save_dialog,
        file_writer=file_writer,
    )


def _phase_n_prime_success(app) -> None:
    app.intake_root_var.set(r"C:\pilot\intake")
    app.load_foundation()
    app.product_label_var.set("Alpha")
    app._on_product_label_selected()
    app.variant_label_var.set("Alpha A")
    app._on_variant_label_selected()
    app.background_var.set("dark studio")
    app.camera_angle_var.set("front")
    app.requested_output_text.insert("1.0", "grounded product prompt")
    app.submit()


def test_phase_n_current_save_writes_exact_utf8_prompt_and_exact_dialog_contract(root) -> None:
    dialogs = []
    writes = []
    def dialog(**kwargs):
        dialogs.append(kwargs)
        return r"C:\exports\prompt.txt"
    app = _phase_n_app(
        root,
        save_dialog=dialog,
        file_writer=lambda path, payload: writes.append((path, payload)),
    )
    _phase_n_prime_success(app)
    before = app._visible_request()
    app.save_prompt()
    assert writes == [(r"C:\exports\prompt.txt", b"compiled grounded prompt")]
    assert dialogs == [{
        "title": "Save prompt",
        "initialfile": "RCIS-grounded-prompt.txt",
        "defaultextension": ".txt",
        "filetypes": (
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ),
    }]
    assert "initialdir" not in dialogs[0]
    assert app.copy_feedback_var.get() == "Prompt saved."
    assert app.result_state_var.get() == "Prompt ready"
    assert app._visible_request() == before


def test_phase_n_shared_writer_adds_no_bom_metadata_newline_or_newline_translation(root) -> None:
    writes = []
    app = _phase_n_app(
        root,
        save_dialog=lambda **_kwargs: r"C:\exports\exact.txt",
        file_writer=lambda path, payload: writes.append((path, payload)),
    )
    prompt = "line one\nline two"
    assert app._save_prompt_text(prompt) is True
    assert writes == [(r"C:\exports\exact.txt", b"line one\nline two")]
    assert not writes[0][1].startswith(b"\xef\xbb\xbf")
    assert not writes[0][1].endswith(b"\n")
    assert b"product_id" not in writes[0][1]
    assert b"variant_id" not in writes[0][1]


def test_phase_n_current_save_cancel_is_noop_and_preserves_result_workspace_and_feedback(root) -> None:
    writes = []
    app = _phase_n_app(
        root,
        save_dialog=lambda **_kwargs: "",
        file_writer=lambda path, payload: writes.append((path, payload)),
    )
    _phase_n_prime_success(app)
    app.copy_feedback_var.set("Copied to clipboard.")
    before_request = app._visible_request()
    before_workspace = app._workspace
    app.save_prompt()
    assert writes == []
    assert app.prompt_output.get("1.0", "end-1c") == "compiled grounded prompt"
    assert app.result_state_var.get() == "Prompt ready"
    assert app.copy_feedback_var.get() == "Copied to clipboard."
    assert app._visible_request() == before_request
    assert app._workspace == before_workspace
    assert app.error_var.get() == ""


def test_phase_n_current_save_is_blocked_after_result_becomes_stale(root) -> None:
    dialogs = []
    app = _phase_n_app(
        root,
        save_dialog=lambda **kwargs: dialogs.append(kwargs) or r"C:\never.txt",
    )
    _phase_n_prime_success(app)
    app.background_var.set("changed after success")
    app.save_prompt()
    assert dialogs == []
    assert app.prompt_output.get("1.0", "end-1c") == ""
    assert app.error_var.get() == "Generate a current prompt before saving."
    assert "empty or stale" in app.technical_error_var.get()


def test_phase_n_write_failure_is_friendly_and_preserves_current_prompt_and_request(root) -> None:
    def fail_write(_path, _payload):
        raise OSError("destination is read-only")
    app = _phase_n_app(
        root,
        save_dialog=lambda **_kwargs: r"C:\exports\prompt.txt",
        file_writer=fail_write,
    )
    _phase_n_prime_success(app)
    before = app._visible_request()
    app.save_prompt()
    assert app.error_var.get() == (
        "RCIS couldn't save this prompt. Choose another location and try again."
    )
    assert "destination is read-only" in app.technical_error_var.get()
    assert app.prompt_output.get("1.0", "end-1c") == "compiled grounded prompt"
    assert app.result_state_var.get() == "Prompt ready"
    assert app._visible_request() == before


def test_phase_n_recent_save_writes_exact_stored_prompt_without_open_duplicate_or_submit(root) -> None:
    workspace = record_recent_prompt(
        empty_workspace(),
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "bg",
            "camera_angle": "front",
            "requested_output": "out",
        },
        "stored recent prompt",
    )
    writes = []
    app = _phase_n_app(
        root,
        workspace=workspace,
        save_dialog=lambda **_kwargs: r"C:\exports\recent.txt",
        file_writer=lambda path, payload: writes.append((path, payload)),
    )
    before_request = app._visible_request()
    app.recent_listbox.selection_set(0)
    app.save_recent_prompt()
    assert writes == [(r"C:\exports\recent.txt", b"stored recent prompt")]
    assert app._visible_request() == before_request
    assert app._workspace == workspace


def test_phase_n_recent_save_without_selection_does_not_open_dialog_or_write(root) -> None:
    dialogs = []
    writes = []
    app = _phase_n_app(
        root,
        save_dialog=lambda **kwargs: dialogs.append(kwargs) or r"C:\never.txt",
        file_writer=lambda path, payload: writes.append((path, payload)),
    )
    app.save_recent_prompt()
    assert dialogs == []
    assert writes == []
    assert app.error_var.get() == "Choose a recent prompt before saving."


def test_phase_n_recent_save_cancel_is_noop_and_preserves_recent_workspace(root) -> None:
    workspace = record_recent_prompt(
        empty_workspace(),
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "bg",
            "camera_angle": "front",
            "requested_output": "out",
        },
        "stored recent prompt",
    )
    writes = []
    app = _phase_n_app(
        root,
        workspace=workspace,
        save_dialog=lambda **_kwargs: "",
        file_writer=lambda path, payload: writes.append((path, payload)),
    )
    app.recent_listbox.selection_set(0)
    before = app._workspace
    app.save_recent_prompt()
    assert writes == []
    assert app._workspace == before
    assert app.error_var.get() == ""

# Phase P - searchable operator workspace

def _phase_p_workspace():
    workspace = empty_workspace()
    workspace = record_recent_prompt(
        workspace,
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "alpha background",
            "camera_angle": "front",
            "requested_output": "alpha output",
        },
        "alpha stored prompt",
    )
    workspace = record_recent_prompt(
        workspace,
        {
            "product_id": "beta",
            "variant_id": "beta-a",
            "background": "beta background",
            "camera_angle": "side",
            "requested_output": "beta output",
        },
        "beta stored prompt",
    )
    workspace = save_preset(
        workspace,
        "Studio Alpha",
        {
            "product_id": "alpha",
            "variant_id": "alpha-b",
            "background": "studio",
            "camera_angle": "top",
            "requested_output": "alpha preset output",
        },
    )
    workspace = save_preset(
        workspace,
        "Outdoor Beta",
        {
            "product_id": "beta",
            "variant_id": "beta-a",
            "background": "outdoor",
            "camera_angle": "front",
            "requested_output": "beta preset output",
        },
    )
    return workspace


def test_phase_p_recent_filter_is_case_insensitive_and_clear_restores_rows(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_p_workspace,
    )
    original_rows = tuple(app.recent_listbox.get(0, "end"))
    assert len(original_rows) == 2

    app.recent_filter_var.set("ALPHA")
    assert tuple(app.recent_listbox.get(0, "end")) == (
        "Alpha / Alpha A",
    )

    app.recent_filter_var.set("")
    assert tuple(app.recent_listbox.get(0, "end")) == original_rows


def test_phase_p_filtered_recent_duplicate_maps_to_exact_source_item(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_p_workspace,
    )
    app.recent_filter_var.set("alpha")
    app.recent_listbox.selection_set(0)

    app.duplicate_recent()

    assert app.product_var.get() == "alpha"
    assert app.variant_var.get() == "alpha-a"
    assert app.background_var.get() == "alpha background"
    assert app.camera_angle_var.get() == "front"
    assert app.requested_output_text.get("1.0", "end-1c") == "alpha output"
    assert controller.submit_calls == []


def test_phase_p_filtered_recent_favorite_maps_to_exact_source_index(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_p_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    app.recent_filter_var.set("alpha")
    app.recent_listbox.selection_set(0)

    app.toggle_recent_selected_favorite()

    alpha = next(
        item
        for item in app._workspace["recent_prompts"]
        if item["product_id"] == "alpha"
    )
    beta = next(
        item
        for item in app._workspace["recent_prompts"]
        if item["product_id"] == "beta"
    )
    assert alpha["favorite"] is True
    assert beta["favorite"] is False
    assert app.recent_filter_var.get() == "alpha"
    assert tuple(app.recent_listbox.get(0, "end")) == (
        "* Alpha / Alpha A",
    )
    assert saved[-1]["recent_prompts"]


def test_phase_p_preset_filter_maps_load_and_delete_to_exact_source(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_p_workspace,
    )
    app.preset_filter_var.set("OUTDOOR")
    assert tuple(app.preset_listbox.get(0, "end")) == (
        "Outdoor Beta",
    )
    app.preset_listbox.selection_set(0)

    app.load_selected_preset()

    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == "beta-a"
    assert app.background_var.get() == "outdoor"
    assert controller.submit_calls == []

    app.show_workspace_view("Presets")
    assert app.preset_filter_var.get() == "OUTDOOR"
    app.preset_listbox.selection_set(0)

    app.delete_selected_preset()

    assert [item["name"] for item in app._workspace["presets"]] == [
        "Studio Alpha"
    ]
    assert tuple(app.preset_listbox.get(0, "end")) == ()


def test_phase_p_product_filter_maps_use_default_and_favorite_to_exact_ids(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
    )
    app.show_workspace_view("Products")
    app.product_filter_var.set("bEtA")
    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "Beta / Beta A",
    )
    app.product_variant_listbox.selection_set(0)

    app.use_selected_product_variant()

    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == "beta-a"
    assert controller.submit_calls == []

    app.show_workspace_view("Products")
    assert app.product_filter_var.get() == "bEtA"
    app.product_variant_listbox.selection_set(0)

    app.set_selected_product_variant_default()

    assert app._workspace["default_product_variant"] == {
        "product_id": "beta",
        "variant_id": "beta-a",
    }

    app.product_variant_listbox.selection_set(0)
    app.toggle_selected_product_variant_favorite()

    assert app._workspace["product_favorites"] == [
        {"product_id": "beta", "variant_id": "beta-a"}
    ]
    assert app.product_filter_var.get() == "bEtA"
    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "* Beta / Beta A",
    )


def test_phase_p_filter_changes_never_persist_workspace(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_p_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)

    app.recent_filter_var.set("alpha")
    app.preset_filter_var.set("studio")
    app.product_filter_var.set("beta")
    app.recent_filter_var.set("")
    app.preset_filter_var.set("")
    app.product_filter_var.set("")

    assert len(saved) == baseline


def test_phase_p_no_match_filters_are_empty_and_non_mutating(root) -> None:
    workspace = _phase_p_workspace()
    before = clone_workspace(workspace)
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )

    app.recent_filter_var.set("not-present-anywhere")
    app.preset_filter_var.set("not-present-anywhere")
    app.product_filter_var.set("not-present-anywhere")

    assert tuple(app.recent_listbox.get(0, "end")) == ()
    assert tuple(app.preset_listbox.get(0, "end")) == ()
    assert tuple(app.product_variant_listbox.get(0, "end")) == ()
    assert app._workspace == before


def test_phase_p_favorite_markers_do_not_participate_in_matching(root) -> None:
    workspace = _phase_p_workspace()
    alpha_index = next(
        index
        for index, item in enumerate(workspace["recent_prompts"])
        if item["product_id"] == "alpha"
    )
    workspace["recent_prompts"][alpha_index]["favorite"] = True
    workspace = toggle_product_favorite(
        workspace,
        "beta",
        "beta-a",
    )
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )

    app.recent_filter_var.set("*")
    app.product_filter_var.set("*")

    assert tuple(app.recent_listbox.get(0, "end")) == ()
    assert tuple(app.product_variant_listbox.get(0, "end")) == ()

    app.recent_filter_var.set("alpha")
    app.product_filter_var.set("beta")

    assert tuple(app.recent_listbox.get(0, "end")) == (
        "* Alpha / Alpha A",
    )
    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "* Beta / Beta A",
    )

# Phase Q - Recent prompt context preview and context search

def _phase_q_workspace():
    workspace = empty_workspace()
    workspace = record_recent_prompt(
        workspace,
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "matte charcoal wall",
            "camera_angle": "front",
            "requested_output": "catalog hero",
        },
        "prompt-only-token-one",
    )
    workspace = record_recent_prompt(
        workspace,
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "bright window studio",
            "camera_angle": "rear three-quarter",
            "requested_output": "marketplace detail",
        },
        "prompt-only-token-two",
    )
    workspace = record_recent_prompt(
        workspace,
        {
            "product_id": "beta",
            "variant_id": "beta-a",
            "background": "outdoor stone",
            "camera_angle": "side",
            "requested_output": "social crop",
        },
        "beta prompt body",
    )
    return workspace


def _select_recent_visible_row(app, visible_index: int) -> None:
    app.recent_listbox.selection_clear(0, "end")
    app.recent_listbox.selection_set(visible_index)
    app._on_recent_selection_changed()


def test_phase_q_recent_preview_shows_exact_selected_source_item(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    assert app.recent_listbox.bind("<<ListboxSelect>>")

    _select_recent_visible_row(app, 0)
    source_index = app._visible_recent_indices[0]
    expected = app._workspace["recent_prompts"][source_index]

    assert app.recent_context_product_variant_var.get() == (
        app._display_product_variant(
            expected["product_id"],
            expected["variant_id"],
        )
    )
    assert (
        app.recent_context_background_var.get()
        == expected["background"]
    )
    assert (
        app.recent_context_camera_angle_var.get()
        == expected["camera_angle"]
    )
    assert (
        app.recent_context_requested_output_var.get()
        == expected["requested_output"]
    )


def test_phase_q_filtered_duplicate_preview_maps_to_exact_original_item(
    root,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    app.recent_filter_var.set("alpha")
    assert tuple(app.recent_listbox.get(0, "end")) == (
        "Alpha / Alpha A",
        "Alpha / Alpha A",
    )

    _select_recent_visible_row(app, 1)
    source_index = app._visible_recent_indices[1]
    expected = app._workspace["recent_prompts"][source_index]

    assert (
        app.recent_context_background_var.get()
        == expected["background"]
    )
    assert (
        app.recent_context_camera_angle_var.get()
        == expected["camera_angle"]
    )
    assert (
        app.recent_context_requested_output_var.get()
        == expected["requested_output"]
    )


@pytest.mark.parametrize(
    ("query", "field"),
    (
        ("CHARCOAL", "background"),
        ("three-QUARTER", "camera_angle"),
        ("Marketplace Detail", "requested_output"),
    ),
)
def test_phase_q_recent_context_search_matches_request_fields(
    root,
    query,
    field,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    app.recent_filter_var.set(query)

    assert app.recent_listbox.size() == 1
    source_index = app._visible_recent_indices[0]
    selected = app._workspace["recent_prompts"][source_index]
    assert query.strip().casefold() in str(selected[field]).casefold()


def test_phase_t_recent_search_matches_prompt_text_alone(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )

    app.recent_filter_var.set("PROMPT-only-token-one")

    assert tuple(app.recent_listbox.get(0, "end")) == (
        "Alpha / Alpha A",
    )
    assert len(app._visible_recent_indices) == 1
    source_index = app._visible_recent_indices[0]
    assert (
        app._workspace["recent_prompts"][source_index]["prompt_text"]
        == "prompt-only-token-one"
    )


def test_phase_q_favorite_marker_does_not_participate_in_context_search(
    root,
) -> None:
    workspace = _phase_q_workspace()
    workspace["recent_prompts"][0]["favorite"] = True
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=lambda: workspace,
    )

    app.recent_filter_var.set("*")

    assert tuple(app.recent_listbox.get(0, "end")) == ()


def test_phase_q_filter_refresh_and_no_match_clear_stale_preview(
    root,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    _select_recent_visible_row(app, 0)
    assert app.recent_context_product_variant_var.get()

    app.recent_filter_var.set("not-present-anywhere")

    assert tuple(app.recent_listbox.get(0, "end")) == ()
    assert app.recent_context_product_variant_var.get() == ""
    assert app.recent_context_background_var.get() == ""
    assert app.recent_context_camera_angle_var.get() == ""
    assert app.recent_context_requested_output_var.get() == ""


def test_phase_q_preview_and_filter_interaction_never_persists_workspace(
    root,
) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)

    app.recent_filter_var.set("alpha")
    _select_recent_visible_row(app, 0)
    app.recent_filter_var.set("window")
    _select_recent_visible_row(app, 0)
    app.recent_filter_var.set("")

    assert len(saved) == baseline


def test_phase_q_filtered_duplicate_actions_still_use_exact_source_item(
    root,
) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    app.recent_filter_var.set("alpha")
    _select_recent_visible_row(app, 1)
    source_index = app._visible_recent_indices[1]
    expected = dict(app._workspace["recent_prompts"][source_index])

    app.duplicate_recent()

    assert app.product_var.get() == expected["product_id"]
    assert app.variant_var.get() == expected["variant_id"]
    assert app.background_var.get() == expected["background"]
    assert app.camera_angle_var.get() == expected["camera_angle"]
    assert (
        app.requested_output_text.get("1.0", "end-1c")
        == expected["requested_output"]
    )
    assert controller.submit_calls == []


def test_phase_q_daily_use_guide_documents_context_preview_and_search() -> None:
    guide = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "rcis-grounded-prompt-daily-use.md"
    ).read_text(encoding="ascii").lower()

    for value in (
        "read-only product / variant, background, camera angle, requested output, and exact stored prompt text context",
        "selected recent context preview, including the exact stored prompt text, is temporary ui state",
        "it is not written to the persisted local workspace",
        "phase o general-user usability proof remains a separate unresolved governance activity",
    ):
        assert value in guide

# Phase T - Recent prompt text preview and full-text search

def test_phase_t_recent_preview_shows_exact_stored_prompt_text(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )

    _select_recent_visible_row(app, 0)
    source_index = app._visible_recent_indices[0]
    expected = app._workspace["recent_prompts"][source_index]

    assert app.recent_context_prompt_text_var.get() == expected["prompt_text"]


def test_phase_t_filtered_recent_preview_maps_prompt_text_to_exact_source(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    app.recent_filter_var.set("alpha")

    _select_recent_visible_row(app, 1)
    source_index = app._visible_recent_indices[1]
    expected = app._workspace["recent_prompts"][source_index]

    assert app.recent_context_prompt_text_var.get() == expected["prompt_text"]


def test_phase_t_no_match_filter_clears_all_recent_preview_fields(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    _select_recent_visible_row(app, 0)
    source_index = app._visible_recent_indices[0]
    expected = app._workspace["recent_prompts"][source_index]
    assert app.recent_context_prompt_text_var.get() == expected["prompt_text"]

    app.recent_filter_var.set("not-present-anywhere")

    assert tuple(app.recent_listbox.get(0, "end")) == ()
    assert app.recent_context_product_variant_var.get() == ""
    assert app.recent_context_background_var.get() == ""
    assert app.recent_context_camera_angle_var.get() == ""
    assert app.recent_context_requested_output_var.get() == ""
    assert app.recent_context_prompt_text_var.get() == ""


def test_phase_t_prompt_preview_and_full_text_filter_never_persist_workspace(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)

    app.recent_filter_var.set("prompt-only-token-two")
    _select_recent_visible_row(app, 0)
    assert app.recent_context_prompt_text_var.get() == "prompt-only-token-two"
    app.recent_filter_var.set("")

    assert len(saved) == baseline


def test_phase_t_filtered_open_uses_exact_prompt_text_source(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    app.recent_filter_var.set("prompt-only-token-two")
    app.recent_listbox.selection_set(0)

    app.open_recent()

    assert app.prompt_output.get("1.0", "end-1c") == "prompt-only-token-two"
    assert app.background_var.get() == "bright window studio"
    assert controller.submit_calls == []


def test_phase_t_filtered_duplicate_uses_exact_original_source(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    app.recent_filter_var.set("prompt-only-token-two")
    app.recent_listbox.selection_set(0)

    app.duplicate_recent()

    assert app.background_var.get() == "bright window studio"
    assert app.camera_angle_var.get() == "rear three-quarter"
    assert app.requested_output_text.get("1.0", "end-1c") == "marketplace detail"
    assert app.prompt_output.get("1.0", "end-1c") == ""
    assert controller.submit_calls == []


def test_phase_t_filtered_copy_uses_exact_original_prompt(root, monkeypatch) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
    )
    clipboard = []
    monkeypatch.setattr(root, "clipboard_clear", lambda: clipboard.clear())
    monkeypatch.setattr(root, "clipboard_append", clipboard.append)
    app.recent_filter_var.set("prompt-only-token-two")
    app.recent_listbox.selection_set(0)

    app.copy_recent_prompt()

    assert clipboard == ["prompt-only-token-two"]
    assert controller.submit_calls == []


def test_phase_t_filtered_save_uses_exact_original_prompt(root) -> None:
    writes = []
    controller = _FakeController()

    app = GroundedPromptTkApplication(
        root,
        controller_factory=lambda **_kwargs: controller,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        settings_saver=lambda _value: None,
        workspace_loader=_phase_q_workspace,
        workspace_saver=lambda _state: None,
        save_dialog=lambda **_kwargs: r"C:\exports\phase-t.txt",
        file_writer=lambda path, payload: writes.append((path, payload)),
    )
    root.update_idletasks()
    app.recent_filter_var.set("prompt-only-token-two")
    app.recent_listbox.selection_set(0)

    app.save_recent_prompt()

    assert writes == [(r"C:\exports\phase-t.txt", b"prompt-only-token-two")]
    assert controller.submit_calls == []


def test_phase_t_filtered_favorite_uses_exact_original_source_index(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_q_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    app.recent_filter_var.set("prompt-only-token-two")
    source_index = app._visible_recent_indices[0]
    app.recent_listbox.selection_set(0)

    app.toggle_recent_selected_favorite()

    assert app._workspace["recent_prompts"][source_index]["favorite"] is True
    assert sum(1 for item in app._workspace["recent_prompts"] if item["favorite"]) == 1
    assert saved[-1]["recent_prompts"][source_index]["favorite"] is True


def test_phase_t_daily_use_guide_documents_prompt_text_preview_and_search() -> None:
    guide = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "rcis-grounded-prompt-daily-use.md"
    ).read_text(encoding="ascii").lower()

    for value in (
        "exact stored prompt text",
        "prompt text",
        "recent search also matches the exact stored prompt text",
        "temporary ui state",
        "not written to the persisted local workspace",
        "phase o general-user usability proof remains a separate unresolved governance activity",
    ):
        assert value in guide


# Phase U - Favorite-only workspace filters

def _phase_u_workspace():
    workspace = _phase_q_workspace()
    for item in workspace["recent_prompts"]:
        if item["prompt_text"] in (
            "beta prompt body",
            "prompt-only-token-one",
        ):
            item["favorite"] = True
    workspace = toggle_product_favorite(
        workspace,
        "alpha",
        "alpha-b",
    )
    workspace = toggle_product_favorite(
        workspace,
        "beta",
        "beta-a",
    )
    return workspace


def test_phase_u_recent_favorites_only_off_preserves_existing_order(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )

    assert app.recent_favorites_only_var.get() is False
    assert tuple(app.recent_listbox.get(0, "end")) == (
        "* Beta / Beta A",
        "Alpha / Alpha A",
        "* Alpha / Alpha A",
    )


def test_phase_u_recent_favorites_only_shows_exact_favorite_rows(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )

    app.recent_favorites_only_var.set(True)

    assert tuple(app.recent_listbox.get(0, "end")) == (
        "* Beta / Beta A",
        "* Alpha / Alpha A",
    )
    assert [
        app._workspace["recent_prompts"][index]["prompt_text"]
        for index in app._visible_recent_indices
    ] == [
        "beta prompt body",
        "prompt-only-token-one",
    ]


def test_phase_u_recent_favorites_only_and_text_search_compose_by_and(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )

    app.recent_favorites_only_var.set(True)
    app.recent_filter_var.set("alpha")

    assert tuple(app.recent_listbox.get(0, "end")) == (
        "* Alpha / Alpha A",
    )
    source_index = app._visible_recent_indices[0]
    assert (
        app._workspace["recent_prompts"][source_index]["prompt_text"]
        == "prompt-only-token-one"
    )


def test_phase_u_recent_favorite_only_preview_maps_exact_source(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )
    app.recent_favorites_only_var.set(True)
    app.recent_filter_var.set("alpha")

    _select_recent_visible_row(app, 0)
    source_index = app._visible_recent_indices[0]
    expected = app._workspace["recent_prompts"][source_index]

    assert app.recent_context_product_variant_var.get() == (
        app._display_product_variant(
            expected["product_id"],
            expected["variant_id"],
        )
    )
    assert app.recent_context_prompt_text_var.get() == expected["prompt_text"]


def test_phase_u_unfavorite_recent_removes_row_and_clears_preview(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    app.recent_favorites_only_var.set(True)
    app.recent_filter_var.set("alpha")
    _select_recent_visible_row(app, 0)
    source_index = app._visible_recent_indices[0]

    app.toggle_recent_selected_favorite()

    assert app._workspace["recent_prompts"][source_index]["favorite"] is False
    assert tuple(app.recent_listbox.get(0, "end")) == ()
    assert app.recent_context_product_variant_var.get() == ""
    assert app.recent_context_background_var.get() == ""
    assert app.recent_context_camera_angle_var.get() == ""
    assert app.recent_context_requested_output_var.get() == ""
    assert app.recent_context_prompt_text_var.get() == ""
    assert saved[-1]["recent_prompts"][source_index]["favorite"] is False


def test_phase_u_recent_favorite_only_filter_state_never_persists(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)

    app.recent_favorites_only_var.set(True)
    app.recent_filter_var.set("beta")
    app.recent_favorites_only_var.set(False)
    app.recent_filter_var.set("")

    assert len(saved) == baseline


def test_phase_u_products_favorites_only_off_preserves_existing_order(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )
    app.show_workspace_view("Products")

    assert app.product_favorites_only_var.get() is False
    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "Alpha / Alpha A",
        "* Alpha / Alpha B",
        "* Beta / Beta A",
    )


def test_phase_u_products_favorites_only_shows_exact_favorite_rows(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )
    app.show_workspace_view("Products")

    app.product_favorites_only_var.set(True)

    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "* Alpha / Alpha B",
        "* Beta / Beta A",
    )
    assert app._visible_product_variants == [
        ("alpha", "alpha-b"),
        ("beta", "beta-a"),
    ]


def test_phase_u_products_favorites_only_and_text_search_compose_by_and(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )
    app.show_workspace_view("Products")

    app.product_favorites_only_var.set(True)
    app.product_filter_var.set("beta")

    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "* Beta / Beta A",
    )
    assert app._visible_product_variants == [
        ("beta", "beta-a"),
    ]


def test_phase_u_product_use_under_favorite_only_maps_exact_pair(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )
    app.show_workspace_view("Products")
    app.product_favorites_only_var.set(True)
    app.product_filter_var.set("alpha b")
    app.product_variant_listbox.selection_set(0)

    app.use_selected_product_variant()

    assert app.product_var.get() == "alpha"
    assert app.variant_var.get() == "alpha-b"
    assert controller.submit_calls == []


def test_phase_u_product_default_under_favorite_only_maps_exact_pair(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
    )
    app.show_workspace_view("Products")
    app.product_favorites_only_var.set(True)
    app.product_filter_var.set("beta")
    app.product_variant_listbox.selection_set(0)

    app.set_selected_product_variant_default()

    assert app._workspace["default_product_variant"] == {
        "product_id": "beta",
        "variant_id": "beta-a",
    }


def test_phase_u_unfavorite_product_removes_row_while_filter_active(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    app.show_workspace_view("Products")
    app.product_favorites_only_var.set(True)
    app.product_filter_var.set("alpha b")
    app.product_variant_listbox.selection_set(0)

    app.toggle_selected_product_variant_favorite()

    assert app._workspace["product_favorites"] == [
        {"product_id": "beta", "variant_id": "beta-a"},
    ]
    assert tuple(app.product_variant_listbox.get(0, "end")) == ()
    assert saved[-1]["product_favorites"] == [
        {"product_id": "beta", "variant_id": "beta-a"},
    ]


def test_phase_u_product_favorite_only_filter_state_never_persists(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_u_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    app.show_workspace_view("Products")

    app.product_favorites_only_var.set(True)
    app.product_filter_var.set("alpha")
    app.product_favorites_only_var.set(False)
    app.product_filter_var.set("")

    assert len(saved) == baseline


def test_phase_u_daily_use_guide_documents_favorite_only_filters() -> None:
    guide = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "rcis-grounded-prompt-daily-use.md"
    ).read_text(encoding="ascii").lower()

    for value in (
        "favorites only",
        "recent and products",
        "logical and",
        "off by default",
        "temporary ui state",
        "not written to the persisted local workspace",
        "phase o general-user usability proof remains a separate unresolved governance activity",
    ):
        assert value in guide


# Phase V - Workspace filter reset and result counts

def _phase_v_workspace():
    workspace = _phase_u_workspace()
    workspace = save_preset(
        workspace,
        "Studio Alpha",
        {
            "product_id": "alpha",
            "variant_id": "alpha-b",
            "background": "studio",
            "camera_angle": "top",
            "requested_output": "alpha preset output",
        },
    )
    workspace = save_preset(
        workspace,
        "Outdoor Beta",
        {
            "product_id": "beta",
            "variant_id": "beta-a",
            "background": "outdoor",
            "camera_angle": "front",
            "requested_output": "beta preset output",
        },
    )
    return workspace


def test_phase_v_recent_result_count_matches_unfiltered_visible_rows(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )

    assert app.recent_result_count_var.get() == "3 results"
    assert len(app._visible_recent_indices) == 3
    assert app.recent_result_count_label.cget("textvariable")


def test_phase_v_recent_result_count_updates_under_text_filter(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )

    app.recent_filter_var.set("alpha")

    assert tuple(app.recent_listbox.get(0, "end")) == (
        "Alpha / Alpha A",
        "* Alpha / Alpha A",
    )
    assert app.recent_result_count_var.get() == "2 results"


def test_phase_v_recent_result_count_tracks_favorite_and_combined_filters(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )

    app.recent_favorites_only_var.set(True)
    assert app.recent_result_count_var.get() == "2 results"

    app.recent_filter_var.set("alpha")
    assert tuple(app.recent_listbox.get(0, "end")) == (
        "* Alpha / Alpha A",
    )
    assert app.recent_result_count_var.get() == "1 result"


def test_phase_v_recent_clear_resets_text_only_and_preserves_favorites(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.recent_favorites_only_var.set(True)
    app.recent_filter_var.set("beta")

    app.recent_filter_clear_button.invoke()

    assert app.recent_filter_var.get() == ""
    assert app.recent_favorites_only_var.get() is True
    assert tuple(app.recent_listbox.get(0, "end")) == (
        "* Beta / Beta A",
        "* Alpha / Alpha A",
    )
    assert app.recent_result_count_var.get() == "2 results"


def test_phase_v_recent_clear_never_persists_workspace(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    app.recent_filter_var.set("alpha")

    app.recent_filter_clear_button.invoke()
    app.recent_filter_clear_button.invoke()

    assert app.recent_filter_var.get() == ""
    assert len(saved) == baseline


def test_phase_v_preset_result_count_matches_and_tracks_text_filter(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )

    assert app.preset_result_count_var.get() == "2 results"

    app.preset_filter_var.set("outdoor")

    assert tuple(app.preset_listbox.get(0, "end")) == (
        "Outdoor Beta",
    )
    assert app.preset_result_count_var.get() == "1 result"
    assert app.preset_result_count_label.cget("textvariable")


def test_phase_v_preset_clear_restores_complete_original_order(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    original_rows = tuple(app.preset_listbox.get(0, "end"))
    app.preset_filter_var.set("outdoor")

    app.preset_filter_clear_button.invoke()

    assert app.preset_filter_var.get() == ""
    assert tuple(app.preset_listbox.get(0, "end")) == original_rows
    assert app.preset_result_count_var.get() == "2 results"


def test_phase_v_preset_clear_never_persists_workspace(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    app.preset_filter_var.set("studio")

    app.preset_filter_clear_button.invoke()
    app.preset_filter_clear_button.invoke()

    assert app.preset_filter_var.get() == ""
    assert len(saved) == baseline


def test_phase_v_product_result_count_matches_unfiltered_visible_rows(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.show_workspace_view("Products")

    assert app.product_result_count_var.get() == "3 results"
    assert len(app._visible_product_variants) == 3
    assert app.product_result_count_label.cget("textvariable")


def test_phase_v_product_result_count_updates_under_text_filter(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.show_workspace_view("Products")

    app.product_filter_var.set("beta")

    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "* Beta / Beta A",
    )
    assert app.product_result_count_var.get() == "1 result"


def test_phase_v_product_result_count_tracks_favorite_and_combined_filters(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.show_workspace_view("Products")

    app.product_favorites_only_var.set(True)
    assert app.product_result_count_var.get() == "2 results"

    app.product_filter_var.set("beta")
    assert app.product_result_count_var.get() == "1 result"
    assert app._visible_product_variants == [
        ("beta", "beta-a"),
    ]


def test_phase_v_product_clear_resets_text_only_and_preserves_favorites(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.show_workspace_view("Products")
    app.product_favorites_only_var.set(True)
    app.product_filter_var.set("beta")

    app.product_filter_clear_button.invoke()

    assert app.product_filter_var.get() == ""
    assert app.product_favorites_only_var.get() is True
    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "* Alpha / Alpha B",
        "* Beta / Beta A",
    )
    assert app.product_result_count_var.get() == "2 results"


def test_phase_v_product_clear_never_persists_workspace(root) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    app.show_workspace_view("Products")
    app.product_filter_var.set("alpha")

    app.product_filter_clear_button.invoke()
    app.product_filter_clear_button.invoke()

    assert app.product_filter_var.get() == ""
    assert len(saved) == baseline


def test_phase_v_clear_refreshes_preserve_exact_source_mappings(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )

    app.recent_filter_var.set("prompt-only-token-two")
    app.recent_filter_clear_button.invoke()
    app.recent_filter_var.set("prompt-only-token-two")
    _select_recent_visible_row(app, 0)
    source_index = app._visible_recent_indices[0]
    expected_recent = app._workspace["recent_prompts"][source_index]
    app.duplicate_recent()

    assert expected_recent["prompt_text"] == "prompt-only-token-two"
    assert app.background_var.get() == "bright window studio"
    assert app.camera_angle_var.get() == "rear three-quarter"

    app.show_workspace_view("Presets")
    app.preset_filter_var.set("outdoor")
    app.preset_filter_clear_button.invoke()
    app.preset_filter_var.set("outdoor")
    app.preset_listbox.selection_set(0)
    app.load_selected_preset()

    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == "beta-a"
    assert app.background_var.get() == "outdoor"

    app.show_workspace_view("Products")
    app.product_favorites_only_var.set(True)
    app.product_filter_var.set("beta")
    app.product_filter_clear_button.invoke()
    app.product_filter_var.set("beta")
    app.product_variant_listbox.selection_set(0)
    app.use_selected_product_variant()

    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == "beta-a"
    assert controller.submit_calls == []


def test_phase_v_daily_use_guide_documents_result_counts_and_clear_scope() -> None:
    guide = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "rcis-grounded-prompt-daily-use.md"
    ).read_text(encoding="ascii").lower()

    for value in (
        "visible result count",
        "clear",
        "recent, presets, and products",
        "text search / filter field",
        "does not change favorites only",
        "temporary ui state",
        "not written to the persisted local workspace",
        "phase o general-user usability proof remains a separate unresolved governance activity",
    ):
        assert value in guide


# Phase W - Workspace quick activation

def _phase_w_select(listbox, visible_index: int) -> None:
    listbox.selection_clear(0, "end")
    listbox.selection_set(visible_index)


def _phase_w_button(section, text: str):
    for child in section.winfo_children():
        if child.winfo_class() == "TButton" and child.cget("text") == text:
            return child
    raise AssertionError(f"button not found: {text}")


def test_phase_w_recent_enter_uses_existing_open_behavior(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    _phase_w_select(app.recent_listbox, 0)
    source_index = app._visible_recent_indices[0]
    expected = app._workspace["recent_prompts"][source_index]

    assert app.recent_listbox.bind("<Return>")
    app._activate_recent_primary(None)

    assert app.product_var.get() == expected["product_id"]
    assert app.variant_var.get() == expected["variant_id"]
    assert app.result_state_var.get() == "Saved prompt"
    assert (
        app.prompt_output.get("1.0", "end-1c")
        == expected["prompt_text"]
    )


def test_phase_w_recent_double_click_uses_existing_open_behavior(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    _phase_w_select(app.recent_listbox, 1)
    source_index = app._visible_recent_indices[1]
    expected = app._workspace["recent_prompts"][source_index]

    assert app.recent_listbox.bind("<Double-Button-1>")
    app._activate_recent_primary(None)

    assert app.background_var.get() == expected["background"]
    assert app.camera_angle_var.get() == expected["camera_angle"]
    assert (
        app.prompt_output.get("1.0", "end-1c")
        == expected["prompt_text"]
    )


def test_phase_w_recent_quick_activation_uses_exact_combined_filter_mapping(
    root,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.recent_favorites_only_var.set(True)
    app.recent_filter_var.set("alpha")
    assert tuple(app.recent_listbox.get(0, "end")) == (
        "* Alpha / Alpha A",
    )
    _phase_w_select(app.recent_listbox, 0)
    source_index = app._visible_recent_indices[0]
    expected = app._workspace["recent_prompts"][source_index]

    app._activate_recent_primary(None)

    assert expected["prompt_text"] == "prompt-only-token-one"
    assert (
        app.prompt_output.get("1.0", "end-1c")
        == expected["prompt_text"]
    )
    assert app.background_var.get() == expected["background"]


def test_phase_w_recent_enter_without_selection_is_noop_and_never_persists(
    root,
) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    app.recent_listbox.selection_clear(0, "end")

    app._activate_recent_primary(None)

    assert len(saved) == baseline
    assert app.workspace_view_var.get() == "New Prompt"
    assert app.result_state_var.get() == ""


def test_phase_w_preset_enter_uses_existing_load_behavior(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    _phase_w_select(app.preset_listbox, 0)
    source_index = app._visible_preset_indices[0]
    expected = app._workspace["presets"][source_index]

    assert app.preset_listbox.bind("<Return>")
    app._activate_preset_primary(None)

    assert app.product_var.get() == expected["product_id"]
    assert app.variant_var.get() == expected["variant_id"]
    assert app.background_var.get() == expected["background"]
    assert app.camera_angle_var.get() == expected["camera_angle"]


def test_phase_w_preset_double_click_uses_existing_load_behavior(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    _phase_w_select(app.preset_listbox, 1)
    source_index = app._visible_preset_indices[1]
    expected = app._workspace["presets"][source_index]

    assert app.preset_listbox.bind("<Double-Button-1>")
    app._activate_preset_primary(None)

    assert app.product_var.get() == expected["product_id"]
    assert app.variant_var.get() == expected["variant_id"]
    assert (
        app.requested_output_text.get("1.0", "end-1c")
        == expected["requested_output"]
    )


def test_phase_w_preset_quick_activation_uses_exact_filtered_mapping(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.preset_filter_var.set("outdoor")
    assert tuple(app.preset_listbox.get(0, "end")) == (
        "Outdoor Beta",
    )
    _phase_w_select(app.preset_listbox, 0)
    source_index = app._visible_preset_indices[0]
    expected = app._workspace["presets"][source_index]

    app._activate_preset_primary(None)

    assert expected["name"] == "Outdoor Beta"
    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == "beta-a"
    assert app.background_var.get() == expected["background"]


def test_phase_w_preset_enter_without_selection_is_noop_and_never_persists(
    root,
) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    app.preset_listbox.selection_clear(0, "end")

    app._activate_preset_primary(None)

    assert len(saved) == baseline
    assert app.workspace_view_var.get() == "New Prompt"
    assert app.product_var.get() == ""


def test_phase_w_product_enter_uses_existing_use_product_behavior(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.show_workspace_view("Products")
    _phase_w_select(app.product_variant_listbox, 0)
    expected = app._visible_product_variants[0]

    assert app.product_variant_listbox.bind("<Return>")
    app._activate_product_primary(None)

    assert (app.product_var.get(), app.variant_var.get()) == expected
    assert app.background_var.get() == ""
    assert app.camera_angle_var.get() == ""


def test_phase_w_product_double_click_uses_existing_use_product_behavior(
    root,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.show_workspace_view("Products")
    _phase_w_select(app.product_variant_listbox, 2)
    expected = app._visible_product_variants[2]

    assert app.product_variant_listbox.bind("<Double-Button-1>")
    app._activate_product_primary(None)

    assert (app.product_var.get(), app.variant_var.get()) == expected
    assert app.requested_output_text.get("1.0", "end-1c") == ""


def test_phase_w_product_quick_activation_uses_exact_combined_filter_mapping(
    root,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )
    app.show_workspace_view("Products")
    app.product_favorites_only_var.set(True)
    app.product_filter_var.set("beta")
    assert app._visible_product_variants == [
        ("beta", "beta-a"),
    ]
    _phase_w_select(app.product_variant_listbox, 0)

    app._activate_product_primary(None)

    assert app.product_var.get() == "beta"
    assert app.variant_var.get() == "beta-a"


def test_phase_w_product_enter_without_selection_is_noop_and_never_persists(
    root,
) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    app.show_workspace_view("Products")
    app.product_variant_listbox.selection_clear(0, "end")

    app._activate_product_primary(None)

    assert len(saved) == baseline
    assert app.workspace_view_var.get() == "Products"
    assert app.product_var.get() == ""


def test_phase_w_quick_activation_bindings_are_scoped_to_workspace_lists(
    root,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )

    for listbox in (
        app.recent_listbox,
        app.preset_listbox,
        app.product_variant_listbox,
    ):
        assert listbox.bind("<Return>")
        assert listbox.bind("<Double-Button-1>")

    assert root.bind("<Return>") == ""
    assert root.bind("<Double-Button-1>") == ""


def test_phase_w_existing_primary_action_buttons_remain_available(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_v_workspace,
    )

    recent_open = _phase_w_button(app.recent_section, "Open")
    preset_load = _phase_w_button(app.presets_section, "Load")
    product_use = _phase_w_button(app.products_section, "Use Product")

    assert recent_open.cget("command")
    assert preset_load.cget("command")
    assert product_use.cget("command")


def test_phase_w_daily_use_guide_documents_scoped_quick_activation() -> None:
    guide = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "rcis-grounded-prompt-daily-use.md"
    ).read_text(encoding="ascii").lower()

    for value in (
        "quick activation",
        "enter",
        "double-click",
        "recent",
        "presets",
        "products",
        "workspace lists",
        "same existing primary actions",
        "no global keyboard shortcut",
        "phase o general-user usability proof remains a separate unresolved governance activity",
    ):
        assert value in guide


# Phase R - Preset context preview and context search

def _phase_r_workspace():
    workspace = _phase_p_workspace()
    workspace = save_preset(
        workspace,
        "Window Alpha",
        {
            "product_id": "alpha",
            "variant_id": "alpha-b",
            "background": "bright window wall",
            "camera_angle": "rear three-quarter",
            "requested_output": "marketplace detail crop",
        },
    )
    return workspace


def _select_preset_visible_row(app, visible_index: int) -> None:
    app.preset_listbox.selection_clear(0, "end")
    app.preset_listbox.selection_set(visible_index)
    app._on_preset_selection_changed()


def test_phase_r_preset_preview_shows_exact_selected_source_item(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_r_workspace,
    )
    assert app.preset_listbox.bind("<<ListboxSelect>>")

    _select_preset_visible_row(app, 1)
    source_index = app._visible_preset_indices[1]
    expected = app._workspace["presets"][source_index]

    assert app.preset_context_name_var.get() == expected["name"]
    assert app.preset_context_product_variant_var.get() == (
        app._display_product_variant(
            expected["product_id"],
            expected["variant_id"],
        )
    )
    assert (
        app.preset_context_background_var.get()
        == expected["background"]
    )
    assert (
        app.preset_context_camera_angle_var.get()
        == expected["camera_angle"]
    )
    assert (
        app.preset_context_requested_output_var.get()
        == expected["requested_output"]
    )


def test_phase_r_filtered_preset_preview_maps_to_exact_original_item(
    root,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_r_workspace,
    )
    source_indices = [
        index
        for index, item in enumerate(app._workspace["presets"])
        if "alpha" in str(item["name"]).casefold()
    ]

    app.preset_filter_var.set("alpha")

    assert app._visible_preset_indices == source_indices
    assert tuple(app.preset_listbox.get(0, "end")) == tuple(
        app._workspace["presets"][index]["name"]
        for index in source_indices
    )

    target_source_index = next(
        index
        for index in source_indices
        if app._workspace["presets"][index]["name"] == "Window Alpha"
    )
    visible_index = app._visible_preset_indices.index(target_source_index)
    _select_preset_visible_row(app, visible_index)
    expected = app._workspace["presets"][target_source_index]

    assert app.preset_context_name_var.get() == expected["name"]
    assert (
        app.preset_context_background_var.get()
        == expected["background"]
    )
    assert (
        app.preset_context_camera_angle_var.get()
        == expected["camera_angle"]
    )
    assert (
        app.preset_context_requested_output_var.get()
        == expected["requested_output"]
    )


@pytest.mark.parametrize(
    ("query", "expected_names"),
    (
        ("OUTDOOR beta", ("Outdoor Beta",)),
        ("Alpha / Alpha B", ("Window Alpha", "Studio Alpha")),
        ("bright WINDOW", ("Window Alpha",)),
        ("rear THREE-quarter", ("Window Alpha",)),
        ("marketplace DETAIL crop", ("Window Alpha",)),
    ),
)
def test_phase_r_preset_context_search_matches_name_and_request_fields(
    root,
    query,
    expected_names,
) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_r_workspace,
    )

    app.preset_filter_var.set(query)

    assert tuple(app.preset_listbox.get(0, "end")) == expected_names
    assert tuple(
        app._workspace["presets"][index]["name"]
        for index in app._visible_preset_indices
    ) == expected_names


def test_phase_r_no_match_filter_clears_stale_preset_preview(root) -> None:
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_r_workspace,
    )
    _select_preset_visible_row(app, 0)
    assert app.preset_context_name_var.get()

    app.preset_filter_var.set("not-present-anywhere")

    assert tuple(app.preset_listbox.get(0, "end")) == ()
    assert app.preset_context_name_var.get() == ""
    assert app.preset_context_product_variant_var.get() == ""
    assert app.preset_context_background_var.get() == ""
    assert app.preset_context_camera_angle_var.get() == ""
    assert app.preset_context_requested_output_var.get() == ""


def test_phase_r_preset_preview_and_filter_never_persist_workspace(
    root,
) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_r_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)

    app.preset_filter_var.set("alpha")
    _select_preset_visible_row(app, 0)
    app.preset_filter_var.set("window")
    _select_preset_visible_row(app, 0)
    app.preset_filter_var.set("")

    assert len(saved) == baseline


def test_phase_r_filtered_load_uses_exact_selected_source_preset(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_r_workspace,
    )
    app.preset_filter_var.set("marketplace detail")
    _select_preset_visible_row(app, 0)
    source_index = app._visible_preset_indices[0]
    expected = dict(app._workspace["presets"][source_index])

    app.load_selected_preset()

    assert app.product_var.get() == expected["product_id"]
    assert app.variant_var.get() == expected["variant_id"]
    assert app.background_var.get() == expected["background"]
    assert app.camera_angle_var.get() == expected["camera_angle"]
    assert (
        app.requested_output_text.get("1.0", "end-1c")
        == expected["requested_output"]
    )
    assert controller.submit_calls == []


def test_phase_r_filtered_delete_uses_exact_selected_source_preset(
    root,
) -> None:
    saved = []
    app, _, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_r_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    before_names = [
        item["name"]
        for item in app._workspace["presets"]
    ]

    app.preset_filter_var.set("bright window")
    _select_preset_visible_row(app, 0)
    selected_source_index = app._visible_preset_indices[0]
    expected_remaining_names = [
        name
        for index, name in enumerate(before_names)
        if index != selected_source_index
    ]

    app.delete_selected_preset()

    assert [
        item["name"]
        for item in app._workspace["presets"]
    ] == expected_remaining_names
    assert tuple(app.preset_listbox.get(0, "end")) == ()
    assert app.preset_context_name_var.get() == ""
    assert saved


def test_phase_r_daily_use_guide_documents_preset_preview_and_search() -> None:
    guide = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "rcis-grounded-prompt-daily-use.md"
    ).read_text(encoding="ascii").lower()

    for value in (
        "select a preset to see its read-only preset name, product / variant, background, camera angle, and requested output context",
        "presets matches the preset name plus product / variant, background, camera angle, and requested output",
        "selected preset context preview is temporary ui state",
        "it is not written to the persisted local workspace",
        "phase o general-user usability proof remains a separate unresolved governance activity",
    ):
        assert value in guide

# Phase Y - selected Recent history removal

def _phase_y_workspace():
    workspace = empty_workspace()
    workspace = record_recent_prompt(
        workspace,
        {
            "product_id": "gamma",
            "variant_id": "gamma-a",
            "background": "gamma background",
            "camera_angle": "top",
            "requested_output": "gamma output",
        },
        "gamma stored prompt",
    )
    workspace = record_recent_prompt(
        workspace,
        {
            "product_id": "alpha",
            "variant_id": "alpha-a",
            "background": "alpha background",
            "camera_angle": "front",
            "requested_output": "alpha output",
        },
        "alpha stored prompt",
    )
    workspace = record_recent_prompt(
        workspace,
        {
            "product_id": "beta",
            "variant_id": "beta-a",
            "background": "beta background",
            "camera_angle": "side",
            "requested_output": "beta output",
        },
        "beta stored prompt",
    )
    workspace["recent_prompts"][0]["favorite"] = True
    workspace["recent_prompts"][1]["favorite"] = True
    return workspace


def test_phase_y_unfiltered_remove_button_deletes_exact_selected_recent_and_persists_once(root) -> None:
    saved = []
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_y_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    original = clone_workspace(app._workspace)
    app.recent_listbox.selection_set(1)
    app._refresh_recent_context_preview()
    assert app.recent_context_prompt_text_var.get() == "alpha stored prompt"

    _phase_w_button(app.recent_section, "Remove").invoke()

    assert [item["product_id"] for item in app._workspace["recent_prompts"]] == [
        original["recent_prompts"][0]["product_id"],
        original["recent_prompts"][2]["product_id"],
    ]
    assert len(saved) == baseline + 1
    assert app.recent_result_count_var.get() == "2 results"
    assert app.recent_context_product_variant_var.get() == ""
    assert app.recent_context_prompt_text_var.get() == ""
    assert controller.submit_calls == []


def test_phase_y_text_filtered_remove_maps_exact_source_and_refreshes_preview_and_count(root) -> None:
    saved = []
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_y_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    app.recent_filter_var.set("alpha")
    assert app._visible_recent_indices == [1]
    app.recent_listbox.selection_set(0)
    app._refresh_recent_context_preview()
    assert app.recent_context_prompt_text_var.get() == "alpha stored prompt"

    app.delete_selected_recent()

    assert [item["product_id"] for item in app._workspace["recent_prompts"]] == [
        "beta",
        "gamma",
    ]
    assert app.recent_filter_var.get() == "alpha"
    assert tuple(app.recent_listbox.get(0, "end")) == ()
    assert app.recent_result_count_var.get() == "0 results"
    assert app.recent_context_prompt_text_var.get() == ""
    assert len(saved) == baseline + 1
    assert controller.submit_calls == []


def test_phase_y_favorites_and_text_filtered_remove_maps_exact_favorite_source_without_disturbing_others(root) -> None:
    saved = []
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_y_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    before = clone_workspace(app._workspace)
    app.recent_favorites_only_var.set(True)
    app.recent_filter_var.set("alpha")
    assert app._visible_recent_indices == [1]
    app.recent_listbox.selection_set(0)

    app.delete_selected_recent()

    assert app._workspace["recent_prompts"] == [
        before["recent_prompts"][0],
        before["recent_prompts"][2],
    ]
    assert app.recent_favorites_only_var.get() is True
    assert app.recent_filter_var.get() == "alpha"
    assert app.recent_result_count_var.get() == "0 results"
    assert len(saved) == baseline + 1
    assert controller.submit_calls == []


def test_phase_y_remove_without_selection_is_noop_and_never_persists(root) -> None:
    saved = []
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
        workspace_loader=_phase_y_workspace,
        workspace_saver=lambda state: saved.append(clone_workspace(state)),
    )
    baseline = len(saved)
    before = clone_workspace(app._workspace)

    _phase_w_button(app.recent_section, "Remove").invoke()

    assert app._workspace == before
    assert len(saved) == baseline
    assert controller.submit_calls == []


def test_phase_y_daily_use_guide_documents_recent_removal_local_workspace_boundary() -> None:
    guide = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "rcis-grounded-prompt-daily-use.md"
    ).read_text(encoding="ascii").lower()

    for value in (
        "remove the selected recent item from local workspace history",
        "removing a recent item changes only local operator workspace history",
        "it does not delete governed evidence",
        "enter and double-click still use open",
        "phase o general-user usability proof remains a separate unresolved governance activity",
    ):
        assert value in guide

