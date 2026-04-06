"""
URLs for the forum app.
"""

# Django
from django.urls import path

# AA Forum
from aa_forum.constants import INTERNAL_URL_PREFIX
from aa_forum.views import forum

# Forum "public" URLs
urls = [
    path(route="", view=forum.index, name="forum_index"),
    # Forum URLs :: Board
    path(
        route="<slug:category_slug>/<slug:board_slug>/",
        view=forum.board,
        name="forum_board",
    ),
    path(
        route="<slug:category_slug>/<slug:board_slug>/page/<int:page_number>/",
        view=forum.board,
        name="forum_board",
    ),
    path(
        route=(
            f"{INTERNAL_URL_PREFIX}/<slug:category_slug>/<slug:board_slug>/new-topic/"
        ),
        view=forum.board_new_topic,
        name="forum_board_new_topic",
    ),
    # Forum URLs :: Topic
    path(
        route="<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/",
        view=forum.topic,
        name="forum_topic",
    ),
    path(
        route=(
            "<slug:category_slug>/<slug:board_slug>/"
            "<slug:topic_slug>/page/<int:page_number>/"
        ),
        view=forum.topic,
        name="forum_topic",
    ),
    path(
        route="<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/reply/",
        view=forum.topic_reply,
        name="forum_topic_reply",
    ),
    path(
        route="<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/unread/",
        view=forum.topic_first_unread_message,
        name="forum_topic_first_unread_message",
    ),
    path(
        route="<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/modify/",
        view=forum.topic_modify,
        name="forum_topic_modify",
    ),
    # Forum URLs :: Message
    path(
        route=(
            "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/<int:message_id>/"
        ),
        view=forum.message,
        name="forum_message",
    ),
    path(
        route=(
            "<slug:category_slug>/<slug:board_slug>/"
            "<slug:topic_slug>/<int:message_id>/modify/"
        ),
        view=forum.message_modify,
        name="forum_message_modify",
    ),
]
