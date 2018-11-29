"""
Handles a single metric of a feature
"""
import logging

from .errors import MycroftMetricError
from .sources.base import SourceBase


class Metric:
    """
    Wraps a single metric
    """
    def __init__(self, feature_name, config, spec):
        """
        :type feature_name str
        :type config mycroft_holmes.config.Config
        :type spec dict
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self.feature_name = feature_name
        self.config = config
        self.spec = spec

    def get_name(self):
        """
        :rtype: str
        """
        return self.spec['name']

    def get_source_name(self):
        """
        :rtype: str
        """
        return self.spec.get('source')

    def get_spec(self):
        """
        :rtype: dict
        """
        return self.spec

    def _get_source(self):
        """
        :rtype: SourceBase
        """
        return SourceBase.new_for_metric(metric=self, config=self.config)

    def fetch_value(self):
        """
        Fetches the metric value from the appropriate source

        :raise: MycroftMetricError
        :rtype: int
        """
        self.logger.debug('Fetching value for: %s', self.get_spec())

        if self.get_source_name() is None:
            raise MycroftMetricError('"%s" has no source specified, skipping!' % self.get_name())

        source = self._get_source()

        return source.get_value(**self.get_spec())
