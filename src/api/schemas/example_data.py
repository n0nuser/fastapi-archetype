from typing import Optional

from pydantic import BaseModel, Field

from src.api.schemas.example_data_data import ExampleDataData


class ExampleData(BaseModel):
    """ExampleData - a model defined in OpenAPI

    data: The data of this ExampleData [Optional].
    """

    data: Optional[ExampleDataData] = Field(alias="data", default=None)


ExampleData.model_rebuild()
