from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from rie.application.visual_generation_provider import (
    VisualGenerationRequest,
    VisualGenerationResult,
)
from rie.ui.pyside_product_shell import ProductCompletionShell


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app


class _FakeVisualGenerationProvider:
    def __init__(
        self,
        *,
        result: VisualGenerationResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self.calls: list[VisualGenerationRequest] = []
        self._result = result or VisualGenerationResult(
            provider_output_refs=("provider-output-1",),
            message="Visual request accepted.",
        )
        self._error = error

    def generate(
        self,
        request: VisualGenerationRequest,
    ) -> VisualGenerationResult:
        self.calls.append(request)
        if self._error is not None:
            raise self._error
        return self._result


def test_pc5_provider_absent_keeps_generate_visuals_disabled(qt_app) -> None:
    shell = ProductCompletionShell()
    try:
        assert shell.visual_button.isEnabled() is False
        assert "No provider is connected" in shell.visual_button.toolTip()
    finally:
        shell.close()


def test_pc5_invalid_provider_contract_is_rejected(qt_app) -> None:
    with pytest.raises(TypeError, match="must expose generate"):
        ProductCompletionShell(visual_generation_provider=object())


def test_pc5_injected_provider_enables_generate_visuals(qt_app) -> None:
    provider = _FakeVisualGenerationProvider()
    shell = ProductCompletionShell(visual_generation_provider=provider)
    try:
        assert shell.visual_button.isEnabled() is True
    finally:
        shell.close()


def test_pc5_generate_visuals_fails_closed_without_grounded_prompt(qt_app) -> None:
    provider = _FakeVisualGenerationProvider()
    shell = ProductCompletionShell(visual_generation_provider=provider)
    try:
        shell.visual_button.click()

        assert provider.calls == []
        assert (
            shell.create_feedback.text()
            == "Build a grounded prompt before generating visuals."
        )
    finally:
        shell.close()


def test_pc5_generate_visuals_forwards_exact_prompt_and_selected_reference_ids(
    qt_app,
) -> None:
    provider = _FakeVisualGenerationProvider(
        result=VisualGenerationResult(
            provider_output_refs=("provider-output-a",),
            message="Fake provider completed.",
        )
    )
    shell = ProductCompletionShell(visual_generation_provider=provider)
    try:
        shell.prompt_preview.setPlainText("Grounded prompt ready.")
        shell._selected_create_reference_asset_ids = lambda: (
            "asset-reference-a",
            "asset-reference-b",
        )

        shell.visual_button.click()

        assert provider.calls == [
            VisualGenerationRequest(
                grounded_prompt="Grounded prompt ready.",
                selected_reference_asset_ids=(
                    "asset-reference-a",
                    "asset-reference-b",
                ),
            )
        ]
        assert shell.create_feedback.text() == "Fake provider completed."
    finally:
        shell.close()


def test_pc5_provider_failure_is_rendered_without_retry(qt_app) -> None:
    provider = _FakeVisualGenerationProvider(error=RuntimeError("provider failed"))
    shell = ProductCompletionShell(visual_generation_provider=provider)
    try:
        shell.prompt_preview.setPlainText("Grounded prompt ready.")

        shell.visual_button.click()

        assert len(provider.calls) == 1
        assert shell.create_feedback.text() == (
            "Could not generate visuals: provider failed"
        )
    finally:
        shell.close()
