"""
Messages views
"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
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
from aa_forum.forms import PersonalMessageForm
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

    personal_messages = PersonalMessage.objects.get_personal_messages_for_user(
        request.user
    )

    paginator = Paginator(
        personal_messages,
        int(Setting.objects.get_setting(setting_key=Setting.MESSAGESPERPAGE)),
    )
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}

    return render(request, "aa_forum/view/personal-messages/inbox.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def new_message(request: WSGIRequest) -> HttpResponse:
    """
    Create a new personal message
    :param request:
    :return:
    """

    logger.info(f"{request.user} called the new personal message page")

    # If this is a POST request we need to process the form data
    if request.method == "POST":
        new_private_message_form = PersonalMessageForm(request.POST)

        # Check whether it's valid:
        if new_private_message_form.is_valid():
            sender = request.user
            recipient = new_private_message_form.cleaned_data["recipient"]
            subject = new_private_message_form.cleaned_data["subject"]
            message = new_private_message_form.cleaned_data["message"]

            PersonalMessage(
                sender=sender,
                recipient=recipient,
                subject=subject,
                message=message,
            ).save()

            messages.success(
                request,
                mark_safe(_(f"<h4>Success!</h4><p>Message to {recipient} sent.<p>")),
            )

            return redirect("aa_forum:personal_messages_inbox")

        messages.error(
            request,
            mark_safe(
                _(
                    "<h4>Error!</h4>"
                    "<p>Something went wrong, please check your input<p>"
                )
            ),
        )
    else:
        new_private_message_form = PersonalMessageForm()

    context = {"form": new_private_message_form}

    return render(request, "aa_forum/view/personal-messages/new-message.html", context)


@login_required
@permission_required("aa_forum.basic_access")
def sent_messages(request: WSGIRequest, page_number: int = None) -> HttpResponse:
    """
    Overview of all messages sent by a user
    :param request:
    :param page_number:
    :return:
    """

    logger.info(f"{request.user} called the their sent personal message page")

    personal_messages = PersonalMessage.objects.get_personal_messages_sent_for_user(
        request.user
    )

    paginator = Paginator(
        personal_messages,
        int(Setting.objects.get_setting(setting_key=Setting.MESSAGESPERPAGE)),
    )
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}

    return render(
        request, "aa_forum/view/personal-messages/sent-messages.html", context
    )
