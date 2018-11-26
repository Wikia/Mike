"""
Common code
"""
import logging


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

        :rtype: list[SourceBase]
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
    def new_from_name(name):
        """
        :type name str
        :rtype: SourceBase|None
        """
        for source in SourceBase._sources():
            if source.NAME == name:
                return source

        return None

    def get_value(self):
        """
        :rtype: int
        """
        raise NotImplementedError('get_value needs to be implemented')
