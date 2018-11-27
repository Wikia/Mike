"""
Set of unit test for Config class
"""
# https://docs.pytest.org/en/latest/assert.html#assertions-about-expected-exceptions
import pytest

from mycroft_holmes.config import Config, MycroftHolmesConfigError
from mycroft_holmes.sources import JiraSource

from . import get_fixtures_directory


def test_config_loads_correctly():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')

    assert config.get_raw()['name'] == 'The A-Team components'
    assert config.get_name() == 'The A-Team components'


def test_config_missing_file():
    with pytest.raises(MycroftHolmesConfigError) as exc_info:
        Config(config_file=get_fixtures_directory() + '/missing.yaml')

    print(exc_info)

    assert 'Failed to load' in str(exc_info.value)
    assert 'fixtures/missing.yaml' in str(exc_info.value)


def test_config_broken_file():
    with pytest.raises(MycroftHolmesConfigError) as exc_info:
        Config(config_file=get_fixtures_directory() + '/broken.yaml')

    print(exc_info)

    assert 'Failed to parse' in str(exc_info.value)
    assert 'fixtures/broken.yaml' in str(exc_info.value)
    assert 'line 2, column 7' in str(exc_info.value)


def test_config_variables_subst():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')
    assert config.get_raw()['sources'][0]['user'] == '${JIRA_USER}', 'Variable should be kept'

    config = Config(config_file=get_fixtures_directory() + '/config.yaml', env={
        'JIRA_USER': 'MrFoo'
    })
    assert config.get_raw()['sources'][0]['user'] == 'MrFoo', 'Variable should be replaced'


def test_config_get_sources():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')
    sources = config.get_sources()

    assert 'wikia/jira' in sources
    assert 'wikia/elastic' in sources
    assert 'wikia/tags-report' in sources

    assert sources['wikia/jira'] == {
        'name': 'wikia/jira',
        'kind': 'common/jira',
        'server': "${JIRA_URL}",
        'user': "${JIRA_USER}",
        'password': "${JIRA_PASSWORD}"
    }


def test_config_get_features():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')
    features = config.get_features()

    print(features)

    assert 'DynamicPageList' in features
    assert features['DynamicPageList'] == {
        'name': 'DynamicPageList',
        'url': 'http://docs.company.net/pages/DynamicPageList',
        'metrics': [
            {'name': 'jira/p2-tickets'},
            {'name': 'jira/p3-tickets'},
            {'name': 'tags-report/usage', 'weight': 0.1},
        ],
        'template': {
            'project': 'DynamicPageList',
            'tag': 'dpl'
        }
    }


def test_config_get_metrics():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')
    metrics = config.get_metrics()

    print(metrics)

    assert 'jira/p2-tickets' in metrics
    assert 'jira/p3-tickets' in metrics
    assert metrics['jira/p2-tickets'] == {
        'name': 'jira/p2-tickets',
        'source': 'wikia/jira',
        'query': "project = '{project}' AND Priority = 'P2' AND status = 'Open'",
        'label': '%d P2 tickets'
    }


def test_config_get_source_from_metric():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml', env={
        'JIRA_URL': 'https://foo.atlasian.net',
        'JIRA_USER': 'MrFoo',
        'JIRA_PASSWORD': '9bec73487c01653ad7830c25e4b1dc926d17e518',
    })
    source = config.get_source_from_metric({
        'name': 'jira/p2-tickets',
        'source': 'wikia/jira',
        'template': {
            'project': 'DynamicPageList',
            'tag': 'dpl'
        }
    })

    print(source)

    assert isinstance(source, JiraSource), 'get_source_from_metric should return an instance of JiraSource'
    assert source._server == 'https://foo.atlasian.net'
    assert source._basic_auth == ('MrFoo', '9bec73487c01653ad7830c25e4b1dc926d17e518')
