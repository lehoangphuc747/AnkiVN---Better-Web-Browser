from aqt import QSplitter, Qt, gui_hooks, mw
from aqt.qt import QWidget, QVBoxLayout, QShortcut, QKeySequence, QAction, QObject, QEvent, QMenu
from aqt.utils import tooltip
from .browser import BrowserWidget
from . import config
from .settings import SettingsDialog

class BrowserEventFilter(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if (event.key() == Qt.Key.Key_W and 
                (event.modifiers() & (Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.ControlModifier)) and
                hasattr(self.parent, '_browser_sidebar') and
                self.parent._browser_sidebar.isVisible() and
                self.parent._browser_sidebar.tabs.count() > 1):
                self.parent._browser_sidebar._close_current_tab()
                event.accept()
                return True
        elif event.type() == QEvent.Type.Close:
            if (hasattr(self.parent, '_browser_sidebar') and 
                self.parent._browser_sidebar.isVisible() and 
                self.parent._browser_sidebar.tabs.count() > 1):
                modifiers = mw.app.keyboardModifiers()
                if modifiers & (Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.ControlModifier):
                    self.parent._browser_sidebar._close_current_tab()
                    event.ignore()
                    return True
        return False

class BrowserCloseEventFilter(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Close:
            if (hasattr(self.parent, '_browser_sidebar') and 
                self.parent._browser_sidebar.isVisible() and 
                self.parent._browser_sidebar.tabs.count() > 1):
                modifiers = mw.app.keyboardModifiers()
                if modifiers & (Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.ControlModifier):
                    self.parent._browser_sidebar._close_current_tab()
                    event.ignore()
                    return True
        return False

class BrowserActionFilter(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Paint:
            if obj.text() == "&Close" or obj.text() == "Close":
                original_trigger = obj.triggered
                def new_trigger(checked=False):
                    if (hasattr(self.parent, '_browser_sidebar') and 
                        self.parent._browser_sidebar.isVisible() and 
                        self.parent._browser_sidebar.tabs.count() > 1):
                        self.parent._browser_sidebar._close_current_tab()
                    else:
                        original_trigger.emit()
                obj.triggered.connect(new_trigger)
                return True
        return False

def show_settings():
    dialog = SettingsDialog(mw)
    dialog.exec()

def show_browser_sidebar(editor, url=None):
    parent = editor.parentWindow
    
    if hasattr(parent, '_browser_sidebar'):
        if parent._browser_sidebar.isVisible():
            if parent.__class__.__name__ == "Browser":
                if hasattr(parent, '_browser_dock'):
                    parent._browser_dock.hide()
            parent._browser_sidebar.hide()
            return
        else:
            if parent.__class__.__name__ == "Browser":
                if hasattr(parent, '_browser_dock'):
                    parent._browser_dock.show()
            parent._browser_sidebar.show()
            return

    event_filter = BrowserEventFilter(parent)
    parent.installEventFilter(event_filter)

    close_event_filter = BrowserCloseEventFilter(parent)
    parent.installEventFilter(close_event_filter)

    for action in parent.findChildren(QAction):
        action_filter = BrowserActionFilter(parent)
        action.installEventFilter(action_filter)

    if parent.__class__.__name__ == "Browser":
        from PyQt6.QtWidgets import QDockWidget, QSizePolicy
        # Pass None for url, as it's no longer configured
        browser = BrowserWidget(url=None, parent=parent) 
        parent._browser_sidebar = browser
        
        dock = QDockWidget(parent)  
        dock.setTitleBarWidget(QWidget())  
        dock.setWidget(browser)
        dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        
        browser.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        window_width = parent.width()
        target_width = window_width // 3
        browser.setFixedWidth(target_width)
        
        parent.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        parent._browser_dock = dock  
        return

    splitter = QSplitter(Qt.Orientation.Horizontal)
    parent._splitter = splitter
    
    main_widget = parent
    old_layout = main_widget.layout()
    
    container = QWidget()
    container.setLayout(old_layout)
    
    splitter.addWidget(container)
    # Pass None for start_url, as it's no longer configured
    # start_url = url if url is not None else config.get_config()["start_url"]
    browser = BrowserWidget(url=None, parent=parent) # Pass None for url
    parent._browser_sidebar = browser
    splitter.addWidget(browser)
    
    new_layout = QVBoxLayout()
    new_layout.setContentsMargins(0, 0, 0, 0)
    new_layout.addWidget(splitter)
    main_widget.setLayout(new_layout)
    
    splitter.setSizes([500, 500])

def add_browser_button(buttons, editor):
    tip_text = "Toggle web browser" if editor.parentWindow.__class__.__name__ == "Browser" else "Toggle web browser (Ctrl+Shift+L)"
    button = editor.addButton(
        icon=None,
        cmd="toggle_browser",
        func=lambda e: show_browser_sidebar(editor),
        tip=tip_text,  
        label="🌐"
    )

    shortcut = QShortcut(QKeySequence("Shift+Ctrl+L"), editor.widget)
    shortcut.activated.connect(lambda: show_browser_sidebar(editor))

    buttons.append(button)
    return buttons

# 메인 메뉴에 AnkiVN 서브메뉴 생성
ankivn_menu = QMenu("AnkiVN", mw)
mw.form.menubar.insertMenu(mw.form.menuHelp.menuAction(), ankivn_menu) # Add this line to insert before Help menu

# 서브메뉴에 Better Web Browser 항목 추가
browser_settings_action = QAction("Better Web Browser", mw)
browser_settings_action.triggered.connect(show_settings)
ankivn_menu.addAction(browser_settings_action)

# 추가 항목을 원하면 여기에 코드 작성
# 예: 다른 기능에 대한 액션 추가
# another_action = QAction("Another Feature", mw)
# another_action.triggered.connect(some_function)
# ankivn_menu.addAction(another_action)

gui_hooks.editor_did_init_buttons.append(add_browser_button)
