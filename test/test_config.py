"""
Set of unit test for Config class
"""
# https://docs.pytest.org/en/latest/assert.html#assertions-about-expected-exceptions
import pytest

from mycroft_holmes.config import Config, MycroftHolmesConfigError

from . import get_fixtures_directory


def test_config_loads_correctly():
    config = Config(config_file=get_fixtures_directory() + '/config.yaml')
    assert isinstance(config, Config)


def test_config_missing_file():
    with pytest.raises(MycroftHolmesConfigError) as exc_info:
        Config(config_file=get_fixtures_directory() + '/missing.yaml')

    print(exc_info)
    assert 'Failed to load' in str(exc_info.value)
    assert 'fixtures/missing.yaml' in str(exc_info.value)


def test_config_broken_file():
    with pytest.raises(MycroftHolmesConfigError) as exc_info:
        Config(config_file=get_fixtures_directory() + '/broken.yaml')

    print(exc_info)

    assert 'Failed to parse' in str(exc_info.value)
    assert 'fixtures/broken.yaml' in str(exc_info.value)
    assert 'line 2, column 7' in str(exc_info.value)
