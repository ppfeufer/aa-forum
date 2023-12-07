"""
Pagination helper functions
"""

# Django
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet


def get_paginated_page_object(
    queryset: QuerySet, items_per_page: int = 10, page_number: int = None
) -> Page:
    """
    Return a paginated page object

    :param queryset:
    :type queryset:
    :param items_per_page:
    :type items_per_page:
    :param page_number:
    :type page_number:
    :return:
    :rtype:
    """

    paginator = Paginator(object_list=queryset, per_page=items_per_page)
    page_obj = paginator.get_page(number=page_number)

    return page_obj
