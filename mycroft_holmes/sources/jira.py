"""
JiraSource class
"""
from urllib.parse import quote
from jira.client import JIRA

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.utils import format_query

from .base import SourceBase


class JiraSource(SourceBase):
    """
    Returns a number of Jira ticket matching given JQL query.

    #### `sources` config

    ```yaml
    sources:
      - name: foo/jira
        kind: common/jira
        server: "https://foo-company.attlasian.net"
        user: "${JIRA_USER}"  # variables substitution
        password: "${JIRA_PASSWORD}" # Jira API key
    ```

    Password is an API token that you can generate:
    https://confluence.atlassian.com/cloud/api-tokens-938839638.html.

    #### `metrics` config

    ```yaml
        metrics:
          # Jira
          - name: jira/p3-tickets
            source: foo/jira  # defined above
            query: "project = '{project}' AND Priority = 'P3' AND status = 'Open'"
            label: "%d P3 tickets"
    ```

    #### `features` config

    ```yaml
        features:
          - name: FooBar
            template:
              - project: "Foo"  # this will be used in template string
            metrics:
              -  name: jira/p3-tickets
    ```
    """

    NAME = 'common/jira'

    def __init__(self, server, user, password, client=None):
        """
        :type server str
        :type user str
        :type password str
        :type client obj
        """
        super(JiraSource, self).__init__()

        self._server = server
        self._basic_auth = (user, password)

        self._client = client or None

    @property
    def client(self):
        """
        Connect to Jira lazily

        :rtype: JIRA
        """
        if not self._client:
            self.logger.info('Setting up Jira client for %s (auth: %s:***)',
                             self._server, self._basic_auth[0])
            self._client = JIRA(server=self._server, basic_auth=self._basic_auth)

            self.logger.info('Connected with Jira server: %s', self._client.server_info())

        return self._client

    @staticmethod
    def _get_jql(**kwargs):
        """
        :rtype: str
        """
        query = kwargs.get('query')
        assert isinstance(query, str), '"query" parameter needs to be provided'

        jql = format_query(query, kwargs.get('template'))
        return jql

    def get_value(self, **kwargs):
        """
        :raise: MycroftSourceError
        :rtype: int
        """
        jql = self._get_jql(**kwargs)
        self.logger.info('JQL query: "%s"', jql)

        try:
            tickets = self.client.search_issues(jql_str=jql)
        except Exception as ex:
            raise MycroftSourceError('Failed to get metric value: %s' % repr(ex))

        return len(tickets)

    def get_more_link(self, **kwargs):
        """
        Returns a tuple with link name and URL that can give you more details
        for this metric, e.g. link to a JIRA dashboard

        :rtype: tuple[str, str]|None
        """
        jql = self._get_jql(**kwargs)

        return (
            'View tickets',
            # https://foo.atlassian.net/issues/?jql=...
            '{server}/issues/?jql={jql}'.format(
                server=self._server,
                jql=quote(jql)
            )
        )
