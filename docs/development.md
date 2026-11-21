# Development Guide

Run all commands from `backend/`.

## Starting and Inspecting Services

```bash
make up
make ps
make logs
make down
```

`make up` starts PostgreSQL, Redis, RabbitMQ, and the API. If you change a
dependency, rebuild with `make up` again.

## Database Migrations

Apply migrations in the API container:

```bash
make migrate
```

Create a migration after changing SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Review every generated migration before applying it. Check migration state with:

```bash
uv run alembic current
uv run alembic check
```

## Testing

Create `alibi_test` once in the local PostgreSQL container and set
`TEST_DATABASE_URL` as described in the README. Then run:

```bash
make test
uv run pytest --cov=app --cov-report=term-missing
```

Integration tests use `alibi_test`; migration tests create their own disposable
database. Never point either URL at a development or production database.

## Code Quality

```bash
make lint
make format
make check
uv run pre-commit run --all-files
```

`make format` writes formatting changes. `make check` only verifies linting,
formatting, and types.

## Adding Dependencies

Add a production dependency:

```bash
uv add package-name
```

Add a development dependency:

```bash
uv add --dev package-name
```

Commit both `pyproject.toml` and `uv.lock` after dependency changes.

## Development Rules

1. Keep routers thin.
2. Put business logic in services.
3. Put persistence queries in repositories.
4. Use explicit transaction boundaries.
5. Add tests with new behavior.
6. Do not log credentials or private player data.
7. Run `make check` and the relevant tests before committing.
