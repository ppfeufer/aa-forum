"""
User profile view
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
from aa_forum.forms import UserProfileForm
from aa_forum.helper.user import get_user_profile

# from django.contrib import messages
# from django.utils.translation import gettext as _


logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aa_forum.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Profile indes view
    :param request:
    :return:
    """

    logger.info(f"{request.user} called their user profile")

    user_profile = get_user_profile(user=request.user)

    user_settings_form = UserProfileForm(instance=user_profile)

    context = {"form": user_settings_form}

    return render(request, "aa_forum/view/profile/index.html", context)
