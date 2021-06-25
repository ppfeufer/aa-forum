"""
AA-Forum path config
"""

from django.urls import path

from aa_forum.views import admin, forum, search

app_name: str = "aa_forum"

urlpatterns = [
    path("", forum.index, name="forum_index"),
    # Admin URLs (These need to be first!)
    path("admin/", admin.index, name="admin_index"),
    path(
        "admin/category/create/",
        admin.category_create,
        name="admin_category_create",
    ),
    path(
        "admin/category/<int:category_id>/edit/",
        admin.category_edit,
        name="admin_category_edit",
    ),
    path(
        "admin/category/<int:category_id>/delete/",
        admin.category_delete,
        name="admin_category_delete",
    ),
    path(
        "admin/category/<int:category_id>/board/create/",
        admin.board_create,
        name="admin_board_create",
    ),
    path(
        "admin/category/<int:category_id>/board/<int:board_id>/edit/",
        admin.board_edit,
        name="admin_board_edit",
    ),
    path(
        "admin/category/<int:category_id>/board/<int:board_id>/delete/",
        admin.board_delete,
        name="admin_board_delete",
    ),
    path(
        "ajax/admin/category-order/",
        admin.ajax_category_order,
        name="admin_ajax_category_order",
    ),
    path(
        "ajax/admin/board-order/",
        admin.ajax_board_order,
        name="admin_ajax_board_order",
    ),
    # Service URLs (These have to be before the forum URLs!)
    path(
        "message/<int:message_id>/",
        forum.message_entry_point_in_topic,
        name="forum_message_entry_point_in_topic",
    ),
    path(
        "message/<int:message_id>/delete/",
        forum.message_delete,
        name="forum_message_delete",
    ),
    path(
        "topic/<int:topic_id>/change-lock-state/",
        forum.topic_change_lock_state,
        name="forum_topic_change_lock_state",
    ),
    path(
        "topic/<int:topic_id>/change-sticky-state/",
        forum.topic_change_sticky_state,
        name="forum_topic_change_sticky_state",
    ),
    path(
        "topic/<int:topic_id>/delete/",
        forum.topic_delete,
        name="forum_topic_delete",
    ),
    path(
        "search/",
        search.results,
        name="search_results",
    ),
    path(
        "search/page/<int:page_number>/",
        search.results,
        name="search_results",
    ),
    # Forum URLs (This needs to be the last block!)
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
        "<slug:category_slug>/<slug:board_slug>/new-topic/",
        forum.board_new_topic,
        name="forum_board_new_topic",
    ),
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
        "<slug:category_slug>/<slug:board_slug>/"
        "<slug:topic_slug>/modify/<int:message_id>/",
        forum.message_modify,
        name="forum_message_modify",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/unread/",
        forum.topic_unread,
        name="forum_topic_unread",
    ),
]
