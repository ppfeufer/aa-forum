"""
Helper functions for text processing
"""

# Standard Library
import html
import re

# Third Party
from bs4 import BeautifulSoup

# Django
from django.utils.html import strip_tags

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import site_absolute_url

# AA Forum
from aa_forum import __title__
from aa_forum.constants import DISCORD_EMBED_MESSAGE_LENGTH

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


def verify_image_url(image_url):
    """
    Verify if the passed string is a valid image url

    We're verifying image URLs for inclusion in Slack/Discord Webhook integration,
    which requires a scheme at the beginning (http(s)) and a file extension at the end
    to render correctly. So, a URL which passes verify_url()
    (like example.com/kitten.gif) might not pass this test. If you need to test that
    the URL is both valid AND an image suitable for the Incoming Webhook integration,
    run it through both verify_url() and verify_image_url().

    :param image_url:
    :type image_url:
    :return:
    :rtype:
    """

    return re.match(
        pattern=r"(https?:\/\/.*\.(?:gif|jpg|jpeg|png|bmp|webp))",
        string=image_url,
    )


def get_first_image_url_from_text(text):
    """
    Get the first image URL from a text

    :param text:
    :type text:
    :return:
    :rtype:
    """

    soup = BeautifulSoup(markup=text, features="html.parser")

    images = soup.findAll(name="img")

    # The first image to verify we will use
    if images:
        for image in images:
            image__src = image["src"]

            logger.debug(msg=f"Image found: {image__src}")

            if not image__src.startswith(("http://", "https://")):
                logger.debug(msg="Image has no absolute URL, fixing!")

                absolute_site_url = site_absolute_url()
                image__src = f"{absolute_site_url}{image__src}"

            if verify_image_url(image_url=image__src):
                logger.debug(f"Image verified: {image__src}")

                return image__src

    logger.debug(msg="No images found.")

    return None


def string_cleanup(string: str) -> str:
    """
    Clean up a string

    :param string:
    :type string:
    :return:
    :rtype:
    """

    if string:
        re_head = re.compile(
            pattern=r"<\s*head[^>]*>.*?<\s*/\s*head\s*>", flags=re.S | re.I
        )
        re_script = re.compile(
            pattern=r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", flags=re.S | re.I
        )
        re_css = re.compile(
            pattern=r"<\s*style[^>]*>.*?<\s*/\s*style\s*>", flags=re.S | re.I
        )

        # Strip JS
        string = re_head.sub(repl="", string=string)
        string = re_script.sub(repl="", string=string)
        string = re_css.sub(repl="", string=string)

    logger.debug(msg=f"Cleaned up string: {string}")

    return string


def strip_html_tags(text: str, strip_nbsp: bool = False) -> str:
    """
    Strip HTML tags from a text

    :param text: The text to strip HTML tags from
    :type text: str
    :param strip_nbsp: Whether to strip &nbsp; as well
    :type strip_nbsp: bool
    :return: The stripped text
    :rtype: str
    """

    stripped_text = (
        re.compile(pattern=r"&nbsp;").sub(repl="", string=strip_tags(value=text))
        if strip_nbsp
        else strip_tags(value=text)
    )

    logger.debug(msg=f"Stripped text: {stripped_text}")

    return stripped_text


def prepare_message_for_discord(
    message: str, message_length=DISCORD_EMBED_MESSAGE_LENGTH
) -> str:
    """
    Prepare a message for Discord

    We have to run strip_html_tags() twice here.
    1.  To remove HTML tags from the text, we want to send
    2.  After html.unescape() in case that unescaped former escaped HTML tags,
        which now need to be removed as well

    :param message:
    :type message:
    :param message_length:
    :type message_length:
    :return:
    :rtype:
    """

    return strip_html_tags(
        text=html.unescape(
            s=strip_html_tags(
                text=(
                    message[:message_length] + "…"
                    if len(message) > message_length
                    else message
                ),
                strip_nbsp=True,
            )
        ),
        strip_nbsp=True,
    )
