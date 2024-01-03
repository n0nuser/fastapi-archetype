"""This module contains the data models for error messages."""
from pydantic import BaseModel, Field, field_validator


class ErrorMessageData(BaseModel):
    """A data model representing an error message.

    Attributes:
        code (str): The code of the error message.
        message (str): The message of the error message.
        error_type (str): The type of the error message.
        description (str | None): The description of the error message (optional).
    """

    code: str = Field()
    message: str = Field()
    error_type: str = Field()
    description: str | None = Field(default=None)

    @field_validator("code")
    @classmethod
    def code_length(cls: type["ErrorMessageData"], value: str) -> str:
        """Validates values of the model."""
        max_value = 50
        min_value = 1
        if value and (len(value) > max_value or len(value) < min_value):
            error_message = f"Characters must be more than {min_value} or less than {max_value}."
            raise ValueError(error_message)
        return value

    @field_validator("message", "description")
    @classmethod
    def message_description_length(cls: type["ErrorMessageData"], value: str | None) -> str | None:
        """Validates values of the model."""
        max_value = 500
        min_value = 1
        if value and (len(value) > max_value or len(value) < min_value):
            error_message = f"Characters must be more than {min_value} or less than {max_value}."
            raise ValueError(error_message)
        return value


class ErrorMessage(BaseModel):
    """A data model representing an error message.

    Attributes:
        messages (list[ErrorMessageData] | None): The list of error message data objects (optional).
    """

    messages: list[ErrorMessageData] | None = Field(default=None)


ErrorMessageData.model_rebuild()
ErrorMessage.model_rebuild()
