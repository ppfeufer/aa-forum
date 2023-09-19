"""
A couple of variables to use throughout the app
"""

# Standard Library
from importlib import metadata

__version__ = metadata.version(distribution_name="aa-forum")
__title__ = "Forum"

del metadata
