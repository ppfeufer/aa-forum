"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.text import format_lazy

# AA Forum
from aa_forum import __title_translated__, __version__


class AaForumConfig(AppConfig):
    """
    AA Forum App Config
    """

    name = "aa_forum"
    label = "aa_forum"
    verbose_name = format_lazy(
        "{app_title} v{version}", app_title=__title_translated__, version=__version__
    )

    def ready(self):
        """
        Make sure we can utilize signals

        :return:
        :rtype:
        """

        # AA Forum
        import aa_forum.signals  # noqa: F401 # pylint: disable=unused-import, import-outside-toplevel
