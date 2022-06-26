"""
Form helper
"""

# Django
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.forms import Form
from django.utils.translation import gettext_lazy


def message_form_errors(request: WSGIRequest, form: Form) -> None:
    """
    Send form errors as messages.
    :param request:
    :param form:
    :return:
    """

    for _, errors in form.errors.items():
        for text in errors:
            messages.error(request, f"{gettext_lazy('Error: ')} {text}")
