"""
This script should be run periodically to collect metrics
that are used to calculate scores for features.
"""
import logging
from collections import OrderedDict

from mycroft_holmes.app.utils import get_config
from mycroft_holmes.config import Config
from mycroft_holmes.errors import MycroftHolmesError
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.storage import MetricsStorage


def get_metrics_for_feature(feature_name, config):
    """
    :type feature_name str
    :type config Config
    :rtype: OrderedDict
    """
    logger = logging.getLogger('get_metrics_for_feature')
    logger.info('Collecting metrics for "%s" feature', feature_name)

    result = OrderedDict(score=0)

    feature_score = 0

    for metric in config.get_metrics_for_feature(feature_name):
        metric_name = metric.get_name()

        try:
            metric_value = metric.fetch_value()

            result[metric_name] = metric_value
            feature_score += metric_value * metric.get_weight()
        except MycroftHolmesError:
            logger.warning('Failed to fetch value for "%s"', metric_name, exc_info=True)

    result['score'] = feature_score
    logger.info('Score for "%s" feature: %d', feature_name, feature_score)

    return result


def main():
    """
    Script entry point
    """
    logger = logging.getLogger('collect_metrics')

    # list available sources
    logger.info('Available sources: %s', SourceBase.get_sources_names())

    # read config file provided by MIKE_CONFIG
    config = get_config()

    # list features and metrics
    logger.info('Configured metrics: %s', list(config.get_metrics().keys()))
    logger.info('Features: %s', list(config.get_features().keys()))

    # set up the metrics storage (and connect to master database)
    storage = MetricsStorage(config=config, use_slave=False)

    # print(storage.get('ckeditor', 'score')); exit(1)

    # fetch metrics values for eac feature and calculate their score
    for _, feature in config.get_features().items():
        try:
            feature_id = Config.get_feature_id(feature['name'])
            feature_metrics = get_metrics_for_feature(feature['name'], config)

            storage.push(feature_id, feature_metrics)

        except MycroftHolmesError as ex:
            logger.error('Failed to get metrics values', exc_info=True)

            print('\nWe failed to generate metrics values:\n\t%s\n' % repr(ex))
            exit(1)

    storage.commit()
    logger.info('Done')
