"""
RabbitMQ — broker principal de filas assíncronas.
Filas: realtime, media, sync, reminders, reactivation
"""

import os
import aio_pika

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

QUEUES = {
    "realtime": "realtime",
    "media": "media",
    "sync": "sync",
    "reminders": "reminders",
    "reactivation": "reactivation",
}


async def get_connection():
    return await aio_pika.connect_robust(RABBITMQ_URL)


async def publish(queue_name: str, message: dict):
    """Publica mensagem em uma fila."""
    # TODO: implementar publish com retry e dead letter queue
    pass
