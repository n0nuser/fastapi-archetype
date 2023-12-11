# coding: utf-8

from typing import Optional

from pydantic import BaseModel, Field, validator


class PostExamplesRequest(BaseModel):
    """
    PostExamplesRequest - a model defined in OpenAPI

        value1: The value1 of this PostExamplesRequest.
        value2: The value2 of this PostExamplesRequest [Optional].
    """

    value1: str = Field(alias="value1")
    value2: Optional[int] = Field(alias="value2", default=None)

    @validator("value1")
    def value1_min_length(cls, value):
        if value is not None:
            assert len(value) >= 1
        return value

    @validator("value1")
    def value1_max_length(cls, value):
        if value is not None:
            assert len(value) <= 15
        return value

    @validator("value2")
    def value2_max(cls, value):
        if value is not None:
            assert value <= 50
        return value

    @validator("value2")
    def value2_min(cls, value):
        if value is not None:
            assert value >= 0
        return value


PostExamplesRequest.update_forward_refs()
