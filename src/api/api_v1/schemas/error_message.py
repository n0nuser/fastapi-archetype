"""This module contains the data models for error messages."""
from pydantic import BaseModel, Field


class ErrorMessageData(BaseModel):
    """A data model representing an error message.

    Attributes:
        code (str): The code of the error message.
        message (str): The message of the error message.
        error_type (str): The type of the error message.
        description (str | None): The description of the error message (optional).
    """

    code: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=500)
    error_type: str = Field()
    description: str | None = Field(default=None, min_length=1, max_length=500)


class ErrorMessage(BaseModel):
    """A data model representing an error message.

    Attributes:
        messages (list[ErrorMessageData] | None): The list of error message data objects (optional).
    """

    messages: list[ErrorMessageData] | None = Field(default=None)


ErrorMessageData.model_rebuild()
ErrorMessage.model_rebuild()
