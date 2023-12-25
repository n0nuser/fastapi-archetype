from typing import Optional

from pydantic import BaseModel, Field, validator


class ErrorMessageData(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    ErrorMessageMessagesInner - a model defined in OpenAPI

        code: The code of this ErrorMessageMessagesInner.
        message: The message of this ErrorMessageMessagesInner.
        type: The type of this ErrorMessageMessagesInner.
        description: The description of this ErrorMessageMessagesInner [Optional].
    """

    code: str = Field(alias="code")
    message: str = Field(alias="message")
    type: str = Field(alias="type")
    description: Optional[str] = Field(alias="description", default=None)

    @validator("code")
    def code_min_length(cls, value):
        assert len(value) >= 1
        return value

    @validator("code")
    def code_max_length(cls, value):
        assert len(value) <= 50
        return value

    @validator("message")
    def message_min_length(cls, value):
        assert len(value) >= 1
        return value

    @validator("message")
    def message_max_length(cls, value):
        assert len(value) <= 500
        return value

    @validator("description")
    def description_min_length(cls, value):
        if value is not None:
            assert len(value) >= 1
        return value

    @validator("description")
    def description_max_length(cls, value):
        if value is not None:
            assert len(value) <= 500
        return value


ErrorMessageData.update_forward_refs()
