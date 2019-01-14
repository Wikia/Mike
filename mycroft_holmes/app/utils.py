"""
App utilities
"""
from os import environ, path

from mycroft_holmes.config import Config


# pylint: disable=too-few-public-methods
class Cache:
    """
    This object is used as a static variables wrapper
    """
    CONFIG = None

    def __init__(self):
        pass


def get_config():
    """
    :rtype: mycroft_holmes.config.Config
    """
    if Cache.CONFIG is None:
        config_file = path.join(path.dirname(__file__), '../../test/fixtures', 'config.yaml')

        Cache.CONFIG = Config(
            config_file=config_file,
            env=environ
        )

    return Cache.CONFIG
