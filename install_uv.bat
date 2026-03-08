@echo off
REM Optional: Install uv only (Windows).
REM After running once, you can use run.bat or "uv sync" and "uv run python app.py" yourself.

set "LOCAL_BIN=%USERPROFILE%\.local\bin"
set "PATH=%LOCAL_BIN%;%PATH%"

where uv >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo uv is already installed.
    uv --version
    exit /b 0
)

if exist "%LOCAL_BIN%\uv.exe" (
    echo uv is already installed at %LOCAL_BIN%\uv.exe
    "%LOCAL_BIN%\uv.exe" --version
    exit /b 0
)

echo Installing uv...
powershell -ExecutionPolicy ByPass -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex"
if %ERRORLEVEL% NEQ 0 (
    echo Install failed. Try: winget install --id=astral-sh.uv -e
    pause
    exit /b 1
)

echo Done. You can run run.bat or open a new terminal and use: uv sync ^& uv run python app.py
pause
