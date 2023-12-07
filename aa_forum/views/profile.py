"""
Views for the user profile
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

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required
@permission_required(perm="aa_forum.basic_access")
def index(request: WSGIRequest) -> HttpResponse:
    """
    View for the user profile

    :param request:
    :type request:
    :return:
    :rtype:
    """

    logger.info(msg=f"{request.user} called their user profile.")

    user_profile = get_user_profile(user=request.user)

    # If this is a POST request, we need to process the form data
    if request.method == "POST":
        user_profile_form = UserProfileForm(data=request.POST, instance=user_profile)

        # Check whether it's valid:
        if user_profile_form.is_valid():
            user_profile.signature = user_profile_form.cleaned_data["signature"]
            user_profile.website_title = user_profile_form.cleaned_data["website_title"]
            user_profile.website_url = user_profile_form.cleaned_data["website_url"]
            user_profile.discord_dm_on_new_personal_message = (
                user_profile_form.cleaned_data["discord_dm_on_new_personal_message"]
            )
            user_profile.save()

            messages.success(
                request=request,
                message=mark_safe(s=_("<h4>Success!</h4><p>Profile saved.</p>")),
            )

            return redirect(to="aa_forum:profile_index")

        messages.error(
            request=request,
            message=mark_safe(
                # pylint: disable=duplicate-code
                s=_(
                    "<h4>Error!</h4>"
                    "<p>Something went wrong, please check your input.</p>"
                )
            ),
        )
    else:
        user_profile_form = UserProfileForm(instance=user_profile)

    context = {"form": user_profile_form}

    return render(
        request=request,
        template_name="aa_forum/view/profile/index.html",
        context=context,
    )
