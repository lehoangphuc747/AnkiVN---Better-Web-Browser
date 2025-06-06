from functools import partial
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, 
    QScrollArea, QGroupBox, QWidget, QListWidget, QListWidgetItem, Qt, QTreeWidget, QTreeWidgetItem,
    QDialogButtonBox, QEvent, QKeySequence, QSplitter
)
from aqt import mw
from aqt.utils import showInfo
from . import config

PREDEFINED_SEARCH_SITES = {
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

class ShortcutEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Click to set shortcut...")
        self.setToolTip("Press any key combination to set shortcut")
        
    def keyPressEvent(self, event):
        try:
            if event.type() == QEvent.Type.KeyPress:
                modifiers = event.modifiers()
                key = event.key()
                
                # Skip if key is not valid
                if key in (Qt.Key.Key_unknown, Qt.Key.Key_Control, Qt.Key.Key_Shift, 
                          Qt.Key.Key_Alt, Qt.Key.Key_Meta, Qt.Key.Key_AltGr):
                    return
                    
                # Convert modifiers to string
                mod_str = ""
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    mod_str += "Ctrl+"
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    mod_str += "Shift+"
                if modifiers & Qt.KeyboardModifier.AltModifier:
                    mod_str += "Alt+"
                    
                # Convert key to string
                key_str = QKeySequence(key).toString()
                if not key_str:
                    return
                    
                # Set the shortcut text
                self.setText(mod_str + key_str)
                event.accept()
        except Exception as e:
            # Log error but don't crash
            print(f"Error in ShortcutEdit.keyPressEvent: {str(e)}")
            return

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Better Web Browser Settings")
        self.field_site_checkboxes = {}  # [note_type][field_name][category_name][site_name] -> QCheckBox
        self.configurable_field_details = {} # [field_name] -> { "group_box": QGroupBox, "content_widget": QWidget, "toggle_button": QPushButton, "categories": {}}
        
        self.current_note_type_name = None # To track current note type easily
        self.current_main_field_name = None # To track current main field easily

        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create two columns
        columns_layout = QHBoxLayout()
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()
        
        # Left Column - Basic Configuration
        # Note Type Selection
        note_type_group = QGroupBox("Note Type")
        note_type_layout = QVBoxLayout()
        self.note_type_combo = QComboBox()
        self.note_type_combo.currentTextChanged.connect(self.on_note_type_changed)
        note_type_layout.addWidget(self.note_type_combo)
        note_type_group.setLayout(note_type_layout)
        left_column.addWidget(note_type_group)
        
        # Main Field Selection
        main_field_group = QGroupBox("Main Field")
        main_field_layout = QVBoxLayout()
        self.main_field_combo = QComboBox()
        main_field_layout.addWidget(self.main_field_combo)
        main_field_group.setLayout(main_field_layout)
        left_column.addWidget(main_field_group)
        
        # Configurable Fields
        fields_group = QGroupBox("Configurable Fields")
        fields_layout = QVBoxLayout()
        self.fields_list = QListWidget()
        self.fields_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.fields_list.itemChanged.connect(self.on_field_selection_changed)
        fields_layout.addWidget(self.fields_list)
        fields_group.setLayout(fields_layout)
        left_column.addWidget(fields_group)
        
        # Refresh Shortcut (moved to bottom)
        shortcut_group = QGroupBox("Refresh Shortcut")
        shortcut_layout = QVBoxLayout()
        self.shortcut_edit = ShortcutEdit()
        shortcut_layout.addWidget(self.shortcut_edit)
        shortcut_group.setLayout(shortcut_layout)
        left_column.addWidget(shortcut_group)
        
        # Right Column - Search Sites
        sites_group = QGroupBox("Search Sites")
        sites_layout = QVBoxLayout()
        
        # Add search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to filter sites...")
        self.search_edit.textChanged.connect(self.filter_sites)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        sites_layout.addLayout(search_layout)
        
        # Create single column for sites
        self.sites_tree = QTreeWidget()
        self.sites_tree.setHeaderLabels(["Site", "Enabled", "URL Template"])
        sites_layout.addWidget(self.sites_tree)
        
        sites_group.setLayout(sites_layout)
        right_column.addWidget(sites_group)
        
        # Add columns to main layout with stretch factors
        columns_layout.addLayout(left_column, 1)  # Left column takes 1/3
        columns_layout.addLayout(right_column, 2)  # Right column takes 2/3
        main_layout.addLayout(columns_layout)
        
        # Buttons at bottom
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Set minimum sizes for better layout
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

    def load_config(self):
        cfg = config.get_config()
        
        # Load note types
        note_types = mw.col.models.all()
        self.note_type_combo.clear()
        for note_type in note_types:
            self.note_type_combo.addItem(note_type['name'])
            
        # Set current note type
        if cfg.get("note_type"):
            index = self.note_type_combo.findText(cfg["note_type"])
            if index >= 0:
                self.note_type_combo.setCurrentIndex(index)
                
        # Load main field
        self.update_main_field_combo()
        if cfg.get("main_field"):
            index = self.main_field_combo.findText(cfg["main_field"])
            if index >= 0:
                self.main_field_combo.setCurrentIndex(index)
                
        # Load refresh shortcut
        self.shortcut_edit.setText(cfg.get("refresh_shortcut", "Ctrl+R"))
        
        # Load configurable fields
        self.update_fields_list()
        
        # Load search sites
        self.update_sites_tree()
        
    def update_main_field_combo(self):
        self.main_field_combo.clear()
        note_type = self.note_type_combo.currentText()
        if note_type:
            model = mw.col.models.by_name(note_type)
            if model:
                for field in model['flds']:
                    self.main_field_combo.addItem(field['name'])
                    
    def update_fields_list(self):
        self.fields_list.clear()
        note_type = self.note_type_combo.currentText()
        if note_type:
            model = mw.col.models.by_name(note_type)
            if model:
                cfg = config.get_config()
                configurable_fields = cfg.get("configurable_fields", {}).get(note_type, [])
                
                for field in model['flds']:
                    item = QListWidgetItem(field['name'])
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(
                        Qt.CheckState.Checked if field['name'] in configurable_fields 
                        else Qt.CheckState.Unchecked
                    )
                    self.fields_list.addItem(item)
                    
    def update_sites_tree(self):
        """Update the sites tree based on selected fields."""
        self.sites_tree.clear()
        note_type = self.note_type_combo.currentText()
        if not note_type:
            return

        # Get selected fields
        selected_fields = []
        for i in range(self.fields_list.count()):
            item = self.fields_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_fields.append(item.text())

        if not selected_fields:
            return

        # Load saved configurations
        cfg = config.get_config()
        field_configs = cfg.get("field_search_configs", {}).get(note_type, {})
        
        # Add all fields to single tree
        for field_name in selected_fields:
            self._add_field_to_tree(self.sites_tree, field_name, field_configs.get(field_name, {}))
        
        # Resize columns
        self.sites_tree.resizeColumnToContents(0)
        self.sites_tree.resizeColumnToContents(1)
        self.sites_tree.resizeColumnToContents(2)

    def _add_field_to_tree(self, tree, field_name, field_config):
        """Add a field and its sites to a tree widget."""
        field_item = QTreeWidgetItem([field_name, "", ""])
        tree.addTopLevelItem(field_item)
        
        # Add all predefined categories and sites
        for category, sites in PREDEFINED_SEARCH_SITES.items():
            cat_item = QTreeWidgetItem([category, "", ""])
            field_item.addChild(cat_item)
            
            # Create toggle button for category
            toggle_btn = QPushButton("Select All")
            toggle_btn.setCheckable(True)
            toggle_btn.clicked.connect(lambda checked, cat=cat_item, btn=toggle_btn: self._toggle_category_sites(cat, checked, btn))
            tree.setItemWidget(cat_item, 1, toggle_btn)
            
            # Get saved site states for this category
            saved_sites = field_config.get(category, {})
            
            # Check if all sites are enabled
            all_enabled = all(saved_sites.get(site_name, False) for site_name in sites)
            toggle_btn.setChecked(all_enabled)
            
            for site_name, url_template in sites.items():
                # Check if site was previously enabled
                is_enabled = saved_sites.get(site_name, False)
                
                site_item = QTreeWidgetItem([site_name, "", url_template])
                site_item.setCheckState(1, Qt.CheckState.Checked if is_enabled else Qt.CheckState.Unchecked)
                cat_item.addChild(site_item)
        
        # Expand the field item by default
        field_item.setExpanded(True)

    def _toggle_category_sites(self, category_item, checked, button):
        """Toggle all sites in a category."""
        for i in range(category_item.childCount()):
            site_item = category_item.child(i)
            site_item.setCheckState(1, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        
        # Update button text
        button.setText("Deselect All" if checked else "Select All")

    def filter_sites(self, text):
        """Filter sites based on search text."""
        for i in range(self.sites_tree.topLevelItemCount()):
            field_item = self.sites_tree.topLevelItem(i)
            field_visible = False
            
            for j in range(field_item.childCount()):
                cat_item = field_item.child(j)
                cat_visible = False
                
                for k in range(cat_item.childCount()):
                    site_item = cat_item.child(k)
                    site_name = site_item.text(0).lower()
                    site_visible = text.lower() in site_name
                    site_item.setHidden(not site_visible)
                    cat_visible = cat_visible or site_visible
                
                cat_item.setHidden(not cat_visible)
                field_visible = field_visible or cat_visible
            
            field_item.setHidden(not field_visible)

    def on_note_type_changed(self, note_type):
        self.update_main_field_combo()
        self.update_fields_list()
        self.update_sites_tree()
        
    def on_field_selection_changed(self, item):
        """Handle field selection change in the fields list."""
        self.update_sites_tree()

    def accept(self):
        cfg = config.get_config()
        
        # Save note type
        cfg["note_type"] = self.note_type_combo.currentText()
        
        # Save main field
        cfg["main_field"] = self.main_field_combo.currentText()
        
        # Save refresh shortcut
        cfg["refresh_shortcut"] = self.shortcut_edit.text()
        
        # Save configurable fields
        note_type = self.note_type_combo.currentText()
        if note_type:
            configurable_fields = []
            for i in range(self.fields_list.count()):
                item = self.fields_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    configurable_fields.append(item.text())
                    
            if "configurable_fields" not in cfg:
                cfg["configurable_fields"] = {}
            cfg["configurable_fields"][note_type] = configurable_fields
            
        # Save search sites configuration
        if note_type:
            field_configs = {}
            for i in range(self.sites_tree.topLevelItemCount()):
                field_item = self.sites_tree.topLevelItem(i)
                field_name = field_item.text(0)
                field_config = {}
                
                for j in range(field_item.childCount()):
                    cat_item = field_item.child(j)
                    category = cat_item.text(0)
                    sites = {}
                    
                    for k in range(cat_item.childCount()):
                        site_item = cat_item.child(k)
                        site_name = site_item.text(0)
                        enabled = site_item.checkState(1) == Qt.CheckState.Checked
                        sites[site_name] = enabled
                        
                    field_config[category] = sites
                    
                field_configs[field_name] = field_config
                
            if "field_search_configs" not in cfg:
                cfg["field_search_configs"] = {}
            cfg["field_search_configs"][note_type] = field_configs
            
        # Save configuration
        if config.save_config(cfg):
            super().accept()
        else:
            showInfo("Failed to save configuration.")