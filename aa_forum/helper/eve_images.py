"""
Eve images
"""

# Alliance Auth
from allianceauth.eveonline.evelinks.eveimageserver import character_portrait_url
from allianceauth.eveonline.models import EveCharacter


def get_character_portrait_from_evecharacter(
    character: EveCharacter, size: int = 32, as_html: bool = False
) -> str:
    """
    Get the character portrait URL from EveCharacter model
    :param character:
    :param size:
    :param as_html:
    :return:
    """

    portrait_url = character_portrait_url(
        character_id=character.character_id, size=size
    )

    return_value = portrait_url

    if as_html is True:
        character_name = character.character_name
        return_value = (
            '<img class="aa-forum-character-portrait img-rounded" '
            f'src="{portrait_url}" alt="{character_name}" '
            f'width="{size}" height="{size}">'
        )

    return return_value
