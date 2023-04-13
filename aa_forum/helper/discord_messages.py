"""
Helper to handle Discord messaging to users (Discord DM)
"""

# Standard Library
from datetime import datetime

# Third Party
from dhooks_lite import Embed, Footer, Image, Webhook

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import reverse_absolute

# AA Forum
from aa_forum import __title__
from aa_forum.app_settings import (
    allianceauth_discordbot_installed,
    discordproxy_installed,
)
from aa_forum.constants import DISCORD_EMBED_COLOR_MAP
from aa_forum.helper.eve_images import get_character_portrait_from_evecharacter
from aa_forum.helper.text import get_image_url, prepare_message_for_discord
from aa_forum.models import Board, Message, PersonalMessage, Topic

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def _aadiscordbot_send_private_message(
    user_id: int, level: str, title: str, message: str, embed_message: bool = True
) -> None:
    """
    Try to send a PM to a user on Discord via allianceauth-discordbot
    :param user_id:
    :param level:
    :param title:
    :param message:
    :param embed_message:
    :return:
    """

    if allianceauth_discordbot_installed():
        logger.debug(
            "allianceauth-discordbot is active, trying to send private message"
        )

        # Third Party
        from aadiscordbot.tasks import send_message
        from discord import Embed

        embed = Embed(
            title=str(title),
            description=message,
            color=DISCORD_EMBED_COLOR_MAP.get(level, None),
            timestamp=datetime.now(),
        )

        if embed_message is True:
            send_message(user_id=user_id, embed=embed)
        else:
            send_message(user_id=user_id, message=f"**{title}**\n\n{message}")
    else:
        logger.debug(
            "allianceauth-discordbot is not available on this "
            "system to send the private message"
        )


def _discordproxy_send_private_message(
    user_id: int, level: str, title: str, message: str, embed_message: bool = True
):
    """
    Try to send a PM to a user on Discord via discordproxy
    (fall back to allianceauth-discordbot if needed)
    :param user_id:
    :param level:
    :param title:
    :param message:
    :param embed_message:
    :return:
    """

    # Third Party
    from discordproxy.client import DiscordClient
    from discordproxy.exceptions import DiscordProxyException

    client = DiscordClient()

    try:
        logger.debug("Trying to send a direct message via discordproxy")

        if embed_message is True:
            # Third Party
            from discordproxy.discord_api_pb2 import Embed

            footer = Embed.Footer(text=__title__)
            embed = Embed(
                title=str(title),
                description=message,
                color=DISCORD_EMBED_COLOR_MAP.get(level, None),
                timestamp=timezone.now().isoformat(),
                footer=footer,
            )

            client.create_direct_message(user_id=user_id, embed=embed)
        else:
            client.create_direct_message(
                user_id=user_id, content=f"**{title}**\n\n{message}"
            )
    except DiscordProxyException as ex:
        # Something went wrong with discordproxy
        # Fail silently and try if allianceauth-discordbot is available
        # as a last ditch effort to get the message out to Discord
        logger.debug(
            "Something went wrong with discordproxy, "
            "cannot send a direct message, trying allianceauth-discordbot "
            f"to send the message if available. Error: {ex}"
        )

        _aadiscordbot_send_private_message(
            user_id=user_id,
            level=level,
            title=title,
            message=message,
            embed_message=embed_message,
        )


def send_new_personal_message_notification(
    message: PersonalMessage, embed_message: bool = True
) -> None:
    """
    Send a DM to the recipient of a personal message
    :param message:
    :param embed_message:
    :return:
    """

    # Needs to be imported here, otherwise it's a circular import
    # AA Forum
    from aa_forum.helper.user import get_main_character_from_user, get_user_profile

    recipient_forum_settings = get_user_profile(message.recipient)

    if recipient_forum_settings.discord_dm_on_new_personal_message is True and hasattr(
        message.recipient, "discord"
    ):
        # Get the main characters for sender and recipient
        sender_main_char = get_main_character_from_user(message.sender)
        recipient_main_char = get_main_character_from_user(message.recipient)

        logger.debug(
            f"Sending Discord PM to {recipient_main_char} to "
            "notify about a new personal message"
        )

        message_to_send = prepare_message_for_discord(
            message=message.message, message_length=750
        )
        forum_pm_url = reverse_absolute("aa_forum:personal_messages_inbox")
        dm_level = "info"
        dm_title = "Forum: New Personal Message"
        dm_text = (
            f"Hey {recipient_main_char},\nYou received a new personal message.\n\n"
        )
        dm_text += f"**Sender:** {sender_main_char}\n"
        dm_text += f"**Subject:** {message.subject}\n\n"
        dm_text += f"**Message:**\n{message_to_send}\n\n"
        dm_text += f"[Your Personal Messages]({forum_pm_url})"

        if discordproxy_installed():
            logger.debug("discordproxy seems to be available …")

            _discordproxy_send_private_message(
                user_id=int(message.recipient.discord.uid),
                level=dm_level,
                title=dm_title,
                message=dm_text,
                embed_message=embed_message,
            )
        else:
            # discordproxy not available, try if allianceauth-discordbot is
            # available
            logger.debug(
                "discordproxy not available to send a direct message, "
                "let's see if we can use allianceauth-discordbot if available"
            )

            _aadiscordbot_send_private_message(
                user_id=int(message.recipient.discord.uid),
                level=dm_level,
                title=dm_title,
                message=dm_text,
                embed_message=embed_message,
            )


def send_message_to_discord_webhook(
    board: Board, topic: Topic, message: Message, headline: str
):
    """
    Send a message to a Discord Webhook
    :param board:
    :param topic:
    :param message:
    :param headline:
    :return:
    """

    discord_webhook = Webhook(board.discord_webhook)
    message_to_send = prepare_message_for_discord(message=message.message)
    embed_color = DISCORD_EMBED_COLOR_MAP.get("info", None)
    image_url = get_image_url(message.message)
    author_eve_avatar = get_character_portrait_from_evecharacter(
        character=message.user_created.profile.main_character, size=256
    )
    author_eve_name = message.user_created.profile.main_character.character_name

    if message.pk == message.topic.first_message.pk:
        title = topic.subject
        url = reverse_absolute(
            "aa_forum:forum_topic",
            args=[board.category.slug, board.slug, topic.slug],
        )
    else:
        title = f"Re: {topic.subject}"
        url = reverse_absolute(
            "aa_forum:forum_message",
            args=[board.category.slug, board.slug, topic.slug, message.pk],
        )

    embed = Embed(
        description=message_to_send,
        title=title,
        url=url,
        timestamp=message.time_posted,
        color=embed_color,
        footer=Footer(f"Posted by: {author_eve_name}", author_eve_avatar),
        image=Image(image_url) if image_url else None,
        # thumbnail=Thumbnail(author_eve_avatar),
        # author=Author(
        #     author_eve_name,
        #     # url="https://en.wikipedia.org/wiki/Albert_Einstein",
        #     icon_url=author_eve_avatar,
        # ),
        # fields=[
        #     Field("1st Measurement", "Failed"),
        #     Field("2nd Measurement", "Succeeded"),
        # ],
    )

    discord_webhook.execute(
        headline,
        # username=author_eve_name,
        # avatar_url=author_eve_avatar,
        embeds=[embed],
        wait_for_response=True,
    )
