"""
Set of unit test for Metric class
"""
import pytest

from mycroft_holmes.config import Config
from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.metric import Metric
from mycroft_holmes.sources import JiraSource
from mycroft_holmes.sources.base import SourceBase

from . import get_fixtures_directory


def test_metric():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml', env={
        'JIRA_URL': 'https://foo.atlasian.net',
        'JIRA_USER': 'MrFoo',
        'JIRA_PASSWORD': '9bec73487c01653ad7830c25e4b1dc926d17e518',
    })
    metric = Metric(spec={
        'name': 'jira/p2-tickets',
        'source': 'wikia/jira',
        'template': {
            'project': 'DynamicPageList',
            'tag': 'dpl'
        }
    }, feature_name='foo', config=config)

    print(metric)

    assert metric.get_name() == 'jira/p2-tickets'
    assert metric.get_source_name() == 'wikia/jira'
    assert metric.get_spec() == {
        'name': 'jira/p2-tickets',
        'source': 'wikia/jira',
        'template': {'project': 'DynamicPageList', 'tag': 'dpl'}
    }

    source = SourceBase.new_for_metric(metric=metric, config=config)

    print(source)

    assert isinstance(source, JiraSource), 'get_source_from_metric should return an instance of JiraSource'
    assert source._server == 'https://foo.atlasian.net'
    assert source._basic_auth == ('MrFoo', '9bec73487c01653ad7830c25e4b1dc926d17e518')


def test_metric_missing_source_handling():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')

    metric = Metric(spec={
        'name': 'foo/var',
        'source': 'foo/missing-source'
    }, feature_name='foo', config=config)

    with pytest.raises(MycroftSourceError):
        metric.fetch_value()


def test_metric_get_weight():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')

    metric = Metric(spec={
        'name': 'foo/var',
        'weight': 2.5
    }, feature_name='foo', config=config)

    print(metric)
    assert metric.get_weight() == 2.5

    metric = Metric(spec={
        'name': 'foo/var'
    }, feature_name='foo', config=config)

    print(metric)
    assert metric.get_weight() == 1  # a default value
