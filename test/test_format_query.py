"""
Set of unit test for query format
"""
from mycroft_holmes.utils import format_query


def test_format():
    assert format_query('foo') == 'foo'
    assert format_query('{foo}') == '{foo}'
    assert format_query('{foo}', {'foo': 'bar'}) == 'bar'
    assert format_query('123 {foo} 456', {'foo': 'bar'}) == '123 bar 456'
    assert format_query('123 {foo} 456 {bar}', {'foo': 'bar'}) == '123 bar 456 {bar}'
    assert format_query('project = "{project}"', {'project': 'Foo'}) == 'project = "Foo"'
    assert format_query('project = "{project}" AND priority = "{priority}"',
                        {'project': 'Foo', 'priority': 'P3'}) == 'project = "Foo" AND priority = "P3"'
