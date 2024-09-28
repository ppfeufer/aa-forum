"""
URL config for the AA-Forum app
"""

# Django
from django.urls import include, path

# AA Forum
from aa_forum.constants import INTERNAL_URL_PREFIX
from aa_forum.urls import forum, internal

app_name: str = "aa_forum"

# Put it all together
# IMPORTANT
# All internal URLs need to start with the designated prefix `{INTERNAL_URL_PREFIX}` to
# prevent conflicts with user-generated forum URLs.
urlpatterns = [
    # Forum internal URLs (Need to be first in line)
    path(f"{INTERNAL_URL_PREFIX}/", include(internal.urls)),
    # Forum "public" URLs
    path("", include(forum.urls)),
]
