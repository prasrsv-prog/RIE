"""Parallel PySide6 product-completion shell.

This is a migration-foundation UI.  It does not replace the current Tkinter
production entrypoint and does not access governed storage directly.
"""

from __future__ import annotations

from dataclasses import asdict

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
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

from rie.application.creative_prompt_composer import (
    CreativePromptBrief,
    CreativePromptComposer,
)
from rie.application.governed_creative_workflow_application_service import (
    GovernedCreativeWorkflowApplicationAssessment,
)
from rie.application.product_intelligence_query import ProductIntelligenceQuery
from rie.application.safe_operator_dashboard_adapter import (
    STATUS_DENIED,
    STATUS_INVALID,
    STATUS_READY,
    SafeOperatorDashboardRequest,
    SafeOperatorDashboardResult,
)
from rie.application.visual_reference_asset_query import VisualReferenceAssetQuery
from rie.application.visual_generation_provider import (
    VisualGenerationRequest,
    VisualGenerationResult,
)
from rie.domain.governed_creative_workflow_request import (
    GovernedCreativeWorkflowRequest,
)

from rie.ui.local_operator_settings import load_remembered_intake_root
from rie.ui.local_operator_workspace import load_workspace, append_pyside_history_prompt
from rie.ui.studio_localization import Localizer, SUPPORTED_LOCALES
from rie.ui.studio_ui_preferences import load_preferred_locale, save_preferred_locale
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
    "Approvals",
    "Workflow",
    "Projects",
    "History",
    "Presets",
    "Settings",
)

# Stable English identities continue to index nine existing workspace pages.
# Only the user-facing labels are localized; routes and backend stay unchanged.
NAVIGATION_LABELS = (
    "Buat Visual", "Produk", "Foto Produk", "Persetujuan", "Alur Kerja",
    "Proyek", "Riwayat", "Preset", "Pengaturan",
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
                selected_reference_asset_ids=tuple(
                    brief.selected_reference_asset_ids
                ),
                freeform_notes=brief.freeform_notes,
            ),
        )


class VisualReferenceAssetPresentationAdapter:
    """Expose PC4 visual-reference reads without UI storage access."""

    def __init__(self, query: Any) -> None:
        self._query = query

    @property
    def product_options(self) -> tuple[Any, ...]:
        return tuple(self._query.product_options)

    def variant_options_for_product(self, product_id: str) -> tuple[Any, ...]:
        return tuple(self._query.variant_options_for_product(product_id))

    def assets_for_selection(
        self,
        *,
        product_id: str,
        variant_id: str,
    ) -> tuple[Any, ...]:
        return tuple(
            self._query.list_assets(
                product_id=product_id,
                variant_id=variant_id,
            )
        )

    def preview_bytes(self, asset_id: str) -> bytes:
        return self._query.load_preview_bytes(asset_id)


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
        visual_reference_asset_query: Any | None = None,
        visual_generation_provider: Any | None = None,
        operator_dashboard_builder: Any | None = None,
        governed_workflow_assessor: Any | None = None,
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
        if visual_generation_provider is not None and not callable(
            getattr(visual_generation_provider, "generate", None)
        ):
            raise TypeError(
                "visual_generation_provider must expose generate"
            )
        self._visual_generation_provider = visual_generation_provider
        if operator_dashboard_builder is not None and not callable(
            operator_dashboard_builder
        ):
            raise TypeError("operator_dashboard_builder must be callable")
        self._operator_dashboard_builder = operator_dashboard_builder
        if governed_workflow_assessor is not None and not callable(
            governed_workflow_assessor
        ):
            raise TypeError("governed_workflow_assessor must be callable")
        self._governed_workflow_assessor = governed_workflow_assessor

        self._visual_reference_assets = (
            VisualReferenceAssetPresentationAdapter(visual_reference_asset_query)
            if visual_reference_asset_query is not None
            else None
        )
        self._product_ids_by_label: dict[str, str] = {}
        self._variant_ids_by_label: dict[str, str] = {}
        self._workspace_product_ids_by_label: dict[str, str] = {}
        self._workspace_variant_ids_by_label: dict[str, str] = {}
        self._workspace_provenance_refs: tuple[str, ...] = ()
        self._create_reference_assets_by_ref: dict[str, Any] = {}
        self._assets_workspace_product_ids_by_label: dict[str, str] = {}
        self._assets_workspace_variant_ids_by_label: dict[str, str] = {}
        self._assets_workspace_assets_by_ref: dict[str, Any] = {}
        self._history_records: tuple[dict, ...] = ()
        self._history_loaded = False
        self._history_copy_feedback_active = False
        self._presets_records: tuple[dict, ...] = ()

        self._pyside_history_pending: dict | None = None
        self._pyside_history_feedback_key = ""
        self._localizer = Localizer(load_preferred_locale())
        self._h3d_live_status: dict[QLabel, tuple[str, str]] = {}
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(1360, 840)
        self.setMinimumSize(1040, 680)

        self.navigation = QListWidget()
        self.navigation.setObjectName("primaryNavigation")
        self.navigation.addItems(list(NAVIGATION_LABELS))
        self.navigation.setSpacing(5)
        self.navigation.setStyleSheet("""
            QListWidget#primaryNavigation {
                background: #19222e; border: 0; font-size: 14px;
                color: #e4ebf5; padding: 5px;
            }
            QListWidget#primaryNavigation::item {
                padding: 11px 9px; border-radius: 7px;
            }
            QListWidget#primaryNavigation::item:selected {
                background: #2058a1; color: #ffffff;
            }
        """)
        self.navigation.setMinimumWidth(174)
        for row in range(3, len(NAVIGATION)):
            self.navigation.setRowHidden(row, True)
        self.nav_more_button = QPushButton("Lainnya (6)  ▸")
        self.nav_more_button.setObjectName("studioMoreNavigation")
        self.nav_more_button.setCheckable(True)
        self.nav_more_button.toggled.connect(self._toggle_extra_navigation)
        nav_panel = QWidget()
        nav_panel.setObjectName("studioNavigationPanel")
        nav_panel.setFixedWidth(191)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(7, 13, 7, 11)
        nav_layout.setSpacing(8)
        nav_label = QLabel("STUDIO KREATIF")
        nav_label.setObjectName("studioNavigationHeading")
        nav_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #b5c5d8;")
        self._h2_nav_heading = nav_label
        nav_layout.addWidget(nav_label)
        nav_layout.addWidget(self.navigation, 1)
        nav_layout.addWidget(self.nav_more_button)
        self._h2_language_label = QLabel("Bahasa antarmuka")
        self._h2_language_label.setObjectName("studioLanguageLabel")
        nav_layout.addWidget(self._h2_language_label)
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("studioLanguageSelector")
        self.language_combo.addItem("Bahasa Indonesia", "id-ID")
        self.language_combo.addItem("English", "en-US")
        self.language_combo.setCurrentIndex(self.language_combo.findData(self._localizer.locale))
        self.language_combo.currentIndexChanged.connect(self._h2_language_changed)
        nav_layout.addWidget(self.language_combo)

        self.pages = QStackedWidget()
        self.pages.setObjectName("workspacePages")

        self._create_page = self._build_create_page()
        self.pages.addWidget(self._create_page)
        self._products_page = self._build_products_page()
        self.pages.addWidget(self._products_page)
        self._assets_page = self._build_assets_page()
        self.pages.addWidget(self._assets_page)
        self._approvals_page = self._build_approvals_page()
        self.pages.addWidget(self._approvals_page)
        self._workflow_page = self._build_workflow_page()
        self.pages.addWidget(self._workflow_page)
        for name in NAVIGATION[5:]:
            if name == "History":
                self._history_page = self._build_history_page()
                self.pages.addWidget(self._history_page)
            elif name == "Presets":
                self._presets_page = self._build_presets_page()
                self.pages.addWidget(self._presets_page)
            else:
                self.pages.addWidget(self._placeholder_page(name))

        self.product_context_panel = self._build_product_context_panel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("mainThreePaneSplitter")
        splitter.addWidget(nav_panel)
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
        status.showMessage("Mode lokal — layanan AI eksternal belum diaktifkan")
        self.setStatusBar(status)

        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.currentRowChanged.connect(self._reveal_selected_navigation)
        self.navigation.setCurrentRow(0)

        if self._adapter is not None or self._product_intelligence is not None:
            self._load_products()
        self._load_products_workspace()
        self._load_assets_workspace()
        self._h3b_bind_workspace_chrome()
        self._h2_apply_language()



    def _h2_update_more_navigation_text(self) -> None:
        expanded = self.nav_more_button.isChecked()
        key = "nav.hide_more" if expanded else "nav.more"
        value = self._localizer.tr(key, **({"count": len(NAVIGATION) - 3} if not expanded else {}))
        self.nav_more_button.setText(value + ("  ▾" if expanded else "  ▸"))

    def _h2_update_advanced_toggle_text(self, expanded: bool) -> None:
        key = "create.advanced_hide" if expanded else "create.advanced_show"
        self.advanced_brief_toggle.setText(self._localizer.tr(key) + ("  ▾" if expanded else "  ▸"))

    def _h2_update_grounding_toggle_text(self, expanded: bool) -> None:
        key = "prompt.details_hide" if expanded else "prompt.details_show"
        self.create_grounding_details_toggle.setText(self._localizer.tr(key) + ("  ▾" if expanded else "  ▸"))

    def _h2_language_changed(self, index: int) -> None:
        locale = self.language_combo.itemData(index)
        if locale not in SUPPORTED_LOCALES or locale == self._localizer.locale:
            return
        # Persistence commits first; in-memory state is untouched on failure.
        try:
            save_preferred_locale(locale)
        except (OSError, ValueError) as exc:
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(self.language_combo.findData(self._localizer.locale))
            self.language_combo.blockSignals(False)
            self.statusBar().showMessage("Cannot save interface language: " + str(exc))
            return
        self._localizer.set_locale(locale)
        self._h2_apply_language()

    def _h2_apply_language(self) -> None:
        # Change display strings only; never rebuild controls or payloads.
        tr = self._localizer.tr
        nav_keys = (
            "nav.create", "nav.products", "nav.assets", "nav.approvals",
            "nav.workflow", "nav.projects", "nav.history", "nav.presets", "nav.settings",
        )
        for row, key in enumerate(nav_keys):
            self.navigation.item(row).setText(tr(key))
        self._h2_nav_heading.setText(tr("nav.heading"))
        self._h2_language_label.setText(tr("language.label"))
        self._h2_update_more_navigation_text()
        self.statusBar().showMessage(tr("provider.local_mode"))
        groups = (
            ("createProductCard", "create.step.product"),
            ("createConceptCard", "create.step.concept"),
            ("createReferenceCard", "create.step.reference"),
            ("createReviewCard", "create.step.review"),
        )
        for name, key in groups:
            self._create_page.findChild(QGroupBox, name).setTitle(tr(key))
        self._create_page.findChild(QLabel, "createHeading").setText(
            "Buat Visual Produk" if self._localizer.locale == "id-ID"
            else "Create Product Visual"
        )
        self._create_page.findChild(QLabel, "createIntro").setText(tr("create.instruction"))
        for name, key in (
            ("createStepProduct", "create.step.product"),
            ("createStepConcept", "create.step.concept"),
            ("createStepReferences", "create.step.reference"),
            ("createStepReview", "create.step.review"),
        ):
            self._create_page.findChild(QLabel, name).setText(tr(key))
        for form, entries in (
            (self._h2_product_form, ((self.product_combo, "create.product"), (self.variant_combo, "create.variant"))),
            (self._h2_brief_form, (
                (self.objective_edit,"create.objective"), (self.environment_edit,"create.environment"),
                (self.camera_edit,"create.camera"), (self.deliverable_edit,"create.output"),
                (self.notes_edit,"create.notes"))),
            (self._h2_advanced_form, (
                (self.shot_type_edit,"create.shot_type"),(self.lighting_edit,"create.lighting"),
                (self.composition_edit,"create.composition"),(self.mood_edit,"create.mood"),
                (self.aspect_ratio_edit,"create.aspect_ratio"),(self.orientation_edit,"create.orientation"),
                (self.product_emphasis_edit,"create.product_emphasis"),
                (self.preserve_edit,"create.preserve"),(self.avoid_edit,"create.avoid"))),
        ):
            for widget, key in entries:
                form.labelForField(widget).setText(tr(key))
        for widget, key in (
            (self.objective_edit,"create.objective_hint"),
            (self.environment_edit,"create.environment_hint"),
            (self.camera_edit,"create.camera_hint"),
            (self.deliverable_edit,"create.output_hint"),
            (self.notes_edit,"create.notes_hint"),
        ):
            if widget is self.deliverable_edit and self._localizer.locale == "id-ID":
                # Preserve the existing required-field hint during this staged rollout.
                widget.setPlaceholderText("Wajib: contoh foto produk untuk katalog daring")
            else:
                widget.setPlaceholderText(tr(key))
        self._h2_update_advanced_toggle_text(self.advanced_brief_toggle.isChecked())
        self._h2_update_grounding_toggle_text(self.create_grounding_details_toggle.isChecked())
        self.prompt_button.setText(tr("prompt.build"))
        self.copy_prompt_button.setText(tr("prompt.copy"))
        self.history_save_button.setText(tr("history.save_action"))
        if self._pyside_history_feedback_key:
            self.history_save_feedback.setText(tr(self._pyside_history_feedback_key))
        if self._copy_prompt_feedback_active:
            self.copy_prompt_feedback.setText(tr("prompt.copy_success"))
        self.prompt_preview.setPlaceholderText(tr("prompt.empty"))
        if self._visual_generation_provider is None:
            self.visual_button.setText(tr("provider.generate_disabled"))
            self.visual_button.setToolTip(tr("provider.rights_warning"))
        self.create_safety_note.setText(tr("provider.rights_warning"))
        self._refresh_create_grounding_status()
        self._h3_context_chrome()
        self._h3_reference_status()
        self._h3b_apply_workspace_chrome()
        self._h3d_apply_live_status()
        self._history_apply_language()
        self._presets_apply_language()


    def _h3_context_chrome(self) -> None:
        """Translate only chrome, never product facts, rights evidence or payloads."""
        tr = self._localizer.tr
        self._h3_context_heading.setText(tr("context.title"))
        for original, key in (
            ("Hal yang harus dipertahankan", "context.constraints"),
            ("Fakta produk (rinci)", "context.facts"),
            ("Hak penggunaan referensi", "context.reference_rights"),
            ("Unknown / Conflict", "context.conflicts"),
        ):
            self._h3_context_section_titles[original].setText(tr(key))
        self.context_governance_note.setText(tr("reference.local_only"))
        self._h3_technical_toggle_text(self.context_technical_toggle.isChecked())

    def _h3_technical_toggle_text(self, expanded: bool) -> None:
        key = "context.details_hide" if expanded else "context.details_show"
        self.context_technical_toggle.setText(
            self._localizer.tr(key) + ("  ▾" if expanded else "  ▸")
        )

    def _h3_reference_status(self) -> None:
        """Re-render selection text without re-querying images or modifying IDs."""
        tr = self._localizer.tr
        selected = []
        for row in range(self.reference_asset_list.count()):
            item = self.reference_asset_list.item(row)
            if not item.isSelected():
                continue
            ref = item.data(Qt.ItemDataRole.UserRole)
            asset = self._create_reference_assets_by_ref.get(ref)
            if asset is not None and asset.available and asset.asset_id is not None:
                selected.append(asset)
        if selected:
            self.reference_asset_detail.setText(
                tr("reference.selected_count", count=len(selected)) + "\n"
                + tr("reference.preview", filename=selected[0].filename) + "\n"
                + tr("reference.local_only")
            )
        elif self.reference_asset_list.count() > 0:
            self.reference_asset_detail.setText(
                tr("reference.none") + " " + tr("reference.local_only")
            )
        picture = self.reference_asset_preview.pixmap()
        if picture is None or picture.isNull():
            if self.reference_asset_preview.text() in (
                "No reference selected.",
                "Belum ada foto referensi yang dipilih.",
                "No reference photo selected yet.",
            ):
                self.reference_asset_preview.setText(tr("reference.none"))


    def _h3b_bind_workspace_chrome(self) -> None:
        """Capture *only* static presentation widgets, never business data fields."""
        from PySide6.QtWidgets import QFormLayout
        self._h3b_term_keys = {'Products': 'workspace.products_title', 'Assets': 'workspace.assets_title', 'Approvals': 'workspace.approvals_title', 'Workflow': 'workspace.workflow_title', 'Product / Variant': 'workspace.product_variant', 'Grounded Product Intelligence': 'workspace.grounded_intelligence', 'Search Grounded Facts': 'workspace.search_facts', 'Provenance': 'workspace.provenance', 'Approved Visual References': 'workspace.approved_references', 'Approval Request': 'workspace.approval_request', 'Safe Dashboard Projection': 'workspace.safe_dashboard', 'Governed Workflow Request': 'workspace.workflow_request', 'Transition Assessment': 'workspace.transition_assessment', 'Search': 'workspace.search', 'Inspect': 'workspace.inspect', 'Evaluate Approval Request': 'workspace.evaluate_approval', 'Assess Workflow Transition': 'workspace.assess_transition', 'Product': 'workspace.product', 'Variant': 'workspace.variant', 'Request ID': 'workspace.request_id', 'Operator': 'workspace.operator', 'Role': 'workspace.role', 'Target Type': 'workspace.target_type', 'Target Reference': 'workspace.target_reference', 'Action': 'workspace.action', 'Reason Reference': 'workspace.reason_reference', 'Audit Context': 'workspace.audit_context', 'Audit Limit': 'workspace.audit_limit', 'Idempotency Key': 'workspace.idempotency_key', 'Project Reference': 'workspace.project_reference', 'Campaign Reference': 'workspace.campaign_reference', 'Creative Brief Reference': 'workspace.brief_reference', 'Approved Knowledge': 'workspace.approved_knowledge', 'Governed Assets': 'workspace.governed_assets', 'Instruction Reference': 'workspace.instruction_reference', 'Instruction Authority': 'workspace.instruction_authority', 'Requesting Actor': 'workspace.requesting_actor', 'Request Timestamp': 'workspace.request_timestamp', 'Contract Name': 'workspace.contract_name', 'Contract Version': 'workspace.contract_version', 'Output Purpose': 'workspace.output_purpose', 'Review Policy': 'workspace.review_policy', 'External Handoff': 'workspace.external_handoff', 'Current State': 'workspace.current_state', 'Requested State': 'workspace.requested_state', 'Responsible Kind': 'workspace.responsible_kind', 'Responsible Reference': 'workspace.responsible_reference', 'Assessment Timestamp': 'workspace.assessment_timestamp', 'Evidence References': 'workspace.evidence_references', 'Reason Codes': 'workspace.reason_codes', 'Manual Handoff Reference': 'workspace.manual_handoff_reference', 'Creative Result Candidate': 'workspace.creative_candidate', 'Accepted Gate 16 Decision': 'workspace.gate16_decision', 'Accepted Gate 15 Asset': 'workspace.gate15_asset', 'Manual external-tool handoff is explicitly declared': 'workspace.manual_handoff_declared'}
        labels = {
            'Products': 'workspace.products_title',
            'Assets': 'workspace.assets_title',
            'Approvals': 'workspace.approvals_title',
            'Workflow': 'workspace.workflow_title',
        }
        names = ('productsHeading', 'assetsHeading', 'approvalsHeading',
                 'creativeWorkflowHeading')
        self._h3b_bindings = []
        pages = (self._products_page, self._assets_page,
                 self._approvals_page, self._workflow_page)
        for page, name in zip(pages, names):
            heading = page.findChild(QLabel, name)
            if heading is None or heading.text() not in labels:
                raise RuntimeError('C20-H3B static heading missing: ' + name)
            self._h3b_bindings.append((heading, 'text', labels[heading.text()]))
            for group in page.findChildren(QGroupBox):
                key = self._h3b_term_keys.get(group.title())
                if key is not None:
                    self._h3b_bindings.append((group, 'title', key))
            for button in page.findChildren(QPushButton):
                key = self._h3b_term_keys.get(button.text())
                if key is not None:
                    self._h3b_bindings.append((button, 'text', key))
            for form in page.findChildren(QFormLayout):
                for row in range(form.rowCount()):
                    entry = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
                    label = entry.widget() if entry is not None else None
                    if isinstance(label, QLabel):
                        key = self._h3b_term_keys.get(label.text())
                        if key is not None:
                            self._h3b_bindings.append((label, 'text', key))
            for check in page.findChildren(QCheckBox):
                key = self._h3b_term_keys.get(check.text())
                if key is not None:
                    self._h3b_bindings.append((check, 'text', key))
        if len(self._h3b_bindings) < 30:
            raise RuntimeError('C20-H3B insufficient static chrome bindings')

    def _h3b_apply_workspace_chrome(self) -> None:
        """Switch chrome in place; do not clear forms or re-run a service."""
        for widget, kind, key in self._h3b_bindings:
            label = self._localizer.tr(key)
            if kind == 'title':
                widget.setTitle(label)
            else:
                widget.setText(label)


    def _h3d_set_status(self, widget: QLabel, key: str) -> None:
        """Mark a human-readable status as locally owned, not domain evidence."""
        value = self._localizer.tr(key)
        widget.setText(value)
        self._h3d_live_status[widget] = (key, value)

    def _h3d_apply_live_status(self) -> None:
        """Translate only unchanged, H3D-owned UI statuses on locale switch.

        A later domain/service message must never be overwritten by an old key.
        """
        for widget, (key, previous_text) in tuple(self._h3d_live_status.items()):
            if widget.text() != previous_text:
                del self._h3d_live_status[widget]
                continue
            translated = self._localizer.tr(key)
            widget.setText(translated)
            self._h3d_live_status[widget] = (key, translated)

    def _toggle_extra_navigation(self, expanded: bool) -> None:
        """Display all existing secondary pages; never remove or reindex routes."""
        for row in range(3, len(NAVIGATION)):
            self.navigation.setRowHidden(row, not expanded)
        self._h2_update_more_navigation_text()

    def _reveal_selected_navigation(self, row: int) -> None:
        # Existing workflow tests and deep navigation retain their exact row IDs.
        if row >= 3 and not self.nav_more_button.isChecked():
            self.nav_more_button.setChecked(True)
        if row == NAVIGATION.index("History"):
            self._history_refresh_workspace()
        elif row == NAVIGATION.index("Presets"):
            self._presets_refresh_workspace()

    def _build_create_page(self) -> QWidget:
        """C20-A visual-first composition; existing contracts and signals unchanged."""
        page = QScrollArea()
        page.setObjectName("createPageScrollArea")
        page.setWidgetResizable(True)
        page.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setObjectName("visualFirstCreateContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(22, 18, 22, 22)
        layout.setSpacing(16)
        page.setStyleSheet("""
            QWidget#visualFirstCreateContent { background-color: #111820; }
            QLabel#createHeading { color: #f3f6fc; font-size: 24px; font-weight: 700; }
            QLabel#createIntro { color: #aebdcc; font-size: 12px; }
            QLabel#createStepProduct, QLabel#createStepConcept,
            QLabel#createStepReferences, QLabel#createStepReview {
                border: 1px solid #344357; border-radius: 9px;
                padding: 12px 6px; background: #1c2633;
                color: #d6e0ee; font-weight: 600;
            }
            QLabel#createStepProduct { background: #163a6e; border-color: #367de2; }
            QGroupBox#createProductCard, QGroupBox#createConceptCard,
            QGroupBox#createReferenceCard, QGroupBox#createReviewCard {
                background-color: #19232e; border: 1px solid #334152;
                border-radius: 12px; margin-top: 15px;
                padding: 12px;
                color: #edf2fa; font-size: 12px; font-weight: 600;
            }
            QGroupBox#createProductCard::title, QGroupBox#createConceptCard::title,
            QGroupBox#createReferenceCard::title, QGroupBox#createReviewCard::title {
                subcontrol-origin: margin; left: 14px;
                padding: 0 6px; color: #eff5ff;
            }
            QPushButton#createAdvancedToggle {
                background: #273649; color: #dbe8f6; border: 1px solid #42546d;
                border-radius: 7px; padding: 8px 10px; text-align: left;
            }
            QLabel#createSafetyNote { color: #c9bdf5; font-size: 14px; }
            QWidget#visualFirstCreateContent QLabel { font-size: 14px; }
            QWidget#visualFirstCreateContent QLineEdit,
            QWidget#visualFirstCreateContent QComboBox {
                font-size: 14px; min-height: 24px; padding: 4px 7px;
            }
            QWidget#visualFirstCreateContent QPlainTextEdit {
                font-size: 14px; padding: 8px;
            }
            QWidget#visualFirstCreateContent QPushButton {
                font-size: 14px; min-height: 26px;
            }
            QListWidget#createReferenceAssetList { font-size: 13px; }
            QLabel#createGroundingStatus { color: #b9edce; font-size: 14px; }
        """)

        heading = QLabel("Buat Visual Produk")
        heading.setObjectName("createHeading")
        layout.addWidget(heading)

        intro = QLabel(
            "Pilih produk, tentukan konsep, pilih foto, lalu tinjau prompt Anda."
        )
        intro.setWordWrap(True)
        intro.setObjectName("createIntro")
        layout.addWidget(intro)

        steps = QHBoxLayout()
        steps.setSpacing(8)
        for name, label_text in (
            ("createStepProduct", "1  Produk"),
            ("createStepConcept", "2  Konsep"),
            ("createStepReferences", "3  Foto referensi"),
            ("createStepReview", "4  Tinjau prompt"),
        ):
            step = QLabel(label_text)
            step.setObjectName(name)
            step.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step.setToolTip("Panduan urutan kerja, bukan status penyelesaian")
            steps.addWidget(step, 1)
        layout.addLayout(steps)

        top_cards = QHBoxLayout()
        top_cards.setSpacing(14)

        product_group = QGroupBox("1. Pilih Produk")
        product_group.setObjectName("createProductCard")
        product_form = QFormLayout(product_group)
        self._h2_product_form = product_form
        product_form.setVerticalSpacing(13)
        self.product_combo = QComboBox()
        self.product_combo.setObjectName("productSelector")
        self.product_combo.addItem("Choose product...")
        self.variant_combo = QComboBox()
        self.variant_combo.setObjectName("variantSelector")
        self.variant_combo.addItem("Choose variant...")
        self.variant_combo.setEnabled(False)
        product_form.addRow("Produk", self.product_combo)
        product_form.addRow("Varian", self.variant_combo)
        top_cards.addWidget(product_group, 1)

        brief_group = QGroupBox("2. Tentukan Konsep Visual")
        brief_group.setObjectName("createConceptCard")
        brief_layout = QVBoxLayout(brief_group)
        brief_layout.setSpacing(9)
        brief_form = QFormLayout()
        self._h2_brief_form = brief_form
        brief_form.setVerticalSpacing(10)
        self.objective_edit = QLineEdit()
        self.objective_edit.setPlaceholderText("Contoh: foto hero untuk katalog produk")
        self.environment_edit = QLineEdit()
        self.environment_edit.setPlaceholderText("Contoh: studio profesional")
        self.camera_edit = QLineEdit()
        self.camera_edit.setPlaceholderText("Contoh: tampak depan tiga perempat")
        self.deliverable_edit = QLineEdit()
        self.deliverable_edit.setObjectName("creativeBriefRequiredOutput")
        self.deliverable_edit.setPlaceholderText(
            "Wajib: contoh foto produk untuk katalog daring"
        )
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setObjectName("creativeBriefFreeformNotes")
        self.notes_edit.setPlaceholderText("Ceritakan ide visual Anda (opsional)")
        self.notes_edit.setMaximumHeight(64)
        brief_form.addRow("Tujuan", self.objective_edit)
        brief_form.addRow("Suasana (wajib)", self.environment_edit)
        brief_form.addRow("Sudut pandang (wajib)", self.camera_edit)
        brief_form.addRow("Hasil (wajib)", self.deliverable_edit)
        brief_form.addRow("Ide tambahan", self.notes_edit)
        brief_layout.addLayout(brief_form)

        self.advanced_brief_toggle = QPushButton("Pengaturan Lanjutan  ▸")
        self.advanced_brief_toggle.setObjectName("createAdvancedToggle")
        self.advanced_brief_toggle.setCheckable(True)
        self.advanced_brief_toggle.setChecked(False)
        brief_layout.addWidget(self.advanced_brief_toggle)
        self.advanced_brief_panel = QWidget()
        self.advanced_brief_panel.setObjectName("createAdvancedPanel")
        advanced_form = QFormLayout(self.advanced_brief_panel)
        self._h2_advanced_form = advanced_form
        advanced_form.setVerticalSpacing(9)
        self.shot_type_edit = QLineEdit()
        self.shot_type_edit.setObjectName("creativeBriefShotType")
        self.shot_type_edit.setPlaceholderText("Contoh: foto produk tampak sedang")
        self.lighting_edit = QLineEdit()
        self.lighting_edit.setPlaceholderText("Contoh: cahaya studio lembut dari samping")
        self.composition_edit = QLineEdit()
        self.composition_edit.setPlaceholderText("Contoh: produk di tengah dengan latar sederhana")
        self.mood_edit = QLineEdit()
        self.mood_edit.setPlaceholderText("Contoh: premium dan profesional")
        self.aspect_ratio_edit = QLineEdit()
        self.aspect_ratio_edit.setObjectName("creativeBriefAspectRatio")
        self.aspect_ratio_edit.setPlaceholderText("Example: 4:5")
        self.orientation_edit = QLineEdit()
        self.orientation_edit.setObjectName("creativeBriefOrientation")
        self.orientation_edit.setPlaceholderText("Contoh: vertikal")
        self.product_emphasis_edit = QLineEdit()
        self.product_emphasis_edit.setObjectName("creativeBriefProductEmphasis")
        self.product_emphasis_edit.setPlaceholderText("Contoh: produk memenuhi sebagian besar bingkai")
        self.preserve_edit = QLineEdit()
        self.preserve_edit.setObjectName("creativeBriefUserPreserve")
        self.preserve_edit.setPlaceholderText(
            "Hal yang harus dipertahankan, pisahkan dengan ;"
        )
        self.avoid_edit = QLineEdit()
        self.avoid_edit.setObjectName("creativeBriefUserAvoid")
        self.avoid_edit.setPlaceholderText(
            "Hal yang perlu dihindari, pisahkan dengan ;"
        )
        advanced_form.addRow("Jenis shot", self.shot_type_edit)
        advanced_form.addRow("Pencahayaan", self.lighting_edit)
        advanced_form.addRow("Komposisi", self.composition_edit)
        advanced_form.addRow("Gaya / suasana", self.mood_edit)
        advanced_form.addRow("Rasio aspek", self.aspect_ratio_edit)
        advanced_form.addRow("Orientasi", self.orientation_edit)
        advanced_form.addRow("Fokus produk", self.product_emphasis_edit)
        advanced_form.addRow("Harus dipertahankan", self.preserve_edit)
        advanced_form.addRow("Hindari", self.avoid_edit)
        self.advanced_brief_panel.setVisible(False)
        brief_layout.addWidget(self.advanced_brief_panel)
        self.advanced_brief_toggle.toggled.connect(
            self.advanced_brief_panel.setVisible
        )
        self.advanced_brief_toggle.toggled.connect(
            self._h2_update_advanced_toggle_text
        )
        top_cards.addWidget(brief_group, 2)
        layout.addLayout(top_cards)

        reference_group = QGroupBox("3. Pilih Foto Referensi")
        reference_group.setObjectName("createReferenceCard")
        reference_layout = QHBoxLayout(reference_group)
        reference_layout.setSpacing(14)
        self.reference_asset_list = QListWidget()
        self.reference_asset_list.setObjectName("createReferenceAssetList")
        self.reference_asset_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.reference_asset_list.setViewMode(QListView.ViewMode.IconMode)
        self.reference_asset_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.reference_asset_list.setMovement(QListView.Movement.Static)
        self.reference_asset_list.setWrapping(True)
        self.reference_asset_list.setWordWrap(True)
        self.reference_asset_list.setUniformItemSizes(True)
        self.reference_asset_list.setIconSize(QSize(100, 78))
        self.reference_asset_list.setGridSize(QSize(132, 117))
        self.reference_asset_list.setSpacing(6)
        self.reference_asset_list.setMinimumHeight(235)
        self.reference_asset_list.setMaximumHeight(264)
        self.reference_asset_list.setToolTip(
            "Klik foto untuk memilih. Tekan Ctrl untuk memilih beberapa referensi."
        )
        reference_layout.addWidget(self.reference_asset_list, 3)
        reference_detail_layout = QVBoxLayout()
        self.reference_asset_preview = QLabel("No reference selected.")
        self.reference_asset_preview.setObjectName("createReferenceAssetPreview")
        self.reference_asset_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reference_asset_preview.setMinimumSize(235, 190)
        self.reference_asset_preview.setWordWrap(True)
        reference_detail_layout.addWidget(self.reference_asset_preview, 1)
        self.reference_asset_detail = QLabel(
            "Pilih foto untuk melihat pratinjau. Foto lokal belum berarti "
            "diizinkan untuk layanan AI eksternal."
        )
        self.reference_asset_detail.setObjectName("createReferenceAssetDetail")
        self.reference_asset_detail.setWordWrap(True)
        reference_detail_layout.addWidget(self.reference_asset_detail)
        reference_layout.addLayout(reference_detail_layout, 2)
        layout.addWidget(reference_group)

        review_group = QGroupBox("4. Tinjau Prompt")
        review_group.setObjectName("createReviewCard")
        review_layout = QVBoxLayout(review_group)
        review_layout.setSpacing(10)
        self.prompt_preview = QPlainTextEdit()
        self.prompt_preview.setObjectName("promptPreview")
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setPlaceholderText(
            "Prompt Anda akan tampil di sini setelah memilih Buat Prompt."
        )
        self.prompt_preview.setMinimumHeight(154)
        self.prompt_preview.setMaximumHeight(215)
        review_layout.addWidget(self.prompt_preview)
        self.create_grounding_status = QLabel(
            "Belum ada prompt. Isi konsep lalu pilih Buat Prompt."
        )
        self.create_grounding_status.setObjectName("createGroundingStatus")
        self.create_grounding_status.setWordWrap(True)
        review_layout.addWidget(self.create_grounding_status)
        self.create_grounding_details_toggle = QPushButton("Lihat detail grounding  ▸")
        self.create_grounding_details_toggle.setObjectName(
            "createGroundingDetailsToggle"
        )
        self.create_grounding_details_toggle.setCheckable(True)
        review_layout.addWidget(self.create_grounding_details_toggle)
        self.prompt_grounding_metadata = QLabel("No grounded prompt built yet.")
        self.prompt_grounding_metadata.setObjectName("promptGroundingMetadata")
        self.prompt_grounding_metadata.setWordWrap(True)
        self.prompt_grounding_metadata.setVisible(False)
        review_layout.addWidget(self.prompt_grounding_metadata)
        self.create_grounding_details_toggle.toggled.connect(
            self.prompt_grounding_metadata.setVisible
        )
        self.create_grounding_details_toggle.toggled.connect(
            self._h2_update_grounding_toggle_text
        )
        action_row = QHBoxLayout()
        self.prompt_button = QPushButton("Buat Prompt")
        self.prompt_button.setObjectName("buildGroundedPrompt")
        self.copy_prompt_button = QPushButton("Salin Prompt")
        self.copy_prompt_button.setObjectName("copyGroundedPrompt")
        self.copy_prompt_button.setEnabled(False)
        self.history_save_button = QPushButton("")
        self.history_save_button.setObjectName("saveGroundedPromptToHistory")
        self.history_save_button.setEnabled(False)
        self.visual_button = QPushButton("Buat Visual (belum tersedia)")
        self.visual_button.setObjectName("generateVisuals")
        self.visual_button.setEnabled(False)
        if self._visual_generation_provider is not None:
            self.visual_button.setEnabled(True)
        self.visual_button.setToolTip(
            "Visual generation provider is not connected. "
            "No provider is connected in the normal foundation slice."
        )
        self.visual_button.clicked.connect(self._generate_visuals)
        action_row.addWidget(self.prompt_button)
        action_row.addWidget(self.copy_prompt_button)
        action_row.addWidget(self.history_save_button)
        action_row.addWidget(self.visual_button)
        action_row.addStretch(1)
        review_layout.addLayout(action_row)
        self.copy_prompt_feedback = QLabel("")
        self.copy_prompt_feedback.setObjectName("promptCopyFeedback")
        self.copy_prompt_feedback.setWordWrap(True)
        self._copy_prompt_feedback_active = False
        review_layout.addWidget(self.copy_prompt_feedback)
        self.history_save_feedback = QLabel("")
        self.history_save_feedback.setObjectName("historySaveFeedback")
        self.history_save_feedback.setWordWrap(True)
        review_layout.addWidget(self.history_save_feedback)
        self.create_safety_note = QLabel(
            "Generasi AI belum tersedia tanpa provider dan hak penggunaan aset yang sah."
        )
        self.create_safety_note.setObjectName("createSafetyNote")
        self.create_safety_note.setWordWrap(True)
        review_layout.addWidget(self.create_safety_note)
        layout.addWidget(review_group)

        self.create_feedback = QLabel("Select a product and variant to begin.")
        self.create_feedback.setObjectName("createFeedback")
        self.create_feedback.setWordWrap(True)
        layout.addWidget(self.create_feedback)

        self.product_combo.currentIndexChanged.connect(self._product_changed)
        self.variant_combo.currentIndexChanged.connect(self._variant_changed)
        self.reference_asset_list.itemSelectionChanged.connect(
            self._create_reference_selection_changed
        )
        self.prompt_button.clicked.connect(self._build_grounded_prompt)
        self.prompt_button.clicked.connect(self._refresh_create_grounding_status)
        self.prompt_preview.textChanged.connect(self._update_copy_prompt_availability)
        self.copy_prompt_button.clicked.connect(self._copy_existing_prompt)
        self.prompt_preview.textChanged.connect(self._history_save_preview_changed)
        self.history_save_button.clicked.connect(self._save_grounded_prompt_to_history)

        page.setWidget(content)
        return page


    def _update_copy_prompt_availability(self) -> None:
        """Enable local copy only for nonblank existing prompt text."""
        self.copy_prompt_button.setEnabled(bool(self.prompt_preview.toPlainText().strip()))
        self._copy_prompt_feedback_active = False
        self.copy_prompt_feedback.clear()

    def _copy_existing_prompt(self, _checked: bool = False) -> None:
        """Copy exact preview text to local clipboard; no translation or provider."""
        prompt = self.prompt_preview.toPlainText()
        if not prompt.strip():
            return
        QApplication.clipboard().setText(prompt)
        self._copy_prompt_feedback_active = True
        self.copy_prompt_feedback.setText(self._localizer.tr("prompt.copy_success"))

    def _history_save_preview_changed(self) -> None:
        """Only the exact successful grounded snapshot is eligible to save."""
        snap = self._pyside_history_pending
        if snap is not None and self.prompt_preview.toPlainText() != snap["prompt_text"]:
            self._pyside_history_pending = None
            self.history_save_button.setEnabled(False)
        self._pyside_history_feedback_key = ""
        self.history_save_feedback.clear()

    def _save_grounded_prompt_to_history(self, _checked: bool = False) -> None:
        """Opt-in local history write, never a provider call or rights grant."""
        snapshot = self._pyside_history_pending
        if snapshot is None or self.prompt_preview.toPlainText() != snapshot["prompt_text"]:
            return
        try:
            append_pyside_history_prompt(
                snapshot["request"], snapshot["prompt_text"], snapshot["context"],
            )
        except (OSError, ValueError, TypeError, RuntimeError):
            self._pyside_history_feedback_key = "history.save_failed"
            self.history_save_feedback.setText(self._localizer.tr("history.save_failed"))
            return
        self._pyside_history_pending = None
        self.history_save_button.setEnabled(False)
        self._pyside_history_feedback_key = "history.save_success"
        self.history_save_feedback.setText(self._localizer.tr("history.save_success"))
        self._history_refresh_workspace()

    def _populate_create_thumbnail_icons(self) -> int:
        """Preview up to 16 local manifest images; never perform provider calls.

        Original asset IDs and list ordering are not changed. Missing thumbnail
        bytes produce an empty icon rather than a forged or guessed image.
        """
        if self._visual_reference_assets is None:
            return 0
        rendered = 0
        for row in range(min(self.reference_asset_list.count(), 16)):
            item = self.reference_asset_list.item(row)
            reference_id = item.data(Qt.ItemDataRole.UserRole)
            asset = self._create_reference_assets_by_ref.get(reference_id)
            if asset is None or not asset.available or asset.asset_id is None:
                continue
            try:
                payload = self._visual_reference_assets.preview_bytes(asset.asset_id)
                thumbnail = QPixmap()
                if not thumbnail.loadFromData(payload):
                    continue
            except Exception:
                # The separate preview pane still exposes the precise read error.
                continue
            item.setIcon(QIcon(thumbnail.scaled(
                QSize(100, 78),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )))
            rendered += 1
        return rendered

    def _refresh_create_grounding_status(self, _checked: bool = False) -> None:
        """Show a human-readable UI state, not rights/provider authorization."""
        tr = self._localizer.tr
        meta = self.prompt_grounding_metadata.text()
        feedback = self.create_feedback.text()
        if (
            "Grounding: PASSED" in meta
            and bool(self.prompt_preview.toPlainText().strip())
            and "Missing: none" in meta
            and "Conflicts: none" in meta
        ):
            status = tr("status.prompt_ready")
        elif "Grounding: FAILED" in meta:
            status = tr("status.prompt_failed")
        elif feedback.startswith("Could not build prompt:"):
            status = tr("status.brief_required")
        elif not self.prompt_preview.toPlainText().strip():
            status = tr("status.prompt_empty")
        else:
            status = tr("status.prompt_review")
        self.create_grounding_status.setText(status)

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

    def _build_assets_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("assetsWorkspace")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        heading = QLabel("Assets")
        heading.setObjectName("assetsHeading")
        heading.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(heading)

        intro = QLabel(
            "Browse approved product-photo references through the read-only PC4 "
            "application boundary. Asset selection does not generate or promote "
            "new product truth."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        selector_group = QGroupBox("Product / Variant")
        selector_form = QFormLayout(selector_group)
        self.assets_product_combo = QComboBox()
        self.assets_product_combo.setObjectName("assetsProductSelector")
        self.assets_variant_combo = QComboBox()
        self.assets_variant_combo.setObjectName("assetsVariantSelector")
        self.assets_variant_combo.setEnabled(False)
        selector_form.addRow("Product", self.assets_product_combo)
        selector_form.addRow("Variant", self.assets_variant_combo)
        layout.addWidget(selector_group)

        browser_group = QGroupBox("Approved Visual References")
        browser_layout = QHBoxLayout(browser_group)
        self.assets_list = QListWidget()
        self.assets_list.setObjectName("assetsReferenceList")
        self.assets_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        browser_layout.addWidget(self.assets_list, 1)

        detail_layout = QVBoxLayout()
        self.assets_preview = QLabel("Choose a product and variant.")
        self.assets_preview.setObjectName("assetsPreview")
        self.assets_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.assets_preview.setMinimumSize(300, 220)
        self.assets_preview.setWordWrap(True)
        detail_layout.addWidget(self.assets_preview)

        self.assets_detail = QLabel("No visual reference selected.")
        self.assets_detail.setObjectName("assetsDetail")
        self.assets_detail.setWordWrap(True)
        detail_layout.addWidget(self.assets_detail)
        browser_layout.addLayout(detail_layout, 1)
        layout.addWidget(browser_group, 1)

        self.assets_status = QLabel("")
        self.assets_status.setObjectName("assetsWorkspaceStatus")
        self.assets_status.setWordWrap(True)
        layout.addWidget(self.assets_status)

        self.assets_product_combo.currentIndexChanged.connect(
            self._assets_product_changed
        )
        self.assets_variant_combo.currentIndexChanged.connect(
            self._assets_variant_changed
        )
        self.assets_list.itemSelectionChanged.connect(
            self._assets_selection_changed
        )
        return page

    def _build_approvals_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("approvalsWorkspace")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        heading = QLabel("Approvals")
        heading.setObjectName("approvalsHeading")
        heading.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(heading)

        intro = QLabel(
            "Review one explicit Gate 16 approval request through the existing "
            "safe operator dashboard boundary. This workspace is read-only and "
            "does not execute approval mutations."
        )
        intro.setObjectName("approvalsIntro")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        request_group = QGroupBox("Approval Request")
        request_form = QFormLayout(request_group)

        self.approvals_request_id = QLineEdit()
        self.approvals_request_id.setObjectName("approvalsRequestId")
        self.approvals_operator_reference = QLineEdit()
        self.approvals_operator_reference.setObjectName(
            "approvalsOperatorReference"
        )
        self.approvals_role_reference = QLineEdit()
        self.approvals_role_reference.setObjectName("approvalsRoleReference")
        self.approvals_target_type = QLineEdit()
        self.approvals_target_type.setObjectName("approvalsTargetType")
        self.approvals_target_reference = QLineEdit()
        self.approvals_target_reference.setObjectName(
            "approvalsTargetReference"
        )
        self.approvals_action = QLineEdit()
        self.approvals_action.setObjectName("approvalsAction")
        self.approvals_action.setPlaceholderText("APPROVE or REJECT")
        self.approvals_reason_reference = QLineEdit()
        self.approvals_reason_reference.setObjectName(
            "approvalsReasonReference"
        )
        self.approvals_audit_context_reference = QLineEdit()
        self.approvals_audit_context_reference.setObjectName(
            "approvalsAuditContextReference"
        )
        self.approvals_audit_limit = QLineEdit()
        self.approvals_audit_limit.setObjectName("approvalsAuditLimit")
        self.approvals_audit_limit.setPlaceholderText("1-100")

        request_form.addRow("Request ID", self.approvals_request_id)
        request_form.addRow("Operator", self.approvals_operator_reference)
        request_form.addRow("Role", self.approvals_role_reference)
        request_form.addRow("Target Type", self.approvals_target_type)
        request_form.addRow("Target Reference", self.approvals_target_reference)
        request_form.addRow("Action", self.approvals_action)
        request_form.addRow("Reason Reference", self.approvals_reason_reference)
        request_form.addRow(
            "Audit Context",
            self.approvals_audit_context_reference,
        )
        request_form.addRow("Audit Limit", self.approvals_audit_limit)
        layout.addWidget(request_group)

        self.approvals_refresh_button = QPushButton("Evaluate Approval Request")
        self.approvals_refresh_button.setObjectName(
            "approvalsEvaluateRequest"
        )
        layout.addWidget(self.approvals_refresh_button)

        self.approvals_status = QLabel("")
        self.approvals_status.setObjectName("approvalsWorkspaceStatus")
        self.approvals_status.setWordWrap(True)
        layout.addWidget(self.approvals_status)

        result_group = QGroupBox("Safe Dashboard Projection")
        result_layout = QVBoxLayout(result_group)
        self.approvals_summary = QPlainTextEdit()
        self.approvals_summary.setObjectName("approvalsAssessmentSummary")
        self.approvals_summary.setReadOnly(True)
        self.approvals_summary.setPlaceholderText(
            "Approval assessment will appear here."
        )
        result_layout.addWidget(self.approvals_summary)

        self.approvals_audit_history = QPlainTextEdit()
        self.approvals_audit_history.setObjectName("approvalsAuditHistory")
        self.approvals_audit_history.setReadOnly(True)
        self.approvals_audit_history.setPlaceholderText(
            "Matching approval audit records will appear here."
        )
        result_layout.addWidget(self.approvals_audit_history)
        layout.addWidget(result_group, 1)

        connected = self._operator_dashboard_builder is not None
        self.approvals_refresh_button.setEnabled(connected)
        if connected:
            self.approvals_status.setText(
                "Operator dashboard boundary connected. "
                "Enter an explicit approval request."
            )
        else:
            self.approvals_status.setText(
                "Operator dashboard boundary is unavailable; "
                "no storage fallback is used."
            )

        self.approvals_refresh_button.clicked.connect(
            self._refresh_operator_dashboard
        )
        return page

    def _approval_request_from_inputs(self) -> SafeOperatorDashboardRequest:
        audit_limit_text = self.approvals_audit_limit.text().strip()
        try:
            audit_limit = int(audit_limit_text, 10)
        except ValueError as exc:
            raise ValueError(
                "audit limit must be an integer from 1 through 100"
            ) from exc

        return SafeOperatorDashboardRequest(
            request_id=self.approvals_request_id.text(),
            operator_reference=self.approvals_operator_reference.text(),
            role_reference=self.approvals_role_reference.text(),
            target_type=self.approvals_target_type.text(),
            target_reference=self.approvals_target_reference.text(),
            action=self.approvals_action.text(),
            reason_reference=self.approvals_reason_reference.text(),
            audit_context_reference=(
                self.approvals_audit_context_reference.text()
            ),
            audit_limit=audit_limit,
        )

    @staticmethod
    def _operator_dashboard_summary(
        result: SafeOperatorDashboardResult,
    ) -> str:
        lines = [
            f"Status: {result.status}",
            f"Error: {result.error_code or 'none'}",
        ]
        projection = result.projection
        if projection is None:
            lines.append("Projection: unavailable")
            return "\n".join(lines)

        lines.extend(
            [
                f"Request: {projection.request_id}",
                f"Operator: {projection.operator_reference}",
                f"Role: {projection.role_reference}",
                f"Permission: {projection.permission_reference or 'none'}",
                f"Target: {projection.target_type} / {projection.target_reference}",
                f"Action: {projection.action}",
                f"Assessment: {projection.assessment_outcome}",
                f"Reason Code: {projection.assessment_reason_code}",
                f"Reason Reference: {projection.reason_reference}",
                f"Audit Context: {projection.audit_context_reference}",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _operator_dashboard_audit_text(
        result: SafeOperatorDashboardResult,
    ) -> str:
        projection = result.projection
        if projection is None or not projection.matching_audit_records:
            return "No matching approval audit records."

        return "\n".join(
            (
                f"{record.audit_record_id} | {record.decision_id} | "
                f"{record.action} | {record.assessment_outcome} | "
                f"{record.assessment_reason_code}"
            )
            for record in projection.matching_audit_records
        )

    def _refresh_operator_dashboard(self, _checked: bool = False) -> None:
        builder = self._operator_dashboard_builder
        self.approvals_summary.clear()
        self.approvals_audit_history.clear()

        if builder is None:
            self.approvals_status.setText(
                "Operator dashboard boundary is unavailable; "
                "no storage fallback is used."
            )
            return

        try:
            request = self._approval_request_from_inputs()
            result = builder(request)
            if not isinstance(result, SafeOperatorDashboardResult):
                raise TypeError(
                    "operator dashboard builder returned an invalid result"
                )
        except Exception as exc:
            self.approvals_status.setText(
                f"Could not build operator dashboard: {exc}"
            )
            return

        self.approvals_summary.setPlainText(
            self._operator_dashboard_summary(result)
        )
        self.approvals_audit_history.setPlainText(
            self._operator_dashboard_audit_text(result)
        )

        if result.status == STATUS_READY:
            self.approvals_status.setText(
                "Operator approval projection ready. "
                "No approval mutation has been executed."
            )
        elif result.status == STATUS_DENIED:
            self.approvals_status.setText(
                "Operator approval projection denied. "
                "No approval mutation has been executed."
            )
        elif result.status == STATUS_INVALID:
            self.approvals_status.setText(
                "Operator dashboard projection invalid: "
                f"{result.error_code}. No approval mutation has been executed."
            )


    def _build_workflow_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("creativeWorkflowWorkspace")
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(24, 20, 24, 20)
        outer_layout.setSpacing(12)

        heading = QLabel("Workflow")
        heading.setObjectName("creativeWorkflowHeading")
        heading.setStyleSheet("font-size: 22px; font-weight: 600;")
        outer_layout.addWidget(heading)

        intro = QLabel(
            "Assess one explicit Gate 18 creative-workflow transition through "
            "the existing governed application service. This workspace does "
            "not execute approval, asset-admission, lifecycle, external-tool, "
            "or production-release authority."
        )
        intro.setObjectName("creativeWorkflowIntro")
        intro.setWordWrap(True)
        outer_layout.addWidget(intro)

        scroll = QScrollArea()
        scroll.setObjectName("creativeWorkflowScrollArea")
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)

        request_group = QGroupBox("Governed Workflow Request")
        request_form = QFormLayout(request_group)

        self.workflow_request_id = QLineEdit()
        self.workflow_request_id.setObjectName("workflowRequestId")
        self.workflow_idempotency_key = QLineEdit()
        self.workflow_idempotency_key.setObjectName("workflowIdempotencyKey")
        self.workflow_project_reference = QLineEdit()
        self.workflow_project_reference.setObjectName("workflowProjectReference")
        self.workflow_campaign_reference = QLineEdit()
        self.workflow_campaign_reference.setObjectName("workflowCampaignReference")
        self.workflow_creative_brief_reference = QLineEdit()
        self.workflow_creative_brief_reference.setObjectName(
            "workflowCreativeBriefReference"
        )
        self.workflow_knowledge_references = QLineEdit()
        self.workflow_knowledge_references.setObjectName(
            "workflowApprovedKnowledgeReferences"
        )
        self.workflow_knowledge_references.setPlaceholderText(
            "Comma-separated references; optional"
        )
        self.workflow_governed_asset_references = QLineEdit()
        self.workflow_governed_asset_references.setObjectName(
            "workflowGovernedAssetReferences"
        )
        self.workflow_governed_asset_references.setPlaceholderText(
            "Comma-separated references; optional"
        )
        self.workflow_instruction_reference = QLineEdit()
        self.workflow_instruction_reference.setObjectName(
            "workflowInstructionReference"
        )
        self.workflow_instruction_authority = QLineEdit()
        self.workflow_instruction_authority.setObjectName(
            "workflowInstructionAuthority"
        )
        self.workflow_instruction_authority.setPlaceholderText(
            "PROMPT_CANDIDATE or APPROVED_INSTRUCTION"
        )
        self.workflow_requesting_actor = QLineEdit()
        self.workflow_requesting_actor.setObjectName("workflowRequestingActor")
        self.workflow_request_timestamp = QLineEdit()
        self.workflow_request_timestamp.setObjectName("workflowRequestTimestamp")
        self.workflow_request_timestamp.setPlaceholderText(
            "ISO-8601 timezone-aware timestamp"
        )
        self.workflow_contract_name = QLineEdit()
        self.workflow_contract_name.setObjectName("workflowContractName")
        self.workflow_contract_version = QLineEdit()
        self.workflow_contract_version.setObjectName("workflowContractVersion")
        self.workflow_output_purpose = QLineEdit()
        self.workflow_output_purpose.setObjectName("workflowOutputPurpose")
        self.workflow_review_policy = QLineEdit()
        self.workflow_review_policy.setObjectName("workflowReviewPolicy")
        self.workflow_manual_handoff_declared = QCheckBox(
            "Manual external-tool handoff is explicitly declared"
        )
        self.workflow_manual_handoff_declared.setObjectName(
            "workflowManualExternalHandoffDeclared"
        )

        request_form.addRow("Request ID", self.workflow_request_id)
        request_form.addRow("Idempotency Key", self.workflow_idempotency_key)
        request_form.addRow("Project Reference", self.workflow_project_reference)
        request_form.addRow("Campaign Reference", self.workflow_campaign_reference)
        request_form.addRow(
            "Creative Brief Reference",
            self.workflow_creative_brief_reference,
        )
        request_form.addRow(
            "Approved Knowledge",
            self.workflow_knowledge_references,
        )
        request_form.addRow(
            "Governed Assets",
            self.workflow_governed_asset_references,
        )
        request_form.addRow(
            "Instruction Reference",
            self.workflow_instruction_reference,
        )
        request_form.addRow(
            "Instruction Authority",
            self.workflow_instruction_authority,
        )
        request_form.addRow("Requesting Actor", self.workflow_requesting_actor)
        request_form.addRow(
            "Request Timestamp",
            self.workflow_request_timestamp,
        )
        request_form.addRow("Contract Name", self.workflow_contract_name)
        request_form.addRow("Contract Version", self.workflow_contract_version)
        request_form.addRow("Output Purpose", self.workflow_output_purpose)
        request_form.addRow("Review Policy", self.workflow_review_policy)
        request_form.addRow(
            "External Handoff",
            self.workflow_manual_handoff_declared,
        )
        layout.addWidget(request_group)

        transition_group = QGroupBox("Transition Assessment")
        transition_form = QFormLayout(transition_group)

        self.workflow_current_state = QLineEdit()
        self.workflow_current_state.setObjectName("workflowCurrentState")
        self.workflow_requested_state = QLineEdit()
        self.workflow_requested_state.setObjectName("workflowRequestedState")
        self.workflow_responsible_kind = QLineEdit()
        self.workflow_responsible_kind.setObjectName("workflowResponsibleKind")
        self.workflow_responsible_kind.setPlaceholderText(
            "ACTOR or ACCEPTED_SERVICE"
        )
        self.workflow_responsible_reference = QLineEdit()
        self.workflow_responsible_reference.setObjectName(
            "workflowResponsibleReference"
        )
        self.workflow_assessment_timestamp = QLineEdit()
        self.workflow_assessment_timestamp.setObjectName(
            "workflowAssessmentTimestamp"
        )
        self.workflow_assessment_timestamp.setPlaceholderText(
            "ISO-8601 timezone-aware timestamp"
        )
        self.workflow_evidence_references = QLineEdit()
        self.workflow_evidence_references.setObjectName(
            "workflowEvidenceReferences"
        )
        self.workflow_evidence_references.setPlaceholderText(
            "Comma-separated evidence identities in deterministic order"
        )
        self.workflow_reason_codes = QLineEdit()
        self.workflow_reason_codes.setObjectName("workflowReasonCodes")
        self.workflow_reason_codes.setPlaceholderText(
            "Comma-separated uppercase reason codes in deterministic order"
        )
        self.workflow_handoff_reference = QLineEdit()
        self.workflow_handoff_reference.setObjectName("workflowHandoffReference")
        self.workflow_handoff_reference.setPlaceholderText(
            "Identity within the explicit project/campaign; optional"
        )
        self.workflow_candidate_reference = QLineEdit()
        self.workflow_candidate_reference.setObjectName(
            "workflowCreativeResultCandidateReference"
        )
        self.workflow_candidate_reference.setPlaceholderText(
            "Identity within the explicit project/campaign; optional"
        )
        self.workflow_gate16_reference = QLineEdit()
        self.workflow_gate16_reference.setObjectName(
            "workflowAcceptedGate16DecisionReference"
        )
        self.workflow_gate16_reference.setPlaceholderText(
            "Accepted decision identity; optional"
        )
        self.workflow_gate15_reference = QLineEdit()
        self.workflow_gate15_reference.setObjectName(
            "workflowAcceptedGate15AssetReference"
        )
        self.workflow_gate15_reference.setPlaceholderText(
            "Accepted governed-asset identity; optional"
        )

        transition_form.addRow("Current State", self.workflow_current_state)
        transition_form.addRow("Requested State", self.workflow_requested_state)
        transition_form.addRow(
            "Responsible Kind",
            self.workflow_responsible_kind,
        )
        transition_form.addRow(
            "Responsible Reference",
            self.workflow_responsible_reference,
        )
        transition_form.addRow(
            "Assessment Timestamp",
            self.workflow_assessment_timestamp,
        )
        transition_form.addRow(
            "Evidence References",
            self.workflow_evidence_references,
        )
        transition_form.addRow("Reason Codes", self.workflow_reason_codes)
        transition_form.addRow(
            "Manual Handoff Reference",
            self.workflow_handoff_reference,
        )
        transition_form.addRow(
            "Creative Result Candidate",
            self.workflow_candidate_reference,
        )
        transition_form.addRow(
            "Accepted Gate 16 Decision",
            self.workflow_gate16_reference,
        )
        transition_form.addRow(
            "Accepted Gate 15 Asset",
            self.workflow_gate15_reference,
        )
        layout.addWidget(transition_group)

        self.workflow_assess_button = QPushButton("Assess Workflow Transition")
        self.workflow_assess_button.setObjectName("workflowAssessTransition")
        layout.addWidget(self.workflow_assess_button)

        self.workflow_status = QLabel("")
        self.workflow_status.setObjectName("creativeWorkflowStatus")
        self.workflow_status.setWordWrap(True)
        layout.addWidget(self.workflow_status)

        self.workflow_summary = QPlainTextEdit()
        self.workflow_summary.setObjectName("creativeWorkflowAssessmentSummary")
        self.workflow_summary.setReadOnly(True)
        self.workflow_summary.setMinimumHeight(220)
        self.workflow_summary.setPlaceholderText(
            "Governed workflow assessment will appear here."
        )
        layout.addWidget(self.workflow_summary)

        connected = self._governed_workflow_assessor is not None
        self.workflow_assess_button.setEnabled(connected)
        if connected:
            self.workflow_status.setText(
                "Gate 18 assessment boundary connected. Enter explicit "
                "workflow inputs and authority references."
            )
        else:
            self.workflow_status.setText(
                "Gate 18 assessment boundary is unavailable; no storage or "
                "authority fallback is used."
            )

        self.workflow_assess_button.clicked.connect(
            self._assess_governed_workflow
        )
        scroll.setWidget(content)
        outer_layout.addWidget(scroll, 1)
        return page

    @staticmethod
    def _workflow_items(value: str) -> tuple[str, ...]:
        return tuple(
            item.strip()
            for item in value.split(",")
            if item.strip()
        )

    @staticmethod
    def _workflow_timestamp(value: str, field_name: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.strip())
        except ValueError as exc:
            raise ValueError(
                f"{field_name} must be an ISO-8601 timestamp"
            ) from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")
        return parsed

    @staticmethod
    def _workflow_bound_reference(
        identity: str,
        *,
        project_reference: str,
        campaign_reference: str,
    ) -> tuple[str, str, str] | None:
        value = identity.strip()
        if not value:
            return None
        return (project_reference, campaign_reference, value)

    def _workflow_request_from_inputs(self) -> GovernedCreativeWorkflowRequest:
        project_reference = self.workflow_project_reference.text()
        campaign_reference = self.workflow_campaign_reference.text()
        return GovernedCreativeWorkflowRequest(
            workflow_request_id=self.workflow_request_id.text(),
            idempotency_key=self.workflow_idempotency_key.text(),
            project_context_reference=project_reference,
            campaign_context_reference=(
                project_reference,
                campaign_reference,
            ),
            creative_brief_reference=(
                self.workflow_creative_brief_reference.text()
            ),
            approved_knowledge_references=self._workflow_items(
                self.workflow_knowledge_references.text()
            ),
            governed_asset_references=self._workflow_items(
                self.workflow_governed_asset_references.text()
            ),
            instruction_reference=(
                self.workflow_instruction_reference.text(),
                self.workflow_instruction_authority.text(),
            ),
            requesting_actor_reference=self.workflow_requesting_actor.text(),
            request_timestamp=self._workflow_timestamp(
                self.workflow_request_timestamp.text(),
                "request timestamp",
            ),
            workflow_contract_reference=(
                self.workflow_contract_name.text(),
                self.workflow_contract_version.text(),
            ),
            requested_output_purpose_code=self.workflow_output_purpose.text(),
            requested_review_policy_reference=self.workflow_review_policy.text(),
            manual_external_tool_handoff_declared=(
                self.workflow_manual_handoff_declared.isChecked()
            ),
        )

    @staticmethod
    def _workflow_reference_text(reference: Any) -> str:
        if reference is None:
            return "none"
        return " / ".join(str(item) for item in reference)

    @classmethod
    def _workflow_assessment_summary(
        cls,
        result: GovernedCreativeWorkflowApplicationAssessment,
    ) -> str:
        evaluation = result.transition_evaluation
        event = result.creative_workflow_event
        workflow_result = result.governed_creative_workflow_result
        diagnostics = (
            "; ".join(
                f"{code}: {message}"
                for code, message in evaluation.diagnostics
            )
            or "none"
        )
        lines = [
            f"Assessment Fingerprint: {result.assessment_fingerprint}",
            f"Request: {result.workflow_request_reference}",
            f"Current State: {result.current_workflow_state}",
            f"Requested State: {result.requested_workflow_state}",
            f"Disposition: {evaluation.disposition}",
            f"Resulting State: {evaluation.resulting_workflow_state}",
            f"Reason Codes: {', '.join(evaluation.reason_codes)}",
            f"Diagnostics: {diagnostics}",
            (
                "Gate 16 Decision: "
                + cls._workflow_reference_text(
                    result.accepted_gate_16_operator_decision_reference
                )
            ),
            (
                "Gate 15 Asset: "
                + cls._workflow_reference_text(
                    result.accepted_gate_15_governed_asset_reference
                )
            ),
            (
                "Workflow Event: "
                + (
                    event.creative_workflow_event_id
                    if event is not None
                    else "none"
                )
            ),
            (
                "Workflow Result: "
                + (
                    str(workflow_result.final_workflow_state)
                    if workflow_result is not None
                    else "none"
                )
            ),
            f"Production Release Claimed: {result.production_release_claimed}",
        ]
        return "\n".join(lines)

    def _assess_governed_workflow(self, _checked: bool = False) -> None:
        assessor = self._governed_workflow_assessor
        self.workflow_summary.clear()

        if assessor is None:
            self.workflow_status.setText(
                "Gate 18 assessment boundary is unavailable; no storage or "
                "authority fallback is used."
            )
            return

        try:
            request = self._workflow_request_from_inputs()
            project_reference = request.project_context_reference
            campaign_reference = request.campaign_context_reference[1]
            result = assessor(
                workflow_request=request,
                current_workflow_state=self.workflow_current_state.text(),
                requested_next_workflow_state=(
                    self.workflow_requested_state.text()
                ),
                responsible_actor_or_service_reference=(
                    self.workflow_responsible_kind.text(),
                    self.workflow_responsible_reference.text(),
                ),
                assessment_timestamp=self._workflow_timestamp(
                    self.workflow_assessment_timestamp.text(),
                    "assessment timestamp",
                ),
                evidence_references=tuple(
                    (
                        project_reference,
                        campaign_reference,
                        identity,
                    )
                    for identity in self._workflow_items(
                        self.workflow_evidence_references.text()
                    )
                ),
                reason_codes=self._workflow_items(
                    self.workflow_reason_codes.text()
                ),
                workflow_contract_reference=(
                    request.workflow_contract_reference
                ),
                manual_external_tool_handoff_reference=(
                    self._workflow_bound_reference(
                        self.workflow_handoff_reference.text(),
                        project_reference=project_reference,
                        campaign_reference=campaign_reference,
                    )
                ),
                creative_result_candidate_reference=(
                    self._workflow_bound_reference(
                        self.workflow_candidate_reference.text(),
                        project_reference=project_reference,
                        campaign_reference=campaign_reference,
                    )
                ),
                accepted_gate_16_operator_decision_reference=(
                    self._workflow_bound_reference(
                        self.workflow_gate16_reference.text(),
                        project_reference=project_reference,
                        campaign_reference=campaign_reference,
                    )
                ),
                accepted_gate_15_governed_asset_reference=(
                    self._workflow_bound_reference(
                        self.workflow_gate15_reference.text(),
                        project_reference=project_reference,
                        campaign_reference=campaign_reference,
                    )
                ),
            )
            if not isinstance(
                result,
                GovernedCreativeWorkflowApplicationAssessment,
            ):
                raise TypeError(
                    "governed workflow assessor returned an invalid result"
                )
            if result.production_release_claimed:
                raise ValueError(
                    "governed workflow assessment must not claim "
                    "production release"
                )
        except Exception as exc:
            self.workflow_status.setText(
                f"Could not assess governed workflow: {exc}"
            )
            return

        self.workflow_summary.setPlainText(
            self._workflow_assessment_summary(result)
        )
        self.workflow_status.setText(
            "Governed workflow assessment ready. No approval execution, "
            "asset admission execution, lifecycle mutation, external-tool "
            "execution, or production release has been executed."
        )

    def _build_product_context_panel(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 18, 16, 18)

        heading = QLabel("Ringkasan Produk")
        heading.setStyleSheet("font-size: 18px; font-weight: 600;")
        self._h3_context_heading = heading
        self._h3_context_section_titles = {}
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

        self.constraints_label = self._add_context_section(
            layout,
            "Hal yang harus dipertahankan",
            "Belum ada ketentuan produk.",
        )
        self.context_governance_note = QLabel(
            "Foto bisa dipratinjau secara lokal. Pemakaian pada layanan AI "
            "eksternal tetap memerlukan izin yang sah."
        )
        self.context_governance_note.setObjectName("productContextGovernanceNote")
        self.context_governance_note.setWordWrap(True)
        layout.addWidget(self.context_governance_note)
        self.context_technical_toggle = QPushButton("Lihat detail teknis  ▸")
        self.context_technical_toggle.setObjectName("productContextTechnicalToggle")
        self.context_technical_toggle.setCheckable(True)
        layout.addWidget(self.context_technical_toggle)
        self.context_technical_panel = QWidget()
        self.context_technical_panel.setObjectName("productContextTechnicalPanel")
        technical_layout = QVBoxLayout(self.context_technical_panel)
        technical_layout.setContentsMargins(0, 0, 0, 0)
        self.facts_label = self._add_context_section(
            technical_layout, "Fakta produk (rinci)", "No facts loaded.")
        self.references_label = self._add_context_section(
            technical_layout, "Hak penggunaan referensi", "No authorized references loaded.")
        self.unknowns_label = self._add_context_section(
            technical_layout, "Unknown / Conflict", "No product context loaded.")
        self.context_technical_panel.setVisible(False)
        layout.addWidget(self.context_technical_panel)
        self.context_technical_toggle.toggled.connect(
            self.context_technical_panel.setVisible
        )
        self.context_technical_toggle.toggled.connect(
            self._h3_technical_toggle_text
        )
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("productContextPanel")
        scroll.setStyleSheet("""
            QScrollArea#productContextPanel QLabel { font-size: 14px; color: #e7edf5; }
            QScrollArea#productContextPanel QPushButton { font-size: 14px; padding: 8px; }
        """)
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
        if hasattr(self, "_h3_context_section_titles"):
            self._h3_context_section_titles[title] = title_label
        value = QLabel(initial)
        value.setWordWrap(True)
        value.setProperty("sectionTitle", title)
        layout.addWidget(title_label)
        layout.addWidget(value)
        return value

    @staticmethod
    def _asset_detail_text(asset: Any) -> str:
        scope = asset.product_label
        if asset.variant_id is not None:
            scope += " / " + asset.variant_label
        return (
            f"Scope: {scope}\n"
            f"Authority: {asset.authority}\n"
            f"Status: {asset.status}\n"
            f"Version: {asset.version}\n"
            f"SHA256: {asset.sha256 or 'unavailable'}\n"
            f"Source: {asset.source_relative_path}\n"
            f"Availability: {'available' if asset.available else 'unavailable'}"
        )

    def _set_asset_preview(
        self,
        *,
        label: QLabel,
        asset: Any,
    ) -> None:
        if not asset.available or asset.asset_id is None:
            label.setPixmap(QPixmap())
            label.setText("Reference file is unavailable.")
            return
        if self._visual_reference_assets is None:
            label.setPixmap(QPixmap())
            label.setText("Visual Reference Asset Query is unavailable.")
            return
        try:
            payload = self._visual_reference_assets.preview_bytes(asset.asset_id)
        except Exception as exc:
            label.setPixmap(QPixmap())
            label.setText(f"Preview unavailable: {exc}")
            return
        pixmap = QPixmap()
        if not pixmap.loadFromData(payload):
            label.setPixmap(QPixmap())
            label.setText("Preview format could not be rendered.")
            return
        label.setText("")
        label.setPixmap(
            pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    @staticmethod
    def _populate_asset_list(
        widget: QListWidget,
        assets: tuple[Any, ...],
        target: dict[str, Any],
    ) -> None:
        widget.clear()
        target.clear()
        for asset in assets:
            reference_id = str(asset.reference_id)
            target[reference_id] = asset
            text = str(asset.filename)
            if not asset.available:
                text += " [unavailable]"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, reference_id)
            if not asset.available or asset.asset_id is None:
                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsSelectable
                    & ~Qt.ItemFlag.ItemIsEnabled
                )
                item.setToolTip("This approved reference is currently unavailable.")
            else:
                item.setToolTip(str(asset.source_relative_path))
            widget.addItem(item)

    def _load_create_reference_assets(
        self,
        *,
        product_id: str | None = None,
        variant_id: str | None = None,
    ) -> None:
        self.reference_asset_list.clear()
        self._create_reference_assets_by_ref.clear()
        self.reference_asset_preview.setPixmap(QPixmap())
        self.reference_asset_preview.setText("No reference selected.")

        if self._visual_reference_assets is None:
            self.reference_asset_list.setEnabled(False)
            self.reference_asset_detail.setText(
                "Visual Reference Asset Query is unavailable in this shell session."
            )
            return
        self.reference_asset_list.setEnabled(True)
        if not product_id or not variant_id:
            self.reference_asset_detail.setText(
                "Choose a product and variant to load approved references."
            )
            return

        try:
            assets = self._visual_reference_assets.assets_for_selection(
                product_id=product_id,
                variant_id=variant_id,
            )
        except Exception as exc:
            self.reference_asset_detail.setText(
                f"Could not load approved visual references: {exc}"
            )
            return

        self._populate_asset_list(
            self.reference_asset_list,
            assets,
            self._create_reference_assets_by_ref,
        )
        thumbnail_count = self._populate_create_thumbnail_icons()
        available_count = sum(
            1 for asset in assets if asset.available and asset.asset_id is not None
        )
        unavailable_count = len(assets) - available_count
        self.reference_asset_detail.setText(
            f"{available_count} foto tersedia, "
            f"{thumbnail_count} thumbnail ditampilkan; "
            f"{unavailable_count} tidak tersedia. "
            "Pratinjau lokal bukan izin layanan AI eksternal."
        )

    def _create_reference_selection_changed(self) -> None:
        selected_assets = []
        for row in range(self.reference_asset_list.count()):
            item = self.reference_asset_list.item(row)
            if not item.isSelected():
                continue
            reference_id = item.data(Qt.ItemDataRole.UserRole)
            asset = self._create_reference_assets_by_ref.get(reference_id)
            if asset is not None and asset.available and asset.asset_id is not None:
                selected_assets.append(asset)

        if not selected_assets:
            self.reference_asset_preview.setPixmap(QPixmap())
            self.reference_asset_preview.setText("No reference selected.")
            self._h3_reference_status()
            return

        self._set_asset_preview(
            label=self.reference_asset_preview,
            asset=selected_assets[0],
        )
        selected = selected_assets[0]
        self.reference_asset_detail.setText(
            f"{len(selected_assets)} foto dipilih.\n"
            f"Pratinjau: {selected.filename}\n"
            "Pemilihan lokal bukan izin penggunaan di layanan AI eksternal."
        )
        self._h3_reference_status()

    def _selected_create_reference_asset_ids(self) -> tuple[str, ...]:
        output = []
        for row in range(self.reference_asset_list.count()):
            item = self.reference_asset_list.item(row)
            if not item.isSelected():
                continue
            reference_id = item.data(Qt.ItemDataRole.UserRole)
            asset = self._create_reference_assets_by_ref.get(reference_id)
            if asset is not None and asset.available and asset.asset_id is not None:
                output.append(str(asset.asset_id))
        return tuple(output)

    def _load_assets_workspace(self) -> None:
        self._assets_workspace_product_ids_by_label.clear()
        self._assets_workspace_variant_ids_by_label.clear()
        self._assets_workspace_assets_by_ref.clear()
        self.assets_product_combo.clear()
        self.assets_variant_combo.clear()
        self.assets_list.clear()
        self.assets_product_combo.addItem("Choose product...")
        self.assets_variant_combo.addItem("Choose variant...")
        self.assets_preview.setPixmap(QPixmap())
        self.assets_preview.setText("Choose a product and variant.")
        self.assets_detail.setText("No visual reference selected.")

        if self._visual_reference_assets is None:
            self.assets_product_combo.setEnabled(False)
            self.assets_variant_combo.setEnabled(False)
            self.assets_list.setEnabled(False)
            self._h3d_set_status(self.assets_status, "status.assets_unavailable")
            return

        self.assets_product_combo.setEnabled(True)
        self.assets_list.setEnabled(True)
        for option in self._visual_reference_assets.product_options:
            self._assets_workspace_product_ids_by_label[option.label] = option.product_id
            self.assets_product_combo.addItem(option.label)
        self._h3d_set_status(self.assets_status, "status.assets_connected")

    def _assets_product_changed(self) -> None:
        label = self.assets_product_combo.currentText()
        product_id = self._assets_workspace_product_ids_by_label.get(label)
        self.assets_variant_combo.clear()
        self.assets_variant_combo.addItem("Choose variant...")
        self._assets_workspace_variant_ids_by_label.clear()
        self.assets_list.clear()
        self._assets_workspace_assets_by_ref.clear()
        self.assets_preview.setPixmap(QPixmap())
        self.assets_preview.setText("Choose a product and variant.")
        self.assets_detail.setText("No visual reference selected.")

        if self._visual_reference_assets is None or not product_id:
            self.assets_variant_combo.setEnabled(False)
            return
        try:
            variants = self._visual_reference_assets.variant_options_for_product(
                product_id
            )
        except Exception as exc:
            self.assets_variant_combo.setEnabled(False)
            self.assets_status.setText(f"Could not load variants: {exc}")
            return
        for option in variants:
            self._assets_workspace_variant_ids_by_label[option.label] = option.variant_id
            self.assets_variant_combo.addItem(option.label)
        self.assets_variant_combo.setEnabled(True)
        self._h3d_set_status(self.assets_status, "status.assets_variant_needed")

    def _assets_variant_changed(self) -> None:
        if self._visual_reference_assets is None:
            return
        product_id = self._assets_workspace_product_ids_by_label.get(
            self.assets_product_combo.currentText()
        )
        variant_id = self._assets_workspace_variant_ids_by_label.get(
            self.assets_variant_combo.currentText()
        )
        if not product_id or not variant_id:
            return
        try:
            assets = self._visual_reference_assets.assets_for_selection(
                product_id=product_id,
                variant_id=variant_id,
            )
        except Exception as exc:
            self.assets_status.setText(
                f"Could not load approved visual references: {exc}"
            )
            return
        self._populate_asset_list(
            self.assets_list,
            assets,
            self._assets_workspace_assets_by_ref,
        )
        available_count = sum(
            1 for asset in assets if asset.available and asset.asset_id is not None
        )
        self.assets_status.setText(
            f"Loaded {len(assets)} approved reference(s); "
            f"{available_count} available for selection."
        )

    def _assets_selection_changed(self) -> None:
        selected = self.assets_list.selectedItems()
        if not selected:
            self.assets_preview.setPixmap(QPixmap())
            self.assets_preview.setText("No visual reference selected.")
            self.assets_detail.setText("No visual reference selected.")
            return
        reference_id = selected[0].data(Qt.ItemDataRole.UserRole)
        asset = self._assets_workspace_assets_by_ref.get(reference_id)
        if asset is None:
            return
        self._set_asset_preview(label=self.assets_preview, asset=asset)
        self.assets_detail.setText(self._asset_detail_text(asset))

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
            self._h3d_set_status(self.products_status, "status.products_unavailable")
            return

        self.products_product_combo.setEnabled(True)
        self.products_fact_search.setEnabled(True)
        self.products_fact_search_button.setEnabled(True)
        self.products_provenance_combo.setEnabled(True)
        self.products_provenance_button.setEnabled(True)
        self._h3d_set_status(self.products_status, "status.products_connected")

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
            self._h3d_set_status(self.products_status, "status.search_select_product")
            return
        if not query:
            self._h3d_set_status(self.products_status, "status.search_empty")
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

    def _build_history_page(self) -> QWidget:
        "Display only legacy v1 history; never restore or persist it."
        page = QWidget()
        page.setObjectName("historyWorkspace")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        self.history_heading = QLabel("")
        self.history_heading.setObjectName("historyHeading")
        self.history_heading.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(self.history_heading)
        self.history_intro = QLabel("")
        self.history_intro.setObjectName("historyIntro")
        self.history_intro.setWordWrap(True)
        layout.addWidget(self.history_intro)
        self.history_legacy_note = QLabel("")
        self.history_legacy_note.setObjectName("historyLegacyNotice")
        self.history_legacy_note.setWordWrap(True)
        layout.addWidget(self.history_legacy_note)
        control = QHBoxLayout()
        self.history_status = QLabel("")
        self.history_status.setObjectName("historyStatus")
        self.history_status.setWordWrap(True)
        self.history_refresh_button = QPushButton("")
        self.history_refresh_button.setObjectName("historyRefresh")
        control.addWidget(self.history_status, 1)
        control.addWidget(self.history_refresh_button)
        layout.addLayout(control)
        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        self.history_list.setMinimumHeight(135)
        layout.addWidget(self.history_list, 2)
        self.history_details = QLabel("")
        self.history_details.setObjectName("historyLegacyFields")
        self.history_details.setWordWrap(True)
        self.history_details.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.history_details)
        self.history_preview = QPlainTextEdit()
        self.history_preview.setObjectName("historyPromptPreview")
        self.history_preview.setReadOnly(True)
        self.history_preview.setMinimumHeight(135)
        self.history_preview_hint = QLabel("")
        self.history_preview_hint.setObjectName("historyPromptEmptyHint")
        self.history_preview_hint.setWordWrap(True)
        layout.addWidget(self.history_preview_hint)
        layout.addWidget(self.history_preview, 3)
        copyrow = QHBoxLayout()
        self.history_copy_button = QPushButton("")
        self.history_copy_button.setObjectName("historyCopyPrompt")
        self.history_copy_button.setEnabled(False)
        self.history_copy_feedback = QLabel("")
        self.history_copy_feedback.setObjectName("historyCopyFeedback")
        copyrow.addWidget(self.history_copy_button)
        copyrow.addWidget(self.history_copy_feedback, 1)
        layout.addLayout(copyrow)
        self.history_list.currentRowChanged.connect(self._history_selection_changed)
        self.history_refresh_button.clicked.connect(self._history_refresh_workspace)
        self.history_copy_button.clicked.connect(self._history_copy_prompt)
        return page

    def _history_refresh_workspace(self, _checked: bool = False) -> None:
        "Read normalized legacy workspace through its existing API only."
        try:
            state = load_workspace()
            records = tuple(state["recent_prompts"][:20])
        except (OSError, ValueError, TypeError, KeyError):
            # Do not report specific paths or stored prompt content.
            records = ()
        self._history_records = records
        self._history_loaded = True
        self.history_list.clear()
        for index, record in enumerate(records, 1):
            product = record["product_id"] or "—"
            variant = record["variant_id"] or "—"
            marker = "★ " if record["favorite"] else ""
            self.history_list.addItem(f"{index}. {marker}{product} / {variant}")
        self._history_selection_changed(-1)
        self._history_apply_language()

    def _history_selected_record(self) -> dict | None:
        index = self.history_list.currentRow()
        if index < 0 or index >= len(self._history_records):
            return None
        return self._history_records[index]

    def _history_update_details(self) -> None:
        record = self._history_selected_record()
        if record is None:
            self.history_details.clear()
            return
        fields = ("product_id", "variant_id", "background", "camera_angle", "requested_output")
        self.history_details.setText(self._localizer.tr(
            "history.details", **{field: record[field] for field in fields}
        ))

    def _history_selection_changed(self, _row: int) -> None:
        record = self._history_selected_record()
        self.history_preview.setPlainText(record["prompt_text"] if record is not None else "")
        self.history_preview_hint.setVisible(record is None)
        self.history_copy_button.setEnabled(
            bool(record is not None and record["prompt_text"].strip())
        )
        self._history_copy_feedback_active = False
        self.history_copy_feedback.clear()
        self._history_update_details()

    def _history_copy_prompt(self, _checked: bool = False) -> None:
        record = self._history_selected_record()
        if record is None or not record["prompt_text"].strip():
            return
        QApplication.clipboard().setText(record["prompt_text"])
        self._history_copy_feedback_active = True
        self.history_copy_feedback.setText(self._localizer.tr("prompt.copy_success"))

    def _history_apply_language(self) -> None:
        "Translate presentation only: never re-fetch or mutate history records."
        tr = self._localizer.tr
        self.history_heading.setText(tr("history.title"))
        self.history_intro.setText(tr("history.intro"))
        self.history_legacy_note.setText(tr("history.legacy_note"))
        self.history_refresh_button.setText(tr("history.refresh"))
        self.history_preview.setPlaceholderText("")
        self.history_preview_hint.setText(tr("history.preview_placeholder"))
        self.history_copy_button.setText(tr("prompt.copy"))
        if self._history_copy_feedback_active:
            self.history_copy_feedback.setText(tr("prompt.copy_success"))
        self.history_status.setText(
            tr("history.count", count=len(self._history_records))
            if self._history_records else tr("history.empty")
        )
        self._history_update_details()

    def _build_presets_page(self) -> QWidget:
        """Read-only projection of existing legacy v1 preset records."""
        page = QWidget()
        page.setObjectName("presetsWorkspace")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        self.presets_heading = QLabel("")
        self.presets_heading.setObjectName("presetsHeading")
        self.presets_heading.setStyleSheet("font-size: 22px; font-weight: 600;")
        layout.addWidget(self.presets_heading)
        self.presets_intro = QLabel("")
        self.presets_intro.setObjectName("presetsIntro")
        self.presets_intro.setWordWrap(True)
        layout.addWidget(self.presets_intro)
        self.presets_legacy_note = QLabel("")
        self.presets_legacy_note.setObjectName("presetsLegacyNotice")
        self.presets_legacy_note.setWordWrap(True)
        layout.addWidget(self.presets_legacy_note)
        control = QHBoxLayout()
        self.presets_status = QLabel("")
        self.presets_status.setObjectName("presetsStatus")
        self.presets_status.setWordWrap(True)
        self.presets_refresh_button = QPushButton("")
        self.presets_refresh_button.setObjectName("presetsRefresh")
        control.addWidget(self.presets_status, 1)
        control.addWidget(self.presets_refresh_button)
        layout.addLayout(control)
        self.presets_list = QListWidget()
        self.presets_list.setObjectName("presetsList")
        self.presets_list.setMinimumHeight(170)
        layout.addWidget(self.presets_list, 3)
        self.presets_hint = QLabel("")
        self.presets_hint.setObjectName("presetsSelectionHint")
        self.presets_hint.setWordWrap(True)
        layout.addWidget(self.presets_hint)
        self.presets_details = QLabel("")
        self.presets_details.setObjectName("presetsLegacyFields")
        self.presets_details.setWordWrap(True)
        self.presets_details.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.presets_details)
        layout.addStretch(1)
        self.presets_list.currentRowChanged.connect(self._presets_selection_changed)
        self.presets_refresh_button.clicked.connect(self._presets_refresh_workspace)
        return page

    def _presets_refresh_workspace(self, _checked: bool = False) -> None:
        """Reuse existing loader; no writes or legacy-to-Create hydration."""
        try:
            state = load_workspace()
            records = tuple(state["presets"][:20])
        except (OSError, ValueError, TypeError, KeyError):
            records = ()
        self._presets_records = records
        self.presets_list.clear()
        for record in records:
            self.presets_list.addItem(record["name"])
        self._presets_selection_changed(-1)
        self._presets_apply_language()

    def _presets_selected_record(self) -> dict | None:
        index = self.presets_list.currentRow()
        if index < 0 or index >= len(self._presets_records):
            return None
        return self._presets_records[index]

    def _presets_selection_changed(self, _row: int) -> None:
        record = self._presets_selected_record()
        self.presets_hint.setVisible(record is None)
        if record is None:
            self.presets_details.clear()
        else:
            fields = ("name", "product_id", "variant_id", "background", "camera_angle", "requested_output")
            self.presets_details.setText(self._localizer.tr(
                "presets.details", **{field: record[field] for field in fields}
            ))

    def _presets_apply_language(self) -> None:
        """Retext UI only; never reload, translate, or mutate user data."""
        tr = self._localizer.tr
        self.presets_heading.setText(tr("presets.title"))
        self.presets_intro.setText(tr("presets.intro"))
        self.presets_legacy_note.setText(tr("presets.legacy_note"))
        self.presets_refresh_button.setText(tr("presets.refresh"))
        self.presets_hint.setText(tr("presets.selection_hint"))
        self.presets_status.setText(
            tr("presets.count", count=len(self._presets_records))
            if self._presets_records else tr("presets.empty")
        )
        self._presets_selection_changed(self.presets_list.currentRow())

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
        self._load_create_reference_assets()
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
            self._load_create_reference_assets(
                product_id=product_id,
                variant_id=variant_id,
            )
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
            selected_reference_asset_ids=(
                self._selected_create_reference_asset_ids()
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
        self._pyside_history_pending = None
        self.history_save_button.setEnabled(False)
        self._pyside_history_feedback_key = ""
        self.history_save_feedback.clear()
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
            brief = self.current_brief()
            try:
                result = self._creative_prompt_composer.compose(
                    product_id=product_id,
                    variant_id=variant_id,
                    brief=brief,
                )
            except Exception as exc:
                self.create_feedback.setText(f"Could not build prompt: {exc}")
                return

            self.prompt_preview.setPlainText(result.prompt_text)
            used_knowledge = tuple(result.used_knowledge_ids)
            used_assets = tuple(result.used_asset_ids)
            selected_references = tuple(
                getattr(result, "selected_reference_asset_ids", ())
            )
            missing = tuple(result.missing_knowledge)
            conflicts = tuple(result.conflicts)
            self.prompt_grounding_metadata.setText(
                "Grounding: "
                + str(result.grounding_status)
                + " | Knowledge: "
                + (", ".join(used_knowledge) or "none")
                + " | Grounded Assets: "
                + (", ".join(used_assets) or "none")
                + " | Selected References: "
                + (", ".join(selected_references) or "none")
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
                self._pyside_history_pending = {
                    "request": {
                        "product_id": product_id,
                        "variant_id": variant_id,
                        **brief.legacy_submit_fields(),
                    },
                    "prompt_text": result.prompt_text,
                    "context": {
                        "schema_version": 1,
                        "brief": asdict(brief),
                        "grounding": {
                            "status": str(result.grounding_status),
                            "used_knowledge_ids": list(used_knowledge),
                            "used_asset_ids": list(used_assets),
                            "selected_reference_asset_ids": list(selected_references),
                            "missing_knowledge": list(missing),
                            "conflicts": list(conflicts),
                        },
                    },
                }
                self.history_save_button.setEnabled(True)
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


    def _generate_visuals(self, _checked: bool = False) -> None:
        provider = self._visual_generation_provider
        if provider is None:
            self.create_feedback.setText(
                "Visual generation provider is not connected."
            )
            return

        grounded_prompt = self.prompt_preview.toPlainText()
        if not grounded_prompt.strip():
            self.create_feedback.setText(
                "Build a grounded prompt before generating visuals."
            )
            return

        try:
            request = VisualGenerationRequest(
                grounded_prompt=grounded_prompt,
                selected_reference_asset_ids=(
                    self._selected_create_reference_asset_ids()
                ),
            )
            result = provider.generate(request)
            if not isinstance(result, VisualGenerationResult):
                raise TypeError(
                    "visual generation provider returned an invalid result"
                )
        except Exception as exc:
            self.create_feedback.setText(
                f"Could not generate visuals: {exc}"
            )
            return

        if result.message.strip():
            self.create_feedback.setText(result.message)
        else:
            self.create_feedback.setText(
                "Visual generation completed with "
                f"{len(result.provider_output_refs)} provider output reference(s)."
            )


def build_normal_product_completion_shell() -> ProductCompletionShell:
    """Compose the normal PySide shell from remembered local foundation state."""
    intake_root = load_remembered_intake_root()
    if intake_root is None:
        return ProductCompletionShell()

    try:
        product_intelligence_query = ProductIntelligenceQuery.from_intake_root(
            intake_root=intake_root
        )
        visual_reference_asset_query = VisualReferenceAssetQuery(
            intake_root=intake_root,
            product_intelligence_query=product_intelligence_query,
        )
        creative_prompt_composer = CreativePromptComposer.from_intake_root(
            intake_root=intake_root,
            visual_reference_asset_query=visual_reference_asset_query,
        )
    except Exception:
        return ProductCompletionShell()

    return ProductCompletionShell(
        product_intelligence_query=product_intelligence_query,
        creative_prompt_composer=creative_prompt_composer,
        visual_reference_asset_query=visual_reference_asset_query,
    )


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
    shell = build_normal_product_completion_shell()
    shell.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()