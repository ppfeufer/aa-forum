"""
Views for the admin area
"""

# Standard Library
import json

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Prefetch
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Forum
from aa_forum import __title__
from aa_forum.constants import DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER
from aa_forum.forms import EditBoardForm, EditCategoryForm, NewCategoryForm, SettingForm
from aa_forum.helper.forms import message_form_errors
from aa_forum.models import Board, Category, Setting

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required
@permission_required(perm="aa_forum.manage_forum")
def categories_and_boards(request: WSGIRequest) -> HttpResponse:
    """
    Administration » Categories and Boards

    :param request:
    :type request:
    :return:
    :rtype:
    """

    categories = Category.objects.prefetch_related(
        Prefetch(
            lookup="boards",
            queryset=Board.objects.filter(parent_board__isnull=True)
            .prefetch_related("groups")
            .prefetch_related("child_boards")
            .order_by("order", "id"),
        )
    ).order_by("order", "id")

    groups_queryset = Group.objects.all()
    category_loop = []

    for category in categories:
        boards_data = []

        for board in category.boards.all():
            child_boards_data = [
                {
                    "board_obj": child_board,
                    "board_forms": {
                        "board_edit_form": EditBoardForm(
                            prefix="edit-board-" + str(child_board.id),
                            instance=child_board,
                            groups_queryset=groups_queryset,
                        ),
                    },
                }
                for child_board in board.child_boards.all()
            ]

            boards_data.append(
                {
                    "board_obj": board,
                    "board_forms": {
                        "new_child_board_form": EditBoardForm(
                            prefix="new-child-board-" + str(board.id)
                        ),
                        "board_edit_form": EditBoardForm(
                            prefix="edit-board-" + str(board.id),
                            instance=board,
                            groups_queryset=groups_queryset,
                        ),
                    },
                    "child_boards": child_boards_data,
                }
            )

        category_data = {
            "category_obj": category,
            "category_forms": {
                "new_board": EditBoardForm(
                    prefix="new-board-in-category-" + str(category.id),
                    groups_queryset=groups_queryset,
                ),
                "edit_category": EditCategoryForm(
                    prefix="edit-category-" + str(category.id), instance=category
                ),
            },
            "boards": boards_data,
        }

        category_loop.append(category_data)

    form_new_category = NewCategoryForm(prefix="new-category")

    context = {
        "new_category_form": form_new_category,
        "category_loop": category_loop,
    }

    logger.info(f"{request.user} calling admin view.")

    return render(
        request=request,
        template_name="aa_forum/view/administration/categories-and-boards.html",
        context=context,
    )


@login_required
@permission_required(perm="aa_forum.manage_forum")
def category_create(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Create a new category

    :param request:
    :type request:
    :return:
    :rtype:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = NewCategoryForm(data=request.POST, prefix="new-category")

        # Check whether it's valid:
        if form.is_valid():
            new_category = Category(
                name=form.cleaned_data["name"],
                order=DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER,
            )
            new_category.save()

            # Add boards if any given
            if form.cleaned_data["boards"] != "":
                boards = form.cleaned_data["boards"]

                for board_name in boards.splitlines():
                    Board(
                        name=board_name,
                        category=new_category,
                        order=DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER,
                    ).save()

            messages.success(
                request=request,
                message=mark_safe(s=_("<h4>Success!</h4><p>Category created.</p>")),
            )

            logger.info(msg=f'{request.user} created category "{new_category.name}".')
        else:
            message_form_errors(request=request, form=form)

    return redirect(to="aa_forum:admin_categories_and_boards")


@login_required
@permission_required(perm="aa_forum.manage_forum")
def category_edit(request: WSGIRequest, category_id: int) -> HttpResponseRedirect:
    """
    Edit a category

    :param request:
    :type request:
    :param category_id:
    :type category_id:
    :return:
    :rtype:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditCategoryForm(
            data=request.POST, prefix="edit-category-" + str(category_id)
        )

        if form.is_valid():
            category = Category.objects.get(pk=category_id)
            category_name_old = category.name

            # Set new name
            category.name = form.cleaned_data["name"]
            category.save()

            messages.success(
                request=request,
                message=mark_safe(
                    # pylint: disable=duplicate-code
                    s=_(
                        f'<h4>Success!</h4><p>Category name changed from "{category_name_old}" to "{category.name}".</p>'  # pylint: disable=line-too-long
                    )
                ),
            )

            logger.info(
                msg=(
                    f"{request.user} changed category name "
                    f'from "{category_name_old}" to "{category.name}".'
                )
            )
        else:
            message_form_errors(request=request, form=form)

    return redirect(to="aa_forum:admin_categories_and_boards")


@login_required
@permission_required(perm="aa_forum.manage_forum")
def category_delete(request: WSGIRequest, category_id: int) -> HttpResponseRedirect:
    """
    Delete a category

    :param request:
    :type request:
    :param category_id:
    :type category_id:
    :return:
    :rtype:
    """

    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        msg = f"Category with PK {category_id} not found."
        logger.warning(msg=msg)
        return HttpResponseNotFound(msg)

    category_name = category.name
    category.delete()
    messages.success(
        request=request,
        message=mark_safe(
            s=_(f'<h4>Success!</h4><p>Category "{category_name}" removed.</p>')
        ),
    )

    logger.info(msg=f'{request.user} removed category "{category_name}".')

    return redirect(to="aa_forum:admin_categories_and_boards")


@login_required
@permission_required(perm="aa_forum.manage_forum")
def board_create(request: WSGIRequest, category_id: int) -> HttpResponseRedirect:
    """
    Create a new board

    :param request:
    :type request:
    :param category_id:
    :type category_id:
    :return:
    :rtype:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditBoardForm(
            data=request.POST, prefix="new-board-in-category-" + str(category_id)
        )

        board_category = Category.objects.get(pk=category_id)

        # Check whether it's valid:
        if form.is_valid():
            discord_webhook = (
                form.cleaned_data["discord_webhook"]
                if form.cleaned_data["discord_webhook"] != ""
                else None
            )

            new_board = Board(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                category=board_category,
                discord_webhook=discord_webhook,
                use_webhook_for_replies=form.cleaned_data["use_webhook_for_replies"],
                is_announcement_board=form.cleaned_data["is_announcement_board"],
                order=DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER,
            )
            new_board.save()

            new_board.groups.set(form.cleaned_data["groups"])
            new_board.announcement_groups.set(form.cleaned_data["announcement_groups"])

            messages.success(
                request=request,
                message=mark_safe(
                    s=_(f'<h4>Success!</h4><p>Board "{new_board.name}" created.</p>')
                ),
            )

            logger.info(msg=f'{request.user} created board "{new_board.name}".')
        else:
            message_form_errors(request=request, form=form)

    return redirect(to="aa_forum:admin_categories_and_boards")


@login_required
@permission_required(perm="aa_forum.manage_forum")
def board_create_child(
    request: WSGIRequest,
    category_id: int,  # pylint: disable=unused-argument
    board_id: int,
) -> HttpResponseRedirect:
    """
    Create a new child board

    :param request:
    :type request:
    :param category_id:
    :type category_id:
    :param board_id:
    :type board_id:
    :return:
    :rtype:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditBoardForm(
            data=request.POST, prefix="new-child-board-" + str(board_id)
        )

        # Check whether it's valid:
        if form.is_valid():
            parent_board = Board.objects.get(pk=board_id)
            discord_webhook = (
                form.cleaned_data["discord_webhook"]
                if form.cleaned_data["discord_webhook"] != ""
                else None
            )

            new_board = Board(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                discord_webhook=discord_webhook,
                use_webhook_for_replies=form.cleaned_data["use_webhook_for_replies"],
                parent_board=parent_board,
                category=parent_board.category,
                order=DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER,
            )
            new_board.save()

            messages.success(
                request=request,
                message=mark_safe(
                    s=_(f'<h4>Success!</h4><p>Board "{new_board.name}" created.</p>')
                ),
            )

            logger.info(
                msg=(
                    f'{request.user} created board "{new_board.name}" '
                    f'as child board of "{parent_board.name}".'
                )
            )
        else:
            message_form_errors(request=request, form=form)

    return redirect(to="aa_forum:admin_categories_and_boards")


@login_required
@permission_required(perm="aa_forum.manage_forum")
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
    :return:
    :rtype:
    """

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditBoardForm(data=request.POST, prefix="edit-board-" + str(board_id))

        # Check whether it's valid:
        if form.is_valid():
            discord_webhook = (
                form.cleaned_data["discord_webhook"]
                if form.cleaned_data["discord_webhook"] != ""
                else None
            )

            board = Board.objects.get(pk=board_id, category_id=category_id)
            board.name = form.cleaned_data["name"]
            board.description = form.cleaned_data["description"]
            board.discord_webhook = discord_webhook
            board.use_webhook_for_replies = form.cleaned_data["use_webhook_for_replies"]
            board.groups.set(form.cleaned_data["groups"])
            board.is_announcement_board = form.cleaned_data["is_announcement_board"]
            board.announcement_groups.set(form.cleaned_data["announcement_groups"])
            board.save()

            messages.success(
                request=request,
                message=mark_safe(
                    s=_(f'<h4>Success!</h4><p>Board "{board.name}" changed.</p>')
                ),
            )

            logger.info(msg=f'{request.user} changed board "{board.name}".')
        else:
            message_form_errors(request=request, form=form)

    return redirect(to="aa_forum:admin_categories_and_boards")


@login_required
@permission_required(perm="aa_forum.manage_forum")
def board_delete(
    request: WSGIRequest,
    category_id: int,  # pylint: disable=unused-argument
    board_id: int,
) -> HttpResponseRedirect:
    """
    Delete a board

    :param request:
    :type request:
    :param category_id:
    :type category_id:
    :param board_id:
    :type board_id:
    :return:
    :rtype:
    """

    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        msg = f"Board with PK {board_id} not found."
        logger.warning(msg=msg)

        return HttpResponseNotFound(msg)

    board_name = board.name
    board.delete()

    messages.success(
        request=request,
        message=mark_safe(
            s=_(f'<h4>Success!</h4><p>Board "{board_name}" removed.</p>')
        ),
    )

    logger.info(msg=f'{request.user} removed board "{board_name}".')

    return redirect(to="aa_forum:admin_categories_and_boards")


@login_required
@permission_required(perm="aa_forum.manage_forum")
def ajax_category_order(request: WSGIRequest) -> JsonResponse:
    """
    Ajax call :: Save the category order

    :param request:
    :type request:
    :return:
    :rtype:
    """

    data = []

    if request.method == "POST":
        categories = json.loads(s=request.POST.get("categories"))

        for category in categories:
            try:
                category_obj = Category.objects.get(pk=category["catId"])
            except Category.DoesNotExist:
                category_id = category["catId"]
                logger.warning(
                    msg=(
                        f"You tried to change the order for a non existing category with ID {category_id}."  # pylint: disable=line-too-long
                    )
                )
            else:
                category_obj.order = category["catOrder"]
                category_obj.save(update_fields=["order"])

        data.append({"success": True})

    return JsonResponse(data=data, safe=False)


@login_required
@permission_required(perm="aa_forum.manage_forum")
def ajax_board_order(request: WSGIRequest) -> JsonResponse:
    """
    Ajax call :: Save the board order

    :param request:
    :type request:
    :return:
    :rtype:
    """

    data = []

    if request.method == "POST":
        boards = json.loads(request.POST.get("boards"))

        for board in boards:
            try:
                board_obj = Board.objects.get(pk=board["boardId"])
            except Board.DoesNotExist:
                board_id = board["boardId"]
                logger.warning(
                    msg=(
                        f"You tried to change the order for s non existing board with ID {board_id}."  # pylint: disable=line-too-long
                    )
                )
            else:
                board_obj.order = board["boardOrder"]
                board_obj.save(update_fields=["order"])

        data.append({"success": True})

    return JsonResponse(data=data, safe=False)


@login_required
@permission_required(perm="aa_forum.manage_forum")
def forum_settings(request: WSGIRequest) -> HttpResponse:
    """
    Administration » Forum Settings

    :param request:
    :type request:
    :return:
    :rtype:
    """

    logger.info(f"{request.user} called forum settings page.")

    settings = Setting.objects.get(pk=1)

    # If this is a POST request, we need to process the form data
    if request.method == "POST":
        settings_form = SettingForm(data=request.POST, instance=settings)

        # Check whether it's valid:
        if settings_form.is_valid():
            settings.messages_per_page = settings_form.cleaned_data["messages_per_page"]
            settings.topics_per_page = settings_form.cleaned_data["topics_per_page"]
            settings.user_signature_length = settings_form.cleaned_data[
                "user_signature_length"
            ]
            settings.save()

            messages.success(
                request=request,
                message=mark_safe(s=_("<h4>Success!</h4><p>Settings updated.</p>")),
            )

            return redirect(to="aa_forum:admin_forum_settings")

        messages.error(
            request,
            mark_safe(
                # pylint: disable=duplicate-code
                s=_(
                    "<h4>Error!</h4>"
                    "<p>Something went wrong, please check your input.</p>"
                )
            ),
        )
    else:
        settings_form = SettingForm(instance=settings)

    context = {"form": settings_form}

    return render(
        request=request,
        template_name="aa_forum/view/administration/forum-settings.html",
        context=context,
    )
