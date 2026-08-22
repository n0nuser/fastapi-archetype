"""Celery application for background and heavy tasks.

The broker and result backend live in dedicated Redis logical databases so
queue traffic never collides with the HTTP response cache.
"""

from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.service.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    # Serialize kwargs/args safely across worker versions.
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
