"""This module contains the exceptions for the service layer."""


class BaseExceptionError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str = "An error occurred."):
        self.message = message

    def __str__(self):
        return repr(self.message)


class CustomerServiceError(BaseExceptionError):
    """Base class for exceptions in the Customer service."""
