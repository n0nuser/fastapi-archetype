"""Maps HTTP status codes to their corresponding exception classes."""

from src.controller.errors import exceptions

EXCEPTION_MAPPER = {
    400: exceptions.HTTP400BadRequestError,
    401: exceptions.HTTP401UnauthorizedError,
    403: exceptions.HTTP403ForbiddenError,
    404: exceptions.HTTP404NotFoundError,
    405: exceptions.HTTP405MethodNotAllowedError,
    406: exceptions.HTTP406NotAcceptableError,
    409: exceptions.HTTP409ConflictError,
    413: exceptions.HTTP413PayloadTooLargeError,
    414: exceptions.HTTP414URITooLongError,
    415: exceptions.HTTP415UnsupportedMediaTypeError,
    422: exceptions.HTTP422UnprocessableEntityError,
    423: exceptions.HTTP423LockedError,
    429: exceptions.HTTP429TooManyRequestsError,
    500: exceptions.HTTP500InternalServerError,
    501: exceptions.HTTP501NotImplementedError,
    502: exceptions.HTTP502BadGatewayError,
    503: exceptions.HTTP503ServiceUnavailableError,
    504: exceptions.HTTP504GatewayTimeoutError,
}
