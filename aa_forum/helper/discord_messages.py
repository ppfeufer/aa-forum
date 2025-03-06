"""
Helper functions to send messages to Discord
"""

# Standard Library
from datetime import datetime

# Third Party
from dhooks_lite import Embed as DhooksLiteEmbed
from dhooks_lite import Footer, Image, UserAgent, Webhook

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import reverse_absolute

# AA Forum
from aa_forum import __title__, __version__
from aa_forum.app_settings import (
    DISCORDPROXY_HOST,
    DISCORDPROXY_PORT,
    DISCORDPROXY_TIMEOUT,
    allianceauth_discordbot_installed,
    discordproxy_installed,
)
from aa_forum.constants import (
    APP_NAME_VERBOSE_USERAGENT,
    DISCORD_EMBED_COLOR_MAP,
    GITHUB_URL,
)
from aa_forum.helper.eve_images import get_character_portrait_from_evecharacter
from aa_forum.helper.text import (
    get_first_image_url_from_text,
    prepare_message_for_discord,
)
from aa_forum.models import Board, Message, PersonalMessage, Topic

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def _dhooks_lite_user_agent() -> UserAgent:
    """
    Set the user agent for `dhooks-lite`

    :return: User agent for `dhooks-lite`
    :rtype: UserAgent
    """

    return UserAgent(
        name=APP_NAME_VERBOSE_USERAGENT, url=GITHUB_URL, version=__version__
    )


def _aadiscordbot_send_private_message(
    user_id: int, level: str, title: str, message: str, embed_message: bool = True
) -> None:
    """
    Try to send a PM to a user on Discord via `allianceauth-discordbot`

    :param user_id:
    :type user_id:
    :param level:
    :type level:
    :param title:
    :type title:
    :param message:
    :type message:
    :param embed_message:
    :type embed_message:
    :return:
    :rtype:
    """

    if allianceauth_discordbot_installed():
        logger.debug(
            msg="allianceauth-discordbot is active, trying to send private message"
        )

        # Third Party
        # pylint: disable=import-outside-toplevel
        from aadiscordbot.tasks import send_message

        # pylint: disable=import-outside-toplevel
        from discord import Embed as DiscordEmbed

        embed = DiscordEmbed(
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
            msg=(
                "allianceauth-discordbot is not available on this "
                "system to send the private message"
            )
        )


def _discordproxy_send_private_message(
    user_id: int, level: str, title: str, message: str, embed_message: bool = True
):
    """
    Try to send a PM to a user on Discord via `discordproxy`

    :param user_id:
    :type user_id:
    :param level:
    :type level:
    :param title:
    :type title:
    :param message:
    :type message:
    :param embed_message:
    :type embed_message:
    :return:
    :rtype:
    """

    # Third Party
    from discordproxy.client import (  # pylint: disable=import-outside-toplevel
        DiscordClient,
    )
    from discordproxy.exceptions import (  # pylint: disable=import-outside-toplevel
        DiscordProxyException,
    )

    target = f"{DISCORDPROXY_HOST}:{DISCORDPROXY_PORT}"
    client = DiscordClient(target=target, timeout=DISCORDPROXY_TIMEOUT)

    try:
        logger.debug(msg="Trying to send a direct message via discordproxy")

        if embed_message is True:
            # Third Party
            # pylint: disable=import-outside-toplevel
            from discordproxy.discord_api_pb2 import Embed as DiscordProxyEmbed

            footer = DiscordProxyEmbed.Footer(text=str(__title__))
            embed = DiscordProxyEmbed(
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
            msg=(
                "Something went wrong with discordproxy, "
                "cannot send a direct message, trying allianceauth-discordbot "
                f"to send the message if available. Error: {ex}"
            )
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
    Send a notification to Discord about a new personal message

    :param message:
    :type message:
    :param embed_message:
    :type embed_message:
    :return:
    :rtype:
    """

    # Needs to be imported here, otherwise it's a circular import
    # AA Forum
    from aa_forum.helper.user import (  # pylint: disable=import-outside-toplevel
        get_main_character_from_user,
        get_user_profile,
    )

    recipient_forum_settings = get_user_profile(user=message.recipient)

    if recipient_forum_settings.discord_dm_on_new_personal_message is True and hasattr(
        message.recipient, "discord"
    ):
        # Get the main characters for sender and recipient
        sender_main_char = get_main_character_from_user(user=message.sender)
        recipient_main_char = get_main_character_from_user(user=message.recipient)

        logger.debug(
            msg=(
                f"Sending Discord PM to {recipient_main_char} to "
                "notify about a new personal message"
            )
        )

        message_to_send = prepare_message_for_discord(
            message=message.message, message_length=750
        )
        forum_pm_url = reverse_absolute(viewname="aa_forum:personal_messages_inbox")
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
            logger.debug(msg="discordproxy seems to be available …")

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
                msg=(
                    "discordproxy not available to send a direct message, "
                    "let's see if we can use allianceauth-discordbot if available"
                )
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
    Send a message to a Discord webhook

    :param board:
    :type board:
    :param topic:
    :type topic:
    :param message:
    :type message:
    :param headline:
    :type headline:
    :return:
    :rtype:
    """

    discord_webhook = Webhook(
        url=board.discord_webhook, user_agent=_dhooks_lite_user_agent()
    )
    message_to_send = prepare_message_for_discord(message=message.message)
    embed_color = DISCORD_EMBED_COLOR_MAP.get("info", None)
    image_url = get_first_image_url_from_text(text=message.message)
    author_eve_avatar = get_character_portrait_from_evecharacter(
        character=message.user_created.profile.main_character, size=256
    )
    author_eve_name = message.user_created.profile.main_character.character_name

    if message.pk == message.topic.first_message.pk:
        title = topic.subject
        url = reverse_absolute(
            viewname="aa_forum:forum_topic",
            args=[board.category.slug, board.slug, topic.slug],
        )
    else:
        title = f"Re: {topic.subject}"
        url = reverse_absolute(
            viewname="aa_forum:forum_message",
            args=[board.category.slug, board.slug, topic.slug, message.pk],
        )

    embed = DhooksLiteEmbed(
        description=message_to_send,
        title=title,
        url=url,
        timestamp=message.time_posted,
        color=embed_color,
        footer=Footer(text=f"Posted by: {author_eve_name}", icon_url=author_eve_avatar),
        image=Image(url=image_url) if image_url else None,
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
        content=headline,
        # username=author_eve_name,
        # avatar_url=author_eve_avatar,
        embeds=[embed],
        wait_for_response=True,
    )
