# Standard Library
import datetime as dt
import random
import re
from typing import List
from unittest.mock import patch

# Third Party
from faker import Faker

# Django
from django.contrib.auth.models import User
from django.utils.timezone import now

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA Forum
from aa_forum.constants import SETTING_MESSAGESPERPAGE
from aa_forum.models import Message, Setting, Topic

MESSAGE_DATETIME_HOURS_INTO_PAST = 240
MESSAGE_DATETIME_MINUTES_OFFSET = 2
NEW_MESSAGE_DATETIME = now() - dt.timedelta(hours=MESSAGE_DATETIME_HOURS_INTO_PAST)

fake = Faker()


def create_fake_user(
    character_id: int,
    character_name: str,
    corporation_id: int = None,
    corporation_name: str = None,
    corporation_ticker: str = None,
    alliance_id: int = None,
    alliance_name: str = None,
    permissions: List[str] = None,
) -> User:
    """
    Create a fake user incl. main character and (optional) permissions.
    """

    username = re.sub(r"[^\w\d@\.\+-]", "_", character_name)
    user = AuthUtils.create_user(username)

    if not corporation_id:
        corporation_id = 2001
        corporation_name = "Wayne Technologies Inc."
        corporation_ticker = "WTE"

    if not alliance_id:
        alliance_id = 3001
        alliance_name = "Wayne Enterprises"

    AuthUtils.add_main_character_2(
        user=user,
        name=character_name,
        character_id=character_id,
        corp_id=corporation_id,
        corp_name=corporation_name,
        corp_ticker=corporation_ticker,
        alliance_id=alliance_id,
        alliance_name=alliance_name,
    )

    if permissions:
        perm_objs = [AuthUtils.get_permission_by_name(perm) for perm in permissions]
        user = AuthUtils.add_permissions_to_user(perms=perm_objs, user=user)

    return user


def create_fake_message(topic: Topic, user: User):
    """
    Create a fake message.
    """

    return Message.objects.create(
        topic=topic, message=f"<p>{fake.sentence()}</p>", user_created=user
    )


def create_fake_messages(topic: Topic, amount) -> List[Message]:
    """
    Create a bunch of fake messages in given topic.
    """

    users = list(User.objects.all())
    messages = list()

    with patch("django.utils.timezone.now", new=message_datetime):
        for _ in range(amount):
            messages.append(create_fake_message(topic, user=random.choice(users)))

    return messages


def message_datetime():
    """
    Make sure follow-up messages can not be before the earlier message
    :return:
    :rtype:
    """

    global MESSAGE_DATETIME_MINUTES_OFFSET

    message_datetime = NEW_MESSAGE_DATETIME + dt.timedelta(
        minutes=MESSAGE_DATETIME_MINUTES_OFFSET
    )

    MESSAGE_DATETIME_MINUTES_OFFSET += 2

    return message_datetime


def my_get_setting(setting_key: str) -> str:
    """
    Overload settings for tests.
    """

    if setting_key == SETTING_MESSAGESPERPAGE:
        return "5"

    return Setting.objects.get_setting(setting_key=setting_key)
