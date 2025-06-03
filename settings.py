from functools import partial
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, 
    QScrollArea, QGroupBox, QWidget, QListWidget, QListWidgetItem, Qt
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
        self.setWindowTitle("Better Web Browser - Settings")
        self.field_site_checkboxes = {}  # [note_type][field_name][category_name][site_name] -> QCheckBox
        self.configurable_field_details = {} # [field_name] -> { "group_box": QGroupBox, "content_widget": QWidget, "toggle_button": QPushButton, "categories": {}}
        
        self.current_note_type_name = None # To track current note type easily
        self.current_main_field_name = None # To track current main field easily

        self.setup_ui()
        
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.setMinimumWidth(600) 
        self.setMinimumHeight(500)

        # Note Type selection
        note_type_layout = QHBoxLayout()
        note_type_label = QLabel("Note Type:")
        self.note_type_combo = QComboBox()
        all_note_types = mw.col.models.allNames()
        self.note_type_combo.addItems(all_note_types)
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

        # Field Chooser (to select which other fields are configurable)
        field_chooser_layout = QHBoxLayout()
        field_chooser_label = QLabel("Select fields to configure:")
        self.field_chooser_list = QListWidget()
        self.field_chooser_list.setSelectionMode(QListWidget.SelectionMode.NoSelection) # Items are checkable, not selectable
        field_chooser_layout.addWidget(field_chooser_label)
        field_chooser_layout.addWidget(self.field_chooser_list)
        self.main_layout.addLayout(field_chooser_layout)
        self.main_layout.addWidget(QLabel("<b>Configure selected fields:</b>"))

        # Scrollable area for the details of fields selected in field_chooser_list
        self.details_scroll_area = QScrollArea(self)
        self.details_scroll_area.setWidgetResizable(True)
        self.details_widget_container = QWidget() 
        self.details_layout = QVBoxLayout(self.details_widget_container) 
        self.details_scroll_area.setWidget(self.details_widget_container)
        self.main_layout.addWidget(self.details_scroll_area)
        
        # Load initial config and populate UI
        self._load_initial_config_and_populate()

        # Connections
        self.note_type_combo.currentTextChanged.connect(self._on_note_type_changed)
        self.main_field_combo.currentTextChanged.connect(self._on_main_field_changed)
        self.field_chooser_list.itemChanged.connect(self._on_field_chooser_item_changed)

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

    def _load_initial_config_and_populate(self):
        cfg = config.get_config()
        saved_note_type = cfg.get("note_type")

        if saved_note_type and saved_note_type in mw.col.models.allNames():
            self.note_type_combo.setCurrentText(saved_note_type)
        elif self.note_type_combo.count() > 0:
            self.note_type_combo.setCurrentIndex(0)
        
        # _on_note_type_changed will be called, which populates main_field_combo and field_chooser
        # and then _update_configurable_fields_display will be called by those handlers.
        # We just need to ensure the first call to _on_note_type_changed happens.
        self._on_note_type_changed(self.note_type_combo.currentText())


    def _on_note_type_changed(self, note_type_name):
        if not note_type_name:
            self.main_field_combo.clear()
            self.field_chooser_list.clear()
            self._clear_details_layout()
            return

        self.current_note_type_name = note_type_name
        cfg = config.get_config()
        
        self.main_field_combo.blockSignals(True)
        self.main_field_combo.clear()
        model = mw.col.models.byName(note_type_name)
        if model:
            field_names = [f['name'] for f in model['flds']]
            self.main_field_combo.addItems(field_names)
            
            saved_main_field = cfg.get("main_field")
            # Check if saved_main_field is valid for this note_type
            if cfg.get("note_type") == note_type_name and saved_main_field and saved_main_field in field_names:
                self.main_field_combo.setCurrentText(saved_main_field)
            elif field_names:
                self.main_field_combo.setCurrentIndex(0)
        self.main_field_combo.blockSignals(False)
        
        # This will trigger _on_main_field_changed if the main field actually changed,
        # which in turn calls _populate_field_chooser_and_details.
        # If it didn't change (e.g. first field is default), we need to call it manually.
        if self.current_main_field_name == self.main_field_combo.currentText() and self.current_note_type_name == note_type_name :
             self._populate_field_chooser_and_details()
        else:
            # Let the _on_main_field_changed signal handle the update.
            # However, we need to ensure current_main_field_name is updated for the first run.
             self.current_main_field_name = self.main_field_combo.currentText()
             self._populate_field_chooser_and_details() # Manually call if main field didn't change via signal

    def _on_main_field_changed(self, main_field_name):
        if not self.current_note_type_name: # Not yet initialized
            return
        self.current_main_field_name = main_field_name
        self._populate_field_chooser_and_details()

    def _populate_field_chooser_and_details(self):
        self.field_chooser_list.blockSignals(True)
        self.field_chooser_list.clear()
        self._clear_details_layout() # Clear existing details UI

        if not self.current_note_type_name:
            self.field_chooser_list.blockSignals(False)
            return

        model = mw.col.models.byName(self.current_note_type_name)
        if not model:
            self.field_chooser_list.blockSignals(False)
            return
            
        cfg = config.get_config()
        # Get list of fields chosen to be configurable for this note type
        configurable_fields_for_note_type = cfg.get("configurable_fields", {}).get(self.current_note_type_name, [])

        all_field_names_in_model = [f['name'] for f in model['flds']]
        
        for field_name in all_field_names_in_model:
            if field_name == self.current_main_field_name:
                continue # Don't add main field to chooser

            item = QListWidgetItem(field_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            # Check if this field was previously selected in chooser
            item.setCheckState(Qt.CheckState.Checked if field_name in configurable_fields_for_note_type else Qt.CheckState.Unchecked)
            self.field_chooser_list.addItem(item)
        
        self.field_chooser_list.blockSignals(False)
        self._update_configurable_fields_display() # Build UI for initially checked items

    def _on_field_chooser_item_changed(self, item):
        # This is called when a checkbox in the field_chooser_list changes state
        self._update_configurable_fields_display()

    def _clear_details_layout(self):
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.configurable_field_details.clear()
        # self.field_site_checkboxes.clear() # This should be managed per note_type/field

    def _update_configurable_fields_display(self):
        self._clear_details_layout() # Clear previous UI
        
        if not self.current_note_type_name:
            return

        cfg = config.get_config()
        saved_display_states = cfg.get("field_display_states", {}).get(self.current_note_type_name, {})
        saved_site_configs = cfg.get("field_search_configs", {}).get(self.current_note_type_name, {})

        # Initialize field_site_checkboxes for the current note type if not present
        if self.current_note_type_name not in self.field_site_checkboxes:
            self.field_site_checkboxes[self.current_note_type_name] = {}

        for i in range(self.field_chooser_list.count()):
            item = self.field_chooser_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                field_name = item.text()

                # Initialize for this field if not present
                if field_name not in self.field_site_checkboxes[self.current_note_type_name]:
                     self.field_site_checkboxes[self.current_note_type_name][field_name] = {}


                field_group_box = QGroupBox() # Main container for this field's config
                field_group_layout = QVBoxLayout(field_group_box)

                # Header with field name and toggle button
                header_layout = QHBoxLayout()
                field_label = QLabel(f"<b>{field_name}</b>")
                toggle_button = QPushButton("▼") # Default to expanded
                toggle_button.setCheckable(True)
                toggle_button.setChecked(True) # Default to expanded
                toggle_button.setStyleSheet("QPushButton { border: none; font-weight: bold; }")
                toggle_button.setMaximumWidth(30)
                header_layout.addWidget(field_label)
                header_layout.addStretch()
                header_layout.addWidget(toggle_button)
                field_group_layout.addLayout(header_layout)

                # Content widget (for categories and sites)
                content_widget = QWidget()
                content_layout = QVBoxLayout(content_widget)

                field_saved_site_cfg = saved_site_configs.get(field_name, {})

                for category_name, sites in PREDEFINED_SEARCH_SITES.items():
                    if category_name not in self.field_site_checkboxes[self.current_note_type_name][field_name]:
                        self.field_site_checkboxes[self.current_note_type_name][field_name][category_name] = {}

                    category_group = QGroupBox(category_name)
                    category_layout = QVBoxLayout(category_group)
                    for site_name_key, site_url in sites.items():
                        site_checkbox = QCheckBox(site_name_key)
                        is_site_checked = field_saved_site_cfg.get(category_name, {}).get(site_name_key, False)
                        site_checkbox.setChecked(is_site_checked)
                        category_layout.addWidget(site_checkbox)
                        self.field_site_checkboxes[self.current_note_type_name][field_name][category_name][site_name_key] = site_checkbox
                    category_group.setLayout(category_layout)
                    content_layout.addWidget(category_group)
                
                content_widget.setLayout(content_layout)
                field_group_layout.addWidget(content_widget)
                field_group_box.setLayout(field_group_layout)
                self.details_layout.addWidget(field_group_box)

                # Store references
                self.configurable_field_details[field_name] = {
                    "group_box": field_group_box,
                    "content_widget": content_widget,
                    "toggle_button": toggle_button
                }

                # Connect toggle button
                toggle_button.toggled.connect(partial(self._toggle_field_content, field_name, content_widget, toggle_button))

                # Set initial expanded state
                is_expanded = saved_display_states.get(field_name, {}).get("expanded", True) # Default to expanded
                toggle_button.setChecked(is_expanded)
                content_widget.setVisible(is_expanded)
                toggle_button.setText("▼" if is_expanded else "►")
        
        self.details_layout.addStretch()

    def _toggle_field_content(self, field_name, content_widget, button, checked):
        content_widget.setVisible(checked)
        button.setText("▼" if checked else "►")
        # The state will be saved in save_settings

    def save_settings(self):
        cfg = config.get_config()

        current_note_type = self.note_type_combo.currentText()
        current_main_field = self.main_field_combo.currentText()

        cfg["note_type"] = current_note_type
        cfg["main_field"] = current_main_field

        # --- Save Configurable Fields (from chooser) ---
        if "configurable_fields" not in cfg:
            cfg["configurable_fields"] = {}
        
        selected_configurable_fields = []
        for i in range(self.field_chooser_list.count()):
            item = self.field_chooser_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_configurable_fields.append(item.text())
        
        if current_note_type: # Only save if a note type is selected
            cfg["configurable_fields"][current_note_type] = selected_configurable_fields
        
        # --- Save Display States and Site Configs for selected configurable fields ---
        if "field_display_states" not in cfg:
            cfg["field_display_states"] = {}
        if "field_search_configs" not in cfg:
            cfg["field_search_configs"] = {}

        if current_note_type:
            if current_note_type not in cfg["field_display_states"]:
                cfg["field_display_states"][current_note_type] = {}
            if current_note_type not in cfg["field_search_configs"]:
                cfg["field_search_configs"][current_note_type] = {}

            # Store current states for fields that are still configurable
            current_note_type_display_states = {}
            current_note_type_search_configs = {}

            for field_name in selected_configurable_fields:
                if field_name in self.configurable_field_details:
                    details = self.configurable_field_details[field_name]
                    is_expanded = details["toggle_button"].isChecked()
                    current_note_type_display_states[field_name] = {"expanded": is_expanded}

                    # Save site checkboxes for this field
                    if field_name in self.field_site_checkboxes.get(current_note_type, {}):
                        current_note_type_search_configs[field_name] = {}
                        for cat_name, sites in self.field_site_checkboxes[current_note_type][field_name].items():
                            current_note_type_search_configs[field_name][cat_name] = {}
                            for site_name_key, checkbox_widget in sites.items():
                                current_note_type_search_configs[field_name][cat_name][site_name_key] = checkbox_widget.isChecked()
            
            cfg["field_display_states"][current_note_type] = current_note_type_display_states
            cfg["field_search_configs"][current_note_type] = current_note_type_search_configs

            # Clean up: Remove states/configs for fields no longer in selected_configurable_fields for this note type
            for field_in_cfg in list(cfg["field_display_states"][current_note_type].keys()):
                if field_in_cfg not in selected_configurable_fields:
                    del cfg["field_display_states"][current_note_type][field_in_cfg]
            
            for field_in_cfg in list(cfg["field_search_configs"][current_note_type].keys()):
                if field_in_cfg not in selected_configurable_fields:
                    del cfg["field_search_configs"][current_note_type][field_in_cfg]

        config.save_config(cfg)
        self.accept()