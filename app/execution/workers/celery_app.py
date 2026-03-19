"""
Celery — executor assíncrono de tasks pesadas.
"""

import os
from celery import Celery

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "clinic_ai",
    broker=RABBITMQ_URL,
    backend=REDIS_URL,
    include=[
        "app.execution.workers.media_worker",
        "app.execution.workers.crm_sync_worker",
        "app.execution.workers.doctoralia_sync_worker",
        "app.execution.workers.payments_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
