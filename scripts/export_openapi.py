"""Export the OpenAPI schema of the application to a JSON file.

The export never connects to PostgreSQL or Redis: importing the app only
builds routes and middleware, while connections happen during lifespan
startup. A resolvable environment is still required (same as running the
app), e.g. `cp src/.env.example src/.env`.

Usage:
    uv run python scripts/export_openapi.py [output_path]

Defaults to writing `openapi.json` at the repository root.
"""

import json
import sys
from pathlib import Path

from src.app import app

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    """Dump the FastAPI OpenAPI schema as JSON."""
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "openapi.json"
    schema = app.openapi()
    output.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OpenAPI schema written to {output}")


if __name__ == "__main__":
    main()
