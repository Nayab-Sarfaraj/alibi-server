# Alibi Server

Backend for Alibi, an AI-powered interrogation game featuring intelligent
detectives, persistent memory, evidence-based investigations, and dynamic
verdicts.

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL and SQLAlchemy 2.x
- Alembic
- Redis
- RabbitMQ (local broker configuration; worker processing is not implemented yet)
- Pydantic Settings
- Docker Compose and uv
- pytest, Ruff, and mypy

## Prerequisites

- Docker Desktop with Docker Compose
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Git

## Quick Start

From the `backend/` directory:

1. Create local configuration and install dependencies.

   ```bash
   cp .env.example .env
   uv sync
   ```

   Set secure local values for `POSTGRES_PASSWORD`, `RABBITMQ_PASSWORD`, and
   `SECRET_KEY` in `.env`. The example file documents every supported setting.

2. Start local services and the API.

   ```bash
   make up
   ```

3. Apply migrations.

   ```bash
   make migrate
   ```

4. Verify the API.

   ```bash
   curl http://localhost:8000/health/live
   curl http://localhost:8000/health/ready
   ```

The API runs at http://localhost:8000. Swagger UI is available at
http://localhost:8000/docs outside production.

## Local Services

| Service | Host address | Purpose |
| --- | --- | --- |
| API | `http://localhost:8000` | FastAPI application |
| PostgreSQL | `localhost:5433` | Durable application data |
| Redis | `localhost:6379` | Temporary cache |
| RabbitMQ | `localhost:5672` | Local broker configuration |
| RabbitMQ Management | http://localhost:15672 | Local broker UI |

RabbitMQ uses the `alibi` user and the local `RABBITMQ_PASSWORD`. Messaging,
outbox dispatch, and background worker behavior are not implemented yet.

## Development Commands

```bash
make up       # build and start services
make down     # stop services
make logs     # follow API logs
make ps       # show service status
make migrate  # apply Alembic migrations in the API container
make test     # run tests from the host environment
make lint     # run Ruff linting
make format   # format code with Ruff
make check    # lint, format-check, and type-check
```

## Testing

Tests use a dedicated PostgreSQL database named `alibi_test`; they do not use
the development database. Create it once after PostgreSQL starts:

```bash
docker compose exec postgres \
  psql -U alibi -d postgres -c "CREATE DATABASE alibi_test;"
```

Set `TEST_DATABASE_URL` in `.env` to that database. Then run:

```bash
make test
uv run pytest --cov=app --cov-report=term-missing
```

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [Development guide](docs/development.md)
- [Deployment handoff](docs/deployment.md)

## Status

Phase 3 backend foundation is in progress. Authentication, case management,
game logic, AI interrogation, transactional outbox dispatch, and background
worker processing are implemented in later phases.
