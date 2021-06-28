"""
Django admin declarations
"""

from django.contrib import admin

from aa_forum.models import Board, Category, Topic


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category admin
    """

    list_display = ("name", "slug")
    exclude = ("slug", "is_collapsible", "order")


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Board admin
    """

    list_display = ("name", "slug", "category")
    exclude = ("slug", "parent_board", "groups", "order")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """
    Topic admin
    """

    list_display = ("subject", "board", "_messages_count")

    def _messages_count(self, obj):
        return obj.messages.count()
