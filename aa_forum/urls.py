"""
AA-Forum url config
"""
from django.conf.urls import url

from aa_forum.views import admin, forum

app_name: str = "aa_forum"

urlpatterns = [
    url(r"^$", forum.forum_index, name="forum_index"),
    url(
        r"^(?P<category_slug>[\w-]+)/(?P<board_slug>[\w-]+)/$",
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
    url(r"^admin/$", admin.admin_index, name="admin_index"),
    url(
        r"^admin_ajax_category_order/$",
        admin.ajax_category_order,
        name="admin_ajax_category_order",
    ),
    url(
        r"^admin_ajax_board_order/$",
        admin.ajax_board_order,
        name="admin_ajax_board_order",
    ),
]
