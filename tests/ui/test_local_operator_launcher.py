from __future__ import annotations

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_PATH = REPOSITORY_ROOT / "run-rcis-grounded-prompt-ui.cmd"


def _launcher_text() -> str:
    return LAUNCHER_PATH.read_text(encoding="ascii")


def test_local_operator_launcher_uses_repo_local_venv_python_and_published_ui_module() -> None:
    source = _launcher_text()
    lower = source.lower()

    assert 'cd /d "%~dp0"' in source
    assert 'if not exist ".venv\\Scripts\\python.exe"' in source
    assert '".venv\\Scripts\\python.exe" -m rie.ui.tkinter_grounded_prompt_app' in source
    assert 'set "rcis_exit_code=%errorlevel%"' in lower
    assert "exit /b %rcis_exit_code%" in lower


def test_local_operator_launcher_contains_no_hidden_operator_request_defaults() -> None:
    lower = _launcher_text().lower()
    prohibited_defaults = (
        "rcis-rsv-real-asset-pilot-01-intake", "sv300", "sv300-white-glossy",
        "dark studio", "grounded product prompt", "product_id=", "variant_id=",
        "background=", "camera_angle=", "requested_output=", "intake_root=",
    )
    for value in prohibited_defaults:
        assert value not in lower


def test_local_operator_launcher_contains_no_install_network_or_git_mutation_commands() -> None:
    lower = _launcher_text().lower()
    prohibited_commands = (
        "pip install", "python -m pip", "git add", "git commit", "git push",
        "git reset", "git clean", "curl ", "wget ", "invoke-webrequest",
        "http://", "https://", "sqlite", "winget ", "choco ", "npm install",
    )
    for value in prohibited_commands:
        assert value not in lower
