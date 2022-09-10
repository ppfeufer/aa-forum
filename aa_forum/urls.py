"""
AA-Forum path config
"""

# Django
from django.urls import include, path

# AA Forum
from aa_forum.constants import INTERNAL_URL_PREFIX
from aa_forum.views import admin, forum, personal_messages, profile, search

app_name: str = "aa_forum"

# Internal URLs
internal_urls = [
    # Admin URLs (Menu Item :: Categories and Boards)
    path(
        route="admin/categories-and-boards/",
        view=admin.categories_and_boards,
        name="admin_categories_and_boards",
    ),
    path(
        route="admin/categories-and-boards/category/create/",
        view=admin.category_create,
        name="admin_category_create",
    ),
    path(
        route="admin/categories-and-boards/category/<int:category_id>/edit/",
        view=admin.category_edit,
        name="admin_category_edit",
    ),
    path(
        route="admin/categories-and-boards/category/<int:category_id>/delete/",
        view=admin.category_delete,
        name="admin_category_delete",
    ),
    path(
        route="admin/categories-and-boards/category/<int:category_id>/board/create/",
        view=admin.board_create,
        name="admin_board_create",
    ),
    path(
        route=(
            "admin/categories-and-boards/category/"
            "<int:category_id>/board/<int:board_id>/create-child-board/"
        ),
        view=admin.board_create_child,
        name="admin_board_create_child",
    ),
    path(
        route=(
            "admin/categories-and-boards/category/"
            "<int:category_id>/board/<int:board_id>/edit/"
        ),
        view=admin.board_edit,
        name="admin_board_edit",
    ),
    path(
        route=(
            "admin/categories-and-boards/category/"
            "<int:category_id>/board/<int:board_id>/delete/"
        ),
        view=admin.board_delete,
        name="admin_board_delete",
    ),
    # Admin Ajax URLs (Menu Item :: Categories and Boards)
    path(
        route="ajax/admin/categories-and-boards/category-order/",
        view=admin.ajax_category_order,
        name="admin_ajax_category_order",
    ),
    path(
        route="ajax/admin/categories-and-boards/board-order/",
        view=admin.ajax_board_order,
        name="admin_ajax_board_order",
    ),
    # Admin URLs (Menu Item :: Forum Settings)
    path(
        route="admin/forum-settings/",
        view=admin.forum_settings,
        name="admin_forum_settings",
    ),
    # Profile URLs
    path(
        route="profile/",
        view=profile.index,
        name="profile_index",
    ),
    # Personal Messages URLs
    path(
        route="personal-messages/inbox/",
        view=personal_messages.inbox,
        name="personal_messages_inbox",
    ),
    path(
        route="personal-messages/inbox/page/<int:page_number>/",
        view=personal_messages.inbox,
        name="personal_messages_inbox",
    ),
    path(
        route="personal-messages/new-message/",
        view=personal_messages.new_message,
        name="personal_messages_new_message",
    ),
    path(
        route="personal-messages/sent-messages/",
        view=personal_messages.sent_messages,
        name="personal_messages_sent_messages",
    ),
    path(
        route="personal-messages/sent-messages/page/<int:page_number>/",
        view=personal_messages.sent_messages,
        name="personal_messages_sent_messages",
    ),
    path(
        route="personal-messages/inbox/message/<int:message_id>/reply/",
        view=personal_messages.reply_message,
        name="personal_messages_message_reply",
    ),
    path(
        route="personal-messages/<str:folder>/message/<int:message_id>/delete/",
        view=personal_messages.delete_message,
        name="personal_messages_message_delete",
    ),
    # Personal Messages Ajax URLs
    path(
        route="ajax/personal-messages/<str:folder>/read-message/",
        view=personal_messages.ajax_read_message,
        name="personal_messages_ajax_read_message",
    ),
    path(
        route="ajax/personal-messages/unread-messages-count/",
        view=personal_messages.ajax_unread_messages_count,
        name="personal_messages_ajax_unread_messages_count",
    ),
    # Service URLs
    path(
        route="message/<int:message_id>/delete/",
        view=forum.message_delete,
        name="forum_message_delete",
    ),
    path(
        route="topic/<int:topic_id>/change-lock-state/",
        view=forum.topic_change_lock_state,
        name="forum_topic_change_lock_state",
    ),
    path(
        route="topic/<int:topic_id>/change-sticky-state/",
        view=forum.topic_change_sticky_state,
        name="forum_topic_change_sticky_state",
    ),
    path(
        route="topic/<int:topic_id>/delete/",
        view=forum.topic_delete,
        name="forum_topic_delete",
    ),
    path(
        route="search/",
        view=search.results,
        name="search_results",
    ),
    path(
        route="search/page/<int:page_number>/",
        view=search.results,
        name="search_results",
    ),
    path(
        route="unread/",
        view=forum.topic_show_all_unread,
        name="forum_topic_show_all_unread",
    ),
    path(
        route="mark-all-as-read/",
        view=forum.mark_all_as_read,
        name="forum_mark_all_as_read",
    ),
]

# Forum "public" URLs
forum_urls = [
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

# Put it all together
# IMPORTANT
# All internal URLs need to start with the designated prefix `{INTERNAL_URL_PREFIX}` to
# prevent conflicts with user generated forum URLs
urlpatterns = [
    # Forum internal URLs (Need to be first in line)
    path(f"{INTERNAL_URL_PREFIX}/", include(internal_urls)),
    # Forum "public" URLs
    path("", include(forum_urls)),
]
