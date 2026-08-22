# uv

[uv](https://docs.astral.sh/uv/) is a dependency management and packaging tool for Python. It simplifies dependency management by providing a unified, extremely fast interface to manage packages and their dependencies.

This project uses uv with a `uv.lock` lockfile for reproducible installs. The `requirements.txt` / `requirements-dev.txt` files are generated exports (used by the Docker image), not hand-maintained.

## Installation

You can install uv using the official installer:

```txt
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Changing the Python version

uv can download and manage Python interpreters itself:

```txt
uv python install 3.12
```

To pin or select the interpreter used by the project:

```txt
uv python pin 3.12
uv venv --python 3.12
```

After changing the interpreter, run `uv sync` to recreate the environment.

## Adding dependencies

To add a runtime dependency, run:

```txt
uv add package-name
```

To add a development dependency, run:

```txt
uv add --dev package-name
```

This will install the latest version of the package and add it to your pyproject.toml file taking into account the other dependencies so it doesn't break anything. The lockfile (`uv.lock`) is updated automatically.

## Updating dependencies

To update all dependencies to their latest allowed versions and refresh the lockfile, run:

```txt
uv lock --upgrade
```

To upgrade a single package:

```txt
uv lock --upgrade-package package-name
```

Then apply the changes to your environment:

```txt
uv sync
```

## Installing dependencies

To install the exact locked environment for a project, run:

```txt
uv sync
```

For production cases without development dependencies:

```txt
uv sync --no-dev
```

## Running commands

Run any command inside the managed environment with:

```txt
uv run pytest
uv run ruff check .
uv run uvicorn src.app:app --reload --port 8000
```

## Exporting requirements.txt

The Docker image installs from an exported requirements file. Regenerate both exports after any dependency change:

```txt
uv export --format requirements.txt --no-dev --no-hashes -o requirements.txt
uv export --format requirements.txt --no-hashes -o requirements-dev.txt
```

## Removing dependencies

To remove a dependency, run:

```txt
uv remove package-name
```

For more information and detailed documentation, check out the official [uv documentation](https://docs.astral.sh/uv/).
