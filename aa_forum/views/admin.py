"""
Administration related views
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from aa_forum.models import Boards, Categories


@login_required
@permission_required("aa_forum.manage_forum")
def admin_index(request: WSGIRequest) -> HttpResponse:
    """
    Administration index view
    :param request:
    :type request:
    :return:
    :rtype:
    """

    categories = (
        Categories.objects.prefetch_related(
            Prefetch(
                "boards",
                queryset=Boards.objects.filter(parent_board__isnull=True).order_by(
                    "order"
                ),
                # to_attr="category_boards",
            )
        )
        .all()
        .order_by("order")
    )

    context = {"categories": categories}

    return render(request, "aa_forum/view/administration/index.html", context)


@login_required
@permission_required("aa_forum.manage_forum")
def ajax_category_order(request: WSGIRequest) -> JsonResponse:
    """
    Ajax call :: Save the category order
    :param request:
    :type request:
    """

    data = list()

    if request.method == "POST":
        import simplejson

        categories = simplejson.loads(request.POST.get("categories"))

        for category in categories:
            Categories.objects.update_or_create(
                pk=category["catId"],
                defaults={"order": category["catOrder"]},
            )

        data.append({"success": True})

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aa_forum.manage_forum")
def ajax_board_order(request: WSGIRequest) -> JsonResponse:
    """
    Ajax call :: Save the board order
    :param request:
    :type request:
    """

    data = list()

    if request.method == "POST":
        import simplejson

        boards = simplejson.loads(request.POST.get("boards"))

        for board in boards:
            Boards.objects.update_or_create(
                pk=board["boardId"],
                defaults={"order": board["boardOrder"]},
            )

        data.append({"success": True})

    return JsonResponse(data, safe=False)
