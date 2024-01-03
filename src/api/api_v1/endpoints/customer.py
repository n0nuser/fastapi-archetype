from fastapi import APIRouter, Body, Depends, Header, Path, Query, Request, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from src.api.api_v1.schemas.customer import (
    AddressResponse,
    CustomerListDataResponse,
    CustomerListResponse,
)
from src.api.api_v1.schemas.error_message import ErrorMessage
from src.api.errors.exceptions import HTTP404NotFoundError, HTTP500InternalServerError
from src.api.pagination import Pagination
from src.db.crud.base import Filter
from src.db.crud.customer import customer_crud
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
    accept_language: str = Header(
        ...,
        description="ISO code of the language that the client accepts in response from the server.",
        regex=r"^[a-z]{2}-[A-Z]{2}$",
        min_length=1,
        max_length=6,
    ),
    x_request_id: str = Header(
        ...,
        description="Request ID.",
        regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
        min_length=1,
    ),
    db: Session = Depends(get_db_session),
    customer_id: int = Path(None, description="Id of a specific customer.", ge=1),
) -> Response:
    """Delete the information of the customer with the matching Id."""
    try:
        customer = customer_crud.delete_by_id(db, customer_id)
    except Exception as error:
        raise HTTP500InternalServerError from error
    if not customer:
        raise HTTP404NotFoundError
    headers = {
        "X-Request-ID": x_request_id,
    }
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)


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
    accept_language: str = Header(
        ...,
        description="ISO code of the language that the client accepts in response from the server.",
        regex=r"^[a-z]{2}-[A-Z]{2}$",
        min_length=1,
        max_length=6,
    ),
    x_request_id: str = Header(
        ...,
        description="Request ID.",
        regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
        min_length=1,
    ),
    db: Session = Depends(get_db_session),
    limit: int = Query(
        10,
        description="Number of records returned per page. If specified on entry, this will be the value of the query, otherwise it will be the value value set by default.",
        ge=1,
        le=100,
    ),
    offset: int = Query(
        0,
        description="Record number from which you want to receive the number of records indicated in the limit. If it is indicated at the entry, it will be the value of the query. If it is not indicated at the input, as the query is on the first page, its value will be 0.",
        ge=0,
        le=100,
    ),
    street: str | None = Query(None, description=""),
    city: str | None = Query(None, description=""),
    country: str | None = Query(None, description=""),
    postal_code: str | None = Query(None, description=""),
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
            response_data = [
                CustomerListDataResponse(
                    id=row.id,
                    name=row.name,
                    addresses=[
                        AddressResponse(
                            id=address.id,
                            street=address.street,
                            city=address.city,
                            country=address.country,
                            postal_code=address.postal_code,
                        )
                        for address in row.addresses
                    ],
                )
                for row in db_data
            ]
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
    "/customers/{customerId}",
    responses={
        200: {"model": CustomerData, "description": "OK."},
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
)
async def get_customers_customer_id(
    accept_language: str = Header(
        ...,
        description="ISO code of the language that the client accepts in response from the server.",
        regex=r"^[a-z]{2}-[A-Z]{2}$",
        min_length=1,
        max_length=6,
    ),
    x_request_id: str = Header(
        ...,
        description="Request ID.",
        regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
        min_length=1,
    ),
    db: Session = Depends(get_db_session),
    customerId: int = Path(None, description="Id of a specific customer.", ge=1),
) -> CustomerData:
    """Retrieve the information of the customer with the matching code."""
    headers = {
        "X-Request-ID": x_request_id,
    }
    address: AddressDBModel = check_entity_exists(customerId, AddressDBModel)
    data = CustomerDataData(
        customerId=address.customer.id,
        name=address.customer.name,
        addressId=address.id,
        line=address.line,
        streetName=address.street_name,
        buildingNumber=address.building_number,
        stair=address.stair,
        floor=address.floor,
        doorNumber=address.door_number,
        postalCode=address.postal_code,
        province=address.province,
        country=address.country,
    )
    response = CustomerData(data=data)
    return JSONResponse(content=response.dict(), status_code=200, headers=headers)


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
    accept_language: str = Header(
        ...,
        description="ISO code of the language that the client accepts in response from the server.",
        regex=r"^[a-z]{2}-[A-Z]{2}$",
        min_length=1,
        max_length=6,
    ),
    x_request_id: str = Header(
        ...,
        description="Request ID.",
        regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
        min_length=1,
    ),
    db: Session = Depends(get_db_session),
    post_customers_request: PostCustomersRequest = Body(description=""),
) -> None:
    """Add a new customer into the list."""
    try:
        customer_id = create(CustomerDBModel(name=post_customers_request.name))
        _ = create(
            AddressDBModel(
                line=post_customers_request.line,
                street_name=post_customers_request.streetName,
                building_number=post_customers_request.buildingNumber,
                stair=post_customers_request.stair,
                floor=post_customers_request.floor,
                door_number=post_customers_request.doorNumber,
                postal_code=post_customers_request.postalCode,
                province=post_customers_request.province,
                country=post_customers_request.country,
                customer_id=customer_id,
            ),
        )
    except Exception as error:
        raise InternalServerError from error
    url = request.url
    headers = {
        "X-Request-ID": x_request_id,
        # TODO: Adapt for prod
        "Location": f"{url.scheme}://{url.netloc}/customers/{customer_id}",
    }
    return Response(status_code=status.HTTP_201_CREATED, headers=headers)


@router.put(
    "/customers/{customerId}",
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
    accept_language: str = Header(
        ...,
        description="ISO code of the language that the client accepts in response from the server.",
        regex=r"^[a-z]{2}-[A-Z]{2}$",
        min_length=1,
        max_length=6,
    ),
    x_request_id: str = Header(
        ...,
        description="Request ID.",
        regex=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$",
        min_length=1,
    ),
    db: Session = Depends(get_db_session),
    customerId: int = Path(None, description="Id of a specific customer.", ge=1),
    post_customers_request: PostCustomersRequest = Body(description=""),
) -> None:
    """Update of the information of a customer with the matching Id."""
    # Checks
    check_entity_exists(customerId, AddressDBModel)
    check_entity_exists(customerId, CustomerDBModel)

    db_customer, db_address = _map_apimodel_to_dbmodel(post_customers_request, customerId)
    try:
        update(db_customer)
        update(db_address)
    except Exception as error:
        raise InternalServerError from error
    headers = {
        "X-Request-ID": x_request_id,
    }
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)
