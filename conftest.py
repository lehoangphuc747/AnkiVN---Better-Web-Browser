import sys
import types
import os
import atexit
from pathlib import Path

# Temporarily rename the addon's __init__.py so pytest doesn't import it
ROOT = Path(__file__).resolve().parent
INIT_FILE = ROOT / "__init__.py"
RENAMED = ROOT / "__init__.py.bak"
if INIT_FILE.exists() and not RENAMED.exists():
    INIT_FILE.rename(RENAMED)
    def restore():
        if RENAMED.exists():
            RENAMED.rename(INIT_FILE)
    atexit.register(restore)

# Provide a minimal fake 'aqt' module so that importing addon modules does not fail
fake_aqt = types.ModuleType("aqt")
fake_aqt.mw = types.SimpleNamespace(
    addonManager=types.SimpleNamespace(addonFolder=lambda: ""),
    pm=types.SimpleNamespace(addonFolder=lambda: ""),
    form=types.SimpleNamespace(
        menubar=types.SimpleNamespace(insertMenu=lambda *a, **k: None),
        menuHelp=types.SimpleNamespace(menuAction=lambda: None),
    ),
    progress=types.SimpleNamespace(timer=lambda *a, **k: None),
    app=types.SimpleNamespace(keyboardModifiers=lambda: 0),
)

fake_aqt.gui_hooks = types.SimpleNamespace(
    editor_did_init_buttons=[],
    editor_did_init=[],
    browser_will_show=[],
)

qt_mod = types.ModuleType("aqt.qt")
for cls in [
    "QWidget",
    "QVBoxLayout",
    "QShortcut",
    "QKeySequence",
    "QAction",
    "QObject",
    "QEvent",
    "QMenu",
    "QSplitter",
    "Qt",
    "QDockWidget",
    "QSizePolicy",
    "QUrl",
]:
    setattr(qt_mod, cls, type(cls, (), {}))

fake_aqt.qt = qt_mod
fake_aqt.utils = types.SimpleNamespace(tooltip=lambda *a, **k: None)

# Additional QtWebEngine stubs used in browser.py
for name in [
    "QWebEngineView",
    "QWebEnginePage",
]:
    setattr(fake_aqt, name, type(name, (), {}))

class DummyProfile:
    class PersistentCookiesPolicy:
        ForcePersistentCookies = 0

    def __init__(self, *a, **k):
        pass

    def setPersistentCookiesPolicy(self, *a, **k):
        pass

    def settings(self):
        return DummySettings()

class DummySettings:
    class WebAttribute:
        JavascriptEnabled = 0
        JavascriptCanAccessClipboard = 1

    def setAttribute(self, *a, **k):
        pass

setattr(fake_aqt, "QWebEngineProfile", DummyProfile)
setattr(fake_aqt, "QWebEngineSettings", DummySettings)

sys.modules.setdefault("aqt", fake_aqt)
sys.modules.setdefault("aqt.gui_hooks", fake_aqt.gui_hooks)
sys.modules.setdefault("aqt.qt", fake_aqt.qt)
sys.modules.setdefault("aqt.utils", fake_aqt.utils)
