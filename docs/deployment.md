# Alibi Deployment Handoff

## Application

- FastAPI backend
- PostgreSQL database
- Redis cache
- RabbitMQ: deferred until worker implementation

## Required Environment Variables

- APP_ENV
- DATABASE_URL
- REDIS_URL
- SECRET_KEY
- TRUSTED_HOSTS
- CORS_ORIGINS

## Deployment Requirements

- HTTPS termination
- Secure secrets management
- Database migration process
- Health and readiness checks
- Logging and monitoring
- Database backups
- Rollback procedure

## Release Process

1. Run CI checks.
2. Build the backend image.
3. Apply approved database migrations.
4. Deploy the application.
5. Verify health and readiness.
6. Monitor errors and performance.
