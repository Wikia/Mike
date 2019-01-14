"""
Handles metrics storage
"""
import logging
from mysql import connector


class MetricsStorage:
    """
    MySQL storage
    """
    CONNECTIONS_CACHE = dict()

    def __init__(self, config):
        """
        :type config mycroft_holmes.config.Config
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self._storage = None
        self.data = dict()

        # read the config
        self.config = config.get_raw()['storage']

        assert self.config['engine'] == 'mysql', 'Only "mysql" storage is currently supported'

    @property
    def storage(self):
        """
        Lazy-connect to a storage and return a handler, i.e. MySQL cursor

        :rtype: mysql.connector.connection.MySQLConnection
        """
        storage_host = self.config['host']

        # use cached connection
        if storage_host in self.CONNECTIONS_CACHE:
            return self.CONNECTIONS_CACHE[storage_host]

        if not self._storage:
            self.logger.info('Connecting to MySQL running at "%s"', storage_host)

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
        :rtype: int|None
        """
        # SELECT value FROM features_metrics
        # WHERE feature = 'ckeditor' and metric = 'score'
        # ORDER BY timestamp desc limit 1;
        self.logger.info('Reading metric for "%s": %s', feature_id, feature_metric)

        cursor = self.storage.cursor()

        cursor.execute(
            'SELECT /* mycroft_holmes */ value FROM features_metrics '
            'WHERE feature = %s and metric = %s '
            'ORDER BY timestamp DESC LIMIT 1',
            (feature_id, feature_metric)
        )

        row = cursor.fetchone()
        return row[0] if row else None

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

            for feature_id, feature_metrics in self.data.items():
                for (metric, value) in feature_metrics.items():
                    cursor.execute(
                        'INSERT INTO /* mycroft_holmes */ features_metrics '
                        '(feature, metric, value) '
                        'VALUES (%(feature)s, %(metric)s, %(value)s)',
                        {
                            'feature': feature_id,
                            'metric': metric,
                            'value': value
                        }
                    )

            self.storage.commit()

            self.data = dict()
            self.logger.info('Data has been stored')

        except connector.errors.Error as ex:
            self.logger.error('Storage error occured: %s', ex)
            raise ex
