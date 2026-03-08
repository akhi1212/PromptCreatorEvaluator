#!/usr/bin/env sh
# Optional: Install uv only (macOS / Linux / Ubuntu).
# After running once, you can use ./run.sh or "uv sync" and "uv run python app.py" yourself.

set -e

UV_INSTALL_URL="https://astral.sh/uv/install.sh"

if command -v uv >/dev/null 2>&1; then
    echo "uv is already installed: $(uv --version)"
    exit 0
fi

echo "Installing uv..."
if command -v curl >/dev/null 2>&1; then
    curl -LsSf "$UV_INSTALL_URL" | sh
elif command -v wget >/dev/null 2>&1; then
    wget -qO- "$UV_INSTALL_URL" | sh
else
    echo "Error: curl or wget is required."
    echo "See: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

export PATH="$HOME/.local/bin:$PATH"
echo "Done. Add to your shell profile if needed: export PATH=\"\$HOME/.local/bin:\$PATH\""
echo "Then run: ./run.sh   or   uv sync && uv run python app.py"
