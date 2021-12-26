"""
Constants
"""

# Django
from django.utils.text import slugify

# AA Forum
from aa_forum import __version__

github_url = "https://github.com/ppfeufer/aa-forum"
verbose_name = "AA-Forum - A simple forum for Alliance Auth"
verbose_name_slug = slugify(verbose_name, allow_unicode=True)
user_agent = f"{verbose_name_slug} v{__version__} {github_url}"

# Setting keys
SETTING_MESSAGESPERPAGE = "defaultMaxMessages"
SETTING_TOPICSPERPAGE = "defaultMaxTopics"

# All internal URLs need to start with this prefix
# to prevent conflicts with user generated forum URLs
INTERNAL_URL_PREFIX = "-"

# Default sort order for new categories and boards
DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER = 999999

# Search stop words. These words and characters will be removed from the search phrase
SEARCH_STOPWORDS = [
    '"',
    "<",
    ">",
    "(",
    ")",
    "{",
    "}",
    "a",
    "an",
    "are",
    "as",
    "at",
    "be",
    "if",
    "in",
    "into",
    "is",
    "of",
    "off",
    "on",
    "the",
    "what",
    "which",
    "who",
]
