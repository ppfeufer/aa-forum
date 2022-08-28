"""
Messages views
"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Forum
from aa_forum import __title__
from aa_forum.models import PersonalMessage, Setting

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aa_forum.basic_access")
def inbox(request: WSGIRequest, page_number: int = None) -> HttpResponse:
    """
    Messages overview
    :param request:
    :param page_number:
    :return:
    """

    logger.info(f"{request.user} called their messages overview")

    personal_messages = (
        PersonalMessage.objects.filter(recipient=request.user)
        .select_related("sender", "sender__profile", "sender__profile__main_character")
        .order_by("time_sent")
    )

    paginator = Paginator(
        personal_messages,
        int(Setting.objects.get_setting(setting_key=Setting.MESSAGESPERPAGE)),
    )
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}

    return render(request, "aa_forum/view/messages/inbox.html", context)
