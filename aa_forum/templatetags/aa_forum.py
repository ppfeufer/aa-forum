"""
AA Forum template tags
"""

# Standard Library
import re
from datetime import datetime

# Third Party
from bs4 import BeautifulSoup

# Django
from django import template
from django.contrib.auth.models import User
from django.template.defaulttags import register
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import reverse as reverse_url

# AA Forum
from aa_forum import __title__
from aa_forum.app_settings import aa_timezones_installed
from aa_forum.constants import SEARCH_STOPWORDS
from aa_forum.models import PersonalMessage

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


class SetVarNode(template.Node):
    """
    Set a template variable
    """

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        """
        Render the template variable

        :param context:
        :type context:
        :return:
        :rtype:
        """

        try:
            value = template.Variable(var=self.var_value).resolve(context=context)
        except template.VariableDoesNotExist:
            value = ""

        context[self.var_name] = value

        return ""


@register.filter
def aa_forum_time(db_datetime: datetime) -> str:
    """
    Format a datetime object for the forum

    :param db_datetime:
    :type db_datetime:
    :return:
    :rtype:
    """

    # If empty, return empty
    if db_datetime in (None, ""):
        return ""

    # Try to format the date for a localized output
    try:
        formatted_date_string = formats.date_format(value=db_datetime)
    except AttributeError:
        try:
            formatted_date_string = format(db_datetime)
        except AttributeError:
            formatted_date_string = ""

    formatted_time_string = db_datetime.strftime("%H:%M:%S")
    formatted_forum_date = f"{formatted_date_string}, {formatted_time_string}"

    # If `aa-timezones` is installed, add (?) to the date-time string
    # and link to the time zones conversion
    if aa_timezones_installed():
        timestamp_from_db_datetime = int(datetime.timestamp(db_datetime))
        timezones_url = reverse_url(
            viewname="timezones:index", args=[timestamp_from_db_datetime]
        )
        link_title = _("Timezone conversion")

        return mark_safe(
            s=(
                f"{formatted_forum_date} "
                f'<sup>(<a href="{timezones_url}" target="_blank" rel="noopener noreferer" '
                f'title="{link_title}" data-bs-tooltip="aa-forum">'
                '<i class="fa-solid fa-circle-question"></i></a>)</sup>'
            )
        )

    return formatted_forum_date


@register.filter
def aa_forum_highlight_search_term(text: str, search_phrase: str) -> str:
    """
    Highlight a search term in a text

    :param text:
    :type text:
    :param search_phrase:
    :type search_phrase:
    :return:
    :rtype:
    """

    delimiter_search_term_start = "{«}"
    delimiter_search_term_end = "{»}"

    querywords = search_phrase.split()
    search_phrase_terms = [
        word for word in querywords if word.lower() not in SEARCH_STOPWORDS
    ]
    highlighted = text

    for search_term in search_phrase_terms:
        highlighted = re.sub(
            pattern=f"(?i)({(re.escape(search_term))})",
            repl=f"{delimiter_search_term_start}\\1{delimiter_search_term_end}",
            string=highlighted,
        )

    highlighted = BeautifulSoup(markup=highlighted, features="html.parser")

    for hyperlink in highlighted.findAll(name="a"):
        try:
            hyperlink["href"] = (
                hyperlink["href"]
                .replace(delimiter_search_term_start, "")
                .replace(delimiter_search_term_end, "")
            )
        except KeyError:
            # this should never happen, but in case it does, add a dummy href
            hyperlink["href"] = "#"

        try:
            hyperlink["title"] = (
                hyperlink["title"]
                .replace(delimiter_search_term_start, "")
                .replace(delimiter_search_term_end, "")
            )
        except KeyError:
            pass

        try:
            hyperlink["name"] = (
                hyperlink["name"]
                .replace(delimiter_search_term_start, "")
                .replace(delimiter_search_term_end, "")
            )
        except KeyError:
            pass

    for image in highlighted.findAll("img"):
        try:
            image["src"] = (
                image["src"]
                .replace(delimiter_search_term_start, "")
                .replace(delimiter_search_term_end, "")
            )
        except KeyError:
            # this should never happen, but in case it does, add a dummy src
            image["src"] = "#"

        try:
            image["alt"] = (
                image["alt"]
                .replace(delimiter_search_term_start, "")
                .replace(delimiter_search_term_end, "")
            )
        except KeyError:
            pass

        try:
            image["title"] = (
                image["title"]
                .replace(delimiter_search_term_start, "")
                .replace(delimiter_search_term_end, "")
            )
        except KeyError:
            pass

    return mark_safe(
        str(highlighted)
        .replace(
            delimiter_search_term_start, '<span class="aa-forum-search-term-highlight">'
        )
        .replace(delimiter_search_term_end, "</span>")
    )


@register.tag(name="aa_forum_template_variable")
def aa_forum_template_variable(parser, token):  # pylint: disable=unused-argument
    """
    Set a template variable

    Usage:
        {% aa_forum_template_variable <var_name> = <var_value> %}

    :param parser:
    :type parser:
    :param token:
    :type token:
    :return:
    :rtype:
    """

    parts = token.split_contents()

    if len(parts) < 4:
        raise template.TemplateSyntaxError(
            "'aa_forum_template_variable' tag must be of the form: "
            "{% aa_forum_template_variable <var_name> = <var_value> %}"
        )

    return SetVarNode(parts[1], parts[3])


@register.simple_tag
def personal_message_unread_count(user: User) -> str:
    """
    Get the unread personal message count for a user

    :param user:
    :type user:
    :return:
    :rtype:
    """

    return_value = ""
    message_count = PersonalMessage.objects.get_personal_message_unread_count_for_user(
        user=user
    )

    if message_count > 0:
        return_value = mark_safe(
            s=f'<span class="badge text-bg-secondary aa-forum-badge-personal-messages-unread-count">{message_count}</span>'  # pylint: disable=line-too-long
        )

    return return_value


@register.filter
def aa_forum_main_character_name(user: User) -> str:
    """
    Get the users main character name, or return the username if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return ""

    try:
        return_value = user.profile.main_character.character_name
    except AttributeError:
        return str(user)

    return return_value


# pylint: disable=duplicate-code
@register.filter
def aa_forum_main_character_id(user: User) -> int:
    """
    Get the users' main character id, or 1 if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return 1

    try:
        return_value = user.profile.main_character.character_id
    except AttributeError:
        return_value = 1

    return return_value


@register.filter
def aa_forum_main_character_corporation_name(user: User) -> str:
    """
    Get the users' main character corporation name, or an empty string if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return ""

    try:
        return_value = user.profile.main_character.corporation_name
    except AttributeError:
        return_value = ""

    return return_value


@register.filter
def aa_forum_main_character_corporation_id(user: User) -> int:
    """
    Get the users' main character corporation id, or 1 if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return 1

    try:
        return_value = user.profile.main_character.corporation_id
    except AttributeError:
        return_value = 1

    return return_value


@register.filter
def aa_forum_main_character_alliance_name(user: User) -> str:
    """
    Get the users' main character alliance name, or an empty string if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return ""

    try:
        return_value = user.profile.main_character.alliance_name
    except AttributeError:
        return_value = ""

    return return_value


@register.filter
def aa_forum_main_character_alliance_id(user: User) -> int:
    """
    Get the users' main character alliance id, or 1 if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return 1

    try:
        return_value = user.profile.main_character.alliance_id

        # Check if the user is in an alliance
        try:
            return_value = int(return_value)
        except Exception:  # pylint: disable=broad-exception-caught
            return_value = 1
    except AttributeError:
        return_value = 1

    return return_value
