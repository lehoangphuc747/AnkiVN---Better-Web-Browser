import importlib
import os
import sys
import types

import pytest


@pytest.fixture
def config_module(tmp_path, monkeypatch):
    # Set up fake aqt.mw with addonFolder methods
    addon_dir = tmp_path / "addon"
    addon_dir.mkdir()

    class DummyAddonManager:
        def addonFolder(self):
            return str(addon_dir)

    dummy_manager = DummyAddonManager()
    # mw has addonManager and pm attributes
    mw = types.SimpleNamespace(
        addonManager=dummy_manager,
        pm=types.SimpleNamespace(addonFolder=dummy_manager.addonFolder),
    )

    fake_aqt = types.ModuleType("aqt")
    fake_aqt.mw = mw

    monkeypatch.setitem(sys.modules, "aqt", fake_aqt)

    # Import or reload config module after patching
    module = importlib.import_module("config")
    importlib.reload(module)

    yield module, addon_dir

    # cleanup
    monkeypatch.delitem(sys.modules, "config", raising=False)
    monkeypatch.delitem(sys.modules, "aqt", raising=False)


def test_get_config_path_uses_addon_folder(config_module):
    module, addon_dir = config_module
    expected = os.path.join(str(addon_dir), "config.json")
    assert module.get_config_path() == expected


def test_get_config_returns_defaults_when_missing(tmp_path, monkeypatch):
    addon_dir = tmp_path / "addon"
    addon_dir.mkdir()

    class DummyAddonManager:
        def addonFolder(self):
            return str(addon_dir)

    dummy_manager = DummyAddonManager()
    mw = types.SimpleNamespace(
        addonManager=dummy_manager,
        pm=types.SimpleNamespace(addonFolder=dummy_manager.addonFolder),
    )
    fake_aqt = types.ModuleType("aqt")
    fake_aqt.mw = mw
    monkeypatch.setitem(sys.modules, "aqt", fake_aqt)

    module = importlib.import_module("config")
    importlib.reload(module)

    cfg = module.get_config()
    assert cfg == module.get_default_config()
    assert not os.path.exists(module.get_config_path())
