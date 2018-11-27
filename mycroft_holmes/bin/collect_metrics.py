"""
This script should be run periodically to collect metrics
that are used to calculate scores for features.
"""
import logging
from collections import OrderedDict
from os import environ
from sys import argv

from mycroft_holmes.config import Config
from mycroft_holmes.errors import MycroftHolmesError
from mycroft_holmes.sources.base import SourceBase


def get_metrics_for_feature(feature_name, config):
    """
    :type feature_name str
    :type config Config
    :rtype: OrderedDict
    """
    logger = logging.getLogger('get_metrics_for_feature')
    logger.info('Collecting metrics for "%s" feature', feature_name)

    result = OrderedDict()

    for metric_spec in config.get_metrics_specs_for_feature(feature_name):
        logger.debug('Metric: %s', metric_spec)

        if metric_spec.get('source') is None:
            logger.warning('"%s" has no source specified, skipping!', metric_spec['name'])
            continue

        # build source spec and set it up
        source = config.get_source_from_metric_spec(metric_spec)
        logger.debug('Source: %s', source)

        result[metric_spec['name']] = source.get_value(**metric_spec)

    return result


def main():
    """
    Script entry point
    """
    logger = logging.getLogger('collect_metrics')
    logger.info('argv: %s', argv)

    # list available sources
    logger.info('Available sources: %s', SourceBase.get_sources_names())

    # read provided config file
    config = Config(config_file=argv[1], env=environ)

    # list features and metrics
    logger.info('Configured metrics: %s', list(config.get_metrics().keys()))
    logger.info('Features: %s', list(config.get_features().keys()))

    # fetch metrics values for eac feature and calculate their score
    for _, feature in config.get_features().items():
        try:
            feature_metrics = get_metrics_for_feature(feature['name'], config)
            logger.info('Collected metrics: %s', feature_metrics)
        except MycroftHolmesError as ex:
            logger.error('Failed to get metrics values', exc_info=True)

            print('\nWe failed to generate metrics values:\n\t%s\n' % repr(ex))
            exit(1)

    logger.info('Done')
