.PHONY: up down logs ps migrate test lint format check

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api

ps:
	docker compose ps

migrate:
	docker compose exec api alembic upgrade head

test:
	uv run pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy app
