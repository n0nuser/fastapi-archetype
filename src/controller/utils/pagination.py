"""Defines data models for representing hyperlinks and pagination configuration."""

import math

from pydantic import AnyHttpUrl, BaseModel, Field, HttpUrl, field_validator


def calculate_page_number(offset: int, limit: int, total_elements: int) -> int:
    """Calculate the page number based on the given offset, limit, and total elements.

    Args:
        offset (int): The starting index of the current page (0-based).
        limit (int): The maximum number of elements per page.
        total_elements (int): The total number of elements across all pages.

    Raises:
        ValueError: If the limit is not a positive integer, or if the
            total elements is not a non-negative integer.

    Returns:
        int: The page number (1-based).
    """
    if limit <= 0:
        error_message = "Limit must be a positive integer."
        raise ValueError(error_message)

    if total_elements < 0:
        error_message = "Total elements must be a non-negative integer."
        raise ValueError(error_message)

    return math.ceil((offset - 1) / limit) + 1


def calculate_total_pages(limit: int, total_elements: int) -> int:
    """Calculate the total number of pages based on the given offset, limit, and total elements.

    Args:
        limit (int): The maximum number of elements per page.
        total_elements (int): The total number of elements across all pages.

    Raises:
        ValueError: If the limit is not a positive integer,
            or if the total elements is not a non-negative integer.

    Returns:
        int: The total number of pages.
    """
    if limit <= 0:
        error_message = "Limit must be a positive integer."
        raise ValueError(error_message)

    if total_elements < 0:
        error_message = "Total elements must be a non-negative integer."
        raise ValueError(error_message)

    return math.ceil(float(total_elements) / limit)


class HyperLink(BaseModel):
    """Represents a hyperlinked reference.

    Attributes:
        href (str, optional): The URL reference. Defaults to None.
    """

    href: str | None = Field(
        default=None,
        examples=["http://localhost:8000/api/v1/customers?limit=10&offset=0"],
    )


class PaginationLinks(BaseModel):
    """Represents a set of hyperlinks for pagination purposes.

    Attributes:
        first (HyperLink, optional): The link to the first page. Defaults to None.
        prev (HyperLink, optional): The link to the previous page. Defaults to None.
        actual (HyperLink): The link to the current page.
        next (HyperLink, optional): The link to the next page. Defaults to None.
        last (HyperLink, optional): The link to the last page. Defaults to None.
    """

    first: HyperLink | None = Field(
        default=None,
        examples=[{"href": "http://localhost:8000/api/v1/customers?limit=10&offset=0"}],
    )
    prev: HyperLink | None = Field(
        default=None,
        examples=[{"href": "http://localhost:8000/api/v1/customers?limit=10&offset=0"}],
    )
    actual: HyperLink = Field(
        examples=[{"href": "http://localhost:8000/api/v1/customers?limit=10&offset=0"}],
    )
    next: HyperLink | None = Field(
        default=None,
        examples=[{"href": "http://localhost:8000/api/v1/customers?limit=10&offset=10"}],
    )
    last: HyperLink | None = Field(
        default=None,
        examples=[{"href": "http://localhost:8000/api/v1/customers?limit=10&offset=10"}],
    )

    @classmethod
    def generate_pagination_links(
        cls: type["PaginationLinks"],
        url: HttpUrl,
        total_pages: int,
        limit: int,
        offset: int,
        no_elements: int,
    ) -> "PaginationLinks":
        """Generate pagination links and return a new instance of PaginationLinks.

        Args:
            url (HttpUrl): The base URL for the pagination links.
            total_pages (int): The total number of pages available.
            limit (int): The number of elements per page.
            offset (int): The current offset for the pagination.
            no_elements (int): The total number of elements.

        Returns:
            PaginationLinks: An object containing HyperLink instances for
                first, actual, prev, next, and last pages.
                The actual page link is based on the provided offset.
        """
        base_href = f"{url}&" if "?" in str(url) else f"{url}?"
        base_href = f"{base_href}limit={limit}"
        self_href = f"{base_href}&offset={offset}"
        actual = HyperLink(href=str(AnyHttpUrl(self_href)))

        if no_elements == 0:
            return cls(first=None, actual=actual, prev=None, next=None, last=None)

        last_page = total_pages - 1

        first_href = f"{base_href}&offset=0"
        prev_href = f"{base_href}&offset={max(0, offset - limit)}"
        next_href = f"{base_href}&offset={min(last_page * limit, offset + limit)}"
        last_href = f"{base_href}&offset={max(0, (last_page - 1) * limit)}"

        first_page = HyperLink(href=str(AnyHttpUrl(first_href)))
        prev_page = (
            HyperLink(href=str(AnyHttpUrl(prev_href)))
            if offset > 0
            else HyperLink(href=str(AnyHttpUrl(self_href)))
        )
        next_page = (
            HyperLink(href=str(AnyHttpUrl(next_href)))
            if offset < last_page * limit
            else HyperLink(href=str(AnyHttpUrl(self_href)))
        )
        last_page = HyperLink(href=str(AnyHttpUrl(last_href)))

        return cls(first=first_page, actual=actual, prev=prev_page, next=next_page, last=last_page)


class Pagination(BaseModel):
    """Represents a pagination configuration for handling offsets,
    limits, page numbers, total pages, total elements, and pagination links.

    Attributes:
    - offset (int | None): The offset for pagination.
    - limit (int | None): The limit of elements per page.
    - page_number (int | None): The current page number.
    - total_pages (int | None): The total number of pages.
    - total_elements (int | None): The total number of elements.
    - links (PaginationLinks | None): Links associated with the pagination.

    Class Methods:
    - offset_validator(cls: type[Pagination], value: int | None) -> int | None:
        Validates the offset value based on specified constraints.

    Note: The offset value must be within the range [0, 255].
    """

    offset: int | None = Field(default=None)
    limit: int | None = Field(default=None)
    page_number: int | None = Field(default=None)
    total_pages: int | None = Field(default=None)
    total_elements: int | None = Field(default=None)
    links: PaginationLinks | None = Field(
        default=None,
        examples=[
            {
                "actual": {"href": "http://localhost:8000/api/v1/customers?limit=10&offset=0"},
                "first": {"href": "http://localhost:8000/api/v1/customers?limit=10&offset=0"},
                "prev": {"href": "http://localhost:8000/api/v1/customers?limit=10&offset=0"},
                "next": {"href": "http://localhost:8000/api/v1/customers?limit=10&offset=10"},
                "last": {"href": "http://localhost:8000/api/v1/customers?limit=10&offset=10"},
            },
        ],
    )

    @field_validator("offset", "limit", "page_number", "total_pages", "total_elements")
    @classmethod
    def offset_validator(cls: type["Pagination"], value: int | None) -> int | None:
        """Validates values of the model."""
        max_value = 255
        min_value = 0
        if value and (value > max_value or value < min_value):
            error_message = f"Must be less than {min_value} or more than {max_value}."
            raise ValueError(error_message)
        return value

    @classmethod
    def get_pagination(
        cls: type["Pagination"],
        offset: int,
        limit: int,
        no_elements: int,
        url: str,
    ) -> "Pagination":
        """Generate pagination information based on the provided parameters.

        Parameters:
        - offset (int): The starting index of the current page.
        - limit (int): The maximum number of elements per page.
        - no_elements (int): The total number of elements to be paginated.
        - url (str): The base URL used for generating pagination links.

        Returns:
        Pagination: An object containing pagination information, including offset,
        limit, current page number, total pages, total elements, and pagination links.
        """
        total_pages = calculate_total_pages(limit, no_elements)
        links = PaginationLinks.generate_pagination_links(
            url=url,
            total_pages=total_pages,
            limit=limit,
            offset=offset,
            no_elements=no_elements,
        )
        return cls(
            offset=offset,
            limit=limit,
            page_number=calculate_page_number(offset, limit, no_elements),
            total_pages=total_pages,
            total_elements=no_elements,
            links=links,
        )


HyperLink.model_rebuild()
PaginationLinks.model_rebuild()
Pagination.model_rebuild()
