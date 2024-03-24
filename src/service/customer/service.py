from uuid import UUID

from pydantic import UUID4
from sqlalchemy.orm import Session

from src.controller.api.schemas.customer import (
    AddressBase,
    AddressResponse,
    CustomerCreate,
    CustomerDetailResponse,
    CustomerListDataResponse,
    CustomerUpdate,
)
from src.repository.crud.address import address_crud
from src.repository.crud.base import Filter
from src.repository.crud.customer import customer_crud
from src.repository.exceptions import ElementNotFound
from src.repository.models.customer import Address, Customer
from src.service.exceptions import CustomerServiceError


class CustomerApplicationService:
    """Defines the application service for the customer domain."""

    @staticmethod
    def delete_customer(db_connection: Session, customer_id: UUID4) -> None:
        """Deletes a customer from the database.

        Args:
            db_connection (Session): Database connection.
            customer_id (UUID4): Customer ID.

        Raises:
            CustomerServiceException: If an error occurs while deleting the customer.
        """
        try:
            db_customer = customer_crud.get_by_id(db_connection, customer_id)
            customer_crud.delete_row(db_connection, db_customer)
        except ElementNotFound:
            raise
        except Exception as error:
            raise CustomerServiceError from error

    @staticmethod
    def get_customers(
        db_connection: Session,
        limit: int,
        offset: int,
        street: str | None,
        city: str | None,
        country: str | None,
        postal_code: str | None,
    ) -> tuple[list[CustomerListDataResponse], int]:
        """Retrieves a list of customers from the database.

        Args:
            db_connection (Session): Database connection.
            limit (int): Limit of elements per page.
            offset (int): Offset of elements per page.
            street (str | None): Street name.
            city (str | None): City name.
            country (str | None): Country name.
            postal_code (str | None): Postal code.

        Raises:
            CustomerServiceException: If an error occurs while retrieving the customers.

        Returns:
            tuple[list[CustomerListDataResponse], int]: A tuple containing the list of customers
                and the total count.
        """
        try:
            filters = []
            if street:
                filters.append(Filter(field="addresses.street", operator="contains", value=street))
            if city:
                filters.append(Filter(field="addresses.city", operator="contains", value=city))
            if country:
                filters.append(
                    Filter(field="addresses.country", operator="contains", value=country),
                )
            if postal_code:
                filters.append(
                    Filter(field="addresses.postal_code", operator="eq", value=postal_code),
                )
            relationships = ["addresses"]

            db_data = customer_crud.get_list(
                db_connection,
                offset,
                limit,
                filters,
                join_fields=relationships,
            )
            response_data = [
                CustomerListDataResponse(
                    customer_id=str(row.id),
                    name=row.name,
                )
                for row in db_data
            ]
            db_count = customer_crud.count(db_connection, filters)
        except ElementNotFound:
            return [], 0
        except Exception as error:
            raise CustomerServiceError from error
        else:
            return response_data, db_count

    @staticmethod
    def get_customer_id(db_connection: Session, customer_id: UUID4) -> CustomerDetailResponse:
        """Retrieves a customer by ID from the database.

        Args:
            db_connection (Session): Database connection.
            customer_id (UUID4): Customer ID.

        Raises:
            CustomerServiceException: If an error occurs while retrieving the customer.

        Returns:
            CustomerDetailResponse: Response data of the customer.
        """
        try:
            db_data = customer_crud.get_by_id(db_connection, customer_id)
            api_data = CustomerDetailResponse(
                customer_id=str(db_data.id),
                name=db_data.name,
                addresses=[
                    AddressResponse(
                        address_id=str(address.id),
                        street=address.street,
                        city=address.city,
                        country=address.country,
                        postal_code=address.postal_code,
                    )
                    for address in db_data.addresses
                ],
            )
        except ElementNotFound:
            raise
        except Exception as error:
            raise CustomerServiceError from error
        else:
            return api_data

    @staticmethod
    def post_customer(db_connection: Session, customer: CustomerCreate) -> UUID:
        """Creates a new customer in the database.

        Args:
            db_connection (Session): Database connection.
            customer (CustomerCreate): Customer data.

        Raises:
            CustomerServiceException: If an error occurs while creating the customer.

        Returns:
            UUID: Customer ID.
        """
        try:
            db_customer = Customer(name=customer.name)
            customer_crud.create(db_connection, db_customer)
            for address in customer.addresses:
                db_address = Address(
                    customer_id=db_customer.id,
                    street=address.street,
                    city=address.city,
                    country=address.country,
                    postal_code=address.postal_code,
                )
                address_crud.create(db_connection, db_address)
        except Exception as error:
            raise CustomerServiceError from error
        else:
            return UUID(str(db_customer.id))

    @staticmethod
    def put_customers(db_connection: Session, customer_id: UUID4, customer: CustomerUpdate) -> None:
        """Updates a customer in the database.

        Args:
            db_connection (Session): Database connection.
            customer_id (UUID4): Customer ID.
            customer (CustomerUpdate): Customer data.

        Raises:
            CustomerServiceException: If an error occurs while updating the customer.
        """
        try:
            db_customer = customer_crud.get_by_id(db_connection, customer_id)
            if customer.name:
                db_customer.name = customer.name
                customer_crud.update(db_connection, db_customer)
        except ElementNotFound:
            raise
        except Exception as error:
            raise CustomerServiceError from error

    @staticmethod
    def post_address(db_connection: Session, customer_id: UUID4, address: AddressBase) -> UUID:
        """Creates a new address for a customer in the database.

        Args:
            db_connection (Session): Database connection.
            customer_id (UUID4): Customer ID.
            address (AddressBase): Address data.

        Raises:
            CustomerServiceException: If an error occurs while creating the address.

        Returns:
            UUID: Address ID.
        """
        try:
            # Check if Customer Exists
            customer_crud.get_by_id(db_connection, customer_id)

            db_address = Address(
                customer_id=customer_id,
                street=address.street,
                city=address.city,
                country=address.country,
                postal_code=address.postal_code,
            )
            db_address = address_crud.create(db_connection, db_address)
        except ElementNotFound:
            raise
        except Exception as error:
            raise CustomerServiceError from error
        else:
            return UUID(str(db_address.id))

    @staticmethod
    def put_adress(
        db_connection: Session,
        customer_id: UUID4,
        address_id: UUID4,
        address: AddressBase,
    ) -> None:
        """Updates an address for a customer in the database.

        Args:
            db_connection (Session): Database connection.
            customer_id (UUID4): Customer ID.
            address_id (UUID4): Address ID.
            address (AddressBase): Address data.

        Raises:
            CustomerServiceException: If an error occurs while updating the address.
        """
        try:
            filters = [
                Filter(field="customer_id", operator="eq", value=str(customer_id)),
                Filter(field="id", operator="eq", value=str(address_id)),
            ]
            db_address = address_crud.get_one_by_fields(db_connection, filters)
            db_address.street = address.street
            db_address.city = address.city
            db_address.country = address.country
            db_address.postal_code = address.postal_code
            address_crud.update(db_connection, db_address)
        except ElementNotFound:
            raise
        except Exception as error:
            raise CustomerServiceError from error

    @staticmethod
    def delete_address(db_connection: Session, customer_id: UUID4, address_id: UUID4) -> None:
        """Deletes an address for a customer from the database.

        Args:
            db_connection (Session): Database connection.
            customer_id (UUID4): Customer ID.
            address_id (UUID4): Address ID.

        Raises:
            CustomerServiceException: If an error occurs while deleting the address.
        """
        try:
            filters = [
                Filter(field="customer_id", operator="eq", value=str(customer_id)),
                Filter(field="id", operator="eq", value=str(address_id)),
            ]
            db_address = address_crud.get_one_by_fields(db_connection, filters)
            address_crud.delete_row(db_connection, db_address)
        except ElementNotFound:
            raise
        except Exception as error:
            raise CustomerServiceError from error
