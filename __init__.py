from aqt import gui_hooks, mw
from aqt.qt import (QWidget, QVBoxLayout, QShortcut, QKeySequence, QAction, QObject, QEvent, QMenu, 
                    QSplitter, Qt, QDockWidget, QSizePolicy, QUrl)
from aqt.utils import tooltip
from aqt.gui_hooks import browser_will_show
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

    # Get search query from main field and configured sites
    search_urls = _get_search_urls_for_editor(editor)

    event_filter = BrowserEventFilter(parent)
    parent.installEventFilter(event_filter)

    close_event_filter = BrowserCloseEventFilter(parent)
    parent.installEventFilter(close_event_filter)

    for action in parent.findChildren(QAction):
        action_filter = BrowserActionFilter(parent)
        action.installEventFilter(action_filter)

    if parent.__class__.__name__ == "Browser":
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
        
        # Open search URLs if any
        if search_urls:
            _open_search_urls_in_browser(browser, search_urls)
        return

    splitter = QSplitter(Qt.Orientation.Horizontal)
    parent._splitter = splitter
    
    main_widget = parent
    old_layout = main_widget.layout()
    
    container = QWidget()
    container.setLayout(old_layout)
    
    splitter.addWidget(container)
    browser = BrowserWidget(url=None, parent=parent)
    parent._browser_sidebar = browser
    splitter.addWidget(browser)
    
    new_layout = QVBoxLayout()
    new_layout.setContentsMargins(0, 0, 0, 0)
    new_layout.addWidget(splitter)
    main_widget.setLayout(new_layout)
    
    splitter.setSizes([500, 500])
    
    # Open search URLs if any
    if search_urls:
        _open_search_urls_in_browser(browser, search_urls)

def _get_search_urls_for_editor(editor):
    """Get the search URLs based on the current note's main field content and configured sites."""
    cfg = config.get_config()
    
    # Get the current note type and main field
    note_type_name = cfg.get("note_type")
    main_field_name = cfg.get("main_field")
    
    if not note_type_name or not main_field_name:
        return []
    
    # Get the main field content from the editor
    try:
        if hasattr(editor, 'note') and editor.note:
            note = editor.note
            if main_field_name in note:
                main_field_content = note[main_field_name].strip()
                if not main_field_content:
                    return []
            else:
                return []
        else:
            return []
    except:
        return []
    
    # Get configured fields and their sites for this note type
    configurable_fields = cfg.get("configurable_fields", {}).get(note_type_name, [])
    field_search_configs = cfg.get("field_search_configs", {}).get(note_type_name, {})
    
    search_urls = []
    
    # From settings.py PREDEFINED_SEARCH_SITES
    predefined_sites = {
        "English": {
            "Cambridge Dictionary": "https://dictionary.cambridge.org/dictionary/english/{}",
            "Oxford Dictionary": "https://www.oxfordlearnersdictionaries.com/definition/english/{}_1?q={}",
            "Merriam-Webster": "https://www.merriam-webster.com/dictionary/{}",
            "Longman Dictionary": "https://www.ldoceonline.com/dictionary/{}",
            "Collins Dictionary": "https://www.collinsdictionary.com/dictionary/english/{}",
            "Macmillan Dictionary": "https://www.macmillandictionary.com/search/?q={}",
            "Urban Dictionary": "https://www.urbandictionary.com/define.php?term={}",
            "Vocabulary.com": "https://www.vocabulary.com/dictionary/{}",
            "The Free Dictionary": "https://www.thefreedictionary.com/{}",
            "Dictionary.com": "https://www.dictionary.com/browse/{}"
        },
        "Tiếng Việt": {
            "Cambridge Việt": "https://dictionary.cambridge.org/dictionary/english-vietnamese/{}",
            "Dunno": "https://dunno.ai/search/word/{}?hl=vi",
            "Laban": "https://dict.laban.vn/find?type=1&query={}",
            "VDict": "https://vdict.com/{},1,0,0.html",
        },
        "Example": {
            "Dunno Examples": "https://dunno.ai/search/example/{}?hl=vi",
            "TraCau": "https://tracau.vn/?s={}",
            "Ludwig": "https://ludwig.guru/s/{}",
            "Sentence Stack": "https://sentencestack.com/q/{}",
            "Fraze.it": "https://fraze.it/n_search.jsp?q={}&l=0"
        },
        "Thesaurus": {
            "Thesaurus.com": "https://www.thesaurus.com/browse/{}",
            "Power Thesaurus": "https://www.powerthesaurus.org/{}",
            "Merriam-Webster Thesaurus": "https://www.merriam-webster.com/thesaurus/{}"
        },
        "Image": {
            "Google Images": "https://www.google.com/search?q={}&tbm=isch",
            "Bing Images": "https://www.bing.com/images/search?q={}",
            "Giphy": "https://giphy.com/search/{}",
            "Tenor": "https://tenor.com/search/{}"
        }
    }
    
    # For each configured field, get the selected sites
    for field_name in configurable_fields:
        if field_name in field_search_configs:
            field_config = field_search_configs[field_name]
            for category_name, sites_config in field_config.items():
                if category_name in predefined_sites:
                    for site_name, is_enabled in sites_config.items():
                        if is_enabled and site_name in predefined_sites[category_name]:
                            url_template = predefined_sites[category_name][site_name]
                            # Format the URL with the main field content
                            try:
                                placeholders = url_template.count("{}")
                                search_url = url_template.format(*([main_field_content] * placeholders))
                                search_urls.append((site_name, search_url))
                            except Exception:
                                # Handle URL formatting errors
                                pass
    
    return search_urls

def _open_search_urls_in_browser(browser, search_urls):
    """Open search URLs in the browser as separate tabs."""
    if not search_urls:
        return
    
    # Open the first URL in the current tab (replace the blank page)
    first_site_name, first_url = search_urls[0]
    current_tab = browser.tabs.currentWidget()
    if current_tab:
        current_tab.webview.setUrl(QUrl(first_url))
        current_tab.url_edit.setText(first_url)
        # Update tab title
        index = browser.tabs.indexOf(current_tab)
        browser.tabs.setTabText(index, first_site_name[:15] + "..." if len(first_site_name) > 15 else first_site_name)
    
    # Open remaining URLs in new tabs
    for site_name, url in search_urls[1:]:
        browser._add_new_tab(url)

def add_browser_button(buttons, editor):
    """Add Web Browser button to editor buttons."""
    browser_button = editor.addButton(
        icon=None,
        cmd="web_browser",
        func=lambda e=editor: show_browser_sidebar(e),
        tip="Web Browser (Ctrl+B)",
        keys="Ctrl+B"
    )
    buttons.append(browser_button)

def setup_editor_shortcuts(editor):
    """Setup editor shortcuts for browser refresh."""
    cfg = config.get_config()
    refresh_shortcut = cfg.get("refresh_shortcut", "Ctrl+R")

    if hasattr(editor, "parentWindow"):
        window = editor.parentWindow

        # Nếu đã có shortcut cũ, xóa để tránh trùng lặp
        if hasattr(window, "_refresh_shortcut"):
            window._refresh_shortcut.setParent(None)

        # Tạo QShortcut trên cửa sổ Add Dialog
        shortcut = QShortcut(QKeySequence(refresh_shortcut), window)
        # Cho phép shortcut hoạt động dù focus con của window
        shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut.activated.connect(lambda: refresh_browser_search(editor))
        # Giữ tham chiếu để Qt không garbage-collect
        window._refresh_shortcut = shortcut

def refresh_browser_search(editor):
    """Refresh browser search based on current note's main field content."""
    if not hasattr(editor, 'parentWindow') or not hasattr(editor.parentWindow, '_browser_sidebar'):
        return
        
    browser = editor.parentWindow._browser_sidebar
    if not browser or not browser.isVisible():
        return
        
    # Lấy nội dung từ Main Field
    cfg = config.get_config()
    main_field = cfg.get("main_field")
    if not main_field:
        return
        
    # Lưu note đang mở trước khi lấy nội dung
    def after_save():
        # Lấy nội dung từ editor sau khi đã lưu
        if hasattr(editor, 'note') and editor.note:
            note = editor.note
            if main_field in note:
                main_field_content = note[main_field].strip()
                if not main_field_content:
                    return
                    
                # Hiển thị tooltip cho người dùng biết đang tìm kiếm gì
                tooltip(f"🔍 Searching for: {main_field_content}")
                
                # Lấy danh sách URL cần tìm kiếm
                search_urls = _get_search_urls_for_editor(editor)
                if search_urls:
                    _open_search_urls_in_browser(browser, search_urls)
    
    # Gọi saveNow với callback
    editor.saveNow(after_save)

def on_browser_row_changed(browser, row):
    """Handle browser row change to refresh search."""
    if not hasattr(browser, '_browser_sidebar') or not browser._browser_sidebar.isVisible():
        return
        
    editor = browser.editor
    if editor:
        # Thêm delay nhỏ để đảm bảo editor đã được cập nhật
        mw.progress.timer(100, lambda: refresh_browser_search(editor), False)

def setup_browser_shortcuts(browser):
    """Setup browser shortcuts for refresh."""
    cfg = config.get_config()
    refresh_shortcut = cfg.get("refresh_shortcut", "Ctrl+R")
    
    # Gán phím tắt cho browser.form thay vì browser
    shortcut = QShortcut(QKeySequence(refresh_shortcut), browser.form)
    shortcut.activated.connect(lambda: refresh_browser_search(browser.editor))

def setup_browser_hooks(browser):
    """Setup all browser hooks and shortcuts."""
    # Setup shortcuts
    setup_browser_shortcuts(browser)
    
    # Connect to row change signal
    browser.form.table.selectionModel().selectionChanged.connect(
        lambda: on_browser_row_changed(browser, None)
    )

# Register hooks
gui_hooks.editor_did_init_buttons.append(add_browser_button)
gui_hooks.editor_did_init.append(setup_editor_shortcuts)
browser_will_show.append(setup_browser_hooks)  # Use browser_will_show instead of browser_did_load

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