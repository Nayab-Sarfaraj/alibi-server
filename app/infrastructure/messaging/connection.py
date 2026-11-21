"""Message-broker connection lifecycle helpers."""

import aio_pika
from aio_pika.abc import AbstractRobustConnection

from app.core.config import settings


async def connect_rabbitmq() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(
        settings.RABBITMQ_URL.get_secret_value(),
        timeout=10,
    )
