"""
App utilities
"""
import functools

from os import environ, path

from mycroft_holmes.config import Config


def memoize(func):
    """
    Memoization pattern implemented
    :type func
    :rtype func
    """
    # @see https://medium.com/@nkhaja/memoization-and-decorators-with-python-32f607439f84
    cache = func.cache = {}

    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        """
        :type args
        :type kwargs
        """
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return memoized_func


@memoize
def get_config():
    """
    :rtype: mycroft_holmes.config.Config
    """
    config_file = path.join(path.dirname(__file__), '../../test/fixtures', 'config.yaml')

    return Config(
        config_file=config_file,
        env=environ
    )


def get_feature_spec_by_id(config, feature_id):
    """
    :type config Config
    :type feature_id str
    :rtype: dict|None
    """
    for feature_name, spec in config.get_features().items():
        _id = config.get_feature_id(feature_name)

        if _id == feature_id:
            return spec

    return None
