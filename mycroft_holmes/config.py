"""
Handles YAML config files
"""
import logging

from collections import OrderedDict

import yaml
from yaml.error import MarkedYAMLError

from .errors import MycroftHolmesError
from .sources.base import SourceBase
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
        self.sources_cache = dict()

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

    def get_metrics(self):
        """
        Returns metric name -> spec dictionary

        :rtype: OrderedDict
        """
        metrics = OrderedDict()

        for spec in self.data['metrics']:
            metrics[spec['name']] = spec

        return metrics

    def get_features(self):
        """
        Returns feature name -> spec dictionary

        :rtype: OrderedDict
        """
        features = OrderedDict()

        # apply common part for each feature
        common_metrics = self.get_raw().get('common', {}).get('metrics')

        for spec in self.data['features']:
            spec = spec.copy()

            if common_metrics:
                # merge metrics - common ones + spec-specific ones
                metrics = common_metrics.copy()
                metrics += spec.get('metrics', [])

                spec['metrics'] = metrics

            features[spec['name']] = spec

        return features

    def get_source_from_metric(self, metric_spec):
        """
        Return an instance of BaseSource object that matches provided metric spec
        from "features" YAML config section.

        Cache by metric's spec "source" field

        :type metric_spec dict
        :rtype: SourceBase
        """
        source_name = metric_spec['source']

        if source_name in self.sources_cache:
            return self.sources_cache.get(source_name)

        # get an entry from "source" config file section that matches given metric "source"
        source_spec = self.get_sources().get(source_name).copy()
        source_kind = source_spec['kind']

        del source_spec['name']
        del source_spec['kind']

        self.logger.info('Setting up "%s" source of "%s" kind (args: %s)',
                         metric_spec['source'], source_kind, list(source_spec.keys()))

        source = SourceBase.new_from_name(source_kind, args=source_spec)

        # cache it
        self.sources_cache[source_name] = source

        return source
