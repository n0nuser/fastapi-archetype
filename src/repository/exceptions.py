class BaseException(Exception):
    def __init__(self, message: str = "An error occurred."):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ElementNotFound(BaseException):
    pass


class DatabaseConnectionError(BaseException):
    pass
