.PHONY: dev test lint migrate seed clean setup

setup:
	uv venv .venv
	uv sync

dev:
	uv run uvicorn src.agentsphere.interfaces.api.app:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

test-unit:
	uv run pytest tests/unit -v --cov=src --cov-report=term-missing

test-integration:
	uv run pytest tests/integration -v

lint:
	uv run ruff check src/
	uv run ruff format --check src/
	uv run mypy --strict src/

lint-fix:
	uv run ruff check src/ --fix
	uv run ruff format src/

migrate:
	uv run alembic -c src/agentsphere/infrastructure/persistence/migrations/alembic.ini upgrade head

migrate-downgrade:
	uv run alembic -c src/agentsphere/infrastructure/persistence/migrations/alembic.ini downgrade -1

migrate-create:
	uv run alembic -c src/agentsphere/infrastructure/persistence/migrations/alembic.ini revision --autogenerate -m "$(name)"

seed:
	uv run python -c "from agentsphere.scripts.seed import seed; import asyncio; asyncio.run(seed())"

clean:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.egg-info

security:
	uv run bandit -r src/
	uv run pip-audit
	uv run detect-secrets scan

docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down

docker-build:
	docker compose -f docker/docker-compose.yml build
