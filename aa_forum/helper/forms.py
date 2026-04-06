"""
Helper functions for forms
"""

# Standard Library
import re

# Django
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.forms import Form
from django.utils.translation import gettext_lazy

# AA Forum
from aa_forum.helper.text import string_cleanup, strip_html_tags


def message_form_errors(request: WSGIRequest, form: Form) -> None:
    """
    Add form errors to messages

    :param request: The request
    :type request: WSGIRequest
    :param form: The form
    :type form: Form
    :return: None
    :rtype: None
    """

    for _, errors in form.errors.items():
        for text in errors:
            messages.error(request=request, message=f"{gettext_lazy('Error:')} {text}")


def message_empty(message: str) -> bool:
    """
    Check if a message is empty

    :param message: The message to check
    :type message: str
    :return: Whether the message is empty
    :rtype: bool
    """

    return (
        message
        and (
            ("<p>" in message or "<br>" in message or "&nbsp;" in message)
            and re.compile(pattern=r"&nbsp;")
            .sub(repl="", string=message.replace("<p>", "").replace("</p>", ""))
            .strip()
            == ""
        )
        and strip_html_tags(text=string_cleanup(message), strip_nbsp=True).strip() == ""
    )
