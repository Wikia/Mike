"""
Set of unit test for GoogleAnalyticsSource class
"""
from pytest import raises

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import GoogleAnalyticsSource


class ReportCalledError(Exception):
    """
    This is raised by reports() method of MockedClient
    """
    pass


class MockedClient:
    """
    Mocked Google API client class returning provided number of tickets
    """
    def reports(self):
        raise ReportCalledError('reports() method should not be called')  # TODO


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

    # these calls should make it into reports() method of GA client
    with raises(MycroftSourceError):
        source.get_value(metric='foo')

    # client check
    with raises(MycroftSourceError):
        assert source.get_value(metric='foo', filters='bar') == 5  # TODO


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
