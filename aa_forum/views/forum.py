"""
Forum views
"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count, Exists, OuterRef, Prefetch, Q
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Forum
from aa_forum import __title__
from aa_forum.forms import EditMessageForm, EditTopicForm, NewTopicForm
from aa_forum.helper.discord_messages import send_message_to_discord_webhook
from aa_forum.helper.pagination import get_paginated_page_object
from aa_forum.models import Board, Category, LastMessageSeen, Message, Setting, Topic

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required
@permission_required(perm="aa_forum.basic_access")
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
    unread_topic_pks = Topic.objects.filter(
        ~Exists(queryset=has_read_all_messages)
    ).values_list("pk", flat=True)

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
                lookup="child_boards",
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
                    num_posts=Count(expression="topics__messages", distinct=True),
                    num_topics=Count(expression="topics", distinct=True),
                    num_unread=Count(
                        expression="topics",
                        filter=Q(topics__in=unread_topic_pks),
                        distinct=True,
                    ),
                )
                .user_has_access(user=request.user)
                .order_by("order", "id"),
            )
        )
        .prefetch_related(
            Prefetch(lookup="groups", queryset=Group.objects.order_by("name"))
        )
        .prefetch_related("topics")
        .user_has_access(user=request.user)
        .filter(parent_board__isnull=True)
        .annotate(
            num_posts=Count(expression="topics__messages", distinct=True),
            num_topics=Count(expression="topics", distinct=True),
            num_unread=Count(
                expression="topics",
                filter=Q(topics__in=unread_topic_pks),
                distinct=True,
            ),
        )
        .order_by("category__order", "category__id", "order", "id")
    )

    categories_map = {}

    for board_in_loop in boards:
        category = board_in_loop.category

        if category.pk not in categories_map:
            categories_map[category.pk] = {
                "id": category.id,
                "name": category.name,
                "boards_sorted": [],
                "order": category.order,
            }

        categories_map[category.pk]["boards_sorted"].append(board_in_loop)

    categories = sorted(categories_map.values(), key=lambda k: k["order"])
    context = {"categories": categories}

    logger.info(msg=f"{request.user} called forum index.")

    return render(
        request=request, template_name="aa_forum/view/forum/index.html", context=context
    )


@login_required
@permission_required(perm="aa_forum.basic_access")
def board(
    request: WSGIRequest, category_slug: str, board_slug: str, page_number: int = None
) -> HttpResponse:
    """
    View a board

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
    unread_topic_pks = Topic.objects.filter(
        ~Exists(queryset=has_read_all_messages)
    ).values_list("pk", flat=True)

    try:
        current_board = (
            Board.objects.select_related("category")
            .select_related("parent_board")
            .prefetch_related(
                Prefetch(
                    lookup="child_boards",
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
                    .prefetch_related(
                        Prefetch(
                            lookup="groups", queryset=Group.objects.order_by("name")
                        )
                    )
                    .prefetch_related("topics")
                    .annotate(
                        num_posts=Count(expression="topics__messages", distinct=True),
                        num_topics=Count(expression="topics", distinct=True),
                        num_unread=Count(
                            expression="topics",
                            filter=Q(topics__in=unread_topic_pks),
                            distinct=True,
                        ),
                    )
                    .user_has_access(user=request.user)
                    .order_by("order", "id"),
                )
            )
            .prefetch_related(
                Prefetch(
                    lookup="topics",
                    queryset=Topic.objects.select_related(
                        "last_message",
                        "last_message__user_created",
                        "last_message__user_created__profile__main_character",
                        "first_message",
                        "first_message__user_created",
                        "first_message__user_created__profile__main_character",
                    )
                    .annotate(num_posts=Count(expression="messages", distinct=True))
                    .annotate(
                        has_unread_messages=~Exists(queryset=has_read_all_messages)
                    )
                    .order_by("-is_sticky", "-last_message__time_posted", "-id"),
                    to_attr="topics_sorted",
                )
            )
            .prefetch_related(
                Prefetch(
                    lookup="announcement_groups",
                    queryset=Group.objects.order_by("name"),
                )
            )
            .filter(category__slug=category_slug, slug=board_slug)
            .user_has_access(user=request.user)
            .get()
        )
    except Board.DoesNotExist:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The board you were trying to visit does "
                    "either not exist, or you don't have access to it.</p>"
                )
            ),
        )

        logger.info(
            msg=(
                f"{request.user} called board without having access to it. "
                "Redirecting to forum index."
            )
        )

        return redirect(to="aa_forum:forum_index")

    page_obj = get_paginated_page_object(
        queryset=current_board.topics_sorted,
        items_per_page=Setting.objects.get_setting(
            setting_key=Setting.Field.TOPICSPERPAGE
        ),
        page_number=page_number,
    )

    context = {
        "board": current_board,
        "user_can_start_topic": current_board.user_can_start_topic(user=request.user),
        "page_obj": page_obj,
    }

    logger.info(msg=f'{request.user} called board "{current_board.name}".')

    return render(
        request=request, template_name="aa_forum/view/forum/board.html", context=context
    )


@login_required
@permission_required(perm="aa_forum.basic_access")
def board_new_topic(
    request: WSGIRequest, category_slug: str, board_slug: str
) -> HttpResponse:
    """
    Create a new topic in a board

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
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The category you were trying to post in "
                    "does not exist.</p>"
                )
            ),
        )

        logger.info(
            msg=(
                f"{request.user} tried to open a non existing category. "
                "Redirecting to forum index."
            )
        )

        return redirect(to="aa_forum:forum_index")

    try:
        current_board: Board = (
            Board.objects.select_related("category")
            .user_has_access(user=request.user)
            .filter(category__slug=category_slug, slug=board_slug)
            .get()
        )
    except Board.DoesNotExist:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The board you were trying to post in does "
                    "either not exist, or you don't have access to it.</p>"
                )
            ),
        )

        logger.info(
            msg=(
                f"{request.user} tried to create a topic in a board they have no "
                "access to. Redirecting to forum index."
            )
        )

        return redirect(to="aa_forum:forum_index")

    if not current_board.user_can_start_topic(user=request.user):
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The board you were trying to post in is "
                    "an announcement board and you don't have the permissions to "
                    "start a topic there.</p>"
                )
            ),
        )

        logger.info(
            msg=(
                f"{request.user} tried to create a topic in an announcement board "
                "without the permission to do so. Redirecting to board index."
            )
        )

        return redirect(
            to="aa_forum:forum_board",
            category_slug=current_board.category.slug,
            board_slug=current_board.slug,
        )

    # If this is a POST request, we need to process the form data …
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = NewTopicForm(data=request.POST)

        # Check whether it's valid:
        if form.is_valid():
            try:
                # Let's see if we can create a new topic
                new_topic = current_board.new_topic(
                    subject=form.cleaned_data["subject"],
                    message=form.cleaned_data["message"],
                    user=request.user,
                )
            except current_board.TopicAlreadyExists as exc:
                # Apparently there is already a topic with this subject
                logger.debug(msg=f"{request.user} tried to create a duplicate topic.")

                messages.warning(request=request, message=exc)

                return render(
                    request=request,
                    template_name="aa_forum/view/forum/new-topic.html",
                    context={"board": current_board, "form": form},
                )

            return redirect(
                to="aa_forum:forum_topic",
                category_slug=current_board.category.slug,
                board_slug=current_board.slug,
                topic_slug=new_topic.slug,
            )

        # The form is invalid
        messages.error(
            request=request,
            message=mark_safe(
                # pylint: disable=duplicate-code
                s=_(
                    "<h4>Error!</h4>"
                    "<p>Either subject or message is missing. "
                    "Please make sure you enter both fields, "
                    "as both fields are mandatory.</p>"
                )
            ),
        )
    # If not, we'll create a blank form
    else:
        form = NewTopicForm()

    context = {"board": current_board, "form": form}

    logger.info(
        msg=f'{request.user} is starting a new topic in board "{current_board.name}".'
    )

    return render(
        request=request,
        template_name="aa_forum/view/forum/new-topic.html",
        context=context,
    )


@login_required
@permission_required(perm="aa_forum.basic_access")
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

    current_topic = _topic_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )

    if not current_topic:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The topic you were trying to view does not "
                    "exist or you do not have access to it.</p>"
                )
            ),
        )

        logger.info(
            msg=(
                f"{request.user} called a non existent topic. Redirecting to forum index."  # pylint: disable=line-too-long
            )
        )

        return redirect(to="aa_forum:forum_index")

    # Determine if the current user can modify the topics subject
    can_modify_subject = False
    if (
        request.user == current_topic.first_message.user_created
        or request.user.has_perm(perm="aa_forum.manage_forum")
    ):
        can_modify_subject = True

    page_obj = get_paginated_page_object(
        queryset=current_topic.messages_sorted,
        items_per_page=Setting.objects.get_setting(
            setting_key=Setting.Field.MESSAGESPERPAGE
        ),
        page_number=page_number,
    )

    # Set this topic as "read by" by the current user
    try:
        last_message_on_page = page_obj.object_list[-1]
    except IndexError:
        pass
    else:
        try:
            last_message_seen = LastMessageSeen.objects.get(
                topic=current_topic, user=request.user
            )
        except LastMessageSeen.DoesNotExist:
            last_message_seen = None

        if (
            not last_message_seen
            or last_message_seen.message_time < last_message_on_page.time_posted
        ):
            LastMessageSeen.objects.update_or_create(
                topic=current_topic,
                user=request.user,
                defaults={"message_time": last_message_on_page.time_posted},
            )

    context = {
        "topic": current_topic,
        "can_modify_subject": can_modify_subject,
        "page_obj": page_obj,
        "reply_form": EditMessageForm(),
    }

    logger.info(msg=f'{request.user} called topic "{current_topic.subject}".')

    return render(
        request=request, template_name="aa_forum/view/forum/topic.html", context=context
    )


@login_required
@permission_required(perm="aa_forum.basic_access")
def topic_modify(
    request: WSGIRequest,
    category_slug: str,
    board_slug: str,
    topic_slug: str,
) -> HttpResponse:
    """
    Modify a topic subject

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

    topic_to_modify = _topic_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )

    if not topic_to_modify:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The topic you were trying to modify does "
                    "not exist or you do not have access to it.</p>"
                )
            ),
        )

        logger.info(
            msg=(
                f"{request.user} called a non existent topic. Redirecting to forum index."  # pylint: disable=line-too-long
            )
        )

        return redirect(to="aa_forum:forum_index")

    # Check if the user actually has the right to edit this message
    if (
        topic_to_modify.first_message.user_created != request.user
        and not request.user.has_perm(perm="aa_forum.manage_forum")
    ):
        messages.error(
            request=request,
            message=mark_safe(
                s=_("<h4>Error!</h4><p>You are not allowed to modify this topic!</p>")
            ),
        )

        logger.info(
            msg=(
                f'{request.user} tried to modify topic "{topic_to_modify.subject}" '
                "without the proper permissions. Redirecting to forum index."
            )
        )

        return redirect(
            to="aa_forum:forum_topic",
            category_slug=category_slug,
            board_slug=board_slug,
            topic_slug=topic_slug,
        )

    # We are in the clear, let's see what we've got
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditTopicForm(data=request.POST)

        # Check whether it's valid:
        if form.is_valid():
            topic_to_modify.subject = form.cleaned_data["subject"]
            topic_to_modify.save()

            messages.success(
                request=request,
                message=mark_safe(
                    # pylint: disable=duplicate-code
                    s=_("<h4>Success!</h4><p>The topic subject has been updated.</p>")
                ),
            )

            logger.info(
                msg=f'{request.user} modified topic "{topic_to_modify.subject}".'
            )

            return redirect(
                to="aa_forum:forum_topic",
                category_slug=category_slug,
                board_slug=board_slug,
                topic_slug=topic_slug,
            )
    # If not, we'll fill the form with the information from the message object
    else:
        form = EditTopicForm(instance=topic_to_modify)

    context = {"form": form, "topic": topic_to_modify}

    logger.info(msg=f'{request.user} modifying "{topic_to_modify.subject}".')

    return render(
        request=request,
        template_name="aa_forum/view/forum/modify-topic.html",
        context=context,
    )


def _topic_from_slugs(
    request: WSGIRequest, category_slug: str, board_slug: str, topic_slug: str
) -> Topic | None:
    """
    Helper function to get a topic from slugs

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

    current_topic = Topic.objects.get_from_slugs(
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
        user=request.user,
    )

    return current_topic


@login_required
@permission_required(perm="aa_forum.basic_access")
def topic_first_unread_message(
    request: WSGIRequest, category_slug: str, board_slug: str, topic_slug: str
) -> HttpResponse:
    """
    Redirect to the first unread message in a topic

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

    current_topic = _topic_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )

    if not current_topic:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The topic you were trying to view does not "
                    "exist or you do not have access to it.</p>"
                )
            ),
        )

        return redirect(to="aa_forum:forum_index")

    messages_sorted = current_topic.messages.order_by("time_posted")

    try:
        last_message_seen = LastMessageSeen.objects.filter(
            topic=current_topic, user=request.user
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
        return redirect(to=redirect_message.get_absolute_url())

    return redirect(to=current_topic.get_absolute_url())


def _get_boards_with_unread_topics(request: WSGIRequest):
    """
    Get all boards with unread topics

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
    unread_topic_pks = Topic.objects.filter(
        ~Exists(queryset=has_read_all_messages)
    ).values_list("pk", flat=True)

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
                lookup="topics",
                queryset=Topic.objects.select_related(
                    "last_message",
                    "last_message__user_created",
                    "last_message__user_created__profile__main_character",
                    "first_message",
                    "first_message__user_created",
                    "first_message__user_created__profile__main_character",
                )
                .filter(pk__in=unread_topic_pks)
                .annotate(num_posts=Count(expression="messages", distinct=True))
                .annotate(has_unread_messages=~Exists(queryset=has_read_all_messages))
                .order_by("-is_sticky", "-last_message__time_posted", "-id"),
            )
        )
        .filter(topics__in=unread_topic_pks)
        .user_has_access(user=request.user)
        .order_by("category__order", "category__id", "order", "id")
        .all()
        .distinct()
    )

    return boards


@login_required
@permission_required(perm="aa_forum.basic_access")
def topic_show_all_unread(request: WSGIRequest) -> HttpResponse:
    """
    Show all unread topics

    :param request:
    :type request:
    :return:
    :rtype:
    """

    context = {"boards": _get_boards_with_unread_topics(request=request)}

    logger.info(msg=f"{request.user} calling unread topics view.")

    return render(
        request=request,
        template_name="aa_forum/view/forum/unread-topics.html",
        context=context,
    )


@login_required
@permission_required(perm="aa_forum.basic_access")
def topic_reply(
    request: WSGIRequest, category_slug: str, board_slug: str, topic_slug: str
) -> HttpResponse:
    """
    Reply to a topic

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

    current_topic = _topic_from_slugs(
        request=request,
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )

    if not current_topic:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The topic you were trying to reply does not "
                    "exist or you do not have access to it.</p>"
                )
            ),
        )

        logger.info(
            msg=(
                f"{request.user} called a non existent topic. Redirecting to forum index."  # pylint: disable=line-too-long
            )
        )

        return redirect(to="aa_forum:forum_index")

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditMessageForm(data=request.POST)

        # Check whether it's valid:
        if form.is_valid():
            new_message = Message(
                topic=current_topic,
                user_created=request.user,
                message=form.cleaned_data["message"],
            )
            new_message.save()

            # Check if the user has the rights to close or reopen the topic
            if (
                request.user.has_perm(perm="aa_forum.manage_forum")
                or request.user == current_topic.first_message.user_created
            ):
                # Close the topic if requested
                if (
                    form.cleaned_data["close_topic"]
                    and not form.cleaned_data["reopen_topic"]
                ):
                    current_topic.is_locked = True
                    current_topic.save(update_fields=["is_locked"])

                # Reopen the topic if requested
                if (
                    form.cleaned_data["reopen_topic"]
                    and not form.cleaned_data["close_topic"]
                ) and request.user.has_perm(perm="aa_forum.manage_forum"):
                    current_topic.is_locked = False
                    current_topic.save(update_fields=["is_locked"])

            # Send to webhook if one is configured
            if (
                current_topic.board.discord_webhook is not None
                and current_topic.board.use_webhook_for_replies is not False
            ):
                send_message_to_discord_webhook(
                    board=current_topic.board,
                    topic=current_topic,
                    message=new_message,
                    headline=f'**New reply has been posted in topic "{current_topic.subject}"**',
                )

            logger.info(
                msg=f'{request.user} replied to topic "{current_topic.subject}".'
            )

            return redirect(
                to="aa_forum:forum_message",
                category_slug=category_slug,
                board_slug=board_slug,
                topic_slug=topic_slug,
                message_id=new_message.id,
            )

        messages.error(
            request=request,
            message=mark_safe(
                # pylint: disable=duplicate-code
                s=_(
                    "<h4>Error!</h4>"
                    "<p>Message field is mandatory and cannot be empty.</p>"
                )
            ),
        )
    else:
        messages.error(
            request=request,
            message=mark_safe(
                s=_("<h4>Error!</h4><p>Something went wrong, please try again.</p>")
            ),
        )

    return redirect(
        to="aa_forum:forum_topic",
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
    )


@login_required
@permission_required(perm="aa_forum.manage_forum")
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
        current_topic = Topic.objects.select_related("board").get(pk=topic_id)
    except Topic.DoesNotExist:
        return HttpResponseNotFound("Could not find topic.")

    if current_topic.is_locked:
        current_topic.is_locked = False

        messages.success(
            request=request,
            message=mark_safe(
                # pylint: disable=duplicate-code
                s=_(
                    f'<h4>Success!</h4><p>Topic "{current_topic}" has been unlocked/re-opened.</p>'  # pylint: disable=line-too-long
                )
            ),
        )

        logger.info(msg=f'{request.user} unlocked/re-opened topic "{current_topic}".')
    else:
        current_topic.is_locked = True

        messages.success(
            request=request,
            message=mark_safe(
                # pylint: disable=duplicate-code
                s=_(
                    f'<h4>Success!</h4><p>Topic "{current_topic}" has been locked/closed.</p>'  # pylint: disable=line-too-long
                )
            ),
        )

        logger.info(msg=f'{request.user} locked/closed "{current_topic}".')

    current_topic.save(update_fields=["is_locked"])

    return redirect(
        to="aa_forum:forum_board",
        category_slug=current_topic.board.category.slug,
        board_slug=current_topic.board.slug,
    )


@login_required
@permission_required(perm="aa_forum.manage_forum")
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
        curent_topic = Topic.objects.select_related("board").get(pk=topic_id)
    except Topic.DoesNotExist:
        return HttpResponseNotFound("Could not find topic.")

    if curent_topic.is_sticky:
        curent_topic.is_sticky = False

        messages.success(
            request=request,
            message=mark_safe(
                s=_(
                    f'<h4>Success!</h4><p>Topic "{curent_topic}" is no longer "sticky".</p>'  # pylint: disable=line-too-long
                )
            ),
        )

        logger.info(
            msg=f'{request.user} changed topic "{curent_topic}" to be no longer sticky.'
        )
    else:
        curent_topic.is_sticky = True

        messages.success(
            request=request,
            message=mark_safe(
                s=_(f'<h4>Success!</h4><p>Topic "{curent_topic}" is now "sticky".</p>')
            ),
        )

        logger.info(msg=f'{request.user} changed topic "{curent_topic}" to be sticky.')

    curent_topic.save(update_fields=["is_sticky"])

    return redirect(to=curent_topic.board.get_absolute_url())


@login_required
@permission_required(perm="aa_forum.manage_forum")
def topic_delete(request: WSGIRequest, topic_id: int) -> HttpResponseRedirect:
    """
    Delete a topic from a board

    :param request:
    :type request:
    :param topic_id:
    :type topic_id:
    :return:
    :rtype:
    """

    try:
        current_topic = Topic.objects.select_related("board").get(pk=topic_id)
    except Topic.DoesNotExist:
        return HttpResponseNotFound("Could not find topic.")

    topic__board = current_topic.board
    topic__subject = current_topic.subject

    current_topic.delete()

    messages.success(
        request=request,
        message=mark_safe(
            s=_(f'<h4>Success!</h4><p>Topic "{topic__subject}" removed.</p>')
        ),
    )

    logger.info(msg=f'{request.user} removed topic "{topic__subject}".')

    return redirect(to=topic__board.get_absolute_url())


@login_required
@permission_required(perm="aa_forum.basic_access")
def message(
    request: WSGIRequest,
    category_slug: str,  # pylint: disable=unused-argument
    board_slug: str,  # pylint: disable=unused-argument
    topic_slug: str,  # pylint: disable=unused-argument
    message_id: int,
) -> HttpResponseRedirect:
    """
    Redirect to a given message

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
        current_message = Message.objects.select_related(
            "topic", "topic__board", "topic__board__category"
        ).get(pk=message_id)
    except Message.DoesNotExist:
        messages.error(
            request=request,
            message=mark_safe(s=_("<h4>Error!</h4><p>The message doesn't exist.</p>")),
        )

        return redirect(to="aa_forum:forum_index")

    return redirect(to=current_message.get_absolute_url())


@login_required
@permission_required(perm="aa_forum.basic_access")
def message_modify(
    request: WSGIRequest,
    category_slug: str,
    board_slug: str,
    topic_slug: str,
    message_id: int,
) -> HttpResponse:
    """
    Modify a message

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
    # Either way, the message can't be edited
    if not message_to_modify:
        messages.error(
            request=request,
            message=mark_safe(
                s=_(
                    "<h4>Error!</h4><p>The message you were trying to modify does "
                    "either not exist, or you don't have access to it.</p>"
                )
            ),
        )

        logger.info(
            msg=(
                f"{request.user} trying to change a message in a topic that either "
                "does not exist or they have no access to."
            )
        )

        return redirect(to="aa_forum:forum_index")

    # Check if the user actually has the right to edit this message
    if (
        message_to_modify.user_created_id != request.user.id
        and not request.user.has_perm(perm="aa_forum.manage_forum")
    ):
        messages.error(
            request=request,
            message=mark_safe(
                s=_("<h4>Error!</h4><p>You are not allowed to modify this message!</p>")
            ),
        )

        logger.info(
            msg=(
                f"{request.user} tried to modify a message in topic "
                f'"{message_to_modify.topic.subject}" without permission to do so.'
            )
        )

        return redirect(to=message_to_modify.topic.get_absolute_url())

    # We are in the clear, let's see what we've got
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = EditMessageForm(data=request.POST)

        # Check whether it's valid:
        if form.is_valid():
            message_to_modify.user_updated = request.user
            message_to_modify.message = form.cleaned_data["message"]
            message_to_modify.save()

            messages.success(
                request=request,
                message=mark_safe(
                    s=_("<h4>Success!</h4><p>The message has been updated.</p>")
                ),
            )

            logger.info(
                msg=(
                    f"{request.user} modified message ID {message_to_modify.pk} "
                    f'in topic "{message_to_modify.topic.subject}".'
                )
            )

            return redirect(
                to="aa_forum:forum_message",
                category_slug=category_slug,
                board_slug=board_slug,
                topic_slug=topic_slug,
                message_id=message_id,
            )

        # Form invalid
        messages.error(
            request=request,
            message=mark_safe(
                s=_("<h4>Error!</h4><p>Mandatory form field is empty.</p>")
            ),
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
        msg=(
            f"{request.user} is modifying message ID {message_to_modify.pk} "
            f'in topic "{message_to_modify.topic.subject}".'
        )
    )

    return render(
        request=request,
        template_name="aa_forum/view/forum/modify-message.html",
        context=context,
    )


def _message_from_slugs(
    request: WSGIRequest,
    category_slug: str,
    board_slug: str,
    topic_slug: str,
    message_id: int,
) -> Message | None:
    """
    Helper function to get a message from slugs

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

    current_message = Message.objects.get_from_slugs(
        category_slug=category_slug,
        board_slug=board_slug,
        topic_slug=topic_slug,
        message_id=message_id,
        user=request.user,
    )

    return current_message


@login_required
@permission_required(perm="aa_forum.basic_access")
def message_delete(request: WSGIRequest, message_id: int) -> HttpResponseRedirect:
    """
    Delete a message from a topic

    :param request:
    :type request:
    :param message_id:
    :type message_id:
    :return:
    :rtype:
    """

    try:
        current_message = (
            Message.objects.select_related(
                "topic", "topic__board", "topic__board__category"
            )
            .user_has_access(user=request.user)
            .get(pk=message_id)
        )
    except Message.DoesNotExist:
        return HttpResponseNotFound("Message not found.")

    current_message__topic = current_message.topic
    current_message__topic__subject = current_message__topic.subject

    # Safety check to make sure the user is allowed to delete this message
    if (
        current_message.user_created_id != request.user.id
        and not request.user.has_perm(perm="aa_forum.manage_forum")
    ):
        messages.error(
            request=request,
            message=mark_safe(
                s=_("<h4>Error!</h4><p>You are not allowed to delete this message!</p>")
            ),
        )

        logger.info(
            msg=(
                f"{request.user} was trying to delete message ID {message_id} without "
                "permission to do so. Redirecting to forum index."
            )
        )

        return redirect(
            to="aa_forum:forum_topic",
            category_slug=current_message__topic.board.category.slug,
            board_slug=current_message__topic.board.slug,
            topic_slug=current_message__topic.slug,
        )

    # Let's check if we have more than one message in this topic
    # and the message we want to delete is not the first
    # If so, remove just that message and return to the topic
    if (
        current_message__topic.first_message.pk != current_message.pk
        and current_message__topic.messages.all().count() > 1
    ):
        current_message.delete()

        messages.success(
            request=request,
            message=mark_safe(
                s=_("<h4>Success!</h4><p>The message has been deleted.</p>")
            ),
        )

        logger.info(
            msg=(
                f"{request.user} removed message ID {message_id} "
                f'from topic "{current_message__topic__subject}".'
            )
        )

        return redirect(
            to="aa_forum:forum_topic",
            category_slug=current_message__topic.board.category.slug,
            board_slug=current_message__topic.board.slug,
            topic_slug=current_message__topic.slug,
        )

    # If it is the topics opening post …
    current_message__topic.delete()

    messages.success(
        request=request,
        message=mark_safe(
            s=_(
                "<h4>Success!</h4><p>The message has been deleted.</p>"
                "<p>This was the topics opening post, so the topic has been "
                "deleted as well.</p>"
            )
        ),
    )

    logger.info(
        msg=(
            f"{request.user} removed message ID {message_id}. This was the original "
            f'post, so the topic "{current_message__topic__subject}" has been '
            "removed as well."
        )
    )

    return redirect(
        to="aa_forum:forum_board",
        category_slug=current_message__topic.board.category.slug,
        board_slug=current_message__topic.board.slug,
    )


@login_required
@permission_required(perm="aa_forum.basic_access")
def mark_all_as_read(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Mark all topics as read

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
                lookup="topics",
                queryset=Topic.objects.select_related(
                    "last_message",
                ).annotate(has_unread_messages=~Exists(queryset=has_read_all_messages)),
            )
        )
        .user_has_access(user=request.user)
        .all()
    )

    if boards.count() > 0:
        for board_in_loop in boards:
            for topic_in_loop in board_in_loop.topics.all():
                LastMessageSeen.objects.update_or_create(
                    topic=topic_in_loop,
                    user=request.user,
                    defaults={"message_time": topic_in_loop.last_message.time_posted},
                )

    logger.info(msg=f"{request.user} marked all topics as read.")

    return redirect(to="aa_forum:forum_index")


@login_required
@permission_required(perm="aa_forum.basic_access")
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
    unread_topic_pks = Topic.objects.filter(
        ~Exists(queryset=has_read_all_messages)
    ).values_list("pk", flat=True)

    boards = (
        Board.objects.annotate(
            num_unread_topics=Count(
                expression="topics",
                filter=Q(topics__in=unread_topic_pks),
                distinct=True,
            ),
        )
        .user_has_access(user=request.user)
        .all()
    )

    count_unread_topics = 0

    if boards.count() > 0:
        for board_in_loop in boards:
            count_unread_topics += board_in_loop.num_unread_topics

    return count_unread_topics
