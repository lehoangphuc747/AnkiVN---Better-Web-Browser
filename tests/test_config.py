import json
import types
import pytest


def test_get_default_config_keys(load_module):
    config = load_module("config")
    cfg = config.get_default_config()
    expected_keys = {
        "note_type",
        "main_field",
        "refresh_shortcut",
        "configurable_fields",
        "field_search_configs",
    }
    assert set(cfg.keys()) == expected_keys


def test_get_config_no_file(load_module, tmp_path):
    config = load_module("config")
    # aqt.mw.addonManager.addonFolder was set to tmp_path by fixture
    cfg = config.get_config()
    assert cfg == config.get_default_config()


def test_save_and_get_config_roundtrip(load_module, tmp_path):
    config = load_module("config")
    sample = {
        "note_type": "Basic",
        "main_field": "Front",
        "refresh_shortcut": "Ctrl+X",
        "configurable_fields": {"Basic": ["Front"]},
        "field_search_configs": {"Basic": {"Front": {}}},
    }
    assert config.save_config(sample)
    loaded = config.get_config()
    assert loaded == sample
