from aqt import mw

def get_config():
    return mw.addonManager.getConfig(__name__) or default_config()

def save_config(config):
    mw.addonManager.writeConfig(__name__, config)

def default_config():
    return {
        "note_type": "",
        "main_field": "",
        "field_search_configs": {}  # New: To store search sites for other fields
    }
