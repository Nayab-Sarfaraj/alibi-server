import logging
from uuid import UUID

from httpx import AsyncClient


async def test_request_id_header(client: AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert UUID(response.headers["X-Request-ID"])


async def test_request_ids_are_unique(client: AsyncClient) -> None:
    first_response = await client.get("/health/live")
    second_response = await client.get("/health/live")

    assert (
        first_response.headers["X-Request-ID"]
        != second_response.headers["X-Request-ID"]
    )


async def test_structured_request_log(client: AsyncClient, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="alibi.api"):
        response = await client.get("/health/live")

    assert response.status_code == 200
    records = [
        record
        for record in caplog.records
        if record.name == "alibi.api"
        and record.getMessage() == "HTTP request completed"
    ]
    assert records
    assert records[-1].status_code == 200
    assert records[-1].duration_ms >= 0


async def test_metrics_exposes_http_metrics(client: AsyncClient) -> None:
    await client.get("/health/live")
    response = await client.get("/metrics")

    assert response.status_code == 200
    assert "alibi_http_requests_total" in response.text
    assert "alibi_http_request_duration_seconds" in response.text
