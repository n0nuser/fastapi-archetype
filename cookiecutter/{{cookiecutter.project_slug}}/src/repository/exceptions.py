"""Repository exceptions.

`ElementNotFoundError` is raised by the shared CRUD library and re-exported
here for convenience; `DatabaseConnectionError` is application-specific.
"""

from fastapi_crud_base.exceptions import BaseExceptionError, ElementNotFoundError

__all__ = ["BaseExceptionError", "DatabaseConnectionError", "ElementNotFoundError"]


class DatabaseConnectionError(BaseExceptionError):
    """Raised when a database connection error occurs."""
