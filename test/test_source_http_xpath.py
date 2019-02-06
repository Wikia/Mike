"""
Set of unit test for http/xpath source
"""
from pytest import raises

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import HttpXPathSource


class HttpResponse:
    """
    Mocked HTTP response
    """
    def __init__(self, text: str = None):
        self.text = text
        self.status_code = 200

    def raise_for_status(self):
        if self.text is None:
            raise Exception('Mocked HTTP exception')


class HttpClient:
    """
    Mocked requests class
    """
    def __init__(self, text: str = None):
        self.response = HttpResponse(text)
        self.requested_url: str = None

    def get(self, url: str):
        """
        :type url str
        :rtype: HttpResponse
        """
        self.requested_url = url
        return self.response


def get_source_with_mocked_client(mocked_client=None):
    """
    :type mocked_client HttpClient
    :rtype: HttpXPathSource
    """
    return SourceBase.new_from_name(
        source_name=HttpXPathSource.NAME,
        args={
            'client': mocked_client
        }
    )


URL = 'http://foo.bar/{path}'
TEXT = '<p>foo bar<b>\n123,5\n</b></p>'


def test_is_source_present():
    assert HttpXPathSource.NAME in SourceBase.get_sources_names()


def test_source_get_value():
    args = dict(
        url=URL, xpath='//p/b', template={'path': 'get/foo'}
    )

    # exceptions handling
    source = get_source_with_mocked_client(HttpClient(None))

    # AssertionError: "url" parameter needs to be provided
    with raises(MycroftSourceError):
        source.get_value(url=URL, xpath='//p/b', template={'path': 'get/foo'})

    # HTML parsing
    source = get_source_with_mocked_client(HttpClient(TEXT))

    print(source)
    assert isinstance(source, HttpXPathSource)
    assert isinstance(source._client, HttpClient), 'client should be mocked'

    assert source.get_value(**args) == 123

    # URL should be properly filled with template values
    assert source._client.requested_url == 'http://foo.bar/get/foo'
    assert source.get_more_link(**args) == ('Visit the page', 'http://foo.bar/get/foo')


def test_invalid_xpath_and_no_matches():
    source = get_source_with_mocked_client(HttpClient(TEXT))

    # XPathEvalError
    with raises(MycroftSourceError) as ex:
        source.get_value(url=URL, xpath='hello!')

    print(ex)
    assert str(ex).endswith("XPathEvalError('Invalid expression')")

    # xpath is valid, but there are no matches
    with raises(MycroftSourceError) as ex:
        source.get_value(url=URL, xpath='//h1')

    print(ex)
    assert str(ex).endswith("MycroftSourceError('xpath query returned no matches')")


def test_client_exception_handling():
    source = get_source_with_mocked_client()

    # AssertionError: "url" parameter needs to be provided
    with raises(AssertionError):
        source.get_value(query='Foo')

    # AssertionError: "xpath" parameter needs to be provided
    with raises(AssertionError):
        source.get_value(url='Foo')
