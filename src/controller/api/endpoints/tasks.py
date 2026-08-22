"""Endpoints to enqueue and track Celery background tasks."""

import logging
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.core.celery_app import celery_app
from src.service.tasks import heavy_computation

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Tasks"])


@router.post(
    "/heavy-tasks",
    summary="Enqueue a heavy task",
    description=(
        "Offload a simulated long-running job to the Celery worker and return "
        "its tracking id immediately."
    ),
)
async def enqueue_heavy_task(duration_seconds: int = 5) -> JSONResponse:
    """Enqueue ``heavy_computation`` on the worker queue."""
    task = heavy_computation.apply_async(args=[duration_seconds])
    return JSONResponse(status_code=202, content={"task_id": task.id})


@router.get(
    "/heavy-tasks/{task_id}",
    summary="Track a heavy task",
    description="Return the state and result (when finished) of a queued task.",
)
async def heavy_task_status(task_id: str) -> dict[str, Any]:
    """Report progress for a previously enqueued task."""
    result = celery_app.AsyncResult(task_id)
    payload: dict[str, Any] = {"task_id": task_id, "state": result.state}
    if result.ready():
        payload["result"] = result.result
    return payload
