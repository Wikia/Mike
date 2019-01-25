"""
Set of unit test for Config class
"""
# https://docs.pytest.org/en/latest/assert.html#assertions-about-expected-exceptions
import pytest

from mycroft_holmes.config import Config, MycroftHolmesConfigError

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
    assert 'wikia/analytics' in sources

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

    assert len(features) == 4

    assert 'DynamicPageList' in features
    assert features['DynamicPageList'] == {
        'name': 'DynamicPageList',
        'url': 'http://docs.company.net/pages/DynamicPageList',
        'repo': 'https://github.com/Wikia/app/tree/dev/extensions/DynamicPageList',
        'metrics': [
            {'name': 'jira/p2-tickets', 'weight': 2},
            {'name': 'jira/p3-tickets'},
            {'name': 'tags-report/usage', 'weight': 0.1},
        ],
        'template': {
            'component': 'DynamicPageList',
            'tag': 'dpl'
        }
    }

    assert 'CKEditor' in features
    assert features['CKEditor'] == {
        'name': 'CKEditor',
        'url': 'http://docs.company.net/pages/CKEditor',
        'repo': 'https://github.com/Wikia/app/tree/dev/extensions/wikia/RTE',
        'metrics': [
            {'name': 'jira/p2-tickets', 'weight': 2},
            {'name': 'jira/p3-tickets'},
            {'name': 'analytics/events'},
        ],
        'template': {
            'component': 'CK Editor (RTE)',
            'ga_filter': 'ga:eventCategory==editor-ck;ga:eventAction==submit;ga:eventLabel==publish',
            'ga_label': 'Edits published daily',
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
        'query': "component = '{component}' AND Priority = 'Severe - fix in 48h (P2)' AND status = 'Open'",
        'label': '%d P2 tickets'
    }

    assert 'analytics/events' in metrics
    assert metrics['analytics/events'] == {
        'name': 'analytics/events',
        'source': 'wikia/analytics',
        'metric': 'ga:totalEvents',
        'label': '{ga_label}: %d',
        'filters': '{ga_filter}'
    }


def test_config_get_metrics_specs_for_feature():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')

    assert config.get_metrics_for_feature(feature_name='foobar') == []

    metrics_specs = config.get_metrics_for_feature(feature_name='DynamicPageList')
    print(metrics_specs)

    assert len(metrics_specs) == 3

    assert metrics_specs[0].get_spec() == {
        'query': "component = '{component}' AND Priority = 'Severe - fix in 48h (P2)' AND status = 'Open'",
        'source': 'wikia/jira',
        'name': 'jira/p2-tickets',
        'label': '%d P2 tickets',
        'template': {'component': 'DynamicPageList', 'tag': 'dpl'},
        'weight': 2
    }

    assert metrics_specs[1].get_spec() == {
        'query': "component = '{component}' AND Priority = 'Major - fix in 28 days (P3)' AND status = 'Open'",
        'source': 'wikia/jira',
        'name': 'jira/p3-tickets',
        'label': '%d P3 tickets',
        'template': {'component': 'DynamicPageList', 'tag': 'dpl'}
    }


def test_config_get_metrics_for_feature_const():
    config = Config(config_file=get_fixtures_directory() + '/const.yaml')

    metrics = config.get_metrics_for_feature('Foo Bar')

    print(metrics)
    assert len(metrics) == 2

    assert metrics[0].get_source_name() == 'common/const'
    assert metrics[0].get_weight() == 42

    assert metrics[1].get_source_name() == 'common/const'
    assert metrics[1].get_weight() == 66


def test_example_config():
    config = Config(config_file=get_fixtures_directory() + '/../../example.yaml')
    metrics = config.get_metrics_for_feature('Foo Bar')

    assert len(config.get_features()) == 1

    print(metrics)
    assert len(metrics) == 1

    assert metrics[0].get_source_name() == 'common/const'
    assert metrics[0].get_weight() == 700

    # can we handle empty entries in the config?
    assert len(config.get_metrics()) == 0
    assert len(config.get_sources()) == 0
