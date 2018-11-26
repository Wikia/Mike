"""
Set of unit test for SourceBase class
"""
from mycroft_holmes.sources.base import SourceBase
from mycroft_holmes.sources import ConstSource


def test_get_sources_names():
    sources = SourceBase.get_sources_names()

    print(sources)
    assert 'common/const' in sources


def test_new_from_name():
    source = SourceBase.new_from_name('common/const')

    print(source)
    assert isinstance(source, ConstSource.__class__), 'ConstSource should be returned by SourceBase.new_from_name'
