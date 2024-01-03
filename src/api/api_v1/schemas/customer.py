"""This module defines the response structure for an customer API endpoint."""
from pydantic import UUID4, BaseModel, Field

from src.api.pagination import Pagination


class AddressBase(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str


class AddressResponse(AddressBase):
    id: UUID4

    class Config:
        orm_mode = True


class CustomerListDataResponse(BaseModel):
    id: UUID4
    name: str
    addresses: list[AddressResponse]


class CustomerDetailResponse(CustomerListDataResponse):
    class Config:
        orm_mode = True


class CustomerCreate(BaseModel):
    name: str
    addresses: list[AddressBase] = []


class CustomerUpdate(BaseModel):
    name: str | None = None
    addresses: list[AddressBase] | None = None


class CustomerListResponse(BaseModel):
    """Model for the response of an customer API endpoint.

    This class represents the structure of the response returned by an customer API endpoint.
    It includes a 'data' attribute, which is a list of `CustomerListData` objects,
    and a 'pagination' attribute, which is a `Pagination` object.

    Attributes:
        data (list[CustomerListData] | None): The data returned by the endpoint.
            This is a list of `CustomerListData` objects. If no data is returned,
            this is None.
        pagination (Pagination | None): The pagination information for the data.
            If no pagination information is provided, this is None.
    """

    data: list[CustomerListDataResponse] | None = Field(default=None)
    pagination: Pagination | None = Field(default=None)
