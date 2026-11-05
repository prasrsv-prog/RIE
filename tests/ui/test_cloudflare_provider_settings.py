"""Offline tests for Windows user-scoped provider credential persistence.

Tests substitute DPAPI with a reversible fake; they never store a real token.
"""
from pathlib import Path

import pytest

from rie.ui import cloudflare_provider_settings as settings

ACCOUNT = "a" * 32
TOKEN = "cfut_OFFLINE_ONLY_NOT_REAL_SECRET"


def fake_crypto(monkeypatch):
    monkeypatch.setattr(settings, "_protect", lambda data: b"DPAPI_FAKE:" + data[::-1])
    def decrypt(blob):
        if not blob.startswith(b"DPAPI_FAKE:"):
            raise settings.CredentialStoreError("invalid ciphertext")
        return blob[len(b"DPAPI_FAKE:"):][::-1]
    monkeypatch.setattr(settings, "_unprotect", decrypt)


def test_save_load_and_update_only_encrypted_bytes(tmp_path, monkeypatch):
    fake_crypto(monkeypatch)
    target = tmp_path / "rcis-secrets"
    assert settings.load_credentials(root=target) is None
    settings.save_credentials(ACCOUNT.upper(), TOKEN, root=target)
    blob = (target / "cloudflare-workers-ai.dpapi").read_bytes()
    assert b"cfut_" not in blob and b'"api_token"' not in blob
    loaded = settings.load_credentials(root=target)
    assert loaded.account_id == ACCOUNT and loaded.api_token == TOKEN
    settings.save_credentials(ACCOUNT, "cfut_REPLACED_FAKE", root=target)
    assert settings.load_credentials(root=target).api_token == "cfut_REPLACED_FAKE"
    assert list(target.glob("*.tmp")) == []


def test_corrupt_ciphertext_fails_closed(tmp_path, monkeypatch):
    fake_crypto(monkeypatch)
    path = tmp_path / "secrets"
    path.mkdir()
    (path / "cloudflare-workers-ai.dpapi").write_bytes(b"garbage")
    with pytest.raises(settings.CredentialStoreError):
        settings.load_credentials(root=path)


def test_invalid_account_or_token_never_writes(tmp_path, monkeypatch):
    fake_crypto(monkeypatch)
    target = tmp_path / "rcis"
    for bad_account, bad_token in (("not-an-id", TOKEN), (ACCOUNT, ""),
                                   (ACCOUNT, "token\nmalformed"), (ACCOUNT, " token")):
        with pytest.raises(ValueError):
            settings.save_credentials(bad_account, bad_token, root=target)
    assert not target.exists()


def test_symlink_target_rejected(tmp_path, monkeypatch):
    fake_crypto(monkeypatch)
    folder = tmp_path / "folder"
    folder.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(folder, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable on this Windows account")
    with pytest.raises(settings.CredentialStoreError):
        settings.save_credentials(ACCOUNT, TOKEN, root=link)


def test_delete_only_managed_secret(tmp_path, monkeypatch):
    fake_crypto(monkeypatch)
    folder = tmp_path / "rcis"
    settings.save_credentials(ACCOUNT, TOKEN, root=folder)
    adjacent = folder / "other-settings.json"
    adjacent.write_text('keep', encoding="utf-8")
    settings.delete_credentials(root=folder)
    assert settings.load_credentials(root=folder) is None
    assert adjacent.read_text(encoding="utf-8") == 'keep'


def test_no_windows_dpapi_fail_closed_on_nonwindows():
    if settings.os.name == "nt":
        pytest.skip("tested with DPAPI on Windows only")
    with pytest.raises(settings.CredentialStoreError):
        settings._protect(b"test")

@pytest.mark.skipif(settings.os.name != "nt", reason="real Windows DPAPI only")
def test_real_windows_dpapi_roundtrip_with_fake_token(tmp_path):
    """Office regression proves the actual OS credential API, not just a mock."""
    folder = tmp_path / "real-windows-credential"
    settings.save_credentials(ACCOUNT, TOKEN, root=folder)
    raw = (folder / "cloudflare-workers-ai.dpapi").read_bytes()
    assert TOKEN.encode("ascii") not in raw
    assert settings.load_credentials(root=folder).api_token == TOKEN
    settings.delete_credentials(root=folder)
    assert settings.load_credentials(root=folder) is None
