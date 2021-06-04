"""
Constants
"""

from django.utils.text import slugify

from aa_forum import __version__

github_url = "https://github.com/ppfeufer/aa-forum"
verbose_name = "AA-Forum - A simple forum for Alliance Auth"
verbose_name_slug = slugify(verbose_name, allow_unicode=True)
user_agent = f"{verbose_name_slug} v{__version__} {github_url}"

TOPICS_PER_PAGE = 20
MESSAGES_PER_PAGE = 20
