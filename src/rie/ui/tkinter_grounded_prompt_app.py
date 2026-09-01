"""Tkinter presentation adapter for the RCIS grounded prompt UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable

from rie.ui.grounded_prompt_ui_controller import (
    GroundedPromptUiController,
    GroundedPromptUiResult,
)
from rie.ui.local_operator_settings import (
    load_remembered_intake_root,
    save_remembered_intake_root,
)
from rie.ui.local_operator_workspace import (
    clear_default_product_variant,
    clone_workspace,
    delete_preset,
    empty_workspace,
    load_workspace,
    record_recent_prompt,
    save_preset,
    save_workspace,
    set_default_product_variant,
    set_last_request,
    toggle_product_favorite,
    toggle_recent_favorite,
)


WINDOW_TITLE = "RCIS Grounded Prompt"


def _write_prompt_bytes(path: str, payload: bytes) -> object:
    with open(path, "wb") as stream:
        return stream.write(payload)


class GroundedPromptTkApplication:
    """Local product-facing Tkinter UI for grounded prompt generation."""

    def __init__(
        self,
        root: tk.Misc,
        *,
        controller_factory: Callable[..., GroundedPromptUiController] = (
            GroundedPromptUiController.from_intake_root
        ),
        directory_picker: Callable[[], str] = filedialog.askdirectory,
        save_dialog: Callable[..., str] = filedialog.asksaveasfilename,
        file_writer: Callable[[str, bytes], object] = _write_prompt_bytes,
        settings_loader: Callable[[], str | None] = (
            load_remembered_intake_root
        ),
        settings_saver: Callable[[str], object] = (
            save_remembered_intake_root
        ),
        workspace_loader: Callable[[], dict] = load_workspace,
        workspace_saver: Callable[[dict], object] = save_workspace,
    ) -> None:
        self.root = root
        self._controller_factory = controller_factory
        self._directory_picker = directory_picker
        self._save_dialog = save_dialog
        self._file_writer = file_writer
        self._settings_loader = settings_loader
        self._settings_saver = settings_saver
        self._workspace_loader = workspace_loader
        self._workspace_saver = workspace_saver
        self._controller: GroundedPromptUiController | None = None
        self._data_source_visible = True
        self._details_visible = False
        self._workspace_view = "New Prompt"
        self._workspace_restore_attempted = False
        self._suspend_workspace_persistence = True
        self.root.winfo_toplevel().title(WINDOW_TITLE)

        self.intake_root_var = tk.StringVar(master=root, value="")
        self.product_var = tk.StringVar(master=root, value="")
        self.variant_var = tk.StringVar(master=root, value="")
        self.product_label_var = tk.StringVar(master=root, value="")
        self.variant_label_var = tk.StringVar(master=root, value="")
        self._product_label_to_id: dict[str, str] = {}
        self._product_id_to_label: dict[str, str] = {}
        self._variant_label_to_id: dict[str, str] = {}
        self._variant_id_to_label: dict[str, str] = {}
        self.background_var = tk.StringVar(master=root, value="")
        self.camera_angle_var = tk.StringVar(master=root, value="")
        self.error_var = tk.StringVar(master=root, value="")
        self.technical_error_var = tk.StringVar(master=root, value="")
        self.copy_feedback_var = tk.StringVar(master=root, value="")
        self._retry_action: str | None = None
        self._retry_copy_text = ""
        self.result_state_var = tk.StringVar(master=root, value="")
        self.bridge_status_var = tk.StringVar(master=root, value="")
        self.exact_six_status_var = tk.StringVar(master=root, value="")
        self.binding_status_var = tk.StringVar(master=root, value="")
        self.grounding_status_var = tk.StringVar(master=root, value="")
        self.workspace_feedback_var = tk.StringVar(master=root, value="")
        self.workspace_view_var = tk.StringVar(master=root, value="New Prompt")
        self.preset_name_var = tk.StringVar(master=root, value="")
        self.default_status_var = tk.StringVar(master=root, value="No default")

        try:
            self._workspace = clone_workspace(self._workspace_loader())
        except Exception as exc:
            self._workspace = empty_workspace()
            self.workspace_feedback_var.set(
                "Local workspace could not be loaded. Starting with an empty workspace."
            )
            self.technical_error_var.set(str(exc))

        self._build_widgets()
        self.retry_button = ttk.Button(
            root,
            text="Try Again",
            command=self.retry_last_action,
        )
        self.retry_button.place(relx=0.02, rely=0.98, anchor="sw")
        self.retry_button.place_forget()
        self.open_settings_button = ttk.Button(
            root,
            text="Open Settings",
            command=self.open_recovery_settings,
        )
        self.open_settings_button.place(relx=0.18, rely=0.98, anchor="sw")
        self.open_settings_button.place_forget()
        self.copy_feedback_label = ttk.Label(
            root,
            textvariable=self.copy_feedback_var,
        )
        self.copy_feedback_label.place(relx=0.98, rely=0.98, anchor="se")

        self._bind_result_invalidation()
        self._suspend_workspace_persistence = False
        if self._restore_remembered_foundation():
            self._set_data_source_visible(False)
        else:
            self._set_data_source_visible(True)
        self._refresh_workspace_views()

    def _bind_result_invalidation(self) -> None:
        for variable in (
            self.intake_root_var,
            self.product_var,
            self.variant_var,
            self.background_var,
            self.camera_angle_var,
        ):
            variable.trace_add(
                "write",
                self._on_result_defining_variable_changed,
            )
        self.requested_output_text.bind(
            "<<Modified>>",
            self._on_requested_output_modified,
        )
        self.requested_output_text.edit_modified(False)

    def _on_result_defining_variable_changed(self, *_args: object) -> None:
        self._clear_result_output()
        self._persist_visible_request()

    def _on_requested_output_modified(self, _event: object = None) -> None:
        if not self.requested_output_text.edit_modified():
            return
        self._clear_result_output()
        self.requested_output_text.edit_modified(False)
        self._persist_visible_request()

    def _build_widgets(self) -> None:
        self.navigation_frame = ttk.Frame(
            self.root,
            padding=(12, 12, 12, 0),
        )
        self.navigation_frame.grid(
            row=0,
            column=0,
            sticky="ew",
        )
        self.navigation_buttons = {}
        for column, label in enumerate(
            ("New Prompt", "Recent", "Presets", "Products", "Settings")
        ):
            button = ttk.Button(
                self.navigation_frame,
                text=label,
                command=lambda value=label: self.show_workspace_view(value),
            )
            button.grid(
                row=0,
                column=column,
                padx=(0, 6),
            )
            self.navigation_buttons[label] = button

        frame = ttk.Frame(self.root, padding=12)
        frame.grid(row=1, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)

        self.primary_heading = ttk.Label(
            frame,
            text="Create a Grounded Product Prompt",
        )
        self.primary_heading.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 8),
        )
        self.data_source_toggle_button = ttk.Button(
            frame,
            text="Data Source",
            command=self.toggle_data_source,
        )
        self.data_source_toggle_button.grid(
            row=0,
            column=2,
            sticky="e",
            pady=(0, 8),
        )

        self.data_source_frame = ttk.LabelFrame(
            frame,
            text="Data Source",
            padding=8,
        )
        self.data_source_frame.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(0, 8),
        )
        self.data_source_frame.columnconfigure(1, weight=1)
        ttk.Label(self.data_source_frame, text="Intake Root").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=3,
        )
        self.intake_root_entry = ttk.Entry(
            self.data_source_frame,
            textvariable=self.intake_root_var,
        )
        self.intake_root_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=3,
        )
        self.intake_action_frame = ttk.Frame(self.data_source_frame)
        self.intake_action_frame.grid(
            row=0,
            column=2,
            padx=(8, 0),
            pady=3,
        )
        self.browse_button = ttk.Button(
            self.intake_action_frame,
            text="Browse...",
            command=self.browse_intake_root,
        )
        self.browse_button.grid(row=0, column=0)
        self.load_button = ttk.Button(
            self.intake_action_frame,
            text="Load Foundation",
            command=self.load_foundation,
        )
        self.load_button.grid(row=0, column=1, padx=(8, 0))

        ttk.Label(frame, text="Product").grid(
            row=2,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=3,
        )
        self.product_combo = ttk.Combobox(
            frame,
            textvariable=self.product_label_var,
            values=(),
            state="disabled",
        )
        self.product_combo.grid(
            row=2,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=3,
        )
        self.product_combo.bind(
            "<<ComboboxSelected>>",
            self._on_product_label_selected,
        )

        ttk.Label(frame, text="Variant").grid(
            row=3,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=3,
        )
        self.variant_combo = ttk.Combobox(
            frame,
            textvariable=self.variant_label_var,
            values=(),
            state="disabled",
        )
        self.variant_combo.grid(
            row=3,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=3,
        )

        self.variant_combo.bind(
            "<<ComboboxSelected>>",
            self._on_variant_label_selected,
        )
        ttk.Label(frame, text="Background").grid(
            row=4,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=3,
        )
        self.background_entry = ttk.Entry(
            frame,
            textvariable=self.background_var,
        )
        self.background_entry.grid(
            row=4,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=3,
        )

        ttk.Label(frame, text="Camera Angle").grid(
            row=5,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=3,
        )
        self.camera_angle_entry = ttk.Entry(
            frame,
            textvariable=self.camera_angle_var,
        )
        self.camera_angle_entry.grid(
            row=5,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=3,
        )

        ttk.Label(frame, text="Requested Output").grid(
            row=6,
            column=0,
            sticky="nw",
            padx=(0, 8),
            pady=3,
        )
        self.requested_output_text = tk.Text(
            frame,
            height=3,
            width=50,
        )
        self.requested_output_text.grid(
            row=6,
            column=1,
            columnspan=2,
            sticky="ew",
            pady=3,
        )

        self.generate_button = ttk.Button(
            frame,
            text="Generate Prompt",
            command=self.submit,
        )
        self.generate_button.grid(
            row=7,
            column=1,
            columnspan=2,
            sticky="e",
            pady=(8, 4),
        )
        self.submit_button = self.generate_button

        self.result_state_label = ttk.Label(
            frame,
            textvariable=self.result_state_var,
        )
        self.result_state_label.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 4),
        )
        self.details_toggle_button = ttk.Button(
            frame,
            text="View Details",
            command=self.toggle_details,
        )
        self.details_toggle_button.grid(
            row=8,
            column=2,
            sticky="e",
            pady=(6, 4),
        )

        self.details_frame = ttk.LabelFrame(
            frame,
            text="Verification Details",
            padding=8,
        )
        self.details_frame.grid(
            row=9,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(0, 6),
        )
        self.details_frame.columnconfigure(1, weight=1)
        status_rows = (
            ("Bridge materialization", self.bridge_status_var),
            ("Exact-six materialization", self.exact_six_status_var),
            ("Binding", self.binding_status_var),
            ("Grounding", self.grounding_status_var),
            ("Technical error", self.technical_error_var),
        )
        for row, (label, variable) in enumerate(status_rows):
            ttk.Label(self.details_frame, text=label).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 8),
            )
            ttk.Label(
                self.details_frame,
                textvariable=variable,
            ).grid(
                row=row,
                column=1,
                sticky="w",
            )

        ttk.Label(frame, text="Generated Prompt").grid(
            row=10,
            column=0,
            sticky="nw",
            padx=(0, 8),
            pady=3,
        )
        self.prompt_output = tk.Text(
            frame,
            height=12,
            width=70,
            state="disabled",
        )
        self.prompt_output.grid(
            row=10,
            column=1,
            columnspan=2,
            sticky="nsew",
            pady=3,
        )
        frame.rowconfigure(10, weight=1)

        self.result_actions_frame = ttk.Frame(frame)
        self.result_actions_frame.grid(
            row=11,
            column=1,
            columnspan=2,
            sticky="e",
            pady=(4, 0),
        )
        self.copy_prompt_button = ttk.Button(
            self.result_actions_frame,
            text="Copy Prompt",
            command=self.copy_prompt,
        )
        self.copy_prompt_button.grid(row=0, column=0)
        self.save_prompt_button = ttk.Button(
            self.result_actions_frame,
            text="Save prompt...",
            command=self.save_prompt,
        )
        self.save_prompt_button.grid(
            row=1,
            column=0,
            pady=(6, 0),
        )
        self.new_request_button = ttk.Button(
            self.result_actions_frame,
            text="New Request",
            command=self.new_request,
        )
        self.new_request_button.grid(
            row=0,
            column=1,
            padx=(8, 0),
        )

        self.error_label = ttk.Label(
            frame,
            textvariable=self.error_var,
        )
        self.error_label.grid(
            row=12,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(6, 0),
        )
        self.workspace_feedback_label = ttk.Label(
            frame,
            textvariable=self.workspace_feedback_var,
        )
        self.workspace_feedback_label.grid(
            row=13,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(4, 0),
        )

        self.workspace_panel = ttk.LabelFrame(
            self.root,
            text=self.workspace_view_var.get(),
            padding=10,
        )
        self.workspace_panel.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 12),
        )
        self.workspace_panel.columnconfigure(0, weight=1)

        self.recent_section = ttk.Frame(self.workspace_panel)
        self.recent_section.grid(row=0, column=0, sticky="ew")
        self.recent_section.columnconfigure(0, weight=1)
        self.recent_listbox = tk.Listbox(
            self.recent_section,
            height=6,
            exportselection=False,
        )
        self.recent_listbox.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="ew",
        )
        ttk.Button(
            self.recent_section,
            text="Open",
            command=self.open_recent,
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Button(
            self.recent_section,
            text="Duplicate",
            command=self.duplicate_recent,
        ).grid(row=1, column=1, sticky="w", pady=(6, 0))
        ttk.Button(
            self.recent_section,
            text="Copy Prompt",
            command=self.copy_recent_prompt,
        ).grid(row=1, column=2, sticky="w", pady=(6, 0))
        ttk.Button(
            self.recent_section,
            text="Save selected prompt...",
            command=self.save_recent_prompt,
        ).grid(row=2, column=2, sticky="w", pady=(6, 0))
        ttk.Button(
            self.recent_section,
            text="Favorite / Unfavorite",
            command=self.toggle_recent_selected_favorite,
        ).grid(row=1, column=3, sticky="w", pady=(6, 0))

        self.presets_section = ttk.Frame(self.workspace_panel)
        self.presets_section.grid(row=0, column=0, sticky="ew")
        self.presets_section.columnconfigure(1, weight=1)
        ttk.Label(
            self.presets_section,
            text="Preset Name",
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.preset_name_entry = ttk.Entry(
            self.presets_section,
            textvariable=self.preset_name_var,
        )
        self.preset_name_entry.grid(
            row=0,
            column=1,
            sticky="ew",
        )
        self.preset_listbox = tk.Listbox(
            self.presets_section,
            height=6,
            exportselection=False,
        )
        self.preset_listbox.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="ew",
            pady=(6, 0),
        )
        ttk.Button(
            self.presets_section,
            text="Save Current",
            command=self.save_current_preset,
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Button(
            self.presets_section,
            text="Load",
            command=self.load_selected_preset,
        ).grid(row=2, column=1, sticky="w", pady=(6, 0))
        ttk.Button(
            self.presets_section,
            text="Delete",
            command=self.delete_selected_preset,
        ).grid(row=2, column=2, sticky="w", pady=(6, 0))

        self.products_section = ttk.Frame(self.workspace_panel)
        self.products_section.grid(row=0, column=0, sticky="ew")
        self.products_section.columnconfigure(0, weight=1)
        self.product_variant_listbox = tk.Listbox(
            self.products_section,
            height=6,
            exportselection=False,
        )
        self.product_variant_listbox.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
        )
        ttk.Button(
            self.products_section,
            text="Use Product",
            command=self.use_selected_product_variant,
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Button(
            self.products_section,
            text="Set as Default",
            command=self.set_selected_product_variant_default,
        ).grid(row=1, column=1, sticky="w", pady=(6, 0))
        ttk.Button(
            self.products_section,
            text="Favorite / Unfavorite",
            command=self.toggle_selected_product_variant_favorite,
        ).grid(row=1, column=2, sticky="w", pady=(6, 0))

        self.settings_section = ttk.Frame(self.workspace_panel)
        self.settings_section.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            self.settings_section,
            text="Default Product / Variant",
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(
            self.settings_section,
            textvariable=self.default_status_var,
        ).grid(row=0, column=1, sticky="w")
        self.settings_data_source_button = ttk.Button(
            self.settings_section,
            text="Data Source",
            command=self.toggle_data_source,
        )
        self.settings_data_source_button.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(6, 0),
        )
        self.clear_default_button = ttk.Button(
            self.settings_section,
            text="Clear Default",
            command=self.clear_default_product_variant,
        )
        self.clear_default_button.grid(
            row=1,
            column=1,
            sticky="w",
            pady=(6, 0),
        )

        self._set_details_visible(False)
        self._set_workspace_view("New Prompt")

    def _set_product_options(self, options: tuple) -> None:
        self._product_label_to_id = {
            option.label: option.product_id
            for option in options
        }
        self._product_id_to_label = {
            option.product_id: option.label
            for option in options
        }
        self.product_combo.configure(
            values=tuple(option.label for option in options),
        )

    def _set_variant_options(self, options: tuple) -> None:
        self._variant_label_to_id = {
            option.label: option.variant_id
            for option in options
        }
        self._variant_id_to_label = {
            option.variant_id: option.label
            for option in options
        }
        self.variant_combo.configure(
            values=tuple(option.label for option in options),
        )

    def _label_for_product_id(self, product_id: str) -> str | None:
        return self._product_id_to_label.get(product_id)

    def _label_for_variant_id(
        self,
        product_id: str,
        variant_id: str,
    ) -> str | None:
        if self._controller is None:
            return None
        try:
            options = self._controller.variant_options_for_product(
                product_id
            )
        except Exception:
            return None
        for option in options:
            if option.variant_id == variant_id:
                return option.label
        return None

    def _display_product_variant(
        self,
        product_id: str,
        variant_id: str,
    ) -> str:
        product_label = self._label_for_product_id(product_id)
        variant_label = self._label_for_variant_id(
            product_id,
            variant_id,
        )
        if product_label is None or variant_label is None:
            return "Unavailable saved selection"
        return product_label + " / " + variant_label

    def _on_product_label_selected(self, _event: object = None) -> None:
        label = self.product_label_var.get()
        product_id = self._product_label_to_id.get(label)
        if product_id is None:
            self.product_var.set("")
            self.variant_var.set("")
            self.variant_label_var.set("")
            self._set_variant_options(())
            self.variant_combo.configure(state="disabled")
            self._show_friendly_error(
                "RCIS couldn't resolve the selected product. Reload the data source and try again.",
                technical=(
                    "selected product label is not present in the loaded "
                    "catalog adapter"
                ),
            )
            return
        self.product_var.set(product_id)
        self.refresh_variants()

    def _on_variant_label_selected(self, _event: object = None) -> None:
        label = self.variant_label_var.get()
        variant_id = self._variant_label_to_id.get(label)
        if variant_id is None:
            self.variant_var.set("")
            self._show_friendly_error(
                "RCIS couldn't resolve the selected variant. Choose it again.",
                technical=(
                    "selected variant label is not present in the loaded "
                    "catalog adapter"
                ),
            )
            return
        self.variant_var.set(variant_id)

    def _visible_request(self) -> dict:
        return {
            "product_id": self.product_var.get(),
            "variant_id": self.variant_var.get(),
            "background": self.background_var.get(),
            "camera_angle": self.camera_angle_var.get(),
            "requested_output": self.requested_output_text.get(
                "1.0",
                "end-1c",
            ),
        }

    def _save_workspace_state(self) -> bool:
        try:
            self._workspace_saver(clone_workspace(self._workspace))
        except Exception as exc:
            self.workspace_feedback_var.set(
                "Local workspace could not be saved. Your current prompt is still available."
            )
            self.technical_error_var.set(str(exc))
            return False
        self.workspace_feedback_var.set("")
        return True

    def _persist_visible_request(self) -> None:
        if self._suspend_workspace_persistence:
            return
        if self._controller is None:
            return
        self._workspace = set_last_request(
            self._workspace,
            self._visible_request(),
        )
        self._save_workspace_state()

    def _valid_product_variant(
        self,
        product_id: str,
        variant_id: str,
    ) -> bool:
        if self._controller is None:
            return False
        if product_id not in self._controller.product_ids:
            return False
        try:
            variants = self._controller.variant_ids_for_product(
                product_id
            )
        except Exception:
            return False
        return variant_id in variants

    def _hydrate_request(
        self,
        request: dict,
        *,
        show_prompt: str = "",
    ) -> bool:
        product_id = str(request.get("product_id", ""))
        variant_id = str(request.get("variant_id", ""))
        if product_id or variant_id:
            if not self._valid_product_variant(
                product_id,
                variant_id,
            ):
                return False
        self._suspend_workspace_persistence = True
        try:
            self.product_var.set(product_id)
            self.product_label_var.set(
                self._product_id_to_label.get(product_id, "")
                if product_id
                else ""
            )
            if product_id and self._controller is not None:
                variant_options = (
                    self._controller.variant_options_for_product(
                        product_id
                    )
                )
                self._set_variant_options(variant_options)
                self.variant_combo.configure(state="readonly")
            else:
                self._set_variant_options(())
                self.variant_combo.configure(state="disabled")
            self.variant_var.set(variant_id)
            self.variant_label_var.set(
                self._variant_id_to_label.get(variant_id, "")
                if variant_id
                else ""
            )
            self.background_var.set(
                str(request.get("background", ""))
            )
            self.camera_angle_var.set(
                str(request.get("camera_angle", ""))
            )
            self.requested_output_text.delete("1.0", "end")
            self.requested_output_text.insert(
                "1.0",
                str(request.get("requested_output", "")),
            )
            self.requested_output_text.edit_modified(False)
        finally:
            self._suspend_workspace_persistence = False
        self._clear_result_output()
        if show_prompt:
            self._set_prompt_output(show_prompt)
            self.result_state_var.set("Saved prompt")
        return True

    def _restore_workspace_request_once(self) -> None:
        if self._workspace_restore_attempted:
            return
        self._workspace_restore_attempted = True
        request = self._workspace.get("last_request")
        if not isinstance(request, dict):
            return
        self._hydrate_request(request)

    def _apply_valid_default(self) -> bool:
        value = self._workspace.get("default_product_variant")
        if not isinstance(value, dict):
            return False
        product_id = str(value.get("product_id", ""))
        variant_id = str(value.get("variant_id", ""))
        if not self._valid_product_variant(
            product_id,
            variant_id,
        ):
            return False
        self.product_var.set(product_id)
        self.product_label_var.set(
            self._product_id_to_label.get(product_id, "")
        )
        variant_options = self._controller.variant_options_for_product(
            product_id
        )
        self._set_variant_options(variant_options)
        self.variant_combo.configure(state="readonly")
        self.variant_var.set(variant_id)
        self.variant_label_var.set(
            self._variant_id_to_label.get(variant_id, "")
        )
        return True

    def _record_successful_prompt(
        self,
        result: GroundedPromptUiResult,
    ) -> None:
        request = self._visible_request()
        self._workspace = set_last_request(
            self._workspace,
            request,
        )
        self._workspace = record_recent_prompt(
            self._workspace,
            request,
            result.prompt_text,
        )
        self._save_workspace_state()
        self._refresh_workspace_views()

    def _selected_index(self, listbox: tk.Listbox) -> int | None:
        selected = listbox.curselection()
        if not selected:
            return None
        return int(selected[0])

    def _refresh_recent_workspace(self) -> None:
        self.recent_listbox.delete(0, "end")
        for item in self._workspace["recent_prompts"]:
            favorite = "* " if item.get("favorite") else ""
            self.recent_listbox.insert(
                "end",
                favorite
                + self._display_product_variant(
                    item["product_id"],
                    item["variant_id"],
                ),
            )

    def _refresh_presets_workspace(self) -> None:
        self.preset_listbox.delete(0, "end")
        for item in self._workspace["presets"]:
            self.preset_listbox.insert("end", item["name"])

    def _refresh_products_workspace(self) -> None:
        if not hasattr(self, "product_variant_listbox"):
            return
        self.product_variant_listbox.delete(0, "end")
        if self._controller is None:
            return
        favorites = {
            (item["product_id"], item["variant_id"])
            for item in self._workspace["product_favorites"]
        }
        for product_option in self._controller.product_options:
            product_id = product_option.product_id
            try:
                variants = self._controller.variant_options_for_product(
                    product_id
                )
            except Exception:
                continue
            for variant_option in variants:
                variant_id = variant_option.variant_id
                marker = "* " if (
                    product_id,
                    variant_id,
                ) in favorites else ""
                self.product_variant_listbox.insert(
                    "end",
                    marker
                    + product_option.label
                    + " / "
                    + variant_option.label,
                )

    def _refresh_default_status(self) -> None:
        value = self._workspace.get("default_product_variant")
        if isinstance(value, dict):
            self.default_status_var.set(
                self._display_product_variant(
                    value["product_id"],
                    value["variant_id"],
                )
            )
        else:
            self.default_status_var.set("No default")

    def _refresh_workspace_views(self) -> None:
        self._refresh_recent_workspace()
        self._refresh_presets_workspace()
        self._refresh_products_workspace()
        self._refresh_default_status()

    def _set_workspace_view(self, name: str) -> None:
        self._workspace_view = name
        self.workspace_view_var.set(name)
        self.workspace_panel.configure(text=name)
        for section in (
            self.recent_section,
            self.presets_section,
            self.products_section,
            self.settings_section,
        ):
            section.grid_remove()
        if name == "New Prompt":
            self.workspace_panel.grid_remove()
            return
        self.workspace_panel.grid()
        section = {
            "Recent": self.recent_section,
            "Presets": self.presets_section,
            "Products": self.products_section,
            "Settings": self.settings_section,
        }.get(name)
        if section is not None:
            section.grid()
        if name == "Settings":
            self._set_data_source_visible(True)

    def show_workspace_view(self, name: str) -> None:
        if name == "New Prompt":
            self.new_request()
            return
        self._refresh_workspace_views()
        self._set_workspace_view(name)

    def _selected_recent(self) -> tuple[int, dict] | None:
        index = self._selected_index(self.recent_listbox)
        if index is None:
            return None
        recent = self._workspace["recent_prompts"]
        if index >= len(recent):
            return None
        return index, recent[index]

    def open_recent(self) -> None:
        selected = self._selected_recent()
        if selected is None:
            return
        _index, item = selected
        if self._hydrate_request(
            item,
            show_prompt=item["prompt_text"],
        ):
            self._set_workspace_view("New Prompt")

    def duplicate_recent(self) -> None:
        selected = self._selected_recent()
        if selected is None:
            return
        _index, item = selected
        if self._hydrate_request(item):
            self._set_workspace_view("New Prompt")

    def copy_recent_prompt(self) -> None:
        selected = self._selected_recent()
        if selected is None:
            return
        _index, item = selected
        prompt = str(item.get("prompt_text", ""))
        if not prompt:
            return
        self._copy_text_to_clipboard(prompt)

    def toggle_recent_selected_favorite(self) -> None:
        selected = self._selected_recent()
        if selected is None:
            return
        index, _item = selected
        self._workspace = toggle_recent_favorite(
            self._workspace,
            index,
        )
        self._save_workspace_state()
        self._refresh_recent_workspace()

    def save_current_preset(self) -> None:
        try:
            self._workspace = save_preset(
                self._workspace,
                self.preset_name_var.get(),
                self._visible_request(),
            )
        except ValueError as exc:
            self.workspace_feedback_var.set(str(exc))
            return
        self._save_workspace_state()
        self._refresh_presets_workspace()

    def _selected_preset(self) -> dict | None:
        index = self._selected_index(self.preset_listbox)
        if index is None:
            return None
        presets = self._workspace["presets"]
        if index >= len(presets):
            return None
        return presets[index]

    def load_selected_preset(self) -> None:
        item = self._selected_preset()
        if item is None:
            return
        if self._hydrate_request(item):
            self._set_workspace_view("New Prompt")

    def delete_selected_preset(self) -> None:
        item = self._selected_preset()
        if item is None:
            return
        self._workspace = delete_preset(
            self._workspace,
            item["name"],
        )
        self._save_workspace_state()
        self._refresh_presets_workspace()

    def _selected_product_variant(
        self,
    ) -> tuple[str, str] | None:
        index = self._selected_index(
            self.product_variant_listbox
        )
        if index is None or self._controller is None:
            return None
        values = []
        for product_option in self._controller.product_options:
            product_id = product_option.product_id
            try:
                variants = self._controller.variant_options_for_product(
                    product_id
                )
            except Exception:
                continue
            for variant_option in variants:
                values.append(
                    (product_id, variant_option.variant_id)
                )
        if index >= len(values):
            return None
        return values[index]

    def use_selected_product_variant(self) -> None:
        selected = self._selected_product_variant()
        if selected is None:
            return
        product_id, variant_id = selected
        self._hydrate_request(
            {
                "product_id": product_id,
                "variant_id": variant_id,
                "background": "",
                "camera_angle": "",
                "requested_output": "",
            }
        )
        self._set_workspace_view("New Prompt")

    def set_selected_product_variant_default(self) -> None:
        selected = self._selected_product_variant()
        if selected is None:
            return
        product_id, variant_id = selected
        self._workspace = set_default_product_variant(
            self._workspace,
            product_id,
            variant_id,
        )
        self._save_workspace_state()
        self._refresh_default_status()

    def toggle_selected_product_variant_favorite(self) -> None:
        selected = self._selected_product_variant()
        if selected is None:
            return
        product_id, variant_id = selected
        self._workspace = toggle_product_favorite(
            self._workspace,
            product_id,
            variant_id,
        )
        self._save_workspace_state()
        self._refresh_products_workspace()

    def clear_default_product_variant(self) -> None:
        self._workspace = clear_default_product_variant(
            self._workspace
        )
        self._save_workspace_state()
        self._refresh_default_status()

    def _clear_error_state(self) -> None:
        self.error_var.set("")
        self.technical_error_var.set("")
        self._retry_action = None
        self._retry_copy_text = ""
        if hasattr(self, "retry_button"):
            self.retry_button.place_forget()
        if hasattr(self, "open_settings_button"):
            self.open_settings_button.place_forget()

    def _show_friendly_error(
        self,
        message: str,
        *,
        technical: str = "",
        retry_action: str | None = None,
        retry_copy_text: str = "",
        open_settings: bool = False,
    ) -> None:
        self.error_var.set(message)
        self.technical_error_var.set(technical)
        self._retry_action = retry_action
        self._retry_copy_text = retry_copy_text
        if retry_action is not None:
            self.retry_button.place(relx=0.02, rely=0.98, anchor="sw")
        else:
            self.retry_button.place_forget()
        if open_settings:
            self.open_settings_button.place(relx=0.18, rely=0.98, anchor="sw")
        else:
            self.open_settings_button.place_forget()

    def retry_last_action(self) -> None:
        action = self._retry_action
        copy_text = self._retry_copy_text
        self._clear_error_state()
        if action == "load":
            self._load_foundation_from_visible_intake(
                persist_on_success=True
            )
        elif action == "submit":
            self.submit()
        elif action == "copy":
            self._copy_text_to_clipboard(copy_text)

    def open_recovery_settings(self) -> None:
        self._set_workspace_view("Settings")
        self._set_data_source_visible(True)

    def _copy_text_to_clipboard(self, value: str) -> bool:
        if not value:
            return False
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
        except Exception as exc:
            self.copy_feedback_var.set("")
            self._show_friendly_error(
                "RCIS couldn't copy to the clipboard. Try again.",
                technical=str(exc),
                retry_action="copy",
                retry_copy_text=value,
            )
            return False
        self._clear_error_state()
        self.copy_feedback_var.set("Copied to clipboard.")
        return True

    def _friendly_submit_error(self, exc: Exception) -> str:
        technical = str(exc)
        messages = (
            ("product_id", "Choose a Product before generating the prompt."),
            ("variant_id", "Choose a Variant before generating the prompt."),
            ("background", "Add a Background before generating the prompt."),
            ("camera_angle", "Add a Camera Angle before generating the prompt."),
            ("requested_output", "Describe the Requested Output before generating the prompt."),
        )
        for token, message in messages:
            if token in technical:
                return message
        return "RCIS couldn't generate the prompt. Review the request and try again."

    def _set_data_source_visible(self, visible: bool) -> None:
        self._data_source_visible = bool(visible)
        if self._data_source_visible:
            self.data_source_frame.grid()
        else:
            self.data_source_frame.grid_remove()

    def toggle_data_source(self) -> None:
        self._set_data_source_visible(
            not self._data_source_visible
        )

    def _set_details_visible(self, visible: bool) -> None:
        self._details_visible = bool(visible)
        if self._details_visible:
            self.details_frame.grid()
            self.details_toggle_button.configure(
                text="Hide Details"
            )
        else:
            self.details_frame.grid_remove()
            self.details_toggle_button.configure(
                text="View Details"
            )

    def toggle_details(self) -> None:
        self._set_details_visible(
            not self._details_visible
        )

    def _set_prompt_output(self, value: str) -> None:
        self.prompt_output.configure(state="normal")
        self.prompt_output.delete("1.0", "end")
        self.prompt_output.insert("1.0", value)
        self.prompt_output.configure(state="disabled")

    def _clear_result_output(self) -> None:
        self.result_state_var.set("")
        self.bridge_status_var.set("")
        self.exact_six_status_var.set("")
        self.binding_status_var.set("")
        self.grounding_status_var.set("")
        self._set_prompt_output("")

    def _render_result(self, result: GroundedPromptUiResult) -> None:
        self.bridge_status_var.set(
            result.bridge_materialization_status
        )
        self.exact_six_status_var.set(
            result.exact_six_materialization_status
        )
        self.binding_status_var.set(result.binding_status)
        self.grounding_status_var.set(result.grounding_status)
        self._set_prompt_output(result.prompt_text)
        self.result_state_var.set("Prompt ready")

    def _save_prompt_text(self, prompt: str) -> bool:
        if not prompt:
            return False
        try:
            destination = self._save_dialog(
                title="Save prompt",
                initialfile="RCIS-grounded-prompt.txt",
                defaultextension=".txt",
                filetypes=(
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ),
            )
        except Exception as exc:
            self._show_friendly_error(
                "RCIS couldn't open Save As. Try again.",
                technical=str(exc),
            )
            return False
        if not destination:
            return False
        try:
            self._file_writer(
                destination,
                prompt.encode("utf-8"),
            )
        except Exception as exc:
            self._show_friendly_error(
                "RCIS couldn't save this prompt. Choose another location and try again.",
                technical=str(exc),
            )
            return False
        self._clear_error_state()
        self.copy_feedback_var.set("Prompt saved.")
        return True

    def save_prompt(self) -> None:
        prompt = self.prompt_output.get("1.0", "end-1c")
        if self.result_state_var.get() != "Prompt ready" or not prompt:
            self._show_friendly_error(
                "Generate a current prompt before saving.",
                technical="current prompt result is empty or stale",
            )
            return
        self._save_prompt_text(prompt)

    def save_recent_prompt(self) -> None:
        selected = self._selected_recent()
        if selected is None:
            self._show_friendly_error(
                "Choose a recent prompt before saving.",
                technical="no recent prompt is selected",
            )
            return
        _index, item = selected
        prompt = str(item.get("prompt_text", ""))
        if not prompt:
            self._show_friendly_error(
                "This recent prompt has no text to save.",
                technical="selected recent prompt_text is empty",
            )
            return
        self._save_prompt_text(prompt)

    def copy_prompt(self) -> None:
        prompt = self.prompt_output.get("1.0", "end-1c")
        if not prompt:
            return
        self._copy_text_to_clipboard(prompt)

    def new_request(self) -> None:
        self._clear_error_state()
        self.copy_feedback_var.set("")
        self.workspace_feedback_var.set("")
        self._suspend_workspace_persistence = True
        try:
            self.product_var.set("")
            self.variant_var.set("")
            self.product_label_var.set("")
            self.variant_label_var.set("")
            self.background_var.set("")
            self.camera_angle_var.set("")
            self.requested_output_text.delete("1.0", "end")
            self.requested_output_text.edit_modified(False)
            self._set_variant_options(())
            self.variant_combo.configure(state="disabled")
            self._apply_valid_default()
        finally:
            self._suspend_workspace_persistence = False
        self._clear_result_output()
        self._set_workspace_view("New Prompt")
        self.product_combo.focus_set()

    def _restore_remembered_foundation(self) -> bool:
        try:
            remembered = self._settings_loader()
        except Exception as exc:
            self._show_friendly_error(
                "Saved data source could not be restored. Open Settings to choose it again.",
                technical=str(exc),
                open_settings=True,
            )
            return False
        if not isinstance(remembered, str) or not remembered.strip():
            return False
        self.intake_root_var.set(remembered.strip())
        return self._load_foundation_from_visible_intake(
            persist_on_success=False
        )

    def _load_foundation_from_visible_intake(
        self,
        *,
        persist_on_success: bool,
    ) -> bool:
        self._clear_error_state()
        self._clear_result_output()
        intake_root = self.intake_root_var.get().strip()
        if not intake_root:
            self._show_friendly_error(
                "Choose a data source before loading RCIS.",
                technical="intake_root must not be empty",
                open_settings=True,
            )
            self._set_data_source_visible(True)
            return False
        try:
            controller = self._controller_factory(
                intake_root=intake_root
            )
            product_options = controller.product_options
        except Exception as exc:
            self._show_friendly_error(
                "RCIS couldn't load this data source. Check the folder and try again.",
                technical=str(exc),
                retry_action="load",
                open_settings=True,
            )
            self._set_data_source_visible(True)
            return False
        previous_suspend = self._suspend_workspace_persistence
        self._suspend_workspace_persistence = True
        try:
            self._controller = controller
            self.product_var.set("")
            self.variant_var.set("")
            self.product_label_var.set("")
            self.variant_label_var.set("")
            self._set_product_options(product_options)
            self.product_combo.configure(state="readonly")
            self._set_variant_options(())
            self.variant_combo.configure(state="disabled")
            self._restore_workspace_request_once()
        finally:
            self._suspend_workspace_persistence = previous_suspend
        self._refresh_products_workspace()
        self._refresh_workspace_views()
        if persist_on_success:
            try:
                self._settings_saver(intake_root)
            except Exception as exc:
                self.workspace_feedback_var.set(
                    "Foundation loaded, but RCIS couldn't remember this data source for next time."
                )
                self.technical_error_var.set(str(exc))

        self._set_data_source_visible(False)
        return True

    def browse_intake_root(self) -> None:
        selected_directory = self._directory_picker()
        if selected_directory:
            self.intake_root_var.set(selected_directory)
            self._load_foundation_from_visible_intake(
                persist_on_success=True
            )

    def load_foundation(self) -> None:
        self._load_foundation_from_visible_intake(
            persist_on_success=True
        )

    def refresh_variants(self) -> None:
        self._clear_error_state()
        self.variant_var.set("")
        self.variant_label_var.set("")
        self._set_variant_options(())
        self.variant_combo.configure(state="disabled")
        if self._controller is None:
            return

        product_id = self.product_var.get().strip()
        if not product_id:
            return
        try:
            variants = self._controller.variant_options_for_product(
                product_id
            )
        except Exception as exc:
            self._show_friendly_error(
                "RCIS couldn't load variants for this product. Choose another product or try again.",
                technical=str(exc),
            )
            return
        self._set_variant_options(variants)
        self.variant_combo.configure(state="readonly")

    def submit(self) -> None:
        self._clear_error_state()
        self.copy_feedback_var.set("")
        self._clear_result_output()
        if self._controller is None:
            self._show_friendly_error(
                "RCIS needs a data source before it can generate a prompt.",
                technical="foundation must be loaded before submit",
                open_settings=True,
            )
            self.result_state_var.set(
                "Could not generate prompt"
            )
            self._set_data_source_visible(True)
            return
        requested_output = self.requested_output_text.get(
            "1.0",
            "end-1c",
        )
        self.requested_output_text.edit_modified(False)
        try:
            result = self._controller.submit(
                product_id=self.product_var.get(),
                variant_id=self.variant_var.get(),
                background=self.background_var.get(),
                camera_angle=self.camera_angle_var.get(),
                requested_output=requested_output,
            )
        except Exception as exc:
            self._show_friendly_error(
                self._friendly_submit_error(exc),
                technical=str(exc),
                retry_action="submit",
            )
            self.result_state_var.set(
                "Could not generate prompt"
            )
            return
        self._clear_error_state()
        self._render_result(result)
        self._record_successful_prompt(result)


def main() -> None:
    root = tk.Tk()
    GroundedPromptTkApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
