"""
Hook into AA
"""

from django.utils.translation import ugettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from aa_forum import __title__, urls


class AaForumMenuItem(MenuItemHook):  # pylint: disable=too-few-public-methods
    """
    This class ensures only authorized users will see the menu entry
    """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _(__title__),
            "fas fa-comments fa-fw",
            "aa_forum:forum_index",
            navactive=["aa_forum:"],
        )

    def render(self, request):
        """
        Check if the user has the permission to view this app
        :param request:
        :return:
        """

        if request.user.has_perm("aa_forum.basic_access"):
            # We might add a count of new messages at a later time
            # app_count = AaForumManager.pending_requests_count_for_user(request.user)
            # self.count = app_count if app_count and app_count > 0 else None

            return MenuItemHook.render(self, request)

        return ""


@hooks.register("menu_item_hook")
def register_menu():
    """
    register our menu item
    :return:
    """

    return AaForumMenuItem()


@hooks.register("url_hook")
def register_urls():
    """
    register our basu url
    :return:
    """

    return UrlHook(urls, "aa_forum", r"^forum/")
