import os
import sys
import types


# create a dummy 'aqt' module before importing config
aqt_dummy = types.ModuleType("aqt")

class DummyMenuBar:
    def insertMenu(self, *a, **k):
        pass

class DummyMenuHelp:
    def menuAction(self):
        return None

mw_dummy = types.SimpleNamespace(
    addonManager=None,
    app=types.SimpleNamespace(keyboardModifiers=lambda: 0),
    form=types.SimpleNamespace(
        menubar=DummyMenuBar(),
        menuHelp=DummyMenuHelp()
    )
)

class DummyQt(types.SimpleNamespace):
    def __getattr__(self, item):
        return type(item, (), {})

aqt_dummy.mw = mw_dummy
aqt_dummy.qt = DummyQt()
aqt_dummy.utils = types.SimpleNamespace(tooltip=lambda *a, **k: None)
aqt_dummy.gui_hooks = types.SimpleNamespace(editor_did_init_buttons=[], editor_did_init=[], browser_will_show=[])

sys.modules['aqt'] = aqt_dummy
sys.modules['aqt.qt'] = aqt_dummy.qt
sys.modules['aqt.utils'] = aqt_dummy.utils
sys.modules['aqt.gui_hooks'] = aqt_dummy.gui_hooks

import importlib.util

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.py')
spec = importlib.util.spec_from_file_location('config', config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

class DummyAddonManager:
    def __init__(self):
        self.called_with = None
    def addonFolder(self, name):
        self.called_with = name
        return '/addon/path'

class DummyMw:
    def __init__(self, addon_manager):
        self.addonManager = addon_manager


def test_get_config_path(monkeypatch):
    manager = DummyAddonManager()
    dummy_mw = DummyMw(manager)
    monkeypatch.setattr(config, 'mw', dummy_mw)
    path = config.get_config_path()
    assert manager.called_with == config.__name__
    assert path == os.path.join('/addon/path', 'config.json')
