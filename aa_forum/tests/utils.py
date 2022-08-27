"""
Helper for our tests
"""

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
from django.template import Context, Template
from django.utils.timezone import now

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA Forum
from aa_forum.models import (
    Board,
    Category,
    LastMessageSeen,
    Message,
    PersonalMessage,
    Setting,
    Topic,
)

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
    permissions: List[str] = None,
    **kwargs,
) -> User:
    """
    Create a fake user incl. main character and (optional) permissions.
    :param character_id:
    :param character_name:
    :param corporation_id:
    :param corporation_name:
    :param corporation_ticker:
    :param permissions:
    :param kwargs:
    :return:
    """

    username = re.sub(r"[^\w\d@\.\+-]", "_", character_name)
    user = AuthUtils.create_user(username)

    if not corporation_id:
        corporation_id = 2001
        corporation_name = "Wayne Technologies Inc."
        corporation_ticker = "WTE"

    alliance_id = kwargs.get("alliance_id", 3001)
    alliance_name = (
        kwargs.get("alliance_name", "Wayne Enterprises")
        if alliance_id is not None
        else ""
    )

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
    :param topic:
    :param user:
    :return:
    """

    return Message.objects.create(
        topic=topic, message=f"<p>{fake.sentence()}</p>", user_created=user
    )


def create_fake_messages(topic: Topic, amount) -> List[Message]:
    """
    Create a bunch of fake messages in given topic.
    :param topic:
    :param amount:
    :return:
    """

    users = list(User.objects.all())
    messages = []

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

    new_message_datetime = NEW_MESSAGE_DATETIME + dt.timedelta(
        minutes=MESSAGE_DATETIME_MINUTES_OFFSET
    )

    MESSAGE_DATETIME_MINUTES_OFFSET += 2

    return new_message_datetime


def my_get_setting(setting_key: str) -> str:
    """
    Overload settings for tests.
    :param setting_key:
    :return:
    """

    if setting_key == Setting.MESSAGESPERPAGE:
        return "5"

    return Setting.objects.get_setting(setting_key=setting_key)


# Factories for test objects
def create_category(**kwargs) -> Category:
    """
    Create category
    :param kwargs:
    :return:
    """

    if "name" not in kwargs:
        kwargs["name"] = fake.name()

    return Category.objects.create(**kwargs)


def create_board(**kwargs) -> Board:
    """
    Create board
    :param kwargs:
    :return:
    """

    if "name" not in kwargs:
        kwargs["name"] = fake.name()

    if "category" not in kwargs:
        kwargs["category"] = create_category()

    return Board.objects.create(**kwargs)


def create_topic(**kwargs) -> Topic:
    """
    Create topic
    :param kwargs:
    :return:
    """

    if "subject" not in kwargs:
        kwargs["subject"] = fake.name()

    if "board" not in kwargs:
        kwargs["board"] = create_board()

    return Topic.objects.create(**kwargs)


def create_message(**kwargs) -> Message:
    """
    Create message
    :param kwargs:
    :return:
    """

    if "message" not in kwargs:
        kwargs["message"] = f"<p>{fake.sentence()}</p>"

    return Message.objects.create(**kwargs)


def create_last_message_seen(**kwargs):
    """
    Create last message seen
    :param kwargs:
    :return:
    """

    if "user" not in kwargs:
        kwargs["user"] = get_or_create_fake_user(1001, "Bruce Wayne")

    return LastMessageSeen.objects.create(**kwargs)


def create_personal_message(**kwargs) -> PersonalMessage:
    """
    Create personal message
    :param kwargs:
    :return:
    """

    if "sender" not in kwargs:
        kwargs["sender"] = get_or_create_fake_user(1001, "Bruce Wayne")

    if "recipient" not in kwargs:
        kwargs["recipient"] = get_or_create_fake_user(1011, "Lex Luthor")

    if "subject" not in kwargs:
        kwargs["subject"] = fake.sentence()

    return PersonalMessage.objects.create(**kwargs)


def create_setting(**kwargs) -> Setting:
    """
    Create setting
    :param kwargs:
    :return:
    """

    return Setting.objects.create(**kwargs)


def get_or_create_fake_user(*args, **kwargs) -> User:
    """
    Same as create_fake_user but will not fail when user already exists.
    """

    if len(args) > 1:
        character_name = args[1]
    elif "character_name" in kwargs:
        character_name = kwargs["character_name"]
    else:
        ValueError("character_name is not defined")

    username = character_name.replace("'", "").replace(" ", "_")

    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return create_fake_user(*args, **kwargs)


def render_template(string, context=None):
    """
    Helper to render templates
    :param string:
    :param context:
    :return:
    """

    context = context or {}
    context = Context(context)

    return Template(string).render(context)
