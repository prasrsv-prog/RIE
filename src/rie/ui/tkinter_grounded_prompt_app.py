"""Tkinter presentation adapter for the Phase F grounded prompt UI MVP."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable

from rie.ui.grounded_prompt_ui_controller import (
    GroundedPromptUiController,
    GroundedPromptUiResult,
)


WINDOW_TITLE = "RCIS Grounded Prompt MVP"


class GroundedPromptTkApplication:
    """Minimum local single-operator Tkinter UI."""

    def __init__(
        self,
        root: tk.Misc,
        *,
        controller_factory: Callable[..., GroundedPromptUiController] = (
            GroundedPromptUiController.from_intake_root
        ),
        directory_picker: Callable[[], str] = filedialog.askdirectory,
    ) -> None:
        self.root = root
        self._controller_factory = controller_factory
        self._directory_picker = directory_picker
        self._controller: GroundedPromptUiController | None = None

        self.root.winfo_toplevel().title(WINDOW_TITLE)

        self.intake_root_var = tk.StringVar(master=root, value="")
        self.product_var = tk.StringVar(master=root, value="")
        self.variant_var = tk.StringVar(master=root, value="")
        self.background_var = tk.StringVar(master=root, value="")
        self.camera_angle_var = tk.StringVar(master=root, value="")
        self.error_var = tk.StringVar(master=root, value="")

        self.bridge_status_var = tk.StringVar(master=root, value="")
        self.exact_six_status_var = tk.StringVar(master=root, value="")
        self.binding_status_var = tk.StringVar(master=root, value="")
        self.grounding_status_var = tk.StringVar(master=root, value="")

        self._build_widgets()

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Intake Root").grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=3
        )
        self.intake_root_entry = ttk.Entry(
            frame, textvariable=self.intake_root_var
        )
        self.intake_root_entry.grid(
            row=0, column=1, sticky="ew", pady=3
        )
        self.intake_action_frame = ttk.Frame(frame)
        self.intake_action_frame.grid(row=0, column=2, padx=(8, 0), pady=3)
        self.browse_button = ttk.Button(
            self.intake_action_frame, text="Browse...", command=self.browse_intake_root
        )
        self.browse_button.grid(row=0, column=0)
        self.load_button = ttk.Button(
            self.intake_action_frame, text="Load Foundation", command=self.load_foundation
        )
        self.load_button.grid(row=0, column=1, padx=(8, 0))

        ttk.Label(frame, text="Product ID").grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=3
        )
        self.product_combo = ttk.Combobox(
            frame,
            textvariable=self.product_var,
            values=(),
            state="disabled",
        )
        self.product_combo.grid(row=1, column=1, columnspan=2, sticky="ew", pady=3)
        self.product_combo.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_variants(),
        )

        ttk.Label(frame, text="Variant ID").grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=3
        )
        self.variant_combo = ttk.Combobox(
            frame,
            textvariable=self.variant_var,
            values=(),
            state="disabled",
        )
        self.variant_combo.grid(row=2, column=1, columnspan=2, sticky="ew", pady=3)

        ttk.Label(frame, text="Background").grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=3
        )
        self.background_entry = ttk.Entry(
            frame, textvariable=self.background_var
        )
        self.background_entry.grid(
            row=3, column=1, columnspan=2, sticky="ew", pady=3
        )

        ttk.Label(frame, text="Camera Angle").grid(
            row=4, column=0, sticky="w", padx=(0, 8), pady=3
        )
        self.camera_angle_entry = ttk.Entry(
            frame, textvariable=self.camera_angle_var
        )
        self.camera_angle_entry.grid(
            row=4, column=1, columnspan=2, sticky="ew", pady=3
        )

        ttk.Label(frame, text="Requested Output").grid(
            row=5, column=0, sticky="nw", padx=(0, 8), pady=3
        )
        self.requested_output_text = tk.Text(frame, height=3, width=50)
        self.requested_output_text.grid(
            row=5, column=1, columnspan=2, sticky="ew", pady=3
        )

        self.submit_button = ttk.Button(
            frame, text="Submit Grounded Prompt", command=self.submit
        )
        self.submit_button.grid(
            row=6, column=1, columnspan=2, sticky="e", pady=(8, 4)
        )

        status_frame = ttk.LabelFrame(frame, text="Grounding Status", padding=8)
        status_frame.grid(
            row=7, column=0, columnspan=3, sticky="ew", pady=(8, 4)
        )
        status_frame.columnconfigure(1, weight=1)
        status_rows = (
            ("Bridge materialization", self.bridge_status_var),
            ("Exact-six materialization", self.exact_six_status_var),
            ("Binding", self.binding_status_var),
            ("Grounding", self.grounding_status_var),
        )
        for row, (label, variable) in enumerate(status_rows):
            ttk.Label(status_frame, text=label).grid(
                row=row, column=0, sticky="w", padx=(0, 8)
            )
            ttk.Label(status_frame, textvariable=variable).grid(
                row=row, column=1, sticky="w"
            )

        ttk.Label(frame, text="Grounded Prompt").grid(
            row=8, column=0, sticky="nw", padx=(0, 8), pady=3
        )
        self.prompt_output = tk.Text(frame, height=12, width=70, state="disabled")
        self.prompt_output.grid(
            row=8, column=1, columnspan=2, sticky="nsew", pady=3
        )
        frame.rowconfigure(8, weight=1)

        self.error_label = ttk.Label(frame, textvariable=self.error_var)
        self.error_label.grid(
            row=9, column=0, columnspan=3, sticky="w", pady=(6, 0)
        )

    def _set_prompt_output(self, value: str) -> None:
        self.prompt_output.configure(state="normal")
        self.prompt_output.delete("1.0", "end")
        self.prompt_output.insert("1.0", value)
        self.prompt_output.configure(state="disabled")

    def _clear_result_output(self) -> None:
        self.bridge_status_var.set("")
        self.exact_six_status_var.set("")
        self.binding_status_var.set("")
        self.grounding_status_var.set("")
        self._set_prompt_output("")

    def _render_result(self, result: GroundedPromptUiResult) -> None:
        self.bridge_status_var.set(result.bridge_materialization_status)
        self.exact_six_status_var.set(result.exact_six_materialization_status)
        self.binding_status_var.set(result.binding_status)
        self.grounding_status_var.set(result.grounding_status)
        self._set_prompt_output(result.prompt_text)

    def browse_intake_root(self) -> None:
        selected_directory = self._directory_picker()
        if selected_directory:
            self.intake_root_var.set(selected_directory)

    def load_foundation(self) -> None:
        self.error_var.set("")
        self._clear_result_output()
        intake_root = self.intake_root_var.get().strip()
        if not intake_root:
            self.error_var.set("intake_root must not be empty")
            return

        try:
            controller = self._controller_factory(intake_root=intake_root)
        except Exception as exc:
            self.error_var.set(str(exc))
            return

        self._controller = controller
        self.product_var.set("")
        self.variant_var.set("")
        self.product_combo.configure(
            values=controller.product_ids,
            state="readonly",
        )
        self.variant_combo.configure(values=(), state="disabled")

    def refresh_variants(self) -> None:
        self.error_var.set("")
        self.variant_var.set("")
        self.variant_combo.configure(values=(), state="disabled")
        if self._controller is None:
            return

        product_id = self.product_var.get().strip()
        if not product_id:
            return

        try:
            variants = self._controller.variant_ids_for_product(product_id)
        except Exception as exc:
            self.error_var.set(str(exc))
            return

        self.variant_combo.configure(values=variants, state="readonly")

    def submit(self) -> None:
        self.error_var.set("")
        self._clear_result_output()
        if self._controller is None:
            self.error_var.set("foundation must be loaded before submit")
            return

        requested_output = self.requested_output_text.get("1.0", "end-1c")
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
            return

        self._render_result(result)


def main() -> None:
    root = tk.Tk()
    GroundedPromptTkApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
