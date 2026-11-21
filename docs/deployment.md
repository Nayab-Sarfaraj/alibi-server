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
- For staging and production, mount readable `DATABASE_URL` and `SECRET_KEY`
  secret files at `/run/secrets`. Set `SECRETS_DIR` in the process environment
  to use a different mount location; these files take precedence over dotenv
  and environment values.
- See `.env.example` and the configuration section of the README for local
  development defaults.
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
