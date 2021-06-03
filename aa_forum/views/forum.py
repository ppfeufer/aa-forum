"""
Forum related views
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render

from aa_forum.models import Boards, Categories


@login_required
@permission_required("aa_forum.basic_access")
def forum_index(request: WSGIRequest) -> HttpResponse:
    """
    Forum index
    :param request:
    :type request:
    """

    categories = Categories.objects.all().distinct().order_by("order")

    categories_for_user = []
    for category in categories:
        boards = (
            Boards.objects.filter(
                Q(groups__in=request.user.groups.all()) | Q(groups__isnull=True),
                category=category,
            )
            .annotate(num_topics=Count("topics"))
            .annotate(num_posts=Count("messages"))
            .distinct()
            .order_by("order")
        )

        if boards:
            categories_for_user.append(
                {"name": category.name, "slug": category.slug.slug, "boards": boards}
            )

    context = {"categories": categories_for_user}

    return render(request, "aa_forum/view/forum/index.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def forum_board(
    request: WSGIRequest, category_slug: str, board_slug: str
) -> HttpResponse:
    """
    Forum board
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    """

    try:
        board = Boards.objects.get(
            Q(groups__in=request.user.groups.all()) | Q(groups__isnull=True),
            category__slug__slug=category_slug,
            slug__slug=board_slug,
        )
    except Boards.DoesNotExist:
        board = None

    context = {"board": board}

    return render(request, "aa_forum/view/forum/board.html", context)
