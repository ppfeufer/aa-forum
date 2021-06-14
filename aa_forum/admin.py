"""
Django admin declarations
"""

from django.contrib import admin

from aa_forum.models import Board, Category


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    """
    Category admin
    """

    list_display = ("name", "slug")
    exclude = ("slug", "is_collapsible", "order")


@admin.register(Board)
class BoardsAdmin(admin.ModelAdmin):
    """
    Board admin
    """

    list_display = ("name", "slug")
    exclude = ("slug", "parent_board", "groups", "order")
