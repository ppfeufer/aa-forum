"""
Helper functions for forms
"""

# Django
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.forms import Form
from django.utils.translation import gettext_lazy


def message_form_errors(request: WSGIRequest, form: Form) -> None:
    """
    Add form errors to messages

    :param request:
    :type request:
    :param form:
    :type form:
    :return:
    :rtype:
    """

    for _, errors in form.errors.items():
        for text in errors:
            messages.error(request=request, message=f"{gettext_lazy('Error:')} {text}")
