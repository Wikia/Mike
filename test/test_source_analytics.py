"""
Set of unit test for GoogleAnalyticsSource class
"""
from pytest import raises

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import GoogleAnalyticsSource


class MockedGoogleAnalyticsSource(GoogleAnalyticsSource):
    """
    This class is used to mock values returned by Google Analytics API
    """
    def __init__(self, mocked_value):
        """
        :type mocked_value float
        """
        super(MockedGoogleAnalyticsSource, self).__init__('', 0)
        self.mocked_value = mocked_value
        self.last_query = None

    def _query(self, **kwargs):
        """
        :rtype: float
        """
        self.last_query = kwargs

        # [{'metrics': [{'values': ['270634']}], 'dimensions': ['20181213']}]
        return {
            'reports': [{
                'data': {
                    'rows': [
                        {
                            'metrics': [{'values': [str(self.mocked_value)]}],
                            'dimensions': ['20181213'],
                        }
                    ]
                }
            }]
        }


class MockedClient:
    """
    Mocked Google API client class returning provided number of tickets
    """
    def reports(self):
        raise Exception('reports() method should not be called')  # TODO


def get_source_with_mocked_client(mocked_client, credentials='{}'):
    """
    :type mocked_client MockedClient|None
    :type credentials str
    :rtype: GoogleAnalyticsSource
    """
    return SourceBase.new_from_name(
        source_name=GoogleAnalyticsSource.NAME,
        args={
            'credentials': credentials,
            'view_id': 123,
            'client': mocked_client
        }
    )


def test_is_source_present():
    assert GoogleAnalyticsSource.NAME in SourceBase.get_sources_names()


def test_source_validation():
    source = get_source_with_mocked_client(MockedClient())

    print(source)
    assert isinstance(source, GoogleAnalyticsSource)
    assert isinstance(source.client, MockedClient), 'client should be mocked'

    # arguments validation
    with raises(AssertionError) as exc_info:
        source.get_value()
    assert str(exc_info).endswith('AssertionError: "metric" parameter needs to be provided')


def test_mocked_source():
    source = MockedGoogleAnalyticsSource(5)
    assert source.get_value(metric='foo') == 5
    assert source.last_query == \
        {'dimension': 'ga:date', 'end_date': '1daysAgo', 'filters': '', 'metric': 'foo', 'start_date': '1daysAgo'}

    source = MockedGoogleAnalyticsSource(42)
    value = source.get_value(metric='foo', filters='bar')

    assert value == 42
    assert isinstance(value, float), 'Returned value is always a float'
    assert source.last_query == \
        {'dimension': 'ga:date', 'end_date': '1daysAgo', 'filters': 'bar', 'metric': 'foo', 'start_date': '1daysAgo'}

    # float value
    source = MockedGoogleAnalyticsSource(5.7)
    assert source.get_value(metric='foo', filters='bar:123') == 5.7, 'float value is kept'
    assert source.last_query == \
        {'dimension': 'ga:date', 'end_date': '1daysAgo', 'filters': 'bar:123', 'metric': 'foo', 'start_date': '1daysAgo'}


def test_client_exception_handling():
    source = get_source_with_mocked_client(MockedClient())

    # AssertionError: "query" parameter needs to be provided
    with raises(MycroftSourceError):
        source.get_value(metric='foo', filters='bar')


def test_client_credentials_validation():
    # empty credentials JSON
    source = get_source_with_mocked_client(mocked_client=None, credentials='{}')

    with raises(AssertionError) as exc_info:
        _ = source.client

    assert str(exc_info).endswith("'client_email' entry not found in service account JSON")

    # broken JSON
    source = get_source_with_mocked_client(mocked_client=None, credentials='{foobar}')

    with raises(MycroftSourceError) as exc_info:
        _ = source.client

    assert str(exc_info).endswith("Failed to load Google's service account JSON file")
