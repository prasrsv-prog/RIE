from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "tools"
    / "governance"
    / "RCIS-GovernanceHelpers.psm1"
)
POWERSHELL = shutil.which("powershell.exe") or shutil.which("powershell")

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="RCIS governance PowerShell helpers require Windows PowerShell.",
)


def _ps_quote(value: str | Path) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _run_powershell(script: str) -> subprocess.CompletedProcess[str]:
    assert POWERSHELL is not None
    completed = subprocess.run(
        [
            POWERSHELL,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, (
        completed.returncode,
        completed.stdout,
        completed.stderr,
    )
    return completed


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, (
        completed.returncode,
        completed.stdout,
        completed.stderr,
    )
    return completed.stdout.strip()


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True)
    _git(repo, "init")
    _git(repo, "config", "user.email", "rcis-governance-test@example.invalid")
    _git(repo, "config", "user.name", "RCIS Governance Test")


def _import_prefix() -> str:
    return (
        f"Import-Module {_ps_quote(MODULE_PATH)} -Force -ErrorAction Stop; "
        "$ErrorActionPreference = 'Stop'; "
    )


def test_exports_exact_minimum_helper_surface() -> None:
    completed = _run_powershell(
        _import_prefix()
        + "(Get-Module RCIS-GovernanceHelpers).ExportedFunctions.Keys "
        "| Sort-Object | ConvertTo-Json -Compress"
    )
    observed = json.loads(completed.stdout)
    assert observed == [
        "Export-RcisGitBlobExact",
        "Get-RcisFileIdentity",
        "Get-RcisGitOneLine",
        "Test-RcisIndexMatchesWorktree",
        "Test-RcisTrackedWorktreeAndIndexClean",
    ]


def test_get_rcis_file_identity_reports_raw_bytes_and_sha256(tmp_path: Path) -> None:
    payload = b"\x00RCIS\r\nraw\xffbytes\n"
    source = tmp_path / "identity payload.bin"
    source.write_bytes(payload)

    completed = _run_powershell(
        _import_prefix()
        + f"Get-RcisFileIdentity -LiteralPath {_ps_quote(source)} "
        "| ConvertTo-Json -Compress"
    )
    observed = json.loads(completed.stdout)

    assert observed["Bytes"] == len(payload)
    assert observed["SHA256"] == hashlib.sha256(payload).hexdigest()


def test_get_rcis_git_one_line_handles_repository_path_with_spaces(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo with spaces"
    _init_repo(repo)
    tracked = repo / "tracked.txt"
    tracked.write_text("alpha\n", encoding="utf-8", newline="\n")
    _git(repo, "add", "--", "tracked.txt")
    _git(repo, "commit", "-m", "base")
    expected = _git(repo, "rev-parse", "HEAD")

    completed = _run_powershell(
        _import_prefix()
        + f"Get-RcisGitOneLine -RepositoryRoot {_ps_quote(repo)} "
        "-GitArguments @('rev-parse','HEAD')"
    )

    assert completed.stdout.strip() == expected


def test_export_rcis_git_blob_exact_preserves_binary_bytes(tmp_path: Path) -> None:
    repo = tmp_path / "binary repo with spaces"
    _init_repo(repo)
    payload = bytes(range(256)) + b"\x00\r\nRCIS\xff\n"
    source = repo / "payload.bin"
    source.write_bytes(payload)
    _git(repo, "add", "--", "payload.bin")
    _git(repo, "commit", "-m", "binary")
    blob_oid = _git(repo, "rev-parse", "HEAD:payload.bin")

    destination = tmp_path / "exported payload.bin"
    completed = _run_powershell(
        _import_prefix()
        + f"Export-RcisGitBlobExact -RepositoryRoot {_ps_quote(repo)} "
        + f"-ObjectId {_ps_quote(blob_oid)} "
        + f"-DestinationPath {_ps_quote(destination)} "
        "| ConvertTo-Json -Compress"
    )
    observed = json.loads(completed.stdout)

    assert destination.read_bytes() == payload
    assert observed["Bytes"] == len(payload)
    assert observed["SHA256"] == hashlib.sha256(payload).hexdigest()


def test_cleanliness_and_index_worktree_checks_are_distinct(tmp_path: Path) -> None:
    repo = tmp_path / "state repo with spaces"
    _init_repo(repo)
    tracked = repo / "tracked.txt"
    tracked.write_text("base\n", encoding="utf-8", newline="\n")
    _git(repo, "add", "--", "tracked.txt")
    _git(repo, "commit", "-m", "base")

    clean = _run_powershell(
        _import_prefix()
        + f"$r={_ps_quote(repo)}; "
        "[pscustomobject]@{"
        "TrackedClean=(Test-RcisTrackedWorktreeAndIndexClean -RepositoryRoot $r);"
        "IndexMatchesWorktree=(Test-RcisIndexMatchesWorktree -RepositoryRoot $r)"
        "} | ConvertTo-Json -Compress"
    )
    clean_state = json.loads(clean.stdout)
    assert clean_state == {
        "TrackedClean": True,
        "IndexMatchesWorktree": True,
    }

    tracked.write_text("modified\n", encoding="utf-8", newline="\n")
    unstaged = _run_powershell(
        _import_prefix()
        + f"$r={_ps_quote(repo)}; "
        "[pscustomobject]@{"
        "TrackedClean=(Test-RcisTrackedWorktreeAndIndexClean -RepositoryRoot $r);"
        "IndexMatchesWorktree=(Test-RcisIndexMatchesWorktree -RepositoryRoot $r)"
        "} | ConvertTo-Json -Compress"
    )
    unstaged_state = json.loads(unstaged.stdout)
    assert unstaged_state == {
        "TrackedClean": False,
        "IndexMatchesWorktree": False,
    }

    _git(repo, "add", "--", "tracked.txt")
    staged = _run_powershell(
        _import_prefix()
        + f"$r={_ps_quote(repo)}; "
        "[pscustomobject]@{"
        "TrackedClean=(Test-RcisTrackedWorktreeAndIndexClean -RepositoryRoot $r);"
        "IndexMatchesWorktree=(Test-RcisIndexMatchesWorktree -RepositoryRoot $r)"
        "} | ConvertTo-Json -Compress"
    )
    staged_state = json.loads(staged.stdout)

    # Regression guard for the PR-119F-C3 verification defect:
    # staged changes make the tracked state differ from HEAD, while the
    # worktree still exactly matches the staged index.
    assert staged_state == {
        "TrackedClean": False,
        "IndexMatchesWorktree": True,
    }


def test_module_excludes_frozen_governance_hazard_patterns() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8")

    assert ".ArgumentList" not in text
    assert "--untracked-files=all" not in text
    assert ".pytest_cache" not in text
    assert "git archive" not in text.lower()
    assert re.search(r"(?i)\$Args\b", text) is None
    assert (
        re.search(
            r"\$(?!(?:env|global|script|local|private):)"
            r"[A-Za-z_][A-Za-z0-9_]*:",
            text,
        )
        is None
    )
