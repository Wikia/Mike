"""
Set of unit test for metrics storage
"""
from unittest import SkipTest

from os import environ

from mycroft_holmes.config import Config
from mycroft_holmes.metric import Metric
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


TIMESTAMP = '2019-03-02 20:22:24'


def test_storage():
    if environ.get('TEST_DATABASE') is None:
        raise SkipTest('TEST_DATABASE env variable needs to be set to run this test.')

    storage = MetricsStorage(config=ConfigForMetricsStorage(), use_slave=False)

    # clean up the storage
    cursor = storage.storage.cursor()
    cursor.execute('TRUNCATE TABLE features_metrics')

    # no data so far
    # assert storage.get_the_latest_timestamp() is None

    # push some metrics and later on try to get them
    storage.push('foo', {'score': 123, 'bar/metric': 42.458})
    storage.push('bar', {'score': 1, 'bar/metric': -3})
    storage.commit(timestamp=TIMESTAMP)

    storage.push('bar', {'score': 5, 'bar/metric': -4})
    storage.commit(timestamp=TIMESTAMP)

    assert storage.get(feature_id='foo', feature_metric='score') == 123
    assert storage.get(feature_id='foo', feature_metric='bar/metric') == 42.46, 'Storage keeps floats with scale of 2'

    assert storage.get(feature_id='bar', feature_metric='score') == 5, 'The most recent value should be taken'
    assert storage.get(feature_id='bar', feature_metric='bar/metric') == -4, 'Negative values are accepted'

    assert storage.get(feature_id='not_existing', feature_metric='bar/metric') is None, 'Not existing metric'

    # now check if we can get the metric value
    metric = Metric(feature_name='Bar', config=ConfigForMetricsStorage(), spec={'name': 'bar/metric'})
    assert metric.value == -4, 'Get the most recent value from the storage'
    assert isinstance(metric.value, int), 'The value is returned as an int'

    metric = Metric(feature_name='Foo', config=ConfigForMetricsStorage(), spec={'name': 'bar/metric'})
    assert metric.value == 42.46, 'Get the most recent value from the storage'
    assert isinstance(metric.value, float), 'The value is returned as a float'

    # check the latest timestamp
    assert storage.get_the_latest_timestamp() == TIMESTAMP
