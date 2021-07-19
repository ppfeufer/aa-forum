"""
Forum related views
"""

from typing import Optional

from app_utils.logging import LoggerAddTag

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Prefetch, Q
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from allianceauth.services.hooks import get_extension_logger

from aa_forum import __title__
from aa_forum.constants import SETTING_MESSAGESPERPAGE, SETTING_TOPICSPERPAGE
from aa_forum.forms import EditMessageForm, EditTopicForm, NewTopicForm
from aa_forum.models import Board, Category, LastMessageSeen, Message, Setting, Topic

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aa_forum.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Forum index view
    :param request:
    :type request:
    :return:
    :rtype:
    """

    has_read_all_messages = LastMessageSeen.objects.filter(
        topic=OuterRef("pk"),
        user=request.user,
        message_time__gte=OuterRef("last_message__time_posted"),
    )
    unread_topic_pks = Topic.objects.filter(~Exists(has_read_all_messages)).values_list(
        "pk", flat=True
    )

    boards = (
        Board.objects.select_related(
            "category",
            "last_message",
            "last_message__topic",
            "last_message__user_created__profile__main_character",
            "first_message",
        )
        .prefetch_related(
            Prefetch(
                "child_boards",
                queryset=Board.objects.select_related(
                    "category",
                    "parent_board",
                    "last_message",
                    "last_message__user_created",
                    "last_message__user_created__profile__main_character",
                    "first_message",
                    "first_message__user_created",
                    "first_message__user_created__profile__main_character",
                )
                .annotate(
                    num_posts=Count("topics__messages", distinct=True),
                    num_topics=Count("topics", distinct=True),
                    num_unread=Count(
                        "topics", filter=Q(topics__in=unread_topic_pks), distinct=True
                    ),
                )
                .user_has_access(request.user)
                .order_by("order", "id"),
            )
        )
        .prefetch_related("groups", "topics")
        .user_has_access(request.user)
        .filter(parent_board__isnull=True)
        .annotate(
            num_posts=Count("topics__messages", distinct=True),
            num_topics=Count("topics", distinct=True),
            num_unread=Count(
                "topics", filter=Q(topics__in=unread_topic_pks), distinct=True
            ),
        )
        .order_by("category__order", "category__id", "order", "id")
    )

    categories_map = dict()

    for board in boards:
        category = board.category

        if category.pk not in categories_map:
            categories_map[category.pk] = {
                "id": category.id,
                "name": category.name,
                "boards_sorted": list(),
                "order": category.order,
            }

        categories_map[category.pk]["boards_sorted"].append(board)

    categories = sorted(categories_map.values(), key=lambda k: k["order"])
    context = {"categories": categories}

    logger.info(f"{request.user} called forum index")

    return render(request, "aa_forum/view/forum/index.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def board(
    request: WSGIRequest, category_slug: str, board_slug: str, page_number: int = None
) -> HttpResponse:
    """
    Forum board view
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param page_number:
    :type page_number:
    :return:
    :rtype:
    """

    has_read_all_messages = LastMessageSeen.objects.filter(
        topic=OuterRef("pk"),
        user=request.user,
        message_time__gte=OuterRef("last_message__time_posted"),
    )
    unread_topic_pks = Topic.objects.filter(~Exists(has_read_all_messages)).values_list(
        "pk", flat=True
    )

    try:
        board = (
            Board.objects.select_related("category")
            .select_related("parent_board")
            .prefetch_related(
                Prefetch(
                    "child_boards",
                    queryset=Board.objects.select_related(
                        "category",
                        "parent_board",
                        "last_message",
                        "last_message__user_created",
                        "last_message__user_created__profile__main_character",
                        "first_message",
                        "first_message__user_created",
                        "first_message__user_created__profile__main_character",
                    )
                    .annotate(
                        num_posts=Count("topics__messages", distinct=True),
                        num_topics=Count("topics", distinct=True),
                        num_unread=Count(
                            "topics",
                            filter=Q(topics__in=unread_topic_pks),
                            distinct=True,
                        ),
                    )
                    .user_has_access(request.user)
                    .order_by("order", "id"),
                )
            )
            .prefetch_related(
                Prefetch(
                    "topics",
                    queryset=Topic.objects.select_related(
                        "last_message",
                        "last_message__user_created",
                        "last_message__user_created__profile__main_character",
                        "first_message",
                        "first_message__user_created",
                        "first_message__user_created__profile__main_character",
                    )
                    .annotate(num_posts=Count("messages", distinct=True))
                    .annotate(has_unread_messages=~Exists(has_read_all_messages))
                    .order_by("-is_sticky", "-last_message__time_posted", "-id"),
                    to_attr="topics_sorted",
                )
            )
            .filter(category__slug=category_slug, slug=board_slug)
            .user_has_access(request.user)
            .get()
        )
    except Board.DoesNotExist:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The board you were trying to visit does "
                    "either not exist, or you don't have access to it ...</p>"
                )
            ),
        )

        logger.info(
            f"{request.user} called board without having access to it. "
            f"Redirecting to forum index"
        )

        return redirect("aa_forum:forum_index")

    paginator = Paginator(
        board.topics_sorted,
        int(Setting.objects.get_setting(setting_key=SETTING_TOPICSPERPAGE)),
    )
    page_obj = paginator.get_page(page_number)
    context = {
        "board": board,
        "page_obj": page_obj,
    }

    logger.info(f'{request.user} called board "{board.name}"')

    return render(request, "aa_forum/view/forum/board.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def board_new_topic(
    request: WSGIRequest, category_slug: str, board_slug: str
) -> HttpResponse:
    """
    Begin a new topic
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :return:
    :rtype:
    """

    try:
        Category.objects.get(slug__exact=category_slug)
    except Category.DoesNotExist:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The category you were trying to post in does "
                    "not exist ...</p>"
                )
            ),
        )

        logger.info(f"{request.user} tried to open a non existing category")

        return redirect("aa_forum:forum_index")

    try:
        board = (
            Board.objects.select_related("category")
            .user_has_access(request.user)
            .filter(category__slug=category_slug, slug=board_slug)
            .get()
        )
    except Board.DoesNotExist:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The board you were trying to post in does "
                    "either not exist, or you don't have access to it ...</p>"
                )
            ),
        )

        logger.info(
            f"{request.user} tried to create a topic in a board they have no access "
            f"to. Redirecting to forum index "
        )

        return redirect("aa_forum:forum_index")

    # If this is a POST request we need to process the form data ...
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = NewTopicForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            with transaction.atomic():
                topic = Topic()
                topic.board = board
                topic.subject = form.cleaned_data["subject"]
                topic.save()

                message = Message()
                message.topic = topic
                message.user_created = request.user
                message.message = form.cleaned_data["message"]
                message.save()

            logger.info(
                f'{request.user} started a new topic "{topic.subject}" '
                f'in board "{board.name}"'
            )

            return redirect(
                "aa_forum:forum_topic",
                category_slug=board.category.slug,
                board_slug=board.slug,
                topic_slug=topic.slug,
            )
    # If not, we'll create a blank form
    else:
        form = NewTopicForm()

    context = {"board": board, "form": form}

    logger.info(f'{request.user} is starting a new topic in board "{board.name}"')

    return render(request, "aa_forum/view/forum/new-topic.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def topic(
    request: WSGIRequest,
    category_slug: str,
    board_slug: str,
    topic_slug: str,
    page_number: int = None,
) -> HttpResponse:
    """
    View a topic
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param topic_slug:
    :type topic_slug:
    :param page_number:
    :type page_number:
    :return:
    :rtype:
    """

    topic = _topic_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )

    if not topic:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The topic you were trying to view does not "
                    "exist or you do not have access to it.</p>"
                )
            ),
        )

        logger.info(
            f"{request.user} called a non existent topic. Redirecting to forum index"
        )

        return redirect("aa_forum:forum_index")

    # Determine if the current user can modify the topics subject
    can_modify_subject = False
    if request.user == topic.first_message.user_created or request.user.has_perm(
        "aa_forum.manage_forum"
    ):
        can_modify_subject = True

    # Set this topic as "read by" by the current user
    paginator = Paginator(
        topic.messages_sorted,
        int(Setting.objects.get_setting(setting_key=SETTING_MESSAGESPERPAGE)),
    )
    page_obj = paginator.get_page(page_number)

    try:
        last_message_on_page = page_obj.object_list[-1]
    except IndexError:
        pass
    else:
        try:
            last_message_seen = LastMessageSeen.objects.get(
                topic=topic, user=request.user
            )
        except LastMessageSeen.DoesNotExist:
            last_message_seen = None

        if (
            not last_message_seen
            or last_message_seen.message_time < last_message_on_page.time_posted
        ):
            LastMessageSeen.objects.update_or_create(
                topic=topic,
                user=request.user,
                defaults={"message_time": last_message_on_page.time_posted},
            )

    context = {
        "topic": topic,
        "can_modify_subject": can_modify_subject,
        "page_obj": page_obj,
        "reply_form": EditMessageForm(),
    }

    logger.info(f'{request.user} called topic "{topic.subject}"')

    return render(request, "aa_forum/view/forum/topic.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def topic_modify(
    request: WSGIRequest,
    category_slug: str,
    board_slug: str,
    topic_slug: str,
) -> HttpResponse:
    """
    Modify the topics subject
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param topic_slug:
    :type topic_slug:
    """

    topic_to_modify = _topic_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )

    if not topic_to_modify:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The topic you were trying to modify does not "
                    "exist or you do not have access to it.</p>"
                )
            ),
        )

        logger.info(
            f"{request.user} called a non existent topic. Redirecting to forum index"
        )

        return redirect("aa_forum:forum_index")

    # Check if the user actually has the right to edit this message
    if (
        topic_to_modify.first_message.user_created != request.user
        and not request.user.has_perm("aa_forum.manage_forum")
    ):
        messages.error(
            request,
            mark_safe(
                _("<h4>Error!</h4><p>You are not allowed to modify this topic!</p>")
            ),
        )

        logger.info(
            f'{request.user} tried to modify topic "{topic_to_modify.subject}" '
            f"without the proper permissions. Redirecting to forum index"
        )

        return redirect(
            "aa_forum:forum_topic",
            category_slug=category_slug,
            board_slug=board_slug,
            topic_slug=topic_slug,
        )

    # We are in the clear, let's see what we've got
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditTopicForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            topic_to_modify.subject = form.cleaned_data["subject"]
            topic_to_modify.save()

            messages.success(
                request,
                mark_safe(
                    _("<h4>Success!</h4><p>The topic subject has been updated.</p>")
                ),
            )

            logger.info(f'{request.user} modified topic "{topic_to_modify.subject}"')

            return redirect(
                "aa_forum:forum_topic",
                category_slug=category_slug,
                board_slug=board_slug,
                topic_slug=topic_slug,
            )
    # If not, we'll fill the form with the information from the message object
    else:
        form = EditTopicForm(instance=topic_to_modify)

    context = {"form": form, "topic": topic_to_modify}

    logger.info(f'{request.user} modifying "{topic_to_modify.subject}"')

    return render(request, "aa_forum/view/forum/modify-topic.html", context)


def _topic_from_slugs(
    request: WSGIRequest, category_slug: str, board_slug: str, topic_slug: str
) -> Optional[Topic]:
    """
    Fetch topic from given slug params.
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param topic_slug:
    :type topic_slug:
    :return:
    :rtype:
    """

    topic = Topic.objects.get_from_slugs(
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
        user=request.user,
    )

    return topic


@login_required
@permission_required("aa_forum.basic_access")
def topic_first_unread_message(
    request: WSGIRequest, category_slug: str, board_slug: str, topic_slug: str
) -> HttpResponse:
    """
    Redirect to first unread message of a topic.
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param topic_slug:
    :type topic_slug:
    :return:
    :rtype:
    """

    topic = _topic_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )

    if not topic:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The topic you were trying to view does not "
                    "exist or you do not have access to it.</p>"
                )
            ),
        )

        return redirect("aa_forum:forum_index")

    messages_sorted = topic.messages.order_by("time_posted")

    try:
        last_message_seen = LastMessageSeen.objects.filter(
            topic=topic, user=request.user
        ).get()
    except LastMessageSeen.DoesNotExist:
        redirect_message = messages_sorted.first()
    else:
        redirect_message = messages_sorted.filter(
            time_posted__gt=last_message_seen.message_time
        ).first()

        if not redirect_message:
            redirect_message = messages_sorted.last()

    if redirect_message:
        return redirect(redirect_message.get_absolute_url())

    return redirect(topic.get_absolute_url())


@login_required
@permission_required("aa_forum.basic_access")
def topic_show_all_unread(request: WSGIRequest) -> HttpResponse:
    """
    Show all available unread topics
    :param request:
    :type request:
    """

    has_read_all_messages = LastMessageSeen.objects.filter(
        topic=OuterRef("pk"),
        user=request.user,
        message_time__gte=OuterRef("last_message__time_posted"),
    )
    unread_topic_pks = Topic.objects.filter(~Exists(has_read_all_messages)).values_list(
        "pk", flat=True
    )

    boards = (
        Board.objects.select_related(
            "parent_board",
            "category",
            "last_message",
            "last_message__topic",
            "last_message__user_created__profile__main_character",
            "first_message",
        )
        .prefetch_related(
            Prefetch(
                "topics",
                queryset=Topic.objects.select_related(
                    "last_message",
                    "last_message__user_created",
                    "last_message__user_created__profile__main_character",
                    "first_message",
                    "first_message__user_created",
                    "first_message__user_created__profile__main_character",
                )
                .filter(pk__in=unread_topic_pks)
                .annotate(num_posts=Count("messages", distinct=True))
                .annotate(has_unread_messages=~Exists(has_read_all_messages))
                .order_by("-is_sticky", "-last_message__time_posted", "-id"),
                # to_attr="topics_sorted",
            )
        )
        .filter(topics__in=unread_topic_pks)
        .user_has_access(request.user)
        .order_by("category__order", "category__id", "order", "id")
        .all()
    )

    context = {"boards": boards}

    logger.info(f"{request.user} calling unread topics view")

    return render(request, "aa_forum/view/forum/unread-topics.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def topic_reply(
    request: WSGIRequest, category_slug: str, board_slug: str, topic_slug: str
) -> HttpResponse:
    """
    Reply to a post in a topic
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param topic_slug:
    :type topic_slug:
    :return:
    :rtype:
    """

    topic = _topic_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )

    if not topic:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The topic you were trying to reply does not "
                    "exist or you do not have access to it.</p>"
                )
            ),
        )

        logger.info(
            f"{request.user} called a non existent topic. Redirecting to forum index"
        )

        return redirect("aa_forum:forum_index")

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditMessageForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            new_message = Message()
            new_message.topic = topic
            new_message.user_created = request.user
            new_message.message = form.cleaned_data["message"]
            new_message.save()

            logger.info(f"{request.user} replied to topic {topic.subject}")

            return redirect(
                "aa_forum:forum_message",
                category_slug=category_slug,
                board_slug=board_slug,
                topic_slug=topic_slug,
                message_id=new_message.id,
            )

    messages.warning(
        request,
        mark_safe(_("<h4>Warning!</h4><p>Something went wrong, please try again</p>.")),
    )

    return redirect("aa_forum:forum_topic", category_slug, board_slug, topic_slug)


@login_required
@permission_required("aa_forum.manage_forum")
def topic_change_lock_state(
    request: WSGIRequest, topic_id: int
) -> HttpResponseRedirect:
    """
    Change the lock state of the given topic
    :param request:
    :type request:
    :param topic_id:
    :type topic_id:
    :return:
    :rtype:
    """

    try:
        topic = Topic.objects.select_related("board").get(pk=topic_id)
    except Topic.DoesNotExist:
        return HttpResponseNotFound("Could not find topic.")

    if topic.is_locked:
        topic.is_locked = False

        messages.success(
            request,
            mark_safe(_("<h4>Success!</h4><p>Topic has been unlocked/re-opened.</p>")),
        )

        logger.info(f"{request.user} unlocked/re-opened topic {topic.subject}")
    else:
        topic.is_locked = True

        messages.success(
            request,
            mark_safe(_("<h4>Success!</h4><p>Topic has been locked/closed.</p>")),
        )

        logger.info(f'{request.user} locked/closed "{topic.subject}"')

    topic.save(update_fields=["is_locked"])

    return redirect("aa_forum:forum_board", topic.board.category.slug, topic.board.slug)


@login_required
@permission_required("aa_forum.manage_forum")
def topic_change_sticky_state(
    request: WSGIRequest, topic_id: int
) -> HttpResponseRedirect:
    """
    Change the sticky state of the given topic
    :param request:
    :type request:
    :param topic_id:
    :type topic_id:
    :return:
    :rtype:
    """

    try:
        topic = Topic.objects.select_related("board").get(pk=topic_id)
    except Topic.DoesNotExist:
        return HttpResponseNotFound("Could not find topic.")

    if topic.is_sticky:
        topic.is_sticky = False

        messages.success(
            request,
            mark_safe(_('<h4>Success!</h4><p>Topic is no longer "Sticky".</p>')),
        )

        logger.info(
            f'{request.user} changed topic "{topic.subject}" to be no longer sticky'
        )
    else:
        topic.is_sticky = True

        messages.success(
            request,
            mark_safe(_('<h4>Success!</h4><p>Topic is now "Sticky".</p>')),
        )

        logger.info(f'{request.user} changed topic "{topic.subject}" to be sticky')

    topic.save(update_fields=["is_sticky"])

    return redirect(topic.board.get_absolute_url())


@login_required
@permission_required("aa_forum.manage_forum")
def topic_delete(request: WSGIRequest, topic_id: int) -> HttpResponseRedirect:
    """
    Delete a given topic
    :param request:
    :type request:
    :param topic_id:
    :type topic_id:
    :return:
    :rtype:
    """

    try:
        topic = Topic.objects.select_related("board").get(pk=topic_id)
    except Topic.DoesNotExist:
        return HttpResponseNotFound("Could not find topic.")

    board = topic.board
    topic_subject = topic.subject

    topic.delete()

    messages.success(
        request,
        mark_safe(_("<h4>Success!</h4><p>Topic removed.</p>")),
    )

    logger.info(f'{request.user} removed topic "{topic_subject}"')

    return redirect(board.get_absolute_url())


@login_required
@permission_required("aa_forum.basic_access")
def message(
    request: WSGIRequest,
    category_slug: str,
    board_slug: str,
    topic_slug: str,
    message_id: int,
) -> HttpResponseRedirect:
    """
    Get a messages' entry point in a topic, so we end up on the right page with it
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param topic_slug:
    :type topic_slug:
    :param message_id:
    :type message_id:
    :return:
    :rtype:
    """

    try:
        message = Message.objects.select_related(
            "topic", "topic__board", "topic__board__category"
        ).get(pk=message_id)
    except Message.DoesNotExist:
        messages.error(
            request,
            mark_safe(_("<h4>Error!</h4><p>The message doesn't exist ...</p>")),
        )

        return redirect("aa_forum:forum_index")

    return redirect(message.get_absolute_url())


@login_required
@permission_required("aa_forum.basic_access")
def message_modify(
    request: WSGIRequest,
    category_slug: str,
    board_slug: str,
    topic_slug: str,
    message_id: int,
) -> HttpResponse:
    """
    Modify a given message
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param topic_slug:
    :type topic_slug:
    :param message_id:
    :type message_id:
    :return:
    :rtype:
    """

    message_to_modify = _message_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
        message_id=message_id,
    )

    # Check if the message exists.
    # If not, the user doesn't have access to its board, or it doesn't exist.
    # Either way, message can't be edited
    if not message_to_modify:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The message you were trying to modify does "
                    "either not exist, or you don't have access to it ...</p>"
                )
            ),
        )

        logger.info(
            f"{request.user} trying to change a message in a topic that either does "
            f"not exist or they have no access to"
        )

        return redirect("aa_forum:forum_index")

    # Check if the user actually has the right to edit this message
    if (
        message_to_modify.user_created_id != request.user.id
        and not request.user.has_perm("aa_forum.manage_forum")
    ):
        messages.error(
            request,
            mark_safe(
                _("<h4>Error!</h4><p>You are not allowed to modify this message!</p>")
            ),
        )

        logger.info(
            f"{request.user} tried to modify a message in topic "
            f'"{message_to_modify.topic.subject}" without permission to do so'
        )

        return redirect(message_to_modify.topic.get_absolute_url())

    # We are in the clear, let's see what we've got
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditMessageForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            message_to_modify.user_updated = request.user
            message_to_modify.message = form.cleaned_data["message"]
            message_to_modify.save()

            messages.success(
                request,
                mark_safe(_("<h4>Success!</h4><p>The message has been updated.</p>")),
            )

            logger.info(
                f"{request.user} modified message ID {message_to_modify.pk} "
                f'in topic "{message_to_modify.topic.subject}"'
            )

            return redirect(
                "aa_forum:forum_message",
                category_slug=category_slug,
                board_slug=board_slug,
                topic_slug=topic_slug,
                message_id=message_id,
            )
    # If not, we'll fill the form with the information from the message object
    else:
        form = EditMessageForm(instance=message_to_modify)

    context = {
        "form": form,
        "board": message_to_modify.topic.board,
        "message": message_to_modify,
    }

    logger.info(
        f"{request.user} is modifying message ID {message_to_modify.pk} "
        f'in topic "{message_to_modify.topic.subject}"'
    )

    return render(request, "aa_forum/view/forum/modify-message.html", context)


def _message_from_slugs(
    request: WSGIRequest,
    category_slug: str,
    board_slug: str,
    topic_slug: str,
    message_id: int,
) -> Optional[Message]:
    """

    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    :param topic_slug:
    :type topic_slug:
    :param message_id:
    :type message_id:
    :return:
    :rtype:
    """

    message = Message.objects.get_from_slugs(
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
        message_id=message_id,
        user=request.user,
    )

    return message


@login_required
@permission_required("aa_forum.basic_access")
def message_delete(request: WSGIRequest, message_id: int) -> HttpResponseRedirect:
    """
    Delete a message from a topic
    If it is the last message in this topic, the topic will be removed as well
    :param request:
    :type request:
    :param message_id:
    :type message_id:
    :return:
    :rtype:
    """

    try:
        message = (
            Message.objects.select_related(
                "topic", "topic__board", "topic__board__category"
            )
            .user_has_access(request.user)
            .get(pk=message_id)
        )
    except Message.DoesNotExist:
        return HttpResponseNotFound("Message not found.")

    topic = message.topic
    topic_subject = topic.subject

    # Safety check to make sure the user is allowed to delete this message
    if message.user_created_id != request.user.id and not request.user.has_perm(
        "aa_forum.manage_forum"
    ):
        messages.error(
            request,
            mark_safe(
                _("<h4>Error!</h4><p>You are not allowed to delete this message.</p>")
            ),
        )

        logger.info(
            f"{request.user} was trying to delete message ID {message_id} without "
            f"permission to do so. Redirecting to forum index"
        )

        return redirect(
            "aa_forum:forum_topic",
            category_slug=topic.board.category.slug,
            board_slug=topic.board.slug,
            topic_slug=topic.slug,
        )

    # Let's check if we have more than one message in this topic
    # and the message we want to delete is not the first
    # If so, remove just that message and return to the topic
    if topic.first_message.pk != message.pk and topic.messages.all().count() > 1:
        message.delete()

        messages.success(
            request,
            mark_safe(_("<h4>Success!</h4><p>The message has been deleted.</p>")),
        )

        logger.info(
            f"{request.user} removed message ID {message_id} "
            f'from topic "{topic_subject}"'
        )

        return redirect(
            "aa_forum:forum_topic",
            category_slug=topic.board.category.slug,
            board_slug=topic.board.slug,
            topic_slug=topic.slug,
        )

    # If it is the topics opening post ...
    topic.delete()

    messages.success(
        request,
        mark_safe(
            _(
                "<h4>Success!</h4><p>The message has been deleted.</p>"
                "<p>This was the topics opening post, so the topic has been "
                "deleted as well</p>"
            )
        ),
    )

    logger.info(
        f"{request.user} removed message ID {message_id}. This was the original post, "
        f'so the topic "{topic_subject}" has been removed as well.'
    )

    return redirect(
        "aa_forum:forum_board",
        category_slug=topic.board.category.slug,
        board_slug=topic.board.slug,
    )


@login_required
@permission_required("aa_forum.basic_access")
def mark_all_as_read(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Mark all available topics as read
    :param request:
    :type request:
    :return:
    :rtype:
    """

    has_read_all_messages = LastMessageSeen.objects.filter(
        topic=OuterRef("pk"),
        user=request.user,
        message_time__gte=OuterRef("last_message__time_posted"),
    )

    boards = (
        Board.objects.prefetch_related(
            Prefetch(
                "topics",
                queryset=Topic.objects.select_related(
                    "last_message",
                ).annotate(has_unread_messages=~Exists(has_read_all_messages)),
            )
        )
        .user_has_access(request.user)
        .all()
    )

    if boards.count() > 0:
        for board in boards:
            for topic in board.topics.all():
                LastMessageSeen.objects.update_or_create(
                    topic=topic,
                    user=request.user,
                    defaults={"message_time": topic.last_message.time_posted},
                )

    logger.info(f"{request.user} marked all topics as read")

    return redirect("aa_forum:forum_index")


@login_required
@permission_required("aa_forum.basic_access")
def unread_topics_count(request: WSGIRequest) -> int:
    """
    Get the number of unread messages for the user
    :param request:
    :type request:
    :return:
    :rtype:
    """

    has_read_all_messages = LastMessageSeen.objects.filter(
        topic=OuterRef("pk"),
        user=request.user,
        message_time__gte=OuterRef("last_message__time_posted"),
    )
    unread_topic_pks = Topic.objects.filter(~Exists(has_read_all_messages)).values_list(
        "pk", flat=True
    )

    boards = (
        Board.objects.annotate(
            num_unread_topics=Count(
                "topics", filter=Q(topics__in=unread_topic_pks), distinct=True
            ),
        )
        .user_has_access(request.user)
        .all()
    )

    count_unread_topics = 0

    if boards.count() > 0:
        for board in boards:
            count_unread_topics += board.num_unread_topics

    return count_unread_topics
