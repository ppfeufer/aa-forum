"""
Versioned static URLs to break browser caches when changing the app version
"""

# Django
from django.template.defaulttags import register
from django.templatetags.static import static

# AA Forum
from aa_forum import __version__


@register.simple_tag
def aa_forum_static(path: str) -> str:
    """
    Return versioned static URL
    :param path:
    :return:
    """

    static_url = static(path)
    versioned_url = static_url + "?v=" + __version__

    return versioned_url
