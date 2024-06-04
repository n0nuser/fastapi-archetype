import logging
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
from src.repository.exceptions import ElementNotFoundError
from src.repository.models.customer import Address, Customer
from src.service.exceptions import CustomerServiceError

logger = logging.getLogger(__name__)


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
        logger.info("Entering...")
        try:
            logger.info("Deleting customer.")
            db_customer = customer_crud.get_by_id(db_connection, customer_id)
            customer_crud.delete_row(db_connection, db_customer)
        except ElementNotFoundError:
            logger.error("Customer not found.")  # noqa: TRY400
            raise
        except Exception as error:
            logger.exception("An error occurred while deleting the customer.")
            raise CustomerServiceError from error
        finally:
            logger.info("Exiting...")

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
        logger.info("Entering...")
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
            logger.debug("Filters: %s", filters)

            db_data = customer_crud.get_list(
                db_connection,
                offset,
                limit,
                filters,
                join_fields=relationships,
            )
            logger.debug("Data retrieved: %s", db_data)
            response_data = [
                CustomerListDataResponse(
                    customerId=str(row.id),
                    name=row.name,
                )
                for row in db_data
            ]
            logger.debug("Response data: %s", response_data)
            db_count = customer_crud.count(db_connection, filters)
            logger.debug("Total count: %s", db_count)
        except ElementNotFoundError:
            logger.error("No customers found.")  # noqa: TRY400
            return [], 0
        except Exception as error:
            logger.exception("An error occurred while retrieving the customers.")
            raise CustomerServiceError from error
        else:
            return response_data, db_count
        finally:
            logger.info("Exiting...")

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
        logger.info("Entering...")
        try:
            logger.debug("Customer ID: %s", customer_id)
            db_data = customer_crud.get_by_id(db_connection, customer_id)
            logger.debug("Data retrieved: %s", db_data)
            api_data = CustomerDetailResponse(
                customerId=str(db_data.id),
                name=db_data.name,
                addresses=[
                    AddressResponse(
                        addressId=str(address.id),
                        street=address.street,
                        city=address.city,
                        country=address.country,
                        postalCode=address.postal_code,
                    )
                    for address in db_data.addresses
                ],
            )
            logger.debug("Response data: %s", api_data)
        except ElementNotFoundError:
            logger.error("Customer not found.")  # noqa: TRY400
            raise
        except Exception as error:
            logger.exception("An error occurred while retrieving the customer.")
            raise CustomerServiceError from error
        else:
            return api_data
        finally:
            logger.info("Exiting...")

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
        logger.info("Entering...")
        try:
            db_customer = Customer(name=customer.name)
            customer_crud.create(db_connection, db_customer)
            logger.debug("Customer created: %s", db_customer)
            for address in customer.addresses:
                db_address = Address(
                    customer_id=db_customer.id,
                    street=address.street,
                    city=address.city,
                    country=address.country,
                    postal_code=address.postalCode,
                )
                address_crud.create(db_connection, db_address)
                logger.debug("Address created: %s", db_address)
        except Exception as error:
            logger.exception("An error occurred while creating the customer.")
            raise CustomerServiceError from error
        else:
            return UUID(str(db_customer.id))
        finally:
            logger.info("Exiting...")

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
        logger.info("Entering...")
        try:
            db_customer = customer_crud.get_by_id(db_connection, customer_id)
            logger.debug("Customer retrieved: %s", db_customer)
            if customer.name:
                db_customer.name = customer.name
                customer_crud.update(db_connection, db_customer)
                logger.debug("Customer updated: %s", db_customer)
        except ElementNotFoundError:
            logger.error("Customer not found.")  # noqa: TRY400
            raise
        except Exception as error:
            logger.exception("An error occurred while updating the customer.")
            raise CustomerServiceError from error
        finally:
            logger.info("Exiting...")

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
        logger.info("Entering...")
        try:
            # Check if Customer Exists
            customer_crud.get_by_id(db_connection, customer_id)
            logger.debug("Customer ID: %s", customer_id)

            db_address = Address(
                customer_id=customer_id,
                street=address.street,
                city=address.city,
                country=address.country,
                postal_code=address.postalCode,
            )
            db_address = address_crud.create(db_connection, db_address)
            logger.debug("Address created: %s", db_address)
        except ElementNotFoundError:
            logger.error("Customer not found.")  # noqa: TRY400
            raise
        except Exception as error:
            logger.exception("An error occurred while creating the address.")
            raise CustomerServiceError from error
        else:
            return UUID(str(db_address.id))
        finally:
            logger.info("Exiting...")

    @staticmethod
    def put_address(
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
        logger.info("Entering...")
        try:
            filters = [
                Filter(field="customer_id", operator="eq", value=str(customer_id)),
                Filter(field="id", operator="eq", value=str(address_id)),
            ]
            logger.debug("Filters: %s", filters)
            db_address = address_crud.get_one_by_fields(db_connection, filters)
            logger.debug("Address retrieved: %s", db_address)
            db_address.street = address.street
            db_address.city = address.city
            db_address.country = address.country
            db_address.postal_code = address.postalCode
            address_crud.update(db_connection, db_address)
            logger.debug("Address updated: %s", db_address)
        except ElementNotFoundError:
            logger.error("Address not found.")  # noqa: TRY400
            raise
        except Exception as error:
            logger.exception("An error occurred while updating the address.")
            raise CustomerServiceError from error
        finally:
            logger.info("Exiting...")

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
        logger.info("Entering...")
        try:
            filters = [
                Filter(field="customer_id", operator="eq", value=str(customer_id)),
                Filter(field="id", operator="eq", value=str(address_id)),
            ]
            logger.debug("Filters: %s", filters)
            db_address = address_crud.get_one_by_fields(db_connection, filters)
            logger.debug("Address retrieved: %s", db_address)
            address_crud.delete_row(db_connection, db_address)
            logger.debug("Address deleted: %s", db_address)
        except ElementNotFoundError:
            logger.error("Address not found.")  # noqa: TRY400
            raise
        except Exception as error:
            logger.exception("An error occurred while deleting the address.")
            raise CustomerServiceError from error
        finally:
            logger.info("Exiting...")
