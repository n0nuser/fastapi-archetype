from fastapi import APIRouter, Body, Header, Path, Query, Request, status
from fastapi.responses import JSONResponse, Response

from src.api.responses.exceptions import InternalServerError, NotFound
# from src.api.schemas.extra_models import TokenModel
# from src.api.security_api import get_token_oAuthSample
from src.api.schemas.error_message import ErrorMessage
from src.api.schemas.office_data import OfficeData
from src.api.schemas.office_data_data import OfficeDataData
from src.api.schemas.office_response import OfficeResponse
from src.api.schemas.office_response_data_inner import OfficeResponseDataInner
from src.api.schemas.post_offices_request import PostOfficesRequest
from src.api.utils import check_entity_exists, get_pagination
from src.db.crud import count, create, delete_by_id, get_list, update
from src.db.models import Address as AddressDBModel
from src.db.models import Office as OfficeDBModel

router = APIRouter()


def _map_apimodel_to_dbmodel(
    api_model: PostOfficesRequest,
    model_id: int,
) -> tuple[OfficeDBModel, AddressDBModel]:
    kwargs = {"id": model_id, "name": api_model.name}
    office = OfficeDBModel(**kwargs)

    kwargs = {
        "id": model_id,
        "line": api_model.line,
        "street_name": api_model.streetName,
        "building_number": api_model.buildingNumber,
        "stair": api_model.stair,
        "floor": api_model.floor,
        "door_number": api_model.doorNumber,
        "postal_code": api_model.postalCode,
        "province": api_model.province,
        "country": api_model.country,
        "office_id": model_id,
    }
    address = AddressDBModel(**kwargs)
    return office, address


@router.delete(
    "/offices/{officeId}",
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
    tags=["Offices"],
    summary="Delete specific office.",
    response_model_by_alias=True,
)
async def delete_offices_office_id(
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
    officeId: int = Path(None, description="Id of a specific office.", ge=1),
    # token_oAuthSample: TokenModel = Security(
    #     get_token_oAuthSample,
    #     scopes=[
    #         "offices-system.offices.delete",
    #         "offices-system.ALL.ALL",
    #         "offices-system.ALL.delete",
    #         "offices-system.offices.ALL",
    #     ],
    # ),
) -> None:
    """Delete the information of the office with the matching Id."""
    try:
        if not delete_by_id(OfficeDBModel, officeId, soft_delete=True):  # type: ignore
            raise NotFound
        if not delete_by_id(AddressDBModel, officeId, soft_delete=True):  # type: ignore
            raise NotFound
    except Exception as error:
        raise InternalServerError from error
    headers = {
        "X-Request-ID": x_request_id,
    }
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)  # type: ignore


@router.get(
    "/offices",
    responses={
        200: {"model": OfficeResponse, "description": "OK."},
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
    tags=["Offices"],
    summary="List of offices.",
    response_model_by_alias=True,
)
async def get_offices(
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
    address_province: str = Query(
        None,
        description="Field to filter the offices by the specific provinces.",
        max_length=50,
        alias="address.province",
    ),
    # token_oAuthSample: TokenModel = Security(
    #     get_token_oAuthSample,
    #     scopes=[
    #         "offices-system.offices.read",
    #         "offices-system.ALL.ALL",
    #         "offices-system.ALL.read",
    #         "offices-system.offices.ALL",
    #     ],
    # ),
) -> OfficeResponse:
    """List of offices."""
    filters = {"deleted_on": ("eq", None)}
    if address_province:
        filters["province"] = ("eq", address_province)  # type: ignore
    relationships = ["office"]

    try:
        db_data: list[AddressDBModel]
        if db_data := get_list(AddressDBModel, limit, offset, filters, join_fields=relationships):  # type: ignore
            response_data = [
                OfficeResponseDataInner(officeId=d.id, name=d.office.name) for d in db_data
            ]
            db_count = count(AddressDBModel, filters)  # type: ignore
        else:
            response_data = []
            db_count = 0
    except Exception as error:
        raise InternalServerError from error

    pagination = get_pagination(offset=offset, limit=limit, no_elements=db_count, request=request)

    headers = {"X-Request-ID": x_request_id}
    response = OfficeResponse(data=response_data, pagination=pagination)
    return JSONResponse(content=response.dict(), status_code=200, headers=headers)  # type: ignore


@router.get(
    "/offices/{officeId}",
    responses={
        200: {"model": OfficeData, "description": "OK."},
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
    tags=["Offices"],
    summary="Office information.",
    response_model_by_alias=True,
)
async def get_offices_office_id(
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
    officeId: int = Path(None, description="Id of a specific office.", ge=1),
    # token_oAuthSample: TokenModel = Security(
    #     get_token_oAuthSample,
    #     scopes=[
    #         "offices-system.offices.read",
    #         "offices-system.ALL.ALL",
    #         "offices-system.ALL.read",
    #         "offices-system.offices.ALL",
    #     ],
    # ),
) -> OfficeData:
    """Retrieve the information of the office with the matching code."""
    headers = {
        "X-Request-ID": x_request_id,
    }
    address: AddressDBModel = check_entity_exists(officeId, AddressDBModel)  # type: ignore
    data = OfficeDataData(
        officeId=address.office.id,
        name=address.office.name,
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
    response = OfficeData(data=data)
    return JSONResponse(content=response.dict(), status_code=200, headers=headers)  # type: ignore


@router.post(
    "/offices",
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
    tags=["Offices"],
    summary="Create a new office.",
    response_model_by_alias=True,
)
async def post_offices(
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
    post_offices_request: PostOfficesRequest = Body(description=""),
    # token_oAuthSample: TokenModel = Security(
    #     get_token_oAuthSample,
    #     scopes=[
    #         "offices-system.offices.write",
    #         "offices-system.ALL.ALL",
    #         "offices-system.ALL.write",
    #         "offices-system.offices.ALL",
    #     ],
    # ),
) -> None:
    """Add a new office into the list."""
    try:
        office_id = create(OfficeDBModel(name=post_offices_request.name))
        _ = create(
            AddressDBModel(
                line=post_offices_request.line,
                street_name=post_offices_request.streetName,
                building_number=post_offices_request.buildingNumber,
                stair=post_offices_request.stair,
                floor=post_offices_request.floor,
                door_number=post_offices_request.doorNumber,
                postal_code=post_offices_request.postalCode,
                province=post_offices_request.province,
                country=post_offices_request.country,
                office_id=office_id,
            ),
        )
    except Exception as error:
        raise InternalServerError from error
    url = request.url
    headers = {
        "X-Request-ID": x_request_id,
        # TODO: Adapt for prod
        "Location": f"{url.scheme}://{url.netloc}/offices/{office_id}",
    }
    return Response(status_code=status.HTTP_201_CREATED, headers=headers)  # type: ignore


@router.put(
    "/offices/{officeId}",
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
    tags=["Offices"],
    summary="Update information from a office.",
    response_model_by_alias=True,
)
async def put_offices_office_id(
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
    officeId: int = Path(None, description="Id of a specific office.", ge=1),
    post_offices_request: PostOfficesRequest = Body(description=""),
    # token_oAuthSample: TokenModel = Security(
    #     get_token_oAuthSample,
    #     scopes=[
    #         "offices-system.offices.update",
    #         "offices-system.ALL.ALL",
    #         "offices-system.ALL.update",
    #         "offices-system.offices.ALL",
    #     ],
    # ),
) -> None:
    """Update of the information of a office with the matching Id."""
    # Checks
    check_entity_exists(officeId, AddressDBModel)
    check_entity_exists(officeId, OfficeDBModel)

    db_office, db_address = _map_apimodel_to_dbmodel(post_offices_request, officeId)
    try:
        update(db_office)
        update(db_address)
    except Exception as error:
        raise InternalServerError from error
    headers = {
        "X-Request-ID": x_request_id,
    }
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=headers)  # type: ignore
