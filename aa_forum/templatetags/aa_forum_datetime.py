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
def forum_time(db_datetime: datetime) -> str:
    """
    Convert DB time into a formatted date-time string we use in our templates
    :param db_datetime:
    :type db_datetime:
    :param arg:
    :type arg:
    :return:
    :rtype:
    """

    # If empty, return empty
    if db_datetime in (None, ""):
        return ""

    # Try to format the date for a localised output
    try:
        formatted_date_string = formats.date_format(db_datetime)
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
            "timezones:index", args=[timestamp_from_db_datetime]
        )
        link_title = _("Timezone Conversion")

        return mark_safe(
            f"{formatted_forum_date} "
            f'<sup>(<a href="{timezones_url}" target="_blank" rel="noopener noreferer" '
            f'title="{link_title}"><i class="fas fa-question-circle"></i></a>)</sup>'
        )

    return formatted_forum_date
