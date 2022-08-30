"""
User helper
"""

# Django
from django.contrib.auth.models import User

# AA Forum
from aa_forum.models import UserProfile, get_sentinel_user


def get_user_profile(user: User) -> UserProfile:
    """
    Get a users settings or create them
    :param user:
    :return:
    """

    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    return user_profile


def get_main_character_from_user(user: User) -> str:
    """
    Get the main character from a user
    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        sentinel_user = get_sentinel_user()

        return sentinel_user.username

    try:
        return_value = user.profile.main_character.character_name
    except AttributeError:
        return str(user)

    return return_value
