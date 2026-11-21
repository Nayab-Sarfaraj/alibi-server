# Configuration Guide

Alibi uses Pydantic Settings. `.env` is for local development and is not
committed; `.env.example` is the safe, committed reference.

## Configuration Sources

- `.env.example`: documented local template with no real secrets.
- `.env`: local values, ignored by Git.
- CI: injected environment variables.
- Staging and production: injected environment variables and secret files.

In staging and production, `DATABASE_URL` and `SECRET_KEY` are required from
the configured secrets directory (default: `/run/secrets`).

## Application Settings

| Variable | Purpose |
| --- | --- |
| `PROJECT_NAME` | Application name |
| `VERSION` | Application version |
| `APP_ENV` | `development`, `testing`, `staging`, or `production` |
| `APP_HOST` | Server bind address |
| `APP_PORT` | Server port |
| `APP_DEBUG` | Enable FastAPI debug behavior |
| `LOG_LEVEL` | Application log level |

## Database Settings

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL SQLAlchemy URL for the application |
| `TEST_DATABASE_URL` | Dedicated `alibi_test` URL used only by pytest |
| `DB_POOL_SIZE` | Persistent connections per process |
| `DB_MAX_OVERFLOW` | Additional temporary connections |
| `DB_POOL_TIMEOUT` | Connection-acquisition timeout in seconds |
| `DB_POOL_RECYCLE` | Connection recycle interval in seconds |
| `SQL_ECHO` | SQLAlchemy SQL logging flag |

`TEST_DATABASE_URL` must end in `/alibi_test`. The test fixture refuses other
database names, protecting local development and production databases.

## Redis Settings

| Variable | Purpose |
| --- | --- |
| `REDIS_URL` | Redis connection URL |
| `REDIS_MAX_CONNECTIONS` | Maximum Redis pool connections |
| `REDIS_SOCKET_TIMEOUT` | Redis operation timeout in seconds |

## RabbitMQ Settings

| Variable | Purpose |
| --- | --- |
| `RABBITMQ_URL` | RabbitMQ connection URL |
| `RABBITMQ_PREFETCH` | Consumer prefetch limit for future workers |
| `RABBITMQ_MAX_RETRIES` | Future worker retry limit |
| `RABBITMQ_PASSWORD` | Docker Compose local broker password; not a Pydantic app setting |

The RabbitMQ settings and Compose service support local development. Durable
outbox publishing and worker consumption are deferred.

## HTTP and Security Settings

| Variable | Purpose |
| --- | --- |
| `CORS_ORIGINS` | JSON list of allowed browser origins |
| `TRUSTED_HOSTS` | JSON list of accepted HTTP hostnames |
| `MAX_REQUEST_BODY_BYTES` | Maximum request body size in bytes |
| `SECRET_KEY` | Future authentication/signing secret |
| `SECRETS_DIR` | Directory holding staging/production secret files |

## Docker Compose Variables

`POSTGRES_PASSWORD` and `RABBITMQ_PASSWORD` are required by Docker Compose.
The API container uses service hostnames (`postgres`, `redis`, and `rabbitmq`),
while host-run Python uses the published localhost ports.

## Security Rules

- Never commit `.env` or a real secret.
- Do not use local credentials outside local development.
- Keep `APP_DEBUG=false` outside development.
- Use a long, non-placeholder `SECRET_KEY` in staging and production.
- Secret-bearing settings are redacted from diagnostics and must not be logged.
- Rotate any credential that is accidentally committed.
