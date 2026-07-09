#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Starting AgentSphere development environment..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv .venv
fi

echo "Installing dependencies..."
uv sync

echo "Starting services with Docker Compose..."
docker compose -f docker/docker-compose.yml up -d

echo "Waiting for PostgreSQL to be ready..."
until docker compose -f docker/docker-compose.yml exec -T postgres pg_isready -U postgres; do
    sleep 1
done

echo "Running migrations..."
uv run alembic -c src/agentsphere/infrastructure/persistence/migrations/alembic.ini upgrade head

echo "Starting development server..."
uv run uvicorn src.agentsphere.interfaces.api.app:app --reload --host 0.0.0.0 --port 8000
