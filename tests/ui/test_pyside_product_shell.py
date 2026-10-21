from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QScrollArea, QSplitter

import rie.ui.pyside_product_shell as shell_module

from rie.application.governed_creative_workflow_application_service import (
    assess_governed_creative_workflow,
)
from rie.application.operator_approval_application_service import (
    CONFLICT_CLEAR,
    IDEMPOTENCY_NEW,
    LIFECYCLE_ELIGIBLE,
    PROVENANCE_VERIFIED,
    REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
    RIGHTS_CLEARED,
    TargetApprovalContext,
)
from rie.application.safe_operator_dashboard_adapter import (
    STATUS_READY,
    SafeOperatorDashboardRequest,
    build_safe_operator_dashboard,
)
from rie.domain.operator_approval_audit_history import (
    OperatorApprovalAuditHistory,
    OperatorApprovalAuditRecord,
)
from rie.domain.operator_approval_decision import OperatorApprovalDecision
from rie.domain.operator_role_authority import (
    OperatorRoleBinding,
    RoleActionTargetPermission,
)
from rie.ui.product_completion_models import (
    ProductConstraint,
    ProductContextSnapshot,
    ProductFact,
    ProductUnknown,
)
from rie.ui.pyside_product_shell import (
    GroundedPromptCompatibilityAdapter,
    NAVIGATION,
    NAVIGATION_LABELS,
    ProductCompletionShell,
    WINDOW_TITLE,
    build_normal_product_completion_shell,
    packaging_smoke_main,
)


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    return QApplication.instance() or QApplication([])


class _FakeController:
    product_options = (
        SimpleNamespace(product_id="sv300", label="SV300"),
        SimpleNamespace(product_id="ffs21", label="FFS21"),
    )

    def variant_options_for_product(self, product_id: str):
        if product_id == "sv300":
            return (
                SimpleNamespace(
                    variant_id="white-glossy",
                    product_id="sv300",
                    label="White Glossy",
                ),
            )
        return ()

    def submit(self, **kwargs):
        return SimpleNamespace(
            prompt_text=(
                f"{kwargs['product_id']} / {kwargs['variant_id']} / "
                f"{kwargs['background']} / {kwargs['camera_angle']} / "
                f"{kwargs['requested_output']}"
            )
        )


def _shell() -> ProductCompletionShell:
    return ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(_FakeController())
    )


def test_shell_has_product_completion_title_and_navigation(qt_app) -> None:
    shell = _shell()
    try:
        assert shell.windowTitle() == WINDOW_TITLE
        assert [shell.navigation.item(i).text() for i in range(shell.navigation.count())] == list(NAVIGATION_LABELS)
    finally:
        shell.close()


def test_shell_has_three_pane_layout_and_product_context(qt_app) -> None:
    shell = _shell()
    try:
        splitter = shell.findChild(QSplitter, "mainThreePaneSplitter")
        assert splitter is not None
        assert splitter.count() == 3
        assert shell.findChild(QScrollArea, "productContextPanel") is not None
    finally:
        shell.close()


def test_create_page_scrolls_instead_of_crushing_required_brief_rows(qt_app) -> None:
    shell = _shell()
    try:
        page = shell.findChild(QScrollArea, "createPageScrollArea")
        assert page is not None
        assert shell.pages.widget(0) is page
        assert page.widget() is not None
        assert shell.deliverable_edit.objectName() == "creativeBriefRequiredOutput"
        assert "wajib" in shell.deliverable_edit.placeholderText().lower()
        assert shell.deliverable_edit.parentWidget() is not None

        shell.show()
        qt_app.processEvents()
        assert page.verticalScrollBar().maximum() > 0
        page.ensureWidgetVisible(shell.deliverable_edit)
        qt_app.processEvents()
        assert shell.deliverable_edit.isVisible()
        shell.deliverable_edit.setText("Ecommerce product hero visual")
        assert shell.current_brief().deliverable == "Ecommerce product hero visual"
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


def test_product_selection_scopes_variant_and_updates_context(qt_app) -> None:
    shell = _shell()
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        assert shell.variant_combo.isEnabled()
        assert shell.variant_combo.findText("White Glossy") >= 0
        shell.variant_combo.setCurrentText("White Glossy")
        qt_app.processEvents()
        assert shell.context_title.text() == "SV300 / White Glossy"
    finally:
        shell.close()


def test_creative_brief_is_richer_than_legacy_three_fields(qt_app) -> None:
    shell = _shell()
    try:
        shell.objective_edit.setText("ecommerce hero")
        shell.environment_edit.setText("dark studio")
        shell.camera_edit.setText("front")
        shell.shot_type_edit.setText("medium product shot")
        shell.lighting_edit.setText("soft directional")
        shell.composition_edit.setText("centered")
        shell.mood_edit.setText("premium")
        shell.aspect_ratio_edit.setText("4:5")
        shell.orientation_edit.setText("portrait")
        shell.product_emphasis_edit.setText("helmet dominant")
        shell.preserve_edit.setText("keep visor clear; preserve logo")
        shell.avoid_edit.setText("no floating product")
        shell.notes_edit.setPlainText("natural floor contact")
        shell.deliverable_edit.setText("grounded product prompt")
        brief = shell.current_brief()
        assert brief.objective == "ecommerce hero"
        assert brief.shot_type == "medium product shot"
        assert brief.lighting_style == "soft directional"
        assert brief.composition == "centered"
        assert brief.aspect_ratio == "4:5"
        assert brief.orientation == "portrait"
        assert brief.product_emphasis == "helmet dominant"
        assert brief.preserve_constraints == ("keep visor clear", "preserve logo")
        assert brief.avoid_constraints == ("no floating product",)
        assert brief.freeform_notes == "natural floor contact"
        assert brief.legacy_submit_fields()["background"] == "dark studio"
    finally:
        shell.close()


def test_legacy_grounded_prompt_adapter_preserves_existing_submit_contract(qt_app) -> None:
    shell = _shell()
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.variant_combo.setCurrentText("White Glossy")
        shell.environment_edit.setText("dark studio")
        shell.camera_edit.setText("front")
        shell.deliverable_edit.setText("grounded product prompt")
        shell.prompt_button.click()
        qt_app.processEvents()
        assert shell.prompt_preview.toPlainText() == (
            "sv300 / white-glossy / dark studio / front / grounded product prompt"
        )
        assert shell.create_feedback.text() == "Grounded prompt ready."
    finally:
        shell.close()


def test_visual_generation_is_explicitly_disabled_in_foundation_slice(qt_app) -> None:
    shell = _shell()
    try:
        assert not shell.visual_button.isEnabled()
        assert shell._visual_generation_provider is None
        assert shell.visual_button.toolTip() == shell._localizer.tr("provider.rights_warning")
    finally:
        shell.close()


def test_product_context_renders_facts_constraints_and_unknowns_separately(qt_app) -> None:
    shell = _shell()
    try:
        snapshot = ProductContextSnapshot(
            product_id="sv300",
            variant_id="white-glossy",
            product_label="SV300",
            variant_label="White Glossy",
            summary="Grounded product context.",
            fact_groups=(
                ProductFact(
                    fact_id="material",
                    category="Appearance",
                    label="Material",
                    value="ABS",
                    scope="product",
                ),
            ),
            preservation_constraints=(
                ProductConstraint(
                    constraint_id="preserve-material",
                    label="Material",
                    rule_text="Preserve ABS shell material",
                    scope="product",
                ),
            ),
            unknown_topics=(
                ProductUnknown(
                    topic="weight",
                    user_facing_label="Exact weight is not available",
                ),
            ),
        )
        shell.apply_product_context(snapshot)
        assert shell.context_title.text() == "SV300 / White Glossy"
        assert "Material: ABS" in shell.facts_label.text()
        assert "Preserve ABS shell material" in shell.constraints_label.text()
        assert "Exact weight is not available" in shell.unknowns_label.text()
    finally:
        shell.close()


def test_shell_source_does_not_import_governed_storage_or_provider_network() -> None:
    source = Path(__file__).resolve().parents[2] / "src" / "rie" / "ui" / "pyside_product_shell.py"
    text = source.read_text(encoding="utf-8").lower()
    for forbidden in (
        "sqlite3",
        "requests",
        "httpx",
        "openai",
        "anthropic",
        "governed_knowledge_repository",
        "evidence_repository",
    ):
        assert forbidden not in text


def test_packaging_smoke_constructs_shell_and_writes_marker(qt_app, tmp_path, monkeypatch) -> None:
    marker = tmp_path / "pyside-smoke.txt"
    monkeypatch.setenv("RCIS_PYSIDE_PACKAGING_SMOKE_MARKER_PATH", str(marker))
    packaging_smoke_main()
    assert marker.read_text(encoding="ascii") == "RCIS_PYSIDE_FOUNDATION_SMOKE_OK\n"


class _FakeProductIntelligenceQuery:
    def __init__(self) -> None:
        self.context_calls = []
        self.search_calls = []
        self.provenance_calls = []

    def list_products(self):
        return (
            SimpleNamespace(product_id="sv300", label="SV300"),
        )

    def list_variants(self, product_id: str):
        assert product_id == "sv300"
        return (
            SimpleNamespace(
                variant_id="sv300-white-glossy",
                product_id="sv300",
                label="White Glossy",
            ),
        )

    def get_product_context(self, product_id: str, variant_id: str):
        self.context_calls.append((product_id, variant_id))
        return SimpleNamespace(
            product_id=product_id,
            variant_id=variant_id,
            product_label="SV300",
            variant_label="White Glossy",
            summary="Grounded product intelligence loaded.",
            fact_groups=(
                SimpleNamespace(
                    fact_id="fact-1",
                    category="Appearance",
                    label="Finish",
                    value="White glossy shell finish",
                    scope="variant",
                    authority_state="grounded",
                    provenance_refs=("ev-1",),
                ),
            ),
            preservation_constraints=(
                SimpleNamespace(
                    constraint_id="constraint-1",
                    label="Finish",
                    rule_text="Preserve the white glossy shell finish",
                    scope="variant",
                    severity="preserve",
                    source_fact_refs=("fact-1",),
                ),
            ),
            authorized_reference_asset_ids=(),
            unknown_topics=(
                SimpleNamespace(
                    topic="mass",
                    user_facing_label="Exact mass is not available.",
                    reason="absent",
                ),
            ),
            conflicts=(),
            provenance_summary="official / manufacturer / accepted",
        )


    def search_product_facts(
        self,
        query: str,
        *,
        product_id: str,
        variant_id: str,
    ):
        self.search_calls.append((query, product_id, variant_id))
        if "glossy" not in query.casefold():
            return ()
        return (
            SimpleNamespace(
                fact_id="fact-1",
                category="Appearance",
                label="Finish",
                value="White glossy shell finish",
                scope="variant",
                authority_state="grounded",
                provenance_refs=("ev-1",),
            ),
        )

    def get_provenance(self, reference_id: str):
        self.provenance_calls.append(reference_id)
        assert reference_id == "ev-1"
        return SimpleNamespace(
            reference_id="ev-1",
            source_type="structured_evidence",
            authority="manufacturer-approved-source",
            status="approved",
            version="2026.08",
            source_paths=(
                "SV300/sv300manual book.pdf",
                "SV300/White Glossy/front.png",
            ),
        )


def test_product_intelligence_query_hydrates_product_context_on_variant_selection(qt_app) -> None:
    query = _FakeProductIntelligenceQuery()
    shell = ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(_FakeController()),
        product_intelligence_query=query,
    )
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        assert shell.variant_combo.findText("White Glossy") >= 0

        shell.variant_combo.setCurrentText("White Glossy")
        qt_app.processEvents()

        assert query.context_calls == [
            ("sv300", "sv300-white-glossy"),
        ]
        assert shell.context_title.text() == "SV300 / White Glossy"
        assert "White glossy shell finish" in shell.facts_label.text()
        assert "Preserve the white glossy shell finish" in shell.constraints_label.text()
        assert "Exact mass is not available." in shell.unknowns_label.text()
        assert shell.create_feedback.text().startswith(
            "Grounded Product Context ready"
        )
    finally:
        shell.close()


def test_product_intelligence_query_can_drive_selection_without_legacy_adapter(qt_app) -> None:
    query = _FakeProductIntelligenceQuery()
    shell = ProductCompletionShell(product_intelligence_query=query)
    try:
        assert shell.product_combo.findText("SV300") >= 0
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.variant_combo.setCurrentText("White Glossy")
        qt_app.processEvents()
        assert "White glossy shell finish" in shell.facts_label.text()

        shell.prompt_button.click()
        qt_app.processEvents()
        assert "adapter is not connected" in shell.create_feedback.text()
    finally:
        shell.close()


def test_pyside_source_uses_query_only_through_presentation_adapter() -> None:
    source = Path(__file__).resolve().parents[2] / "src" / "rie" / "ui" / "pyside_product_shell.py"
    text = source.read_text(encoding="utf-8")
    assert "ProductIntelligencePresentationAdapter" in text
    assert "product_intelligence_query: Any | None" in text
    lowered = text.lower()
    for forbidden in (
        "evidence_repository",
        "governed_asset_library_registry",
        "persisted_evidence",
        "sqlite3",
    ):
        assert forbidden not in lowered



def _products_shell(query=None) -> ProductCompletionShell:
    return ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(_FakeController()),
        product_intelligence_query=query,
    )


def _select_products_workspace_variant(
    shell: ProductCompletionShell,
    qt_app: QApplication,
) -> None:
    shell.navigation.setCurrentRow(NAVIGATION.index("Products"))
    qt_app.processEvents()
    shell.products_product_combo.setCurrentText("SV300")
    qt_app.processEvents()
    shell.products_variant_combo.setCurrentText("White Glossy")
    qt_app.processEvents()


def test_products_navigation_is_real_workspace_not_placeholder(qt_app) -> None:
    shell = _products_shell(_FakeProductIntelligenceQuery())
    try:
        shell.navigation.setCurrentRow(NAVIGATION.index("Products"))
        qt_app.processEvents()
        assert shell.pages.currentWidget().objectName() == "productsWorkspace"
        assert shell.products_product_combo.objectName() == "productsProductSelector"
        assert shell.products_fact_search.objectName() == "productsFactSearch"
        assert (
            shell.products_provenance_detail.objectName()
            == "productsProvenanceDetail"
        )
    finally:
        shell.close()


def test_products_workspace_populates_query_products_and_variants(qt_app) -> None:
    query = _FakeProductIntelligenceQuery()
    shell = _products_shell(query)
    try:
        assert shell.products_product_combo.findText("SV300") >= 0
        shell.products_product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        assert shell.products_variant_combo.isEnabled()
        assert shell.products_variant_combo.findText("White Glossy") >= 0
    finally:
        shell.close()


def test_products_workspace_variant_selection_renders_grounded_context(qt_app) -> None:
    query = _FakeProductIntelligenceQuery()
    shell = _products_shell(query)
    try:
        _select_products_workspace_variant(shell, qt_app)

        assert query.context_calls[-1] == (
            "sv300",
            "sv300-white-glossy",
        )
        assert shell.products_identity.text() == "SV300 / White Glossy"
        assert "White glossy shell finish" in shell.products_facts.toPlainText()
        assert (
            "Preserve the white glossy shell finish"
            in shell.products_constraints.toPlainText()
        )
        assert "Exact mass is not available." in shell.products_unknowns.text()
        assert "manufacturer" in shell.products_provenance_summary.text()
        assert shell.products_provenance_combo.findText("ev-1") >= 0
    finally:
        shell.close()


def test_products_workspace_fact_search_uses_product_intelligence_query(qt_app) -> None:
    query = _FakeProductIntelligenceQuery()
    shell = _products_shell(query)
    try:
        _select_products_workspace_variant(shell, qt_app)
        shell.products_fact_search.setText("glossy")
        shell.products_fact_search_button.click()
        qt_app.processEvents()

        assert query.search_calls == [
            ("glossy", "sv300", "sv300-white-glossy"),
        ]
        assert "White glossy shell finish" in (
            shell.products_search_results.toPlainText()
        )
        assert "1 match" in shell.products_status.text()
    finally:
        shell.close()


def test_products_workspace_provenance_inspection_uses_query_boundary(qt_app) -> None:
    query = _FakeProductIntelligenceQuery()
    shell = _products_shell(query)
    try:
        _select_products_workspace_variant(shell, qt_app)
        shell.products_provenance_combo.setCurrentText("ev-1")
        shell.products_provenance_button.click()
        qt_app.processEvents()

        assert query.provenance_calls == ["ev-1"]
        detail = shell.products_provenance_detail.toPlainText()
        assert "Authority: manufacturer-approved-source" in detail
        assert "Status: approved" in detail
        assert "Version: 2026.08" in detail
        assert "SV300/White Glossy/front.png" in detail
    finally:
        shell.close()


def test_products_workspace_disconnected_state_has_no_fallback(qt_app) -> None:
    shell = ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(_FakeController())
    )
    try:
        shell.navigation.setCurrentRow(NAVIGATION.index("Products"))
        qt_app.processEvents()
        assert not shell.products_product_combo.isEnabled()
        assert not shell.products_fact_search.isEnabled()
        assert "tidak tersedia" in shell.products_status.text().lower()
        assert "penyimpanan cadangan" in shell.products_status.text().lower()
    finally:
        shell.close()


def test_products_workspace_browsing_does_not_mutate_create_selection(qt_app) -> None:
    query = _FakeProductIntelligenceQuery()
    shell = _products_shell(query)
    try:
        assert shell.product_combo.currentText() == "Choose product..."
        _select_products_workspace_variant(shell, qt_app)
        assert shell.product_combo.currentText() == "Choose product..."
        assert shell.variant_combo.currentText() == "Choose variant..."
    finally:
        shell.close()


def test_products_workspace_source_has_no_direct_storage_or_asset_registry_access() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "ui"
        / "pyside_product_shell.py"
    )
    lowered = source.read_text(encoding="utf-8").lower()
    for forbidden in (
        "evidence_repository",
        "governed_asset_library_registry",
        "persisted_evidence",
        "sqlite3",
        "knowledge_repository",
        "database_connection",
    ):
        assert forbidden not in lowered

class _FakeVisualReferenceAssetQuery:
    product_options = (
        SimpleNamespace(product_id="sv300", label="SV300"),
    )

    def __init__(self) -> None:
        self.list_calls = []
        self.preview_calls = []
        self._asset = SimpleNamespace(
            reference_id="reference-front",
            asset_id="asset-photo-front",
            product_id="sv300",
            variant_id="white-glossy",
            product_label="SV300",
            variant_label="White Glossy",
            filename="front.png",
            source_relative_path="SV300/White Glossy/front.png",
            source_type="APPROVED_PRODUCT_PHOTO",
            authority="RSV_INTERNAL_APPROVED_SOURCE",
            version="2026-08-09",
            status="APPROVED",
            sha256="a" * 64,
            available=True,
        )

    def variant_options_for_product(self, product_id: str):
        assert product_id == "sv300"
        return (
            SimpleNamespace(
                variant_id="white-glossy",
                product_id="sv300",
                label="White Glossy",
            ),
        )

    def list_assets(self, *, product_id: str, variant_id: str):
        self.list_calls.append((product_id, variant_id))
        return (self._asset,)

    def load_preview_bytes(self, asset_id: str):
        self.preview_calls.append(asset_id)
        assert asset_id == "asset-photo-front"
        return b"not-an-image-for-widget-contract-test"


def test_assets_navigation_is_real_read_only_workspace(qt_app) -> None:
    query = _FakeVisualReferenceAssetQuery()
    shell = ProductCompletionShell(visual_reference_asset_query=query)
    try:
        shell.navigation.setCurrentRow(NAVIGATION.index("Assets"))
        qt_app.processEvents()
        assert shell.pages.currentWidget().objectName() == "assetsWorkspace"
        assert shell.assets_product_combo.objectName() == "assetsProductSelector"
        assert shell.assets_list.objectName() == "assetsReferenceList"
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


def test_assets_workspace_browses_approved_reference_metadata(qt_app) -> None:
    query = _FakeVisualReferenceAssetQuery()
    shell = ProductCompletionShell(visual_reference_asset_query=query)
    try:
        shell.navigation.setCurrentRow(NAVIGATION.index("Assets"))
        shell.assets_product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.assets_variant_combo.setCurrentText("White Glossy")
        qt_app.processEvents()
        assert query.list_calls == [("sv300", "white-glossy")]
        assert shell.assets_list.count() == 1
        shell.assets_list.setCurrentRow(0)
        qt_app.processEvents()
        assert "RSV_INTERNAL_APPROVED_SOURCE" in shell.assets_detail.text()
        assert "APPROVED" in shell.assets_detail.text()
        assert "SV300/White Glossy/front.png" in shell.assets_detail.text()
        assert query.preview_calls == ["asset-photo-front"]
    finally:
        shell.close()


def test_create_reference_selection_flows_to_composer_without_generation(qt_app) -> None:
    visual_query = _FakeVisualReferenceAssetQuery()
    composer = _FakeCreativePromptComposer()
    shell = ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(_FakeController()),
        creative_prompt_composer=composer,
        visual_reference_asset_query=visual_query,
    )
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.variant_combo.setCurrentText("White Glossy")
        qt_app.processEvents()
        assert shell.reference_asset_list.count() == 1
        shell.reference_asset_list.item(0).setSelected(True)
        qt_app.processEvents()
        assert shell.current_brief().selected_reference_asset_ids == (
            "asset-photo-front",
        )
        _fill_required_create_fields(shell)
        shell.prompt_button.click()
        qt_app.processEvents()
        assert composer.calls[0]["brief"].selected_reference_asset_ids == (
            "asset-photo-front",
        )
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


class _FakeCreativePromptComposer:
    def __init__(self, *, result=None, error=None) -> None:
        self.calls = []
        self._result = result or SimpleNamespace(
            prompt_text="PC3 compiled grounded prompt",
            grounding_status="PASSED",
            used_knowledge_ids=("knowledge-identity", "knowledge-manual"),
            used_asset_ids=("asset-identity",),
            missing_knowledge=(),
            conflicts=(),
        )
        self._error = error

    def compose_grounded_prompt(self, *, product_id, variant_id, brief):
        self.calls.append(
            {
                "product_id": product_id,
                "variant_id": variant_id,
                "brief": brief,
            }
        )
        if self._error is not None:
            raise self._error
        return self._result


class _FailIfSubmittedController(_FakeController):
    def __init__(self) -> None:
        self.submit_calls = 0

    def submit(self, **kwargs):
        self.submit_calls += 1
        raise AssertionError("legacy adapter must not be called when composer is connected")


def _fill_required_create_fields(shell: ProductCompletionShell) -> None:
    shell.environment_edit.setText("dark studio")
    shell.camera_edit.setText("front three-quarter")
    shell.deliverable_edit.setText("grounded product prompt")


def test_normal_launch_composition_wires_pc2_pc3_and_pc4_dependencies(
    qt_app,
    monkeypatch,
) -> None:
    product_query = _FakeProductIntelligenceQuery()

    class _NormalLaunchVisualQuery(_FakeVisualReferenceAssetQuery):
        def list_assets(self, *, product_id: str, variant_id: str):
            assert product_id == "sv300"
            assert variant_id == "sv300-white-glossy"
            self.list_calls.append((product_id, variant_id))
            self._asset.variant_id = variant_id
            return (self._asset,)

    visual_query = _NormalLaunchVisualQuery()
    composer = _FakeCreativePromptComposer()
    intake_root = "C:/pilot-intake"

    monkeypatch.setattr(
        shell_module,
        "load_remembered_intake_root",
        lambda: intake_root,
    )
    monkeypatch.setattr(
        shell_module.ProductIntelligenceQuery,
        "from_intake_root",
        staticmethod(lambda *, intake_root: product_query),
    )
    monkeypatch.setattr(
        shell_module,
        "VisualReferenceAssetQuery",
        lambda *, intake_root, product_intelligence_query: visual_query,
    )
    monkeypatch.setattr(
        shell_module.CreativePromptComposer,
        "from_intake_root",
        staticmethod(
            lambda *, intake_root, visual_reference_asset_query: composer
        ),
    )

    shell = build_normal_product_completion_shell()
    try:
        assert shell._product_intelligence is not None
        assert shell._creative_prompt_composer is not None
        assert shell._visual_reference_assets is not None
        assert shell.reference_asset_list.count() == 0
        assert "Choose a product and variant" in shell.reference_asset_detail.text()

        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        assert shell.variant_combo.findText("White Glossy") >= 0

        shell.variant_combo.setCurrentText("White Glossy")
        qt_app.processEvents()
        assert visual_query.list_calls == [("sv300", "sv300-white-glossy")]
        assert shell.reference_asset_list.count() == 1
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


def test_normal_launch_without_remembered_intake_remains_disconnected(
    qt_app,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        shell_module,
        "load_remembered_intake_root",
        lambda: None,
    )
    shell = build_normal_product_completion_shell()
    try:
        assert shell._product_intelligence is None
        assert shell._creative_prompt_composer is None
        assert shell._visual_reference_assets is None
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


def test_create_workspace_exposes_rich_pc3_brief_fields(qt_app) -> None:
    shell = _shell()
    try:
        assert shell.shot_type_edit.objectName() == "creativeBriefShotType"
        assert shell.aspect_ratio_edit.objectName() == "creativeBriefAspectRatio"
        assert shell.orientation_edit.objectName() == "creativeBriefOrientation"
        assert (
            shell.product_emphasis_edit.objectName()
            == "creativeBriefProductEmphasis"
        )
        assert shell.preserve_edit.objectName() == "creativeBriefUserPreserve"
        assert shell.avoid_edit.objectName() == "creativeBriefUserAvoid"
        assert shell.notes_edit.objectName() == "creativeBriefFreeformNotes"
        assert shell.prompt_grounding_metadata.objectName() == (
            "promptGroundingMetadata"
        )
    finally:
        shell.close()


def test_pc3_composer_path_is_preferred_over_legacy_adapter(qt_app) -> None:
    controller = _FailIfSubmittedController()
    composer = _FakeCreativePromptComposer()
    shell = ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(controller),
        creative_prompt_composer=composer,
    )
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.variant_combo.setCurrentText("White Glossy")
        _fill_required_create_fields(shell)
        shell.objective_edit.setText("ecommerce hero")
        shell.shot_type_edit.setText("medium product shot")
        shell.aspect_ratio_edit.setText("4:5")
        shell.preserve_edit.setText("keep visor clear; preserve logo")
        shell.avoid_edit.setText("no floating product")
        shell.notes_edit.setPlainText("natural floor contact")

        shell.prompt_button.click()
        qt_app.processEvents()

        assert controller.submit_calls == 0
        assert len(composer.calls) == 1
        call = composer.calls[0]
        assert call["product_id"] == "sv300"
        assert call["variant_id"] == "white-glossy"
        assert call["brief"].objective == "ecommerce hero"
        assert call["brief"].shot_type == "medium product shot"
        assert call["brief"].aspect_ratio == "4:5"
        assert call["brief"].preserve_constraints == (
            "keep visor clear",
            "preserve logo",
        )
        assert call["brief"].avoid_constraints == ("no floating product",)
        assert call["brief"].freeform_notes == "natural floor contact"
        assert shell.prompt_preview.toPlainText() == "PC3 compiled grounded prompt"
        assert "Grounding: PASSED" in shell.prompt_grounding_metadata.text()
        assert "knowledge-identity" in shell.prompt_grounding_metadata.text()
        assert shell.create_feedback.text() == "Grounded prompt ready."
    finally:
        shell.close()


def test_pc3_composer_error_preserves_entered_creative_brief(qt_app) -> None:
    composer = _FakeCreativePromptComposer(
        error=ValueError("environment must be a nonempty string")
    )
    shell = ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(_FakeController()),
        creative_prompt_composer=composer,
    )
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.variant_combo.setCurrentText("White Glossy")
        shell.objective_edit.setText("ecommerce hero")
        shell.environment_edit.setText("   ")
        shell.camera_edit.setText("front")
        shell.shot_type_edit.setText("close-up")
        shell.deliverable_edit.setText("grounded product prompt")

        shell.prompt_button.click()
        qt_app.processEvents()

        assert "environment must be a nonempty string" in shell.create_feedback.text()
        assert shell.objective_edit.text() == "ecommerce hero"
        assert shell.environment_edit.text() == "   "
        assert shell.camera_edit.text() == "front"
        assert shell.shot_type_edit.text() == "close-up"
        assert shell.deliverable_edit.text() == "grounded product prompt"
    finally:
        shell.close()


def test_pc3_failed_grounding_is_not_presented_as_success(qt_app) -> None:
    composer = _FakeCreativePromptComposer(
        result=SimpleNamespace(
            prompt_text="",
            grounding_status="FAILED",
            used_knowledge_ids=("knowledge-identity",),
            used_asset_ids=("asset-identity",),
            missing_knowledge=(),
            conflicts=("creative_override:helmet_body_material",),
        )
    )
    shell = ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(_FakeController()),
        creative_prompt_composer=composer,
    )
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.variant_combo.setCurrentText("White Glossy")
        _fill_required_create_fields(shell)
        shell.prompt_button.click()
        qt_app.processEvents()

        assert shell.prompt_preview.toPlainText() == ""
        assert "Grounding: FAILED" in shell.prompt_grounding_metadata.text()
        assert "creative_override:helmet_body_material" in (
            shell.prompt_grounding_metadata.text()
        )
        assert "could not be completed safely" in shell.create_feedback.text()
    finally:
        shell.close()


def test_legacy_adapter_only_path_remains_compatible_with_richer_fields(qt_app) -> None:
    shell = _shell()
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.variant_combo.setCurrentText("White Glossy")
        shell.environment_edit.setText("dark studio")
        shell.camera_edit.setText("front")
        shell.shot_type_edit.setText("close-up")
        shell.aspect_ratio_edit.setText("4:5")
        shell.deliverable_edit.setText("grounded product prompt")
        shell.prompt_button.click()
        qt_app.processEvents()

        assert shell.prompt_preview.toPlainText() == (
            "sv300 / white-glossy / dark studio / front / grounded product prompt"
        )
        assert "Compatibility path result" in (
            shell.prompt_grounding_metadata.text()
        )
        assert shell.create_feedback.text() == "Grounded prompt ready."
    finally:
        shell.close()


def test_pc3_pyside_source_has_no_direct_storage_access_and_keeps_visuals_disabled() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "ui"
        / "pyside_product_shell.py"
    )
    text = source.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "CreativePromptComposerPresentationAdapter" in text
    assert "creative_prompt_composer: Any | None" in text
    assert "self.visual_button.setEnabled(False)" in text
    for forbidden in (
        "evidence_repository",
        "knowledge_repository",
        "governed_asset_library_registry",
        "persisted_evidence",
        "sqlite3",
        "database_connection",
    ):
        assert forbidden not in lowered

def _gate16_dashboard_builder():
    decision = OperatorApprovalDecision(
        decision_id="decision-current",
        operator_reference="operator-1",
        role_reference="reviewer",
        target_type="KNOWLEDGE",
        target_reference="knowledge-1",
        action="APPROVE",
        reason_reference="reason-1",
        audit_context_reference="audit-context-1",
    )
    bindings = (
        OperatorRoleBinding(
            operator_reference="operator-1",
            role_reference="reviewer",
            binding_reference="binding-1",
            reason_reference="reason-1",
            audit_context_reference="audit-context-1",
        ),
    )
    permissions = (
        RoleActionTargetPermission(
            role_reference="reviewer",
            target_type="KNOWLEDGE",
            action="APPROVE",
            permission_reference="permission-1",
            reason_reference="reason-1",
            audit_context_reference="audit-context-1",
        ),
    )
    context = TargetApprovalContext(
        target_type="KNOWLEDGE",
        target_reference="knowledge-1",
        lifecycle_state="REVIEW_READY",
        lifecycle_eligibility=LIFECYCLE_ELIGIBLE,
        lifecycle_reason_reference="lifecycle-1",
        provenance_status=PROVENANCE_VERIFIED,
        provenance_reference="provenance-1",
        rights_status=RIGHTS_CLEARED,
        rights_reference="rights-1",
        idempotency_status=IDEMPOTENCY_NEW,
        idempotency_reference="idempotency-1",
        conflict_status=CONFLICT_CLEAR,
        conflict_reference="conflict-1",
        reason_reference="reason-1",
        audit_context_reference="audit-context-1",
    )
    history = OperatorApprovalAuditHistory(
        records=(
            OperatorApprovalAuditRecord(
                audit_record_id="audit-record-prior",
                decision_id="decision-prior",
                operator_reference="operator-1",
                role_reference="reviewer",
                permission_reference="permission-1",
                target_type="KNOWLEDGE",
                target_reference="knowledge-1",
                action="APPROVE",
                assessment_outcome="ELIGIBLE",
                assessment_reason_code=(
                    REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
                ),
                reason_reference="reason-1",
                audit_context_reference="audit-context-prior",
                lifecycle_reason_reference="lifecycle-1",
                provenance_reference="provenance-1",
                rights_reference="rights-1",
                idempotency_reference="idempotency-1",
                conflict_reference="conflict-1",
            ),
        )
    )
    calls = []

    def builder(request):
        calls.append(request)
        return build_safe_operator_dashboard(
            request,
            decision,
            bindings,
            permissions,
            context,
            history,
        )

    return builder, calls


def _fill_gate16_request(shell: ProductCompletionShell) -> None:
    shell.approvals_request_id.setText("request-1")
    shell.approvals_operator_reference.setText("operator-1")
    shell.approvals_role_reference.setText("reviewer")
    shell.approvals_target_type.setText("KNOWLEDGE")
    shell.approvals_target_reference.setText("knowledge-1")
    shell.approvals_action.setText("APPROVE")
    shell.approvals_reason_reference.setText("reason-1")
    shell.approvals_audit_context_reference.setText("audit-context-1")
    shell.approvals_audit_limit.setText("10")


def test_approvals_navigation_is_real_workspace_and_safe_when_disconnected(
    qt_app,
) -> None:
    shell = ProductCompletionShell()
    try:
        shell.navigation.setCurrentRow(NAVIGATION.index("Approvals"))
        qt_app.processEvents()

        assert shell.pages.currentWidget().objectName() == "approvalsWorkspace"
        assert not shell.approvals_refresh_button.isEnabled()
        assert "unavailable" in shell.approvals_status.text()
        assert "no storage fallback" in shell.approvals_status.text()
        assert shell.approvals_summary.isReadOnly()
        assert shell.approvals_audit_history.isReadOnly()
    finally:
        shell.close()


def test_approvals_workspace_renders_existing_gate16_dashboard_projection(
    qt_app,
) -> None:
    builder, calls = _gate16_dashboard_builder()
    shell = ProductCompletionShell(operator_dashboard_builder=builder)
    try:
        shell.navigation.setCurrentRow(NAVIGATION.index("Approvals"))
        _fill_gate16_request(shell)
        shell.approvals_refresh_button.click()
        qt_app.processEvents()

        assert len(calls) == 1
        assert isinstance(calls[0], SafeOperatorDashboardRequest)
        assert calls[0].request_id == "request-1"
        assert calls[0].audit_limit == 10
        assert "projection ready" in shell.approvals_status.text()
        assert "No approval mutation has been executed" in (
            shell.approvals_status.text()
        )
        assert f"Status: {STATUS_READY}" in shell.approvals_summary.toPlainText()
        assert "Permission: permission-1" in shell.approvals_summary.toPlainText()
        assert (
            REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
            in shell.approvals_summary.toPlainText()
        )
        assert "audit-record-prior" in shell.approvals_audit_history.toPlainText()
    finally:
        shell.close()


def test_approvals_workspace_invalid_input_does_not_call_dashboard_builder(
    qt_app,
) -> None:
    builder, calls = _gate16_dashboard_builder()
    shell = ProductCompletionShell(operator_dashboard_builder=builder)
    try:
        _fill_gate16_request(shell)
        shell.approvals_audit_limit.setText("not-an-integer")
        shell.approvals_refresh_button.click()
        qt_app.processEvents()

        assert calls == []
        assert "audit limit must be an integer" in shell.approvals_status.text()
        assert shell.approvals_summary.toPlainText() == ""
        assert shell.approvals_audit_history.toPlainText() == ""
    finally:
        shell.close()


def test_approvals_workspace_rejects_invalid_dashboard_result(qt_app) -> None:
    shell = ProductCompletionShell(
        operator_dashboard_builder=lambda _request: SimpleNamespace(
            status="READY"
        )
    )
    try:
        _fill_gate16_request(shell)
        shell.approvals_refresh_button.click()
        qt_app.processEvents()

        assert "returned an invalid result" in shell.approvals_status.text()
        assert shell.approvals_summary.toPlainText() == ""
    finally:
        shell.close()


def test_gate16_pyside_source_has_no_direct_storage_or_approval_mutation() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "ui"
        / "pyside_product_shell.py"
    )
    text = source.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "SafeOperatorDashboardRequest" in text
    assert "SafeOperatorDashboardResult" in text
    assert "operator_dashboard_builder: Any | None" in text
    assert "No approval mutation has been executed" in text
    for forbidden in (
        "evidence_repository",
        "knowledge_repository",
        "governed_asset_library_registry",
        "persisted_evidence",
        "sqlite3",
        "database_connection",
        "append_operator_approval_audit",
    ):
        assert forbidden not in lowered



def _fill_gate18_workflow_request(shell: ProductCompletionShell) -> None:
    shell.workflow_request_id.setText("workflow-request-1")
    shell.workflow_idempotency_key.setText("workflow-idempotency-1")
    shell.workflow_project_reference.setText("project-1")
    shell.workflow_campaign_reference.setText("campaign-1")
    shell.workflow_creative_brief_reference.setText("brief-1")
    shell.workflow_knowledge_references.setText("knowledge-1")
    shell.workflow_governed_asset_references.setText("asset-context-1")
    shell.workflow_instruction_reference.setText("instruction-1")
    shell.workflow_instruction_authority.setText("APPROVED_INSTRUCTION")
    shell.workflow_requesting_actor.setText("operator-1")
    shell.workflow_request_timestamp.setText(
        "2026-09-27T00:00:00+00:00"
    )
    shell.workflow_contract_name.setText("GATE_18_CREATIVE_WORKFLOW")
    shell.workflow_contract_version.setText("1.0")
    shell.workflow_output_purpose.setText("CREATIVE_WORKFLOW_ASSESSMENT")
    shell.workflow_review_policy.setText("LOCAL_SINGLE_OPERATOR_REVIEW")
    shell.workflow_manual_handoff_declared.setChecked(False)

    shell.workflow_current_state.setText("REQUESTED")
    shell.workflow_requested_state.setText("INPUTS_VALIDATED")
    shell.workflow_responsible_kind.setText("ACTOR")
    shell.workflow_responsible_reference.setText("operator-1")
    shell.workflow_assessment_timestamp.setText(
        "2026-09-27T00:01:00+00:00"
    )
    shell.workflow_evidence_references.setText("evidence-1")
    shell.workflow_reason_codes.setText("INPUTS_VALIDATED")
    shell.workflow_handoff_reference.setText("")
    shell.workflow_candidate_reference.setText("")
    shell.workflow_gate16_reference.setText("decision-1")
    shell.workflow_gate15_reference.setText("governed-asset-1")


def test_gate18_workflow_navigation_is_real_workspace_and_safe_when_disconnected(
    qt_app,
) -> None:
    shell = ProductCompletionShell()
    try:
        shell.navigation.setCurrentRow(NAVIGATION.index("Workflow"))
        qt_app.processEvents()

        assert shell.pages.currentWidget().objectName() == (
            "creativeWorkflowWorkspace"
        )
        assert not shell.workflow_assess_button.isEnabled()
        assert "unavailable" in shell.workflow_status.text()
        assert "no storage or authority fallback" in shell.workflow_status.text()
        assert shell.workflow_summary.isReadOnly()
    finally:
        shell.close()


def test_gate18_workflow_workspace_reuses_existing_application_service(
    qt_app,
) -> None:
    shell = ProductCompletionShell(
        governed_workflow_assessor=assess_governed_creative_workflow
    )
    try:
        shell.navigation.setCurrentRow(NAVIGATION.index("Workflow"))
        _fill_gate18_workflow_request(shell)
        shell.workflow_assess_button.click()
        qt_app.processEvents()

        summary = shell.workflow_summary.toPlainText()
        assert "Governed workflow assessment ready" in (
            shell.workflow_status.text()
        )
        assert "Disposition: ACCEPTED" in summary
        assert "Current State: REQUESTED" in summary
        assert "Requested State: INPUTS_VALIDATED" in summary
        assert "Resulting State: INPUTS_VALIDATED" in summary
        assert (
            "Gate 16 Decision: project-1 / campaign-1 / decision-1"
            in summary
        )
        assert (
            "Gate 15 Asset: project-1 / campaign-1 / governed-asset-1"
            in summary
        )
        assert "Production Release Claimed: False" in summary
        assert "production release has been executed" in (
            shell.workflow_status.text()
        )
    finally:
        shell.close()


def test_gate18_workflow_invalid_input_does_not_fabricate_assessment(
    qt_app,
) -> None:
    calls = []

    def assessor(**kwargs):
        calls.append(kwargs)
        return assess_governed_creative_workflow(**kwargs)

    shell = ProductCompletionShell(governed_workflow_assessor=assessor)
    try:
        _fill_gate18_workflow_request(shell)
        shell.workflow_assessment_timestamp.setText("not-a-timestamp")
        shell.workflow_assess_button.click()
        qt_app.processEvents()

        assert calls == []
        assert "ISO-8601 timestamp" in shell.workflow_status.text()
        assert shell.workflow_summary.toPlainText() == ""
    finally:
        shell.close()


def test_gate18_workflow_rejects_invalid_assessor_result(qt_app) -> None:
    shell = ProductCompletionShell(
        governed_workflow_assessor=lambda **_kwargs: SimpleNamespace(
            production_release_claimed=False
        )
    )
    try:
        _fill_gate18_workflow_request(shell)
        shell.workflow_assess_button.click()
        qt_app.processEvents()

        assert "returned an invalid result" in shell.workflow_status.text()
        assert shell.workflow_summary.toPlainText() == ""
    finally:
        shell.close()


def test_gate18_normal_launch_remains_disconnected_without_authority(
    qt_app,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        shell_module,
        "load_remembered_intake_root",
        lambda: None,
    )
    shell = build_normal_product_completion_shell()
    try:
        assert shell._governed_workflow_assessor is None
        assert not shell.workflow_assess_button.isEnabled()
        assert "no storage or authority fallback" in (
            shell.workflow_status.text()
        )
    finally:
        shell.close()


def test_gate18_pyside_source_reuses_backend_without_release_execution() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "ui"
        / "pyside_product_shell.py"
    )
    text = source.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "GovernedCreativeWorkflowRequest" in text
    assert "GovernedCreativeWorkflowApplicationAssessment" in text
    assert "governed_workflow_assessor: Any | None" in text
    assert "creativeWorkflowWorkspace" in text
    assert "Production Release Claimed" in text
    assert "production_release_requested" not in text
    assert "local_operator_runtime" not in lowered

    for forbidden in (
        "evidence_repository",
        "knowledge_repository",
        "governed_asset_library_registry",
        "persisted_evidence",
        "sqlite3",
        "database_connection",
    ):
        assert forbidden not in lowered


def test_c20_a_create_visual_first_four_step_layout(qt_app) -> None:
    from PySide6.QtWidgets import QGroupBox, QLabel

    shell = _shell()
    try:
        page = shell.findChild(QScrollArea, "createPageScrollArea")
        assert page is shell.pages.widget(0)
        assert shell.findChild(QLabel, "createHeading").text() == "Buat Visual Produk"
        for name in (
            "createStepProduct", "createStepConcept",
            "createStepReferences", "createStepReview",
        ):
            assert shell.findChild(QLabel, name) is not None
        for name in (
            "createProductCard", "createConceptCard",
            "createReferenceCard", "createReviewCard",
        ):
            assert shell.findChild(QGroupBox, name) is not None
        assert shell.deliverable_edit.objectName() == "creativeBriefRequiredOutput"
        assert shell.deliverable_edit.text() == ""
        assert shell.objective_edit.text() == ""
        assert shell.environment_edit.text() == ""
        assert not shell.advanced_brief_panel.isAncestorOf(shell.environment_edit)
        assert not shell.advanced_brief_panel.isAncestorOf(shell.camera_edit)
        assert not shell.advanced_brief_panel.isAncestorOf(shell.deliverable_edit)
        assert shell.prompt_button.objectName() == "buildGroundedPrompt"
        assert not shell.visual_button.isEnabled()
        assert "provider" in shell.create_safety_note.text().lower()
    finally:
        shell.close()


def test_c20_a_advanced_brief_disclosure_preserves_model_values(qt_app) -> None:
    shell = _shell()
    try:
        shell.show()
        qt_app.processEvents()
        assert not shell.advanced_brief_toggle.isChecked()
        assert not shell.advanced_brief_panel.isVisible()
        shell.advanced_brief_toggle.click()
        qt_app.processEvents()
        assert shell.advanced_brief_panel.isVisible()
        shell.environment_edit.setText("professional studio")
        shell.camera_edit.setText("front three-quarter")
        shell.lighting_edit.setText("soft studio lighting")
        shell.deliverable_edit.setText("ecommerce hero visual")
        brief = shell.current_brief()
        assert brief.environment == "professional studio"
        assert brief.camera_angle == "front three-quarter"
        assert brief.lighting_style == "soft studio lighting"
        assert brief.deliverable == "ecommerce hero visual"
        shell.advanced_brief_toggle.click()
        qt_app.processEvents()
        assert not shell.advanced_brief_panel.isVisible()
        assert shell.current_brief().environment == "professional studio"
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


def test_c20_a_normal_shell_has_no_hidden_provider_or_auto_selection(qt_app) -> None:
    shell = ProductCompletionShell()
    try:
        assert shell.product_combo.currentText() == "Choose product..."
        assert shell.variant_combo.currentText() == "Choose variant..."
        assert shell.reference_asset_list.selectedItems() == []
        assert shell.visual_button.isEnabled() is False
        assert shell.prompt_preview.toPlainText() == ""
    finally:
        shell.close()


def test_c20_b_reference_gallery_has_actual_local_thumbnails(qt_app) -> None:
    import io
    from PIL import Image
    from PySide6.QtWidgets import QListView

    visual_query = _FakeVisualReferenceAssetQuery()
    output = io.BytesIO()
    Image.new("RGB", (50, 32), (77, 130, 188)).save(output, format="PNG")
    png = output.getvalue()
    visual_query.load_preview_bytes = lambda asset_id: png
    shell = ProductCompletionShell(
        adapter=GroundedPromptCompatibilityAdapter(_FakeController()),
        visual_reference_asset_query=visual_query,
    )
    try:
        shell.product_combo.setCurrentText("SV300")
        qt_app.processEvents()
        shell.variant_combo.setCurrentText("White Glossy")
        qt_app.processEvents()
        assert shell.reference_asset_list.viewMode() == QListView.ViewMode.IconMode
        assert shell.reference_asset_list.count() == 1
        item = shell.reference_asset_list.item(0)
        assert not item.icon().isNull()
        item.setSelected(True)
        qt_app.processEvents()
        assert shell.current_brief().selected_reference_asset_ids == (
            "asset-photo-front",
        )
        assert "bukan izin" in shell.reference_asset_detail.text().lower()
        assert shell.visual_button.isEnabled() is False
    finally:
        shell.close()


def test_c20_b_product_summary_hides_technical_detail_by_default(qt_app) -> None:
    shell = _shell()
    try:
        shell.show()
        qt_app.processEvents()
        assert not shell.context_technical_panel.isVisible()
        assert "izin" in shell.context_governance_note.text().lower()
        assert shell.constraints_label.isVisible()
        shell.context_technical_toggle.click()
        qt_app.processEvents()
        assert shell.context_technical_panel.isVisible()
        assert shell.facts_label is not None
        assert shell.references_label is not None
        assert shell.unknowns_label is not None
        shell.context_technical_toggle.click()
        qt_app.processEvents()
        assert not shell.context_technical_panel.isVisible()
    finally:
        shell.close()


def test_c20_b_prompt_review_distinguishes_grounding_from_provider_rights(qt_app) -> None:
    shell = _shell()
    try:
        shell.show()
        qt_app.processEvents()
        assert not shell.prompt_grounding_metadata.isVisible()
        assert "Belum ada prompt" in shell.create_grounding_status.text()
        shell.prompt_preview.setPlainText("Example grounded prompt")
        shell.prompt_grounding_metadata.setText(
            "Grounding: PASSED | Knowledge: knowledge-fixture | "
            "Grounded Assets: none | Selected References: reference-fixture | "
            "Missing: none | Conflicts: none"
        )
        shell._refresh_create_grounding_status()
        assert "grounding lulus" in shell.create_grounding_status.text().lower()
        assert not shell.visual_button.isEnabled()
        shell.create_grounding_details_toggle.click()
        qt_app.processEvents()
        assert shell.prompt_grounding_metadata.isVisible()
        assert "Grounded Assets: none" in shell.prompt_grounding_metadata.text()
        shell.prompt_preview.clear()
        shell.prompt_grounding_metadata.setText("No grounded prompt built yet.")
        shell.create_feedback.setText(
            "Could not build prompt: deliverable must be a nonempty string"
        )
        shell._refresh_create_grounding_status()
        assert "wajib" in shell.create_grounding_status.text().lower()
    finally:
        shell.close()


def test_c20_e_primary_navigation_is_localized_and_secondary_routes_are_reachable(qt_app) -> None:
    from rie.ui.pyside_product_shell import NAVIGATION_LABELS
    shell = _shell()
    try:
        assert shell.navigation.count() == len(NAVIGATION) == len(NAVIGATION_LABELS)
        assert shell.navigation.item(0).text() == "Buat Visual"
        assert shell.navigation.item(2).text() == "Foto Produk"
        assert shell.navigation.isRowHidden(3)
        shell.nav_more_button.click()
        qt_app.processEvents()
        assert not shell.navigation.isRowHidden(3)
        assert not shell.navigation.isRowHidden(8)
        shell.navigation.setCurrentRow(NAVIGATION.index("Approvals"))
        qt_app.processEvents()
        assert shell.pages.currentWidget().objectName() == "approvalsWorkspace"
        shell.nav_more_button.click()
        qt_app.processEvents()
        assert shell.navigation.isRowHidden(3)
    finally:
        shell.close()


def test_c20_e_create_ui_is_readable_without_changing_required_contract(qt_app) -> None:
    shell = _shell()
    try:
        assert shell.deliverable_edit.objectName() == "creativeBriefRequiredOutput"
        assert "wajib" in shell.deliverable_edit.placeholderText().lower()
        assert "Contoh:" in shell.lighting_edit.placeholderText()
        assert "visualFirstCreateContent" in shell._create_page.styleSheet()
        assert "font-size: 14px" in shell._create_page.styleSheet()
        assert shell.prompt_preview.minimumHeight() == 154
        assert shell.visual_button.isEnabled() is False
        assert "belum tersedia" in shell.visual_button.text().lower()
        shell.environment_edit.setText("studio profesional")
        shell.camera_edit.setText("tampak depan")
        shell.deliverable_edit.setText("prompt produk katalog")
        assert shell.current_brief().environment == "studio profesional"
        assert shell.current_brief().camera_angle == "tampak depan"
        assert shell.current_brief().deliverable == "prompt produk katalog"
    finally:
        shell.close()


def test_c20_e_secondary_navigation_preserves_internal_route_identity(qt_app) -> None:
    shell = _shell()
    try:
        for route, workspace in (
            ("Products", "productsWorkspace"),
            ("Assets", "assetsWorkspace"),
            ("Workflow", "creativeWorkflowWorkspace"),
        ):
            shell.navigation.setCurrentRow(NAVIGATION.index(route))
            qt_app.processEvents()
            assert shell.pages.currentWidget().objectName() == workspace
        assert shell.nav_more_button.isChecked()
        assert shell._visual_generation_provider is None
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()

def test_c20_h2_live_id_en_roundtrip_keeps_brief_prompt_and_routes(qt_app, tmp_path, monkeypatch) -> None:
    from rie.ui.studio_ui_preferences import load_preferred_locale
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    shell = _shell()
    try:
        shell.show()
        qt_app.processEvents()
        assert shell.language_combo.currentData() == "id-ID"
        assert shell.navigation.item(0).text() == "Buat Visual"
        shell.environment_edit.setText("studio profesional")
        shell.camera_edit.setText("sisi depan")
        shell.deliverable_edit.setText("foto katalog")
        shell.prompt_preview.setPlainText("PRODUCT LOCKS: keep approved variant identity")
        shell.prompt_grounding_metadata.setText(
            "Grounding: PASSED | Missing: none | Conflicts: none"
        )
        shell._refresh_create_grounding_status()
        shell.nav_more_button.click()
        qt_app.processEvents()
        assert shell.nav_more_button.isChecked()
        original_route = shell.pages.currentIndex()
        locale_index = shell.language_combo.findData("en-US")
        assert locale_index >= 0
        shell.language_combo.setCurrentIndex(locale_index)
        qt_app.processEvents()
        assert shell.navigation.item(0).text() == "Create Visual"
        assert shell.findChild(shell_module.QLabel, "createHeading").text() == "Create Product Visual"
        assert shell.visual_button.toolTip() == shell._localizer.tr("provider.rights_warning")
        assert shell._create_page.findChild(shell_module.QGroupBox, "createConceptCard").title() == "2. Define Visual Concept"
        assert shell._h2_brief_form.labelForField(shell.camera_edit).text() == "Camera angle (required)"
        assert shell.prompt_button.text() == "Build Prompt"
        assert "grounding passed" in shell.create_grounding_status.text().lower()
        assert shell.nav_more_button.isChecked()
        assert shell.pages.currentIndex() == original_route
        assert shell.environment_edit.text() == "studio profesional"
        assert shell.camera_edit.text() == "sisi depan"
        assert shell.deliverable_edit.text() == "foto katalog"
        assert shell.prompt_preview.toPlainText() == "PRODUCT LOCKS: keep approved variant identity"
        assert load_preferred_locale() == "en-US"
        assert not shell.visual_button.isEnabled()
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("id-ID"))
        qt_app.processEvents()
        assert shell.navigation.item(0).text() == "Buat Visual"
        assert shell.findChild(shell_module.QLabel, "createHeading").text() == "Buat Visual Produk"
        assert shell.visual_button.toolTip() == shell._localizer.tr("provider.rights_warning")
        assert "grounding lulus" in shell.create_grounding_status.text().lower()
        assert load_preferred_locale() == "id-ID"
    finally:
        shell.close()


def test_c20_h2_saved_locale_loaded_in_new_shell_without_modifying_intake(qt_app, tmp_path, monkeypatch) -> None:
    from rie.ui.studio_ui_preferences import save_preferred_locale
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    save_preferred_locale("en-US")
    shell = _shell()
    try:
        assert shell.language_combo.currentData() == "en-US"
        assert shell.navigation.item(1).text() == "Products"
        assert shell.prompt_button.text() == "Build Prompt"
        assert shell.navigation.count() == len(NAVIGATION)
        assert not (tmp_path / "RCIS" / "settings.json").exists()
    finally:
        shell.close()


def test_c20_h2_reference_widget_and_model_identity_do_not_reset_on_switch(qt_app, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    shell = _shell()
    try:
        original_widget = shell.reference_asset_list
        original_model = original_widget.model()
        original_count = original_widget.count()
        original_combo = shell.product_combo
        original_prompt = shell.prompt_preview
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("en-US"))
        assert shell.reference_asset_list is original_widget
        assert shell.reference_asset_list.model() is original_model
        assert shell.reference_asset_list.count() == original_count
        assert shell.product_combo is original_combo
        assert shell.prompt_preview is original_prompt
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()

def test_c20_h3a_context_headers_switch_both_languages_without_mutating_rights(
    qt_app, tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    shell = _shell()
    try:
        shell.show()
        qt_app.processEvents()
        assert shell.language_combo.currentData() == "id-ID"
        assert shell._h3_context_heading.text() == "Ringkasan Produk"
        assert "izin" in shell.context_governance_note.text().lower()
        shell.context_technical_toggle.click()
        qt_app.processEvents()
        assert "Sembunyikan" in shell.context_technical_toggle.text()
        assert shell.context_technical_panel.isVisible()
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("en-US"))
        qt_app.processEvents()
        assert shell._h3_context_heading.text() == "Product Summary"
        assert "Hide technical details" in shell.context_technical_toggle.text()
        assert "external AI" in shell.context_governance_note.text()
        assert shell.context_technical_panel.isVisible()
        assert shell._h3_context_section_titles["Fakta produk (rinci)"].text() == "Product facts (detailed)"
        shell.context_title.setText("FFS21 / Hustle")
        shell.context_summary.setText("SOURCE GROUNDED FACT: DO NOT TRANSLATE")
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("id-ID"))
        assert shell.context_title.text() == "FFS21 / Hustle"
        assert shell.context_summary.text() == "SOURCE GROUNDED FACT: DO NOT TRANSLATE"
        assert shell._h3_context_heading.text() == "Ringkasan Produk"
        assert "Lihat" not in shell.context_technical_toggle.text()
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


def test_c20_h3a_selected_photo_caption_switch_retains_internal_identity(
    qt_app, tmp_path, monkeypatch
) -> None:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QListWidgetItem
    from types import SimpleNamespace
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    shell = _shell()
    try:
        shell.show()
        qt_app.processEvents()
        shell.reference_asset_list.setEnabled(True)
        selected = QListWidgetItem("photo-source-name.png")
        selected.setData(Qt.ItemDataRole.UserRole, "reference-unchanged")
        shell.reference_asset_list.addItem(selected)
        shell._create_reference_assets_by_ref["reference-unchanged"] = SimpleNamespace(
            available=True, asset_id="asset-unchanged", filename="photo-source-name.png"
        )
        selected.setSelected(True)
        shell._h3_reference_status()
        assert "1 foto dipilih" in shell.reference_asset_detail.text()
        assert "photo-source-name.png" in shell.reference_asset_detail.text()
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("en-US"))
        qt_app.processEvents()
        assert "1 photo(s) selected" in shell.reference_asset_detail.text()
        assert "Local preview" in shell.reference_asset_detail.text()
        assert selected.isSelected()
        assert selected.data(Qt.ItemDataRole.UserRole) == "reference-unchanged"
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("id-ID"))
        assert "1 foto dipilih" in shell.reference_asset_detail.text()
        assert "reference-unchanged" in shell._create_reference_assets_by_ref
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()

def test_c20_h3b_four_workspaces_switch_chrome_without_changing_request_fields(qt_app, tmp_path, monkeypatch) -> None:
    from PySide6.QtWidgets import QGroupBox, QLabel
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    shell = _shell()
    try:
        shell.approvals_request_id.setText('approval-original-123')
        shell.workflow_request_id.setText('workflow-original-456')
        shell.workflow_contract_name.setText('GATE_18_CREATIVE_WORKFLOW')
        shell.show()
        qt_app.processEvents()
        assert shell.findChild(QLabel, 'productsHeading').text() == 'Produk'
        assert shell.findChild(QLabel, 'approvalsHeading').text() == 'Persetujuan'
        assert shell.findChild(QLabel, 'creativeWorkflowHeading').text() == 'Alur Kerja'
        original_widget = shell.workflow_request_id
        original_pages = [shell.pages.widget(i) for i in range(shell.pages.count())]
        shell.navigation.setCurrentRow(NAVIGATION.index('Workflow'))
        selected_route = shell.pages.currentIndex()
        shell.language_combo.setCurrentIndex(shell.language_combo.findData('en-US'))
        qt_app.processEvents()
        assert shell.findChild(QLabel, 'productsHeading').text() == 'Products'
        assert shell.findChild(QLabel, 'assetsHeading').text() == 'Assets'
        assert shell.findChild(QLabel, 'approvalsHeading').text() == 'Approvals'
        assert shell.findChild(QLabel, 'creativeWorkflowHeading').text() == 'Workflow'
        assert shell.workflow_request_id is original_widget
        assert shell.workflow_request_id.text() == 'workflow-original-456'
        assert shell.approvals_request_id.text() == 'approval-original-123'
        assert shell.workflow_contract_name.text() == 'GATE_18_CREATIVE_WORKFLOW'
        assert shell.pages.currentIndex() == selected_route
        assert [shell.pages.widget(i) for i in range(shell.pages.count())] == original_pages
        assert not shell.visual_button.isEnabled()
        shell.language_combo.setCurrentIndex(shell.language_combo.findData('id-ID'))
        qt_app.processEvents()
        assert shell.findChild(QLabel, 'productsHeading').text() == 'Produk'
        assert shell.findChild(QLabel, 'creativeWorkflowHeading').text() == 'Alur Kerja'
    finally:
        shell.close()


def test_c20_h3b_form_labels_bilingual_preserves_operator_input(qt_app, tmp_path, monkeypatch) -> None:
    from PySide6.QtWidgets import QFormLayout, QLabel, QPushButton
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    shell = _shell()
    try:
        shell.workflow_reason_codes.setText('INPUTS_VALIDATED')
        shell.approvals_target_type.setText('KNOWLEDGE')
        def bound(key):
            return [(widget, kind) for widget, kind, k in shell._h3b_bindings if k == key]
        assert len(bound('workspace.reason_codes')) >= 1
        assert bound('workspace.reason_codes')[0][0].text() == 'Kode Alasan'
        assert bound('workspace.search')[0][0].text() == 'Cari'
        assert bound('workspace.approved_references')[0][0].title() == 'Referensi Visual yang Disetujui'
        shell.language_combo.setCurrentIndex(shell.language_combo.findData('en-US'))
        qt_app.processEvents()
        assert bound('workspace.reason_codes')[0][0].text() == 'Reason Codes'
        assert bound('workspace.search')[0][0].text() == 'Search'
        assert bound('workspace.approved_references')[0][0].title() == 'Approved Visual References'
        assert shell.workflow_reason_codes.text() == 'INPUTS_VALIDATED'
        assert shell.approvals_target_type.text() == 'KNOWLEDGE'
        assert shell._visual_generation_provider is None
    finally:
        shell.close()

def test_c20_h3c_dynamic_grounding_status_bilingual_preserves_evidence(
    qt_app, tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    shell = _shell()
    try:
        shell.show()
        qt_app.processEvents()
        prompt = "Grounded helmet prompt — preserve product silhouette"
        metadata = (
            "Grounding: PASSED | Knowledge: knowledge-1 | Grounded Assets: none | "
            "Selected References: reference-1 | Missing: none | Conflicts: none"
        )
        shell.prompt_preview.setPlainText(prompt)
        shell.prompt_grounding_metadata.setText(metadata)
        shell._refresh_create_grounding_status()
        assert shell.create_grounding_status.text() == "Prompt siap ditinjau — grounding lulus."
        assert shell.visual_button.isEnabled() is False
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("en-US"))
        qt_app.processEvents()
        assert shell.create_grounding_status.text() == "Prompt ready for review — grounding passed."
        assert shell.prompt_preview.toPlainText() == prompt
        assert shell.prompt_grounding_metadata.text() == metadata
        assert shell.visual_button.isEnabled() is False
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("id-ID"))
        qt_app.processEvents()
        assert shell.create_grounding_status.text() == "Prompt siap ditinjau — grounding lulus."
    finally:
        shell.close()


def test_c20_h3c_failed_empty_required_status_bilingual_without_mutation(
    qt_app, tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    shell = _shell()
    try:
        shell.show()
        qt_app.processEvents()
        shell.prompt_grounding_metadata.setText("Grounding: FAILED | Missing: environment")
        shell._refresh_create_grounding_status()
        assert shell.create_grounding_status.text() == "Prompt belum siap — periksa detail grounding."
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("en-US"))
        qt_app.processEvents()
        assert shell.create_grounding_status.text() == "Prompt not ready — review grounding details."
        shell.prompt_grounding_metadata.setText("No grounded prompt built yet.")
        shell.create_feedback.setText("Could not build prompt: deliverable must be a nonempty string")
        shell._refresh_create_grounding_status()
        assert shell.create_grounding_status.text() == "Check required fields before building a prompt."
        shell.create_feedback.setText("No prompt built yet.")
        shell._refresh_create_grounding_status()
        assert shell.create_grounding_status.text() == "No prompt yet. Complete the concept, then select Build Prompt."
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("id-ID"))
        qt_app.processEvents()
        assert "Belum ada prompt" in shell.create_grounding_status.text()
        assert shell.visual_button.isEnabled() is False
    finally:
        shell.close()


def test_c20_h3d_unavailable_read_only_status_switch_preserves_safety(qt_app, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    shell = ProductCompletionShell()
    try:
        assert "tidak tersedia" in shell.products_status.text().lower()
        assert "tidak tersedia" in shell.assets_status.text().lower()
        assert "penyimpanan cadangan" in shell.products_status.text().lower()
        assert not shell.visual_button.isEnabled()
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("en-US"))
        qt_app.processEvents()
        assert "unavailable" in shell.products_status.text().lower()
        assert "No storage fallback" in shell.assets_status.text()
        assert not shell.visual_button.isEnabled()
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("id-ID"))
        qt_app.processEvents()
        assert "tidak tersedia" in shell.products_status.text().lower()
    finally:
        shell.close()


def test_c20_h3d_status_translation_never_replaces_opaque_service_message(qt_app, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    shell = _shell()
    try:
        old_brief = shell.current_brief()
        shell._h3d_set_status(shell.products_status, "status.search_empty")
        assert shell.products_status.text() == "Masukkan istilah pencarian fakta."
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("en-US"))
        qt_app.processEvents()
        assert shell.products_status.text() == "Enter a fact search term."
        shell.products_status.setText("OPAQUE_SERVICE_DIAGNOSTIC_123")
        shell.language_combo.setCurrentIndex(shell.language_combo.findData("id-ID"))
        qt_app.processEvents()
        assert shell.products_status.text() == "OPAQUE_SERVICE_DIAGNOSTIC_123"
        assert shell.current_brief() == old_brief
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


def test_c20_i2_copy_button_empty_guard_and_enablement(qt_app) -> None:
    shell = _shell()
    try:
        assert shell.copy_prompt_button.objectName() == "copyGroundedPrompt"
        assert shell.copy_prompt_button.text() == "Salin Prompt"
        assert not shell.copy_prompt_button.isEnabled()
        shell.prompt_preview.setPlainText("  \n ")
        assert not shell.copy_prompt_button.isEnabled()
        shell.prompt_preview.setPlainText("Grounded exact text")
        assert shell.copy_prompt_button.isEnabled()
        assert shell.prompt_preview.isReadOnly()
        assert not shell.visual_button.isEnabled()
    finally:
        shell.close()


def test_c20_i2_copy_exact_prompt_preserves_metadata_and_input(qt_app) -> None:
    shell = _shell()
    board = qt_app.clipboard()
    previous = board.text()
    try:
        payload = "PRODUCT LOCKS: preserve FFS21.\nCreative variables:  studio  \nEnd"
        shell.prompt_preview.setPlainText(payload)
        shell.prompt_grounding_metadata.setText("Grounding: PASSED | Missing: none | Conflicts: none")
        before_meta = shell.prompt_grounding_metadata.text()
        before_brief = shell.current_brief()
        shell.copy_prompt_button.click()
        assert board.text() == payload
        assert shell.copy_prompt_feedback.text() == "Prompt berhasil disalin."
        assert shell.prompt_preview.toPlainText() == payload
        assert shell.prompt_grounding_metadata.text() == before_meta
        assert shell.current_brief() == before_brief
        assert not shell.visual_button.isEnabled()
    finally:
        board.setText(previous)
        shell.close()


def test_c20_i2_copy_feedback_localizes_without_recopy(qt_app) -> None:
    shell = _shell()
    board = qt_app.clipboard()
    previous = board.text()
    try:
        payload = "DO NOT TRANSLATE: exact source prompt"
        shell.prompt_preview.setPlainText(payload)
        shell.copy_prompt_button.click()
        assert board.text() == payload
        shell._localizer.set_locale("en-US")
        shell._h2_apply_language()
        assert shell.copy_prompt_button.text() == "Copy Prompt"
        assert shell.copy_prompt_feedback.text() == "Prompt copied."
        assert board.text() == payload
        shell._localizer.set_locale("id-ID")
        shell._h2_apply_language()
        assert shell.copy_prompt_button.text() == "Salin Prompt"
        assert shell.copy_prompt_feedback.text() == "Prompt berhasil disalin."
        assert shell.prompt_preview.toPlainText() == payload
        assert not shell.visual_button.isEnabled()
    finally:
        board.setText(previous)
        shell.close()


def test_c20_i2_copy_feedback_resets_on_new_prompt_and_clear(qt_app) -> None:
    shell = _shell()
    board = qt_app.clipboard()
    previous = board.text()
    try:
        shell.prompt_preview.setPlainText("old prompt")
        shell.copy_prompt_button.click()
        assert shell.copy_prompt_feedback.text() == "Prompt berhasil disalin."
        shell.prompt_preview.setPlainText("new prompt")
        assert shell.copy_prompt_feedback.text() == ""
        assert shell.copy_prompt_button.isEnabled()
        assert board.text() == "old prompt"
        shell.prompt_preview.clear()
        assert not shell.copy_prompt_button.isEnabled()
        assert shell.copy_prompt_feedback.text() == ""
        shell._copy_existing_prompt()
        assert board.text() == "old prompt"
        assert not shell.visual_button.isEnabled()
    finally:
        board.setText(previous)
        shell.close()
