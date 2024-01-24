"""Exceptions for the API."""


class BaseHTTPError(Exception):
    """Base HTTP error."""

    def __init__(self: "BaseHTTPError", message: str = "") -> None:
        """Initialize BaseHTTPError."""
        self.message = message
        super().__init__(self.message)

    def __str__(self: "BaseHTTPError") -> str:
        """Return string representation of the error."""
        return self.message


class HTTP400BadRequestError(BaseHTTPError):
    """Error 400."""

    def __init__(
        self: "HTTP400BadRequestError",
        message: str = "The request is incorrect because the selected parameters "  # noqa: ISC003
        + "are wrong or a functional error has occurred.",
    ) -> None:
        """Initialize HTTP400BadRequestError."""
        self.message = message
        super().__init__(self.message)


class HTTP401UnauthorizedError(BaseHTTPError):
    """Error 401."""

    def __init__(
        self: "HTTP401UnauthorizedError",
        message: str = "The call needs some kind of authorization either expired or not reported.",
    ) -> None:
        """Initialize HTTP401UnauthorizedError."""
        self.message = message
        super().__init__(self.message)


class HTTP403ForbiddenError(BaseHTTPError):
    """Error 403."""

    def __init__(
        self: "HTTP403ForbiddenError",
        message: str = "You do not have permissions to operate with this invocation.",
    ) -> None:
        """Initialize HTTP403ForbiddenError."""
        self.message = message
        super().__init__(self.message)


class HTTP404NotFoundError(BaseHTTPError):
    """Error 404."""

    def __init__(self: "HTTP404NotFoundError", message: str = "Resource not found.") -> None:
        """Initialize HTTP404NotFoundError."""
        self.message = message
        super().__init__(self.message)


class HTTP405MethodNotAllowedError(BaseHTTPError):
    """Error 405."""

    def __init__(
        self: "HTTP405MethodNotAllowedError",
        message: str = "The request method is known by the server but"  # noqa: ISC003
        + " is not supported by the target resource.",
    ) -> None:
        """Initialize HTTP405MethodNotAllowedError."""
        self.message = message
        super().__init__(self.message)


class HTTP406NotAcceptableError(BaseHTTPError):
    """Error 406."""

    def __init__(
        self: "HTTP406NotAcceptableError",
        message: str = 'The format indicated in the "Accept" header of '  # noqa: ISC003
        + "the request is not supported by the destination server.",
    ) -> None:
        """Initialize HTTP406NotAcceptableError."""
        self.message = message
        super().__init__(self.message)


class HTTP409ConflictError(BaseHTTPError):
    """Error 409."""

    def __init__(
        self: "HTTP409ConflictError",
        message: str = "The request has not been completed due to "  # noqa: ISC003
        + "a conflict with the current status of the resource.",
    ) -> None:
        """Initialize HTTP409ConflictError."""
        self.message = message
        super().__init__(self.message)


class HTTP413PayloadTooLargeError(BaseHTTPError):
    """Error 413."""

    def __init__(
        self: "HTTP413PayloadTooLargeError",
        message: str = "The size of the client request has exceeded the server's file size limit.",
    ) -> None:
        """Initialize HTTP413PayloadTooLargeError."""
        self.message = message
        super().__init__(self.message)


class HTTP414URITooLongError(BaseHTTPError):
    """Error 414."""

    def __init__(
        self: "HTTP414URITooLongError",
        message: str = "The URL of the request has exceeded the length limit.",
    ) -> None:
        """Initialize HTTP414URITooLongError."""
        self.message = message
        super().__init__(self.message)


class HTTP415UnsupportedMediaTypeError(BaseHTTPError):
    """Error 415."""

    def __init__(
        self: "HTTP415UnsupportedMediaTypeError",
        message: str = "Incorrect format of the response, does not match"  # noqa: ISC003
        + ' the one indicated in the "Content-Type" header.',
    ) -> None:
        """Initialize HTTP415UnsupportedMediaTypeError."""
        self.message = message
        super().__init__(self.message)


class HTTP429TooManyRequestsError(BaseHTTPError):
    """Error 429."""

    def __init__(
        self: "HTTP429TooManyRequestsError",
        message: str = "Too many requests in a given period of time and limit has been exceeded.",
    ) -> None:
        """Initialize HTTP429TooManyRequestsError."""
        self.message = message
        super().__init__(self.message)


class HTTP422UnprocessableEntityError(BaseHTTPError):
    """Error 422."""

    def __init__(
        self: "HTTP422UnprocessableEntityError",
        message: str = "The structure of the request is correct,"  # noqa: ISC003
        + " but it is not semantically correct.",
    ) -> None:
        """Initialize HTTP422UnprocessableEntityError."""
        self.message = message
        super().__init__(self.message)


class HTTP423LockedError(BaseHTTPError):
    """Error 423."""

    def __init__(
        self: "HTTP423LockedError",
        message: str = "The resource you are trying to access is blocked.",
    ) -> None:
        """Initialize HTTP423LockedError."""
        self.message = message
        super().__init__(self.message)


class HTTP500InternalServerError(BaseHTTPError):
    """Error 500."""

    def __init__(
        self: "HTTP500InternalServerError",
        message: str = "Unexpected error from the server,"  # noqa: ISC003
        + " it has no way to respond to the invocation.",
    ) -> None:
        """Initialize HTTP500InternalServerError."""
        self.message = message
        super().__init__(self.message)


class HTTP501NotImplementedError(BaseHTTPError):
    """Error 501."""

    def __init__(
        self: "HTTP501NotImplementedError",
        message: str = "The functionality is not supported by the service.",
    ) -> None:
        """Initialize HTTP501NotImplementedError."""
        self.message = message
        super().__init__(self.message)


class HTTP502BadGatewayError(BaseHTTPError):
    """Error 502."""

    def __init__(
        self: "HTTP502BadGatewayError",
        message: str = "Indicates that the server, while acting as a gateway or proxy,"  # noqa: ISC003
        + " received an invalid response from an inbound service that it"
        + " accessed while attempting to fulfill the request.",
    ) -> None:
        """Initialize HTTP502BadGatewayError."""
        self.message = message
        super().__init__(self.message)


class HTTP503ServiceUnavailableError(BaseHTTPError):
    """Error 503."""

    def __init__(
        self: "HTTP503ServiceUnavailableError",
        message: str = "Indicates that the server is unavailable to perform the request"  # noqa: ISC003
        + " because it is overloaded or maintenance is being performed,"
        + " and that it will probably be relieved after some time.",
    ) -> None:
        """Initialize HTTP503ServiceUnavailableError."""
        self.message = message
        super().__init__(self.message)


class HTTP504GatewayTimeoutError(BaseHTTPError):
    """Error 504."""

    def __init__(
        self: "HTTP504GatewayTimeoutError",
        message: str = "Indicates that the server, while acting as a gateway or proxy,"  # noqa: ISC003
        + " did not receive a timely response from an upstream server"
        + " it needed to access to complete the request.",
    ) -> None:
        """Initialize HTTP504GatewayTimeoutError."""
        self.message = message
        super().__init__(self.message)
