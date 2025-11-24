"""
Personal Messages Views
"""

# Standard Library
import json
from http import HTTPStatus

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Forum
from aa_forum import __title__
from aa_forum.forms import NewPersonalMessageForm, ReplyPersonalMessageForm
from aa_forum.helper.pagination import get_paginated_page_object
from aa_forum.helper.user import get_main_character_from_user
from aa_forum.models import PersonalMessage, Setting
from aa_forum.providers import AppLogger

logger = AppLogger(my_logger=get_extension_logger(name=__name__), prefix=__title__)


@login_required
@permission_required(perm="aa_forum.basic_access")
def inbox(request: WSGIRequest, page_number: int = None) -> HttpResponse:
    """
    Overview of all messages in a user's inbox

    :param request:
    :type request:
    :param page_number:
    :type page_number:
    :return:
    :rtype:
    """

    logger.info(msg=f"{request.user} called their messages overview.")

    personal_messages = PersonalMessage.objects.get_personal_messages_for_user(
        user=request.user
    )

    page_obj = get_paginated_page_object(
        queryset=personal_messages,
        items_per_page=Setting.objects.get_setting(
            setting_key=Setting.Field.MESSAGESPERPAGE
        ),
        page_number=page_number,
    )

    context = {"page_obj": page_obj}

    return render(
        request=request,
        template_name="aa_forum/view/personal-messages/inbox.html",
        context=context,
    )


@login_required
@permission_required("aa_forum.basic_access")
def new_message(request: WSGIRequest) -> HttpResponse:
    """
    Create a new personal message

    :param request:
    :type request:
    :return:
    :rtype:
    """

    logger.info(msg=f"{request.user} called the new personal message page.")

    # If this is a POST request, we need to process the form data
    if request.method == "POST":
        new_private_message_form = NewPersonalMessageForm(data=request.POST)

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

            recipient_main_char = get_main_character_from_user(user=recipient)

            messages.success(
                request=request,
                message=mark_safe(
                    # pylint: disable=duplicate-code
                    s=_(
                        "<h4>Success!</h4><p>Message to {recipient_main_char} sent.</p>"
                    ).format(recipient_main_char=recipient_main_char)
                ),
            )

            return redirect(to="aa_forum:personal_messages_inbox")

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
        new_private_message_form = NewPersonalMessageForm()

    context = {"form": new_private_message_form}

    return render(
        request=request,
        template_name="aa_forum/view/personal-messages/new-message.html",
        context=context,
    )


@login_required
@permission_required(perm="aa_forum.basic_access")
def sent_messages(request: WSGIRequest, page_number: int = None) -> HttpResponse:
    """
    Overview of all messages in a users sent messages

    :param request:
    :type request:
    :param page_number:
    :type page_number:
    :return:
    :rtype:
    """

    logger.info(msg=f"{request.user} called the their sent personal message page.")

    personal_messages = PersonalMessage.objects.get_personal_messages_sent_for_user(
        user=request.user
    )

    page_obj = get_paginated_page_object(
        queryset=personal_messages,
        items_per_page=Setting.objects.get_setting(
            setting_key=Setting.Field.MESSAGESPERPAGE
        ),
        page_number=page_number,
    )

    context = {"page_obj": page_obj}

    return render(
        request=request,
        template_name="aa_forum/view/personal-messages/sent-messages.html",
        context=context,
    )


@login_required
@permission_required("aa_forum.basic_access")
def reply_message(request: WSGIRequest, message_id: int) -> HttpResponse:
    """
    Reply to a personal message

    :param request:
    :type request:
    :param message_id:
    :type message_id:
    :return:
    :rtype:
    """

    context = {}

    try:
        personal_message = PersonalMessage.objects.get(
            pk=message_id, recipient=request.user, deleted_by_recipient=False
        )
    except PersonalMessage.DoesNotExist:
        messages.error(
            request=request,
            message=mark_safe(
                # pylint: disable=duplicate-code
                s=_(
                    "<h4>Error!</h4>"
                    "<p>The message you were trying to reply to does either not "
                    "exist or you are not the recipient.</p>"
                )
            ),
        )

        return redirect(to="aa_forum:personal_messages_inbox")

    # If this is a POST request, we need to process the form data
    if request.method == "POST":
        reply_private_message_form = ReplyPersonalMessageForm(data=request.POST)

        # Check whether it's valid:
        if reply_private_message_form.is_valid():
            sender = request.user
            recipient = personal_message.sender

            subject = personal_message.subject
            if not subject.startswith("Re:"):
                subject = "Re: " + subject

            message = reply_private_message_form.cleaned_data["message"]

            PersonalMessage(
                sender=sender,
                recipient=recipient,
                subject=subject,
                message=message,
            ).save()

            recipient_main_char = get_main_character_from_user(user=recipient)
            messages.success(
                request=request,
                message=mark_safe(
                    # pylint: disable=duplicate-code
                    s=_(
                        "<h4>Success!</h4><p>Reply to {recipient_main_char} sent.</p>"
                    ).format(recipient_main_char=recipient_main_char)
                ),
            )

            return redirect(to="aa_forum:personal_messages_inbox")

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
        reply_private_message_form = ReplyPersonalMessageForm()

    context["message"] = personal_message
    context["form"] = reply_private_message_form

    return render(
        request=request,
        template_name="aa_forum/view/personal-messages/reply-message.html",
        context=context,
    )


@login_required
@permission_required("aa_forum.basic_access")
def delete_message(request: WSGIRequest, folder: str, message_id: int) -> HttpResponse:
    """
    Delete a personal message

    :param request:
    :type request:
    :param folder:
    :type folder:
    :param message_id:
    :type message_id:
    :return:
    :rtype:
    """

    def folder_inbox() -> HttpResponse:
        """
        Remove message from inbox

        :return:
        """

        try:
            message = PersonalMessage.objects.get(pk=message_id, recipient=request.user)
        except PersonalMessage.DoesNotExist:
            messages.error(
                request=request,
                message=mark_safe(
                    # pylint: disable=duplicate-code
                    s=_(
                        "<h4>Error!</h4>"
                        "<p>The message you tried to remove does either not exist "
                        "or is not yours to remove.</p>"
                    )
                ),
            )
        else:
            if message.deleted_by_sender is True:
                message.delete()
            else:
                message.deleted_by_recipient = True
                message.save()

            messages.success(
                request=request,
                message=mark_safe(
                    s=_("<h4>Success!</h4><p>Message removed from your inbox.</p>")
                ),
            )

        return redirect(to="aa_forum:personal_messages_inbox")

    def folder_sent_messages() -> HttpResponse:
        """
        Remove a message from sent messages

        :return:
        """

        try:
            message = PersonalMessage.objects.get(pk=message_id, sender=request.user)
        except PersonalMessage.DoesNotExist:
            messages.error(
                request=request,
                message=mark_safe(
                    # pylint: disable=duplicate-code
                    s=_(
                        "<h4>Error!</h4>"
                        "<p>The message you tried to remove does either not exist "
                        "or is not yours to remove.</p>"
                    )
                ),
            )
        else:
            if message.deleted_by_recipient is True:
                message.delete()
            else:
                message.deleted_by_sender = True
                message.save()

            messages.success(
                request=request,
                message=mark_safe(
                    # pylint: disable=duplicate-code
                    s=_(
                        "<h4>Success!</h4>"
                        "<p>Message has been removed from your sent messages.</p>"
                    )
                ),
            )

        return redirect(to="aa_forum:personal_messages_sent_messages")

    switch = {"inbox": folder_inbox, "sent-messages": folder_sent_messages}

    if folder in switch:
        return switch[folder]()

    messages.error(
        request=request,
        message=mark_safe(s=_("<h4>Error!</h4><p>Something went wrong.</p>")),
    )

    return redirect(to="aa_forum:personal_messages_inbox")


@login_required
@permission_required(perm="aa_forum.basic_access")
def ajax_read_message(request: WSGIRequest, folder: str) -> HttpResponse:
    """
    Read a personal message

    :param request:
    :type request:
    :param folder:
    :type folder:
    :return:
    :rtype:
    """

    data = {}

    # Validate request method
    if request.method != "POST":
        return HttpResponse(status=HTTPStatus.NO_CONTENT)

    # Parse and validate JSON request body
    try:
        request_body = json.loads(request.body)
        required_keys = ("sender", "recipient", "message")

        if not all(key in request_body for key in required_keys):
            raise ValueError("Missing required keys")

        sender_id = int(request_body["sender"])
        recipient_id = int(request_body["recipient"])
        message_id = int(request_body["message"])
    except (json.JSONDecodeError, ValueError, TypeError, KeyError):
        return HttpResponse(status=HTTPStatus.NO_CONTENT)

    # Validate user permissions and get message
    user_id = request.user.id

    if not (
        (folder == "inbox" and user_id == recipient_id)
        or (folder == "sent-messages" and user_id == sender_id)
    ):
        return HttpResponse(status=HTTPStatus.NO_CONTENT)

    try:
        message = PersonalMessage.objects.get(
            pk=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
        )
    except PersonalMessage.DoesNotExist:
        return HttpResponse(status=HTTPStatus.NO_CONTENT)

    # Mark message as read if it's in inbox and unread
    if folder == "inbox" and not message.is_read:
        message.is_read = True
        message.save()

    data["message"] = message
    data["folder"] = folder

    return render(
        request=request,
        template_name="aa_forum/ajax-render/personal-messages/message.html",
        context=data,
    )


@login_required
@permission_required("aa_forum.basic_access")
def ajax_unread_messages_count(request: WSGIRequest) -> JsonResponse:
    """
    Get the number of unread messages for a user

    :param request:
    :type request:
    :return:
    :rtype:
    """

    unread_messages_count = (
        PersonalMessage.objects.get_personal_message_unread_count_for_user(
            user=request.user
        )
    )

    data = {"unread_messages_count": unread_messages_count}

    return JsonResponse(data=data, safe=False)
