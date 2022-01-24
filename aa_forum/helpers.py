"""
Our little helpers
"""

# Standard Library
import re

# Third Party
import requests

# Django
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.forms import Form
from django.utils.translation import gettext_lazy

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA Forum
from aa_forum import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def message_form_errors(request: WSGIRequest, form: Form) -> None:
    """
    Send form errors as messages.
    """

    for _, errors in form.errors.items():
        for text in errors:
            messages.error(request, f"{gettext_lazy('Error: ')} {text}")


def string_cleanup(string: str) -> str:
    """
    Clean up a string by removing JS, CSS and Head tags
    :param string:
    :type string:
    """

    re_head = re.compile(r"<\s*head[^>]*>.*?<\s*/\s*head\s*>", re.S | re.I)
    re_script = re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.S | re.I)
    re_css = re.compile(r"<\s*style[^>]*>.*?<\s*/\s*style\s*>", re.S | re.I)

    # Strip JS
    string = re_head.sub("", string)
    string = re_script.sub("", string)
    string = re_css.sub("", string)

    return string


def send_message_to_discord_webhook(webhook_url: str, text_message: str, embeds: {}):
    """
    Send a message to a Discord Webhook
    :param webhook_url:
    :param text_message:
    :param embeds:
    :return:
    """

    data = {"content": text_message, "embeds": [embeds]}

    result = requests.post(webhook_url, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.info(f"Discord Webhook Error: {err}")
