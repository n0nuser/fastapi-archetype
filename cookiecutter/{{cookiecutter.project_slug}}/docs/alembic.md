# Alembic

Alembic is a **tool designed to help you manage database schema changes**. It is **recommended** to use Alembic in combination **with SQLAlchemy** to keep your database schema in sync with your application's data model.

If you are not using Alembic yet, it is a good idea to start using it. Alembic provides a way to track and apply database schema changes in a consistent and repeatable manner, which can help make your application more maintainable over time.

## Getting Started

### Create migration repository

To get started with Alembic, you need to create a migration repository. This repository will hold all of your database schema changes as individual migration scripts. You can create a new migration repository using the alembic init command:

```py
alembic init <repository_name>
# Recommended
alembic init alembic
```

This command will create a new directory with the specified repository name, containing several files and directories that are used by Alembic.

### Adding migration scripts

Once you have created the migration repository, you can start adding migration scripts to it. A migration script is a Python script that contains instructions for changing the database schema. You can create a new migration script using the alembic revision command:

```py
alembic revision --autogenerate -m "<description_of_change>"
# Example
alembic revision --autogenerate -m "Initial schema"
```

This command will create a new migration script with the specified description. You can then edit the migration script to add your database schema changes.

### Apply migration scripts

To apply the migration scripts to your database, you can use the alembic upgrade command:

```py
alembic upgrade head
```

This command will apply all of the migration scripts that have not yet been applied to your database.

## Usage in this project

Alembic is already wired up: the repository lives in `migrations/`, configured by `alembic.ini` at the project root. All commands run through `uv run alembic ...`.

The target database URL is taken from `SQLALCHEMY_DATABASE_URI` (built from your `src/.env`). Override it for a single command with the `ALEMBIC_DATABASE_URL` environment variable, which is handy when generating a migration against a scratch database.

### Create a new migration

After changing a model under `src/repository/models/`, generate a script and review it before applying:

```txt
uv run alembic revision --autogenerate -m "add discount to customer"
```

Model modules must be importable for autogenerate to see them; `migrations/env.py` already imports them explicitly.

### Apply or revert migrations

```txt
uv run alembic upgrade head
uv run alembic downgrade -1
```

To confirm the models match the applied migrations (useful in CI later):

```txt
uv run alembic check
```

### Relationship with `init_db`

The application still creates missing tables on startup (`init_db`) so a fresh development stack works without a manual step. Alembic is the tool to use once a database holds data you cannot recreate: it evolves the schema instead of assuming an empty one.
