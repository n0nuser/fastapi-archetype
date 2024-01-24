from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, Path, Query, Request, status
from fastapi.responses import JSONResponse, Response
from pydantic import UUID4
from sqlalchemy.orm import Session

from src.controller.api.schemas.customer import (
    AddressBase,
    CustomerCreate,
    CustomerDetailResponse,
    CustomerListResponse,
    CustomerUpdate,
)
from src.controller.api.schemas.error_message import ErrorMessage
from src.controller.errors.exceptions import HTTP404NotFoundError, HTTP500InternalServerError
from src.controller.pagination import Pagination
from src.repository.exceptions import ElementNotFound
from src.repository.session import get_db_session
from src.service.application.customer import CustomerApplicationService

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
    x_request_id: Annotated[UUID4, Header(description="Request ID.")],
    customer_id: Annotated[UUID4, Path(description="Id of a specific customer.")],
    accept_language: Annotated[
        str | None,
        Header(
            ...,
            description="ISO code of the language that the client accepts in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
) -> Response:
    """Delete the information of the customer with the matching Id."""
    try:
        CustomerApplicationService.delete_customer(db, customer_id)
    except ElementNotFound as error:
        raise HTTP404NotFoundError from error
    except Exception as error:
        raise HTTP500InternalServerError from error
    headers = {"X-Request-ID": str(x_request_id)}
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
    x_request_id: Annotated[UUID4, Header(description="Request ID.")],
    accept_language: Annotated[
        str | None,
        Header(
            description="ISO code of the language that the client accepts"
            + " in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            description="Number of records returned per page. If specified on entry, this will be"
            + " the value of the query, otherwise it will be the value value set by default.",
            ge=1,
            le=100,
        ),
    ] = 10,
    offset: Annotated[
        int,
        Query(
            description="Record number from which you want to receive the number of records"
            + " indicated in the limit. If it is indicated at the entry, it will be the value of the query. If it is not indicated at the input, as the query is on the first page, its value will be 0.",
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
    try:
        response_data, db_count = CustomerApplicationService.get_customers(
            db,
            limit,
            offset,
            street,
            city,
            country,
            postal_code,
        )
    except ElementNotFound as error:
        raise HTTP404NotFoundError from error
    except Exception as error:
        raise HTTP500InternalServerError from error

    # url = f"{request.url.scheme}://{request.url.netloc}{request.scope.get('path', '')}"
    pagination = Pagination.get_pagination(
        offset=offset,
        limit=limit,
        no_elements=db_count,
        url=request.url,
    )
    headers = {"X-Request-ID": str(x_request_id)}
    response = CustomerListResponse(data=response_data, pagination=pagination)
    return JSONResponse(content=response.model_dump(), status_code=200, headers=headers)


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
async def get_customer_id(
    x_request_id: Annotated[UUID4, Header(description="Request ID.")],
    customer_id: Annotated[UUID4, Path(description="Id of a specific customer.")],
    accept_language: Annotated[
        str | None,
        Header(
            description="ISO code of the language that the client accepts"
            + " in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
) -> JSONResponse:
    """Retrieve the information of the customer with the matching code."""
    try:
        api_data = CustomerApplicationService.get_customer_id(db, customer_id)
    except ElementNotFound as error:
        raise HTTP404NotFoundError from error
    except Exception as error:
        raise HTTP500InternalServerError from error
    headers = {"X-Request-ID": str(x_request_id)}
    return JSONResponse(content=api_data.model_dump(), status_code=200, headers=headers)


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
async def post_customer(
    request: Request,
    x_request_id: Annotated[UUID4, Header(description="Request ID.")],
    accept_language: Annotated[
        str | None,
        Header(
            description="ISO code of the language that the client accepts"
            + " in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
    post_customers_request: CustomerCreate = Body(description=""),
) -> Response:
    """Add a new customer into the list."""
    try:
        customer_id = CustomerApplicationService.post_customer(db, post_customers_request)
    except Exception as error:
        raise HTTP500InternalServerError from error
    url = request.url
    headers = {
        "X-Request-ID": str(x_request_id),
        "Location": f"{url.scheme}://{url.netloc}/customers/{customer_id}",
    }
    return Response(status_code=status.HTTP_201_CREATED, headers=headers)


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
    x_request_id: Annotated[UUID4, Header(description="Request ID.")],
    customer_id: Annotated[UUID4, Path(description="Id of a specific customer.")],
    accept_language: Annotated[
        str | None,
        Header(
            description="ISO code of the language that the client accepts"
            + " in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
    post_customers_request: CustomerUpdate = Body(description=""),
) -> Response:
    """Update of the information of a customer with the matching Id."""
    try:
        CustomerApplicationService.put_customers(db, customer_id, post_customers_request)
    except ElementNotFound as error:
        raise HTTP404NotFoundError from error
    except Exception as error:
        raise HTTP500InternalServerError from error
    headers = {"X-Request-ID": str(x_request_id)}
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)


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
    x_request_id: Annotated[UUID4, Header(description="Request ID.")],
    customer_id: Annotated[UUID4, Path(description="Id of a specific customer.")],
    address_id: Annotated[UUID4, Path(description="Id of a specific address.")],
    accept_language: Annotated[
        str | None,
        Header(
            description="ISO code of the language that the client accepts"
            + " in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
    post_address_request: AddressBase = Body(description=""),
) -> Response:
    """Update of the information of a customer with the matching Id."""
    try:
        CustomerApplicationService.put_adress(db, customer_id, address_id, post_address_request)
    except ElementNotFound as error:
        raise HTTP404NotFoundError from error
    except Exception as error:
        raise HTTP500InternalServerError from error
    headers = {"X-Request-ID": str(x_request_id)}
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)


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
    x_request_id: Annotated[UUID4, Header(description="Request ID.")],
    customer_id: Annotated[UUID4, Path(description="Id of a specific customer.")],
    address_id: Annotated[UUID4, Path(description="Id of a specific address.")],
    accept_language: Annotated[
        str | None,
        Header(
            description="ISO code of the language that the client accepts"
            + " in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = None,
    db: Session = Depends(get_db_session),
) -> Response:
    """Delete the information of the customer with the matching Id."""
    try:
        CustomerApplicationService.delete_address(db, customer_id, address_id)
    except Exception as error:
        raise HTTP500InternalServerError from error
    headers = {
        "X-Request-ID": str(x_request_id),
    }
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)
