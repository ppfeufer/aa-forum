# Django
from django.apps import apps
from django.urls import include, path, re_path

# Alliance Auth
from allianceauth import urls

# Alliance auth urls
urlpatterns = [
    path("", include(urls)),
]

# URL configuration for cKeditor
if apps.is_installed("ckeditor"):
    # Django
    from django.contrib.auth.decorators import login_required
    from django.views.decorators.cache import never_cache

    # ckEditor
    from ckeditor_uploader import views as ckeditor_views

    urlpatterns = [
        re_path(
            r"^upload/", login_required(ckeditor_views.upload), name="ckeditor_upload"
        ),
        re_path(
            r"^browse/",
            never_cache(login_required(ckeditor_views.browse)),
            name="ckeditor_browse",
        ),
    ] + urlpatterns
