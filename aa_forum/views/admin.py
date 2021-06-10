"""
Administration related views
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from aa_forum.forms import EditBoardForm, EditCategoryForm
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
            )
        )
        .all()
        .order_by("order")
    )

    category_loop = list()
    for category in categories:
        boards_data = [
            {"board_obj": board, "board_form": EditBoardForm(prefix=board.id)}
            for board in category.boards.all()
        ]
        category_data = {
            "category_obj": category,
            "category_form": EditBoardForm(prefix=category.id),
            "boards": boards_data,
        }
        category_loop.append(category_data)

    # Forms
    form_new_category = EditCategoryForm()

    context = {
        "new_category_form": form_new_category,
        "category_loop": category_loop,
    }

    return render(request, "aa_forum/view/administration/index.html", context)


@login_required
@permission_required("aa_forum.manage_forum")
def admin_category_create(request: WSGIRequest) -> HttpResponse:
    """
    Create a new category
    :param request:
    :type request:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditCategoryForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            new_category = Categories()
            new_category.name = form.cleaned_data["name"]
            new_category.order = 999999
            new_category.save()

    return redirect("aa_forum:admin_index")


@login_required
@permission_required("aa_forum.manage_forum")
def admin_board_create(request: WSGIRequest, category_id: int) -> HttpResponse:
    """
    Create a new board
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditBoardForm(request.POST, prefix=category_id)

        board_category = Categories.objects.get(pk=category_id)

        # Check whether it's valid:
        if form.is_valid():
            new_board = Boards()
            new_board.name = form.cleaned_data["name"]
            new_board.description = form.cleaned_data["description"]
            new_board.category = board_category
            new_board.order = 999999
            new_board.save()

            new_board.groups.set(form.cleaned_data["groups"])

    return redirect("aa_forum:admin_index")


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
