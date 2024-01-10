from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, Path, Query, Request, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from src.api.api_v1.schemas.customer import (
    AddressBase,
    AddressResponse,
    CustomerCreate,
    CustomerDetailResponse,
    CustomerListDataResponse,
    CustomerListResponse,
    CustomerUpdate,
)
from src.api.api_v1.schemas.error_message import ErrorMessage
from src.api.errors.exceptions import HTTP404NotFoundError, HTTP500InternalServerError
from src.api.pagination import Pagination
from src.db.crud.address import address_crud
from src.db.crud.base import Filter
from src.db.crud.customer import customer_crud
from src.db.models.customer import Address as AddressDBModel
from src.db.models.customer import Customer as CustomerDBModel
from src.db.session import get_db_session

router = APIRouter()


@router.delete(
    "/customers/{customer_id}",
    responses={
        204: {"description": "No Content."},
        400: {"model": ErrorMessage, "description": "Bad Request."},
        401: {"model": ErrorMessage, "description": "Unauthorized."},
        403: {"model": ErrorMessage, "description": "Forbidden."},
        404: {"model": ErrorMessage, "description": "Not Found."},
        405: {"model": ErrorMessage, "description": "Method Not Allowed."},
        406: {"model": ErrorMessage, "description": "Not Acceptable."},
        409: {"model": ErrorMessage, "description": "Conflict."},
        413: {"model": ErrorMessage, "description": "Payload Too Large."},
        414: {"model": ErrorMessage, "description": "URI Too Long."},
        422: {"model": ErrorMessage, "description": "Unprocessable Entity."},
        423: {"model": ErrorMessage, "description": "Locked."},
        429: {"model": ErrorMessage, "description": "Too Many Requests."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
        501: {"model": ErrorMessage, "description": "Not Implemented."},
        502: {"model": ErrorMessage, "description": "Bad Gateway."},
        503: {"model": ErrorMessage, "description": "Service Unavailable."},
        504: {"model": ErrorMessage, "description": "Gateway Timeout."},
    },
    tags=["Customers"],
    summary="Delete specific customer.",
    response_model=None,
)
async def delete_customer_id(
    accept_language: Annotated[
        str,
        Header(
            ...,
            description="ISO code of the language that the client accepts in response from the server.",
            regex=r"^[a-z]{2}-[A-Z]{2}$",
            min_length=1,
            max_length=6,
        ),
    ],
    x_request_id: Annotated[
        str,
        Header(
            ...,
            description="Request ID.",
            regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
            min_length=1,
        ),
    ],
    customer_id: Annotated[int, Path(description="Id of a specific customer.", ge=1)],
    db: Session = Depends(get_db_session),
) -> Response:
    """Delete the information of the customer with the matching Id."""
    try:
        db_customer = customer_crud.get_by_id(db, customer_id)
        if not db_customer:
            raise HTTP404NotFoundError
        customer_crud.delete_row(db, db_customer)
        headers = {
            "X-Request-ID": x_request_id,
        }
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)
    except Exception as error:
        raise HTTP500InternalServerError from error


@router.get(
    "/customers",
    responses={
        200: {"model": CustomerListResponse, "description": "OK."},
        400: {"model": ErrorMessage, "description": "Bad Request."},
        401: {"model": ErrorMessage, "description": "Unauthorized."},
        403: {"model": ErrorMessage, "description": "Forbidden."},
        404: {"model": ErrorMessage, "description": "Not Found."},
        405: {"model": ErrorMessage, "description": "Method Not Allowed."},
        406: {"model": ErrorMessage, "description": "Not Acceptable."},
        413: {"model": ErrorMessage, "description": "Payload Too Large."},
        414: {"model": ErrorMessage, "description": "URI Too Long."},
        422: {"model": ErrorMessage, "description": "Unprocessable Entity."},
        423: {"model": ErrorMessage, "description": "Locked."},
        429: {"model": ErrorMessage, "description": "Too Many Requests."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
        501: {"model": ErrorMessage, "description": "Not Implemented."},
        502: {"model": ErrorMessage, "description": "Bad Gateway."},
        503: {"model": ErrorMessage, "description": "Service Unavailable."},
        504: {"model": ErrorMessage, "description": "Gateway Timeout."},
    },
    tags=["Customers"],
    summary="List of customers.",
    response_model_by_alias=True,
    response_model=CustomerListResponse,
)
async def get_customers(
    request: Request,
    accept_language: Annotated[
        str,
        Header(
            description="ISO code of the language that the client accepts in response from the server.",
            regex=r"^[a-z]{2}-[A-Z]{2}$",
            min_length=1,
            max_length=6,
        ),
    ],
    x_request_id: Annotated[
        str,
        Header(
            description="Request ID.",
            regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
            min_length=1,
        ),
    ],
    limit: Annotated[
        int,
        Query(
            description="Number of records returned per page. If specified on entry, this will be the value of the query, otherwise it will be the value value set by default.",
            ge=1,
            le=100,
        ),
    ] = 10,
    offset: Annotated[
        int,
        Query(
            description="Record number from which you want to receive the number of records indicated in the limit. If it is indicated at the entry, it will be the value of the query. If it is not indicated at the input, as the query is on the first page, its value will be 0.",
            ge=0,
            le=100,
        ),
    ] = 0,
    street: Annotated[str | None, Query(description="")] = None,
    city: Annotated[str | None, Query(description="")] = None,
    country: Annotated[str | None, Query(description="")] = None,
    postal_code: Annotated[str | None, Query(description="")] = None,
    db: Session = Depends(get_db_session),
) -> JSONResponse:
    """List of customers."""
    filters = []
    if street:
        filters.append(Filter(field="street", operator="contains", value=street))
    if city:
        filters.append(Filter(field="city", operator="contains", value=city))
    if country:
        filters.append(Filter(field="country", operator="contains", value=country))
    if postal_code:
        filters.append(Filter(field="postal_code", operator="eq", value=postal_code))
    relationships = ["addresses"]

    try:
        db_data: list[CustomerDBModel]
        if db_data := customer_crud.get_list(db, offset, limit, filters, join_fields=relationships):
            response_data = [CustomerListDataResponse(id=row.id, name=row.name) for row in db_data]
            db_count = customer_crud.count(db, filters)
        else:
            response_data = []
            db_count = 0
    except Exception as error:
        raise HTTP500InternalServerError from error

    # url = f"{request.url.scheme}://{request.url.netloc}{request.scope.get('path', '')}"
    pagination = Pagination.get_pagination(
        offset=offset,
        limit=limit,
        no_elements=db_count,
        url=request.url,
    )

    headers = {"X-Request-ID": x_request_id}
    response = CustomerListResponse(data=response_data, pagination=pagination)
    return JSONResponse(content=response.dict(), status_code=200, headers=headers)


@router.get(
    "/customers/{customer_id}",
    responses={
        200: {"model": CustomerDetailResponse, "description": "OK."},
        401: {"model": ErrorMessage, "description": "Unauthorized."},
        403: {"model": ErrorMessage, "description": "Forbidden."},
        404: {"model": ErrorMessage, "description": "Not Found."},
        405: {"model": ErrorMessage, "description": "Method Not Allowed."},
        406: {"model": ErrorMessage, "description": "Not Acceptable."},
        413: {"model": ErrorMessage, "description": "Payload Too Large."},
        414: {"model": ErrorMessage, "description": "URI Too Long."},
        422: {"model": ErrorMessage, "description": "Unprocessable Entity."},
        423: {"model": ErrorMessage, "description": "Locked."},
        429: {"model": ErrorMessage, "description": "Too Many Requests."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
        501: {"model": ErrorMessage, "description": "Not Implemented."},
        502: {"model": ErrorMessage, "description": "Bad Gateway."},
        503: {"model": ErrorMessage, "description": "Service Unavailable."},
        504: {"model": ErrorMessage, "description": "Gateway Timeout."},
    },
    tags=["Customers"],
    summary="Customer information.",
    response_model_by_alias=True,
    response_model=CustomerDetailResponse,
)
async def get_customers_customer_id(
    accept_language: Annotated[
        str,
        Header(
            description="ISO code of the language that the client accepts in response from the server.",
            regex=r"^[a-z]{2}-[A-Z]{2}$",
            min_length=1,
            max_length=6,
        ),
    ],
    x_request_id: Annotated[
        str,
        Header(
            ...,
            description="Request ID.",
            regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
            min_length=1,
        ),
    ],
    customer_id: Annotated[int, Path(description="Id of a specific customer.", ge=1)],
    db: Session = Depends(get_db_session),
) -> JSONResponse:
    """Retrieve the information of the customer with the matching code."""
    headers = {
        "X-Request-ID": x_request_id,
    }
    try:
        if db_data := customer_crud.get_by_id(db, customer_id):
            api_data = CustomerDetailResponse(
                id=db_data.id,
                name=db_data.name,
                addresses=[
                    AddressResponse(
                        id=address.id,
                        street=address.street,
                        city=address.city,
                        country=address.country,
                        postal_code=address.postal_code,
                    )
                    for address in db_data.addresses
                ],
            )
    except Exception as error:
        raise HTTP500InternalServerError from error
    return JSONResponse(content=api_data.dict(), status_code=200, headers=headers)


@router.post(
    "/customers",
    responses={
        201: {"description": "Created."},
        400: {"model": ErrorMessage, "description": "Bad Request."},
        401: {"model": ErrorMessage, "description": "Unauthorized."},
        403: {"model": ErrorMessage, "description": "Forbidden."},
        405: {"model": ErrorMessage, "description": "Method Not Allowed."},
        406: {"model": ErrorMessage, "description": "Not Acceptable."},
        413: {"model": ErrorMessage, "description": "Payload Too Large."},
        414: {"model": ErrorMessage, "description": "URI Too Long."},
        415: {"model": ErrorMessage, "description": "Unsupported Media Type."},
        422: {"model": ErrorMessage, "description": "Unprocessable Entity."},
        423: {"model": ErrorMessage, "description": "Locked."},
        429: {"model": ErrorMessage, "description": "Too Many Requests."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
        501: {"model": ErrorMessage, "description": "Not Implemented."},
        502: {"model": ErrorMessage, "description": "Bad Gateway."},
        503: {"model": ErrorMessage, "description": "Service Unavailable."},
        504: {"model": ErrorMessage, "description": "Gateway Timeout."},
    },
    tags=["Customers"],
    summary="Create a new customer.",
    response_model_by_alias=True,
)
async def post_customers(
    request: Request,
    accept_language: Annotated[
        str,
        Header(
            description="ISO code of the language that the client accepts in response from the server.",
            regex=r"^[a-z]{2}-[A-Z]{2}$",
            min_length=1,
            max_length=6,
        ),
    ],
    x_request_id: Annotated[
        str,
        Header(
            description="Request ID.",
            regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
            min_length=1,
        ),
    ],
    db: Session = Depends(get_db_session),
    post_customers_request: CustomerCreate = Body(description=""),
) -> Response:
    """Add a new customer into the list."""
    try:
        customer = CustomerDBModel(name=post_customers_request.name)
        customer_crud.create(db, customer)
        for address in post_customers_request.addresses:
            db_address = AddressDBModel(
                customer_id=customer.id,
                street=address.street,
                city=address.city,
                country=address.country,
                postal_code=address.postal_code,
            )
            address_crud.create(db, db_address)
        url = request.url
        headers = {
            "X-Request-ID": x_request_id,
            "Location": f"{url.scheme}://{url.netloc}/customers/{customer.id}",
        }
        return Response(status_code=status.HTTP_201_CREATED, headers=headers)
    except Exception as error:
        raise HTTP500InternalServerError from error


@router.put(
    "/customers/{customer_id}",
    responses={
        204: {"description": "No Content."},
        400: {"model": ErrorMessage, "description": "Bad Request."},
        401: {"model": ErrorMessage, "description": "Unauthorized."},
        403: {"model": ErrorMessage, "description": "Forbidden."},
        404: {"model": ErrorMessage, "description": "Not Found."},
        405: {"model": ErrorMessage, "description": "Method Not Allowed."},
        406: {"model": ErrorMessage, "description": "Not Acceptable."},
        409: {"model": ErrorMessage, "description": "Conflict."},
        413: {"model": ErrorMessage, "description": "Payload Too Large."},
        414: {"model": ErrorMessage, "description": "URI Too Long."},
        415: {"model": ErrorMessage, "description": "Unsupported Media Type."},
        422: {"model": ErrorMessage, "description": "Unprocessable Entity."},
        423: {"model": ErrorMessage, "description": "Locked."},
        429: {"model": ErrorMessage, "description": "Too Many Requests."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
        501: {"model": ErrorMessage, "description": "Not Implemented."},
        502: {"model": ErrorMessage, "description": "Bad Gateway."},
        503: {"model": ErrorMessage, "description": "Service Unavailable."},
        504: {"model": ErrorMessage, "description": "Gateway Timeout."},
    },
    tags=["Customers"],
    summary="Update information from a customer.",
    response_model_by_alias=True,
)
async def put_customers_customer_id(
    accept_language: Annotated[
        str,
        Header(
            description="ISO code of the language that the client accepts in response from the server.",
            regex=r"^[a-z]{2}-[A-Z]{2}$",
            min_length=1,
            max_length=6,
        ),
    ],
    x_request_id: Annotated[
        str,
        Header(
            description="Request ID.",
            regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
            min_length=1,
        ),
    ],
    customer_id: Annotated[int, Path(description="Id of a specific customer.", ge=1)],
    db: Session = Depends(get_db_session),
    post_customers_request: CustomerUpdate = Body(description=""),
) -> Response:
    """Update of the information of a customer with the matching Id."""
    try:
        db_customer = customer_crud.get_by_id(db, customer_id)
        if not db_customer:
            raise HTTP404NotFoundError
        if post_customers_request.name:
            db_customer.name = post_customers_request.name
            customer_crud.update(db, db_customer)
        headers = {
            "X-Request-ID": x_request_id,
        }
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)
    except Exception as error:
        raise HTTP500InternalServerError from error


@router.put(
    "/customers/{customer_id}/addresses/{address_id}",
    responses={
        204: {"description": "No Content."},
        400: {"model": ErrorMessage, "description": "Bad Request."},
        401: {"model": ErrorMessage, "description": "Unauthorized."},
        403: {"model": ErrorMessage, "description": "Forbidden."},
        404: {"model": ErrorMessage, "description": "Not Found."},
        405: {"model": ErrorMessage, "description": "Method Not Allowed."},
        406: {"model": ErrorMessage, "description": "Not Acceptable."},
        409: {"model": ErrorMessage, "description": "Conflict."},
        413: {"model": ErrorMessage, "description": "Payload Too Large."},
        414: {"model": ErrorMessage, "description": "URI Too Long."},
        415: {"model": ErrorMessage, "description": "Unsupported Media Type."},
        422: {"model": ErrorMessage, "description": "Unprocessable Entity."},
        423: {"model": ErrorMessage, "description": "Locked."},
        429: {"model": ErrorMessage, "description": "Too Many Requests."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
        501: {"model": ErrorMessage, "description": "Not Implemented."},
        502: {"model": ErrorMessage, "description": "Bad Gateway."},
        503: {"model": ErrorMessage, "description": "Service Unavailable."},
        504: {"model": ErrorMessage, "description": "Gateway Timeout."},
    },
    tags=["Customers"],
    summary="Update information from a customer.",
    response_model_by_alias=True,
)
async def put_addresses_customer_id(
    accept_language: Annotated[
        str,
        Header(
            description="ISO code of the language that the client accepts in response from the server.",
            regex=r"^[a-z]{2}-[A-Z]{2}$",
            min_length=1,
            max_length=6,
        ),
    ],
    x_request_id: Annotated[
        str,
        Header(
            description="Request ID.",
            regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
            min_length=1,
        ),
    ],
    customer_id: Annotated[int, Path(description="Id of a specific customer.", ge=1)],
    address_id: Annotated[int, Path(description="Id of a specific address.", ge=1)],
    db: Session = Depends(get_db_session),
    post_address_request: AddressBase = Body(description=""),
) -> Response:
    """Update of the information of a customer with the matching Id."""
    try:
        filters = [
            Filter(field="customer_id", operator="eq", value=customer_id),
            Filter(field="id", operator="eq", value=address_id),
        ]
        db_address = address_crud.get_one_by_fields(db, filters)
        if not db_address:
            raise HTTP404NotFoundError

        db_address.street = post_address_request.street
        db_address.city = post_address_request.city
        db_address.country = post_address_request.country
        db_address.postal_code = post_address_request.postal_code
        address_crud.update(db, db_address)
        headers = {
            "X-Request-ID": x_request_id,
        }
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)
    except Exception as error:
        raise HTTP500InternalServerError from error


@router.delete(
    "/customers/{customer_id}/addresses/{address_id}",
    responses={
        204: {"description": "No Content."},
        400: {"model": ErrorMessage, "description": "Bad Request."},
        401: {"model": ErrorMessage, "description": "Unauthorized."},
        403: {"model": ErrorMessage, "description": "Forbidden."},
        404: {"model": ErrorMessage, "description": "Not Found."},
        405: {"model": ErrorMessage, "description": "Method Not Allowed."},
        406: {"model": ErrorMessage, "description": "Not Acceptable."},
        409: {"model": ErrorMessage, "description": "Conflict."},
        413: {"model": ErrorMessage, "description": "Payload Too Large."},
        414: {"model": ErrorMessage, "description": "URI Too Long."},
        422: {"model": ErrorMessage, "description": "Unprocessable Entity."},
        423: {"model": ErrorMessage, "description": "Locked."},
        429: {"model": ErrorMessage, "description": "Too Many Requests."},
        500: {"model": ErrorMessage, "description": "Internal Server Error."},
        501: {"model": ErrorMessage, "description": "Not Implemented."},
        502: {"model": ErrorMessage, "description": "Bad Gateway."},
        503: {"model": ErrorMessage, "description": "Service Unavailable."},
        504: {"model": ErrorMessage, "description": "Gateway Timeout."},
    },
    tags=["Customers"],
    summary="Delete specific customer.",
    response_model=None,
)
async def delete_address_id(
    accept_language: Annotated[
        str,
        Header(
            description="ISO code of the language that the client accepts in response from the server.",
            regex=r"^[a-z]{2}-[A-Z]{2}$",
            min_length=1,
            max_length=6,
        ),
    ],
    x_request_id: Annotated[
        str,
        Header(
            description="Request ID.",
            regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
            min_length=1,
        ),
    ],
    customer_id: Annotated[int, Path(description="Id of a specific customer.", ge=1)],
    address_id: Annotated[int, Path(description="Id of a specific address.", ge=1)],
    db: Session = Depends(get_db_session),
) -> Response:
    """Delete the information of the customer with the matching Id."""
    try:
        filters = [
            Filter(field="customer_id", operator="eq", value=customer_id),
            Filter(field="id", operator="eq", value=address_id),
        ]
        db_address = address_crud.get_one_by_fields(db, filters)
        if not db_address:
            raise HTTP404NotFoundError
        address_crud.delete_row(db, db_address)
        headers = {
            "X-Request-ID": x_request_id,
        }
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)
    except Exception as error:
        raise HTTP500InternalServerError from error
