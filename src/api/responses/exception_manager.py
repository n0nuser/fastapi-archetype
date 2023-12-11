import contextlib
import json
import os
import traceback
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound, OperationalError, ProgrammingError

import src.api.responses.exceptions as exceptions
from src.api.schemas.error_message import ErrorMessage
from src.api.responses.error_responses import ERROR_RESPONSES
from src.core.logger import logger


def _log_exception(request: Request, exc):
    exc_str = None
    try:
        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    except Exception:
        exc_str = traceback.format_exc().replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")


def _manage_exception(request: Request, exc, code):
    _log_exception(request, exc)
    if x_request_id := request.headers.get("x-request-id"):
        headers = {"X-Request-ID": x_request_id}
    else:
        headers = None

    error: Union[ErrorMessage, None] = ERROR_RESPONSES.get(code)
    if not error:
        return JSONResponse(status_code=code, content=None, headers=headers)

    if os.getenv("ENVIRONMENT") in ["PYTEST", "DEV", "PREPROD"]:
        with contextlib.suppress(TypeError):
            if error is not None and error.messages is not None and len(error.messages) > 0:
                error.messages[0].description = json.loads(json.dumps(str(exc)))
    return JSONResponse(status_code=code, content=error.dict() if error else None, headers=headers)


def manage_api_exceptions(app: FastAPI) -> None:  # noqa: C901
    """Add Exception listeners so raising errors is easier.

    Args:
        app (FastAPI): FastAPI application
    """

    @app.exception_handler(exceptions.BadRequest)
    @app.exception_handler(RequestValidationError)
    async def bad_request_handler(request: Request, exc: exceptions.BadRequest):
        code = status.HTTP_400_BAD_REQUEST
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.Unauthorized)
    async def unauthorized_handler(request: Request, exc: exceptions.Unauthorized):
        code = status.HTTP_401_UNAUTHORIZED
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.Forbidden)
    async def forbidden_handler(request: Request, exc: exceptions.Forbidden):
        code = status.HTTP_403_FORBIDDEN
        return _manage_exception(request, exc, code)

    @app.exception_handler(NoResultFound)
    @app.exception_handler(exceptions.NotFound)
    async def not_found_handler(request: Request, exc: exceptions.NotFound):
        code = status.HTTP_404_NOT_FOUND
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.MethodNotAllowed)
    async def method_not_allowed_handler(request: Request, exc: exceptions.MethodNotAllowed):
        code = status.HTTP_405_METHOD_NOT_ALLOWED
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.NotAcceptable)
    async def not_acceptable_handler(request: Request, exc: exceptions.NotAcceptable):
        code = status.HTTP_406_NOT_ACCEPTABLE
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.Conflict)
    async def conflict_handler(request: Request, exc: exceptions.Conflict):
        code = status.HTTP_409_CONFLICT
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.PayloadTooLarge)
    async def payload_too_large_handler(request: Request, exc: exceptions.PayloadTooLarge):
        code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.URITooLong)
    async def uri_too_long_handler(request: Request, exc: exceptions.URITooLong):
        code = status.HTTP_414_REQUEST_URI_TOO_LONG
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.UnsupportedMediaType)
    async def unsupported_media_type_handler(
        request: Request, exc: exceptions.UnsupportedMediaType
    ):
        code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.UnprocessableEntity)
    async def unprocessable_entity_handler(request: Request, exc: Exception):
        code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.Locked)
    async def locked_handler(request: Request, exc: exceptions.Locked):
        code = status.HTTP_423_LOCKED
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.TooManyRequests)
    async def too_many_requests_handler(request: Request, exc: exceptions.TooManyRequests):
        code = status.HTTP_429_TOO_MANY_REQUESTS
        return _manage_exception(request, exc, code)

    @app.exception_handler(ValueError)
    @app.exception_handler(exceptions.InternalServerError)
    @app.exception_handler(OperationalError)
    @app.exception_handler(ProgrammingError)
    @app.exception_handler(IntegrityError)
    async def internal_server_error_handler(request: Request, exc: Exception):
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.NotImplemented)
    async def not_implemented_handler(request: Request, exc: exceptions.NotImplemented):
        code = status.HTTP_501_NOT_IMPLEMENTED
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.BadGateway)
    async def bad_gateway_handler(request: Request, exc: exceptions.BadGateway):
        code = status.HTTP_502_BAD_GATEWAY
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.ServiceUnavailable)
    async def service_unavailable_handler(request: Request, exc: exceptions.ServiceUnavailable):
        code = status.HTTP_503_SERVICE_UNAVAILABLE
        return _manage_exception(request, exc, code)

    @app.exception_handler(exceptions.GatewayTimeout)
    async def gateway_timeout_handler(request: Request, exc: exceptions.GatewayTimeout):
        code = status.HTTP_504_GATEWAY_TIMEOUT
        return _manage_exception(request, exc, code)
