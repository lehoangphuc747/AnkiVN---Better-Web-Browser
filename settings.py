from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox
)
from aqt import mw
from . import config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setting - Better Web Browser")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.setMinimumWidth(400)
        
        # Note Type selection
        note_type_layout = QHBoxLayout()
        note_type_label = QLabel("Note Type:")
        self.note_type_combo = QComboBox()
        all_note_types = mw.col.models.allNames()
        self.note_type_combo.addItems(all_note_types)
        
        current_note_type = config.get_config().get("note_type")
        if current_note_type and current_note_type in all_note_types:
            self.note_type_combo.setCurrentText(current_note_type)
        elif all_note_types: # If no saved type or saved type is invalid, select the first one
            self.note_type_combo.setCurrentIndex(0)
            current_note_type = self.note_type_combo.currentText() # Update current_note_type

        self.note_type_combo.currentTextChanged.connect(self.update_field_combo)
        note_type_layout.addWidget(note_type_label)
        note_type_layout.addWidget(self.note_type_combo)
        layout.addLayout(note_type_layout)

        # Main Field selection
        field_layout = QHBoxLayout()
        field_label = QLabel("Main Field:")
        self.field_combo = QComboBox()
        self.update_field_combo(current_note_type if current_note_type else self.note_type_combo.currentText()) # Populate initially
        
        field_layout.addWidget(field_label)
        field_layout.addWidget(self.field_combo)
        layout.addLayout(field_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def update_field_combo(self, note_type_name):
        self.field_combo.clear()
        if note_type_name:
            model = mw.col.models.byName(note_type_name)
            if model:
                field_names = [f['name'] for f in model['flds']]
                self.field_combo.addItems(field_names)
                
                current_main_field = config.get_config().get("main_field")
                if current_main_field and current_main_field in field_names:
                    self.field_combo.setCurrentText(current_main_field)
                elif field_names: # If no saved field or saved is invalid, select first
                    self.field_combo.setCurrentIndex(0)

    def save_settings(self):
        cfg = config.get_config()
        cfg["note_type"] = self.note_type_combo.currentText()
        cfg["main_field"] = self.field_combo.currentText()
        config.save_config(cfg)
        self.accept()
