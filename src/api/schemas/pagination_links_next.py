# coding: utf-8

import re
from typing import Optional

from pydantic import BaseModel, Field, validator


class PaginationLinksNext(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    PaginationLinksNext - a model defined in OpenAPI

        href: The href of this PaginationLinksNext [Optional].
    """

    href: Optional[str] = Field(alias="href", default=None)

    @validator("href")
    def href_pattern(cls, value):
        if value is not None:
            assert re.match(
                r"^(https?://)?([\w.-]+)(:[0-9]+)?(/[a-zA-Z0-9/-]*)?(\?[\w=&]*)?$", value
            )
        return value


PaginationLinksNext.update_forward_refs()
