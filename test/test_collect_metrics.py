"""
Set of unit test for collect_metrics script
"""

from mycroft_holmes.bin.collect_metrics import get_metrics_for_feature
from mycroft_holmes.config import Config

from . import get_fixtures_directory


def test_calculate_metrics_and_score():
    config = Config(config_file=get_fixtures_directory() + '/const.yaml')

    metrics = get_metrics_for_feature('Foo Bar', config)

    print(metrics)

    assert len(metrics) == 3
    assert metrics['score'] == 108
    assert metrics['usage/foo'] == 1
    assert metrics['usage/bar'] == 1
