import re
from typing import List

from django.contrib.auth.models import User

from allianceauth.tests.auth_utils import AuthUtils


def create_fake_user(
    character_id: int,
    character_name: str,
    corporation_id: int = None,
    corporation_name: str = None,
    permissions: List[str] = None,
) -> User:
    """Create a fake user incl. main character and (optional) permissions."""
    username = re.sub(r"[^\w\d@\.\+-]", "_", character_name)
    user = AuthUtils.create_user(username)
    params = {"user": user, "name": character_name, "character_id": character_id}
    if corporation_id:
        params["corp_id"] = corporation_id
    if corporation_name:
        params["corp_name"] = corporation_name
    AuthUtils.add_main_character_2(**params)
    if permissions:
        perm_objs = [AuthUtils.get_permission_by_name(perm) for perm in permissions]
        user = AuthUtils.add_permissions_to_user(perms=perm_objs, user=user)
    return user
