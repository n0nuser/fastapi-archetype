# Poetry

Poetry is a dependency management and packaging tool for Python. It simplifies dependency management by providing a unified interface to manage packages and their dependencies.

## Installation

You can install Poetry using pip:

```txt
pip install poetry
```

## Changing the Python version

Check the [official documentation](poetry config virtualenvs.create false --local) for more information.

To change the Python version used by Poetry, run:

```txt
poetry env use /full/path/to/python
poetry env use python3.10
poetry env use 3.7
```

After that, run `poetry update` to update the dependencies. This will update the `pyproject.toml` and `poetry.lock` files with the new versions and also install the environment.

## Adding dependencies

To add a dependency, run:

```txt
poetry add package-name
```

This will install the latest version of the package and add it to your pyproject.toml file taking in account the other dependencies so it doesn't break anything.

## Updating dependencies

To update a dependency, run:

```txt
poetry update
poetry update package-name
```

This will update the package(s) to the latest version and update the pyproject.toml file.

## Installing dependencies

To install the dependencies for a project, run:

```txt
poetry install
```

This will install all the dependencies listed in the pyproject.toml file.

## Running scripts

You can define scripts in the pyproject.toml file and run them with Poetry. For example, to run a script called test:

```toml
[tool.poetry.scripts]
test = "pytest"
```

You can run the script with:

```txt
poetry run test
```

## Building and packaging

To build your project and create a distributable package, run:

```txt
poetry build
```

This will create a dist directory with the distributable package(s).

## Publishing

To publish your package to a package index (such as PyPI), you can use Poetry's publish command. Before publishing, make sure you have configured your credentials and set the appropriate repository in your pyproject.toml file.

```txt
poetry publish
```

This will package and upload your package to the configured repository.

For more information and detailed documentation, check out the official Poetry documentation.
