from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QScrollArea, QSplitter

from rie.ui.product_completion_models import (
    ProductConstraint,
    ProductContextSnapshot,
    ProductFact,
    ProductUnknown,
)
from rie.ui.pyside_product_shell import (
    GroundedPromptCompatibilityAdapter,
    NAVIGATION,
    ProductCompletionShell,
    WINDOW_TITLE,
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
        assert [shell.navigation.item(i).text() for i in range(shell.navigation.count())] == list(NAVIGATION)
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
        assert "not connected" in shell.visual_button.toolTip().lower()
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
        assert "Product Intelligence is unavailable" in shell.products_status.text()
        assert "No storage fallback" in shell.products_status.text()
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

