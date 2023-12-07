"""
Test for app_settings.py
"""

# Django
from django.test import TestCase, modify_settings

# AA Forum
from aa_forum.app_settings import (
    aa_timezones_installed,
    allianceauth_discordbot_installed,
    discord_messaging_proxy_available,
)


class TestModulesInstalled(TestCase):
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
