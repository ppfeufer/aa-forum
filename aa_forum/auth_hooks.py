"""
Hooks for the auth app
"""

# Alliance Auth
from allianceauth import hooks
from allianceauth.hooks import DashboardItemHook
from allianceauth.services.hooks import MenuItemHook, UrlHook

# AA Forum
from aa_forum import __title__, urls
from aa_forum.views.forum import unread_topics_count
from aa_forum.views.widgets import dashboard_widgets


class AaForumMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """
    Menu item hook for AA Forum
    """

    def __init__(self):
        """
        Constructor
        """

        self.count = None

        # Setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            text=__title__,
            classes="fa-solid fa-comments",
            url_name="aa_forum:forum_index",
            navactive=["aa_forum:"],
        )

    def get_unread_topics_count(self, request):
        """
        Get the unread topics count

        :param request:
        :type request:
        :return:
        :rtype:
        """

        count_unread_topics = unread_topics_count(request=request)
        self.count = (
            count_unread_topics
            if count_unread_topics and count_unread_topics > 0
            else None
        )

    def render(self, request):
        """
        Render the menu item

        :param request:
        :type request:
        :return:
        :rtype:
        """

        if request.user.has_perm(perm="aa_forum.basic_access"):
            # Get the unread topics count
            self.get_unread_topics_count(request=request)

            # Render the menu item
            return MenuItemHook.render(self, request=request)

        return ""


class AaForumDashboardWidgets(DashboardItemHook):
    """
    This class adds the AA Forum dashboard widgets to the Alliance Auth dashboard.
    """

    def __init__(self):
        # Setup dashboard widget
        DashboardItemHook.__init__(self=self, view_function=dashboard_widgets, order=5)


@hooks.register("menu_item_hook")
def register_menu():
    """
    Register our menu item

    :return:
    :rtype:
    """

    return AaForumMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    Register our urls

    :return:
    :rtype:
    """

    return UrlHook(urls=urls, namespace="aa_forum", base_url=r"^forum/")


@hooks.register("dashboard_hook")
def register_dashboard_widgets():
    """
    Register our dashboard hook

    :return: The hook
    :rtype: AaForumDashboardWidgets
    """

    return AaForumDashboardWidgets()
