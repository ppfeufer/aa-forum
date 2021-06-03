"""
Django admin declarations
"""

from django.contrib import admin

from aa_forum.models import Boards, Categories, Slugs


def custom_filter(title):
    """
    custom filter for model properties
    :param title:
    :return:
    """

    class Wrapper(admin.FieldListFilter):
        """
        custom_filter :: wrapper
        """

        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title

            return instance

    return Wrapper


@admin.register(Slugs)
class SlugsAdmin(admin.ModelAdmin):
    """
    Slugs admin
    """

    list_display = ("slug",)


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    """
    Categories admin
    """

    list_display = ("name", "slug")
    readonly_fields = ("slug",)


@admin.register(Boards)
class BoardsAdmin(admin.ModelAdmin):
    """
    Boards admin
    """

    list_display = ("name", "slug")
    readonly_fields = ("slug",)
