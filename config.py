import json
import os
from aqt import mw

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

def get_config_path():
    """Return the path to the addon's configuration file."""
    mgr = mw.addonManager

    try:
        # Try the most common method first
        if hasattr(mgr, "addonFolder"):
            addon_dir = mgr.addonFolder(__name__)
        elif hasattr(mgr, "addon_meta"):
            addon_meta = mgr.addon_meta(__name__)
            # Check if addon_meta has path attribute, otherwise use dir_name
            if hasattr(addon_meta, 'path'):
                addon_dir = addon_meta.path
            elif hasattr(addon_meta, 'dir_name'):
                addon_dir = os.path.join(mgr.addonsFolder(), addon_meta.dir_name)
            else:
                # Fallback: use the addon folder directly
                addon_dir = os.path.join(mgr.addonsFolder(), __name__)
        elif hasattr(mgr, "addon_path"):
            addon_dir = mgr.addon_path(__name__)
        else:
            # Final fallback
            addon_base = getattr(mgr, "addon_base", None)
            if addon_base is None:
                addon_dir = os.path.dirname(__file__)
            else:
                addon_dir = os.path.join(addon_base, __name__)
    except Exception as e:
        print(f"Error getting addon path: {e}")
        # Ultimate fallback: use the directory of this file
        addon_dir = os.path.dirname(__file__)

    return os.path.join(addon_dir, "config.json")

def get_default_config():
    """Get default configuration."""
    return {
        "note_type": "",  # Selected note type
        "main_field": "",  # Main field for search
        "refresh_shortcut": "Ctrl+R",  # Default refresh shortcut
        "configurable_fields": {},  # Fields that can show web content
        "field_search_configs": {}  # Search configurations for each field
    }

def get_config():
    """Get current configuration."""
    config_path = get_config_path()
    
    if not os.path.exists(config_path):
        return get_default_config()
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Ensure all required keys exist
        default_config = get_default_config()
        for key in default_config:
            if key not in config:
                config[key] = default_config[key]

        return config
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        return get_default_config()

def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Failed to save configuration: {e}")
        return False