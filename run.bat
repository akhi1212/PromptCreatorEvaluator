@echo off
setlocal EnableDelayedExpansion
REM PromptAnalyzer — Run script for Windows
REM First time: installs uv if missing, then syncs deps and runs the app.
REM Next times: syncs (if needed) and runs the app. Uses .venv automatically via uv.

set "VENV_DIR=.venv"
set "APP_SCRIPT=app.py"
set "LOCAL_BIN=%USERPROFILE%\.local\bin"
set "PATH=%LOCAL_BIN%;%PATH%"

REM Ensure we're in the project root (directory containing pyproject.toml)
cd /d "%~dp0"
if not exist "pyproject.toml" (
    echo Error: pyproject.toml not found. Run this script from the PromptAnalyzer project root.
    exit /b 1
)

REM Check for uv (in PATH or in .local\bin)
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "%LOCAL_BIN%\uv.exe" (
        set "UV_CMD=%LOCAL_BIN%\uv.exe"
    ) else (
        echo uv not found. Installing uv...
        powershell -ExecutionPolicy ByPass -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex"
        if !ERRORLEVEL! NEQ 0 (
            echo uv install failed. Install manually: https://docs.astral.sh/uv/getting-started/installation/
            echo Or: winget install --id=astral-sh.uv -e
            pause
            exit /b 1
        )
        set "PATH=%LOCAL_BIN%;%PATH%"
        set "UV_CMD=%LOCAL_BIN%\uv.exe"
        if not exist "!UV_CMD!" (
            echo uv was installed. Close this window, open a new Command Prompt or PowerShell, and run run.bat again.
            pause
            exit /b 1
        )
    )
) else (
    set "UV_CMD=uv"
)

REM Sync dependencies (creates/updates .venv)
echo Syncing dependencies (uv sync)...
if "%UV_CMD%"=="uv" (
    uv sync
) else (
    "%UV_CMD%" sync
)
if %ERRORLEVEL% NEQ 0 (
    echo uv sync failed.
    pause
    exit /b 1
)

REM Run the app (uv run uses .venv automatically)
echo Starting PromptAnalyzer...
if "%UV_CMD%"=="uv" (
    uv run python "%APP_SCRIPT%" %*
) else (
    "%UV_CMD%" run python "%APP_SCRIPT%" %*
)

endlocal
