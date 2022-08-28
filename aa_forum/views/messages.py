"""
Messages views
"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Forum
from aa_forum import __title__
from aa_forum.models import PersonalMessage

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aa_forum.basic_access")
def inbox(request: WSGIRequest) -> HttpResponse:
    """
    Messages overview
    :return:
    """

    logger.info(f"{request.user} called their messages overview")

    personal_messages = PersonalMessage.objects.filter(
        recipient=request.user
    ).select_related("sender", "sender__profile", "sender__profile__main_character")

    context = {"personal_messages": personal_messages}

    return render(request, "aa_forum/view/messages/inbox.html", context)
