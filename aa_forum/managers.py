"""
Managers for our models
"""

from django.db import models


class SettingsManager(models.Manager):
    """
    SettingsManager
    """

    def get_setting(self, setting_key: str) -> str:
        """Return value for given setting."""

        return self.get(variable=setting_key).value
