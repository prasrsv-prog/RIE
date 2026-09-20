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

from rie.application.creative_prompt_composer import CreativePromptBrief

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


class CreativePromptComposerPresentationAdapter:
    """Project the UI CreativeBrief into the framework-neutral PC3 facade."""

    def __init__(self, composer: Any) -> None:
        self._composer = composer

    def compose(
        self,
        *,
        product_id: str,
        variant_id: str,
        brief: CreativeBrief,
    ) -> Any:
        return self._composer.compose_grounded_prompt(
            product_id=product_id,
            variant_id=variant_id,
            brief=CreativePromptBrief(
                objective=brief.objective,
                deliverable=brief.deliverable,
                environment=brief.environment,
                camera_angle=brief.camera_angle,
                shot_type=brief.shot_type,
                lighting_style=brief.lighting_style,
                composition=brief.composition,
                mood_style=brief.mood_style,
                aspect_ratio=brief.aspect_ratio,
                orientation=brief.orientation,
                product_emphasis=brief.product_emphasis,
                preserve_constraints=tuple(brief.preserve_constraints),
                avoid_constraints=tuple(brief.avoid_constraints),
                freeform_notes=brief.freeform_notes,
            ),
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


    def search_facts(
        self,
        query: str,
        *,
        product_id: str,
        variant_id: str,
    ) -> tuple[Any, ...]:
        return tuple(
            self._query.search_product_facts(
                query,
                product_id=product_id,
                variant_id=variant_id,
            )
        )

    def provenance(self, reference_id: str) -> Any:
        return self._query.get_provenance(reference_id)


class ProductCompletionShell(QMainWindow):
    """Foundation shell for the PC1-PC7 product-completion migration."""

    def __init__(
        self,
        *,
        adapter: GroundedPromptCompatibilityAdapter | None = None,
        product_intelligence_query: Any | None = None,
        creative_prompt_composer: Any | None = None,
    ) -> None:
        super().__init__()
        self._adapter = adapter
        self._creative_prompt_composer = (
            CreativePromptComposerPresentationAdapter(creative_prompt_composer)
            if creative_prompt_composer is not None
            else None
        )
        self._product_intelligence = (
            ProductIntelligencePresentationAdapter(product_intelligence_query)
            if product_intelligence_query is not None
            else None
        )
        self._product_ids_by_label: dict[str, str] = {}
        self._variant_ids_by_label: dict[str, str] = {}
        self._workspace_product_ids_by_label: dict[str, str] = {}
        self._workspace_variant_ids_by_label: dict[str, str] = {}
        self._workspace_provenance_refs: tuple[str, ...] = ()

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
        self._products_page = self._build_products_page()
        self.pages.addWidget(self._products_page)
        for name in NAVIGATION[2:]:
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
        self._load_products_workspace()

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
        self.shot_type_edit = QLineEdit()
        self.shot_type_edit.setObjectName("creativeBriefShotType")
        self.shot_type_edit.setPlaceholderText("Example: medium product shot")
        self.lighting_edit = QLineEdit()
        self.lighting_edit.setPlaceholderText("Example: soft directional light")
        self.composition_edit = QLineEdit()
        self.composition_edit.setPlaceholderText("Example: centered product, clean negative space")
        self.mood_edit = QLineEdit()
        self.mood_edit.setPlaceholderText("Example: premium, technical")
        self.aspect_ratio_edit = QLineEdit()
        self.aspect_ratio_edit.setObjectName("creativeBriefAspectRatio")
        self.aspect_ratio_edit.setPlaceholderText("Example: 4:5")
        self.orientation_edit = QLineEdit()
        self.orientation_edit.setObjectName("creativeBriefOrientation")
        self.orientation_edit.setPlaceholderText("Example: portrait")
        self.product_emphasis_edit = QLineEdit()
        self.product_emphasis_edit.setObjectName("creativeBriefProductEmphasis")
        self.product_emphasis_edit.setPlaceholderText("Example: product dominant")
        self.preserve_edit = QLineEdit()
        self.preserve_edit.setObjectName("creativeBriefUserPreserve")
        self.preserve_edit.setPlaceholderText(
            "User creative preserve notes; separate multiple items with ;"
        )
        self.avoid_edit = QLineEdit()
        self.avoid_edit.setObjectName("creativeBriefUserAvoid")
        self.avoid_edit.setPlaceholderText(
            "User creative avoid notes; separate multiple items with ;"
        )
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setObjectName("creativeBriefFreeformNotes")
        self.notes_edit.setPlaceholderText("Optional creative notes")
        self.notes_edit.setMaximumHeight(72)
        self.deliverable_edit = QLineEdit()
        self.deliverable_edit.setPlaceholderText("Example: grounded product prompt")
        brief_form.addRow("Purpose", self.objective_edit)
        brief_form.addRow("Scene / Environment", self.environment_edit)
        brief_form.addRow("Camera", self.camera_edit)
        brief_form.addRow("Shot Type", self.shot_type_edit)
        brief_form.addRow("Lighting", self.lighting_edit)
        brief_form.addRow("Composition", self.composition_edit)
        brief_form.addRow("Mood / Style", self.mood_edit)
        brief_form.addRow("Aspect Ratio", self.aspect_ratio_edit)
        brief_form.addRow("Orientation", self.orientation_edit)
        brief_form.addRow("Product Emphasis", self.product_emphasis_edit)
        brief_form.addRow("User Preserve", self.preserve_edit)
        brief_form.addRow("User Avoid", self.avoid_edit)
        brief_form.addRow("Notes", self.notes_edit)
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
        self.prompt_grounding_metadata = QLabel(
            "No grounded prompt built yet."
        )
        self.prompt_grounding_metadata.setObjectName(
            "promptGroundingMetadata"
        )
        self.prompt_grounding_metadata.setWordWrap(True)
        prompt_layout.addWidget(self.prompt_grounding_metadata)
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

    def _build_products_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("productsWorkspace")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        heading = QLabel("Products")
        heading.setObjectName("productsHeading")
        heading.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(heading)

        intro = QLabel(
            "Browse grounded product intelligence without leaving the creative workspace."
        )
        intro.setObjectName("productsIntro")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        selector_group = QGroupBox("Product / Variant")
        selector_form = QFormLayout(selector_group)
        self.products_product_combo = QComboBox()
        self.products_product_combo.setObjectName("productsProductSelector")
        self.products_variant_combo = QComboBox()
        self.products_variant_combo.setObjectName("productsVariantSelector")
        self.products_variant_combo.setEnabled(False)
        selector_form.addRow("Product", self.products_product_combo)
        selector_form.addRow("Variant", self.products_variant_combo)
        layout.addWidget(selector_group)

        self.products_status = QLabel("")
        self.products_status.setObjectName("productsWorkspaceStatus")
        self.products_status.setWordWrap(True)
        layout.addWidget(self.products_status)

        intelligence_group = QGroupBox("Grounded Product Intelligence")
        intelligence_layout = QVBoxLayout(intelligence_group)
        self.products_identity = QLabel("No product selected.")
        self.products_identity.setObjectName("productsIdentity")
        self.products_identity.setWordWrap(True)
        intelligence_layout.addWidget(self.products_identity)

        self.products_summary = QLabel(
            "Select a product and variant to load grounded intelligence."
        )
        self.products_summary.setObjectName("productsSummary")
        self.products_summary.setWordWrap(True)
        intelligence_layout.addWidget(self.products_summary)

        self.products_facts = QPlainTextEdit()
        self.products_facts.setObjectName("productsFacts")
        self.products_facts.setReadOnly(True)
        self.products_facts.setPlaceholderText("Grounded facts will appear here.")
        intelligence_layout.addWidget(self.products_facts)

        self.products_constraints = QPlainTextEdit()
        self.products_constraints.setObjectName("productsConstraints")
        self.products_constraints.setReadOnly(True)
        self.products_constraints.setPlaceholderText(
            "Preservation constraints will appear here."
        )
        intelligence_layout.addWidget(self.products_constraints)

        self.products_unknowns = QLabel("No unknown/conflict state loaded.")
        self.products_unknowns.setObjectName("productsUnknowns")
        self.products_unknowns.setWordWrap(True)
        intelligence_layout.addWidget(self.products_unknowns)

        self.products_provenance_summary = QLabel(
            "No provenance summary loaded."
        )
        self.products_provenance_summary.setObjectName(
            "productsProvenanceSummary"
        )
        self.products_provenance_summary.setWordWrap(True)
        intelligence_layout.addWidget(self.products_provenance_summary)
        layout.addWidget(intelligence_group, 1)

        search_group = QGroupBox("Search Grounded Facts")
        search_layout = QHBoxLayout(search_group)
        self.products_fact_search = QLineEdit()
        self.products_fact_search.setObjectName("productsFactSearch")
        self.products_fact_search.setPlaceholderText(
            "Search grounded fact labels and values"
        )
        self.products_fact_search_button = QPushButton("Search")
        self.products_fact_search_button.setObjectName(
            "productsFactSearchButton"
        )
        search_layout.addWidget(self.products_fact_search, 1)
        search_layout.addWidget(self.products_fact_search_button)
        layout.addWidget(search_group)

        self.products_search_results = QPlainTextEdit()
        self.products_search_results.setObjectName("productsSearchResults")
        self.products_search_results.setReadOnly(True)
        self.products_search_results.setPlaceholderText(
            "Matching grounded facts will appear here."
        )
        layout.addWidget(self.products_search_results)

        provenance_group = QGroupBox("Provenance")
        provenance_layout = QVBoxLayout(provenance_group)
        provenance_selector_row = QHBoxLayout()
        self.products_provenance_combo = QComboBox()
        self.products_provenance_combo.setObjectName(
            "productsProvenanceSelector"
        )
        self.products_provenance_button = QPushButton("Inspect")
        self.products_provenance_button.setObjectName(
            "productsProvenanceInspectButton"
        )
        provenance_selector_row.addWidget(self.products_provenance_combo, 1)
        provenance_selector_row.addWidget(self.products_provenance_button)
        provenance_layout.addLayout(provenance_selector_row)

        self.products_provenance_detail = QPlainTextEdit()
        self.products_provenance_detail.setObjectName(
            "productsProvenanceDetail"
        )
        self.products_provenance_detail.setReadOnly(True)
        self.products_provenance_detail.setPlaceholderText(
            "Authority, version, status, and source paths will appear here."
        )
        provenance_layout.addWidget(self.products_provenance_detail)
        layout.addWidget(provenance_group)

        self.products_product_combo.currentIndexChanged.connect(
            self._products_product_changed
        )
        self.products_variant_combo.currentIndexChanged.connect(
            self._products_variant_changed
        )
        self.products_fact_search_button.clicked.connect(
            self._search_products_facts
        )
        self.products_fact_search.returnPressed.connect(
            self._search_products_facts
        )
        self.products_provenance_button.clicked.connect(
            self._inspect_products_provenance
        )

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

    def _load_products_workspace(self) -> None:
        self._workspace_product_ids_by_label.clear()
        self._workspace_variant_ids_by_label.clear()
        self._workspace_provenance_refs = ()

        self.products_product_combo.clear()
        self.products_variant_combo.clear()
        self.products_provenance_combo.clear()
        self.products_product_combo.addItem("Choose product...")
        self.products_variant_combo.addItem("Choose variant...")
        self.products_provenance_combo.addItem("Choose provenance...")

        if self._product_intelligence is None:
            self.products_product_combo.setEnabled(False)
            self.products_variant_combo.setEnabled(False)
            self.products_fact_search.setEnabled(False)
            self.products_fact_search_button.setEnabled(False)
            self.products_provenance_combo.setEnabled(False)
            self.products_provenance_button.setEnabled(False)
            self.products_status.setText(
                "Product Intelligence is unavailable in this shell session. "
                "No storage fallback is used."
            )
            return

        self.products_product_combo.setEnabled(True)
        self.products_fact_search.setEnabled(True)
        self.products_fact_search_button.setEnabled(True)
        self.products_provenance_combo.setEnabled(True)
        self.products_provenance_button.setEnabled(True)
        self.products_status.setText(
            "Product Intelligence connected. Select a product and variant."
        )

        for option in self._product_intelligence.product_options:
            self._workspace_product_ids_by_label[option.label] = option.product_id
            self.products_product_combo.addItem(option.label)

    def _products_product_changed(self) -> None:
        label = self.products_product_combo.currentText()
        product_id = self._workspace_product_ids_by_label.get(label)

        self.products_variant_combo.clear()
        self.products_variant_combo.addItem("Choose variant...")
        self._workspace_variant_ids_by_label.clear()
        self._clear_products_context()

        if self._product_intelligence is None or not product_id:
            self.products_variant_combo.setEnabled(False)
            return

        for option in self._product_intelligence.variant_options_for_product(
            product_id
        ):
            self._workspace_variant_ids_by_label[option.label] = option.variant_id
            self.products_variant_combo.addItem(option.label)

        self.products_variant_combo.setEnabled(True)
        self.products_identity.setText(label)
        self.products_summary.setText(
            "Product selected. Choose a variant to load grounded intelligence."
        )

    def _products_variant_changed(self) -> None:
        if self._product_intelligence is None:
            return

        product_label = self.products_product_combo.currentText()
        variant_label = self.products_variant_combo.currentText()
        product_id = self._workspace_product_ids_by_label.get(product_label)
        variant_id = self._workspace_variant_ids_by_label.get(variant_label)

        if not product_id or not variant_id:
            return

        try:
            snapshot = self._product_intelligence.context_snapshot(
                product_id=product_id,
                variant_id=variant_id,
            )
        except Exception as exc:
            self._clear_products_context()
            self.products_identity.setText(
                f"{product_label} / {variant_label}"
            )
            self.products_summary.setText(
                "RCIS could not load grounded product intelligence."
            )
            self.products_status.setText(
                f"Could not load Product Intelligence: {exc}"
            )
            return

        self._render_products_context(snapshot)
        self.products_status.setText("Grounded Product Intelligence loaded.")

    def _clear_products_context(self) -> None:
        self._workspace_provenance_refs = ()
        self.products_identity.setText("No product selected.")
        self.products_summary.setText(
            "Select a product and variant to load grounded intelligence."
        )
        self.products_facts.clear()
        self.products_constraints.clear()
        self.products_unknowns.setText("No unknown/conflict state loaded.")
        self.products_provenance_summary.setText(
            "No provenance summary loaded."
        )
        self.products_search_results.clear()
        self.products_provenance_combo.clear()
        self.products_provenance_combo.addItem("Choose provenance...")
        self.products_provenance_detail.clear()

    def _render_products_context(
        self,
        snapshot: ProductContextSnapshot,
    ) -> None:
        self.products_identity.setText(snapshot.display_name)
        self.products_summary.setText(
            snapshot.summary or "Grounded product context loaded."
        )
        self.products_facts.setPlainText(
            "\n".join(
                f"{fact.label}: {fact.value} [{fact.scope}]"
                for fact in snapshot.fact_groups
            )
            or "No grounded facts available."
        )
        self.products_constraints.setPlainText(
            "\n".join(
                f"{constraint.rule_text} [{constraint.scope}]"
                for constraint in snapshot.preservation_constraints
            )
            or "No grounded preservation constraints available."
        )

        unknown_lines = [
            unknown.user_facing_label
            for unknown in snapshot.unknown_topics
        ]
        unknown_lines.extend(snapshot.conflicts)
        self.products_unknowns.setText(
            "\n".join(unknown_lines)
            or "No unknown/conflict items reported."
        )
        self.products_provenance_summary.setText(
            snapshot.provenance_summary
            or "No provenance summary available."
        )

        refs = tuple(
            dict.fromkeys(
                reference_id
                for fact in snapshot.fact_groups
                for reference_id in fact.provenance_refs
            )
        )
        self._workspace_provenance_refs = refs
        self.products_provenance_combo.clear()
        self.products_provenance_combo.addItem("Choose provenance...")
        for reference_id in refs:
            self.products_provenance_combo.addItem(reference_id)
        self.products_provenance_detail.clear()
        self.products_search_results.clear()

    def _current_workspace_identity(
        self,
    ) -> tuple[str | None, str | None]:
        product_id = self._workspace_product_ids_by_label.get(
            self.products_product_combo.currentText()
        )
        variant_id = self._workspace_variant_ids_by_label.get(
            self.products_variant_combo.currentText()
        )
        return product_id, variant_id

    def _search_products_facts(self) -> None:
        if self._product_intelligence is None:
            self.products_status.setText(
                "Product Intelligence is unavailable; no storage fallback is used."
            )
            return

        product_id, variant_id = self._current_workspace_identity()
        query = self.products_fact_search.text().strip()
        if not product_id or not variant_id:
            self.products_status.setText(
                "Choose a product and variant before searching facts."
            )
            return
        if not query:
            self.products_status.setText("Enter a fact search term.")
            return

        try:
            matches = self._product_intelligence.search_facts(
                query,
                product_id=product_id,
                variant_id=variant_id,
            )
        except Exception as exc:
            self.products_status.setText(f"Could not search grounded facts: {exc}")
            return

        self.products_search_results.setPlainText(
            "\n".join(
                f"{fact.label}: {fact.value} [{fact.scope}]"
                for fact in matches
            )
            or "No grounded fact matches."
        )
        self.products_status.setText(
            f"Grounded fact search complete: {len(matches)} match"
            f"{'' if len(matches) == 1 else 'es'}."
        )

    def _inspect_products_provenance(self) -> None:
        if self._product_intelligence is None:
            self.products_status.setText(
                "Product Intelligence is unavailable; no storage fallback is used."
            )
            return

        reference_id = self.products_provenance_combo.currentText()
        if reference_id not in self._workspace_provenance_refs:
            self.products_status.setText(
                "Choose a provenance reference to inspect."
            )
            return

        try:
            provenance = self._product_intelligence.provenance(reference_id)
        except Exception as exc:
            self.products_status.setText(
                f"Could not load provenance: {exc}"
            )
            return

        source_paths = tuple(provenance.source_paths)
        lines = [
            f"Reference: {provenance.reference_id}",
            f"Type: {provenance.source_type or 'unknown'}",
            f"Authority: {provenance.authority or 'unknown'}",
            f"Status: {provenance.status or 'unknown'}",
            f"Version: {provenance.version or 'unknown'}",
            "Source paths:",
        ]
        lines.extend(
            f"- {path}" for path in source_paths
        )
        if not source_paths:
            lines.append("- none")
        self.products_provenance_detail.setPlainText("\n".join(lines))
        self.products_status.setText("Provenance loaded.")

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

    @staticmethod
    def _split_user_instructions(value: str) -> tuple[str, ...]:
        return tuple(
            item.strip()
            for item in value.split(";")
            if item.strip()
        )

    def current_brief(self) -> CreativeBrief:
        return CreativeBrief(
            objective=self.objective_edit.text(),
            deliverable=self.deliverable_edit.text(),
            environment=self.environment_edit.text(),
            camera_angle=self.camera_edit.text(),
            shot_type=self.shot_type_edit.text(),
            lighting_style=self.lighting_edit.text(),
            composition=self.composition_edit.text(),
            mood_style=self.mood_edit.text(),
            aspect_ratio=self.aspect_ratio_edit.text(),
            orientation=self.orientation_edit.text(),
            product_emphasis=self.product_emphasis_edit.text(),
            preserve_constraints=self._split_user_instructions(
                self.preserve_edit.text()
            ),
            avoid_constraints=self._split_user_instructions(
                self.avoid_edit.text()
            ),
            freeform_notes=self.notes_edit.toPlainText(),
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
        product_label = self.product_combo.currentText()
        variant_label = self.variant_combo.currentText()
        product_id = self._product_ids_by_label.get(product_label)
        variant_id = self._variant_ids_by_label.get(variant_label)
        if not product_id or not variant_id:
            self.create_feedback.setText(
                "Choose a product and variant before building a prompt."
            )
            return

        if self._creative_prompt_composer is not None:
            try:
                result = self._creative_prompt_composer.compose(
                    product_id=product_id,
                    variant_id=variant_id,
                    brief=self.current_brief(),
                )
            except Exception as exc:
                self.create_feedback.setText(f"Could not build prompt: {exc}")
                return

            self.prompt_preview.setPlainText(result.prompt_text)
            used_knowledge = tuple(result.used_knowledge_ids)
            used_assets = tuple(result.used_asset_ids)
            missing = tuple(result.missing_knowledge)
            conflicts = tuple(result.conflicts)
            self.prompt_grounding_metadata.setText(
                "Grounding: "
                + str(result.grounding_status)
                + " | Knowledge: "
                + (", ".join(used_knowledge) or "none")
                + " | Assets: "
                + (", ".join(used_assets) or "none")
                + " | Missing: "
                + (", ".join(missing) or "none")
                + " | Conflicts: "
                + (", ".join(conflicts) or "none")
            )
            if (
                result.grounding_status == "PASSED"
                and bool(result.prompt_text.strip())
                and not missing
                and not conflicts
            ):
                self.create_feedback.setText("Grounded prompt ready.")
            else:
                self.create_feedback.setText(
                    "Grounded prompt could not be completed safely; "
                    "review grounding diagnostics."
                )
            return

        if self._adapter is None:
            self.create_feedback.setText(
                "Grounded prompt adapter is not connected in this shell proof."
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
        self.prompt_grounding_metadata.setText(
            "Compatibility path result; structured PC3 grounding metadata "
            "is unavailable on the legacy adapter."
        )
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