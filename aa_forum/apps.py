"""
App config
"""

# Django
from django.apps import AppConfig

# AA Forum
from aa_forum import __version__


class AaForumConfig(AppConfig):
    """
    Application config
    """

    name = "aa_forum"
    label = "aa_forum"
    verbose_name = f"AA Forum v{__version__}"

    def ready(self):
        """
        Make sure we can utilize signals
        :return:
        """

        # AA Forum
        import aa_forum.signals  # noqa: F401 # pylint: disable=unused-import, import-outside-toplevel
