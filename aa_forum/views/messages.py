"""
Messages views
"""

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Forum
from aa_forum import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def index(request: WSGIRequest) -> HttpResponse:
    """
    Messages overview
    :return:
    """

    logger.info(f"{request.user} called their messages overview")

    context = {}

    return render(request, "aa_forum/view/messages/index.html", context)
