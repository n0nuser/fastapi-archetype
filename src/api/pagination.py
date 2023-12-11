import math
from typing import Optional

from fastapi import Request

from src.api.schemas.pagination import Pagination
from src.api.schemas.pagination_links import PaginationLinks
from src.api.schemas.pagination_links_first import PaginationLinksFirst
from src.api.schemas.pagination_links_last import PaginationLinksLast
from src.api.schemas.pagination_links_next import PaginationLinksNext
from src.api.schemas.pagination_links_prev import PaginationLinksPrev
from src.api.responses.exceptions import InternalServerError, NotFound
from src.db.crud import get_by_id


def calculate_page_number(offset: int, limit: int, total_elements: int) -> int:
    """
    Calculate the page number based on the given offset, limit, and total elements.

    Args:
        offset (int): The starting index of the current page (0-based).
        limit (int): The maximum number of elements per page.
        total_elements (int): The total number of elements across all pages.

    Raises:
        ValueError: If the limit is not a positive integer, or if the total elements is not a non-negative integer.

    Returns:
        int: The page number (1-based).
    """
    if limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    if total_elements < 0:
        raise ValueError("Total elements must be a non-negative integer.")

    return math.ceil((offset - 1) / limit) + 1


def calculate_total_pages(limit: int, total_elements: int) -> int:
    """
    Calculate the total number of pages based on the given offset, limit, and total elements.

    Args:
        limit (int): The maximum number of elements per page.
        total_elements (int): The total number of elements across all pages.

    Raises:
        ValueError: If the limit is not a positive integer, or if the total elements is not a non-negative integer.

    Returns:
        int: The total number of pages.
    """
    if limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    if total_elements < 0:
        raise ValueError("Total elements must be a non-negative integer.")

    return math.ceil(float(total_elements) / limit)


def generate_pagination_links(
    request: Request, total_pages: int, limit: int, offset: int, no_elements: int
) -> PaginationLinks:
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    path = request.scope.get("path", "")
    url_without_query_params = base_url + path

    self_href = f"{url_without_query_params}?limit={limit}&offset={offset}"
    _self = PaginationLinksFirst(href=self_href)

    if no_elements == 0:
        return PaginationLinks(first=None, self_=_self, prev=None, next=None, last=None)

    last_page = total_pages - 1

    first_href = f"{url_without_query_params}?limit={limit}&offset=0"
    prev_href = f"{url_without_query_params}?limit={limit}&offset={max(0, offset - limit)}"
    next_href = (
        f"{url_without_query_params}?limit={limit}&offset={min(last_page * limit, offset + limit)}"
    )
    last_href = f"{url_without_query_params}?limit={limit}&offset={max(0, (last_page - 1) * limit)}"

    first = PaginationLinksFirst(href=first_href)
    if offset > 0:
        prev = PaginationLinksPrev(href=prev_href)
    else:
        prev = PaginationLinksPrev(href=self_href)
    if offset < last_page * limit:
        _next = PaginationLinksNext(href=next_href)
    else:
        _next = PaginationLinksNext(href=self_href)
    last = PaginationLinksLast(href=last_href)

    return PaginationLinks(first=first, self_=_self, prev=prev, next=_next, last=last)


def get_pagination(offset: int, limit: int, no_elements: int, request: Request):
    total_pages = calculate_total_pages(limit, no_elements)
    links = generate_pagination_links(
        request=request,
        total_pages=total_pages,
        limit=limit,
        offset=offset,
        no_elements=no_elements,
    )
    return Pagination(
        offset=offset,
        limit=limit,
        pageNumber=calculate_page_number(offset, limit, no_elements),
        totalPages=total_pages,
        totalElements=no_elements,
        links=links,
    )


def check_entity_exists(entity_id: Optional[int] = None, entity_type=None):
    """Checks if the entity exists in the database.

    Args:
        entity_id (Optional[int], optional): The ID of the entity. Defaults to None.
        entity_type (Any, optional): The type of entity (e.g., BookingDBModel,
            StatusDayDBModel, WorkStationDBModel). Defaults to None.

    Raises:
        NotFound: If the entity does not exist in the database.

    Returns:
        Union[BookingDBModel, StatusDayDBModel, WorkstationDBModel]: The entity.
    """
    if entity_id and entity_type:
        try:
            entity = get_by_id(entity_type, entity_id)  # type: ignore
        except Exception as error:
            raise InternalServerError from error
        # TODO: Improve classes by:
        #   - Create CRUDManager as Base class with generic annotations
        #   - Adding this method to each DB class with concrete annotations
        if not entity or hasattr(entity, "deleted_on") and entity.deleted_on:  # type: ignore
            raise NotFound
        return entity
    else:
        raise ValueError("Both entity_id and entity_type must be provided.")
