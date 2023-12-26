from typing import Optional

from pydantic import BaseModel, Field, validator


class ExampleResponseDataInner(BaseModel):
    """ExampleResponseDataInner - a model defined in OpenAPI

    exampleId: The exampleId of this ExampleResponseDataInner.
    value1: Info of this ExampleResponseDataInner [Optional].
    """

    exampleId: int = Field(alias="exampleId")
    value1: Optional[str] = Field(alias="value1", default=None)

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
            assert len(value) <= 50
        return value


ExampleResponseDataInner.model_rebuild()
