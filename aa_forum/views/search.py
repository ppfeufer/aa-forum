"""
Search related views
"""

# Standard Library
from functools import reduce
from operator import or_

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Forum
from aa_forum import __title__
from aa_forum.constants import SEARCH_STOPWORDS
from aa_forum.models import Board, Message, Setting

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aa_forum.basic_access")
def results(request: WSGIRequest, page_number: int = None) -> HttpResponse:
    """
    Search results view
    :param request:
    :param page_number:
    :return:
    """

    if request.GET:
        search_phrase = request.GET.get("q")
    else:
        search_phrase = ""

    search_results = None
    page_obj = None

    querywords = search_phrase.split()
    search_phrase_terms = [
        word for word in querywords if word.lower() not in SEARCH_STOPWORDS
    ]

    if len(search_phrase_terms) >= 1:
        boards = (
            Board.objects.user_has_access(request.user)
            .distinct()
            .values_list("pk", flat=True)
        )

        search_results = (
            Message.objects.filter(
                reduce(
                    or_,
                    [
                        Q(message_plaintext__icontains=search_term)
                        for search_term in search_phrase_terms
                    ],
                ),
                topic__board__pk__in=boards,
            )
            .select_related(
                "user_created",
                "user_created__profile__main_character",
                "topic",
                "topic__first_message",
                "topic__board",
                "topic__board__category",
            )
            .order_by("-time_modified")
            .distinct()
        )

        paginator = Paginator(
            search_results,
            int(Setting.objects.get_setting(setting_key=Setting.MESSAGESPERPAGE)),
        )
        page_obj = paginator.get_page(page_number)

    context = {
        "search_term": search_phrase,
        "search_results": page_obj,
        "search_results_count": 0 if search_results is None else search_results.count(),
    }

    logger.info(f'{request.user} calling search view, searching for "{search_phrase}".')

    return render(request, "aa_forum/view/search/results.html", context)
