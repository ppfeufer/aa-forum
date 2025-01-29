"""
Constants
"""

# Standard Library
import glob
import json
import os
from enum import Enum

# AA Forum
from aa_forum import __version__

APP_NAME = "aa-forum"
GITHUB_URL = f"https://github.com/ppfeufer/{APP_NAME}"
USER_AGENT = f"{APP_NAME}/{__version__} ({GITHUB_URL})"

# aa-forum/aa_forum
AA_FORUM_BASE_DIR = os.path.join(os.path.dirname(__file__))
# aa-forum/aa_forum/static/aa_forum
AA_FORUM_STATIC_DIR = os.path.join(AA_FORUM_BASE_DIR, "static", "aa_forum")

# All internal URLs need to start with this prefix
# to prevent conflicts with user-generated forum URLs
INTERNAL_URL_PREFIX = "-"

# Default sort order for new categories and boards
DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER = 999999

# Search stop words. These words and characters will be removed from the search phrase
SEARCH_STOPWORDS = ['"', "<", ">", "(", ")", "{", "}"]

# Add stopwords from all files (Files downloaded from: https://github.com/stopwords-iso)
for file in glob.glob(os.path.join(AA_FORUM_BASE_DIR, "search/stopwords", "*.json")):
    with open(file, encoding="utf-8") as f:
        SEARCH_STOPWORDS.extend(json.load(f))


class DiscordEmbedColor(Enum):
    """
    Discord embed colors
    """

    INFO = 0x5BC0DE
    SUCCESS = 0x5CB85C
    WARNING = 0xF0AD4E
    DANGER = 0xD9534F


DISCORD_EMBED_COLOR_MAP = {
    "info": DiscordEmbedColor.INFO.value,
    "success": DiscordEmbedColor.SUCCESS.value,
    "warning": DiscordEmbedColor.WARNING.value,
    "danger": DiscordEmbedColor.DANGER.value,
}

DISCORD_EMBED_MESSAGE_LENGTH = 1000
