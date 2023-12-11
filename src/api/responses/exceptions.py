class BadRequest(Exception):
    """Error 400"""

    def __init__(
        self,
        message="The request is incorrect because the selected parameters are wrong or a functional error has occurred.",
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class Unauthorized(Exception):
    """Error 401"""

    def __init__(
        self, message="The call needs some kind of authorization either expired or not reported."
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class Forbidden(Exception):
    """Error 403"""

    def __init__(self, message="You do not have permissions to operate with this invocation."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NotFound(Exception):
    """Error 404"""

    def __init__(self, message="Resource not found."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class MethodNotAllowed(Exception):
    """Error 405"""

    def __init__(
        self,
        message="The request method is known by the server but is not supported by the target resource.",
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NotAcceptable(Exception):
    """Error 406"""

    def __init__(
        self,
        message='The format indicated in the "Accept" header of the request is not supported by the destination server.',
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class Conflict(Exception):
    """Error 409"""

    def __init__(
        self,
        message="The request has not been completed due to a conflict with the current status of the resource.",
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class PayloadTooLarge(Exception):
    """Error 413"""

    def __init__(
        self, message="The size of the client request has exceeded the server's file size limit."
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class URITooLong(Exception):
    """Error 414"""

    def __init__(self, message="The URL of the request has exceeded the length limit."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UnsupportedMediaType(Exception):
    """Error 415"""

    def __init__(
        self,
        message='Incorrect format of the response, does not match the one indicated in the "Content-Type" header.',
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class TooManyRequests(Exception):
    """Error 429"""

    def __init__(
        self, message="Too many requests in a given period of time and limit has been exceeded."
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UnprocessableEntity(Exception):
    """Error 422"""

    def __init__(
        self, message="The structure of the request is correct, but it is not semantically correct."
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class Locked(Exception):
    """Error 423"""

    def __init__(self, message="The resource you are trying to access is blocked."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InternalServerError(Exception):
    """Error 500"""

    def __init__(
        self,
        message="Unexpected error from the server, it has no way to respond to the invocation.",
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NotImplemented(Exception):
    """Error 501"""

    def __init__(self, message="The functionality is not supported by the service."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class BadGateway(Exception):
    """Error 502"""

    def __init__(
        self,
        message="Indicates that the server, while acting as a gateway or proxy, received an invalid response from an inbound service that it accessed while attempting to fulfill the request.",
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ServiceUnavailable(Exception):
    """Error 503"""

    def __init__(
        self,
        message="Indicates that the server is unavailable to perform the request because it is overloaded or maintenance is being performed, and that it will probably be relieved after some time.",
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class GatewayTimeout(Exception):
    """Error 504"""

    def __init__(
        self,
        message="Indicates that the server, while acting as a gateway or proxy, did not receive a timely response from an upstream server it needed to access to complete the request.",
    ):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
