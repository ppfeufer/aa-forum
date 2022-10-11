"""
Template tag for supporting aa-timezones
"""

# Standard Library
from datetime import datetime

# Django
from django.template.defaulttags import register
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

# Alliance Auth (External Libs)
from app_utils.urls import reverse as reverse_url

# AA Forum
from aa_forum.app_settings import aa_timezones_installed


@register.filter
def forum_time(db_time, arg=None) -> str:
    """
    Convert DB time into a formatted date-time string we use in our templates
    :param db_time:
    :type db_time:
    :param arg:
    :type arg:
    :return:
    :rtype:
    """

    formatted_time_string = db_time.strftime("%H:%M:%S")
    timestamp_from_db_time = int(datetime.timestamp(db_time))

    # If empty, return empty
    if db_time in (None, ""):
        return ""

    # try to format the date
    try:
        formatted_date_string = formats.date_format(db_time, arg)
    except AttributeError:
        try:
            formatted_date_string = format(db_time, arg)
        except AttributeError:
            formatted_date_string = ""

    formatted_forum_date = f"{formatted_date_string}, {formatted_time_string}"

    # If `aa-timezones` is installed, add (?) to the date-time string
    # and link to the time zones conversion
    if aa_timezones_installed():
        timezones_url = reverse_url("timezones:index", args=[timestamp_from_db_time])
        link_title = _("Timezone Conversion")

        return mark_safe(
            f"{formatted_forum_date} "
            f'<sup>(<a href="{timezones_url}" target="_blank" rel="noopener noreferer" '
            f'title="{link_title}"><i class="fas fa-question-circle"></i></a>)</sup>'
        )

    return formatted_forum_date
