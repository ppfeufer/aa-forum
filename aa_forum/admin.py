"""
Django admin declarations
"""

from django.contrib import admin

from aa_forum.models import Boards, Categories


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    """
    Categories admin
    """

    list_display = ("name", "slug")
    exclude = ("slug", "is_collapsible", "order")


@admin.register(Boards)
class BoardsAdmin(admin.ModelAdmin):
    """
    Boards admin
    """

    list_display = ("name", "slug")
    exclude = ("slug", "parent_board", "groups", "order")
