"""
Set of unit test for JiraSource class
"""
from pytest import raises

from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import JiraSource


class JiraMockedClient:
    """
    Mocked Jira client class returning provided number of tickets
    """
    def __init__(self, tickets_count):
        self.tickets = ['ticket_%d' % ticket for ticket in range(1, tickets_count+1)]
        self.last_query = None

    def search_issues(self, jql_str):
        self.last_query = jql_str
        return self.tickets

    def get_last_query(self):
        """
        :rtype: str
        """
        return self.last_query


def test_is_source_present():
    assert JiraSource.NAME in SourceBase.get_sources_names()


def test_source_get_value():
    source = SourceBase.new_from_name(
        name=JiraSource.NAME,
        args={
            'server': 'https://foo-company.attlasian.net',
            'user': 'MrFoo',
            'password': 'foobar',
            'client': JiraMockedClient(tickets_count=5)
        }
    )

    print(source)
    assert isinstance(source, JiraSource)
    assert isinstance(source.client, JiraMockedClient), 'client should be mocked'

    # AssertionError: "query" parameter needs to be provided
    with raises(AssertionError):
        source.get_value()

    assert source.get_value(query='Project = "{project}"', template={'project': 'Foo'}) == 5
    assert source.client.get_last_query() == 'Project = "Foo"'
