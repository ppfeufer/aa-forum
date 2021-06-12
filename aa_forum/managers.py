"""
Managers for our models
"""

from django.db import models


class SettingsManager(models.Manager):
    """
    AFatManager
    """

    def get_setting(self, setting_key: str) -> str:
        """
        Apply select_related for default query optimizations.
        """

        return self.values_list("value", flat=True).get(variable__exact=setting_key)
