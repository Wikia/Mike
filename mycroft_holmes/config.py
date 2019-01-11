"""
Handles YAML config files
"""
import logging
import re

from collections import OrderedDict

import yaml
from yaml.error import MarkedYAMLError

from .errors import MycroftHolmesError
from .metric import Metric
from .utils import yaml_variables_subst


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

        for spec in self.data.get('sources', []):
            sources[spec['name']] = spec

        return sources

    def get_metrics(self):
        """
        Returns metric name -> spec dictionary

        :rtype: OrderedDict
        """
        metrics = OrderedDict()

        for spec in self.data.get('metrics', []):
            metrics[spec['name']] = spec

        return metrics

    @staticmethod
    def get_feature_id(feature_name):
        """
        Given feature name returns a string that is suitable for metrics storage

        E.g. "Message Wall" -> message_wall

        :type feature_name str
        :rtype: str
        """
        return re.sub(r'[^a-z0-9]+', '_', feature_name.lower()).strip('_')

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

    def get_metrics_for_feature(self, feature_name):
        """
        Get metrics for a given feature. Each of returned items can then be passed to
        get_source_from_metric method to get an instance of source object

        :type feature_name str
        :rtype: list[Metric]
        """
        feature = self.get_features().get(feature_name)

        if feature is None:
            return []

        available_metrics = self.get_metrics()
        metrics = []

        for metric in feature.get('metrics', []):
            # create a fresh copy of metric spec
            spec = available_metrics.get(metric['name']).copy()

            # extend it with feature-wide template variables
            if feature.get('template'):
                spec['template'] = feature.get('template')

            # pass per-metric weight
            if metric.get('weight'):
                spec['weight'] = metric.get('weight')

            metrics.append(
                Metric(spec=spec, feature_name=feature_name, config=self)
            )

        return metrics
