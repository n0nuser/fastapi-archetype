# Background Tasks with Celery

Heavy or long-running work is offloaded to [Celery](https://docs.celeryq.dev/) workers backed by Redis. [Flower](https://flower.readthedocs.io/) ships alongside for monitoring.

## Architecture

| Piece | Location | Purpose |
| --- | --- | --- |
| Celery app | `src/core/celery_app.py` | Broker/backend wiring from settings |
| Tasks | `src/service/tasks.py` | Task definitions (`tasks.heavy_computation` example) |
| Endpoints | `src/controller/api/endpoints/tasks.py` | Enqueue (`POST /heavy-tasks`) and track (`GET /heavy-tasks/{id}`) |
| Worker | `docker-compose.yml` `worker` service | Executes queued tasks |
| Flower | `docker-compose.yml` `flower` service | Web UI at `http://localhost:5555` |

Broker and result backend use dedicated Redis logical databases (`/1`, `/2`) so queue traffic never collides with the HTTP response cache (`/0`):

```bash
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

## Running the full stack

```bash
cp src/.env.example src/.env
docker compose -f docker/docker-compose.yml up --build
```

Then:

1. Enqueue: `curl -X POST 'http://localhost:8000/api/customer-system/heavy-tasks?duration_seconds=10'`
2. Track: `curl http://localhost:8000/api/customer-system/heavy-tasks/<task_id>`
3. Monitor: open <http://localhost:5555> (Flower)

## Adding your own tasks

1. Add a task function in `src/service/tasks.py`:

   ```python
   @celery_app.task(name="tasks.generate_report")
   def generate_report(user_id: str) -> dict: ...
   ```

2. The module is already listed in `Celery(include=[...])`; restart the worker after changes.
3. Call it from an endpoint with `generate_report.apply_async(args=[...])` and return `task.id`.

## Testing without Redis

The integration suite sets `task_always_eager` plus an in-memory result backend (`tests/controller/api/test_tasks.py`), so tasks run inline during tests — no broker required.
