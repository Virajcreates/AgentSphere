#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Seeding demo data..."
uv run python -c "
import asyncio
from agentsphere.scripts.seed import seed
asyncio.run(seed())
"
echo "Seed complete."
