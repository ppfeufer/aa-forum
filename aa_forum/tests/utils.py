import datetime as dt
import random
import re
from typing import List
from unittest.mock import patch

from faker import Faker

from django.contrib.auth.models import User
from django.utils.timezone import now

from allianceauth.tests.auth_utils import AuthUtils

from aa_forum.constants import SETTING_MESSAGESPERPAGE

from ..models import Message, Setting, Topic

MAX_MESSAGE_HOURS_INTO_PAST = 1000
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
    """Create a fake user incl. main character and (optional) permissions."""
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
    """Create a fake message."""
    return Message.objects.create(
        topic=topic, message=f"<p>{fake.sentence()}</p>", user_created=user
    )


def create_fake_messages(topic: Topic, amount) -> List[Message]:
    """Create a bunch of fake messags in given topic."""
    users = list(User.objects.all())
    messages = list()
    with patch("django.utils.timezone.now", new=random_dt):
        for _ in range(amount):
            messages.append(create_fake_message(topic, user=random.choice(users)))
    return messages


def random_dt() -> dt.datetime:
    """Return random datetime between now and x hours into the past."""
    return now() - dt.timedelta(
        hours=random.randint(0, MAX_MESSAGE_HOURS_INTO_PAST),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )


def my_get_setting(setting_key: str) -> str:
    """Overload settings for tests."""
    if setting_key == SETTING_MESSAGESPERPAGE:
        return "5"
    return Setting.objects.get_setting(setting_key=setting_key)
