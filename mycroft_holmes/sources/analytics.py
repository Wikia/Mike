# pylint: disable=too-many-arguments
"""
GoogleAnalyticsSource class
"""
import json

# https://developers.google.com/api-client-library/python/start/installation
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.utils import format_query

from .base import SourceBase


class GoogleAnalyticsSource(SourceBase):
    """
    Returns a metric value from Google Analytics.

    #### `sources` config

    ```yaml
    sources:
      - name: foo/analytics
        kind: common/analytics
        # JSON-encoded string with service account credentials
        credentials: "${ANALYTICS_SERVICE_ACCOUNT_JSON}"
        view_id: 1234  # your Google Analytics view ID
    ```

    Service account credentials JSON file can obtained from
    https://developers.google.com/analytics/devguides/reporting/core/v4/authorization.

    * "Google Analytics Reporting API" needs to be enabled for service account.
    * You need to add an email (specified in service account JSON file) to your GA users.

    > See https://github.com/Wikia/Mike/issues/12 for more details and troubleshooting guides.

    #### `metrics` config

    ```yaml
        metrics:
          # Google Analytics
          - name: analytics/events
            source: foo/analytics
            label: "%d GA events"
            metric: "ga:totalEvents"
            filters: "{ga_filter}"
    ```

    #### `features` config

    ```yaml
        features:
          - name: FooBar
            template:
              - ga_filter: "ga:eventCategory==foo_bar"
            metrics:
              -  name: analytics/events
    ```
    """

    NAME = 'common/analytics'

    def __init__(self, credentials, view_id, client=None):
        """
        :type credentials str
        :type view_id int
        :type client obj
        """
        super(GoogleAnalyticsSource, self).__init__()

        self.credentials = credentials
        self.view_id = view_id

        self._client = client or None

    @property
    def client(self):
        """
        Set up Google API lazily

        :rtype: googleapiclient.discovery.Resource
        """
        if not self._client:
            self.logger.info('Setting up Google API client')

            try:
                service_account_info = json.loads(self.credentials)
            except json.JSONDecodeError:
                raise MycroftSourceError('Failed to load Google\'s service account JSON file')

            # simple validation of provided JSON credentials
            assert 'client_email' in service_account_info,\
                "'client_email' entry not found in service account JSON"

            self.logger.info('Using service account for %s',
                             service_account_info.get('client_email'))

            self._client = build(
                'analyticsreporting', 'v4',
                credentials=Credentials.from_service_account_info(info=service_account_info),
                # file_cache is unavailable when using oauth2client >= 4.0.0 or google-auth
                cache_discovery=False
            )

            self.logger.info('Connected with Google API for Analytics view #%d', self.view_id)

        return self._client

    def _query(self, start_date, end_date, metric, filters=None, dimension=None):
        """
        :type start_date str
        :type end_date str
        :type metric str
        :type filters str|tuple
        :type dimension str
        :rtype dict
        """
        # @see https://developers.google.com/analytics/devguides/reporting/core/dimsmets
        report_request = {
            'viewId': str(self.view_id),
            'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
            'metrics': [{'expression': metric}],
        }

        if filters is not None:
            report_request['filtersExpression'] = \
                filters if isinstance(filters, str) else ';'.join(filters)

        if dimension is not None:
            report_request['dimensions'] = [{'name': dimension}]

        body = {
            'reportRequests': [report_request]
        }

        self.logger.debug('Query: %s', body)
        return self.client.reports().batchGet(body=body).execute()

    def get_value(self, **kwargs):
        """
        :raise: MycroftSourceError
        :rtype: int
        """
        metric = kwargs.get('metric')
        filters = kwargs.get('filters')

        # validate parameters
        assert isinstance(metric, str), '"metric" parameter needs to be provided'
        assert isinstance(filters, str), '"filters" parameter needs to be provided'

        # apply template variables
        metric = format_query(metric, kwargs.get('template'))
        filters = format_query(filters, kwargs.get('template'))

        self.logger.info('Metric: %s with filters: %s', metric, filters)

        try:
            res = self._query(
                # fetch events for the last 24h
                start_date='1daysAgo', end_date='1daysAgo',
                # 20161016, group by day
                dimension='ga:date',
                # now provide a query
                metric=metric,
                filters=filters,
            )

            self.logger.debug('API response: %s', res)

            report = res['reports'][0]

            # [{'metrics': [{'values': ['270634']}], 'dimensions': ['20181213']}]
            rows = report['data']['rows']
            return int(rows[0]['metrics'][0]['values'][0])

        except Exception as ex:
            self.logger.error('get_value() failed', exc_info=True)
            raise MycroftSourceError('Failed to get metric value: %s' % repr(ex))
