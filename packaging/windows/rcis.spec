import os
from pathlib import Path

project_root = Path(SPECPATH).resolve().parents[1]
src_root = project_root / "src"
bootstrap_value = os.environ.get("RCIS_PYINSTALLER_BOOTSTRAP_PATH", "").strip()
if not bootstrap_value:
    raise RuntimeError("RCIS_PYINSTALLER_BOOTSTRAP_PATH is required for RCIS packaging")
entrypoint = Path(bootstrap_value).resolve()
if not entrypoint.is_file():
    raise RuntimeError(f"RCIS PyInstaller bootstrap missing: {entrypoint}")

a = Analysis(
    [str(entrypoint)],
    pathex=[str(src_root)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RCIS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="RCIS",
)
