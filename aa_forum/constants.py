"""
Constants
"""

from django.utils.text import slugify

from aa_forum import __version__

github_url = "https://github.com/ppfeufer/aa-forum"
verbose_name = "AA-Forum - A simple forum for Alliance Auth"
verbose_name_slug = slugify(verbose_name, allow_unicode=True)
user_agent = f"{verbose_name_slug} v{__version__} {github_url}"

# Settings keys
SETTING_DATEFORMAT = "defaultDateFormat"
SETTING_TIMEFORMAT = "defaultTimeFormat"
SETTING_MAXMESSAGELENGTH = "maxMessageLength"
SETTING_MESSAGESPERPAGE = "defaultMaxMessages"
SETTING_TOPICSPERPAGE = "defaultMaxTopics"
SETTING_OLDTOPICDAYS = "oldTopicDays"
