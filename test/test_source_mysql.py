"""
Set of unit test for MysqlSource class
"""
from os import environ
from unittest import SkipTest

from pytest import raises

from mycroft_holmes.errors import MycroftSourceError
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import MysqlSource


def get_source(env):
    """
    :type env dict
    :rtype: MysqlSource
    """
    return SourceBase.new_from_name(
        source_name=MysqlSource.NAME,
        args={
            'host': '127.0.0.1',
            'database': env.get('TEST_DATABASE'),
            'user': env.get('TEST_DATABASE_USER'),
            'password': env.get('TEST_DATABASE_PASSWORD'),
        }
    )


def test_is_source_present():
    assert MysqlSource.NAME in SourceBase.get_sources_names()


def test_source_get_value():
    if environ.get('TEST_DATABASE') is None:
        raise SkipTest('TEST_DATABASE env variable needs to be set to run this test.')

    source = get_source(environ)

    print(source)
    assert isinstance(source, MysqlSource)

    # AssertionError: "query" parameter needs to be provided
    with raises(AssertionError):
        source.get_value()

    assert source.get_value(
        query='SELECT count(*) FROM mike_test WHERE user_group = %(group)s',
        template={'project': 'Foo', 'group': 'admin'}
    ) == 2


def test_client_exception_handling():
    source = get_source(environ)

    # AssertionError: "query" parameter needs to be provided
    with raises(AssertionError):
        source.get_value()

    # incorrect query
    with raises(MycroftSourceError) as ex:
        source.get_value(query='SELECT foo')

    assert "Unknown column 'foo' in 'field list'" in str(ex)
