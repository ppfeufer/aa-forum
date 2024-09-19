"""
AA Forum Admin
"""

# Third Party
from solo.admin import SingletonModelAdmin

# Django
from django.contrib import admin
from django.utils.safestring import mark_safe

# AA Forum
from aa_forum.models import Board, Category, Setting, Topic, UserProfile


class BaseReadOnlyAdminMixin:
    """
    Base "Read-Only" mixin for admin models
    """

    def has_add_permission(self, request):  # pylint: disable=unused-argument
        """
        Has add permissions

        :param request:
        :type request:
        :return:
        :rtype:
        """

        return False

    def has_change_permission(
        self, request, obj=None  # pylint: disable=unused-argument
    ):
        """
        Has "change" permissions

        :param request:
        :type request:
        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        return False

    def has_delete_permission(
        self, request, obj=None  # pylint: disable=unused-argument
    ):
        """
        Has "delete" permissions

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

    list_display = ("name", "slug", "_board_count")
    exclude = ("is_collapsible",)

    def _board_count(self, obj):
        """
        Return the board count per category

        :param obj:
        :type obj:
        :return:
        :rtype:
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
        Return the groups per board

        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        groups = obj.groups.all()

        if groups.count() > 0:
            return mark_safe("<br>".join([group.name for group in groups]))

        return ""

    def _topics_count(self, obj):
        """
        Return the topic count per board

        :param obj:
        :type obj:
        :return:
        :rtype:
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
        :type obj:
        :return:
        :rtype:
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
    User Profile Admin
    """

    list_display = ("user",)
    readonly_fields = ("user",)
