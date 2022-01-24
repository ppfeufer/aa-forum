"""
Text helper
"""

# Third Party
from bs4 import BeautifulSoup

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import site_absolute_url

# AA Forum
from aa_forum import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def get_image_url(text):
    """
    Extract an image url from the passed text. If there are multiple image urls,
    only the first one will be returned.
    """

    soup = BeautifulSoup(text, "html.parser")

    images = soup.findAll("img")

    if images:
        first_image__src = images[0]["src"]

        if not first_image__src.startswith(("http://", "https://")):
            absolute_site_url = site_absolute_url()
            first_image__src = f"{absolute_site_url}{first_image__src}"

        logger.debug(first_image__src)

        return first_image__src

    return None
