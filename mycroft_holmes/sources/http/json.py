"""
http/json source
"""
import pyjq

from mycroft_holmes.errors import MycroftSourceError
from . import HttpSourceBase


class HttpJsonSource(HttpSourceBase):
    # pylint: disable=line-too-long
    """
    Makes a HTTP request to fetch JSON and extract a single value using jq pattern.

    #### `sources` config

    > Not applicable. This source does not have any specific settings.

    #### `metrics` config

    ```yaml
        metrics:
          - name: wikipedia/stats
            source: http/json  # let's use the base source directly here
            url: "https://{wikipedia_domain}.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=statistics&format=json"
            jq: ".query.statistics.{stats_field}"
            label: "{wikipedia_domain} Wikipedia {stats_field}: %d"
    ```

    > Please refer to [jq pattern documentation](hhttps://stedolan.github.io/jq/manual/#Basicfilters)
    > for how to specify the `jq` parameter.

    #### `features` config

    ```yaml
        features:
          - name: PolishWikipedia
            template:
              wikipedia_domain: pl
            metrics:
              name: wikipedia/stats
    ```
    """

    NAME = 'http/json'

    def __init__(self, client=None, **kwargs):
        """
        :type client object
        :type kwargs object
        """
        super().__init__(client=client, **kwargs)

    def get_value(self, **kwargs):
        """
        :raise: MycroftSourceError
        :rtype: float
        """
        url = self.get_url(**kwargs)
        jq = kwargs.get('jq')

        assert isinstance(url, str), '"url" parameter needs to be provided'
        assert isinstance(jq, str), '"jq" parameter needs to be provided'

        self.logger.info('Fetching <%s>', url)

        try:
            resp = self.make_request(url)

            # parse with jq
            # https://stedolan.github.io/jq/manual/#Basicfilters
            self.logger.info('Parsing JSON and querying it with "%s" jq pattern', jq)

            try:
                match = pyjq.first(jq, resp.json())

            except ValueError as ex:
                # jq: error: test/0 is not defined at <top-level>, line 1:
                self.logger.error(str(ex))
                raise MycroftSourceError(str(ex))

            if match is None:
                raise MycroftSourceError('jq pattern returned no matches')

            # we only support returning a single value
            assert not isinstance(match, list), \
                'Multiple values where found, narrow your jq pattern'

            return float(match)

        except Exception as ex:
            raise MycroftSourceError('Failed to get metric value: %s' % repr(ex))

    def get_more_link(self, **kwargs):
        """
        Returns a tuple with link name and URL that this metric fetches

        :rtype: tuple[str, str]|None
        """
        return (
            'Fetch JSON',
            self.get_url(** kwargs)
        )
