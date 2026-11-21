"""SQLAlchemy instrumentation that avoids logging statements and parameters."""

import time
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.metrics import DB_POOL_CHECKOUTS, DB_QUERY_DURATION


def register_db_observability(engine: AsyncEngine) -> None:
    """Register database timing and pool-checkout metrics for an async engine."""

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        del cursor, statement, parameters, context, executemany
        conn.info.setdefault("query_starts", []).append(time.perf_counter())

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        del cursor, statement, parameters, context, executemany
        starts: list[float] = conn.info.get("query_starts", [])
        if starts:
            DB_QUERY_DURATION.observe(time.perf_counter() - starts.pop())

    @event.listens_for(engine.sync_engine.pool, "checkout")
    def checkout(
        dbapi_connection: Any,
        connection_record: Any,
        connection_proxy: Any,
    ) -> None:
        del dbapi_connection, connection_record, connection_proxy
        DB_POOL_CHECKOUTS.inc()
