"""
App settings

This module provides functions to check if certain apps are installed and active
"""

# Django
from django.apps import apps


def discordproxy_installed() -> bool:
    """
    Check if discordproxy is installed and active

    :return:
    :rtype:
    """

    try:
        # Third Party
        from discordproxy.client import (  # pylint: disable=import-outside-toplevel unused-import  # noqa: F401
            DiscordClient,
        )
    except ModuleNotFoundError:
        return False

    return True


def allianceauth_discordbot_installed() -> bool:
    """
    Check if allianceauth-discordbot is installed and active

    :return:
    :rtype:
    """

    return apps.is_installed(app_name="aadiscordbot")


def discord_messaging_proxy_available() -> bool:
    """
    Check if discord messaging proxy is available

    :return:
    :rtype:
    """

    return discordproxy_installed() or allianceauth_discordbot_installed()


def aa_timezones_installed() -> bool:
    """
    Check if aa-timezones is installed and active

    :return:
    :rtype:
    """

    return apps.is_installed(app_name="timezones")
