"""This module defines the response structure for an customer API endpoint."""

from pydantic import BaseModel, Field

from src.controller.utils.pagination import Pagination


class AddressBase(BaseModel):
    """Model for the address of a customer."""

    street: str = Field(..., examples=["123 Main St"])
    city: str = Field(..., examples=["Anytown"])
    country: str = Field(..., examples=["USA"])
    postalCode: str = Field(..., examples=["12345"])


class AddressResponse(AddressBase):
    """Model for the response of an address API endpoint."""

    addressId: str = Field(..., examples=["a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"])


class CustomerListDataResponse(BaseModel):
    """Model for the data returned by an customer API endpoint."""

    customerId: str = Field(..., examples=["a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"])
    name: str = Field(..., examples=["John Doe"])


class CustomerDetailResponse(CustomerListDataResponse):
    """Model for the response of an customer API endpoint."""

    addresses: list[AddressResponse] = Field(
        examples=[
            [
                {
                    "address_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                    "street": "123 Main St",
                    "city": "Anytown",
                    "country": "USA",
                    "postal_code": "12345",
                },
            ],
        ],
    )


class CustomerCreate(BaseModel):
    """Model for creating a new customer."""

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
    """Model for updating a customer."""

    name: str | None = Field(default=None, examples=["John Doe"])


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
