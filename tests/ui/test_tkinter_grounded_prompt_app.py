from __future__ import annotations

import inspect
import tkinter as tk

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
    assert tuple(app.product_combo["values"]) == ("alpha", "beta")
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


def test_phase_j_products_lists_canonical_ids_and_sets_explicit_default_without_catalog_change(root) -> None:
    app, controller, _ = _phase_j_app(
        root,
        settings_loader=lambda: r"C:\pilot\remembered-intake",
    )
    before_products = controller.product_ids
    app.show_workspace_view("Products")

    assert tuple(app.product_variant_listbox.get(0, "end")) == (
        "alpha / alpha-a",
        "alpha / alpha-b",
        "beta / beta-a",
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
    assert app.default_status_var.get() == "alpha / alpha-a"

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
    assert "workspace disk unavailable" in app.workspace_feedback_var.get()
