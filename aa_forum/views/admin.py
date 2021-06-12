"""
Administration related views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from aa_forum.forms import EditBoardForm, EditCategoryForm
from aa_forum.models import Boards, Categories


@login_required
@permission_required("aa_forum.manage_forum")
def index(request: WSGIRequest) -> HttpResponse:
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
            {
                "board_obj": board,
                "board_edit_form": EditBoardForm(
                    prefix="edit-board-" + str(board.id), instance=board
                ),
            }
            for board in category.boards.all()
        ]
        category_data = {
            "category_obj": category,
            "category_forms": {
                "new_board": EditBoardForm(
                    prefix="new-board-in-category-" + str(category.id)
                ),
                "edit_category": EditCategoryForm(
                    prefix="edit-category-" + str(category.id), instance=category
                ),
            },
            "boards": boards_data,
        }

        category_loop.append(category_data)

    form_new_category = EditCategoryForm(prefix="new-category")

    context = {
        "new_category_form": form_new_category,
        "category_loop": category_loop,
    }

    return render(request, "aa_forum/view/administration/index.html", context)


@login_required
@permission_required("aa_forum.manage_forum")
def category_create(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Create a new category
    :param request:
    :type request:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditCategoryForm(request.POST, prefix="new-category")

        # Check whether it's valid:
        if form.is_valid():
            new_category = Categories()
            new_category.name = form.cleaned_data["name"]
            new_category.order = 999999
            new_category.save()

            messages.success(
                request,
                mark_safe(_("<h4>Success!</h4><p>Category created.</p>")),
            )

    return redirect("aa_forum:admin_index")


@login_required
@permission_required("aa_forum.manage_forum")
def category_edit(request: WSGIRequest, category_id: int) -> HttpResponseRedirect:
    """
    Edit a category
    :param request:
    :type request:
    :param category_id:
    :type category_id:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditCategoryForm(
            request.POST, prefix="edit-category-" + str(category_id)
        )

        if form.is_valid():
            category = Categories.objects.get(pk=category_id)
            category.name = form.cleaned_data["name"]
            category.save()

            messages.success(
                request,
                mark_safe(_("<h4>Success!</h4><p>Category changed.</p>")),
            )

    return redirect("aa_forum:admin_index")


@login_required
@permission_required("aa_forum.manage_forum")
def category_delete(request: WSGIRequest, category_id: int) -> HttpResponseRedirect:
    """
    Edit a board
    :param request:
    :type request:
    :param category_id:
    :type category_id:
    """

    Categories.objects.get(pk=category_id).delete()

    messages.success(
        request,
        mark_safe(_("<h4>Success!</h4><p>Category removed.</p>")),
    )

    return redirect("aa_forum:admin_index")


@login_required
@permission_required("aa_forum.manage_forum")
def board_create(request: WSGIRequest, category_id: int) -> HttpResponseRedirect:
    """
    Create a new board
    :param request:
    :type request:
    :param category_id:
    :type category_id:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditBoardForm(
            request.POST, prefix="new-board-in-category-" + str(category_id)
        )
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

            messages.success(
                request,
                mark_safe(_("<h4>Success!</h4><p>Board created.</p>")),
            )

    return redirect("aa_forum:admin_index")


@login_required
@permission_required("aa_forum.manage_forum")
def board_edit(
    request: WSGIRequest, category_id: int, board_id: int
) -> HttpResponseRedirect:
    """
    Edit a board
    :param request:
    :type request:
    :param category_id:
    :type category_id:
    :param board_id:
    :type board_id:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditBoardForm(request.POST, prefix="edit-board-" + str(board_id))

        # Check whether it's valid:
        if form.is_valid():
            board = Boards.objects.get(pk=board_id, category_id=category_id)
            board.name = form.cleaned_data["name"]
            board.description = form.cleaned_data["description"]
            board.groups.set(form.cleaned_data["groups"])
            board.save()

            messages.success(
                request,
                mark_safe(_("<h4>Success!</h4><p>Board changed.</p>")),
            )

    return redirect("aa_forum:admin_index")


@login_required
@permission_required("aa_forum.manage_forum")
def board_delete(
    request: WSGIRequest, category_id: int, board_id: int
) -> HttpResponseRedirect:
    """
    Edit a board
    :param request:
    :type request:
    :param category_id:
    :type category_id:
    :param board_id:
    :type board_id:
    """

    Boards.objects.get(pk=board_id, category_id=category_id).delete()

    messages.success(
        request,
        mark_safe(_("<h4>Success!</h4><p>Board removed.</p>")),
    )

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
