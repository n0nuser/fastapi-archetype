"""Integration tests for the Celery task endpoints (runs tasks eagerly)."""

from collections.abc import Iterator

import pytest

from src.core.celery_app import celery_app

pytestmark = pytest.mark.integration

HEAVY_TASKS = "/api/customer-system/heavy-tasks"


@pytest.fixture(autouse=True)
def eager_celery() -> Iterator[None]:
    """Execute queued tasks inline so no worker process is required."""
    original = (celery_app.conf.task_always_eager, celery_app.conf.task_store_eager_result)
    celery_app.conf.task_always_eager = True
    # Store eager results so the tracking endpoint can read them back.
    celery_app.conf.task_store_eager_result = True
    yield
    celery_app.conf.task_always_eager, celery_app.conf.task_store_eager_result = original


def test_enqueue_returns_task_id(client) -> None:
    response = client.post(f"{HEAVY_TASKS}?duration_seconds=0")

    assert response.status_code == 202
    assert response.json()["task_id"]


def test_status_reports_result_after_completion(client) -> None:
    enqueued = client.post(f"{HEAVY_TASKS}?duration_seconds=0").json()["task_id"]

    status = client.get(f"{HEAVY_TASKS}/{enqueued}").json()

    assert status["task_id"] == enqueued
    # Eager execution completes inline, so the result is already available.
    assert status["state"] in {"SUCCESS", "PENDING"}
    if status["state"] == "SUCCESS":
        assert status["result"] == {"worked_for": 0}
