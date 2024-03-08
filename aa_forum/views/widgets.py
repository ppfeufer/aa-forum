"""
Dashboard widgets
"""

# Django
from django.contrib.auth.decorators import permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count, Exists, OuterRef, Prefetch
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

# AA Forum
from aa_forum.helper.user import get_user_profile
from aa_forum.models import Board, LastMessageSeen, Topic


def unread_topics(request):
    """
    Return the unread topics

    :param request:
    :type request:
    :return:
    :rtype:
    """

    user_profile = get_user_profile(user=request.user)

    if (
        user_profile.show_unread_topics_dashboard_widget is True
        and request.user.has_perm("aa_forum.basic_access")
    ):
        return render_to_string(
            template_name="aa_forum/view/widgets/unread-topics.html",
            request=request,
        )

    return ""


@permission_required(perm="aa_forum.basic_access")
def ajax_unread_topics(request: WSGIRequest) -> HttpResponse:
    """
    AJAX Unread Topics widget

    :param request:
    :type request:
    :return:
    :rtype:
    """

    user_profile = get_user_profile(user=request.user)

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
            "parent_board",
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

    if user_profile.show_unread_topics_dashboard_widget is True and boards.count() > 0:
        return render(
            template_name="aa_forum/partials/widgets/unread-topics.html",
            context={"boards": boards},
            request=request,
        )

    return HttpResponse(status=204)
