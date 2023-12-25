from typing import Optional

from pydantic import BaseModel, Field

from src.api.schemas.example_response_data_inner import \
    ExampleResponseDataInner
from src.api.schemas.pagination import Pagination


class ExampleResponse(BaseModel):
    """ExampleResponse - a model defined in OpenAPI

    data: The data of this ExampleResponse [Optional].
    pagination: The pagination of this ExampleResponse [Optional].
    """

    data: Optional[list[ExampleResponseDataInner]] = Field(alias="data", default=None)
    pagination: Optional[Pagination] = Field(alias="pagination", default=None)


ExampleResponse.model_rebuild()
