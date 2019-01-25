"""
Set of unit test for ConstSource class
"""
from mycroft_holmes.config import Config
from mycroft_holmes.metric import Metric
from mycroft_holmes.sources import ConstSource

from . import get_fixtures_directory


def test_fetch_value():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')

    metric = Metric(spec={
        'name': 'foo/bar',
        'source': 'common/const',
    }, feature_name='foo', config=config)

    print(metric)
    assert metric.get_source_name() == ConstSource.NAME
    assert metric.fetch_value() == 1
    assert metric.value == 1, 'We should not need to connect to database to get this'


def test_fetch_value_ignore_weight():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')

    metric = Metric(spec={
        'name': 'foo/weighted-bar',
        'source': 'common/const',
        'weight': 1000,
    }, feature_name='foo', config=config)

    print(metric)
    assert metric.get_weight() == 1000
    assert metric.fetch_value() == 1  # value should not be affected by metric's weight
