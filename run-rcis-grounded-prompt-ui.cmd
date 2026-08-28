@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: repository-local Python not found: .venv\Scripts\python.exe 1>&2
    exit /b 1
)
".venv\Scripts\python.exe" -m rie.ui.tkinter_grounded_prompt_app
set "RCIS_EXIT_CODE=%ERRORLEVEL%"
exit /b %RCIS_EXIT_CODE%
