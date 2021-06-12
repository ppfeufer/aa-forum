"""
AA-Forum url config
"""

from django.conf.urls import url

from aa_forum.views import admin, forum

app_name: str = "aa_forum"

urlpatterns = [
    url(r"^$", forum.index, name="forum_index"),
    # Admin URLs (These need to be first!)
    url(r"^admin/$", admin.index, name="admin_index"),
    url(
        r"^admin/category/create/$",
        admin.category_create,
        name="admin_category_create",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/edit/$",
        admin.category_edit,
        name="admin_category_edit",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/delete/$",
        admin.category_delete,
        name="admin_category_delete",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/board/create/$",
        admin.board_create,
        name="admin_board_create",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/board/(?P<board_id>[0-9]+)/edit/$",
        admin.board_edit,
        name="admin_board_edit",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/board/(?P<board_id>[0-9]+)/delete/$",
        admin.board_delete,
        name="admin_board_delete",
    ),
    url(
        r"^ajax/admin/category-order/$",
        admin.ajax_category_order,
        name="admin_ajax_category_order",
    ),
    url(
        r"^ajax/admin/board-order/$",
        admin.ajax_board_order,
        name="admin_ajax_board_order",
    ),
    # Service URLs (These have to be before the forum URLs!)
    url(
        r"^message/(?P<message_id>[0-9]+)/$",
        forum.message_entry_point_in_topic,
        name="forum_message_entry_point_in_topic",
    ),
    url(
        r"^message/(?P<message_id>[0-9]+)/delete/$",
        forum.message_delete,
        name="forum_message_delete",
    ),
    url(
        r"^topic/(?P<topic_id>[0-9]+)/change-lock-state/$",
        forum.topic_change_lock_state,
        name="forum_topic_change_lock_state",
    ),
    url(
        r"^topic/(?P<topic_id>[0-9]+)/change-sticky-state/$",
        forum.topic_change_sticky_state,
        name="forum_topic_change_sticky_state",
    ),
    url(
        r"^topic/(?P<topic_id>[0-9]+)/delete/$",
        forum.topic_delete,
        name="forum_topic_delete",
    ),
    # Forum URLs (This needs to be the last block!)
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/$",
        forum.board,
        name="forum_board",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/(?P<page_number>[0-9]+)/$",
        forum.board,
        name="forum_board",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/new-topic/$",
        forum.board_new_topic,
        name="forum_board_new_topic",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/(?P<topic_slug>[\w-]+)/$",
        forum.topic,
        name="forum_topic",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/"
        r"(?P<topic_slug>[\w-]+)/(?P<page_number>[0-9]+)/$",
        forum.topic,
        name="forum_topic",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/"
        r"(?P<topic_slug>[\w-]+)/reply/$",
        forum.topic_reply,
        name="forum_topic_reply",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/"
        r"(?P<topic_slug>[\w-]+)/modify/(?P<message_id>[\w-]+)/$",
        forum.message_modify,
        name="forum_message_modify",
    ),
]
