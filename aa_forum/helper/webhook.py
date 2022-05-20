"""
Discord webhook helper
"""

# Standard Library
import html

# Third Party
from dhooks_lite import Embed, Footer, Image, Webhook

# Django
from django.utils.html import strip_tags

# Alliance Auth (External Libs)
from app_utils.urls import reverse_absolute

# AA Forum
from aa_forum.constants import DISCORD_EMBED_COLOR_MAP, DISCORD_EMBED_MESSAGE_LENGTH
from aa_forum.helper.eve_images import get_character_portrait_from_evecharacter
from aa_forum.helper.text import get_image_url
from aa_forum.models import Board, Message, Topic


def _prepare_message_for_webhook(message: Message) -> str:
    """
    Preparing the message to be sent with a Discord Webhook

    We have to run strip_tags() twice here.
    1. To remove HTML tags from the text we want to send
    2. After html.unescape() in case that unescaped former escaped HTML tags,
    which now need to be removed as well
    :param message:
    :return:
    """

    return strip_tags(
        html.unescape(
            strip_tags(
                message.message[:DISCORD_EMBED_MESSAGE_LENGTH] + "…"
                if len(message.message) > DISCORD_EMBED_MESSAGE_LENGTH
                else message.message
            )
        )
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
    message_to_send = _prepare_message_for_webhook(message=message)
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
