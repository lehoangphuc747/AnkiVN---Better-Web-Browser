from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, 
    QScrollArea, QGroupBox, QWidget # Ensure all Qt components are from aqt.qt
)
from aqt import mw
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

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setting - Better Web Browser")
        self.field_site_checkboxes = {} 
        self.setup_ui()
        
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.setMinimumWidth(550) 
        self.setMinimumHeight(450)

        # Note Type selection
        note_type_layout = QHBoxLayout()
        note_type_label = QLabel("Note Type:")
        self.note_type_combo = QComboBox()
        all_note_types = mw.col.models.allNames()
        self.note_type_combo.addItems(all_note_types)
        
        current_cfg = config.get_config()
        current_note_type = current_cfg.get("note_type")
        if current_note_type and current_note_type in all_note_types:
            self.note_type_combo.setCurrentText(current_note_type)
        elif all_note_types:
            self.note_type_combo.setCurrentIndex(0)
            current_note_type = self.note_type_combo.currentText()

        note_type_layout.addWidget(note_type_label)
        note_type_layout.addWidget(self.note_type_combo)
        self.main_layout.addLayout(note_type_layout)

        # Main Field selection
        main_field_layout = QHBoxLayout()
        main_field_label = QLabel("Main Field (for integrated browser search):")
        self.main_field_combo = QComboBox()
        main_field_layout.addWidget(main_field_label)
        main_field_layout.addWidget(self.main_field_combo)
        self.main_layout.addLayout(main_field_layout)

        # Scrollable area for other fields settings
        self.other_fields_scroll_area = QScrollArea(self)
        self.other_fields_scroll_area.setWidgetResizable(True)
        self.other_fields_widget_container = QWidget()
        self.other_fields_layout = QVBoxLayout(self.other_fields_widget_container) # This is the layout for the scroll area content
        self.other_fields_scroll_area.setWidget(self.other_fields_widget_container)
        
        self.main_layout.addWidget(QLabel("<b>Configure search sites for other fields:</b>"))
        self.main_layout.addWidget(self.other_fields_scroll_area)
        
        self.note_type_combo.currentTextChanged.connect(self._on_note_type_changed)
        self.main_field_combo.currentTextChanged.connect(self._on_main_field_changed)

        self._on_note_type_changed(self.note_type_combo.currentText()) # Initial population of main_field_combo and other_fields_ui

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        self.main_layout.addLayout(button_layout)

    def _on_note_type_changed(self, note_type_name):
        self.main_field_combo.blockSignals(True)
        self.main_field_combo.clear()
        
        current_cfg = config.get_config()
        saved_note_type = current_cfg.get("note_type")
        saved_main_field = current_cfg.get("main_field")

        if note_type_name:
            model = mw.col.models.byName(note_type_name)
            if model:
                field_names = [f['name'] for f in model['flds']]
                self.main_field_combo.addItems(field_names)
                if note_type_name == saved_note_type and saved_main_field and saved_main_field in field_names:
                    self.main_field_combo.setCurrentText(saved_main_field)
                elif field_names:
                    self.main_field_combo.setCurrentIndex(0)
        
        self.main_field_combo.blockSignals(False)
        # Crucially, call _update_other_fields_settings_ui here AFTER main_field_combo is populated and its signal unblocked.
        # The _on_main_field_changed signal will handle the first update if the main field changed due to repopulation.
        # If it didn't change, we need to trigger it manually.
        if self.main_field_combo.currentText() == saved_main_field and note_type_name == saved_note_type:
             self._update_other_fields_settings_ui() # Manually update if main field didn't change through signal
        else:
            # If main_field_combo changed, its signal _on_main_field_changed will call _update_other_fields_settings_ui
            # If main_field_combo is empty (no fields), also call to clear UI
            if not self.main_field_combo.count():
                self._update_other_fields_settings_ui()

    def _on_main_field_changed(self, main_field_name): # Renamed field_combo to main_field_combo
        self._update_other_fields_settings_ui()

    def _update_other_fields_settings_ui(self):
        # Clear previous checkboxes and layout for other_fields_layout
        while self.other_fields_layout.count():
            item = self.other_fields_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater() # Use deleteLater for safety
        self.field_site_checkboxes.clear()

        note_type_name = self.note_type_combo.currentText()
        current_main_field_name = self.main_field_combo.currentText()

        if not note_type_name:
            return

        model = mw.col.models.byName(note_type_name)
        if not model:
            return

        current_cfg = config.get_config()
        # field_search_configs for the current note_type
        saved_note_type_field_configs = current_cfg.get("field_search_configs", {}).get(note_type_name, {})

        for field_model in model['flds']:
            field_name = field_model['name']
            if field_name == current_main_field_name: # Skip the main field itself
                continue

            self.field_site_checkboxes[field_name] = {}
            
            field_groupbox = QGroupBox(f"Field: {field_name}")
            field_groupbox_layout = QVBoxLayout()

            for category, sites in PREDEFINED_SEARCH_SITES.items():
                self.field_site_checkboxes[field_name][category] = {}
                category_label = QLabel(f"<b>{category}</b>")
                field_groupbox_layout.addWidget(category_label)
                
                # Get saved sites for this specific field and category
                saved_sites_for_field_category = saved_note_type_field_configs.get(field_name, {}).get(category, {})

                for site_name, site_url in sites.items():
                    checkbox = QCheckBox(site_name)
                    is_checked = saved_sites_for_field_category.get(site_name, False)
                    checkbox.setChecked(is_checked)
                    self.field_site_checkboxes[field_name][category][site_name] = checkbox
                    field_groupbox_layout.addWidget(checkbox)
            
            field_groupbox.setLayout(field_groupbox_layout)
            self.other_fields_layout.addWidget(field_groupbox)
        
        self.other_fields_layout.addStretch() 

    def save_settings(self):
        cfg = config.get_config()
        
        current_note_type = self.note_type_combo.currentText()
        current_main_field = self.main_field_combo.currentText()

        cfg["note_type"] = current_note_type
        cfg["main_field"] = current_main_field

        if "field_search_configs" not in cfg:
            cfg["field_search_configs"] = {}
        
        if current_note_type:
            if current_note_type not in cfg["field_search_configs"]:
                cfg["field_search_configs"][current_note_type] = {}
            
            # Clear old configs for fields not present anymore or for the current main field
            current_note_type_field_configs = {}

            for field_name, categories in self.field_site_checkboxes.items():
                # field_name here are the "other" fields
                if field_name not in current_note_type_field_configs:
                    current_note_type_field_configs[field_name] = {}
                for category_name, sites in categories.items():
                    if category_name not in current_note_type_field_configs[field_name]:
                        current_note_type_field_configs[field_name][category_name] = {}
                    for site_name, checkbox in sites.items():
                        current_note_type_field_configs[field_name][category_name][site_name] = checkbox.isChecked()
            cfg["field_search_configs"][current_note_type] = current_note_type_field_configs
        
        config.save_config(cfg)
        self.accept()
