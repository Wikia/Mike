"""
Set of unit test for LogstashSource class
"""
from pytest import raises

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import LogstashSource


class MockedClient:
    """
    Mocked Elasticsearch client class returning provided number of tickets
    """
    def __init__(self, cnt, raise_exc=False):
        self.cnt = cnt
        self.raise_exc = raise_exc

    def count(self, query):
        if self.raise_exc:
            raise Exception('Mocked exception thrown')

        return self.cnt


def get_source_with_mocked_client(mocked_client):
    """
    :type mocked_client JiraMockedClient
    :rtype: JiraSource
    """
    return SourceBase.new_from_name(
        source_name=LogstashSource.NAME,
        args={
            'host': 'es-logs.prod',
            'index': 'logstash-app',
            'client': mocked_client
        }
    )


def test_is_source_present():
    assert LogstashSource.NAME in SourceBase.get_sources_names()


def test_source_get_value():
    source = get_source_with_mocked_client(MockedClient(cnt=5))

    print(source)
    assert isinstance(source, LogstashSource)
    assert isinstance(source.client, MockedClient), 'client should be mocked'

    # AssertionError: "query" parameter needs to be provided
    with raises(AssertionError):
        source.get_value()

    assert source.get_value(query='foo') == 5


def test_client_exception_handling():
    source = get_source_with_mocked_client(MockedClient(cnt=5, raise_exc=True))

    # AssertionError: "query" parameter needs to be provided
    with raises(MycroftSourceError):
        source.get_value(query='Foo')
