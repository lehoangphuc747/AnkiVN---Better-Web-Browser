from aqt import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings, Qt, QUrl
from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QShortcut,
    QKeySequence,
    QTabWidget,
    QTabBar,
    QEvent,
)
from .config import PREDEFINED_SEARCH_SITES

class TabWidget(QWidget):
    def __init__(self, url=None, parent=None, browser=None):
        super().__init__(parent)
        self.browser = browser
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(5, 5, 5, 0)
        
        self.back_button = QPushButton("←", self)
        self.back_button.clicked.connect(self._go_back)
        self.back_button.setMaximumWidth(30)
        self.back_button.setToolTip("Back (Ctrl+[)")
        nav_layout.addWidget(self.back_button)

        self.forward_button = QPushButton("→", self)
        self.forward_button.clicked.connect(self._go_forward)
        self.forward_button.setMaximumWidth(30)
        self.forward_button.setToolTip("Forward (Ctrl+])")
        nav_layout.addWidget(self.forward_button)

        self.reload_button = QPushButton("↻", self)
        self.reload_button.clicked.connect(self._reload_page)
        self.reload_button.setMaximumWidth(30)
        self.reload_button.setToolTip("Reload (Ctrl+R)")
        nav_layout.addWidget(self.reload_button)
        
        self.url_edit = QLineEdit(self)
        self.url_edit.returnPressed.connect(self._navigate_to_url)
        self.url_edit.setCursorPosition(0)
        self.url_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        nav_layout.addWidget(self.url_edit)

        self.new_tab_button = QPushButton("+", self)
        self.new_tab_button.clicked.connect(lambda: self.browser._add_new_tab() if self.browser else None)
        self.new_tab_button.setMaximumWidth(30)
        self.new_tab_button.setToolTip("New Tab (Ctrl+T)")
        nav_layout.addWidget(self.new_tab_button)
        
        layout.addLayout(nav_layout)
        
        self.profile = QWebEngineProfile("browser_profile")
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        
        self.webview = QWebEngineView(self)
        self.webpage = QWebEnginePage(self.profile, self.webview)
        self.webview.setPage(self.webpage)
        
        self.webview.urlChanged.connect(self._url_changed)
        self.webview.loadFinished.connect(self._on_load_finished)
        
        if url:
            self.webview.load(QUrl(url))
            self.url_edit.setText(url)
        else:
            # If no URL is provided, load a default page or leave it blank
            self.webview.load(QUrl("about:blank")) 
            self.url_edit.setText("")
        
        layout.addWidget(self.webview)

        QShortcut(QKeySequence("Ctrl+["), self).activated.connect(self._go_back)
        QShortcut(QKeySequence("Ctrl+]"), self).activated.connect(self._go_forward)

    def _go_back(self):
        self.webview.back()

    def _go_forward(self):
        self.webview.forward()
    
    def _navigate_to_url(self):
        url = self.url_edit.text().strip()
        
        if any([
            url.startswith(('http://', 'https://')),
            url.startswith('www.'),
            '.' in url and not ' ' in url
        ]):
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
        else:
            url = 'https://www.google.com/search?q=' + url.replace(' ', '+')
            
        self.webview.setUrl(QUrl(url))
    
    def _url_changed(self, url):
        self.url_edit.setText(url.toString())
        self.url_edit.setCursorPosition(0)
        if self.parent() and isinstance(self.parent(), QTabWidget):
            index = self.parent().indexOf(self)
            title = self.webview.title() or "New Tab"
            self.parent().setTabText(index, title[:20] + "..." if len(title) > 20 else title)

    def _reload_page(self):
        self.webview.reload()

    def focus_web_content(self):
        self.webview.setFocus()

    def current_url(self):
        return self.webview.url().toString()

    def _on_load_finished(self, ok):
        if ok:
            self.focus_web_content()

class BrowserWidget(QWidget):
    def __init__(self, url=None, parent=None):
        super().__init__(parent)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        
        layout.addWidget(self.tabs)
        
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(lambda: self._add_new_tab())
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self._focus_url_current)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self._reload_current)
        
        self._add_new_tab(url)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key.Key_W and 
            (event.modifiers() & (Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.ControlModifier))):
            if self.tabs.count() > 1:
                self._close_current_tab()
                event.accept()
                return
        super().keyPressEvent(event)

    def event(self, event):
        if event.type() == QEvent.Type.ShortcutOverride:
            if (event.key() == Qt.Key.Key_W and 
                (event.modifiers() & (Qt.KeyboardModifier.MetaModifier | Qt.KeyboardModifier.ControlModifier))):
                event.accept()
                return True
        return super().event(event)

    def _close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.hide()

    def _close_current_tab(self):
        self._close_tab(self.tabs.currentIndex())

    def _next_tab(self):
        curr = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((curr + 1) % self.tabs.count())

    def _prev_tab(self):
        curr = self.tabs.currentIndex()
        self.tabs.setCurrentIndex((curr - 1) % self.tabs.count())

    def _update_tab_title(self, tab, title):
        index = self.tabs.indexOf(tab)
        if index >= 0:
            self.tabs.setTabText(index, title[:20] + "..." if len(title) > 20 else title)

    def _focus_url_current(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.url_edit.setFocus()
            current_tab.url_edit.selectAll()

    def _reload_current(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab._reload_page()

    def focus_web_content(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.focus_web_content()

    def showEvent(self, event):
        super().showEvent(event)
        self.focus_web_content()

    def _add_new_tab(self, url=None):
        # If no url is provided to _add_new_tab, TabWidget will handle it (e.g. load about:blank)
        new_tab = TabWidget(url, self.tabs, browser=self)
        index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        new_tab.webview.titleChanged.connect(lambda title: self._update_tab_title(new_tab, title))
        if not url:
            new_tab.url_edit.setFocus()
            new_tab.url_edit.selectAll()
        return new_tab

    def open_search_tabs(self, search_content):
        """Open multiple search tabs based on configured fields and sites"""
        if not search_content or not search_content.strip():
            return
            
        from . import config
        cfg = config.get_config()
        note_type = cfg.get("note_type")
        
        if not note_type:
            return
            
        # Get configured fields and their search sites
        configurable_fields = cfg.get("configurable_fields", {}).get(note_type, [])
        field_search_configs = cfg.get("field_search_configs", {}).get(note_type, {})
        
        search_urls = []
        search_content_encoded = search_content.strip().replace(' ', '+')
        
        # Collect all search URLs from configured fields
        for field_name in configurable_fields:
            field_config = field_search_configs.get(field_name, {})
            
            for category_name, sites_config in field_config.items():
                if category_name in PREDEFINED_SEARCH_SITES:
                    for site_name, is_enabled in sites_config.items():
                        if is_enabled and site_name in PREDEFINED_SEARCH_SITES[category_name]:
                            url_template = PREDEFINED_SEARCH_SITES[category_name][site_name]
                            placeholders = url_template.count("{}")
                            search_url = url_template.format(*([search_content_encoded] * placeholders))
                            search_urls.append((f"{site_name} - {field_name}", search_url))
        
        # Clear existing tabs if any and open search tabs
        if search_urls:
            # Clear all existing tabs
            while self.tabs.count() > 0:
                self.tabs.removeTab(0)
            
            # Open search tabs
            for tab_title, search_url in search_urls:
                new_tab = self._add_new_tab(search_url)
                # Set a more descriptive tab title
                tab_index = self.tabs.indexOf(new_tab)
                if tab_index >= 0:
                    self.tabs.setTabText(tab_index, tab_title[:15] + "..." if len(tab_title) > 15 else tab_title)
        
        # If no search URLs, just open a blank tab
        if not search_urls:
            self._add_new_tab()