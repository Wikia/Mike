"""
LogstashSource class
"""
from elasticsearch_query import ElasticsearchQuery

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.utils import format_query

from .base import SourceBase


class LogstashSource(SourceBase):
    """
    Returns a number of entries matching a given elasticsearch query.

    We assume that elasticsearch indices follow logstash naming convention
    and are sharded by date, e.g. `logstash-access-log-2017.05.09`

    #### `sources` config

    ```yaml
    sources:
      - name: foo/logstash
        kind: common/logstash
        host: ${ELASTIC_HOST}
        index: logstash-access-log  # will query this index (e.g. logstash-access-log)
        period: 3600  # in seconds, query entries from the last hour (defaults to 86400 s)
    ```

    #### `metrics` config

    ```yaml
        metrics:
          - name: logstash/get-requests-access-log
            source: foo/logstash  # defined above
            query: "request: 'GET' AND url: '{url}'"
            label: "%d GET request"
    ```

    #### `features` config

    ```yaml
        features:
          - name: FooBar
            template:
              - url: "/foo"  # this will be used in template string
            metrics:
              -  name: logstash/get-requests-access-log
    ```
    """

    NAME = 'common/logstash'

    def __init__(self, host, index, period=86400, client=None):
        """
        :type host str
        :type index str
        :type period int
        :type client obj
        """
        super(LogstashSource, self).__init__()

        self._server = host
        self._index = index
        self._period = period
        self._client = client or None

    @property
    def client(self):
        """
        Connect to elasticsearch lazily

        :rtype: ElasticsearchQuery
        """
        if not self._client:
            self.logger.info('Setting up elasticsearch client for %s host ("%s" index)',
                             self._server, self._index)
            self._client = ElasticsearchQuery(
                es_host=self._server, period=self._period, index_prefix=self._index)

        return self._client

    def get_value(self, **kwargs):
        """
        :raise: MycroftSourceError
        :rtype: int
        """
        query = kwargs.get('query')
        assert isinstance(query, str), '"query" parameter needs to be provided'

        query = format_query(query, kwargs.get('template'))
        self.logger.info('Query: "%s"', query)

        try:
            cnt = self.client.count(query=query)
        except Exception as ex:
            raise MycroftSourceError('Failed to get metric value: %s' % repr(ex))

        return cnt
