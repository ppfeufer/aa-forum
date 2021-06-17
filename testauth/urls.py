from ckeditor_uploader import views

from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

# *** New Imports for cKeditor
from django.urls import re_path
from django.views.decorators.cache import never_cache

from allianceauth import urls

urlpatterns = [
    # *** New URL override for cKeditor BEFORE THE MAIN IMPORT
    re_path(r"^upload/", login_required(views.upload), name="ckeditor_upload"),
    re_path(
        r"^browse/",
        never_cache(login_required(views.browse)),
        name="ckeditor_browse",
    ),
    # Alliance Auth URLs
    url(r"", include(urls)),
]
