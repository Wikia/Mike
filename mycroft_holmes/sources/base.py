"""
Common code
"""
import logging
import re

SOURCES_CACHE = dict()


class SourceBase:
    """
    Base class for Mycroft Holmes source.
    Provides sources discovery and documentation generated for all sources.
    """
    NAME = None

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def _sources():
        """
        Returns all subclasses of SourceBase class imported in __init__.py file

        :rtype: list[cls]
        """
        return SourceBase.__subclasses__()

    @staticmethod
    def get_sources_names():
        """
        Returns names of all available sources

        :rtype: list[str]
        """
        return [source.NAME for source in SourceBase._sources()]

    @staticmethod
    def new_from_name(name, args=None):
        """
        :type name str
        :type args dict
        :rtype: SourceBase|None
        """
        for source in SourceBase._sources():
            if source.NAME == name:
                args = args if args else {}
                return source(**args)

        return None

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
        source_spec = config.get_sources().get(source_name).copy()
        source_kind = source_spec['kind']

        del source_spec['name']
        del source_spec['kind']

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
