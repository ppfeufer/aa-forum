"""
aasrp url config
"""

from django.conf.urls import url
from django.urls import path

from aa_forum.views import administration, forum

app_name: str = "aa_forum"

urlpatterns = [
    url(r"^$", forum.forum_index, name="forum_index"),
    path(
        "<str:category_slug>/<str:board_slug>/",
        forum.forum_board,
        name="forum_board",
    ),
    # url(
    #     r"^<str:category_slug>/<str:board_slug>/<str:topic_slug>/$",
    #     forum.forum_topic,
    #     name="forum_topic",
    # ),
    url(r"^admin/$", administration.admin_index, name="admin_index"),
]
