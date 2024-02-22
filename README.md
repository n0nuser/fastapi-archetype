# FastAPI Production Archetype

## Description

This is a FastAPI project archetype for production-ready applications. It provides a structure for building scalable and maintainable applications with FastAPI following Domain Driven Design (DDD) principles, best Docker practices, and a set of tools for development, testing, and deployment with the best code quality tools available.

## Table of Contents

- [FastAPI Production Archetype](#fastapi-production-archetype)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [Contributing](#contributing)
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

## Getting Started

### Built With

<!--

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

Change the tools to fit your project

-->

Development:

- [Python 3](https://www.python.org/): The programming language used.
- [Poetry](https://python-poetry.org/): A tool for dependency management and packaging in Python.
- [FastAPI](https://fastapi.tiangolo.com/): A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
- [Pydantic](https://pydantic-docs.helpmanual.io/): Data validation and settings management using Python type annotations.
- [HTTPX](https://www.python-httpx.org/): A fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2.

Development Tools:

- [Pre-Commit](https://pre-commit.com/): A framework for managing and maintaining multi-language pre-commit hooks.
- [Ruff](https://docs.astral.sh/ruff/): A tool for managing Python environments.
- [Flake8](https://flake8.pycqa.org/en/latest/): A tool that glues together pycodestyle, pyflakes, mccabe, and third-party plugins to check the style and quality of some Python code.
- [Pylint](https://www.pylint.org/): A tool that checks for errors in Python code, tries to enforce a coding standard, looks for code smells, and can offer simple refactoring suggestions.
- [Bandit](https://bandit.readthedocs.io/en/latest/): A tool designed to find common security issues in Python code.

Databases:

- [SQLAlchemy](https://www.sqlalchemy.org/): The Python SQL Toolkit and Object-Relational Mapping (ORM) library.
- [PostgreSQL](https://www.postgresql.org/): A powerful, open-source object-relational database system.

Deployment:

- [Uvicorn](https://www.uvicorn.org/): A lightning-fast ASGI server implementation, using uvloop and httptools.
- [Docker](https://www.docker.com/): A set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages called containers.
- [Docker-Compose](https://docs.docker.com/compose/): A tool for defining and running multi-container Docker applications.

Testing:

- [Pytest](https://docs.pytest.org/en/stable/): A framework that makes it easy to write simple and scalable tests.
- [Pytest-Mock](https://pytest-mock.readthedocs.io/en/latest/): A thin-wrapper around the mock package for easier use with py.test.

### Prerequisites

- [Python 3.10 or higher](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/): Poetry is a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you. For documentation refer to [Poetry](https://python-poetry.org/docs/) or to a little guide we made [here](docs/poetry.md).
- [Docker](https://www.docker.com/): Docker is a set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages called containers. For documentation refer to [Docker](https://docs.docker.com/get-started/).

### Running the App

You need to have the environment set up with Poetry by using `poetry install` and the dependencies will be installed. After that, you can start the application.

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

## Roadmap

See the open issues for a full list of proposed features (and known issues).
