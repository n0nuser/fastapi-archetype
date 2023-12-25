from src.api.responses import exceptions

EXCEPTION_MAPPER = {
    400: exceptions.BadRequest,
    401: exceptions.Unauthorized,
    403: exceptions.Forbidden,
    404: exceptions.NotFound,
    405: exceptions.MethodNotAllowed,
    406: exceptions.NotAcceptable,
    409: exceptions.Conflict,
    413: exceptions.PayloadTooLarge,
    414: exceptions.URITooLong,
    415: exceptions.UnsupportedMediaType,
    422: exceptions.UnprocessableEntity,
    423: exceptions.Locked,
    429: exceptions.TooManyRequests,
    500: exceptions.InternalServerError,
    501: exceptions.NotImplemented,
    502: exceptions.BadGateway,
    503: exceptions.ServiceUnavailable,
    504: exceptions.GatewayTimeout,
}
