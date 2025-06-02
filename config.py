from aqt import mw

def get_config():
    return mw.addonManager.getConfig(__name__) or default_config()

def save_config(config):
    mw.addonManager.writeConfig(__name__, config)

def default_config():
    return {
        "note_type": "",
        "main_field": "",
        "configurable_fields": {},  # Format: {note_type_name: [field_name1, field_name2]}
        "field_display_states": {}, # Format: {note_type_name: {field_name: {"expanded": True/False}}}
        "field_search_configs": {}  # Existing: site selections for configured fields
    }
