"""
Common code
"""
import logging
import re

from mycroft_holmes.errors import MycroftSourceError

SOURCES_CACHE = dict()


class SourceBase:
    """
    Base class for Mycroft Holmes source.
    Provides sources discovery and documentation generated for all sources.
    """
    NAME = None

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        """
        :rtype: str
        """
        return '<{} name:{}>'.format(self.__class__.__name__, self.NAME)

    @staticmethod
    def sources():
        """
        Returns all subclasses of SourceBase class imported in __init__.py file.

        They are ordered by source name.

        :rtype: list[cls]
        """
        classes = SourceBase.__subclasses__() + DatabaseSourceBase.__subclasses__()
        classes = [cls for cls in classes if cls.NAME]

        return sorted(classes, key=lambda x: x.NAME)

    @staticmethod
    def get_sources_names():
        """
        Returns names of all available sources

        :rtype: list[str]
        """
        return [source.NAME for source in SourceBase.sources()]

    @staticmethod
    def new_from_name(source_name, args=None):
        """
        :type source_name str
        :type args dict
        :rtype: SourceBase
        """
        for source in SourceBase.sources():
            if source.NAME == source_name:
                args = args if args else {}
                return source(**args)

        raise MycroftSourceError('"%s" source is not known' % source_name)

    @classmethod
    def new_for_metric(cls, metric, config):
        """
        :type metric mycroft_holmes.metric.Metric
        :type config mycroft_holmes.config.Config
        :rtype: SourceBase
        """
        source_name = metric.get_source_name()

        if source_name in SOURCES_CACHE:
            return SOURCES_CACHE.get(source_name)

        # get an entry from "source" config file section that matches given metric "source"
        spec = config.get_sources().get(source_name)

        # fallback to names of base sources (those defined in the code, not in the config file)
        if spec is None:
            if source_name in cls.get_sources_names():
                spec = metric.get_spec().copy()
                del spec['source']

                spec['kind'] = source_name
                spec['name'] = None

        # raise an error if an entry has not been found
        if spec is None:
            raise MycroftSourceError('"%s" source is not known' % source_name)

        source_spec = spec.copy()
        source_kind = source_spec['kind']

        # remove common spec entries before we pass them as source parameters
        del source_spec['name']
        del source_spec['kind']
        if 'weight' in source_spec:
            del source_spec['weight']

        logger = logging.getLogger(cls.__class__.__name__)
        logger.info('Setting up "%s" source of "%s" kind (args: %s)',
                    source_name, source_kind, list(source_spec.keys()))

        source = SourceBase.new_from_name(source_kind, args=source_spec)

        # cache it
        SOURCES_CACHE[source_name] = source

        return source

    def get_value(self, **kwargs):
        """
        :rtype: int
        """
        raise NotImplementedError('get_value needs to be implemented')

    def get_name(self):
        """
        :rtype: str
        """
        return self.NAME

    def get_more_link(self, **kwargs):
        """
        Returns a tuple with link name and URL that can give you more details
        for this metric, e.g. link to a JIRA dashboard

        :rtype: tuple[str, str]|None
        """
        # pylint: disable=no-self-use,unused-argument
        return None

    @classmethod
    def get_short_description(cls):
        """
        :rtype: str
        """
        doc = str(cls.__doc__).strip()

        return doc.split('\n')[0]

    @classmethod
    def get_description(cls):
        """
        :rtype: str
        """
        doc = str(cls.__doc__).strip()

        # remove indentation
        doc = re.sub(r'^ {4}', '', doc, flags=re.MULTILINE)

        return doc


class DatabaseSourceBase(SourceBase):
    """
    An abstract class for database-related sources

    Used by "aws/athena" and "common/mysql" sources.
    """
    def __init__(self):
        super(DatabaseSourceBase, self).__init__()
        self._client = None

    def _get_client(self):
        """
        Get database client when needed
        """
        raise NotImplementedError('_get_client needs to be implemented')

    @property
    def client(self):
        """
        Connect to Database lazily

        :rtype: mysql.connector.connection.MySQLConnection
        """
        if not self._client:
            self._client = self._get_client()

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
