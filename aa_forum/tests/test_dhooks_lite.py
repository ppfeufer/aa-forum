"""
Test cases for the `aa_forum.helper.discord_messages` module `dhooks-lite` implementation.
"""

# Standard Library
from unittest import TestCase

# AA Forum
from aa_forum import __version__
from aa_forum.constants import APP_NAME_VERBOSE_USERAGENT, GITHUB_URL
from aa_forum.helper.discord_messages import _dhooks_lite_user_agent


class TestDhooksLiteUserAgent(TestCase):
    """
    Test cases for the `dhooks-lite` user agent
    """

    def test_create_useragent(self):
        """
        Test creating a user agent

        :return:
        :rtype:
        """

        obj = _dhooks_lite_user_agent()

        self.assertEqual(first=obj.name, second=APP_NAME_VERBOSE_USERAGENT)
        self.assertEqual(first=obj.url, second=GITHUB_URL)
        self.assertEqual(first=obj.version, second=__version__)

    def test_useragent_str(self):
        """
        Test the string representation of the user agent

        :return:
        :rtype:
        """

        obj = _dhooks_lite_user_agent()

        self.assertEqual(
            first=str(obj),
            second=f"{APP_NAME_VERBOSE_USERAGENT} ({GITHUB_URL}, {__version__})",
        )
