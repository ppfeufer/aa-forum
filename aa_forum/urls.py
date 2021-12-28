"""
AA-Forum path config
"""

# Django
from django.urls import path

# AA Forum
from aa_forum.constants import INTERNAL_URL_PREFIX
from aa_forum.views import admin, forum, search

app_name: str = "aa_forum"

# IMPORTANT
# All internal URLs need to start with the designated prefix
# to prevent conflicts with user generated forum URLs

urlpatterns = [
    path("", forum.index, name="forum_index"),
    # Admin URLs
    path(f"{INTERNAL_URL_PREFIX}/admin/", admin.index, name="admin_index"),
    path(
        f"{INTERNAL_URL_PREFIX}/admin/category/create/",
        admin.category_create,
        name="admin_category_create",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/admin/category/<int:category_id>/edit/",
        admin.category_edit,
        name="admin_category_edit",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/admin/category/<int:category_id>/delete/",
        admin.category_delete,
        name="admin_category_delete",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/admin/category/<int:category_id>/board/create/",
        admin.board_create,
        name="admin_board_create",
    ),
    path(
        (
            f"{INTERNAL_URL_PREFIX}/admin/category/<int:category_id>/board/"
            f"<int:board_id>/create-child-board/"
        ),
        admin.board_create_child,
        name="admin_board_create_child",
    ),
    path(
        (
            f"{INTERNAL_URL_PREFIX}/admin/category/<int:category_id>/board/"
            "<int:board_id>/edit/"
        ),
        admin.board_edit,
        name="admin_board_edit",
    ),
    path(
        (
            f"{INTERNAL_URL_PREFIX}/admin/category/<int:category_id>/board/"
            "<int:board_id>/delete/"
        ),
        admin.board_delete,
        name="admin_board_delete",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/ajax/admin/category-order/",
        admin.ajax_category_order,
        name="admin_ajax_category_order",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/ajax/admin/board-order/",
        admin.ajax_board_order,
        name="admin_ajax_board_order",
    ),
    # Service URLs
    path(
        f"{INTERNAL_URL_PREFIX}/message/<int:message_id>/delete/",
        forum.message_delete,
        name="forum_message_delete",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/topic/<int:topic_id>/change-lock-state/",
        forum.topic_change_lock_state,
        name="forum_topic_change_lock_state",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/topic/<int:topic_id>/change-sticky-state/",
        forum.topic_change_sticky_state,
        name="forum_topic_change_sticky_state",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/topic/<int:topic_id>/delete/",
        forum.topic_delete,
        name="forum_topic_delete",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/search/",
        search.results,
        name="search_results",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/search/page/<int:page_number>/",
        search.results,
        name="search_results",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/unread/",
        forum.topic_show_all_unread,
        name="forum_topic_show_all_unread",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/mark-all-as-read/",
        forum.mark_all_as_read,
        name="forum_mark_all_as_read",
    ),
    # Forum URLs :: Board
    path(
        "<slug:category_slug>/<slug:board_slug>/",
        forum.board,
        name="forum_board",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/page/<int:page_number>/",
        forum.board,
        name="forum_board",
    ),
    path(
        f"{INTERNAL_URL_PREFIX}/<slug:category_slug>/<slug:board_slug>/new-topic/",
        forum.board_new_topic,
        name="forum_board_new_topic",
    ),
    # Forum URLs :: Topic
    path(
        "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/",
        forum.topic,
        name="forum_topic",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/"
        "<slug:topic_slug>/page/<int:page_number>/",
        forum.topic,
        name="forum_topic",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/reply/",
        forum.topic_reply,
        name="forum_topic_reply",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/unread/",
        forum.topic_first_unread_message,
        name="forum_topic_first_unread_message",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/modify/",
        forum.topic_modify,
        name="forum_topic_modify",
    ),
    # Forum URLs :: Message
    path(
        "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/<int:message_id>/",
        forum.message,
        name="forum_message",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/"
        "<slug:topic_slug>/<int:message_id>/modify/",
        forum.message_modify,
        name="forum_message_modify",
    ),
]
