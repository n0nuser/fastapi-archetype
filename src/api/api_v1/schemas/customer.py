"""This module defines the response structure for an customer API endpoint."""

from pydantic import BaseModel, Field

from src.api.pagination import Pagination


class AddressBase(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str


class AddressResponse(AddressBase):
    address_id: str  # UUID


class CustomerListDataResponse(BaseModel):
    customer_id: str  # UUID
    name: str


class CustomerDetailResponse(CustomerListDataResponse):
    addresses: list[AddressResponse]


class CustomerCreate(BaseModel):
    name: str = Field(..., examples=["John Doe"])
    addresses: list[AddressBase] = Field(
        default=[],
        examples=[
            [
                {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "country": "USA",
                    "postal_code": "12345",
                },
            ],
        ],
    )


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None)


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

    data: list[CustomerListDataResponse] = Field(default=[])
    pagination: Pagination | None = Field(default=None)
