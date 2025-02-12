"""
App settings

This module provides functions to check if certain apps are installed and active
"""

# Standard Library
from re import RegexFlag

# Django
from django.apps import apps
from django.conf import settings

# Port used to communicate with Discord Proxy
DISCORDPROXY_PORT = getattr(settings, "DISCORDPROXY_PORT", 50051)

# Host used to communicate with Discord Proxy
DISCORDPROXY_HOST = getattr(settings, "DISCORDPROXY_HOST", "localhost")

# Timeout for Discord Proxy communication
DISCORDPROXY_TIMEOUT = getattr(settings, "DISCORDPROXY_TIMEOUT", 300)


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


def debug_enabled() -> RegexFlag:
    """
    Check if DEBUG is enabled

    :return:
    :rtype:
    """

    return settings.DEBUG
