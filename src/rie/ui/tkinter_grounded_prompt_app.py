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


WINDOW_TITLE = "RCIS Grounded Prompt"


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
        settings_loader: Callable[[], str | None] = (
            load_remembered_intake_root
        ),
        settings_saver: Callable[[str], object] = (
            save_remembered_intake_root
        ),
    ) -> None:
        self.root = root
        self._controller_factory = controller_factory
        self._directory_picker = directory_picker
        self._settings_loader = settings_loader
        self._settings_saver = settings_saver
        self._controller: GroundedPromptUiController | None = None
        self._data_source_visible = True
        self._details_visible = False
        self.root.winfo_toplevel().title(WINDOW_TITLE)

        self.intake_root_var = tk.StringVar(master=root, value="")
        self.product_var = tk.StringVar(master=root, value="")
        self.variant_var = tk.StringVar(master=root, value="")
        self.background_var = tk.StringVar(master=root, value="")
        self.camera_angle_var = tk.StringVar(master=root, value="")
        self.error_var = tk.StringVar(master=root, value="")
        self.result_state_var = tk.StringVar(master=root, value="")
        self.bridge_status_var = tk.StringVar(master=root, value="")
        self.exact_six_status_var = tk.StringVar(master=root, value="")
        self.binding_status_var = tk.StringVar(master=root, value="")
        self.grounding_status_var = tk.StringVar(master=root, value="")

        self._build_widgets()
        self._bind_result_invalidation()
        if self._restore_remembered_foundation():
            self._set_data_source_visible(False)
        else:
            self._set_data_source_visible(True)

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

    def _on_requested_output_modified(self, _event: object = None) -> None:
        if not self.requested_output_text.edit_modified():
            return
        self._clear_result_output()
        self.requested_output_text.edit_modified(False)

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
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
            textvariable=self.product_var,
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
            lambda event: self.refresh_variants(),
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
            textvariable=self.variant_var,
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

        self._set_details_visible(False)

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

    def copy_prompt(self) -> None:
        prompt = self.prompt_output.get("1.0", "end-1c")
        if not prompt:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)

    def new_request(self) -> None:
        self.error_var.set("")
        self.product_var.set("")
        self.variant_var.set("")
        self.background_var.set("")
        self.camera_angle_var.set("")
        self.requested_output_text.delete("1.0", "end")
        self.requested_output_text.edit_modified(False)
        self.variant_combo.configure(
            values=(),
            state="disabled",
        )
        self._clear_result_output()
        self.product_combo.focus_set()

    def _restore_remembered_foundation(self) -> bool:
        try:
            remembered = self._settings_loader()
        except Exception:
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
        self.error_var.set("")
        self._clear_result_output()
        intake_root = self.intake_root_var.get().strip()
        if not intake_root:
            self.error_var.set("intake_root must not be empty")
            self._set_data_source_visible(True)
            return False
        try:
            controller = self._controller_factory(
                intake_root=intake_root
            )
        except Exception as exc:
            self.error_var.set(str(exc))
            self._set_data_source_visible(True)
            return False

        self._controller = controller
        self.product_var.set("")
        self.variant_var.set("")
        self.product_combo.configure(
            values=controller.product_ids,
            state="readonly",
        )
        self.variant_combo.configure(
            values=(),
            state="disabled",
        )

        if persist_on_success:
            try:
                self._settings_saver(intake_root)
            except Exception:
                pass

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
        self.error_var.set("")
        self.variant_var.set("")
        self.variant_combo.configure(
            values=(),
            state="disabled",
        )
        if self._controller is None:
            return

        product_id = self.product_var.get().strip()
        if not product_id:
            return

        try:
            variants = self._controller.variant_ids_for_product(
                product_id
            )
        except Exception as exc:
            self.error_var.set(str(exc))
            return
        self.variant_combo.configure(
            values=variants,
            state="readonly",
        )

    def submit(self) -> None:
        self.error_var.set("")
        self._clear_result_output()
        if self._controller is None:
            self.error_var.set(
                "foundation must be loaded before submit"
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
            self.error_var.set(str(exc))
            self.result_state_var.set(
                "Could not generate prompt"
            )
            return
        self._render_result(result)


def main() -> None:
    root = tk.Tk()
    GroundedPromptTkApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
