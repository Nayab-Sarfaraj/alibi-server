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
        del conn, cursor, statement, parameters, executemany
        context._alibi_query_started = time.perf_counter()

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        del conn, cursor, statement, parameters, executemany
        started = getattr(context, "_alibi_query_started", None)
        if started is not None:
            DB_QUERY_DURATION.observe(time.perf_counter() - started)
            del context._alibi_query_started

    @event.listens_for(engine.sync_engine, "handle_error")
    def handle_error(exception_context: Any) -> None:
        """Discard per-execution timing data when statement execution fails."""
        context = exception_context.execution_context
        if context is not None and hasattr(context, "_alibi_query_started"):
            del context._alibi_query_started

    @event.listens_for(engine.sync_engine.pool, "checkout")
    def checkout(
        dbapi_connection: Any,
        connection_record: Any,
        connection_proxy: Any,
    ) -> None:
        del dbapi_connection, connection_record, connection_proxy
        DB_POOL_CHECKOUTS.inc()
