"""
A base HTTP-bases source
"""
from requests import session

from mycroft_holmes.utils import format_query
from ..base import SourceBase


class HttpSourceBase(SourceBase):
    """
    A generic trait for all HTTP-based sources
    """
    # pylint: disable=unused-argument
    def __init__(self, client, **kwargs):
        """
        :type client object
        :type kwargs object
        """
        super().__init__()
        self._client = client or session()

    def make_request(self, url):
        """
        :type url
        :rtype: requests.Response
        """
        resp = self._client.get(url)
        resp.raise_for_status()

        self.logger.info('GET <%s> - HTTP %d (%.2f kB)',
                         url, resp.status_code, 1. * len(resp.text) / 1024)

        return resp

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
        :rtype: int|float
        """
        raise NotImplementedError('get_value needs to be implemented')
