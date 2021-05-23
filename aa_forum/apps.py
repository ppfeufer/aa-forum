"""
App config
"""

from django.apps import AppConfig

from aa_forum import __version__


class AaForumConfig(AppConfig):
    """
    Application config
    """

    name = "aa_forum"
    label = "aa_forum"
    verbose_name = f"AA Forum v{__version__}"
