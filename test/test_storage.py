"""
Set of unit test for metrics storage
"""
from unittest import SkipTest

from os import environ

from mycroft_holmes.config import Config
from mycroft_holmes.storage import MetricsStorage


class ConfigForMetricsStorage(Config):
    def __init__(self):
        self.data = {
            'storage': {
                'engine': 'mysql',
                'host': '127.0.0.1',
                'database': environ.get('TEST_DATABASE'),
                # TravisCI default values
                'user': environ.get('TEST_DATABASE_USER', 'root'),
                'password': environ.get('TEST_DATABASE_PASSWORD', ''),
            }
        }


def test_storage():
    if environ.get('TEST_DATABASE') is None:
        raise SkipTest('TEST_DATABASE env variable needs to be set to run this test.')

    storage = MetricsStorage(config=ConfigForMetricsStorage())

    # push some metrics and later on try to get them
    storage.push('foo', {'score': 123, 'bar/metric': 42.4})
    storage.push('bar', {'score': 1, 'bar/metric': -3})
    storage.commit()

    assert storage.get(feature_id='foo', feature_metric='score') == 123
    assert storage.get(feature_id='foo', feature_metric='bar/metric') == 42, 'Storage keeps integers'
    assert storage.get(feature_id='bar', feature_metric='score') == 1
    assert storage.get(feature_id='bar', feature_metric='bar/metric') == -3, 'Negative values are accepted'

    assert storage.get(feature_id='not_existing', feature_metric='bar/metric') is None, 'Not existing metric'
