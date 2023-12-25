from typing import Optional

from pydantic import BaseModel, Field

from src.api.schemas.error_message_data import ErrorMessageData


class ErrorMessage(BaseModel):
    """ErrorMessage - A model defined in OpenAPI

    messages: The messages of this ErrorMessage [Optional].
    """

    messages: Optional[list[ErrorMessageData]] = Field(alias="messages", default=None)


ErrorMessage.update_forward_refs()
