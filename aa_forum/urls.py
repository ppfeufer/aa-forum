"""
aasrp url config
"""

from django.conf.urls import url

from aa_forum.views import administration, forum

app_name: str = "aa_forum"

urlpatterns = [
    url(r"^$", forum.forum_index, name="forum_index"),
    url(r"^admin/$", administration.admin_index, name="admin_index"),
]
