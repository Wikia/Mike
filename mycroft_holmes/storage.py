"""
Handles metrics storage
"""
import logging
from mysql import connector
from mysql.connector.errors import Error as MySqlError


class MetricsStorage:
    """
    MySQL storage
    """
    CONNECTIONS_CACHE = dict()

    def __init__(self, config, use_slave=True):
        """
        Connect to storage database.
        Use slave by default (use "host_slave" config entry if provided)

        :type config mycroft_holmes.config.Config
        :type use_slave bool
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self._storage = None
        self.data = dict()

        # read the config
        self.config = config.get_raw()['storage']

        assert self.config['engine'] == 'mysql', 'Only "mysql" storage is currently supported'

        # pick a host
        if use_slave and 'host_slave' in self.config:
            self.config['host'] = self.config['host_slave']

    @property
    def storage(self):
        """
        Lazy-connect to a storage and return a handler, i.e. MySQL cursor

        :rtype: mysql.connector.connection.MySQLConnection
        """
        storage_host = self.config['host']

        # use cached connection
        if storage_host in self.CONNECTIONS_CACHE:
            # https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-ping.html
            self.CONNECTIONS_CACHE[storage_host].ping(reconnect=True, attempts=1, delay=0)

            return self.CONNECTIONS_CACHE[storage_host]

        if not self._storage:
            self.logger.info('Connecting to MySQL running at "%s"...', storage_host)

            # https://dev.mysql.com/doc/connector-python
            self._storage = connector.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
            )

            self.CONNECTIONS_CACHE[storage_host] = self._storage

        return self._storage

    def get(self, feature_id, feature_metric):
        """
        :type feature_id str
        :type feature_metric str
        :rtype: int|float|None
        """
        # SELECT value FROM features_metrics
        # WHERE feature = 'ckeditor' and metric = 'score'
        # ORDER BY timestamp desc limit 1;
        self.logger.info('Reading metric for "%s": %s', feature_id, feature_metric)

        try:
            cursor = self.storage.cursor()

            cursor.execute(
                'SELECT /* mycroft_holmes */ value FROM features_metrics '
                'WHERE feature = %s and metric = %s '
                'ORDER BY timestamp DESC LIMIT 1',
                (feature_id, feature_metric)
            )

            # self.logger.debug('SQL: %s', cursor.statement)

            row = cursor.fetchone()

            if row:
                value = float(row[0])
                return int(value) if value.is_integer() else value

            return None

        except MySqlError as ex:
            self.logger.error('Storage error occured: %s', ex)
            raise ex

    def push(self, feature_id, feature_metrics):
        """
        :type feature_id str
        :type feature_metrics dict
        """
        self.logger.info('Pushing metrics for "%s": %s', feature_id, feature_metrics)

        self.data[feature_id] = feature_metrics

    def commit(self):
        """
        Store metrics collected via push()
        """
        try:
            cursor = self.storage.cursor()
            self.storage.start_transaction()

            # take the current timestamp and use it to make this value consistent
            cursor.execute('SELECT /* mycroft_holmes */ NOW()')
            timestamp = cursor.fetchone()[0]

            self.logger.info("Using timestamp %s", timestamp)

            for feature_id, feature_metrics in self.data.items():
                for (metric, value) in feature_metrics.items():
                    self.logger.info("Storing %s ...", (feature_id, metric, value))

                    cursor.execute(
                        'INSERT INTO /* mycroft_holmes */ features_metrics '
                        '(feature, metric, value, timestamp) '
                        'VALUES (%(feature)s, %(metric)s, %(value)s, %(timestamp)s)',
                        {
                            'feature': feature_id,
                            'metric': metric,
                            'value': value,
                            'timestamp': timestamp,
                        }
                    )

                    # self.logger.debug('SQL: %s', cursor.statement)

            self.storage.commit()

            self.data = dict()
            self.logger.info('Data has been stored')

        except MySqlError as ex:
            self.logger.error('Storage error occured: %s', ex)
            raise ex

    def get_the_latest_timestamp(self):
        """
        Get the timestamp of the latest entry in metrics storage

        :rtype: str|None
        """
        try:
            cursor = self.storage.cursor()
            cursor.execute("SELECT /* mycroft_holmes */ MAX(timestamp) FROM features_metrics")

            return cursor.fetchone()[0]
        except MySqlError as ex:
            self.logger.error('Storage error occured: %s', ex)
            return None

    def get_feature_metrics_history(self, feature__id):
        """
        Yields the historical values of all metrics for a given feature

        :type feature__id str
        :rtype: list[dict]
        """
        cursor = self.storage.cursor()

        cursor.execute(
            "SELECT /* mycroft_holmes */ DATE(timestamp) AS date, metric, value "
            "FROM features_metrics WHERE feature = %(feature)s GROUP BY date, metric",
            {
                'feature': feature__id
            }
        )

        for row in iter(cursor):
            yield dict(zip(
                ('date', 'metric', 'value'),
                row
            ))
