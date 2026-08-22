"""This module provides utilities for managing exceptions in a FastAPI application.

It provides functions for logging exceptions and managing responses to exceptions.
It also imports several common exceptions from SQLAlchemy for convenience.

Functions:
    manage_api_exceptions(app: FastAPI) -> None:
        Add Exception listeners so raising errors is easier.
"""

import contextlib
import logging
import os
import traceback
from typing import TYPE_CHECKING

from asgi_correlation_id import correlation_id
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound, OperationalError, ProgrammingError

from src.controller.errors import exceptions
from src.controller.errors.error_responses import ERROR_RESPONSES

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.controller.api.schemas.error_message import ErrorMessage


def _log_exception(request: Request, exc: Exception) -> None:
    exc_str = None
    try:
        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    except Exception:
        exc_str = traceback.format_exc().replace("\n", " ").replace("   ", " ")
    logger.error("%s: %s", request, exc_str)


def _manage_exception(request: Request, exc: Exception, code: int) -> JSONResponse:
    """Manage exceptions.

    Args:
        request (Request): Request object
        exc (Exception): Exception
        code (int): HTTP status code

    Returns:
        JSONResponse: Exception response
    """
    _log_exception(request, exc)
    error: ErrorMessage | None = ERROR_RESPONSES.get(code)
    headers = {"X-Request-ID": correlation_id.get() or ""}
    if not error:
        return JSONResponse(status_code=code, content=None, headers=headers)

    if os.getenv("ENVIRONMENT") in ["PYTEST", "DEV", "PREPROD"]:
        with contextlib.suppress(TypeError):
            if error and error.messages and len(error.messages) > 0:
                error.messages[0].description = str(exc)
    return JSONResponse(
        status_code=code,
        content=error.model_dump() if error else None,
        headers=headers,
    )


def manage_api_exceptions(app: FastAPI) -> None:  # noqa: C901
    """Add Exception listeners so raising errors is easier.

    Args:
        app (FastAPI): FastAPI application
    """

    @app.exception_handler(exceptions.HTTP400BadRequestError)
    @app.exception_handler(RequestValidationError)
    async def bad_request_handler(
        request: Request,
        exc: exceptions.HTTP400BadRequestError,
    ) -> JSONResponse:
        code = status.HTTP_400_BAD_REQUEST
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP401UnauthorizedError)
    async def unauthorized_handler(
        request: Request,
        exc: exceptions.HTTP401UnauthorizedError,
    ) -> JSONResponse:
        code = status.HTTP_401_UNAUTHORIZED
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP403ForbiddenError)
    async def forbidden_handler(
        request: Request,
        exc: exceptions.HTTP403ForbiddenError,
    ) -> JSONResponse:
        code = status.HTTP_403_FORBIDDEN
        return _manage_exception(request, exc, code)

    @app.exception_handler(NoResultFound)
    @app.exception_handler(exceptions.HTTP404NotFoundError)
    async def not_found_handler(
        request: Request,
        exc: exceptions.HTTP404NotFoundError,
    ) -> JSONResponse:
        code = status.HTTP_404_NOT_FOUND
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP405MethodNotAllowedError)
    async def method_not_allowed_handler(
        request: Request,
        exc: exceptions.HTTP405MethodNotAllowedError,
    ) -> JSONResponse:
        code = status.HTTP_405_METHOD_NOT_ALLOWED
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP406NotAcceptableError)
    async def not_acceptable_handler(
        request: Request,
        exc: exceptions.HTTP406NotAcceptableError,
    ) -> JSONResponse:
        code = status.HTTP_406_NOT_ACCEPTABLE
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP409ConflictError)
    async def conflict_handler(
        request: Request,
        exc: exceptions.HTTP409ConflictError,
    ) -> JSONResponse:
        code = status.HTTP_409_CONFLICT
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP413PayloadTooLargeError)
    async def payload_too_large_handler(
        request: Request,
        exc: exceptions.HTTP413PayloadTooLargeError,
    ) -> JSONResponse:
        code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP414URITooLongError)
    async def uri_too_long_handler(
        request: Request,
        exc: exceptions.HTTP414URITooLongError,
    ) -> JSONResponse:
        code = status.HTTP_414_REQUEST_URI_TOO_LONG
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP415UnsupportedMediaTypeError)
    async def unsupported_media_type_handler(
        request: Request,
        exc: exceptions.HTTP415UnsupportedMediaTypeError,
    ) -> JSONResponse:
        code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP422UnprocessableEntityError)
    async def unprocessable_entity_handler(
        request: Request,
        exc: exceptions.HTTP422UnprocessableEntityError,
    ) -> JSONResponse:
        code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP423LockedError)
    async def locked_handler(request: Request, exc: exceptions.HTTP423LockedError) -> JSONResponse:
        code = status.HTTP_423_LOCKED
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP429TooManyRequestsError)
    async def too_many_requests_handler(
        request: Request,
        exc: exceptions.HTTP429TooManyRequestsError,
    ) -> JSONResponse:
        code = status.HTTP_429_TOO_MANY_REQUESTS
        return _manage_exception(request, exc, code)

    @app.exception_handler(AttributeError)
    @app.exception_handler(ValueError)
    @app.exception_handler(exceptions.HTTP500InternalServerError)
    @app.exception_handler(OperationalError)
    @app.exception_handler(ProgrammingError)
    @app.exception_handler(IntegrityError)
    async def internal_server_error_handler(
        request: Request,
        exc: exceptions.HTTP500InternalServerError,
    ) -> JSONResponse:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP501NotImplementedError)
    async def not_implemented_handler(
        request: Request,
        exc: exceptions.HTTP501NotImplementedError,
    ) -> JSONResponse:
        code = status.HTTP_501_NOT_IMPLEMENTED
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP502BadGatewayError)
    async def bad_gateway_handler(
        request: Request,
        exc: exceptions.HTTP502BadGatewayError,
    ) -> JSONResponse:
        code = status.HTTP_502_BAD_GATEWAY
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP503ServiceUnavailableError)
    async def service_unavailable_handler(
        request: Request,
        exc: exceptions.HTTP503ServiceUnavailableError,
    ) -> JSONResponse:
        code = status.HTTP_503_SERVICE_UNAVAILABLE
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.HTTP504GatewayTimeoutError)
    async def gateway_timeout_handler(
        request: Request,
        exc: exceptions.HTTP504GatewayTimeoutError,
    ) -> JSONResponse:
        code = status.HTTP_504_GATEWAY_TIMEOUT
        return _manage_exception(request, exc, code)
