"""Real RCIS Settings GUI tests: all offline, no provider network traffic."""
from types import SimpleNamespace

import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QLineEdit, QMessageBox

import rie.ui.pyside_product_shell as shell_module
from rie.ui.cloudflare_provider_settings import CloudflareCredentials, CredentialStoreError

ACCOUNT = "a" * 32
TOKEN = "cfut_OFFLINE_TEST_TOKEN"


@pytest.fixture(scope="module")
def qt_app():
    return QApplication.instance() or QApplication([])


def test_settings_tab_replaces_placeholder_and_masks_token(qt_app, monkeypatch):
    monkeypatch.setattr(shell_module, "load_credentials", lambda: None)
    shell = shell_module.ProductCompletionShell()
    try:
        page = shell.pages.widget(shell_module.NAVIGATION.index("Settings"))
        assert page.objectName() == "cloudflareProviderSettingsPage"
        token = shell.findChild(QLineEdit, "cloudflareTokenInput")
        assert token.echoMode() == QLineEdit.EchoMode.Password
        assert shell._visual_generation_provider is None
    finally:
        shell.close()


def test_gui_save_once_clears_input_and_reopens_without_network(qt_app, monkeypatch):
    writes = []
    monkeypatch.setattr(shell_module, "load_credentials", lambda: None)
    monkeypatch.setattr(shell_module, "save_credentials", lambda account, token: writes.append((account, token)))
    shell = shell_module.ProductCompletionShell()
    invoked = []
    try:
        shell._reopen_after_provider_settings = lambda: invoked.append("reopen")
        shell.provider_account_id_edit.setText(ACCOUNT)
        shell.provider_token_edit.setText(TOKEN)
        shell.provider_save_button.click()
        assert writes == [(ACCOUNT, TOKEN)]
        assert shell.provider_token_edit.text() == ""
        assert invoked == ["reopen"]
    finally:
        shell.close()


def test_gui_invalid_save_never_reopens_and_clears_secret(qt_app, monkeypatch):
    monkeypatch.setattr(shell_module, "load_credentials", lambda: None)
    def bad_save(account, token):
        raise ValueError("incorrect account")
    monkeypatch.setattr(shell_module, "save_credentials", bad_save)
    shell = shell_module.ProductCompletionShell()
    invoked = []
    try:
        shell._reopen_after_provider_settings = lambda: invoked.append("reopen")
        shell.provider_account_id_edit.setText("bad")
        shell.provider_token_edit.setText(TOKEN)
        shell.provider_save_button.click()
        assert not invoked
        assert shell.provider_token_edit.text() == ""
        assert TOKEN not in shell.provider_settings_status.text()
    finally:
        shell.close()


def test_provider_auto_load_from_saved_credentials_uses_exact_governed_factory(monkeypatch):
    monkeypatch.setattr(shell_module, "load_credentials", lambda: CloudflareCredentials(ACCOUNT, TOKEN))
    called = []
    sentinel = SimpleNamespace(statusBar=lambda: SimpleNamespace(showMessage=lambda _: None))
    def fake_factory(**kw):
        called.append(kw)
        return sentinel
    monkeypatch.setattr(shell_module, "build_explicit_governed_flux2_product_completion_shell", fake_factory)
    assert shell_module.build_saved_provider_product_completion_shell() is sentinel
    assert len(called) == 1
    assert called[0]["account_id"] == ACCOUNT
    assert called[0]["api_token"] == TOKEN
    assert called[0]["requested_use_scope"] == "rcis-ffs21-cloudflare-flux2-visual-generation"
    assert called[0]["governed_snapshot_path"].name == "RCIS-C20-FFS21-Gate15-rights-snapshot-v1.json"
    assert callable(called[0]["http_post"])


def test_missing_or_corrupt_secret_falls_back_local_without_provider(qt_app, monkeypatch):
    sentinel = object()
    monkeypatch.setattr(shell_module, "build_normal_product_completion_shell", lambda: sentinel)
    monkeypatch.setattr(shell_module, "load_credentials", lambda: None)
    assert shell_module.build_saved_provider_product_completion_shell() is sentinel
    def damaged():
        raise CredentialStoreError("unable")
    monkeypatch.setattr(shell_module, "load_credentials", damaged)
    assert shell_module.build_saved_provider_product_completion_shell() is sentinel


def test_missing_gate15_snapshot_falls_back_local_no_http(qt_app, monkeypatch):
    sentinel = SimpleNamespace(statusBar=lambda: SimpleNamespace(showMessage=lambda _: None))
    monkeypatch.setattr(shell_module, "build_normal_product_completion_shell", lambda: sentinel)
    monkeypatch.setattr(shell_module, "load_credentials", lambda: CloudflareCredentials(ACCOUNT, TOKEN))
    def fail_governance(**_kw):
        raise RuntimeError("no rights")
    monkeypatch.setattr(shell_module, "build_explicit_governed_flux2_product_completion_shell", fail_governance)
    assert shell_module.build_saved_provider_product_completion_shell() is sentinel


def test_saved_token_never_displayed_and_delete_requires_confirmation(qt_app, monkeypatch):
    monkeypatch.setattr(shell_module, "load_credentials", lambda: CloudflareCredentials(ACCOUNT, TOKEN))
    deleted = []
    monkeypatch.setattr(shell_module, "delete_credentials", lambda: deleted.append(True))
    shell = shell_module.ProductCompletionShell()
    try:
        assert shell.provider_account_id_edit.text() == ACCOUNT
        assert shell.provider_token_edit.text() == ""
        assert TOKEN not in shell.provider_settings_status.text()
        monkeypatch.setattr(shell_module, "QMessageBox", SimpleNamespace(
            StandardButton=QMessageBox.StandardButton,
            question=lambda *args, **kwargs: QMessageBox.StandardButton.No,
        ))
        shell.provider_delete_button.click()
        assert deleted == []
        monkeypatch.setattr(shell_module, "QMessageBox", SimpleNamespace(
            StandardButton=QMessageBox.StandardButton,
            question=lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
        ))
        shell.provider_delete_button.click()
        assert deleted == [True]
    finally:
        shell.close()
