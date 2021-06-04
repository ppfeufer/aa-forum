"""
Template tag

Do some useful stuff with a User object
"""

from django.contrib.auth.models import User
from django.template.defaulttags import register


@register.filter
def main_character_name(user: User) -> str:
    """
    Get the users main character name, or return the username if no main character
    :param user:
    :type user:
    :return:
    :rtype:
    """

    try:
        return_value = user.profile.main_character.character_name
    except AttributeError:
        return_value = user.username

    return return_value


@register.filter
def main_character_id(user: User) -> int:
    """
    Get the users main character id, or return 1 if no main character
    :param user:
    :type user:
    :return:
    :rtype:
    """

    try:
        return_value = user.profile.main_character.character_id
    except AttributeError:
        return_value = 1

    return return_value
