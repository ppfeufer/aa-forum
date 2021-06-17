"""
Template filter für search views
"""

import re

from django.template.defaulttags import register
from django.utils.safestring import mark_safe


@register.filter
def highlight_search_term(text: str, search_term: str) -> str:
    """
    Highlight the search term in search results
    :param text:
    :type text:
    :param search_term:
    :type search_term:
    :return:
    :rtype:
    """

    highlighted = re.sub(
        "(?i)(%s)" % (re.escape(search_term)),
        '<span class="aa-forum-search-term-highlight">\\1</span>',
        text,
    )

    return mark_safe(highlighted)
