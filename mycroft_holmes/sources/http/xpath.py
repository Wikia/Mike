"""
http/xpath source
"""
from lxml.html import document_fromstring
from requests import session

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.utils import format_query

from ..base import SourceBase


class HttpXPathSource(SourceBase):
    """
    Makes a HTTP request to fetch HTML and takes a node using xpath query.

    #### `sources` config

    > Not applicable. This source does not have any specific settings.

    #### `metrics` config

    ```yaml
        metrics:
          - name: lubimy_czytac/rating
            source: http/xpath  # use the base source directly here
            url: "http://lubimyczytac.pl/ksiazka/{book_id}"
            xpath: '//*[@itemprop="aggregateRating"]//*[@itemprop="ratingValue"]'
            label: "Book rating: %d"
    ```

    > Please refer to [XPath documentation](https://developer.mozilla.org/en-US/docs/Web/XPath)
    > for how to specify the `xpath` parameter.

    You can use the following JS snippet to test your xpath in a browser:

    ```js
    document.evaluate(
        '//*[@itemprop="aggregateRating"]//*[@itemprop="ratingValue"]', document
    ).iterateNext()
    ```

    #### `features` config

    ```yaml
        features:
          # http://lubimyczytac.pl/ksiazka/4871036/pan-tadeusz
          - name: PanTadeusz
            template:
              book_id: 4871036
            metrics:
              name: lubimy_czytac/rating
    ```
    """

    NAME = 'http/xpath'

    def __init__(self, client=None, **kwargs):
        """
        :type client obj
        :type kwargs obj
        """
        super(HttpXPathSource, self).__init__()

        self._client = client or session()

    @staticmethod
    def get_url(**kwargs):
        """
        :type: dict
        :rtype: str|None
        """
        url = kwargs.get('url')
        return format_query(url, kwargs.get('template')) if url else None

    def get_value(self, **kwargs):
        """
        :raise: MycroftSourceError
        :rtype: float
        """
        url = self.get_url(**kwargs)
        xpath = kwargs.get('xpath')

        assert isinstance(url, str), '"url" parameter needs to be provided'
        assert isinstance(xpath, str), '"xpath" parameter needs to be provided'

        self.logger.info('Fetching <%s>', url)

        try:
            resp = self._client.get(url)
            resp.raise_for_status()

            self.logger.info('GET <%s> - HTTP %d (%.2f kB)',
                             url, resp.status_code, 1. * len(resp.text) / 1024)

            # parse with lxml
            # https://lxml.de/lxmlhtml.html#parsing-html
            self.logger.info('Parsing HTML and querying it with "%s" xpath', xpath)

            node = document_fromstring(resp.text)
            matches = node.xpath(xpath)

            if not matches:
                raise MycroftSourceError('xpath query returned no matches')

            # "123,5" - do our best to parse such value
            text = str(matches[0].text).strip()
            text = text.replace(",", ".")

            return float(text)

        except Exception as ex:
            raise MycroftSourceError('Failed to get metric value: %s' % repr(ex))

    def get_more_link(self, **kwargs):
        """
        Returns a tuple with link name and URL that this metric fetches

        :rtype: tuple[str, str]|None
        """
        return (
            'Visit the page',
            self.get_url(** kwargs)
        )
