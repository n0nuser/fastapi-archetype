from src.api.schemas.error_message import ErrorMessage
from src.api.schemas.error_message_messages_inner import ErrorMessageData

ERROR_RESPONSES = {
    400: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="BAD_REQUEST",
                type="FATAL",
                message="Bad Request",
                description="The request is incorrect because the selected parameters are wrong or a functional error has occurred.",
            ),
        ],
    ),
    401: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="UNAUTHORIZED",
                type="ERROR",
                message="Unauthorized",
                description="The call needs some kind of authorization either expired or not reported.",
            ),
        ],
    ),
    403: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="FORBIDDEN",
                type="FATAL",
                message="Forbidden",
                description="You do not have permissions to operate with this invocation.",
            ),
        ],
    ),
    404: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="NOT_FOUND",
                type="FATAL",
                message="Not Found",
                description="Resource not found.",
            ),
        ],
    ),
    405: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="METHOD_NOT_ALLOWED",
                type="ERROR",
                message="Method not allowed",
                description="The request method is known by the server but is not supported by the target resource.",
            ),
        ],
    ),
    406: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="NOT_ACCEPTABLE",
                type="FATAL",
                message="Not Acceptable",
                description='The format indicated in the "Accept" header of the request is not supported by the destination server.',
            ),
        ],
    ),
    409: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="CONFLICT",
                type="FATAL",
                message="Conflict",
                description="The request has not been completed due to a conflict with the current status of the resource.",
            ),
        ],
    ),
    413: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="PAYLOAD_TOO_LARGE",
                type="FATAL",
                message="Payload Too Large",
                description="The size of the client request has exceeded the server's file size limit.",
            ),
        ],
    ),
    414: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="URI_TOO_LONG",
                type="ERROR",
                message="URI Too Long",
                description="The size of the client request has exceeded the server's file size limit.",
            ),
        ],
    ),
    415: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="UNSUPPORTED_MEDIA_TYPE",
                type="FATAL",
                message="Unsupported Media Type",
                description='Incorrect format of the response, does not match the one indicated in the "Content-Type" header.',
            ),
        ],
    ),
    422: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="UNPROCESSABLE_ENTITY",
                type="FATAL",
                message="Unprocessable Entity",
                description="The structure of the request is correct, but it is not semantically correct.",
            ),
        ],
    ),
    423: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="LOCKED",
                type="FATAL",
                message="Locked",
                description="The resource you are trying to access is blocked.",
            ),
        ],
    ),
    429: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="TOO_MANY_REQUESTS",
                type="ERROR",
                message="Too Many Requests",
                description="Too many requests in a given period of time and limit has been exceeded.",
            ),
        ],
    ),
    500: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="INTERNAL_SERVER_ERROR",
                type="FATAL",
                message="Internal server error",
                description="Unexpected error from the server, it has no way to respond to the invocation.",
            ),
        ],
        description="Internal Server Error.",
    ),
    501: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="NOT_IMPLEMENTED",
                type="ERROR",
                message="Not implemented",
                description="The functionality is not supported by the service.",
            ),
        ],
    ),
    502: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="BAD_GATEWAY",
                type="ERROR",
                message="Bad Gateway",
                description="Indicates that the server, while acting as a gateway or proxy, received an invalid response from an inbound service that it accessed while attempting to fulfill the request.",
            ),
        ],
    ),
    503: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="SERVICE_UNAVAILABLE",
                type="ERROR",
                message="Service unavailable",
                description="Indicates that the server is unavailable to perform the request because it is overloaded or maintenance is being performed, and that it will probably be relieved after some time.",
            ),
        ],
    ),
    504: ErrorMessage(
        messages=[
            ErrorMessageData(
                code="GATEWAY_TIMEOUT",
                type="ERROR",
                message="Gateway timeout",
                description="Indicates that the server, while acting as a gateway or proxy, did not receive a timely response from an upstream server it needed to access to complete the request.",
            ),
        ],
    ),
}
