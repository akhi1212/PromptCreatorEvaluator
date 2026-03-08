#!/usr/bin/env sh
# PromptAnalyzer — Run script for macOS and Linux (Ubuntu, etc.)
# First time: installs uv if missing, then syncs deps and runs the app.
# Next times: syncs (if needed) and runs the app. Uses .venv automatically via uv.

set -e

UV_INSTALL_URL="https://astral.sh/uv/install.sh"
VENV_DIR=".venv"
APP_SCRIPT="app.py"

# Try to run uv (from PATH or common locations)
run_uv() {
    if command -v uv >/dev/null 2>&1; then
        uv "$@"
        return
    fi
    if [ -x "$HOME/.local/bin/uv" ]; then
        "$HOME/.local/bin/uv" "$@"
        return
    fi
    return 1
}

# Install uv if not found
install_uv() {
    echo "uv not found. Installing uv..."
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf "$UV_INSTALL_URL" | sh
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- "$UV_INSTALL_URL" | sh
    else
        echo "Error: curl or wget is required to install uv."
        echo "Install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
    # Installer adds to ~/.local/bin; ensure it's in PATH for this script
    export PATH="$HOME/.local/bin:$PATH"
}

# Ensure we're in the project root (directory containing pyproject.toml)
cd "$(dirname "$0")"
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Run this script from the PromptAnalyzer project root."
    exit 1
fi

# Install uv if needed
if ! run_uv --version >/dev/null 2>&1; then
    install_uv
    if ! run_uv --version >/dev/null 2>&1; then
        echo "uv was installed. If you still see this, open a new terminal or run:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo "  ./run.sh"
        exit 1
    fi
fi

# Sync dependencies (creates/updates .venv)
echo "Syncing dependencies (uv sync)..."
run_uv sync

# Run the app (uv run uses .venv automatically)
echo "Starting PromptAnalyzer..."
exec run_uv run python "$APP_SCRIPT" "$@"
