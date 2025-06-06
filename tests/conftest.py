import os
import sys
import types
import importlib
import pathlib
import pytest

collect_ignore = [os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '__init__.py'))]


class _DummySignal:
    def connect(self, *args, **kwargs):
        pass


class _DummyAction:
    def __init__(self, *args, **kwargs):
        self.triggered = _DummySignal()


class _DummyMenu:
    def __init__(self, *args, **kwargs):
        pass

    def addAction(self, *args, **kwargs):
        pass


class _DummyMenuBar:
    def insertMenu(self, *args, **kwargs):
        pass


@pytest.fixture
def dummy_aqt(tmp_path):
    """Provide a minimal stub of the aqt module required for imports."""
    qt = types.SimpleNamespace(
        QWidget=object,
        QVBoxLayout=object,
        QShortcut=object,
        QKeySequence=object,
        QAction=_DummyAction,
        QObject=object,
        QEvent=types.SimpleNamespace(Type=types.SimpleNamespace(KeyPress=0, Close=1, Paint=2, ShortcutOverride=3)),
        QMenu=_DummyMenu,
        QSplitter=object,
        Qt=types.SimpleNamespace(
            ShortcutContext=types.SimpleNamespace(WidgetWithChildrenShortcut=1),
            AlignmentFlag=types.SimpleNamespace(AlignLeft=0),
            TextElideMode=types.SimpleNamespace(ElideRight=0),
            KeyboardModifier=types.SimpleNamespace(MetaModifier=1, ControlModifier=2),
            Key=types.SimpleNamespace(Key_W=1),
        ),
        QDockWidget=object,
        QSizePolicy=object,
        QUrl=str,
    )

    utils = types.SimpleNamespace(tooltip=lambda *a, **k: None)

    gui_hooks = types.SimpleNamespace(
        editor_did_init_buttons=[],
        editor_did_init=[],
        browser_will_show=[],
    )

    mw = types.SimpleNamespace(
        app=types.SimpleNamespace(keyboardModifiers=lambda: 0),
        form=types.SimpleNamespace(
            menuHelp=types.SimpleNamespace(menuAction=lambda: None),
            menubar=_DummyMenuBar(),
        ),
        progress=types.SimpleNamespace(timer=lambda *a, **k: None),
        addonManager=types.SimpleNamespace(addonFolder=lambda name: str(tmp_path)),
    )

    aqt_module = types.SimpleNamespace(mw=mw, gui_hooks=gui_hooks, qt=qt, utils=utils)
    return aqt_module


@pytest.fixture
def load_module(monkeypatch, dummy_aqt):
    """Helper to import project modules with the dummy aqt available."""
    monkeypatch.setitem(sys.modules, "aqt", dummy_aqt)
    monkeypatch.setitem(sys.modules, "aqt.qt", dummy_aqt.qt)
    monkeypatch.setitem(sys.modules, "aqt.utils", dummy_aqt.utils)
    monkeypatch.setitem(sys.modules, "aqt.gui_hooks", dummy_aqt.gui_hooks)

    def _loader(name):
        root = pathlib.Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root))
        try:
            module = importlib.import_module(name)
            importlib.reload(module)
            return module
        finally:
            sys.path.pop(0)

    return _loader
