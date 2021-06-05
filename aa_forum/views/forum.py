"""
Forum related views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from aa_forum.constants import MESSAGES_PER_PAGE
from aa_forum.forms import NewTopicForm
from aa_forum.models import Boards, Categories, Messages, Topics


@login_required
@permission_required("aa_forum.basic_access")
def forum_index(request: WSGIRequest) -> HttpResponse:
    """
    Forum index view
    :param request:
    :type request:
    """

    categories_for_user = []
    categories = Categories.objects.all().distinct().order_by("order")

    if categories:
        for category in categories:
            boards = (
                Boards.objects.filter(
                    Q(groups__in=request.user.groups.all()) | Q(groups__isnull=True),
                    category=category,
                    parent_board__isnull=True,
                )
                .distinct()
                .annotate(
                    num_posts=Count("messages", distinct=True),
                    num_topics=Count("topics", distinct=True),
                )
                .order_by("order")
            )

            if boards:
                categories_for_user.append(
                    {
                        "name": category.name,
                        "id": category.id,
                        "slug": category.slug.slug,
                        "boards": boards,
                    }
                )

    context = {"categories": categories_for_user}

    return render(request, "aa_forum/view/forum/index.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def forum_board(
    request: WSGIRequest, category_slug: str, board_slug: str
) -> HttpResponse:
    """
    Forum board view
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    """

    try:
        board = (
            Boards.objects.filter(
                Q(groups__in=request.user.groups.all()) | Q(groups__isnull=True),
                category__slug__slug__exact=category_slug,
                slug__slug__exact=board_slug,
            )
            .distinct()
            .get()
        )

    except Boards.DoesNotExist:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The board you were trying to visit does "
                    "either not exist, or you don't have access to it ...</p> "
                )
            ),
        )

        return redirect("aa_forum:forum_index")

    context = {"board": board}

    return render(request, "aa_forum/view/forum/board.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def forum_board_new_topic(
    request: WSGIRequest, category_slug: str, board_slug: str
) -> HttpResponse:
    """
    Start a new topic
    :param request:
    :type request:
    :param category_slug:
    :type category_slug:
    :param board_slug:
    :type board_slug:
    """

    try:
        Categories.objects.get(slug__slug__exact=category_slug)
    except Categories.DoesNotExist:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The category you were trying to post in does "
                    "not exist ...</p> "
                )
            ),
        )

        return redirect("aa_forum:forum_index")

    try:
        board = (
            Boards.objects.filter(
                Q(groups__in=request.user.groups.all()) | Q(groups__isnull=True),
                category__slug__slug__exact=category_slug,
                slug__slug__exact=board_slug,
            )
            .distinct()
            .get()
        )
    except Boards.DoesNotExist:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The board you were trying to post in does "
                    "either not exist, or you don't have access to it ...</p> "
                )
            ),
        )

        return redirect("aa_forum:forum_index")

    # If this is a POST request we need to process the form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = NewTopicForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            user_started = request.user
            user_updated = request.user
            post_time = timezone.now()

            topic = Topics()
            topic.board = board
            topic.user_started = user_started
            topic.user_updated = user_updated
            topic.time_modified = post_time
            topic.subject = form.cleaned_data["subject"]
            topic.save()

            topic.read_by.add(user_updated)

            message = Messages()
            message.topic = topic
            message.board = board
            message.user_created = user_started
            message.message = form.cleaned_data["message"]
            message.save()

            return redirect(
                "aa_forum:forum_board",
                category_slug=board.category.slug.slug,
                board_slug=board.slug.slug,
            )

    # If not, we'll create a blank form
    else:
        # logger.debug(f"Returning blank SRP request form for {request.user}")

        form = NewTopicForm()

    context = {"board": board, "form": form}

    return render(request, "aa_forum/view/forum/new-topic.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def forum_topic(
    request: WSGIRequest, category_slug: str, board_slug: str, topic_slug: str
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
    """

    try:
        Boards.objects.filter(
            Q(groups__in=request.user.groups.all()) | Q(groups__isnull=True),
            category__slug__slug__exact=category_slug,
            slug__slug__exact=board_slug,
        ).distinct().get()
    except Boards.DoesNotExist:
        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4><p>The topic you were trying to view does "
                    "either not exist, or you don't have access to it ...</p> "
                )
            ),
        )

        return redirect("aa_forum:forum_index")

    first_message = Messages.objects.get(slug__slug__exact=topic_slug)
    topic = Topics.objects.get(id=first_message.topic_id)
    topic_messages = Messages.objects.filter(topic=topic)

    paginator = Paginator(topic_messages, MESSAGES_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"first_message": first_message, "page_obj": page_obj}

    return render(request, "aa_forum/view/forum/topic.html", context)
