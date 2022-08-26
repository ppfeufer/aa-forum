"""
User helper
"""

# Django
from django.contrib.auth.models import User

# AA Forum
from aa_forum.models import UserProfile


def get_user_profile(user: User) -> UserProfile:
    """
    Get a users settings or create them
    :param user:
    :return:
    """

    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    return user_profile
