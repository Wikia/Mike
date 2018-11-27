"""
This script should be run periodically to collect metrics
that are used to calculate scores for features.
"""
import logging
from collections import OrderedDict
from sys import argv

from mycroft_holmes.config import Config
from mycroft_holmes.sources.base import SourceBase


SOURCES_CACHE = dict()


def get_source_from_metric(metric_spec, config):
    """
    Cache by metric's spec "source" field

    :type metric_spec dict
    :type config Config
    :rtype: SourceBase
    """
    source_name = metric_spec['source']

    if source_name in SOURCES_CACHE:
        return SOURCES_CACHE.get(source_name)

    # get an entry from "source" config file section that matches given metric "source"
    source_spec = config.get_sources().get(source_name).copy()
    source_kind = source_spec['kind']

    logger = logging.getLogger('get_source')

    del source_spec['name']
    del source_spec['kind']

    logger.info('Setting up "%s" source of "%s" kind (args: %s)',
                metric_spec['source'], source_kind, list(source_spec.keys()))

    source = SourceBase.new_from_name(source_kind, args=source_spec)

    # cache it
    SOURCES_CACHE[source_name] = source
    return source


def get_metrics_for_feature(feature, config):
    """
    :type feature dict
    :type config Config
    :rtype: OrderedDict
    """
    logger = logging.getLogger('get_metrics_for_feature')
    logger.info('Collecting metrics for "%s" feature', feature['name'])

    result = OrderedDict()

    available_metrics = config.get_metrics()

    for metric in feature.get('metrics', []):
        # build metric spec
        metric_spec = available_metrics.get(metric['name']).copy()
        metric_spec['template'] = feature.get('template')

        logger.debug('%s: %s', metric['name'], metric_spec)

        if metric_spec.get('source') is None:
            logger.warning('"%s" has no source specified, skipping!', metric['name'])
            continue

        # build source spec and set it up
        source = get_source_from_metric(metric_spec, config)
        logger.info('Source: %s', source)

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
    config = Config(config_file=argv[1])

    # list features and metrics
    logger.info('Configured metrics: %s', list(config.get_metrics().keys()))
    logger.info('Features: %s', list(config.get_features().keys()))

    # fetch metrics values for eac feature and calculate their score
    for _, feature in config.get_features().items():
        feature_metrics = get_metrics_for_feature(feature, config)
        logger.info('Collected metrics: %s', feature_metrics)

    logger.info('Done')
