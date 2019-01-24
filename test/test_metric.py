"""
Set of unit test for Metric class
"""
import pytest

from mycroft_holmes.config import Config
from mycroft_holmes.errors import MycroftSourceError, MycroftMetricError
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


def test_metric_empty_source_handling():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')

    metric = Metric(spec={
        'name': 'foo/var',
    }, feature_name='foo', config=config)

    with pytest.raises(MycroftMetricError):
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


def test_metric_get_label():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')
    metrics = config.get_metrics_for_feature(feature_name='VisualEditor')

    print(metrics)

    # jira
    metrics[0].set_value(12)
    assert metrics[0].get_label() == 'P2 tickets'
    assert metrics[0].get_label_with_value() == '12 P2 tickets'
    assert metrics[0].get_label_with_value() == '12 P2 tickets'
    assert metrics[0].get_more_link() == (
        'View tickets',
        'https://foo.atlasian.net/issues/?jql=component%20%3D%20%27Visual%20Editor'
        '%27%20AND%20Priority%20%3D%20%27Severe%20-%20fix%20in%2048h%20%28P2%29%27%20AND%20status%20%3D%20%27Open%27'
    )

    # analytics
    metrics[2].set_value(34511)
    assert metrics[2].get_label() == 'Edits published daily'
    assert metrics[2].get_label_with_value() == 'Edits published daily: 34.5k'
    assert metrics[2].get_more_link() is None


def test_format_value():
    assert Metric.format_value(1) == '1'
    assert Metric.format_value(12) == '12'
    assert Metric.format_value(123) == '123'
    assert Metric.format_value(1213) == '1.21k'
    assert Metric.format_value(22213) == '22.2k'
    assert Metric.format_value(222130) == '222k'
    assert Metric.format_value(222930) == '223k'


def test_empty_metric():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')

    metric = Metric(spec={
        'name': 'foo/var',
    }, feature_name='foo', config=config)

    # the value is empty, storage read seems to fail for it
    metric.set_value(None)

    print(metric)

    assert metric.get_label() is None
    assert metric.value is None
    assert metric.get_formatted_value() is None
    assert metric.get_label_with_value() is None
    assert metric.get_more_link() is None
