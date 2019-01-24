"""
Mysql class
"""
from mysql import connector

from mycroft_holmes.errors import MycroftSourceError
from .base import SourceBase


class MysqlSource(SourceBase):
    """
    Returns a number result for a given SQL query.

    #### `sources` config

    ```yaml
    sources:
      - name: foo/mysql
        kind: common/mysql
        host: "${DATABASE_HOST}"
        database: "app_database_name"
        user: "${DATABASE_USER}"
        password: "${DATABASE_PASSWORD}"
    ```

    #### `metrics` config

    ```yaml
        metrics:
          # Get some stats
          - name: users/count
            source: foo/mysql
            query: "SELECT count(*) FROM users WHERE user_group = %(user_group)s"
            label: "{user_group} group members: %d"
    ```

    Please note that only the first column from the first row in the results set will be taken.

    #### `features` config

    ```yaml
        features:
          - name: FooBar
            template:
              - user_group: "Admin"  # this will be used in query defined above
            metrics:
              -  name: users/count
    ```
    """

    NAME = 'common/mysql'

    # pylint: disable=too-many-arguments
    def __init__(self, host, database, user, password, client=None):
        """
        :type host str
        :type database str
        :type user str
        :type password str
        :type client obj
        """
        super(MysqlSource, self).__init__()

        self._connection_params = dict(
            host=host,
            database=database,
            user=user,
            password=password,
        )

        self._client = client or None

    @property
    def client(self):
        """
        Connect to MySQL lazilly

        :rtype: mysql.connector.connection.MySQLConnection
        """
        if not self._client:
            self.logger.info('Connecting to MySQL running at "%s"...',
                             self._connection_params['host'])

            # https://dev.mysql.com/doc/connector-python
            self._client = connector.connect(**self._connection_params)

        return self._client

    def get_value(self, **kwargs):
        """
        :raise: MycroftSourceError
        :rtype: int
        """
        query = kwargs.get('query')
        assert isinstance(query, str), '"query" parameter needs to be provided'

        template = kwargs.get('template')

        try:
            cursor = self.client.cursor()
            cursor.execute(query, template)

            value = cursor.fetchone()[0]

            self.logger.info('SQL: %s', cursor.statement)

            return value
        except Exception as ex:
            raise MycroftSourceError('Failed to get metric value: %s' % repr(ex))
