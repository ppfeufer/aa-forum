"""
Test for app_settings.py
"""

# Standard Library
import importlib
from unittest.mock import patch

# Django
from django.test import modify_settings, override_settings

# AA Forum
from aa_forum.app_settings import (
    aa_timezones_installed,
    allianceauth_discordbot_installed,
    debug_enabled,
    discord_messaging_proxy_available,
    discordproxy_installed,
)
from aa_forum.tests import BaseTestCase


class TestModulesInstalled(BaseTestCase):
    """
    Test if modules are installed
    """

    @modify_settings(INSTALLED_APPS={"append": "aadiscordbot"})
    def test_allianceauth_discordbot_installed_should_return_true(self):
        """
        Test allianceauth_discordbot_installed should return True

        :return:
        :rtype:
        """

        self.assertTrue(expr=allianceauth_discordbot_installed())

    @modify_settings(INSTALLED_APPS={"remove": "aadiscordbot"})
    def test_allianceauth_discordbot_installed_should_return_false(self):
        """
        Test allianceauth_discordbot_installed should return False

        :return:
        :rtype:
        """

        self.assertFalse(expr=allianceauth_discordbot_installed())

    @modify_settings(INSTALLED_APPS={"append": "aadiscordbot"})
    def test_discord_messaging_proxy_available_return_true(self):
        """
        Test discord_messaging_proxy_available should return True for aadiscordbot

        :return:
        :rtype:
        """

        self.assertTrue(expr=discord_messaging_proxy_available())

    @modify_settings(INSTALLED_APPS={"append": "timezones"})
    def test_aa_timezones_installed_should_return_true(self):
        """
        Test aa_timezones_installed should return True

        :return:
        :rtype:
        """

        self.assertTrue(expr=aa_timezones_installed())

    @modify_settings(INSTALLED_APPS={"remove": "timezones"})
    def test_aa_timezones_installed_should_return_false(self):
        """
        Test aa_timezones_installed should return False

        :return:
        :rtype:
        """

        self.assertFalse(expr=aa_timezones_installed())


class TestDebugCheck(BaseTestCase):
    """
    Test if debug is enabled
    """

    @override_settings(DEBUG=True)
    def test_debug_enabled_with_debug_true(self) -> None:
        """
        Test debug_enabled with DEBUG = True

        :return:
        :rtype:
        """

        self.assertTrue(debug_enabled())

    @override_settings(DEBUG=False)
    def test_debug_enabled_with_debug_false(self) -> None:
        """
        Test debug_enabled with DEBUG = False

        :return:
        :rtype:
        """

        self.assertFalse(debug_enabled())


class TestDiscordProxyInstalled(BaseTestCase):
    """
    Test discordproxy_installed function
    """

    @patch("discordproxy.client.DiscordClient")
    def test_returns_true_when_discordclient_imported_successfully(
        self, mock_discord_client
    ):
        """
        Test returns true when discordclient import successfully

        :param mock_discord_client:
        :type mock_discord_client:
        :return:
        :rtype:
        """

        result = discordproxy_installed()
        self.assertTrue(result)

    @patch("builtins.__import__")
    def test_returns_false_when_discordclient_import_fails(self, mock_import):
        """
        Test returns false when discordclient import fails

        :param mock_import:
        :type mock_import:
        :return:
        :rtype:
        """

        # Make the mocked __import__ raise ModuleNotFoundError only for
        # imports that target the discordproxy package. This avoids breaking
        # unrelated imports (coverage, test infrastructure) while still
        # simulating that discordproxy cannot be imported.
        # Capture the original import implementation from importlib so we
        # don't end up calling the mocked `__import__` and recursing.
        real_import = importlib.__import__

        def selective_import(name, globals=None, locals=None, fromlist=(), level=0):
            if isinstance(name, str) and name.startswith("discordproxy"):
                raise ModuleNotFoundError
            return real_import(name, globals, locals, fromlist, level)

        mock_import.side_effect = selective_import

        result = discordproxy_installed()
        self.assertFalse(result)
