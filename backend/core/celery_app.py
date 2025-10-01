from celery import Celery
import os

broker_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
backend_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "ihearyou",
    broker=broker_url,
    backend=backend_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    include=["backend.core.tasks"],
)
