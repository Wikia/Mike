"""
Set of unit test for JiraSource class
"""
from pytest import raises

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import JiraSource


class JiraMockedClient:
    """
    Mocked Jira client class returning provided number of tickets
    """
    def __init__(self, tickets_count, raise_exc=False):
        self.tickets = ['ticket_%d' % ticket for ticket in range(1, tickets_count+1)]
        self.last_query = None
        self.raise_exc = raise_exc

    def search_issues(self, jql_str):
        if self.raise_exc:
            raise Exception('Mocked exception thrown')

        self.last_query = jql_str
        return self.tickets

    def get_last_query(self):
        """
        :rtype: str
        """
        return self.last_query


def get_source_with_mocked_client(mocked_client):
    """
    :type mocked_client JiraMockedClient
    :rtype: JiraSource
    """
    return SourceBase.new_from_name(
        source_name=JiraSource.NAME,
        args={
            'server': 'https://foo-company.attlasian.net',
            'user': 'MrFoo',
            'password': 'foobar',
            'client': mocked_client
        }
    )


def test_is_source_present():
    assert JiraSource.NAME in SourceBase.get_sources_names()


def test_source_get_value():
    source = get_source_with_mocked_client(JiraMockedClient(tickets_count=5))

    print(source)
    assert isinstance(source, JiraSource)
    assert isinstance(source.client, JiraMockedClient), 'client should be mocked'

    # AssertionError: "query" parameter needs to be provided
    with raises(AssertionError):
        source.get_value()

    assert source.get_value(query='Project = "{project}"', template={'project': 'Foo'}) == 5
    assert source.client.get_last_query() == 'Project = "Foo"'


def test_client_exception_handling():
    source = get_source_with_mocked_client(JiraMockedClient(tickets_count=5, raise_exc=True))

    # AssertionError: "query" parameter needs to be provided
    with raises(MycroftSourceError):
        source.get_value(query='Foo')
