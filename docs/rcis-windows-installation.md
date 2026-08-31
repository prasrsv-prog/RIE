# RCIS Windows Installation and Packaging

Phase L packages RCIS as a per-user Windows desktop application. The primary end-user entrypoint is `RCIS.exe`, installed under `%LOCALAPPDATA%\Programs\RCIS` by the Inno Setup installer. Administrator rights are not required by the approved architecture.

The installer creates Start Menu and Desktop shortcuts and registers a normal Windows uninstaller. The repository launcher `run-rcis-grounded-prompt-ui.cmd` remains a development fallback and is not the primary end-user launch path.

## Governed data boundary

The installer must not bundle, copy, migrate, rewrite, or replace the external governed intake or either SQLite repository. RCIS continues to use the Phase-H persisted foundation configuration and discovery behavior. If a usable foundation is unavailable, the Phase-K human-readable Data Source recovery flow remains the approved recovery path.

## Build boundary

The build uses PyInstaller `onedir` plus Inno Setup 6. `packaging/windows/requirements-build.txt` documents the Python build dependency. `scripts/build-rcis-windows.ps1` intentionally does not install tools or access the network. It fails closed if PyInstaller or `ISCC.exe` is missing, or if build output directories already exist.

The build script first runs the packaging contract tests, builds `dist/RCIS/RCIS.exe`, performs a non-UI bundled-runtime smoke check with `RCIS_PACKAGING_SMOKE_TEST=1`, and then compiles `dist/installer/RCIS-Setup.exe`.

Actual installation/uninstallation verification is a separate Phase-L proof boundary. Code signing and automatic network updates are outside this implementation boundary.
