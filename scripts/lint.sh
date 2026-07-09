#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running ruff..."
uv run ruff check src/

echo "Running mypy..."
uv run mypy --strict src/

echo "Running bandit..."
uv run bandit -r src/
