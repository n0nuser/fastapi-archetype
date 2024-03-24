class BaseExceptionError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str = "An error occurred."):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ElementNotFoundError(BaseExceptionError):
    """Raised when an element is not found in the database."""


class DatabaseConnectionError(BaseExceptionError):
    """Raised when a database connection error occurs."""
