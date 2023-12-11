# coding: utf-8

from typing import Optional

from pydantic import BaseModel, Field, validator


class ExampleDataData(BaseModel):
    """
    ExampleDataData - a model defined in OpenAPI

        exampleId: The exampleId of this ExampleDataData.
        value1: Info of this ExampleDataData [Optional].
        value2: Info of this ExampleDataData.
    """

    exampleId: int = Field(alias="exampleId")
    value1: Optional[str] = Field(alias="value1", default=None)
    value2: Optional[int] = Field(alias="value2", default=None)

    @validator("exampleId")
    def exampleId_min(cls, value):
        assert value >= 1
        return value

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


ExampleDataData.model_rebuild()
