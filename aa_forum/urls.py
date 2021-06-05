"""
AA-Forum url config
"""

from django.conf.urls import url
from django.urls import path

from aa_forum.views import administration, forum

app_name: str = "aa_forum"

urlpatterns = [
    url(r"^$", forum.forum_index, name="forum_index"),
    path(
        "<slug:category_slug>/<slug:board_slug>/",
        forum.forum_board,
        name="forum_board",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/new-topic/",
        forum.forum_board_new_topic,
        name="forum_board_new_topic",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/",
        forum.forum_topic,
        name="forum_topic",
    ),
    path(
        "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/<int:page_number>/",
        forum.forum_topic,
        name="forum_topic",
    ),
    # path(
    #     "<slug:category_slug>/<slug:board_slug>/<slug:topic_slug>/response/",
    #     forum.forum_topic_response,
    #     name="forum_topic_response",
    # ),
    url(r"^admin/$", administration.admin_index, name="admin_index"),
]
