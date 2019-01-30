"""
Set of unit test for MysqlSource class
"""
from pytest import raises

from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import AthenaSource


def get_source(mocked_client=None):
    """
    :type mocked_client object
    :rtype: AthenaSource
    """
    return SourceBase.new_from_name(
        source_name=AthenaSource.NAME,
        args={
            'access_key_id': '',
            'secret_access_key': '',
            's3_staging_dir': '',
            'region': 'us-foo-1',
            'client': mocked_client
        }
    )


def test_is_source_present():
    assert AthenaSource.NAME in SourceBase.get_sources_names()


def test_client_exception_handling():
    source = get_source()

    # AssertionError: "query" parameter needs to be provided
    with raises(AssertionError):
        source.get_value()
