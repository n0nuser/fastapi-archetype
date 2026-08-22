"""Exceptions raised by the CRUD operations."""

__all__ = ["BaseExceptionError", "ElementNotFoundError"]


class BaseExceptionError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str = "An error occurred.") -> None:
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)


class ElementNotFoundError(BaseExceptionError):
    """Raised when an element is not found in the database."""
