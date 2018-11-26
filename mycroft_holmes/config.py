"""
Handles YAML config files
"""
import logging

from collections import OrderedDict

import yaml
from yaml.error import MarkedYAMLError

from .errors import MycroftHolmesError
from. utils import yaml_variables_subst


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

        # read from file
        try:
            with open(config_file, 'rt') as handler:
                raw = handler.read()
        except OSError as ex:
            # File not found
            raise MycroftHolmesConfigError('Failed to load "%s" config file: %s' %
                                           (config_file, repr(ex)))

        raw = yaml_variables_subst(raw, variables=env)

        # parse it
        try:
            self.data = yaml.safe_load(raw)

        except MarkedYAMLError as ex:
            # YAML syntax is incorrect
            raise MycroftHolmesConfigError('Failed to parse "%s" config file: %s (%s)' %
                                           (config_file, str(ex).strip(), str(ex.problem_mark)))

    def get_raw(self):
        """
        :rtype: dict
        """
        return self.data

    def get_name(self):
        """
        :rtype: str
        """
        return self.data['name']

    def get_sources(self):
        """
        Returns source name -> spec dictionary

        :rtype: OrderedDict
        """
        sources = OrderedDict()

        for spec in self.data['sources']:
            sources[spec['name']] = spec

        return sources

    def get_features(self):
        """
        :rtype: list[dict]
        """
