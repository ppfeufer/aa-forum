"""
AA-Forum url config
"""

from django.conf.urls import url

from aa_forum.views import admin, forum

app_name: str = "aa_forum"

urlpatterns = [
    url(r"^$", forum.forum_index, name="forum_index"),
    # Admin URLs (These need to be first!)
    url(r"^admin/$", admin.admin_index, name="admin_index"),
    url(
        r"^admin/category/create/$",
        admin.admin_category_create,
        name="admin_category_create",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/edit/$",
        admin.admin_category_edit,
        name="admin_category_edit",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/delete/$",
        admin.admin_category_delete,
        name="admin_category_delete",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/board/create/$",
        admin.admin_board_create,
        name="admin_board_create",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/board/(?P<board_id>[0-9]+)/edit/$",
        admin.admin_board_edit,
        name="admin_board_edit",
    ),
    url(
        r"^admin/category/(?P<category_id>[0-9]+)/board/(?P<board_id>[0-9]+)/delete/$",
        admin.admin_board_delete,
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
        r"^topic/(?P<topic_id>[0-9]+)/change-lock-state/$",
        admin.topic_change_lock_state,
        name="admin_topic_change_lock_state",
    ),
    # Forum URLs (This needs to be the last block!)
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/$",
        forum.forum_board,
        name="forum_board",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/(?P<page_number>[0-9]+)/$",
        forum.forum_board,
        name="forum_board",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/new-topic/$",
        forum.forum_board_new_topic,
        name="forum_board_new_topic",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/(?P<topic_slug>[\w-]+)/$",
        forum.forum_topic,
        name="forum_topic",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/"
        r"(?P<topic_slug>[\w-]+)/(?P<page_number>[0-9]+)/$",
        forum.forum_topic,
        name="forum_topic",
    ),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/"
        r"(?P<topic_slug>[\w-]+)/reply/$",
        forum.forum_topic_reply,
        name="forum_topic_reply",
    ),
]
