"""
Text helper
"""

# Standard Library
import re

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


def verify_image_url(image_url):
    """
    Verify that the passed text is an image URL.

    We're verifying image URLs for inclusion in Slack/Discord Webhook integration,
    which requires a scheme at the beginning (http(s)) and a file extension at the end
    to render correctly. So, a URL which passes verify_url()
    (like example.com/kitten.gif) might not pass this test. If you need to test that
    the URL is both valid AND an image suitable for the Incoming Webhook integration,
    run it through both verify_url() and verify_image_url().
    :param image_url:
    :return:
    """

    return re.match(
        r"(http(s?):)([\/|.|\w|\s|-])*\.(?:gif|jpg|jpeg|png|bmp|webp)", image_url
    )


def get_image_url(text):
    """
    Extract an image url from the passed text. If there are multiple image urls,
    the first to verify will be returned.
    :param text:
    :return:
    """

    soup = BeautifulSoup(text, "html.parser")

    images = soup.findAll("img")

    # The first image to verify we will use
    if images:
        for image in images:
            image__src = image["src"]

            logger.debug(f"Image found: {image__src}")

            if not image__src.startswith(("http://", "https://")):
                logger.debug("Image has no absolute URL, fixing!")

                absolute_site_url = site_absolute_url()
                image__src = f"{absolute_site_url}{image__src}"

            if verify_image_url(image__src):
                logger.debug(f"Image verified: {image__src}")

                return image__src

    logger.debug("No images found.")

    return None


def string_cleanup(string: str) -> str:
    """
    Clean up a string by removing JS, CSS and Head tags
    :param string:
    :return:
    """

    re_head = re.compile(r"<\s*head[^>]*>.*?<\s*/\s*head\s*>", re.S | re.I)
    re_script = re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.S | re.I)
    re_css = re.compile(r"<\s*style[^>]*>.*?<\s*/\s*style\s*>", re.S | re.I)

    # Strip JS
    string = re_head.sub("", string)
    string = re_script.sub("", string)
    string = re_css.sub("", string)

    return string
