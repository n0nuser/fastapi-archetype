"""Background task definitions executed by Celery workers."""

import logging
import time

from src.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.heavy_computation")
def heavy_computation(duration_seconds: int = 5) -> dict:
    """Simulate a long-running job; replace with real workload examples.

    Args:
        duration_seconds: How long to pretend to work.

    Returns:
        A small report describing the executed job.
    """
    logger.info("Heavy computation started for %ss.", duration_seconds)
    time.sleep(duration_seconds)
    logger.info("Heavy computation finished.")
    return {"worked_for": duration_seconds}
