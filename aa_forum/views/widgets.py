"""
Dashboard widgets
"""

# Django
from django.contrib.auth.decorators import permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

# AA Forum
from aa_forum.helper.user import get_user_profile
from aa_forum.views.forum import _get_boards_with_unread_topics


def dashboard_widgets(request):
    """
    Return the unread topics

    :param request:
    :type request:
    :return:
    :rtype:
    """

    if request.user.has_perm("aa_forum.basic_access"):
        return render_to_string(
            template_name="aa_forum/view/widgets/dashboard-widgets.html",
            context={"user_profile": get_user_profile(user=request.user)},
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

    boards = _get_boards_with_unread_topics(request=request)

    if user_profile.show_unread_topics_dashboard_widget is True and boards.count() > 0:
        return render(
            template_name="aa_forum/partials/widgets/unread-topics.html",
            context={"boards": boards},
            request=request,
        )

    return HttpResponse(status=204)
