"""
Template filter für search views
"""

import re

from django.template.defaulttags import register
from django.utils.safestring import mark_safe


@register.filter
def highlight_search_term(text: str, search_phrase: str) -> str:
    """
    Highlight the search term in search results
    :param text:
    :type text:
    :param search_term:
    :type search_term:
    :return:
    :rtype:
    """

    search_phrase_cleaned = (
        search_phrase.replace('"', "").replace("<", "").replace(">", "")
    )
    search_phrase_terms = search_phrase_cleaned.split()
    highlighted = text

    for search_term in search_phrase_terms:
        highlighted = re.sub(
            "(?i)(%s)" % (re.escape(search_term)),
            # "(?!<.?)(%s)(?!.?>)" % (re.escape(search_term)),
            # '<span class="aa-forum-search-term-highlight">\\1</span>',
            "«\\1»",
            highlighted,
        )

    return mark_safe(
        highlighted.replace(
            "«", '<span class="aa-forum-search-term-highlight">'
        ).replace("»", "</span>")
    )
