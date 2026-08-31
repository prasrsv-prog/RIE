from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ENTRYPOINT = ROOT / "src" / "rie" / "ui" / "windows_gui_entrypoint.py"
SPEC = ROOT / "packaging" / "windows" / "rcis.spec"
ISS = ROOT / "packaging" / "windows" / "RCIS.iss"
BUILD_REQUIREMENTS = ROOT / "packaging" / "windows" / "requirements-build.txt"
BUILD_SCRIPT = ROOT / "scripts" / "build-rcis-windows.ps1"
DOC = ROOT / "docs" / "rcis-windows-installation.md"
LEGACY_LAUNCHER = ROOT / "run-rcis-grounded-prompt-ui.cmd"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_windows_entrypoint_has_exact_smoke_mode_and_tkinter_handoff() -> None:
    text = _text(ENTRYPOINT)
    assert 'RCIS_PACKAGING_SMOKE_TEST' in text
    assert 'RCIS_PACKAGING_SMOKE_MARKER_PATH' in text
    assert 'RCIS_PACKAGING_SMOKE_OK' in text
    assert 'Path(marker_path).write_text' in text
    assert 'from rie.ui.tkinter_grounded_prompt_app import main as tkinter_main' in text
    assert 'tkinter_main()' in text


def test_windows_entrypoint_does_not_embed_governed_paths_or_databases() -> None:
    text = _text(ENTRYPOINT).lower()
    assert "pilot-governed" not in text
    assert "pilot-canonical-evidence" not in text
    assert ".sqlite3" not in text
    assert "downloads" not in text


def test_pyinstaller_spec_is_onedir_windowed_rcis_bundle() -> None:
    text = _text(SPEC)
    assert 'name="RCIS"' in text
    assert "console=False" in text
    assert "exclude_binaries=True" in text
    assert "COLLECT(" in text
    assert 'RCIS_PYINSTALLER_BOOTSTRAP_PATH' in text
    assert 'pathex=[str(src_root)]' in text
    assert 'src" / "rie" / "ui" / "windows_gui_entrypoint.py' not in text


def test_pyinstaller_spec_does_not_bundle_external_governed_data() -> None:
    text = _text(SPEC).lower()
    assert "datas=[]" in text.replace(" ", "")
    assert "sqlite3" not in text
    assert "pilot-governed" not in text
    assert "pilot-canonical-evidence" not in text


def test_inno_setup_is_per_user_and_uses_approved_install_location() -> None:
    text = _text(ISS).lower()
    assert "privilegesrequired=lowest" in text
    assert r"defaultdirname={localappdata}\programs\rcis" in text
    assert "uninstallable=yes" in text


def test_inno_setup_creates_start_menu_and_desktop_shortcuts() -> None:
    text = _text(ISS).lower()
    assert r'name: "{group}\rcis"' in text
    assert r'name: "{autodesktop}\rcis"' in text
    assert r'filename: "{app}\{#myappexename}"' in text


def test_inno_setup_packages_only_built_application_bundle() -> None:
    text = _text(ISS).lower()
    assert r'source: "..\..\dist\rcis\*"' in text
    assert "sqlite3" not in text
    assert "pilot-governed" not in text
    assert "pilot-canonical-evidence" not in text


def test_build_requirement_declares_pyinstaller_without_runtime_dependency_change() -> None:
    assert _text(BUILD_REQUIREMENTS).strip() == "pyinstaller>=6,<7"


def test_build_script_never_installs_dependencies_or_uses_network() -> None:
    text = _text(BUILD_SCRIPT).lower()
    assert "pip install" not in text
    assert "invoke-webrequest" not in text
    assert "start-bitstransfer" not in text
    assert "curl " not in text
    assert "pyinstaller --version" in text


def test_build_script_is_fail_closed_and_supports_per_user_iscc() -> None:
    text = _text(BUILD_SCRIPT)
    assert "Refusing to overwrite existing build output" in text
    assert "ISCC.exe was not found" in text
    assert "PyInstaller is not available" in text
    assert "LOCALAPPDATA" in text
    assert r"Programs\Inno Setup 6\ISCC.exe" in text


def test_build_script_uses_external_bootstrap_marker_smoke_and_installer_output() -> None:
    text = _text(BUILD_SCRIPT)
    assert "RCIS_PYINSTALLER_BOOTSTRAP_PATH" in text
    assert "rcis_pyinstaller_bootstrap.py" in text
    assert "from rie.ui.windows_gui_entrypoint import main" in text
    assert "RCIS_PACKAGING_SMOKE_TEST" in text
    assert "RCIS_PACKAGING_SMOKE_MARKER_PATH" in text
    assert "Start-Process -FilePath $AppExe -Wait -PassThru" in text
    assert "RCIS_PACKAGING_SMOKE_OK" in text
    assert "RCIS.exe smoke marker missing" in text
    assert "Installer missing after build" in text


def test_documentation_and_legacy_launcher_preserve_governed_boundary() -> None:
    doc = _text(DOC).lower()
    launcher = _text(LEGACY_LAUNCHER)
    assert "must not bundle, copy, migrate, rewrite, or replace" in doc
    assert "phase-h" in doc
    assert "phase-k" in doc
    assert '.venv\\Scripts\\python.exe' in launcher
    assert "-m rie.ui.tkinter_grounded_prompt_app" in launcher
