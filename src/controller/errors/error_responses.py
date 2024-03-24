"""This module defines standard error responses for HTTP status codes.

It provides a dictionary `ERROR_RESPONSES` that maps HTTP status codes to `ErrorMessage` objects.
Each `ErrorMessage` object contains a list of `ErrorMessageData`
objects that provide details about the error.
"""

from src.controller.api.schemas.error_message import ErrorMessage, ErrorMessageData

ERROR_RESPONSES = {
    400: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="BAD_REQUEST",
                error_type="FATAL",
                message="Bad Request",
                description="The request is incorrect because the selected parameters are"  # noqa: ISC003
                + " wrong or a functional error has occurred.",
            ),
        ],
    ),
    401: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="UNAUTHORIZED",
                error_type="ERROR",
                message="Unauthorized",
                description="The call needs some kind of authorization"  # noqa: ISC003
                + " either expired or not reported.",
            ),
        ],
    ),
    403: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="FORBIDDEN",
                error_type="FATAL",
                message="Forbidden",
                description="You do not have permissions to operate with this invocation.",
            ),
        ],
    ),
    404: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="NOT_FOUND",
                error_type="FATAL",
                message="Not Found",
                description="Resource not found.",
            ),
        ],
    ),
    405: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="METHOD_NOT_ALLOWED",
                error_type="ERROR",
                message="Method not allowed",
                description="The request method is known by the server but"  # noqa: ISC003
                + " is not supported by the target resource.",
            ),
        ],
    ),
    406: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="NOT_ACCEPTABLE",
                error_type="FATAL",
                message="Not Acceptable",
                description='The format indicated in the "Accept" header of'  # noqa: ISC003
                + " the request is not supported by the destination server.",
            ),
        ],
    ),
    409: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="CONFLICT",
                error_type="FATAL",
                message="Conflict",
                description="The request has not been completed due to a"  # noqa: ISC003
                + " conflict with the current status of the resource.",
            ),
        ],
    ),
    413: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="PAYLOAD_TOO_LARGE",
                error_type="FATAL",
                message="Payload Too Large",
                description="The size of the client request has exceeded"  # noqa: ISC003
                + " the server's file size limit.",
            ),
        ],
    ),
    414: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="URI_TOO_LONG",
                error_type="ERROR",
                message="URI Too Long",
                description="The size of the client request has exceeded"  # noqa: ISC003
                + " the server's file size limit.",
            ),
        ],
    ),
    415: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="UNSUPPORTED_MEDIA_TYPE",
                error_type="FATAL",
                message="Unsupported Media Type",
                description="Incorrect format of the response, does not"  # noqa: ISC003
                + ' match the one indicated in the "Content-Type" header.',
            ),
        ],
    ),
    422: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="UNPROCESSABLE_ENTITY",
                error_type="FATAL",
                message="Unprocessable Entity",
                description="The structure of the request is correct,"  # noqa: ISC003
                + " but it is not semantically correct.",
            ),
        ],
    ),
    423: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="LOCKED",
                error_type="FATAL",
                message="Locked",
                description="The resource you are trying to access is blocked.",
            ),
        ],
    ),
    429: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="TOO_MANY_REQUESTS",
                error_type="ERROR",
                message="Too Many Requests",
                description="Too many requests in a given period of time"  # noqa: ISC003
                + " and limit has been exceeded.",
            ),
        ],
    ),
    500: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="INTERNAL_SERVER_ERROR",
                error_type="FATAL",
                message="Internal server error",
                description="Unexpected error from the server, "  # noqa: ISC003
                + "it has no way to respond to the invocation.",
            ),
        ],
    ),
    501: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="NOT_IMPLEMENTED",
                error_type="ERROR",
                message="Not implemented",
                description="The functionality is not supported by the service.",
            ),
        ],
    ),
    502: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="BAD_GATEWAY",
                error_type="ERROR",
                message="Bad Gateway",
                description="Indicates that the server, while acting as a gateway or proxy,"  # noqa: ISC003
                + " received an invalid response from an inbound service "
                + "that it accessed while attempting to fulfill the request.",
            ),
        ],
    ),
    503: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="SERVICE_UNAVAILABLE",
                error_type="ERROR",
                message="Service unavailable",
                description="Indicates that the server is unavailable to perform the"  # noqa: ISC003
                + " request because it is overloaded or maintenance is being performed,"
                + " and that it will probably be relieved after some time.",
            ),
        ],
    ),
    504: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="GATEWAY_TIMEOUT",
                error_type="ERROR",
                message="Gateway timeout",
                description="Indicates that the server, while acting as a gateway or"  # noqa: ISC003
                + " proxy, did not receive a timely response from an upstream server "
                + "it needed to access to complete the request.",
            ),
        ],
    ),
}
