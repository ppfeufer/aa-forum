"""
Pagination helper
"""

# Django
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet


def get_paginated_page_object(
    queryset: QuerySet, items_per_page: int = 10, page_number: int = None
) -> Page:
    """
    Get the pagination page object
    :param queryset:
    :type queryset:
    :param items_per_page:
    :type items_per_page:
    :param page_number:
    :type page_number:
    :return:
    :rtype:
    """

    paginator = Paginator(queryset, items_per_page)
    page_obj = paginator.get_page(page_number)

    return page_obj
