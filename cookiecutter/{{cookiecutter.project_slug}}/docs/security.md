# Security & User Management

The archetype ships [fastapi-users](https://fastapi-users.github.io/fastapi-users/) wired for JWT authentication over a synchronous SQLAlchemy stack.

## What you get out of the box

| Capability | Endpoint | Notes |
| --- | --- | --- |
| Registration | `POST /auth/register` | Email + password, hashed with `pwdlib` (argon2/bcrypt) |
| Login | `POST /auth/jwt/login` | OAuth2 password form; returns a bearer JWT |
| Logout | `POST /auth/jwt/logout` | Stateless: clients discard the token |
| Profile | `GET/PATCH /users/me` | Authenticated user's own profile |
| Administration | `GET/PATCH/DELETE /users/{id}` | Superuser-only |
| Verification | `POST /auth/request-verify-token`, `POST /auth/verify` | Token-based account activation |
| Password reset | `POST /auth/forgot-password`, `POST /auth/reset-password` | Token-based reset |

All routes live under the API root path (e.g. `/api/customer-system/auth/register`) and are tagged `Auth` / `Users` in the OpenAPI schema.

## Configuration

```bash
RESET_PASSWORD_TOKEN_SECRET=changethis   # override in real deployments!
VERIFICATION_TOKEN_SECRET=changethis     # override in real deployments!
JWT_LIFETIME_SECONDS=3600
```

The JWT signing secret reuses `SECRET_KEY`. Every default in `.env.example` is a development-only template value.

## Role-based access control

Guards live in `src/controller/api/security.py`; attach them to any endpoint:

```python
from typing import Annotated

from fastapi import Depends

from src.controller.api.security import current_user, current_superuser


@router.delete("/{customer_id}")
async def delete_customer(
    user: Annotated[User, Depends(current_superuser)],  # admin-only mutation
) -> None:
    ...
```

`current_user(active=True)` rejects anonymous or deactivated users; `current_superuser` additionally requires the `is_superuser` flag. Promote an administrator directly in the database (`UPDATE users SET is_superuser = true WHERE ...`) or via a seed script.

## Email delivery integration point

There is no mail sender in an archetype by design. `UserManager.on_after_forgot_password` and `on_after_request_verify` currently log the tokens; replace those hooks with your delivery provider when moving past local development.

## Database adapter note

Upstream `fastapi-users-db-sqlalchemy` is async-only, while this archetype runs sync SQLAlchemy (psycopg2). `src/repository/crud/user.py` provides `SyncSQLAlchemyUserDatabase`, implementing the upstream interface against the shared request-scoped `Session`. If you later migrate to an async engine, swap this adapter for `SQLAlchemyUserDatabase` from the upstream package.

## Migrations

The `users` table is created by Alembic revision `207a9b64c7fd`. Test environments create it automatically via `Base.metadata.create_all`.
