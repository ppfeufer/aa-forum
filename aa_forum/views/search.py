"""
Search related views
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from aa_forum.constants import SETTING_MESSAGESPERPAGE
from aa_forum.models import Board, Message, Setting


@login_required
@permission_required("aa_forum.basic_access")
def results(request: WSGIRequest, page_number: int = None) -> HttpResponse:
    """
    Search results view
    :param request:
    :type request:
    :param page_number:
    :type page_number:
    :return:
    :rtype:
    """

    if request.GET:
        search_term = request.GET.get("q")
    else:
        search_term = ""

    search_results = None
    page_obj = None

    if search_term != "":
        boards = (
            Board.objects.filter(
                Q(groups__in=request.user.groups.all()) | Q(groups__isnull=True),
                parent_board__isnull=True,
            )
            .distinct()
            .values_list("pk", flat=True)
        )

        search_results = (
            Message.objects.filter(
                Q(message__icontains=search_term),
                # | Q(topic__subject__icontains=search_term),
                topic__board__pk__in=boards,
            )
            .select_related(
                "user_created",
                "user_created__profile__main_character",
                "topic",
                "topic__slug",
                "topic__first_message",
                "topic__board",
                "topic__board__slug",
                "topic__board__category",
                "topic__board__category__slug",
            )
            .order_by("time_modified")
            .distinct()
        )

        paginator = Paginator(
            search_results,
            int(Setting.objects.get_setting(setting_key=SETTING_MESSAGESPERPAGE)),
        )
        page_obj = paginator.get_page(page_number)

    context = {
        "search_term": search_term,
        "search_results": page_obj,
        "search_results_count": 0 if search_results is None else search_results.count(),
    }

    return render(request, "aa_forum/view/search/results.html", context)
