"""
Common code
"""
import logging
import re


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
    def new_from_name(name):
        """
        :type name str
        :rtype: SourceBase|None
        """
        for source in SourceBase._sources():
            if source.NAME == name:
                return source()

        return None

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

    def get_short_description(self):
        """
        :rtype: str
        """
        doc = str(self.__doc__).strip()

        return doc.split('\n')[0]

    def get_description(self):
        """
        :rtype: str
        """
        doc = str(self.__doc__).strip()

        # remove indentation
        doc = re.sub(r'^ {4}', '', doc, flags=re.MULTILINE)

        return doc
