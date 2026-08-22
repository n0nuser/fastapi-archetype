"""Authentication and authorization wiring for fastapi-users.

Assembles the JWT auth routes and user management routes, and exposes the
``current_user`` / ``current_superuser`` dependencies used to protect
endpoints with role-based access control.
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from src.controller.api.schemas.user import UserCreate, UserRead, UserUpdate
from src.core.config import settings
from src.repository.models.user import User
from src.service.user.manager import get_user_manager


def get_jwt_strategy() -> JWTStrategy:
    """Build the JWT strategy; called per request."""
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=settings.JWT_LIFETIME_SECONDS)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])

# Role-based access control guards: attach via ``Depends`` to any endpoint.
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

# fastapi-users ships its operations without OpenAPI descriptions; document
# them here so the exported contract stays Spectral-clean and useful.
_OPERATION_DESCRIPTIONS = {
    ("POST", "/register"): "Register a new user with email and password.",
    ("POST", "/login"): "Exchange username and password for a JWT bearer token.",
    ("POST", "/logout"): "Discard the bearer token client-side (stateless JWT).",
    ("POST", "/forgot-password"): (
        "Request a password reset. Delivers the token via on_after_forgot_password."
    ),
    ("POST", "/reset-password"): "Set a new password using a valid reset token.",
    ("POST", "/request-verify-token"): "Request a verification token for the given email.",
    ("POST", "/verify"): "Activate a user account with a valid verification token.",
    ("GET", "/me"): "Return the authenticated user's profile.",
    ("PATCH", "/me"): "Update the authenticated user's profile.",
    ("GET", "/{id}"): "Return a user by id. Requires superuser privileges.",
    ("PATCH", "/{id}"): "Partially update a user by id. Requires superuser privileges.",
    ("DELETE", "/{id}"): "Delete a user by id. Requires superuser privileges.",
}


def _apply_operation_descriptions(routers: list[APIRouter]) -> None:
    """Attach the curated descriptions to the fastapi-users routes."""
    for router in routers:
        for route in router.routes:
            methods = getattr(route, "methods", None) or set()
            method = next(iter(methods - {"HEAD"}), "")
            description = _OPERATION_DESCRIPTIONS.get((method, route.path))
            if description and not route.description:
                route.description = description


auth_routers = [
    fastapi_users.get_register_router(UserRead, UserCreate),
    fastapi_users.get_auth_router(auth_backend),
    fastapi_users.get_reset_password_router(),
    fastapi_users.get_verify_router(UserRead),
]
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
_apply_operation_descriptions([*auth_routers, users_router])

router = APIRouter()
router.include_router(
    auth_routers[0],
    prefix="/auth",
    tags=["Auth"],
)
router.include_router(
    auth_routers[1],
    prefix="/auth/jwt",
    tags=["Auth"],
)
router.include_router(
    auth_routers[2],
    prefix="/auth",
    tags=["Auth"],
)
router.include_router(
    auth_routers[3],
    prefix="/auth",
    tags=["Auth"],
)
router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)
