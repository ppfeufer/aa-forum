"""
Test URL config
"""

# Django
from django.apps import apps
from django.urls import include, path

# Alliance Auth
from allianceauth import urls

# Alliance auth urls
urlpatterns = [
    path("", include(urls)),
]

# URL configuration for cKeditor
if apps.is_installed("django_ckeditor_5"):
    # Django
    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = (
        [
            path(
                "ckeditor5/",
                include("django_ckeditor_5.urls"),
                name="ck_editor_5_upload_file",
            ),
        ]
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + urlpatterns
    )
