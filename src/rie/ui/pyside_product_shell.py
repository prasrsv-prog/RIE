"""Parallel PySide6 product-completion shell.

This is a migration-foundation UI.  It does not replace the current Tkinter
production entrypoint and does not access governed storage directly.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from rie.ui.product_completion_models import (
    CreativeBrief,
    ProductConstraint,
    ProductContextSnapshot,
    ProductFact,
    ProductUnknown,
)


WINDOW_TITLE = "RCIS Creative Studio"
NAVIGATION = (
    "Create",
    "Products",
    "Assets",
    "Projects",
    "History",
    "Presets",
    "Settings",
)


class GroundedPromptCompatibilityAdapter:
    """Thin adapter over the existing toolkit-independent grounded prompt UI."""

    def __init__(self, controller: Any) -> None:
        self._controller = controller

    @property
    def product_options(self) -> tuple[Any, ...]:
        return tuple(self._controller.product_options)

    def variant_options_for_product(self, product_id: str) -> tuple[Any, ...]:
        return tuple(self._controller.variant_options_for_product(product_id))

    def submit_legacy(
        self,
        *,
        product_id: str,
        variant_id: str,
        brief: CreativeBrief,
    ) -> Any:
        fields = brief.legacy_submit_fields()
        return self._controller.submit(
            product_id=product_id,
            variant_id=variant_id,
            background=fields["background"],
            camera_angle=fields["camera_angle"],
            requested_output=fields["requested_output"],
        )




class ProductIntelligencePresentationAdapter:
    """Map framework-neutral PC2 read models into existing UI read models."""

    def __init__(self, query: Any) -> None:
        self._query = query

    @property
    def product_options(self) -> tuple[Any, ...]:
        return tuple(self._query.list_products())

    def variant_options_for_product(self, product_id: str) -> tuple[Any, ...]:
        return tuple(self._query.list_variants(product_id))

    def context_snapshot(
        self,
        *,
        product_id: str,
        variant_id: str,
    ) -> ProductContextSnapshot:
        context = self._query.get_product_context(product_id, variant_id)
        return ProductContextSnapshot(
            product_id=context.product_id,
            variant_id=context.variant_id,
            product_label=context.product_label,
            variant_label=context.variant_label,
            summary=context.summary,
            fact_groups=tuple(
                ProductFact(
                    fact_id=fact.fact_id,
                    category=fact.category,
                    label=fact.label,
                    value=fact.value,
                    scope=fact.scope,
                    authority_state=fact.authority_state,
                    provenance_refs=tuple(fact.provenance_refs),
                )
                for fact in context.fact_groups
            ),
            preservation_constraints=tuple(
                ProductConstraint(
                    constraint_id=item.constraint_id,
                    label=item.label,
                    rule_text=item.rule_text,
                    scope=item.scope,
                    severity=item.severity,
                    source_fact_refs=tuple(item.source_fact_refs),
                )
                for item in context.preservation_constraints
            ),
            authorized_reference_asset_ids=tuple(
                context.authorized_reference_asset_ids
            ),
            unknown_topics=tuple(
                ProductUnknown(
                    topic=item.topic,
                    user_facing_label=item.user_facing_label,
                    reason=item.reason,
                )
                for item in context.unknown_topics
            ),
            conflicts=tuple(context.conflicts),
            provenance_summary=context.provenance_summary,
        )


class ProductCompletionShell(QMainWindow):
    """Foundation shell for the PC1-PC7 product-completion migration."""

    def __init__(
        self,
        *,
        adapter: GroundedPromptCompatibilityAdapter | None = None,
        product_intelligence_query: Any | None = None,
    ) -> None:
        super().__init__()
        self._adapter = adapter
        self._product_intelligence = (
            ProductIntelligencePresentationAdapter(product_intelligence_query)
            if product_intelligence_query is not None
            else None
        )
        self._product_ids_by_label: dict[str, str] = {}
        self._variant_ids_by_label: dict[str, str] = {}

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(1360, 840)
        self.setMinimumSize(1040, 680)

        self.navigation = QListWidget()
        self.navigation.setObjectName("primaryNavigation")
        self.navigation.addItems(list(NAVIGATION))
        self.navigation.setFixedWidth(150)

        self.pages = QStackedWidget()
        self.pages.setObjectName("workspacePages")

        self._create_page = self._build_create_page()
        self.pages.addWidget(self._create_page)
        for name in NAVIGATION[1:]:
            self.pages.addWidget(self._placeholder_page(name))

        self.product_context_panel = self._build_product_context_panel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("mainThreePaneSplitter")
        splitter.addWidget(self.navigation)
        splitter.addWidget(self.pages)
        splitter.addWidget(self.product_context_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([150, 850, 360])

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        self.setCentralWidget(root)

        status = QStatusBar()
        status.showMessage("Foundation shell - provider not connected")
        self.setStatusBar(status)

        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)

        if self._adapter is not None or self._product_intelligence is not None:
            self._load_products()

    def _build_create_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        heading = QLabel("Create")
        heading.setObjectName("createHeading")
        heading.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(heading)

        intro = QLabel(
            "Choose a product, shape the creative brief, build a grounded prompt, "
            "then continue to visual generation."
        )
        intro.setWordWrap(True)
        intro.setObjectName("createIntro")
        layout.addWidget(intro)

        product_group = QGroupBox("1. Product")
        product_form = QFormLayout(product_group)
        self.product_combo = QComboBox()
        self.product_combo.setObjectName("productSelector")
        self.product_combo.addItem("Choose product...")
        self.variant_combo = QComboBox()
        self.variant_combo.setObjectName("variantSelector")
        self.variant_combo.addItem("Choose variant...")
        self.variant_combo.setEnabled(False)
        product_form.addRow("Product", self.product_combo)
        product_form.addRow("Variant", self.variant_combo)
        layout.addWidget(product_group)

        brief_group = QGroupBox("2. Creative Brief")
        brief_form = QFormLayout(brief_group)
        self.objective_edit = QLineEdit()
        self.objective_edit.setPlaceholderText("Example: ecommerce hero visual")
        self.environment_edit = QLineEdit()
        self.environment_edit.setPlaceholderText("Example: dark studio")
        self.camera_edit = QLineEdit()
        self.camera_edit.setPlaceholderText("Example: front")
        self.lighting_edit = QLineEdit()
        self.lighting_edit.setPlaceholderText("Example: soft directional light")
        self.composition_edit = QLineEdit()
        self.composition_edit.setPlaceholderText("Example: centered product, clean negative space")
        self.mood_edit = QLineEdit()
        self.mood_edit.setPlaceholderText("Example: premium, technical")
        self.deliverable_edit = QLineEdit()
        self.deliverable_edit.setPlaceholderText("Example: grounded product prompt")
        brief_form.addRow("Purpose", self.objective_edit)
        brief_form.addRow("Scene / Environment", self.environment_edit)
        brief_form.addRow("Camera", self.camera_edit)
        brief_form.addRow("Lighting", self.lighting_edit)
        brief_form.addRow("Composition", self.composition_edit)
        brief_form.addRow("Mood / Style", self.mood_edit)
        brief_form.addRow("Output", self.deliverable_edit)
        layout.addWidget(brief_group)

        action_row = QHBoxLayout()
        self.prompt_button = QPushButton("Build Grounded Prompt")
        self.prompt_button.setObjectName("buildGroundedPrompt")
        self.visual_button = QPushButton("Generate Visuals")
        self.visual_button.setObjectName("generateVisuals")
        self.visual_button.setEnabled(False)
        self.visual_button.setToolTip(
            "Visual generation provider is not connected in the foundation slice."
        )
        action_row.addWidget(self.prompt_button)
        action_row.addWidget(self.visual_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        prompt_group = QGroupBox("3. Prompt")
        prompt_layout = QVBoxLayout(prompt_group)
        self.prompt_preview = QPlainTextEdit()
        self.prompt_preview.setObjectName("promptPreview")
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setPlaceholderText(
            "Your grounded prompt will appear here."
        )
        prompt_layout.addWidget(self.prompt_preview)
        layout.addWidget(prompt_group, 1)

        self.create_feedback = QLabel(
            "Select a product and variant to begin."
        )
        self.create_feedback.setObjectName("createFeedback")
        self.create_feedback.setWordWrap(True)
        layout.addWidget(self.create_feedback)

        self.product_combo.currentIndexChanged.connect(self._product_changed)
        self.variant_combo.currentIndexChanged.connect(self._variant_changed)
        self.prompt_button.clicked.connect(self._build_grounded_prompt)

        return page

    def _build_product_context_panel(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 18, 16, 18)

        heading = QLabel("Product Context")
        heading.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(heading)

        self.context_title = QLabel("No product selected")
        self.context_title.setObjectName("productContextTitle")
        self.context_title.setWordWrap(True)
        layout.addWidget(self.context_title)

        self.context_summary = QLabel(
            "Grounded product intelligence will appear here."
        )
        self.context_summary.setWordWrap(True)
        self.context_summary.setObjectName("productContextSummary")
        layout.addWidget(self.context_summary)

        self.facts_label = self._add_context_section(
            layout,
            "Product Facts",
            "No facts loaded.",
        )
        self.constraints_label = self._add_context_section(
            layout,
            "Creative Constraints",
            "No constraints loaded.",
        )
        self.references_label = self._add_context_section(
            layout,
            "References",
            "No authorized references loaded.",
        )
        self.unknowns_label = self._add_context_section(
            layout,
            "Unknown / Conflict",
            "No product context loaded.",
        )
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("productContextPanel")
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(300)
        scroll.setWidget(content)
        return scroll

    def _add_context_section(
        self,
        layout: QVBoxLayout,
        title: str,
        initial: str,
    ) -> QLabel:
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 600; margin-top: 10px;")
        value = QLabel(initial)
        value.setWordWrap(True)
        value.setProperty("sectionTitle", title)
        layout.addWidget(title_label)
        layout.addWidget(value)
        return value

    def _placeholder_page(self, name: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        title = QLabel(name)
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        body = QLabel(
            f"{name} workspace is reserved by the product-completion architecture "
            "and is not implemented in the migration-foundation slice."
        )
        body.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(body)
        layout.addStretch(1)
        return page

    def _product_options(self) -> tuple[Any, ...]:
        if self._product_intelligence is not None:
            return self._product_intelligence.product_options
        if self._adapter is not None:
            return self._adapter.product_options
        return ()

    def _variant_options_for_product(
        self,
        product_id: str,
    ) -> tuple[Any, ...]:
        if self._product_intelligence is not None:
            return self._product_intelligence.variant_options_for_product(
                product_id
            )
        if self._adapter is not None:
            return self._adapter.variant_options_for_product(product_id)
        return ()

    def _load_products(self) -> None:
        self._product_ids_by_label.clear()
        self.product_combo.clear()
        self.product_combo.addItem("Choose product...")
        for option in self._product_options():
            self._product_ids_by_label[option.label] = option.product_id
            self.product_combo.addItem(option.label)

    def _product_changed(self) -> None:
        label = self.product_combo.currentText()
        product_id = self._product_ids_by_label.get(label)
        self.variant_combo.clear()
        self.variant_combo.addItem("Choose variant...")
        self._variant_ids_by_label.clear()

        if not product_id:
            self.variant_combo.setEnabled(False)
            self.apply_product_context(None)
            return

        for option in self._variant_options_for_product(product_id):
            self._variant_ids_by_label[option.label] = option.variant_id
            self.variant_combo.addItem(option.label)
        self.variant_combo.setEnabled(True)
        self.context_title.setText(label)
        self.context_summary.setText(
            "Product identity loaded. Grounded knowledge projection arrives in PC2."
        )
        self.create_feedback.setText("Choose a variant to continue.")

    def _variant_changed(self) -> None:
        product_label = self.product_combo.currentText()
        variant_label = self.variant_combo.currentText()
        if (
            product_label in self._product_ids_by_label
            and variant_label in self._variant_ids_by_label
        ):
            product_id = self._product_ids_by_label[product_label]
            variant_id = self._variant_ids_by_label[variant_label]
            if self._product_intelligence is not None:
                try:
                    snapshot = self._product_intelligence.context_snapshot(
                        product_id=product_id,
                        variant_id=variant_id,
                    )
                except Exception as exc:
                    self.context_title.setText(
                        f"{product_label} / {variant_label}"
                    )
                    self.context_summary.setText(
                        "RCIS could not load grounded product intelligence."
                    )
                    self.create_feedback.setText(
                        f"Could not load Product Context: {exc}"
                    )
                    return
                self.apply_product_context(snapshot)
                self.create_feedback.setText(
                    "Grounded Product Context ready. Complete the creative brief."
                )
                return

            self.context_title.setText(f"{product_label} / {variant_label}")
            self.create_feedback.setText(
                "Product ready. Complete the creative brief."
            )

    def current_brief(self) -> CreativeBrief:
        return CreativeBrief(
            objective=self.objective_edit.text(),
            deliverable=self.deliverable_edit.text(),
            environment=self.environment_edit.text(),
            camera_angle=self.camera_edit.text(),
            lighting_style=self.lighting_edit.text(),
            composition=self.composition_edit.text(),
            mood_style=self.mood_edit.text(),
        )

    def apply_product_context(
        self,
        snapshot: ProductContextSnapshot | None,
    ) -> None:
        if snapshot is None:
            self.context_title.setText("No product selected")
            self.context_summary.setText(
                "Grounded product intelligence will appear here."
            )
            self.facts_label.setText("No facts loaded.")
            self.constraints_label.setText("No constraints loaded.")
            self.references_label.setText("No authorized references loaded.")
            self.unknowns_label.setText("No product context loaded.")
            return

        self.context_title.setText(snapshot.display_name)
        self.context_summary.setText(
            snapshot.summary or "Grounded product context loaded."
        )
        self.facts_label.setText(
            "\n".join(
                f"{fact.label}: {fact.value}" for fact in snapshot.fact_groups
            )
            or "No grounded facts available."
        )
        self.constraints_label.setText(
            "\n".join(
                constraint.rule_text
                for constraint in snapshot.preservation_constraints
            )
            or "No grounded preservation constraints available."
        )
        self.references_label.setText(
            "\n".join(snapshot.authorized_reference_asset_ids)
            or "No authorized references available."
        )
        unknown_lines = [
            unknown.user_facing_label for unknown in snapshot.unknown_topics
        ]
        unknown_lines.extend(snapshot.conflicts)
        self.unknowns_label.setText(
            "\n".join(unknown_lines) or "No unknown/conflict items reported."
        )

    def _build_grounded_prompt(self) -> None:
        if self._adapter is None:
            self.create_feedback.setText(
                "Grounded prompt adapter is not connected in this shell proof."
            )
            return

        product_label = self.product_combo.currentText()
        variant_label = self.variant_combo.currentText()
        product_id = self._product_ids_by_label.get(product_label)
        variant_id = self._variant_ids_by_label.get(variant_label)
        if not product_id or not variant_id:
            self.create_feedback.setText(
                "Choose a product and variant before building a prompt."
            )
            return

        try:
            result = self._adapter.submit_legacy(
                product_id=product_id,
                variant_id=variant_id,
                brief=self.current_brief(),
            )
        except Exception as exc:
            self.create_feedback.setText(f"Could not build prompt: {exc}")
            return

        self.prompt_preview.setPlainText(result.prompt_text)
        self.create_feedback.setText("Grounded prompt ready.")


def packaging_smoke_main() -> None:
    """Construct and validate the Qt shell without entering the event loop."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    shell = ProductCompletionShell()
    assert shell.windowTitle() == WINDOW_TITLE
    assert shell.navigation.count() == len(NAVIGATION)
    assert shell.findChild(QSplitter, "mainThreePaneSplitter") is not None
    assert shell.findChild(QScrollArea, "productContextPanel") is not None
    marker = os.environ.get("RCIS_PYSIDE_PACKAGING_SMOKE_MARKER_PATH", "").strip()
    if marker:
        Path(marker).write_text("RCIS_PYSIDE_FOUNDATION_SMOKE_OK\n", encoding="ascii")
    shell.close()
    app.processEvents()


def main() -> None:
    app = QApplication.instance() or QApplication([])
    shell = ProductCompletionShell()
    shell.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()