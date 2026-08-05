# Courtroom Server

A production-ready FastAPI service scaffold for courtroom-related applications.

## Features

- FastAPI application layout with versioned API routing
- Environment-based configuration using `python-dotenv`
- SQLAlchemy database session and model structure
- Docker and Docker Compose setup for local development
- Pytest-based tests and developer tooling support

## Requirements

- Python 3.11+
- Docker (optional for containerized deployment)

## Local development

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment variables:

   ```bash
   copy .env.example .env
   ```

4. Start the app:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

5. Open documentation:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

## Docker

Build and run with Docker:

```bash
docker compose up --build
```

## Tests

Run the suite with:

```bash
pytest
```
