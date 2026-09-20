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
        shell.lighting_edit.setText("soft directional")
        shell.composition_edit.setText("centered")
        shell.mood_edit.setText("premium")
        shell.deliverable_edit.setText("grounded product prompt")
        brief = shell.current_brief()
        assert brief.objective == "ecommerce hero"
        assert brief.lighting_style == "soft directional"
        assert brief.composition == "centered"
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