"""One-time Windows user-bound Cloudflare credentials for RCIS Creative Studio.

Only DPAPI ciphertext is persisted under the current user's LOCALAPPDATA.
This module never calls Cloudflare, reads photos, or changes rights records.
"""
from __future__ import annotations

from dataclasses import dataclass
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import re
import secrets


class CredentialStoreError(RuntimeError):
    """An unavailable, unreadable, or corrupt local credential store."""


@dataclass(frozen=True)
class CloudflareCredentials:
    account_id: str
    api_token: str


_FILENAME = "cloudflare-workers-ai.dpapi"
_MAX_BLOB_BYTES = 16384


def _storage_path(root: Path | None = None) -> Path:
    if root is None:
        local = os.environ.get("LOCALAPPDATA", "").strip()
        if not local:
            raise CredentialStoreError("LOCALAPPDATA is unavailable")
        root = Path(local) / "RCIS"
    if not root.is_absolute():
        raise CredentialStoreError("credential directory must be absolute")
    if root.is_symlink():
        raise CredentialStoreError("credential directory cannot be a symlink")
    return root / _FILENAME


def _valid_credentials(account_id: str, api_token: str) -> CloudflareCredentials:
    if not isinstance(account_id, str) or re.fullmatch(r"[A-Fa-f0-9]{32}", account_id.strip()) is None:
        raise ValueError("Cloudflare Account ID must contain exactly 32 hex characters")
    if (not isinstance(api_token, str) or not api_token or api_token != api_token.strip()
            or len(api_token) > 4096 or any(ord(char) < 33 or ord(char) > 126 for char in api_token)):
        raise ValueError("Cloudflare API token is empty or has invalid characters")
    return CloudflareCredentials(account_id.strip().lower(), api_token)


def _windows_crypt(blob: bytes, *, decrypt: bool) -> bytes:
    if os.name != "nt":
        raise CredentialStoreError("Windows DPAPI is required for credential storage")

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

    source = ctypes.create_string_buffer(blob)
    incoming = DATA_BLOB(len(blob), ctypes.cast(source, ctypes.POINTER(ctypes.c_byte)))
    outgoing = DATA_BLOB()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    # CRYPTPROTECT_UI_FORBIDDEN. DPAPI binds ciphertext to current Windows user.
    if decrypt:
        method = crypt32.CryptUnprotectData
        method.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.c_void_p,
                           ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                           wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
        args = (ctypes.byref(incoming), None, None, None, None, 1,
                ctypes.byref(outgoing))
    else:
        method = crypt32.CryptProtectData
        method.argtypes = [ctypes.POINTER(DATA_BLOB), wintypes.LPCWSTR,
                           ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                           wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
        args = (ctypes.byref(incoming), "RCIS Cloudflare Workers AI", None,
                None, None, 1, ctypes.byref(outgoing))
    method.restype = wintypes.BOOL
    if not method(*args):
        raise CredentialStoreError("Windows DPAPI could not process the credential")
    try:
        return ctypes.string_at(outgoing.pbData, outgoing.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(outgoing.pbData, ctypes.c_void_p))


def _protect(data: bytes) -> bytes:
    return _windows_crypt(data, decrypt=False)


def _unprotect(data: bytes) -> bytes:
    return _windows_crypt(data, decrypt=True)


def save_credentials(account_id: str, api_token: str, *, root: Path | None = None) -> None:
    """Replace only this user's encrypted credential; never persist plaintext."""
    details = _valid_credentials(account_id, api_token)
    path = _storage_path(root)
    if path.is_symlink():
        raise CredentialStoreError("credential file cannot be a symlink")
    plaintext = json.dumps({"version": 1, "account_id": details.account_id,
                            "api_token": details.api_token}, separators=(",", ":")).encode("utf-8")
    ciphertext = _protect(plaintext)
    if not ciphertext or len(ciphertext) > _MAX_BLOB_BYTES:
        raise CredentialStoreError("encrypted credential size is invalid")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.parent.is_symlink() or path.is_symlink():
            raise CredentialStoreError("credential path changed unexpectedly")
        temp = path.with_name(path.name + "." + secrets.token_hex(8) + ".tmp")
        try:
            fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
            with os.fdopen(fd, "wb") as handle:
                handle.write(ciphertext)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, path)
        finally:
            if temp.exists():
                temp.unlink()
    except OSError as exc:
        raise CredentialStoreError("could not safely save encrypted credentials") from exc


def load_credentials(*, root: Path | None = None) -> CloudflareCredentials | None:
    """Return saved credentials for normal GUI startup; corrupted data fails closed."""
    path = _storage_path(root)
    if path.is_symlink():
        raise CredentialStoreError("credential file cannot be a symlink")
    try:
        if not path.exists():
            return None
        if not path.is_file() or path.stat().st_size > _MAX_BLOB_BYTES:
            raise CredentialStoreError("encrypted credential has an invalid size")
        ciphertext = path.read_bytes()
        if not ciphertext:
            raise CredentialStoreError("encrypted credential is empty")
        payload = json.loads(_unprotect(ciphertext).decode("utf-8"))
        if not isinstance(payload, dict) or payload.get("version") != 1:
            raise CredentialStoreError("credential format is unsupported")
        return _valid_credentials(payload.get("account_id"), payload.get("api_token"))
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise CredentialStoreError("encrypted credential cannot be read or validated") from exc


def delete_credentials(*, root: Path | None = None) -> None:
    path = _storage_path(root)
    if path.is_symlink():
        raise CredentialStoreError("credential file cannot be a symlink")
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        raise CredentialStoreError("encrypted credential cannot be removed") from exc
