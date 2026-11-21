# Alibi Backend Architecture

## Architecture Style

Alibi is a feature-based modular monolith. Features share one FastAPI
application and database while keeping HTTP, business, persistence, and
external-service concerns separated.

## Application Structure

```text
app/
├── api/                    # API composition, shared dependencies, health, metrics
│   └── v1/                 # Versioned HTTP routes
├── core/                   # Settings, security, middleware, logging, errors
├── db/                     # SQLAlchemy base, sessions, database observability
├── modules/                # Product features
│   ├── users/
│   ├── cases/
│   ├── game/
│   ├── investigation/
│   ├── detective/
│   ├── scoring/
│   └── progression/
├── infrastructure/         # Redis, RabbitMQ, and outbox adapters
│   ├── cache/
│   ├── messaging/
│   └── outbox/
└── workers/                # Future background-worker entry points and handlers
```

Messaging, outbox dispatch, and worker behavior currently have scaffolding and
local service configuration only; they are not active product functionality.

## Module Boundaries

Each feature module owns its router, schemas, models, repository, service, and
feature-specific dependencies as those pieces are needed.

- **Router**: HTTP concerns, response status, and dependency injection.
- **Schema**: Pydantic request and response contracts.
- **Service**: business operations and transaction coordination.
- **Repository**: database queries and persistence operations.
- **Model**: SQLAlchemy persistence models.
- **Infrastructure**: external service adapters, not game business rules.

Keep routers thin. Do not place domain rules in routers or database queries in
services when they belong in a repository.

## Dependency Direction

```text
Router -> Service -> Repository -> PostgreSQL
                 -> Infrastructure adapters
```

Dependencies point inward. Feature modules can depend on shared `core` and
`db` primitives; infrastructure must not import feature HTTP routers.

## Database Conventions

- Use SQLAlchemy 2.x async sessions in the application.
- Keep transaction boundaries explicit.
- Manage schema changes exclusively with Alembic.
- PostgreSQL is the source of truth for durable state.
- Do not hold database transactions open during external AI or broker calls.

## Cache Conventions

Redis stores temporary, rebuildable data only. Durable game state belongs in
PostgreSQL. Every cache value needs a positive TTL. Cache keys use:

```text
alibi:<environment>:<namespace>:<identifier>
```

## API, Errors, and Logging

- Routes are versioned under `/api/v1`; health and metrics routes are top-level.
- Centralized exception handlers return a consistent error envelope.
- Structured JSON logs include request and correlation IDs.
- Never log secrets, credentials, hidden evidence, or private player dialogue.

## Testing

- Unit tests isolate business and configuration behavior.
- Integration tests use the dedicated `alibi_test` database.
- Migration tests create and drop a separate temporary database.
- E2E tests cover completed workflows once those workflows exist.
