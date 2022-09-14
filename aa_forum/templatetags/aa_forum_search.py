"""
Template filter for search views
"""

# Standard Library
import re

# Third Party
from bs4 import BeautifulSoup

# Django
from django.template.defaulttags import register
from django.utils.safestring import mark_safe

# AA Forum
from aa_forum.constants import SEARCH_STOPWORDS


@register.filter
def highlight_search_term(text: str, search_phrase: str) -> str:
    """
    Highlight the search term in search results
    :param text:
    :param search_phrase:
    :return:
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
            f"(?i)({(re.escape(search_term))})",
            f"{delimiter_search_term_start}\\1{delimiter_search_term_end}",
            highlighted,
        )

    highlighted = BeautifulSoup(highlighted, "html.parser")

    for hyperlink in highlighted.findAll("a"):
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
