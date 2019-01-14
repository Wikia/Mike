"""
Handles a single metric of a feature
"""
import logging

from .errors import MycroftMetricError, MycroftSourceError
from .sources.base import SourceBase
from .storage import MetricsStorage


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

        self._value = False

    def __repr__(self):
        """
        :rtype: str
        """
        return '<Metric feature:{} "{}">'.format(self.feature_name, self._label)

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

    def get_weight(self):
        """
        :rtype: float
        """
        return self.spec.get('weight', 1)

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

    @property
    def _label(self):
        """
        :rtype: str`
        """
        return self.get_spec().get('label')

    def set_value(self, value):
        """
        This one is used in unit tests

        :type value int|None
        """
        self._value = value

    @property
    def value(self):
        """
        :rtype: int
        """
        # lazy-load value from the storage
        if self._value is False:
            storage = MetricsStorage(config=self.config)
            self._value = storage.get(
                feature_id=self.config.get_feature_id(self.feature_name),
                feature_metric=self.get_name()
            )

        return self._value

    @staticmethod
    def format_value(value):
        """
        :type value int
        :rtype: str
        """
        if value >= 100000:
            # 100k
            return '{:.0f}k'.format(value / 1000)

        if value >= 10000:
            # 21.2k
            return '{:.1f}k'.format(value / 1000)

        if value >= 1000:
            # 1.23k
            return '{:.2f}k'.format(value / 1000)

        return str(value)

    def get_formatted_value(self):
        """
        :rtype: str|None
        """
        return self.format_value(self.value) if self.value is not None else None

    def get_label(self):
        """
        Render a label for a metric when rendering it in UI (without a value)

        E.g. "P2 tickets", "Daily page views"

        :rtype: str|None
        """
        return self._label.replace('%d', '').strip(' :') if self._label is not None else None

    def get_label_with_value(self):
        """
        Render a label with a value for a metric. This is used when rendering a component widget.

        E.g. "45 P2 tickets", "Daily page views: 134"

        :rtype: str|None
        """
        return self._label.replace('%d', self.get_formatted_value()) \
            if self.value is not None else None

    def get_more_link(self):
        """
        Returns a tuple with link name and URL that can give you more details
        for this metric, e.g. link to a JIRA dashboard

        :rtype: tuple[str, str]|None
        """
        try:
            return self._get_source().get_more_link(**self.get_spec())
        except MycroftSourceError:
            return None
