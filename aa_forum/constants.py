"""
Constants
"""

# Django
from django.utils.text import slugify

# AA Forum
from aa_forum import __version__

github_url: str = "https://github.com/ppfeufer/aa-forum"
verbose_name: str = "AA-Forum - A simple forum for Alliance Auth"
verbose_name_slug: str = slugify(verbose_name, allow_unicode=True)
user_agent: str = f"{verbose_name_slug} v{__version__} {github_url}"

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

# Discord embed settings
DISCORD_EMBED_COLOR_INFO = 0x5BC0DE
DISCORD_EMBED_COLOR_SUCCESS = 0x5CB85C
DISCORD_EMBED_COLOR_WARNING = 0xF0AD4E
DISCORD_EMBED_COLOR_DANGER = 0xD9534F

DISCORD_EMBED_COLOR_MAP = {
    "info": DISCORD_EMBED_COLOR_INFO,
    "success": DISCORD_EMBED_COLOR_SUCCESS,
    "warning": DISCORD_EMBED_COLOR_WARNING,
    "danger": DISCORD_EMBED_COLOR_DANGER,
}

DISCORD_EMBED_MESSAGE_LENGTH = 1000
