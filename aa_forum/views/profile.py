"""
User profile view
"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Forum
from aa_forum import __title__
from aa_forum.forms import UserProfileForm
from aa_forum.helper.user import get_user_profile

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aa_forum.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Profile indes view
    :param request:
    :return:
    """

    logger.info(f"{request.user} called their user profile.")

    user_profile = get_user_profile(user=request.user)

    # If this is a POST request we need to process the form data
    if request.method == "POST":
        user_profile_form = UserProfileForm(request.POST, instance=user_profile)

        # Check whether it's valid:
        if user_profile_form.is_valid():
            user_profile.signature = user_profile_form.cleaned_data["signature"]
            user_profile.website_title = user_profile_form.cleaned_data["website_title"]
            user_profile.website_url = user_profile_form.cleaned_data["website_url"]
            user_profile.save()

            messages.success(
                request, mark_safe(_("<h4>Success!</h4><p>Profile saved.<p>"))
            )

            return redirect("aa_forum:profile_index")
        else:
            messages.error(
                request,
                mark_safe(
                    _(
                        "<h4>Error!</h4>"
                        "<p>Something went wrong, please check your input.<p>"
                    )
                ),
            )
    else:
        user_profile_form = UserProfileForm(instance=user_profile)

    context = {"form": user_profile_form}

    return render(request, "aa_forum/view/profile/index.html", context)
