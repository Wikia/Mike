"""
Unit tests for feature ID <-> feature name decoding
"""
from mycroft_holmes.config import Config


def test_get_feature_id():
    assert Config.get_feature_id('Foo Bar') == 'foo_bar'
    assert Config.get_feature_id('Foo  Bar') == 'foo_bar'
    assert Config.get_feature_id('FOO Bar') == 'foo_bar'
    assert Config.get_feature_id('FOO Bar12') == 'foo_bar12'
    assert Config.get_feature_id('CKEditor') == 'ckeditor'
    assert Config.get_feature_id('Message Wall') == 'message_wall'
    assert Config.get_feature_id(' Message Wall ') == 'message_wall'
