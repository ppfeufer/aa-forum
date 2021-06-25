from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.forms import Form
from django.utils.translation import gettext_lazy as _


def message_form_errors(request: WSGIRequest, form: Form) -> None:
    """
    Send form errors as messages.
    """
    for field, errors in form.errors.items():
        for text in errors:
            messages.error(request, f"{_('Error: ')} {text}")
