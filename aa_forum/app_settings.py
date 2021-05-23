"""
Our app setting
"""

from aasrp.utils import clean_setting

from django.apps import apps

# AA-GDPR
AVOID_CDN = clean_setting("AVOID_CDN", False)


def avoid_cdn() -> bool:
    """
    Check if we should avoid CDN usage
    :return: bool
    """

    return AVOID_CDN


def allianceauth_discordbot_active():
    """
    Check if allianceauth-discordbot is installed and active
    :return:
    """

    return apps.is_installed("aadiscordbot")


def aa_discordnotify_active():
    """
    Check if aa-discordnotfify is installed and active
    :return:
    """

    return apps.is_installed("discordnotify")
