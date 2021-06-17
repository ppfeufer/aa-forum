"""
Our app setting
"""

from aasrp.utils import clean_setting

# AA-GDPR
AVOID_CDN = clean_setting("AVOID_CDN", False)


def avoid_cdn() -> bool:
    """
    Check if we should avoid CDN usage
    :return: bool
    """

    return AVOID_CDN
