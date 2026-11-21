"""Prometheus metrics exposed by the Alibi API."""

from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "alibi_http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status_code"],
)
HTTP_DURATION = Histogram(
    "alibi_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "route"],
)
DB_QUERY_DURATION = Histogram(
    "alibi_db_query_duration_seconds",
    "Database query duration",
)
DB_POOL_CHECKOUTS = Counter(
    "alibi_db_pool_checkouts_total",
    "Database connections checked out",
)
