"""
Set of unit test for http/json source
"""
from pytest import raises

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import HttpJsonSource


class HttpResponse:
    """
    Mocked HTTP response
    """
    def __init__(self, data: dict = None):
        self.data = data
        self.status_code = 200

    def raise_for_status(self):
        if self.data is None:
            raise Exception('Mocked HTTP exception')

    @property
    def text(self):
        return ''

    def json(self):
        """
        :rtype: dict
        """
        return self.data


class HttpClient:
    """
    Mocked requests class
    """
    def __init__(self, data: dict = None):
        self.response = HttpResponse(data)
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
        source_name=HttpJsonSource.NAME,
        args={
            'client': mocked_client
        }
    )


URL = 'http://foo.bar/{path}'
DATA = {
    'foo': "123.45",
    'test': [1, 2.4, 3.1415],
    'spaces': "12 345.3"
}

ARGS = dict(
    url=URL, template={'path': 'get/foo'}
)


def test_is_source_present():
    assert HttpJsonSource.NAME in SourceBase.get_sources_names()


def test_source_get_value():
    # HTML parsing
    source = get_source_with_mocked_client(HttpClient(DATA))

    print(source)
    assert isinstance(source, HttpJsonSource)
    assert isinstance(source._client, HttpClient), 'client should be mocked'

    assert source.get_value(jq='.foo', **ARGS) == 123.45, 'String value is casted to float'
    assert source.get_value(jq='.test[0]', **ARGS) == 1, 'Integer remains an integer'
    assert source.get_value(jq='.test[2]', **ARGS) == 3.1415
    assert source.get_value(jq='.spaces', **ARGS) == 12345.3, 'Spaces are removed from the value'

    # jq customized with a template argument
    assert source.get_value(jq='.test[{field_no}]', template={'field_no': 0}, url=URL) == 1
    assert source.get_value(jq='.test[{field_no}]', template={'field_no': 2}, url=URL) == 3.1415

    with raises(MycroftSourceError) as ex:
        source.get_value(jq='.test', **ARGS)
    assert 'Multiple values where found, narrow your jq pattern' in str(ex)

    with raises(MycroftSourceError) as ex:
        source.get_value(jq='.test[3]', **ARGS)
    assert 'jq pattern returned no matches' in str(ex)

    # incorrect jq pattern
    with raises(MycroftSourceError) as ex:
        source.get_value(jq='test[3]', **ARGS)
    assert 'jq: error' in str(ex)

    # URL should be properly filled with template values
    assert source._client.requested_url == 'http://foo.bar/get/foo'
    assert source.get_more_link(**ARGS) == ('Fetch JSON', 'http://foo.bar/get/foo')


def test_client_exception_handling():
    source = get_source_with_mocked_client()

    # AssertionError: "url" parameter needs to be provided
    with raises(AssertionError):
        source.get_value(jq='Foo')

    # AssertionError: "jq" parameter needs to be provided
    with raises(AssertionError):
        source.get_value(url='Foo')
