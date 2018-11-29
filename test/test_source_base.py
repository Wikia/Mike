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
    assert isinstance(source, ConstSource), 'ConstSource should be returned by SourceBase.new_from_name'
    assert source.get_value() == 1


def test_get_description():
    source = ConstSource()

    print(source.get_description())
    assert source.get_name() == 'common/const'
    assert source.get_short_description() == \
        'Returns a constant value (can be used to tweak a score of a feature).'
    assert source.get_description() == """
Returns a constant value (can be used to tweak a score of a feature).

#### `metrics` config

```yaml
    metrics:
      -  name: common/const
         weight: 100
```
""".strip()
