"""
Internal URLs for the AA Forum app.
"""

# Django
from django.urls import path

# AA Forum
from aa_forum.views import admin, forum, personal_messages, profile, search, widgets

# Internal URLs
urls = [
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
    # "Public" ajax URLs
    path(
        route="ajax/widget/unread-topics/",
        view=widgets.ajax_unread_topics,
        name="widgets_ajax_unread_topics",
    ),
]
