#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running tests with coverage..."
uv run pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=80
