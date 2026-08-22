# FastAPI Production Archetype

## Description

This is a FastAPI project archetype for production-ready applications. It provides a structure for building scalable and maintainable applications with FastAPI following Domain Driven Design (DDD) principles, best Docker practices, and a set of tools for development, testing, and deployment with the best code quality tools available.

## Table of Contents

- [FastAPI Production Archetype](#fastapi-production-archetype)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [Contributing](#contributing)
  - [Generate a New Project](#generate-a-new-project)
  - [Security and User Management](#security-and-user-management)
  - [Background Tasks](#background-tasks)
  - [Getting Started](#getting-started)
    - [Built With](#built-with)
    - [Prerequisites](#prerequisites)
    - [Running the App](#running-the-app)
      - [Terminal](#terminal)
      - [VSCode](#vscode)
      - [Docker](#docker)
    - [Development](#development)
  - [Roadmap](#roadmap)

## Contributing

Check the [contributing documentation](.github/CONTRIBUTING.md) for more information.

## Generate a New Project

This repository doubles as a [Cookiecutter](https://cookiecutter.readthedocs.io/) template: it generates a standalone project with this exact structure, best practices and tooling preconfigured, depending on the published [`fastapi-crud-base`](https://pypi.org/project/fastapi-crud-base/) library for the generic CRUD layer.

```bash
uvx cookiecutter gh:n0nuser/fastapi-archetype --directory cookiecutter
```

You will be prompted for a project name, description, author and versions; everything else (structure, CI, Docker, Spectral ruleset, migrations) comes ready out of the box.

## Security and User Management

Registration, JWT authentication, password reset and role-based access control ship by default via [fastapi-users](https://fastapi-users.github.io/fastapi-users/). See [docs/security.md](docs/security.md) for endpoints, configuration and how to protect your own endpoints with `current_user` / `current_superuser`.

## Background Tasks

Heavy work is offloaded to Celery workers over a Redis broker, with Flower monitoring at port 5555. See [docs/celery.md](docs/celery.md).

## Getting Started

### Built With

<!--

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

Change the tools to fit your project

-->

Development:

- [Python 3](https://www.python.org/): The programming language used.
- [uv](https://docs.astral.sh/uv/): A fast tool for dependency management and packaging in Python.
- [FastAPI](https://fastapi.tiangolo.com/): A modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.
- [Pydantic](https://pydantic-docs.helpmanual.io/): Data validation and settings management using Python type annotations.
- [HTTPX](https://www.python-httpx.org/): A fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2.

Security:

- [fastapi-users](https://fastapi-users.github.io/fastapi-users/): Registration, JWT authentication and user management. See [docs/security.md](docs/security.md).

Background Tasks:

- [Celery](https://docs.celeryq.dev/): Distributed task queue for heavy workloads.
- [Flower](https://flower.readthedocs.io/): Web UI for monitoring Celery. See [docs/celery.md](docs/celery.md).

Development Tools:

- [Pre-Commit](https://pre-commit.com/): A framework for managing and maintaining multi-language pre-commit hooks.
- [Ruff](https://docs.astral.sh/ruff/): An extremely fast linter and formatter (linting, style checks, and security rules) for Python.

Databases:

- [SQLAlchemy](https://www.sqlalchemy.org/): The Python SQL Toolkit and Object-Relational Mapping (ORM) library.
- [PostgreSQL](https://www.postgresql.org/): A powerful, open-source object-relational database system.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/): A database migrations tool for SQLAlchemy. See our [Alembic documentation](docs/alembic.md).

Deployment:

- [Uvicorn](https://www.uvicorn.org/): A lightning-fast ASGI server implementation, using uvloop and httptools.
- [Docker](https://www.docker.com/): A set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages called containers.
- [Docker-Compose](https://docs.docker.com/compose/): A tool for defining and running multi-container Docker applications.
- [Traefik / Nginx](docs/deployment.md): Optional reverse proxy overlays with automatic HTTPS (Traefik).
- [Prometheus](https://prometheus.io/): Metrics exposed at `/metrics` via prometheus-fastapi-instrumentator.
- [OpenTelemetry](https://opentelemetry.io/): Opt-in distributed tracing (`OTEL_ENABLED=true`).
- [Redis](https://redis.io/): Opt-in response caching (`CACHE_ENABLED=true`).

Testing:

- [Pytest](https://docs.pytest.org/en/stable/): A framework that makes it easy to write simple and scalable tests.
- [Pytest-Cov](https://pytest-cov.readthedocs.io/): Coverage reporting with a configurable CI floor.
- [Spectral](https://meta.stoplight.io/docs/spectral/): OpenAPI specification linting in CI and pre-commit.
- [Cookiecutter](https://cookiecutter.readthedocs.io/): This repository doubles as a project template (see [Generate a New Project](#generate-a-new-project)).

### Prerequisites

- [Python 3.12 or higher](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/): uv is a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you. For documentation refer to [uv](https://docs.astral.sh/uv/) or to a little guide we made [here](docs/uv.md).
- [Docker](https://www.docker.com/): Docker is a set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages called containers. For documentation refer to [Docker](https://docs.docker.com/get-started/).

### Running the App

You need to have the environment set up with uv by using `uv sync` and the dependencies will be installed. After that, you can start the application.

#### Terminal

To start the application, run the following command:

```bash
uvicorn src.app:app --reload --port 8000
```

This will start the application on port 8000. You can change the port by changing the `--port` argument.

#### VSCode

In VSCode you can use the `Run` button on the top right corner of the editor to start the application as the `launch.json` file is already set up.

#### Docker

Also, you can use the `docker-compose` to start the application with the following command:

```bash
cd docker
docker-compose up
```

If you don't know how to use Docker, you can check the [Docker documentation](https://docs.docker.com/get-started/) and our [deployment documentation](docs/deployment.md).

### Development

> [!IMPORTANT]
> Be sure to:
>
> - Run `pre-commit install` to install the pre-commit hooks. This will run the linters and formatters before you commit your code. If you don't have pre-commit installed in your system, you can install it with `pip install pre-commit`.
> - Check the [project structure documentation](docs/project-structure.md) for more information.
> - Check the [recommended extensions documentation](docs/recommended-extensions.md) for more information.
> - Check the [contributing documentation](.github/CONTRIBUTING.md) for more information.
> - Check the [deployment documentation](docs/deployment.md) for more information.

### Testing

Most of the suite is marked as `integration` because it exercises real Postgres behaviour. Start the ephemeral test database first:

```bash
docker compose -f docker/docker-compose.test.yml up -d db-test
```

Then run everything with coverage:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

The database connection is configured through `TEST_DATABASE_URL` (defaults to the compose instance on port 5433). CI spins up its own Postgres service container, so no extra setup is needed there.

## Roadmap

See the open issues for a full list of proposed features (and known issues).
