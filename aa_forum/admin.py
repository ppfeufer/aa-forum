"""
Django admin declarations
"""

from django.contrib import admin

from aa_forum.models import Board, Category, Topic


class BaseReadOnlyAdminMixin:
    """
    Base "Read Only" mixin for admin models
    """

    def has_add_permission(self, request):
        """
        Has add permissions
        :param request:
        :type request:
        :return:
        :rtype:
        """

        return False

    def has_change_permission(self, request, obj=None):
        """
        Has change permissions
        :param request:
        :type request:
        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        return False

    def has_delete_permission(self, request, obj=None):
        """
        Has delete permissions
        :param request:
        :type request:
        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        return False


@admin.register(Category)
class CategoryAdmin(BaseReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Category admin
    """

    list_display = ("name", "slug")
    exclude = ("slug", "is_collapsible", "order")


@admin.register(Board)
class BoardAdmin(BaseReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Board admin
    """

    list_display = ("name", "slug", "category")
    exclude = ("slug", "parent_board", "groups", "order")


@admin.register(Topic)
class TopicAdmin(BaseReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Topic admin
    """

    list_display = ("subject", "board", "_messages_count")

    def _messages_count(self, obj):
        """
        Return the message count per topic
        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        return obj.messages.count()
