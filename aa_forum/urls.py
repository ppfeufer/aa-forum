"""
aasrp url config
"""

from django.conf.urls import url

from aa_forum.views import forum

app_name: str = "aa_forum"

urlpatterns = [
    url(r"^$", forum.forum_index, name="forum_index"),
]
