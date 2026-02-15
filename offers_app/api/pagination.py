"""
Pagination configuration for offers endpoints.

Why this exists:
- DRF only returns a paginated response shape ({"count", "next", "previous", "results"})
if pagination is enabled.
- If `page_size` is not set (and no global DEFAULT_PAGINATION_CLASS + PAGE_SIZE exists),
DRF will return a plain list instead of the paginated dict.
- Our tests expect the paginated dict shape, so we define `page_size`.

Query params:
- page: int
- page_size: int (bounded by max_page_size)
"""

from rest_framework.pagination import PageNumberPagination


class OffersPagination(PageNumberPagination):
    """
    Page-number pagination for offers.

    Notes:
        - `page_size` enables pagination and ensures the response includes
        {"count", "next", "previous", "results"}.
        - `page_size_query_param` allows the client to request smaller/larger pages.
        - `max_page_size` caps the requested size.
    """

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 3
