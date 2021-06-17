"""
Managers for our models
"""

from django.db import models


class SettingsManager(models.Manager):
    """
    SettingsManager
    """

    def get_setting(self, setting_key: str) -> str:
        """
        Return the value for given setting key
        """

        return self.get(variable=setting_key).value
