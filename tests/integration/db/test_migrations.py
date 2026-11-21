"""Integration tests for Alembic migrations against a disposable database."""

import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from psycopg import connect, sql
from sqlalchemy.engine import make_url

from app.core.config import Settings

BACKEND_DIR = Path(__file__).resolve().parents[3]


def _psycopg_url(url: str, database: str) -> str:
    """Convert a SQLAlchemy psycopg URL into a URL accepted by psycopg directly."""
    sqlalchemy_url = make_url(url).set(database=database)
    return sqlalchemy_url.render_as_string(hide_password=False).replace(
        "postgresql+psycopg://", "postgresql://", 1
    )


def test_alembic_migrations_apply_to_fresh_database(test_settings: Settings) -> None:
    """Upgrade, inspect, and validate migrations without touching alibi_test."""
    if test_settings.TEST_DATABASE_URL is None:
        raise RuntimeError("A dedicated alibi_test database is required")

    test_database_url = test_settings.TEST_DATABASE_URL.get_secret_value()
    if not test_database_url.endswith("/alibi_test"):
        raise RuntimeError("A dedicated alibi_test database is required")

    database_name = f"alibi_migration_test_{uuid4().hex}"
    migration_database_url = (
        make_url(test_database_url)
        .set(database=database_name)
        .render_as_string(hide_password=False)
    )
    admin_url = _psycopg_url(test_database_url, "postgres")

    with connect(admin_url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
            )

    environment = {
        **os.environ,
        "APP_ENV": "testing",
        "DATABASE_URL": migration_database_url,
    }
    try:
        for command in (
            ("upgrade", "head"),
            ("current",),
            ("check",),
        ):
            subprocess.run(
                [sys.executable, "-m", "alembic", *command],
                cwd=BACKEND_DIR,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
    finally:
        with connect(admin_url, autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("DROP DATABASE IF EXISTS {}").format(
                        sql.Identifier(database_name)
                    )
                )
