"""
Handles YAML config files
"""
import logging

import yaml
from yaml.error import MarkedYAMLError

from .errors import MycroftHolmesError


class MycroftHolmesConfigError(MycroftHolmesError):
    """
    An exception to be thrown by Config class
    """


class Config:
    """
    Class that handled reading and parsing YAML config files

    Environment variables can be provided to perform variables substitution
    """
    def __init__(self, config_file, env=None):
        """
        :type config_file str
        :type env dict
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Reading config file "%s"', config_file)

        if env:
            self.logger.info('Got variables to substitute in config file: %s',
                             ', '.join(env.keys()))

        try:
            with open(config_file, 'rt') as handler:
                data = yaml.load(handler)
        except OSError as ex:
            # File not found
            raise MycroftHolmesConfigError('Failed to load "%s" config file: %s' %
                                           (config_file, repr(ex)))
        except MarkedYAMLError as ex:
            # YAML syntax is incorrect
            raise MycroftHolmesConfigError('Failed to parse "%s" config file: %s (%s)' %
                                           (config_file, str(ex).strip(), str(ex.problem_mark)))

        print(data)

    def get_sources(self):
        """
        :rtype: list[dict]
        """

    def get_features(self):
        """
        :rtype: list[dict]
        """
