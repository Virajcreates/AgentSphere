#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Running database migrations..."
uv run alembic -c src/agentsphere/infrastructure/persistence/migrations/alembic.ini upgrade head
echo "Migrations complete."
