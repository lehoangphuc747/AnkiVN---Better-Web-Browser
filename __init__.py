from aqt import gui_hooks, mw
from aqt.qt import (QWidget, QVBoxLayout, QShortcut, QKeySequence, QAction, QObject, QEvent, QMenu, 
                    QSplitter, Qt, QDockWidget, QSizePolicy, QUrl)
from aqt.utils import tooltip, qconnect
from aqt.gui_hooks import browser_will_show
from .browser import BrowserWidget
from . import config
from .config import PREDEFINED_SEARCH_SITES
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
    
    # Determine if this is the Browser dialog
    is_browser_dialog = parent.__class__.__name__ == "Browser"
    
    # Helper to get main field content from selected note in Browser dialog
    def get_main_field_content_from_browser():
        cfg = config.get_config()
        main_field = cfg.get("main_field")
        if not main_field:
            return None
        # Try to get selected note from browser
        try:
            # parent.selectedNotes() returns a list of note ids
            selected = parent.selectedNotes()
            if not selected:
                return None
            note_id = selected[0]
            note = parent.mw.col.get_note(note_id)
            if note and main_field in note:
                return note[main_field].strip()
        except Exception:
            return None
        return None

    if hasattr(parent, '_browser_sidebar'):
        if parent._browser_sidebar.isVisible():
            if is_browser_dialog:
                # If already open, reload with current selected note
                content = get_main_field_content_from_browser()
                if content:
                    parent._browser_sidebar.open_search_tabs(content)
                else:
                    tooltip("No main field content found for selected note.")
                return
            else:
                if parent.__class__.__name__ == "Browser":
                    if hasattr(parent, '_browser_dock'):
                        parent._browser_dock.hide()
                parent._browser_sidebar.hide()
                return
        else:
            if is_browser_dialog:
                parent._browser_sidebar.show()
                # Also reload with current selected note
                content = get_main_field_content_from_browser()
                if content:
                    parent._browser_sidebar.open_search_tabs(content)
                else:
                    tooltip("No main field content found for selected note.")
                return
            else:
                if parent.__class__.__name__ == "Browser":
                    if hasattr(parent, '_browser_dock'):
                        parent._browser_dock.show()
                parent._browser_sidebar.show()
                return

    # Get search query from main field and configured sites
    if is_browser_dialog:
        content = get_main_field_content_from_browser()
        search_urls = []
        if content:
            # Use the same logic as open_search_tabs to get URLs
            cfg = config.get_config()
            note_type_name = cfg.get("note_type")
            main_field_name = cfg.get("main_field")
            configurable_fields = cfg.get("configurable_fields", {}).get(note_type_name, [])
            field_search_configs = cfg.get("field_search_configs", {}).get(note_type_name, {})
            predefined_sites = PREDEFINED_SEARCH_SITES
            search_content_encoded = content.strip().replace(' ', '+')
            for field_name in configurable_fields:
                field_config = field_search_configs.get(field_name, {})
                for category_name, sites_config in field_config.items():
                    if category_name in predefined_sites:
                        for site_name, is_enabled in sites_config.items():
                            if is_enabled and site_name in predefined_sites[category_name]:
                                url_template = predefined_sites[category_name][site_name]
                                placeholders = url_template.count("{}")
                                search_url = url_template.format(*([search_content_encoded] * placeholders))
                                search_urls.append((site_name, search_url))
        else:
            tooltip("No main field content found for selected note.")
        # Continue to create the sidebar as usual
    else:
        search_urls = _get_search_urls_for_editor(editor)

    event_filter = BrowserEventFilter(parent)
    parent.installEventFilter(event_filter)

    close_event_filter = BrowserCloseEventFilter(parent)
    parent.installEventFilter(close_event_filter)

    for action in parent.findChildren(QAction):
        action_filter = BrowserActionFilter(parent)
        action.installEventFilter(action_filter)

    browser = BrowserWidget(url=None, parent=parent)
    parent._browser_sidebar = browser

    if is_browser_dialog:
        # Add to right dock area if possible
        dock = QDockWidget("Better Web Browser", parent)
        dock.setWidget(browser)
        dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)

        # Cho phép widget co giãn thoải mái
        browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        parent.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        parent._browser_dock = dock

        # Đặt kích thước ban đầu cho DOCK một cách linh hoạt
        initial_width = parent.width() // 3
        parent.resizeDocks([dock], [initial_width], Qt.Orientation.Horizontal)
        
        if search_urls:
            # Open all search tabs
            browser.open_search_tabs(content)
        return
    else:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        parent._splitter = splitter
        main_widget = parent
        old_layout = main_widget.layout()
        container = QWidget()
        container.setLayout(old_layout)
        splitter.addWidget(container)
        splitter.addWidget(browser)
        new_layout = QVBoxLayout()
        new_layout.setContentsMargins(0, 0, 0, 0)
        new_layout.addWidget(splitter)
        main_widget.setLayout(new_layout)
        splitter.setSizes([500, 500])
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
    
    # Use predefined sites from config
    predefined_sites = PREDEFINED_SEARCH_SITES
    
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
    # Clear existing tabs if any and open search tabs
    if search_urls:
        # Clear all existing tabs
        while browser.tabs.count() > 0:
            browser.tabs.removeTab(0)
        
        # Open search tabs
        for tab_title, search_url in search_urls:
            new_tab = browser._add_new_tab(search_url)
            # Set a more descriptive tab title
            tab_index = browser.tabs.indexOf(new_tab)
            if tab_index >= 0:
                browser.tabs.setTabText(tab_index, tab_title[:15] + "..." if len(tab_title) > 15 else tab_title)

    # If no search URLs, just open a blank tab
    if not search_urls:
        browser._add_new_tab()

def add_browser_button(buttons, editor):
    """Add Web Browser button and Reset button to editor buttons."""
    browser_button = editor.addButton(
        icon=None,
        cmd="web_browser",
        func=lambda e=editor: show_browser_sidebar(e),
        tip="Web Browser",
        keys=None
    )
    buttons.append(browser_button)

    # Add reset button (🔄) next to web_browser
    def reset_browser():
        # Only refresh if browser sidebar is visible
        parent = editor.parentWindow
        if hasattr(parent, '_browser_sidebar') and parent._browser_sidebar.isVisible():
            refresh_browser_search(editor)
        else:
            tooltip("Web browser sidebar is not open!")

    reset_button = editor.addButton(
        icon=None,
        cmd="reset_web_browser",
        func=lambda e=editor: reset_browser(),
        tip="Reset Web Browser",
        label="🔄"
    )
    buttons.append(reset_button)

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

def on_browser_row_changed(browser):
    """Auto-refresh the web browser sidebar in the Browser dialog when the note selection changes, but only if the main field content has changed."""
    # Only do this if the sidebar is open
    if not hasattr(browser, '_browser_sidebar') or not browser._browser_sidebar.isVisible():
        return
    # Get main field content from selected note
    cfg = config.get_config()
    main_field = cfg.get("main_field")
    if not main_field:
        return
    try:
        selected = browser.selected_notes()
        if not selected:
            return
        note_id = selected[0]
        note = browser.mw.col.get_note(note_id)
        if note and main_field in note:
            content = note[main_field].strip()
            # Only refresh if content is different from last search
            if not hasattr(browser, '_last_browser_search_content') or browser._last_browser_search_content != content:
                browser._browser_sidebar.open_search_tabs(content)
                browser._last_browser_search_content = content
    except Exception:
        return

def setup_browser_hooks(browser):
    """Setup browser hooks for auto-refresh on note selection change (no shortcut, no crash)."""
    # Connect to row change signal using browser.table._view
    browser.table._view.selectionModel().selectionChanged.connect(lambda: on_browser_row_changed(browser))

# Register hooks
gui_hooks.editor_did_init_buttons.append(add_browser_button)
gui_hooks.editor_did_init.append(setup_editor_shortcuts)
browser_will_show.append(setup_browser_hooks)  # Use browser_will_show instead of browser_did_load

def show_settings():
    """Show settings dialog."""
    dialog = SettingsDialog(mw)
    dialog.exec()

# 메인 메뉴에 AnkiVN 서브메뉴 생성
ankivn_menu = QMenu("AnkiVN", mw)
mw.form.menubar.insertMenu(mw.form.menuHelp.menuAction(), ankivn_menu) # Add this line to insert before Help menu

# 서브메뉴에 Better Web Browser 항목 추가
browser_settings_action = QAction("Better Web Browser", mw)
browser_settings_action.triggered.connect(show_settings)
ankivn_menu.addAction(browser_settings_action)

def my_browser_hook(browser):
    sel_model = browser.table._view.selectionModel()
    if not sel_model:
        return

    def on_selection_changed(selected, deselected):
        note_ids = browser.selected_notes()
        if not note_ids:
            return
        note_id = note_ids[0]
        cfg = config.get_config()
        main_field = cfg.get("main_field")
        note = browser.mw.col.get_note(note_id)
        if note and main_field in note:
            content = note[main_field].strip()
            if not hasattr(browser, '_last_browser_search_content') or browser._last_browser_search_content != content:
                if hasattr(browser, '_browser_sidebar') and browser._browser_sidebar.isVisible():
                    browser._browser_sidebar.open_search_tabs(content)
                browser._last_browser_search_content = content

    qconnect(sel_model.selectionChanged, on_selection_changed)

# Register the browser hook
browser_will_show.append(my_browser_hook)

gui_hooks.browser_will_show.append(my_browser_hook)
