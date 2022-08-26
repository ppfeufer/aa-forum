"""
Django admin declarations
"""

# Django
from django.contrib import admin
from django.utils.safestring import mark_safe

# AA Forum
from aa_forum.models import Board, Category, Setting, Topic, UserProfile


class SingletonModelAdmin(admin.ModelAdmin):
    """
    Prevents Django admin users deleting the singleton or adding extra rows.
    """

    actions = None  # Removes the default delete action.

    def has_add_permission(self, request):
        """
        Has add permissions
        :param request:
        :return:
        """

        return self.model.objects.all().count() == 0

    def has_change_permission(self, request, obj=None):
        """
        Has change permissions
        :param request:
        :param obj:
        :return:
        """

        return True

    def has_delete_permission(self, request, obj=None):
        return False


class BaseReadOnlyAdminMixin:
    """
    Base "Read Only" mixin for admin models
    """

    def has_add_permission(self, request):
        """
        Has add permissions
        :param request:
        :return:
        """

        return False

    def has_change_permission(self, request, obj=None):
        """
        Has change permissions
        :param request:
        :param obj:
        :return:
        """

        return False

    def has_delete_permission(self, request, obj=None):
        """
        Has delete permissions
        :param request:
        :param obj:
        :return:
        """

        return False


@admin.register(Category)
class CategoryAdmin(BaseReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Category admin
    """

    list_display = ("name", "slug", "_board_count")
    exclude = ("is_collapsible",)

    def _board_count(self, obj):
        """
        Return the board count per category
        :param obj:
        :return:
        """

        return obj.boards.count()


@admin.register(Board)
class BoardAdmin(BaseReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Board admin
    """

    list_display = (
        "name",
        "slug",
        "parent_board",
        "_groups",
        "category",
        "_topics_count",
    )

    def _groups(self, obj):
        """
        Return the groups this board is restricted to as list
        :param obj:
        :return:
        """

        groups = obj.groups.all()

        if groups.count() > 0:
            return mark_safe("<br>".join([group.name for group in groups]))

        return ""

    def _topics_count(self, obj):
        """
        Return the topics count per board
        :param obj:
        :return:
        """

        return obj.topics.count()


@admin.register(Topic)
class TopicAdmin(BaseReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Topic admin
    """

    list_display = ("subject", "slug", "board", "_messages_count")

    def _messages_count(self, obj):
        """
        Return the message count per topic
        :param obj:
        :return:
        """

        return obj.messages.count()


@admin.register(Setting)
class SettingAdmin(SingletonModelAdmin):
    """
    Setting Admin
    """


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Setting Admin
    """

    list_display = ("user",)
